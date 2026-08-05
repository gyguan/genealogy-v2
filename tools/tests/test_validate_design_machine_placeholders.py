from __future__ import annotations

import unittest

import yaml

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0009-design-contract-v1-1"


class MachineDesignPlaceholderValidationTests(unittest.TestCase):
    def test_review_ready_fact_placeholder_is_rejected(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["facts"][0]["statement"] = "TODO 待确认来源"
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

        result = run(root, "tools/validate_design_machine.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("contains unresolved placeholder", result.stdout)
        self.assertIn("$.facts[0].statement", result.stdout)


if __name__ == "__main__":
    unittest.main()
