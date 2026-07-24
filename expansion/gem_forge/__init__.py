"""Gem Forge — bidirectional PoE gem / inference mechanic synthesis.

Public operations:

- ``load_gem_corpus``: ingest a pinned all-gems snapshot.
- ``translate_gem`` / ``translate_corpus``: preserve PoE wording and generate
  line-by-line inference translations.
- ``forge_component``: identify all relevant gem traits in an LLM software
  component and emit a composite or novel inference gem.
"""
from semantic_compiler.expansion.gem_forge.corpus import (
    dump_normalized_corpus,
    load_gem_corpus,
    load_gem_corpus_file,
)
from semantic_compiler.expansion.gem_forge.forge import forge_component, match_component
from semantic_compiler.expansion.gem_forge.models import (
    ForgeResult,
    GemMatch,
    GemTranslation,
    LineTranslation,
    PoeGem,
    SoftwareComponent,
    SyntheticGem,
)
from semantic_compiler.expansion.gem_forge.taxonomy import (
    CAPABILITY_DOMAINS,
    DEPLOYMENT_SLOTS,
    MECHANIC_PRIMITIVES,
    RELATIONSHIP_TYPES,
    extract_domains,
    extract_primitives,
)
from semantic_compiler.expansion.gem_forge.translator import translate_corpus, translate_gem

__all__ = [
    "PoeGem",
    "SoftwareComponent",
    "LineTranslation",
    "GemTranslation",
    "GemMatch",
    "SyntheticGem",
    "ForgeResult",
    "load_gem_corpus",
    "load_gem_corpus_file",
    "dump_normalized_corpus",
    "translate_gem",
    "translate_corpus",
    "match_component",
    "forge_component",
    "extract_primitives",
    "extract_domains",
    "DEPLOYMENT_SLOTS",
    "CAPABILITY_DOMAINS",
    "MECHANIC_PRIMITIVES",
    "RELATIONSHIP_TYPES",
]
