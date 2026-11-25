"""Helpers so tests derive the domain inventory from the registry, not a hardcoded count."""

from __future__ import annotations

from semantic_compiler.expansion.registry import list_domains
from semantic_compiler.expansion.registry.loader import TEMPLATE_DIR


def on_disk_domain_stems() -> frozenset[str]:
    """Stems of every ``expansion/templates/*.yaml`` file."""
    return frozenset(path.stem for path in TEMPLATE_DIR.glob("*.yaml"))


def registered_domains() -> list[str]:
    return list(list_domains())


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


def registered_domain_count() -> int:
    return len(assert_registry_matches_templates())
