from __future__ import annotations

import re
import unittest

import yaml

from validation_test_utils import ROOT, copy_repo, run


class RepositoryValidationTests(unittest.TestCase):
    def test_current_repository_passes(self) -> None:
        result = run(ROOT, "tools/validate_repo.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_v2_approved_gate_requires_source(self) -> None:
        root = copy_repo(self)
        path = root / "changes/CHG-0004-v01-recovery-loop/change.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["gates"]["spec_review"]["source"] = None
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_repo.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("needs source", result.stdout)

    def test_product_change_requires_high_risk_profile(self) -> None:
        root = copy_repo(self)
        path = root / "changes/CHG-0004-v01-recovery-loop/change.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["change_profile"] = "standard"
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_repo.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must use high-risk", result.stdout)

    def test_active_change_requires_tasks(self) -> None:
        root = copy_repo(self)
        path = root / "changes/CHG-0004-v01-recovery-loop/tasks.md"
        path.write_text("# Tasks\n", encoding="utf-8")
        result = run(root, "tools/validate_repo.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("change needs Tasks", result.stdout)

    def test_active_spec_requires_requirement_id(self) -> None:
        root = copy_repo(self)
        path = root / "changes/CHG-0004-v01-recovery-loop/specs/product.md"
        path.write_text("# Product Spec Delta\n\n<!-- placeholder -->\n", encoding="utf-8")
        result = run(root, "tools/validate_repo.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("no SPEC id found", result.stdout)

    def test_decision_introduced_by_requires_existing_change(self) -> None:
        root = copy_repo(self)
        path = sorted((root / "decisions").glob("DEC-*.md"))[0]
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"^introduced_by:\s*CHG-\d{4}\s*$", "introduced_by: CHG-9999", text, count=1, flags=re.M)
        path.write_text(text, encoding="utf-8")
        result = run(root, "tools/validate_repo.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("introduced_by references unknown Change CHG-9999", result.stdout)

    def test_change_template_requires_all_generator_assets(self) -> None:
        root = copy_repo(self)
        (root / "changes/_template/design.md").unlink()
        result = run(root, "tools/validate_repo.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing required file: changes/_template/design.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
