from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class DesignReviewHardeningTests(unittest.TestCase):
    def test_blockquoted_heading_does_not_count_as_top_level_section(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 安全与隐私",
            "> ## 安全与隐私",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing section ## 安全与隐私", result.stdout)

    def test_matrix_test_must_cover_its_spec_in_registry(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        replaced = 0
        for index, line in enumerate(lines):
            if line.startswith("| SPEC-GOV-DESIGN-002 |"):
                lines[index] = line.replace(
                    "TEST-DESIGN-003",
                    "TEST-DESIGN-001",
                    1,
                )
                replaced += 1
        self.assertEqual(1, replaced)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "Spec traceability row SPEC-GOV-DESIGN-002 uses Test(s) "
            "without registered coverage: TEST-DESIGN-001",
            result.stdout,
        )

    def test_formatted_definition_id_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "设计契约只引用正式领域资产，不复制领域事实；",
            "| **RULE-GOV-FORMATTED-001** | 格式化定义ID | 无正式追踪 |\n\n"
            "设计契约只引用正式领域资产，不复制领域事实；",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "definition ID must be canonical plain text: RULE-GOV-FORMATTED-001",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
