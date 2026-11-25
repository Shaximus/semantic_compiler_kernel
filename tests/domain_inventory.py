"""Helpers so tests check the domain inventory against a checked-in expected list.

The registry-vs-on-disk-YAML comparison is kept so a loader/registry mismatch
still fails. The expected-name list is what makes a lost or added template
fail: comparing ``list_domains()`` only to the YAML directory would still
pass if a file disappeared from both views together.
"""

from __future__ import annotations

from pathlib import Path

from semantic_compiler.expansion.registry import list_domains
from semantic_compiler.expansion.registry.loader import TEMPLATE_DIR

EXPECTED_DOMAINS_PATH = Path(__file__).resolve().parent / "expected_domains.txt"


def on_disk_domain_stems() -> frozenset[str]:
    """Stems of every ``expansion/templates/*.yaml`` file."""
    return frozenset(path.stem for path in TEMPLATE_DIR.glob("*.yaml"))


def registered_domains() -> list[str]:
    return list(list_domains())


def expected_domain_stems() -> frozenset[str]:
    """Names listed in ``tests/expected_domains.txt`` (comments and blanks ignored)."""
    names: set[str] = set()
    text = EXPECTED_DOMAINS_PATH.read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        names.add(line)
    return frozenset(names)


def assert_registry_matches_templates() -> frozenset[str]:
    """Return on-disk stems, raising if ``list_domains()`` disagrees."""
    stems = on_disk_domain_stems()
    registered = frozenset(registered_domains())
    if registered != stems:
        raise AssertionError(
            "list_domains() does not match on-disk YAML templates: "
            f"only_registered={sorted(registered - stems)} "
            f"only_on_disk={sorted(stems - registered)}"
        )
    return stems


def assert_inventory_matches_expected() -> frozenset[str]:
    """Registry, on-disk YAML, and the checked-in expected list must be identical."""
    stems = assert_registry_matches_templates()
    expected = expected_domain_stems()
    if stems != expected:
        raise AssertionError(
            "domain inventory does not match tests/expected_domains.txt: "
            f"only_on_disk_or_registered={sorted(stems - expected)} "
            f"only_expected={sorted(expected - stems)}"
        )
    return stems


def registered_domain_count() -> int:
    return len(assert_inventory_matches_expected())
