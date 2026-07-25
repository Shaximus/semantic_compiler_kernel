"""Gem Forge — bidirectional PoE gem / inference mechanic synthesis.

Public operations:

- ``load_gem_corpus``: ingest a pinned all-gems snapshot.
- ``translate_gem`` / ``translate_corpus``: preserve PoE wording and generate
  line-by-line inference translations.
- ``forge_component``: identify all relevant gem traits in an LLM software
  component and emit a composite or novel inference gem.
- ``multi_source``: merge pinned corpora from independent sources with
  per-source provenance and side-by-side wording diffs (never averaged).
- ``converter_families``: name the converter family that would resolve every
  PARTIAL/UNRESOLVED line (no generic buckets).
- ``composite_attribution``: per-primitive, line-by-line provenance for
  composite syntheses, with single-primitive-composite floor verification.
"""
from semantic_compiler.expansion.gem_forge.composite_attribution import (
    CompositeAttribution,
    PrimitiveContributor,
    attribute_composite,
    floor_violations,
)
from semantic_compiler.expansion.gem_forge.converter_families import (
    CONVERTER_FAMILY_RULES,
    UnmatchedLine,
    build_family_registry,
    classify_line,
)
from semantic_compiler.expansion.gem_forge.corpus import (
    CorpusPinError,
    dump_normalized_corpus,
    load_gem_corpus,
    load_gem_corpus_file,
    load_pinned_corpus,
)
from semantic_compiler.expansion.gem_forge.forge import forge_component, match_component
from semantic_compiler.expansion.gem_forge.multi_source import (
    MergeResult,
    MergedGem,
    ProvenancedSource,
    SourceProvenance,
    WordingDiff,
    load_provenanced_source,
    merge_sources,
    provenance_report,
    wording_diff_records,
)
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
    PRIMITIVE_ALIASES,
    RELATIONSHIP_TYPES,
    canonical_primitive,
    canonical_primitives,
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
    "load_pinned_corpus",
    "CorpusPinError",
    "dump_normalized_corpus",
    "translate_gem",
    "translate_corpus",
    "match_component",
    "forge_component",
    "SourceProvenance",
    "ProvenancedSource",
    "WordingDiff",
    "MergedGem",
    "MergeResult",
    "load_provenanced_source",
    "merge_sources",
    "wording_diff_records",
    "provenance_report",
    "CONVERTER_FAMILY_RULES",
    "UnmatchedLine",
    "classify_line",
    "build_family_registry",
    "CompositeAttribution",
    "PrimitiveContributor",
    "attribute_composite",
    "floor_violations",
    "extract_primitives",
    "extract_domains",
    "canonical_primitive",
    "canonical_primitives",
    "PRIMITIVE_ALIASES",
    "DEPLOYMENT_SLOTS",
    "CAPABILITY_DOMAINS",
    "MECHANIC_PRIMITIVES",
    "RELATIONSHIP_TYPES",
]
