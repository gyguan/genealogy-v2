from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class DefinitionColumnAndHtmlContextTests(unittest.TestCase):
    def test_definition_links_use_designated_columns(self) -> None:
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
            """| ID | 类型 | 设计内容 | 执行位置 | 关联 Spec | 验证测试 |
|---|---|---|---|---|---|
| RULE-GOV-COLUMN-001 | RULE | 描述包含 SPEC-GOV-DESIGN-001 与 TEST-DESIGN-001 | validator | | |
""",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "every RULE/INV row must link both SPEC and TEST",
            result.stdout,
        )

    def test_type7_html_does_not_interrupt_paragraph(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("MIG-GOV-DESIGN-001", "MIGRATION-GOV-DESIGN-001", 1)
        text = text.replace(
            "## 迁移方案\n\n",
            """## 迁移方案

普通段落继续包含内联自定义标签
<widget>
MIG-GOV-PARAGRAPH-001：该迁移设计仍属于同一普通段落并应保持可见。

""",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
