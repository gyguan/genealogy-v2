from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RepositoryValidationTests(unittest.TestCase):
    def copy_repo(self) -> Path:
        target = Path(tempfile.mkdtemp(prefix="genealogy-validation-")) / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        self.addCleanup(lambda: shutil.rmtree(target.parent, ignore_errors=True))
        return target

    def run_validation(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "tools/validate_repo.py"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_current_repository_passes(self) -> None:
        result = self.run_validation(ROOT)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_implementing_change_requires_implementation_gate(self) -> None:
        root = self.copy_repo()
        path = root / "changes/CHG-0001-close-directory-review-findings/change.yaml"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "implementation_approval:\n    status: approved",
            "implementation_approval:\n    status: blocked",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires approved implementation_approval", result.stdout)

    def test_unknown_domain_dependency_is_rejected(self) -> None:
        root = self.copy_repo()
        path = root / "domains/context-map.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "target: person-registry", "target: unknown-domain", 1
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown domain", result.stdout)

    def test_domain_file_cannot_duplicate_dependencies(self) -> None:
        root = self.copy_repo()
        path = root / "domains/person-registry.md"
        text = path.read_text(encoding="utf-8").replace(
            "status: draft", "status: draft\ndepends_on: []", 1
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("dependencies belong only", result.stdout)

    def test_task_cannot_reference_unknown_spec(self) -> None:
        root = self.copy_repo()
        path = root / "changes/CHG-0001-close-directory-review-findings/tasks.md"
        text = path.read_text(encoding="utf-8").replace(
            "Specs: SPEC-GOV-001", "Specs: SPEC-MISSING-999", 1
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("references unknown Spec", result.stdout)

    def test_completed_task_requires_existing_evidence(self) -> None:
        root = self.copy_repo()
        (root / "changes/CHG-0001-close-directory-review-findings/evidence/TASK-0001.md").unlink()
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("evidence does not exist", result.stdout)


if __name__ == "__main__":
    unittest.main()
