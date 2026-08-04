from __future__ import annotations

import re
import unittest

import yaml

from validation_test_utils import ROOT, copy_repo, run


class ProductValidationTests(unittest.TestCase):
    def test_current_repository_passes(self) -> None:
        result = run(ROOT, "tools/validate_product.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_compatibility_projection_is_forbidden(self) -> None:
        root = copy_repo(self)
        path = root / "product/capability-map.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["capability_groups"] = []
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_product.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("compatibility projection is forbidden", result.stdout)

    def test_roadmap_heading_must_match_exactly(self) -> None:
        root = copy_repo(self)
        path = root / "product/roadmap.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("### 成功指标", "### 成功指标待补充", 1),
            encoding="utf-8",
        )
        result = run(root, "tools/validate_product.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing exact section ### 成功指标", result.stdout)

    def test_roadmap_placeholder_body_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / "product/roadmap.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"(## V0\.1[\s\S]*?### 用户目标\n\n)[\s\S]*?(\n### 纵向闭环)",
            r"\1待补充\2",
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_product.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("empty or placeholder", result.stdout)

    def test_closure_cannot_use_later_capability(self) -> None:
        root = copy_repo(self)
        path = root / "product/releases.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["releases"][0]["closure"]["recovery"] = "CAP-PLATFORM-012"
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_product.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("closure recovery uses later capability", result.stdout)

    def test_future_bounded_release_requires_governed_closure(self) -> None:
        root = copy_repo(self)
        releases_path = root / "product/releases.yaml"
        data = yaml.safe_load(releases_path.read_text(encoding="utf-8"))
        data["releases"].append(
            {
                "id": "V0.6",
                "name": "未来受治理版本",
                "status": "planned",
                "planning_confidence": "high",
                "planning_depth": "bounded",
                "goal": "验证未来版本不会绕过纵向闭环门禁",
            }
        )
        releases_path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        roadmap_path = root / "product/roadmap.md"
        roadmap_path.write_text(
            roadmap_path.read_text(encoding="utf-8")
            + """

## V0.6 未来受治理版本
### 用户目标
验证未来版本。
### 纵向闭环
输入 → 审核 → 查询 → 迁出 → 恢复。
### 主要能力
- 示例能力。
### 明确不包含
- 未批准能力。
### 版本验收
完成示例验收。
### 成功指标
- 验收通过率为 100%。
### 核心风险
不能绕过闭环。
""",
            encoding="utf-8",
        )
        result = run(root, "tools/validate_product.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("V0.6 needs closure mapping", result.stdout)


if __name__ == "__main__":
    unittest.main()
