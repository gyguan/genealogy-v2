from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class DesignCommentAndTableBoundaryTests(unittest.TestCase):
    def test_review_ready_design_rejects_html_comment(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 失败、补偿与回滚",
            "## 失败、补偿与回滚\n\n<!-- TODO: complete rollback details -->",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "review-ready design contains forbidden HTML comment",
            result.stdout,
        )

    def test_pipe_less_definition_row_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "设计契约只引用正式领域资产，不复制领域事实；",
            "RULE-GOV-PIPELESS-001 | 无边框定义 | 缺少正式追踪 |\n\n"
            "设计契约只引用正式领域资产，不复制领域事实；",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "definition row must use canonical outer pipes: RULE-GOV-PIPELESS-001",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
