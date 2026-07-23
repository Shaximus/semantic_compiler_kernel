"""Tests for expansion.evidence_tiers."""

from semantic_compiler.core.types import EvidenceSourceType
from semantic_compiler.expansion.evidence_tiers import (
    EvidenceTier,
    TIER_RANK,
    attach_tier,
    priority_rank,
    strongest_tier,
    tier_from_priority_key,
    tier_from_source_type,
)


def test_source_type_enum_mapping():
    assert tier_from_source_type(EvidenceSourceType.DIRECT_LOG) is EvidenceTier.PRIMARY_RECORD
    assert tier_from_source_type(EvidenceSourceType.TRANSCRIPT) is EvidenceTier.PRIMARY_RECORD
    assert tier_from_source_type(EvidenceSourceType.MEASUREMENT) is EvidenceTier.PRIMARY_RECORD
    assert tier_from_source_type(EvidenceSourceType.FIRST_HAND_OBSERVATION) is EvidenceTier.SELF_ASSESSED_ESTIMATE
    assert tier_from_source_type(EvidenceSourceType.RECOLLECTION) is EvidenceTier.SELF_ASSESSED_ESTIMATE
    assert tier_from_source_type(EvidenceSourceType.GENERIC_PRIOR) is EvidenceTier.AI_GENERATED_ASSESSMENT


def test_source_type_string_mapping():
    assert tier_from_source_type("DIRECT_LOG") is EvidenceTier.PRIMARY_RECORD
    assert tier_from_source_type("first_hand_observation") is EvidenceTier.SELF_ASSESSED_ESTIMATE


def test_priority_key_mapping_covers_all_evidence_priority_keys():
    from semantic_compiler.extraction.evidence import EVIDENCE_PRIORITY
    for key in EVIDENCE_PRIORITY:
        tier = tier_from_priority_key(key)
        assert isinstance(tier, EvidenceTier), key
    assert tier_from_priority_key("direct_log") is EvidenceTier.PRIMARY_RECORD
    assert tier_from_priority_key("independent_convergent_observation") is EvidenceTier.PUBLISHED_RESEARCH
    assert tier_from_priority_key("socially_common_explanation") is EvidenceTier.MARKED_SPECULATION
    assert tier_from_priority_key("generic_domain_prior") is EvidenceTier.AI_GENERATED_ASSESSMENT


def test_unknown_maps_to_honest_default_not_promotion():
    assert tier_from_source_type("nonexistent") is EvidenceTier.MARKED_SPECULATION
    assert tier_from_source_type(None) is EvidenceTier.MARKED_SPECULATION
    assert tier_from_priority_key("nonexistent") is EvidenceTier.MARKED_SPECULATION
    assert tier_from_priority_key(None) is EvidenceTier.MARKED_SPECULATION
    # caller may choose a different default
    assert tier_from_source_type(None, default=EvidenceTier.PRIMARY_RECORD) is EvidenceTier.PRIMARY_RECORD


def test_tier_rank_ordering():
    assert priority_rank(EvidenceTier.PRIMARY_RECORD) == 1
    assert priority_rank(EvidenceTier.MARKED_SPECULATION) == 5
    assert strongest_tier([EvidenceTier.MARKED_SPECULATION, EvidenceTier.PRIMARY_RECORD]) is EvidenceTier.PRIMARY_RECORD
    assert strongest_tier([]) is None


def test_attach_tier_non_mutating():
    record = {"content": "claim", "source_type": "transcript"}
    annotated = attach_tier(record)
    assert annotated["evidence_tier"] == "PRIMARY_RECORD"
    assert "evidence_tier" not in record  # original untouched


def test_attach_tier_explicit_and_derived():
    assert attach_tier({}, tier=EvidenceTier.PUBLISHED_RESEARCH)["evidence_tier"] == "PUBLISHED_RESEARCH"
    assert attach_tier({}, tier="PRIMARY_RECORD")["evidence_tier"] == "PRIMARY_RECORD"
    assert attach_tier({}, source_type=EvidenceSourceType.RECOLLECTION)["evidence_tier"] == "SELF_ASSESSED_ESTIMATE"
    assert attach_tier({})["evidence_tier"] == "MARKED_SPECULATION"
