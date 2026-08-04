#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_CAPABILITY_MANIFEST_FIELDS = {
    "version",
    "status",
    "updated_at",
    "release_source",
    "capability_directory",
    "group_files",
    "rules",
}
OBSOLETE_PATHS = (
    "ai",
    "knowledge",
    "changes/active",
    "changes/archived",
)


def main() -> int:
    errors: list[str] = []

    manifest_path = ROOT / "product/capability-map.yaml"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"product/capability-map.yaml: invalid manifest: {exc}")
        manifest = None

    if isinstance(manifest, dict):
        unknown_fields = sorted(set(manifest) - ALLOWED_CAPABILITY_MANIFEST_FIELDS)
        if unknown_fields:
            errors.append(
                "product/capability-map.yaml: unknown top-level fields are forbidden: "
                + ", ".join(unknown_fields)
            )
    elif manifest is not None:
        errors.append("product/capability-map.yaml: manifest must be an object")

    for relative_path in OBSOLETE_PATHS:
        if (ROOT / relative_path).exists():
            errors.append(f"obsolete repository path is forbidden: {relative_path}")

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1

    print("Repository layout validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
