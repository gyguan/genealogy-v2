from __future__ import annotations

import unittest

import yaml

from validation_test_utils import ROOT, copy_repo, run


class RepositoryLayoutValidationTests(unittest.TestCase):
    def test_current_repository_passes(self) -> None:
        result = run(ROOT, "tools/validate_layout.py")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_capability_manifest_rejects_unknown_projection_field(self) -> None:
        root = copy_repo(self)
        path = root / "product/capability-map.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["compatibility_projection"] = {"capabilities": []}
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        result = run(root, "tools/validate_layout.py")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown top-level fields are forbidden", result.stdout)
        self.assertIn("compatibility_projection", result.stdout)

    def test_obsolete_repository_paths_are_rejected(self) -> None:
        for relative_path in ("ai", "knowledge", "changes/active", "changes/archived"):
            with self.subTest(relative_path=relative_path):
                root = copy_repo(self)
                (root / relative_path).mkdir(parents=True, exist_ok=True)
                result = run(root, "tools/validate_layout.py")
                self.assertNotEqual(0, result.returncode)
                self.assertIn(
                    f"obsolete repository path is forbidden: {relative_path}",
                    result.stdout,
                )


if __name__ == "__main__":
    unittest.main()
