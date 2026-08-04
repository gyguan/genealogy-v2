from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0006-requirement-design-contract"


class DesignPlaceholderBoundaryTests(unittest.TestCase):
    def test_ascii_identifier_containing_todo_is_allowed(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 方案概览",
            "## 方案概览\n\nAutodoc.py 作为设计文档生成脚本名称，不是占位符。",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_todo_adjacent_to_chinese_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 方案概览",
            "## 方案概览\n\nTODO补写",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("contains placeholder 'TODO'", result.stdout)


if __name__ == "__main__":
    unittest.main()
