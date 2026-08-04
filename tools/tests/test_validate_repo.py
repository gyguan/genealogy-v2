from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class RepositoryValidationTests(unittest.TestCase):
    def copy_repo(self) -> Path:
        target = Path(tempfile.mkdtemp(prefix="genealogy-validation-")) / "repo"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        self.addCleanup(lambda: shutil.rmtree(target.parent, ignore_errors=True))
        return target

    def run_validation(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-c", "import subprocess,sys; a=subprocess.run([sys.executable, 'tools/validate_repo.py']); b=subprocess.run([sys.executable, 'tools/validate_product.py']); raise SystemExit(a.returncode or b.returncode)"],
            cwd=root, text=True, capture_output=True, check=False,
        )

    def load_yaml(self, path: Path) -> dict:
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def save_yaml(self, path: Path, data: dict) -> None:
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def test_current_repository_passes(self) -> None:
        result = self.run_validation(ROOT)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_implementing_change_requires_implementation_gate(self) -> None:
        root = self.copy_repo()
        path = root / "changes/CHG-0001-close-directory-review-findings/change.yaml"
        text = path.read_text(encoding="utf-8").replace("implementation_approval:\n    status: approved", "implementation_approval:\n    status: blocked", 1)
        path.write_text(text, encoding="utf-8")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires approved implementation_approval", result.stdout)

    def test_unknown_domain_dependency_is_rejected(self) -> None:
        root = self.copy_repo()
        path = root / "domains/context-map.yaml"
        data = self.load_yaml(path)
        data["contexts"][0].setdefault("dependencies", []).append({"target": "unknown-domain", "type": "identity-reference"})
        self.save_yaml(path, data)
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown domain", result.stdout)

    def test_domain_file_cannot_duplicate_dependencies(self) -> None:
        root = self.copy_repo()
        path = root / "domains/person-registry.md"
        text = path.read_text(encoding="utf-8").replace("status: draft", "status: draft\ndepends_on: []", 1)
        path.write_text(text, encoding="utf-8")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("dependencies belong only", result.stdout)

    def test_task_cannot_reference_unknown_spec(self) -> None:
        root = self.copy_repo()
        path = root / "changes/CHG-0001-close-directory-review-findings/tasks.md"
        text = path.read_text(encoding="utf-8").replace("Specs: SPEC-GOV-001", "Specs: SPEC-MISSING-999", 1)
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

    def test_unknown_capability_dependency_is_rejected(self) -> None:
        root = self.copy_repo()
        path = root / "product/capabilities/person.yaml"
        data = self.load_yaml(path)
        data["group"]["capabilities"][0]["depends_on"] = ["CAP-MISSING-999"]
        self.save_yaml(path, data)
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("depends on unknown capability", result.stdout)

    def test_later_release_dependency_is_rejected(self) -> None:
        root = self.copy_repo()
        path = root / "product/capabilities/portability.yaml"
        data = self.load_yaml(path)
        data["group"]["capabilities"][0]["depends_on"] = ["CAP-PLATFORM-011"]
        self.save_yaml(path, data)
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("depends on later capability", result.stdout)

    def test_capability_dependency_cycle_is_rejected(self) -> None:
        root = self.copy_repo()
        path = root / "product/capabilities/person.yaml"
        data = self.load_yaml(path)
        data["group"]["capabilities"][0]["depends_on"] = ["CAP-PERSON-002"]
        self.save_yaml(path, data)
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("dependency cycle", result.stdout)

    def test_invalid_primary_domain_is_rejected(self) -> None:
        root = self.copy_repo()
        path = root / "product/capabilities/query.yaml"
        data = self.load_yaml(path)
        data["group"]["capabilities"][0]["primary_domain"] = "unknown-domain"
        self.save_yaml(path, data)
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid primary_domain", result.stdout)

    def test_unlisted_capability_file_is_rejected(self) -> None:
        root = self.copy_repo()
        shutil.copyfile(root / "product/capabilities/person.yaml", root / "product/capabilities/unlisted.yaml")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("capability file is not listed", result.stdout)

    def test_roadmap_requires_success_metrics(self) -> None:
        root = self.copy_repo()
        path = root / "product/roadmap.md"
        path.write_text(path.read_text(encoding="utf-8").replace("### 成功指标", "### 指标待补充", 1), encoding="utf-8")
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("V0.1 missing section ### 成功指标", result.stdout)

    def test_candidate_requires_low_confidence(self) -> None:
        root = self.copy_repo()
        path = root / "product/capabilities/ecosystem.yaml"
        data = self.load_yaml(path)
        data["group"]["capabilities"][0]["planning_confidence"] = "high"
        self.save_yaml(path, data)
        result = self.run_validation(root)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("candidate CAP-ECOSYSTEM-001 must have low", result.stdout)


if __name__ == "__main__":
    unittest.main()
