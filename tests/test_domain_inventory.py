"""Registry domain inventory must match on-disk YAML and a checked-in expected list."""

from __future__ import annotations

import unittest

from semantic_compiler.expansion.registry import list_domains

from tests.domain_inventory import (
    assert_inventory_matches_expected,
    expected_domain_stems,
    on_disk_domain_stems,
    registered_domain_count,
)


class DomainInventoryTests(unittest.TestCase):
    def test_list_domains_matches_on_disk_yaml_stems(self) -> None:
        stems = on_disk_domain_stems()
        self.assertTrue(stems, "expansion/templates/ must contain YAML templates")
        self.assertEqual(set(list_domains()), stems)
        self.assertIn("universal_generic", stems)

    def test_inventory_matches_checked_in_expected_domain_list(self) -> None:
        expected = expected_domain_stems()
        self.assertTrue(expected, "tests/expected_domains.txt must list domain stems")
        self.assertIn("universal_generic", expected)
        stems = assert_inventory_matches_expected()
        self.assertEqual(stems, expected)
        self.assertEqual(registered_domain_count(), len(expected))
        # A count-only comparison against the live registry would still pass if a
        # template were lost. The expected list is the non-circular pin.
        self.assertEqual(sorted(expected), sorted(on_disk_domain_stems()))


if __name__ == "__main__":
    unittest.main()
