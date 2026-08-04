#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "changes" / "_template"


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python tools/new_change.py CHG-0001 stable-name")
        return 2

    change_id = sys.argv[1].upper()
    name = sys.argv[2].strip().lower()
    if not re.fullmatch(r"CHG-\d{4}", change_id):
        print("Change ID must match CHG-0001")
        return 2
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        print("Name must be lowercase kebab-case")
        return 2

    changes_root = ROOT / "changes"
    reused = [path for path in changes_root.glob(f"{change_id}-*") if path.is_dir()]
    if reused:
        print(f"Change ID already exists: {reused[0].relative_to(ROOT)}")
        return 1

    target = changes_root / f"{change_id}-{name}"
    if target.exists():
        print(f"Target already exists: {target.relative_to(ROOT)}")
        return 1

    shutil.copytree(TEMPLATE, target)
    metadata = target / "change.yaml"
    text = metadata.read_text(encoding="utf-8")
    text = text.replace("CHG-0000", change_id).replace("change-name", name)
    metadata.write_text(text, encoding="utf-8")
    print(f"Created {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
