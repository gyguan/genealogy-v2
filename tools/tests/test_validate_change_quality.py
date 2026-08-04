from __future__ import annotations

import re
import unittest

import yaml

from validation_test_utils import ROOT, copy_repo, run


CHANGE = "changes/CHG-0006-diagnostic-governance"


class ChangeQualityValidationTests(unittest.TestCase):
    def test_current_repository_has_no_quality_errors(self) -> None:
        result = run(ROOT, "tools/validate_change_quality.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("review-only=", result.stdout)

    def test_strict_change_rejects_empty_required_section(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "proposal.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(## 目标\n).*?(?=\n## )", r"\1", text, count=1, flags=re.S)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_change_quality.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("CHG-DOC-003", result.stdout)

    def test_legacy_empty_section_is_a_warning(self) -> None:
        root = copy_repo(self)
        metadata_path = root / CHANGE / "change.yaml"
        data = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        data.pop("quality_policy", None)
        metadata_path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        proposal_path = root / CHANGE / "proposal.md"
        text = proposal_path.read_text(encoding="utf-8")
        text = re.sub(r"(## 目标\n).*?(?=\n## )", r"\1", text, count=1, flags=re.S)
        proposal_path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_change_quality.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("CHG-MIGRATION-002", result.stdout)

    def test_strict_spec_requires_requirement_content(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "specs/repository-governance.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"(## SPEC-GOV-007[^\n]*\n#### Requirement\n).*?(?=\n#### Scenario)",
            r"\1",
            text,
            count=1,
            flags=re.S,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_change_quality.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SPEC-CONTENT-001", result.stdout)

    def test_strict_spec_requires_scenario(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "specs/repository-governance.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"\n#### Scenario SCN-GOV-007-01[\s\S]*?(?=\n## SPEC-|\Z)",
            "",
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_change_quality.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SPEC-SCENARIO-001", result.stdout)

    def test_duplicate_scenario_across_spec_files_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "specs/extra.md"
        path.write_text(
            "# Extra Spec Delta\n\n"
            "## ADDED\n\n"
            "## SPEC-GOV-099 Extra requirement\n"
            "#### Requirement\n"
            "Provide an additional observable requirement.\n\n"
            "#### Scenario SCN-GOV-007-01 Duplicate scenario\n"
            "- Given: a duplicate identifier\n"
            "- When: strict validation runs\n"
            "- Then: validation fails\n",
            encoding="utf-8",
        )
        result = run(root, "tools/validate_change_quality.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SPEC-SCENARIO-004", result.stdout)

    def test_strict_task_test_reference_must_exist(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "tasks.md"
        text = path.read_text(encoding="utf-8").replace(
            "- Tests: TEST-GOV-DIAGNOSTICS-001",
            "- Tests: TEST-UNKNOWN-999",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_change_quality.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("TASK-TEST-001", result.stdout)

    def test_every_strict_spec_must_have_test_coverage(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "tests.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for item in data["tests"]:
            item["specs"] = [value for value in item["specs"] if value != "SPEC-GOV-008"]
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_change_quality.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("TRACE-SPEC-TEST-001", result.stdout)

    def test_warning_does_not_fail_validation(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "change.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data.pop("quality_policy", None)
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_change_quality.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("CHG-MIGRATION-001", result.stdout)
        self.assertIn("WARNING", result.stdout)


if __name__ == "__main__":
    unittest.main()
