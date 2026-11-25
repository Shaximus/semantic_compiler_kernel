"""Registry domain inventory must match on-disk YAML templates."""

from __future__ import annotations

import unittest

from semantic_compiler.expansion.registry import list_domains

from tests.domain_inventory import (
    on_disk_domain_stems,
    registered_domain_count,
)


class DomainInventoryTests(unittest.TestCase):
    def test_list_domains_matches_on_disk_yaml_stems(self) -> None:
        stems = on_disk_domain_stems()
        self.assertTrue(stems, "expansion/templates/ must contain YAML templates")
        self.assertEqual(set(list_domains()), stems)
        self.assertIn("universal_generic", stems)
        self.assertEqual(registered_domain_count(), len(stems))


if __name__ == "__main__":
    unittest.main()
