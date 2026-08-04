from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class DesignTestRegistryTests(unittest.TestCase):
    def test_design_checklist_rejects_unregistered_test(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        replaced = 0
        for index, line in enumerate(lines):
            if line.startswith("| TEST-DESIGN-001 |"):
                lines[index] = line.replace(
                    "TEST-DESIGN-001",
                    "TEST-FAKE",
                    1,
                )
                replaced += 1
        self.assertEqual(1, replaced)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "Design test checklist contains unregistered Test(s): TEST-FAKE",
            result.stdout,
        )

    def test_registry_test_must_appear_in_design_checklist(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        filtered = [
            line for line in lines if not line.startswith("| TEST-DESIGN-001 |")
        ]
        self.assertEqual(len(lines) - 1, len(filtered))
        path.write_text("\n".join(filtered) + "\n", encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "tests.yaml Test(s) missing from Design checklist: TEST-DESIGN-001",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
