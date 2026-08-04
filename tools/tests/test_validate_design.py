from __future__ import annotations

import _test_validate_design_core as _core

_core.CHANGE = "changes/CHG-0007-requirement-design-contract"


def _test_security_row_requires_declared_test(self) -> None:
    root = _core.copy_repo(self)
    path = root / _core.CHANGE / "design.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    replaced = 0
    for index, line in enumerate(lines):
        if line.startswith("| SEC-GOV-DESIGN-001 |"):
            lines[index] = line.replace(
                "TEST-DESIGN-SEC-001",
                "TEST-NOT-DECLARED",
                1,
            )
            replaced += 1
    self.assertEqual(1, replaced)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = _core.run(root, "tools/validate_design.py")

    self.assertNotEqual(0, result.returncode)
    self.assertIn(
        "linked row references unknown Test(s): TEST-NOT-DECLARED",
        result.stdout,
    )


_core.DesignValidationTests.test_security_row_requires_declared_test = (
    _test_security_row_requires_declared_test
)

from _test_validate_design_core import *  # noqa: F401,F403,E402
