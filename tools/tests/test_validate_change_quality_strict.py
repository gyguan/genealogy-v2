from __future__ import annotations

import re
import unittest

from validation_test_utils import ROOT, copy_repo, run


CHANGE = "changes/CHG-0006-diagnostic-governance"
SCRIPT = "tools/validate_change_quality_strict.py"


class StrictChangeQualityEdgeTests(unittest.TestCase):
    def test_current_repository_passes_hardened_entrypoint(self) -> None:
        result = run(ROOT, SCRIPT)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_spec_readme_is_ignored(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "specs/README.md"
        path.write_text("# Spec authoring guide\n\nThis file contains no requirements.\n", encoding="utf-8")
        result = run(root, SCRIPT)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_titleless_scenario_preserves_given_line(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "specs/repository-governance.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"^#### Scenario SCN-GOV-007-01[^\n]*$",
            "#### Scenario SCN-GOV-007-01",
            text,
            count=1,
            flags=re.M,
        )
        path.write_text(text, encoding="utf-8")
        result = run(root, SCRIPT)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("SPEC-SCENARIO-003", result.stdout)

    def test_requirement_outside_action_section_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "specs/repository-governance.md"
        text = path.read_text(encoding="utf-8").replace("## ADDED", "## Notes", 1)
        path.write_text(text + "\n## ADDED\n", encoding="utf-8")
        result = run(root, SCRIPT)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SPEC-FORMAT-003", result.stdout)

    def test_task_template_example_is_not_parsed_as_a_task(self) -> None:
        root = copy_repo(self)
        tasks = root / CHANGE / "tasks.md"
        template = (root / "changes/_template/tasks.md").read_text(encoding="utf-8")
        tasks.write_text(tasks.read_text(encoding="utf-8") + "\n" + template, encoding="utf-8")

        repository_result = run(root, "tools/validate_repo.py")
        self.assertEqual(
            0,
            repository_result.returncode,
            repository_result.stdout + repository_result.stderr,
        )
        quality_result = run(root, SCRIPT)
        self.assertEqual(0, quality_result.returncode, quality_result.stdout + quality_result.stderr)


if __name__ == "__main__":
    unittest.main()
