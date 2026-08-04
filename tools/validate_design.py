#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import _validate_design_core as core

# CHG-0006 was introduced by diagnostic governance on main before the design
# contract landed. The design contract therefore becomes mandatory at CHG-0007.
core.REQUIRED_FROM_CHANGE_NUMBER = 7


def main() -> int:
    core.ERRORS.clear()
    core.validate_template()
    changes_root = core.ROOT / "changes"
    if changes_root.exists():
        for path in sorted(changes_root.iterdir()):
            if path.is_dir() and path.name != "_template":
                core.validate_change(path)
    if core.ERRORS:
        print("Design validation failed:")
        for message in core.ERRORS:
            print(f"- {message.replace('CHG-0006 and later', 'CHG-0007 and later')}")
        return 1
    print("Design validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
