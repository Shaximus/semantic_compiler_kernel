"""Translation module - nouns, functions, relationships, failure modes, public, fractal."""

from semantic_compiler.translation.buildcraft import (
    resolve_buildcraft_entries,
    resolve_buildcraft_mappings,
    summarize_buildcraft_ontology,
)

__all__ = [
    "resolve_buildcraft_entries",
    "resolve_buildcraft_mappings",
    "summarize_buildcraft_ontology",
]
