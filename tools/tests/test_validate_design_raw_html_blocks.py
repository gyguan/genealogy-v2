from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class DesignRawHtmlBlockTests(unittest.TestCase):
    def _replace_real_security_section(self, root, raw_block: str):
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 安全与隐私",
            "### 安全设计",
            1,
        )
        text = text.replace(
            "## 测试 Seam",
            f"{raw_block}\n\n## 测试 Seam",
            1,
        )
        path.write_text(text, encoding="utf-8")
        return run(root, "tools/validate_design.py")

    def test_block_tag_content_does_not_supply_required_heading(self) -> None:
        root = copy_repo(self)
        result = self._replace_real_security_section(
            root,
            "<div>\n## 安全与隐私\nSEC-GOV-HTML-FAKE：div中的伪设计。\n</div>",
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing section ## 安全与隐私", result.stdout)

    def test_generic_html_block_does_not_supply_required_heading(self) -> None:
        root = copy_repo(self)
        result = self._replace_real_security_section(
            root,
            "<design-example>\n## 安全与隐私\nSEC-GOV-HTML-FAKE：自定义标签中的伪设计。\n</design-example>",
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing section ## 安全与隐私", result.stdout)

    def test_html_comment_does_not_supply_required_heading(self) -> None:
        root = copy_repo(self)
        result = self._replace_real_security_section(
            root,
            "<!--\n## 安全与隐私\nSEC-GOV-HTML-FAKE：注释中的伪设计。\n-->",
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing section ## 安全与隐私", result.stdout)


if __name__ == "__main__":
    unittest.main()
