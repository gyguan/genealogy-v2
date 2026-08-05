from __future__ import annotations

import subprocess
import sys
import unittest

import yaml

from validation_test_utils import ROOT, copy_repo, run

CHANGE = "changes/CHG-0008-design-contract-v1-1"


class MachineDesignValidationTests(unittest.TestCase):
    def test_current_repository_passes(self) -> None:
        result = run(ROOT, "tools/validate_design_machine.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_template_machine_contract_is_validated(self) -> None:
        root = copy_repo(self)
        path = root / "changes/_template/design.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["facets"].pop("events")
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_design_machine.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing facets: events", result.stdout)

    def test_review_required_must_be_resolved_before_review(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["facets"]["events"] = {"status": "review-required", "reason": "仍需要判断是否存在事件协作", "design_ids": []}
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_design_machine.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("facet events must be resolved before review", result.stdout)

    def test_fact_requires_source(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["facts"][0].pop("source")
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_design_machine.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("needs a source object", result.stdout)

    def test_traceability_test_must_cover_spec(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["traceability"][0]["tests"] = ["TEST-DESIGN-V11-004"]
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_design_machine.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not cover spec", result.stdout)

    def test_blocking_assumption_must_be_resolved(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["assumptions"].append({"id": "ASM-GOV-V11-BLOCKING", "statement": "该阻断假设尚未获得任何正式确认", "status": "proposed", "blocking": True})
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = run(root, "tools/validate_design_machine.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must be resolved before review", result.stdout)


class DesignV11ToolingTests(unittest.TestCase):
    def test_new_change_creates_machine_contract(self) -> None:
        root = copy_repo(self)
        result = subprocess.run(
            [sys.executable, "tools/new_change.py", "CHG-0099", "sample-engineering", "--type", "engineering", "--issue", "15"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        change_dir = root / "changes/CHG-0099-sample-engineering"
        machine = yaml.safe_load((change_dir / "design.yaml").read_text(encoding="utf-8"))
        change = yaml.safe_load((change_dir / "change.yaml").read_text(encoding="utf-8"))
        self.assertEqual(1, change["design_machine_contract_version"])
        self.assertEqual("review-required", machine["facets"]["events"]["status"])
        self.assertEqual("required", machine["facets"]["security_privacy"]["status"])

    def test_context_bundle_is_machine_readable(self) -> None:
        result = subprocess.run(
            [sys.executable, "tools/context.py", "CHG-0008", "--bundle"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        bundle = yaml.safe_load(result.stdout)
        self.assertEqual("CHG-0008", bundle["change"]["id"])
        self.assertIn("machine_design", bundle)
        self.assertIn("global_constraints", bundle)


if __name__ == "__main__":
    unittest.main()
