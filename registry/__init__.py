"""Registry module - term registry, rules, departments, isomorphisms, negative samples."""

from semantic_compiler.registry.buildcraft import (
    BUILDCRAFT_MAPPINGS,
    BuildcraftMapping,
    get_buildcraft_mapping,
)

__all__ = [
    "BUILDCRAFT_MAPPINGS",
    "BuildcraftMapping",
    "get_buildcraft_mapping",
]
