#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "changes" / "_template"
CHANGE_TYPES = {"product", "domain", "engineering", "governance", "security"}
PROFILE_BY_TYPE = {
    "product": "high-risk",
    "domain": "high-risk",
    "security": "high-risk",
    "governance": "standard",
    "engineering": "standard",
}
SCOPE_BY_TYPE = {
    "product": ["product"],
    "engineering": ["engineering"],
    "governance": ["repository-governance"],
    "security": ["security"],
}


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a YAML object")
    return value


def known_capabilities() -> set[str]:
    manifest = load_yaml(ROOT / "product/capability-map.yaml")
    result: set[str] = set()
    for file_name in manifest.get("group_files", []):
        data = load_yaml(ROOT / "product" / str(file_name))
        for item in data.get("group", {}).get("capabilities", []):
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                result.add(item["id"])
    return result


def known_domains() -> set[str]:
    data = load_yaml(ROOT / "domains/context-map.yaml")
    return {
        item["id"]
        for item in data.get("contexts", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def known_decisions() -> set[str]:
    return {"-".join(path.name.split("-")[:2]) for path in (ROOT / "decisions").glob("DEC-*.md")}


def validate_values(values: list[str], known: set[str], label: str) -> None:
    unknown = sorted(set(values) - known)
    if unknown:
        raise ValueError(f"Unknown {label}: {', '.join(unknown)}")


def spec_scopes(kind: str, domains: list[str]) -> list[str]:
    if kind == "domain":
        if not domains:
            raise ValueError("Domain Change requires at least one --domain")
        return domains
    return SCOPE_BY_TYPE[kind]


def write_spec_skeleton(path: Path, change_id: str, scope: str) -> str:
    spec_id = "SPEC-REPLACE-ME"
    path.write_text(
        f"# {scope} Spec Delta\n\n"
        "## ADDED\n\n"
        f"## {spec_id} Observable requirement\n"
        "#### Requirement\n"
        f"<!-- {change_id}: describe one observable requirement. -->\n\n"
        "#### Scenario SCN-REPLACE-ME-01\n"
        "- Given: describe the initial state\n"
        "- When: describe the action or event\n"
        "- Then: describe the observable result\n",
        encoding="utf-8",
    )
    return spec_id


def update_design_contract(
    path: Path,
    change_id: str,
    capabilities: list[str],
    specs: list[str],
    domains: list[str],
    decisions: list[str],
) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("changes/_template/design.md must contain YAML frontmatter")
    raw_metadata, body = text[4:].split("\n---\n", 1)
    metadata = yaml.safe_load(raw_metadata)
    if not isinstance(metadata, dict):
        raise ValueError("changes/_template/design.md frontmatter must be an object")
    metadata.update(
        {
            "contract_version": 1,
            "change": change_id,
            "status": "draft",
            "capabilities": list(dict.fromkeys(capabilities)),
            "specs": list(dict.fromkeys(specs)),
            "affected_domains": list(dict.fromkeys(domains)),
            "decisions": list(dict.fromkeys(decisions)),
            "open_questions": 0,
        }
    )
    rendered = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=120).rstrip()
    path.write_text(f"---\n{rendered}\n---\n\n{body.lstrip()}", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a validated Change skeleton")
    parser.add_argument("change_id", help="CHG-0001")
    parser.add_argument("name", help="lowercase kebab-case stable name")
    parser.add_argument("--type", choices=sorted(CHANGE_TYPES), required=True, dest="change_type")
    parser.add_argument("--profile", choices=("lightweight", "standard", "high-risk"))
    parser.add_argument("--issue", type=int)
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--domain", action="append", default=[])
    parser.add_argument("--decision", action="append", default=[])
    args = parser.parse_args()

    change_id = args.change_id.upper()
    name = args.name.strip().lower()
    if not re.fullmatch(r"CHG-\d{4}", change_id):
        parser.error("Change ID must match CHG-0001")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        parser.error("name must be lowercase kebab-case")

    profile = args.profile or PROFILE_BY_TYPE[args.change_type]
    if args.change_type in {"product", "domain", "security"} and profile != "high-risk":
        parser.error(f"{args.change_type} Change must use high-risk profile")
    if args.change_type == "governance" and profile == "lightweight":
        parser.error("governance Change cannot use lightweight profile")

    try:
        validate_values(args.capability, known_capabilities(), "Capability IDs")
        validate_values(args.domain, known_domains(), "Domain IDs")
        validate_values(args.decision, known_decisions(), "Decision IDs")
        scopes = spec_scopes(args.change_type, args.domain)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))

    changes_root = ROOT / "changes"
    reused = [path for path in changes_root.glob(f"{change_id}-*") if path.is_dir()]
    if reused:
        parser.error(f"Change ID already exists: {reused[0].relative_to(ROOT)}")
    target = changes_root / f"{change_id}-{name}"
    if target.exists():
        parser.error(f"Target already exists: {target.relative_to(ROOT)}")

    shutil.copytree(TEMPLATE, target)
    metadata = load_yaml(target / "change.yaml")
    metadata.update(
        {
            "version": 2,
            "design_contract_version": 1,
            "id": change_id,
            "title": name,
            "change_type": args.change_type,
            "change_profile": profile,
            "quality_policy": "strict",
            "status": "draft",
            "issue": {"repository": "gyguan/genealogy-v2", "number": args.issue},
            "capabilities": list(dict.fromkeys(args.capability)),
            "affected_domains": list(dict.fromkeys(args.domain)),
            "affected_decisions": list(dict.fromkeys(args.decision)),
        }
    )
    (target / "change.yaml").write_text(
        yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )

    specs_dir = target / "specs"
    specs_dir.mkdir(exist_ok=True)
    spec_ids = [write_spec_skeleton(specs_dir / f"{scope}.md", change_id, scope) for scope in scopes]
    update_design_contract(
        target / "design.md",
        change_id,
        args.capability,
        spec_ids,
        args.domain,
        args.decision,
    )
    (target / "evidence").mkdir(exist_ok=True)

    print(f"Created {target.relative_to(ROOT)}")
    print(f"Next: python tools/context.py {change_id}")
    print("Before review: replace placeholder Spec and Task IDs, register tests in tests.yaml, then run python tools/check.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
