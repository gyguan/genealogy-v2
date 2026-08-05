from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0006-requirement-design-contract"


class DesignContractBypassTests(unittest.TestCase):
    def test_empty_frontmatter_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        _, body = text[4:].split("\n---\n", 1)
        path.write_text(f"---\n{{}}\n---\n{body}", encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("contract_version must be integer 1", result.stdout)
        self.assertIn("missing frontmatter key capabilities", result.stdout)

    def test_required_heading_inside_raw_html_code_block_does_not_count(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 迁移方案",
            "### 迁移细节",
            1,
        )
        text = text.replace(
            "## 备选方案与权衡",
            "<pre>\n## 迁移方案\nMIG-GOV-FAKE：原始HTML代码块中的伪章节。\n</pre>\n\n## 备选方案与权衡",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing section ## 迁移方案", result.stdout)


if __name__ == "__main__":
    unittest.main()
