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
FACETS = (
    "workflow", "domain_model", "state_machine", "persistence", "external_api", "ui",
    "events", "migration", "performance", "security_privacy", "module_consistency", "tests_traceability",
)
MACHINE_REQUIRED_BY_TYPE = {
    "product": {"workflow", "domain_model", "security_privacy", "module_consistency", "tests_traceability"},
    "domain": {"workflow", "domain_model", "security_privacy", "module_consistency", "tests_traceability"},
    "engineering": {"security_privacy", "module_consistency", "tests_traceability"},
    "governance": {"security_privacy", "module_consistency", "tests_traceability"},
    "security": {"security_privacy", "module_consistency", "tests_traceability"},
}
LEGACY_APPLICABILITY_BY_TYPE = {
    "product": {"workflow", "domain_model", "security_privacy", "module_consistency", "tests_traceability"},
    "domain": {"workflow", "domain_model", "security_privacy", "module_consistency", "tests_traceability"},
    "engineering": {"workflow", "domain_model", "security_privacy", "module_consistency", "tests_traceability"},
    "governance": {"workflow", "security_privacy", "module_consistency", "tests_traceability"},
    "security": {"workflow", "security_privacy", "module_consistency", "tests_traceability"},
}
FACET_REASON = {
    "workflow": "需要根据真实用户或作业流程判断",
    "domain_model": "需要根据领域概念、规则和不变量变化判断",
    "state_machine": "需要根据生命周期和状态迁移判断",
    "persistence": "需要根据数据结构、完整性和生命周期判断",
    "external_api": "需要根据对外契约变化判断",
    "ui": "需要根据用户交互变化判断",
    "events": "需要根据跨模块或异步协作判断",
    "migration": "需要根据兼容、历史数据和发布切换判断",
    "performance": "需要根据容量、时延和资源预算判断",
    "security_privacy": "所有 Change 都必须显式评估安全、隐私和审计影响",
    "module_consistency": "所有 Change 都必须声明模块落位和允许依赖",
    "tests_traceability": "所有正式 Spec 都必须追踪到设计与注册测试",
}


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a YAML object")
    return value


def write_yaml(path: Path, value: dict) -> None:
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


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
    return {item["id"] for item in data.get("contexts", []) if isinstance(item, dict) and isinstance(item.get("id"), str)}


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


def legacy_applicability(change_type: str) -> dict[str, str]:
    required = LEGACY_APPLICABILITY_BY_TYPE[change_type]
    return {facet: ("required" if facet in required else "not-applicable") for facet in FACETS}


def machine_facets(change_type: str) -> dict[str, dict]:
    required = MACHINE_REQUIRED_BY_TYPE[change_type]
    result: dict[str, dict] = {}
    for facet in FACETS:
        result[facet] = {
            "status": "required" if facet in required else "review-required",
            "reason": FACET_REASON[facet],
            "design_ids": [],
        }
    return result


def update_design_markdown(path: Path, change_id: str, capabilities: list[str], specs: list[str], domains: list[str], decisions: list[str], change_type: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("changes/_template/design.md must contain YAML frontmatter")
    raw_metadata, body = text[4:].split("\n---\n", 1)
    metadata = yaml.safe_load(raw_metadata)
    if not isinstance(metadata, dict):
        raise ValueError("changes/_template/design.md frontmatter must be an object")
    metadata.update({
        "contract_version": 1,
        "change": change_id,
        "status": "draft",
        "capabilities": list(dict.fromkeys(capabilities)),
        "specs": list(dict.fromkeys(specs)),
        "affected_domains": list(dict.fromkeys(domains)),
        "decisions": list(dict.fromkeys(decisions)),
        "applicability": legacy_applicability(change_type),
        "open_questions": 0,
    })
    rendered = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=120).rstrip()
    path.write_text(f"---\n{rendered}\n---\n\n{body.lstrip()}", encoding="utf-8")


def update_design_machine(path: Path, change_id: str, capabilities: list[str], specs: list[str], domains: list[str], decisions: list[str], change_type: str) -> None:
    data = load_yaml(path)
    data.update({
        "version": 1,
        "change": change_id,
        "status": "draft",
        "references": {
            "capabilities": list(dict.fromkeys(capabilities)),
            "specs": list(dict.fromkeys(specs)),
            "domains": list(dict.fromkeys(domains)),
            "decisions": list(dict.fromkeys(decisions)),
        },
        "facets": machine_facets(change_type),
        "facts": [],
        "assumptions": [],
        "open_questions": [],
        "definitions": [],
        "traceability": [],
    })
    write_yaml(path, data)


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
    metadata.update({
        "version": 2,
        "design_contract_version": 1,
        "design_machine_contract_version": 1,
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
    })
    write_yaml(target / "change.yaml", metadata)

    specs_dir = target / "specs"
    specs_dir.mkdir(exist_ok=True)
    spec_ids = [write_spec_skeleton(specs_dir / f"{scope}.md", change_id, scope) for scope in scopes]
    update_design_markdown(target / "design.md", change_id, args.capability, spec_ids, args.domain, args.decision, args.change_type)
    update_design_machine(target / "design.yaml", change_id, args.capability, spec_ids, args.domain, args.decision, args.change_type)
    (target / "evidence").mkdir(exist_ok=True)

    print(f"Created {target.relative_to(ROOT)}")
    print(f"Next: python tools/context.py {change_id} --bundle")
    print("Before review: resolve review-required facets, replace placeholder IDs, register tests, then run python tools/check.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
