"""Regression tests for the forge matcher floor + primitive aliasing (Harriet review).

DEFECT 1: single-primitive exact-set collisions must not produce score-1.0
COMPOSITE results — they demote to NOVEL with primitives preserved.
DEFECT 2: SHARE_STATE / PERSISTENT_SHARED_MODIFIER vocabulary gap unified.
"""

from semantic_compiler.expansion.gem_forge import (
    SoftwareComponent,
    canonical_primitives,
    forge_component,
    load_pinned_corpus,
    translate_corpus,
)

_TRANSLATIONS = None


def _translations():
    global _TRANSLATIONS
    if _TRANSLATIONS is None:
        _TRANSLATIONS = translate_corpus(load_pinned_corpus())
    return _TRANSLATIONS


# --- DEFECT 1: degenerate cases demote to NOVEL ------------------------------

def test_tokenizer_demotes_to_novel():
    component = SoftwareComponent(
        name="Tokenizer",
        description="Splits raw text into token ids using a fixed vocabulary; deterministic, stateless, and invertible.",
        deployment_slots=("DATA_PIPELINE",),
    )
    result = forge_component(component, _translations())
    assert result.composite_gem.composition == "NOVEL"
    # primitives preserved, never discarded
    assert "FORK_OUTPUT" in result.composite_gem.novel_effects
    assert result.composite_gem.source_gems == ()
    # the degenerate match stays in the record for audit, floor explains demotion
    assert result.record["matcher_floor"]["met"] is False
    assert result.matches  # audit trail retained


def test_quantized_runtime_demotes_to_novel():
    component = SoftwareComponent(
        name="Quantized Inference Runtime",
        description="Quantization runtime: compressed weights reduce persistent reservation and compute cost while preserving output fidelity.",
        deployment_slots=("RUNTIME",),
        capability_domains=("COMPRESSION", "RESOURCE_BUDGETING"),
    )
    result = forge_component(component, _translations())
    assert result.composite_gem.composition == "NOVEL"
    assert result.composite_gem.novel_effects  # primitives preserved
    assert result.record["matcher_floor"]["met"] is False


# --- DEFECT 1: sound cases survive as COMPOSITE ------------------------------

def test_mtp_runtime_survives_as_composite():
    component = SoftwareComponent(
        name="MTP Speculative Runtime",
        description="Multi-token prediction head drafts additional candidate token positions; the verifier accepts or rejects; acceptance rate gates net throughput.",
        deployment_slots=("DRAFT_HEAD", "VERIFIER", "RUNTIME"),
        capability_domains=("SPECULATION", "VERIFICATION"),
    )
    result = forge_component(component, _translations())
    assert result.composite_gem.composition == "COMPOSITE"
    assert result.record["matcher_floor"]["met"] is True
    floor = result.record["matcher_floor"]
    assert len(floor["shared_primitives"]) >= 2 or len(floor["wording_evidence"]) >= 2


def test_qualified_trigger_controller_survives_as_composite():
    component = SoftwareComponent(
        name="Qualified Trigger Controller",
        description="Speculative decoding controller: qualified proposals automatically trigger the expensive verified payload with a cooldown recovery window.",
        deployment_slots=("SCHEDULER", "VERIFIER"),
        capability_domains=("TRIGGERING", "LATENCY_CONTROL"),
    )
    result = forge_component(component, _translations())
    assert result.composite_gem.composition == "COMPOSITE"
    assert result.record["matcher_floor"]["met"] is True


# --- DEFECT 2: vocabulary unification ------------------------------------------

def test_share_state_aliases_to_persistent_shared_modifier():
    assert canonical_primitives(("SHARE_STATE", "PERSISTENT_SHARED_MODIFIER")) == (
        "PERSISTENT_SHARED_MODIFIER",
    )


def test_bcc_component_overlaps_aura_family_primitives():
    """BCC-class shared-memory component must overlap aura gems on the unified
    primitive. Status may still be NOVEL if the floor is unmet — this asserts
    the vocabulary overlap, not the status."""
    component = SoftwareComponent(
        name="BCC Memory Retrieval Layer",
        description="Persistent shared memory field: context retrieval, prefix reuse, and world state shared across compatible agents.",
        deployment_slots=("MEMORY_LAYER", "RETRIEVER", "CACHE_LAYER"),
        capability_domains=("MEMORY", "RETRIEVAL", "CACHING"),
    )
    result = forge_component(component, _translations())
    aura_matches = [
        match for match in result.matches
        if "PERSISTENT_SHARED_MODIFIER" in match.matched_primitives
    ]
    assert aura_matches, "vocabulary gap: shared-persistent-state no longer overlaps aura-family gems"
