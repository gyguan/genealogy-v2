from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class FinalDesignReviewGapTests(unittest.TestCase):
    def test_required_domain_model_needs_traceable_definition_row(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "  domain_model: not-applicable",
            "  domain_model: required",
            1,
        )
        text = text.replace(
            "N/A: domain_model - 本 Change 不增加或修改族谱领域概念、规则和不变量。",
            "RULE-GOV-PROSE-001：普通段落中的规则定义，不含 Spec/Test 追踪。",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "required facet domain_model needs a canonical RULE/INV definition row",
            result.stdout,
        )

    def test_fenced_html_example_does_not_mask_following_sections(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 方案概览\n",
            "## 方案概览\n\n```html\n<div>\n## 伪造章节\n</div>\n```\n",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
