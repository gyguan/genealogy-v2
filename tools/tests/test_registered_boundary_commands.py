from __future__ import annotations

import subprocess
import sys
import unittest

try:
    from .validation_test_utils import ROOT
except ImportError:
    from validation_test_utils import ROOT


class RegisteredBoundaryCommandTests(unittest.TestCase):
    def test_registered_class_commands_run_from_repository_root(self) -> None:
        classes = (
            "DecisionScopeBoundaryTests",
            "SpecVisibilityBoundaryTests",
            "DesignParagraphBoundaryTests",
        )
        for class_name in classes:
            with self.subTest(class_name=class_name):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "unittest",
                        f"tools.tests.test_governance_validator_boundaries.{class_name}",
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
