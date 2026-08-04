#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    ("layout validation", [sys.executable, "tools/validate_layout.py"]),
    ("repository validation", [sys.executable, "tools/validate_repo.py"]),
    ("product validation", [sys.executable, "tools/validate_product.py"]),
    ("regression tests", [sys.executable, "-m", "unittest", "discover", "-s", "tools/tests", "-p", "test_*.py"]),
)


def main() -> int:
    failures: list[str] = []
    for name, command in COMMANDS:
        print(f"==> {name}", flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            failures.append(name)
    if failures:
        print("Checks failed: " + ", ".join(failures))
        return 1
    print("All repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
