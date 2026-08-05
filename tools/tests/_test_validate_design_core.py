from __future__ import annotations

import re
import subprocess
import sys
import unittest

import yaml

from validation_test_utils import ROOT, copy_repo, run

CHANGE = "changes/CHG-0006-requirement-design-contract"


def update_frontmatter(path, mutate) -> None:
    text = path.read_text(encoding="utf-8")
    raw, body = text[4:].split("\n---\n", 1)
    metadata = yaml.safe_load(raw)
    mutate(metadata)
    rendered = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=120).rstrip()
    path.write_text(f"---\n{rendered}\n---\n{body}", encoding="utf-8")


class DesignValidationTests(unittest.TestCase):
    def test_current_repository_passes(self) -> None:
        result = run(ROOT, "tools/validate_design.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_template_contract_is_validated(self) -> None:
        root = copy_repo(self)
        path = root / "changes/_template/design.md"
        update_frontmatter(path, lambda data: data["applicability"].pop("events"))
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing applicability facets: events", result.stdout)

    def test_new_change_number_requires_design_contract(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "change.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data.pop("design_contract_version")
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("require design_contract_version", result.stdout)

    def test_boolean_change_contract_version_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "change.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["design_contract_version"] = True
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("require design_contract_version: integer 1", result.stdout)

    def test_boolean_design_contract_version_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        update_frontmatter(path, lambda data: data.update({"contract_version": True}))
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("contract_version must be integer 1", result.stdout)

    def test_design_references_must_match_change(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        update_frontmatter(path, lambda data: data["capabilities"].append("CAP-PERSON-001"))
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("capabilities must match", result.stdout)

    def test_empty_reference_key_must_be_declared(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        update_frontmatter(path, lambda data: data.pop("capabilities"))
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing frontmatter key capabilities", result.stdout)

    def test_not_applicable_facet_requires_reason(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text, count = re.subn(
            r"^N/A:\s*state_machine\s*-.*$",
            "状态机不适用。",
            text,
            count=1,
            flags=re.M,
        )
        self.assertEqual(1, count)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("not-applicable facet state_machine needs", result.stdout)

    def test_na_reason_requires_non_whitespace(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text, count = re.subn(
            r"^N/A:\s*state_machine\s*-.*$",
            "N/A: state_machine -      ",
            text,
            count=1,
            flags=re.M,
        )
        self.assertEqual(1, count)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("not-applicable facet state_machine needs", result.stdout)

    def test_indented_code_does_not_supply_na_reason(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text, count = re.subn(
            r"^N/A:\s*state_machine\s*-.*$",
            "    N/A: state_machine - 这只是缩进代码示例，不是正式设计。",
            text,
            count=1,
            flags=re.M,
        )
        self.assertEqual(1, count)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("not-applicable facet state_machine needs", result.stdout)

    def test_every_spec_must_appear_in_traceability(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        prefix, trace = text.split("### Spec 追踪矩阵", 1)
        trace = trace.replace("SPEC-GOV-DESIGN-005", "SPEC-GOV-DESIGN-MISSING", 1)
        path.write_text(prefix + "### Spec 追踪矩阵" + trace, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Spec SPEC-GOV-DESIGN-005 is missing", result.stdout)

    def test_extended_matrix_spec_id_does_not_count_as_exact_match(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        prefix, trace = text.split("### Spec 追踪矩阵", 1)
        trace = trace.replace("| SPEC-GOV-DESIGN-005 |", "| SPEC-GOV-DESIGN-005-OLD |", 1)
        path.write_text(prefix + "### Spec 追踪矩阵" + trace, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Spec SPEC-GOV-DESIGN-005 is missing", result.stdout)
        self.assertIn("matrix contains unknown Spec(s): SPEC-GOV-DESIGN-005-OLD", result.stdout)

    def test_matrix_row_requires_declared_test(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        prefix, trace = text.split("### Spec 追踪矩阵", 1)
        trace = trace.replace(
            "| SPEC-GOV-DESIGN-005 | UC-GOV-DESIGN-001 | DESIGN-GOV-002 | Spec Gate Contract | TEST-DESIGN-006 |",
            "| SPEC-GOV-DESIGN-005 | UC-GOV-DESIGN-001 | DESIGN-GOV-002 | Spec Gate Contract | |",
            1,
        )
        path.write_text(prefix + "### Spec 追踪矩阵" + trace, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Spec traceability row SPEC-GOV-DESIGN-005 must link at least one declared Test", result.stdout)

    def test_matrix_row_rejects_unknown_test(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        prefix, trace = text.split("### Spec 追踪矩阵", 1)
        trace = trace.replace("TEST-DESIGN-006", "TEST-NOT-DECLARED", 1)
        path.write_text(prefix + "### Spec 追踪矩阵" + trace, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Spec traceability row SPEC-GOV-DESIGN-005 references unknown Test(s): TEST-NOT-DECLARED", result.stdout)

    def test_rule_row_rejects_unknown_spec(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "设计契约只引用正式领域资产，不复制领域事实；",
            "| RULE-GOV-DESIGN-TEST | 测试规则 | validator | SPEC-GOV-DESIGN-NOT-FOUND | TEST-DESIGN-001 |\n\n设计契约只引用正式领域资产，不复制领域事实；",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("linked row references unknown Spec(s): SPEC-GOV-DESIGN-NOT-FOUND", result.stdout)

    def test_rule_row_rejects_unknown_test(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "设计契约只引用正式领域资产，不复制领域事实；",
            "| RULE-GOV-DESIGN-TEST | 测试规则 | validator | SPEC-GOV-DESIGN-001 | TEST-NOT-FOUND |\n\n设计契约只引用正式领域资产，不复制领域事实；",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("linked row references unknown Test(s): TEST-NOT-FOUND", result.stdout)

    def test_security_row_requires_declared_test(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        security, rest = text.split("## 测试 Seam", 1)
        security = security.replace("TEST-DESIGN-SEC-001", "TEST-NOT-DECLARED", 1)
        path.write_text(security + "## 测试 Seam" + rest, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("linked row references unknown Test(s): TEST-NOT-DECLARED", result.stdout)

    def test_security_row_rejects_missing_test(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        security, rest = text.split("## 测试 Seam", 1)
        security = security.replace("| TEST-DESIGN-SEC-001 |", "| |", 1)
        path.write_text(security + "## 测试 Seam" + rest, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("every SEC row must link TEST", result.stdout)

    def test_rule_traceability_is_checked_in_all_sections(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "### 核心设计结论",
            "| RULE-GOV-OUTSIDE | 跨章节规则 | validator | SPEC-NOT-FOUND | TEST-DESIGN-001 |\n\n### 核心设计结论",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("linked row references unknown Spec(s): SPEC-NOT-FOUND", result.stdout)

    def test_review_design_rejects_placeholder(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace("## 方案概览", "## 方案概览\n\nTODO: later", 1)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("contains placeholder", result.stdout)

    def test_review_design_rejects_todo_adjacent_to_chinese(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace("## 方案概览", "## 方案概览\n\nTODO补写", 1)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("contains placeholder 'TODO'", result.stdout)

    def test_scaffolding_and_empty_table_row_are_not_meaningful(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        replacement = """## 失败、补偿与回滚

### 事务、一致性、并发与幂等

| FAIL ID | 失败点 | 系统状态 | 用户结果 | 补偿/重试/幂等 |
|---|---|---|---|---|
|   |   |   |   |   |

### 回滚方案

"""
        text, count = re.subn(
            r"## 失败、补偿与回滚\n.*?(?=## 迁移方案)",
            replacement,
            text,
            count=1,
            flags=re.S,
        )
        self.assertEqual(1, count)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("section ## 失败、补偿与回滚 has no meaningful content", result.stdout)

    def test_required_heading_inside_fence_does_not_count(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace("## 迁移方案", "### 迁移细节", 1)
        text = text.replace(
            "## 备选方案与权衡",
            "```markdown\n## 迁移方案\nMIG-GOV-FAKE：围栏中的伪章节。\n```\n\n## 备选方案与权衡",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing section ## 迁移方案", result.stdout)

    def test_indented_unclosed_fence_hides_required_heading(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace("## 迁移方案", "### 迁移细节", 1)
        text = text.replace(
            "## 备选方案与权衡",
            "   ```markdown\n## 迁移方案\nMIG-GOV-FAKE：未闭合围栏中的伪章节。\n\n## 备选方案与权衡",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing section ## 迁移方案", result.stdout)

    def test_approved_spec_gate_enforces_complete_draft_change(self) -> None:
        root = copy_repo(self)
        change_path = root / CHANGE / "change.yaml"
        change = yaml.safe_load(change_path.read_text(encoding="utf-8"))
        change["status"] = "draft"
        change_path.write_text(yaml.safe_dump(change, allow_unicode=True, sort_keys=False), encoding="utf-8")

        design_path = root / CHANGE / "design.md"
        update_frontmatter(design_path, lambda data: data.update({"status": "approved", "open_questions": 1}))
        text = design_path.read_text(encoding="utf-8").replace(
            "无阻断性开放问题。",
            "OPEN-GOV-DESIGN-TEST：尚未关闭的阻断问题。",
            1,
        )
        design_path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("approved Change or Spec Gate requires open_questions: 0", result.stdout)

    def test_open_question_count_must_match(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        update_frontmatter(path, lambda data: data.update({"open_questions": 1}))
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("open_questions=1 but found 0", result.stdout)

    def test_open_ids_are_counted_across_entire_design(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 安全与隐私",
            "## 安全与隐私\n\nOPEN-SEC-001：尚未关闭的安全问题。",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("open_questions=0 but found 1 OPEN IDs", result.stdout)

    def test_generator_initializes_design_contract(self) -> None:
        root = copy_repo(self)
        result = subprocess.run(
            [
                sys.executable,
                "tools/new_change.py",
                "CHG-0098",
                "design-sample",
                "--type",
                "engineering",
                "--issue",
                "98",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = root / "changes/CHG-0098-design-sample"
        change = yaml.safe_load((target / "change.yaml").read_text(encoding="utf-8"))
        self.assertEqual(1, change["design_contract_version"])
        design = (target / "design.md").read_text(encoding="utf-8")
        self.assertIn("change: CHG-0098", design)
        self.assertIn("contract_version: 1", design)


if __name__ == "__main__":
    unittest.main()
