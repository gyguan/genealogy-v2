from __future__ import annotations

import sys
import unittest

try:
    from .validation_test_utils import ROOT, copy_repo, run
except ImportError:  # unittest discovery imports this file as a top-level module
    from validation_test_utils import ROOT, copy_repo, run

sys.path.insert(0, str(ROOT / "tools"))
from diagnostics import Reporter  # noqa: E402
from validate_pr_change_strict import (  # noqa: E402
    required_change_types,
    validate_declared_scope,
)

QUALITY_CHANGE = "changes/CHG-0006-diagnostic-governance"
DESIGN_CHANGE = "changes/CHG-0007-requirement-design-contract"


def decision_text(decision_id: str, decision_type: str) -> str:
    return (
        "---\n"
        f"id: {decision_id}\n"
        f"type: {decision_type}\n"
        "status: accepted\n"
        "affected_domains: []\n"
        "introduced_by: CHG-0004\n"
        "supersedes: []\n"
        "effective_at: 2026-08-05\n"
        "---\n\n"
        "# Decision\n"
    )


class DecisionScopeBoundaryTests(unittest.TestCase):
    def test_canonical_architecture_and_compliance_types_are_supported(self) -> None:
        root = copy_repo(self)
        architecture = root / "decisions/DEC-9998-architecture-test.md"
        compliance = root / "decisions/DEC-9999-compliance-test.md"
        architecture.write_text(decision_text("DEC-9998", "architecture"), encoding="utf-8")
        compliance.write_text(decision_text("DEC-9999", "compliance"), encoding="utf-8")

        self.assertEqual(
            {"engineering"},
            required_change_types(root, str(architecture.relative_to(root)), Reporter()),
        )
        self.assertEqual(
            {"governance", "security"},
            required_change_types(root, str(compliance.relative_to(root)), Reporter()),
        )

    def test_decision_readme_is_governance_documentation(self) -> None:
        reporter = Reporter()
        required = required_change_types(ROOT, "decisions/README.md", reporter)
        self.assertEqual({"governance"}, required)
        self.assertFalse(reporter.errors, reporter.render("test"))

    def test_removed_decision_reads_type_from_base_content(self) -> None:
        root = copy_repo(self)
        removed = {
            "filename": "decisions/DEC-9999-removed.md",
            "status": "removed",
            "base_content": decision_text("DEC-9999", "product"),
        }
        reporter = Reporter()
        validate_declared_scope(root, "- Change ID：CHG-0006", [removed], reporter)
        self.assertFalse(any(item.code == "PR-DECISION-001" for item in reporter.errors))
        self.assertTrue(any(item.code == "PR-SCOPE-002" for item in reporter.errors))

    def test_renamed_decision_validates_both_base_and_head_metadata(self) -> None:
        root = copy_repo(self)
        new_path = root / "decisions/DEC-9999-new-name.md"
        new_path.write_text(decision_text("DEC-9999", "product"), encoding="utf-8")
        renamed = {
            "filename": "decisions/DEC-9999-new-name.md",
            "previous_filename": "decisions/DEC-9999-old-name.md",
            "status": "renamed",
            "base_content": decision_text("DEC-9999", "product"),
        }
        reporter = Reporter()
        validate_declared_scope(root, "- Change ID：CHG-0004", [renamed], reporter)
        self.assertFalse(reporter.errors, reporter.render("test"))


class SpecVisibilityBoundaryTests(unittest.TestCase):
    def test_fenced_spec_example_is_not_parsed_as_formal_structure(self) -> None:
        root = copy_repo(self)
        path = root / QUALITY_CHANGE / "specs/repository-governance.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n```markdown\n"
            + "## SPEC-EXAMPLE-NOT-FORMAL\n"
            + "#### Scenario SCN-EXAMPLE-NOT-FORMAL\n"
            + "```\n",
            encoding="utf-8",
        )
        result = run(root, "tools/validate_change_quality_strict.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("SPEC-EXAMPLE-NOT-FORMAL", result.stdout)


class DesignParagraphBoundaryTests(unittest.TestCase):
    def test_non_one_ordered_marker_stays_inside_lazy_quote(self) -> None:
        root = copy_repo(self)
        path = root / DESIGN_CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("MIG-GOV-DESIGN-001", "MIGRATION-GOV-DESIGN-001", 1)
        text = text.replace(
            "## 迁移方案\n\n",
            """## 迁移方案

> quoted migration paragraph
2. MIG-GOV-QUOTED-002：该 ID 仍属于引用段落。

""",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("required facet migration needs stable ID", result.stdout)

    def test_text_bearing_list_item_keeps_type7_html_in_paragraph(self) -> None:
        root = copy_repo(self)
        path = root / DESIGN_CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("MIG-GOV-DESIGN-001", "MIGRATION-GOV-DESIGN-001", 1)
        text = text.replace(
            "## 迁移方案\n\n",
            """## 迁移方案

- rendered migration paragraph
  <widget>
  MIG-GOV-LIST-001：该 ID 是列表项段落中的可见设计内容。

""",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
