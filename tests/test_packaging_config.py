"""pyproject.toml must ship every package and data file the code loads at import/run time.

The V3.0.0 wheel omitted ``expansion.gem_decode`` and ``expansion.gem_forge`` (imported
unconditionally by ``expansion/__init__``), the 19 domain templates and the gem corpus
snapshot, so ``import semantic_compiler.expansion`` raised ModuleNotFoundError after install.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    tomllib = None


@unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
class PackagingConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = tomllib.loads((REPO / "pyproject.toml").read_text())
        cls.setuptools = cls.config["tool"]["setuptools"]

    def test_every_package_directory_is_listed(self) -> None:
        listed = set(self.setuptools["packages"])
        found = {"semantic_compiler"}
        for init in REPO.rglob("__init__.py"):
            relative = init.parent.relative_to(REPO)
            if not relative.parts or relative.parts[0] in {"tests", "scripts", "build"}:
                continue
            found.add("semantic_compiler." + ".".join(relative.parts))
        self.assertEqual(found - listed, set(), "package directories missing from pyproject")
        self.assertEqual(listed - found, set(), "pyproject lists packages that do not exist")

    def test_runtime_data_files_are_covered_by_package_data(self) -> None:
        data = self.setuptools["package-data"]
        self.assertIn("templates/*.yaml", data["semantic_compiler.expansion"])
        self.assertIn("schemas/*.json", data["semantic_compiler.expansion"])
        self.assertIn("data/*.json", data["semantic_compiler.expansion.gem_forge"])
        self.assertIn("schemas/*.json", data["semantic_compiler"])
        # The globs must match files that exist.
        self.assertTrue(list((REPO / "expansion" / "templates").glob("*.yaml")))
        self.assertTrue(list((REPO / "expansion" / "gem_forge" / "data").glob("*.json")))
        self.assertTrue(list((REPO / "expansion" / "schemas").glob("*.json")))
        self.assertTrue(list((REPO / "schemas").glob("*.json")))


if __name__ == "__main__":
    unittest.main()
