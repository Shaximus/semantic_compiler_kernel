"""
Evidence tiers for corpus-level aggregation (V2.2 expansion).

The frozen core classifies evidence by *source mechanics*
(:class:`~semantic_compiler.core.types.EvidenceSourceType`,
:data:`~semantic_compiler.extraction.evidence.EVIDENCE_PRIORITY`). Corpus
orchestration needs a coarser, mission-facing vocabulary: how much weight may
a piece of evidence carry when confirming or disconfirming a cross-document
invariant.

This module is a pure translation layer. It does **not** edit the frozen
enums; it maps them onto five tiers:

============================  ==============================================
Tier                          Meaning
============================  ==============================================
PRIMARY_RECORD                Direct artifacts: logs, transcripts,
                              timestamps, hashes, file metadata, captured
                              records, reproducible measurements.
PUBLISHED_RESEARCH            External, independently checkable work:
                              published studies, independent convergent
                              observations.
SELF_ASSESSED_ESTIMATE        First-hand but subjective: observations,
                              recollections, self-reported estimates.
AI_GENERATED_ASSESSMENT       Model- or prior-derived assessments (including
                              this compiler's own heuristic judgments and
                              generic domain priors).
MARKED_SPECULATION            Explicitly speculative or socially common
                              explanations; also the honest default for
                              anything unmapped.
============================  ==============================================

Tiers are ordered: ``TIER_RANK`` gives 1 (strongest) .. 5 (weakest).
"""

from __future__ import annotations

from enum import Enum, unique
from typing import Any, Optional

from semantic_compiler.core.types import EvidenceSourceType
from semantic_compiler.extraction.evidence import EVIDENCE_PRIORITY


@unique
class EvidenceTier(Enum):
    """Mission-facing evidence weight classification."""

    PRIMARY_RECORD = "PRIMARY_RECORD"
    PUBLISHED_RESEARCH = "PUBLISHED_RESEARCH"
    SELF_ASSESSED_ESTIMATE = "SELF_ASSESSED_ESTIMATE"
    AI_GENERATED_ASSESSMENT = "AI_GENERATED_ASSESSMENT"
    MARKED_SPECULATION = "MARKED_SPECULATION"


# 1 = strongest, 5 = weakest.
TIER_RANK: dict[EvidenceTier, int] = {
    EvidenceTier.PRIMARY_RECORD: 1,
    EvidenceTier.PUBLISHED_RESEARCH: 2,
    EvidenceTier.SELF_ASSESSED_ESTIMATE: 3,
    EvidenceTier.AI_GENERATED_ASSESSMENT: 4,
    EvidenceTier.MARKED_SPECULATION: 5,
}

# Frozen EvidenceSourceType enum -> tier.
_SOURCE_TYPE_MAP: dict[EvidenceSourceType, EvidenceTier] = {
    EvidenceSourceType.DIRECT_LOG: EvidenceTier.PRIMARY_RECORD,
    EvidenceSourceType.TRANSCRIPT: EvidenceTier.PRIMARY_RECORD,
    EvidenceSourceType.FILE_METADATA: EvidenceTier.PRIMARY_RECORD,
    EvidenceSourceType.MEASUREMENT: EvidenceTier.PRIMARY_RECORD,
    EvidenceSourceType.SCREENSHOT: EvidenceTier.PRIMARY_RECORD,
    EvidenceSourceType.FIRST_HAND_OBSERVATION: EvidenceTier.SELF_ASSESSED_ESTIMATE,
    EvidenceSourceType.RECOLLECTION: EvidenceTier.SELF_ASSESSED_ESTIMATE,
    EvidenceSourceType.GENERIC_PRIOR: EvidenceTier.AI_GENERATED_ASSESSMENT,
}

# String keys used by extraction.evidence.EVIDENCE_PRIORITY -> tier.
_PRIORITY_KEY_MAP: dict[str, EvidenceTier] = {
    "direct_log": EvidenceTier.PRIMARY_RECORD,
    "transcript": EvidenceTier.PRIMARY_RECORD,
    "timestamp": EvidenceTier.PRIMARY_RECORD,
    "hash": EvidenceTier.PRIMARY_RECORD,
    "file_metadata": EvidenceTier.PRIMARY_RECORD,
    "record": EvidenceTier.PRIMARY_RECORD,
    "photograph": EvidenceTier.PRIMARY_RECORD,
    "contextual_screenshot": EvidenceTier.PRIMARY_RECORD,
    "reproducible_measurement": EvidenceTier.PRIMARY_RECORD,
    "independent_convergent_observation": EvidenceTier.PUBLISHED_RESEARCH,
    "first_hand_observation": EvidenceTier.SELF_ASSESSED_ESTIMATE,
    "uncertain_recollection": EvidenceTier.SELF_ASSESSED_ESTIMATE,
    "generic_domain_prior": EvidenceTier.AI_GENERATED_ASSESSMENT,
    "socially_common_explanation": EvidenceTier.MARKED_SPECULATION,
}

ALL_TIER_VALUES: tuple[str, ...] = tuple(t.value for t in EvidenceTier)


def tier_from_source_type(
    source_type: EvidenceSourceType | str | None,
    default: EvidenceTier = EvidenceTier.MARKED_SPECULATION,
) -> EvidenceTier:
    """
    Map a frozen :class:`EvidenceSourceType` (or its name/value string) onto a tier.

    Unknown or ``None`` inputs map to ``default`` — honest discipline: an
    unclassifiable source carries the weakest weight, never silent promotion.
    """
    if isinstance(source_type, EvidenceSourceType):
        return _SOURCE_TYPE_MAP.get(source_type, default)
    if isinstance(source_type, str):
        normalized = source_type.strip()
        for member in EvidenceSourceType:
            if normalized.upper() == member.name or normalized.lower() == member.name.lower():
                return _SOURCE_TYPE_MAP.get(member, default)
        # Fall through: maybe it is an EVIDENCE_PRIORITY key instead.
        return _PRIORITY_KEY_MAP.get(normalized.lower(), default)
    return default


def tier_from_priority_key(
    key: str | None,
    default: EvidenceTier = EvidenceTier.MARKED_SPECULATION,
) -> EvidenceTier:
    """
    Map an :data:`EVIDENCE_PRIORITY` string key onto a tier.

    Raises nothing; unknown keys (including keys not present in
    ``EVIDENCE_PRIORITY`` at all) map to ``default``.
    """
    if not isinstance(key, str):
        return default
    return _PRIORITY_KEY_MAP.get(key.strip().lower(), default)


def priority_rank(tier: EvidenceTier) -> int:
    """Numeric rank of a tier (1 strongest .. 5 weakest)."""
    return TIER_RANK[tier]


def strongest_tier(tiers: list[EvidenceTier]) -> Optional[EvidenceTier]:
    """Return the strongest tier in a list, or ``None`` for an empty list."""
    if not tiers:
        return None
    return min(tiers, key=lambda t: TIER_RANK[t])


def attach_tier(
    record: dict[str, Any],
    tier: EvidenceTier | str | None = None,
    *,
    source_type: EvidenceSourceType | str | None = None,
) -> dict[str, Any]:
    """
    Return a copy of a claim/evidence record with an ``evidence_tier`` field.

    The tier may be given explicitly (an :class:`EvidenceTier` or its string
    value); otherwise it is derived from ``source_type`` if provided, else
    from the record's own ``source_type`` field, else the honest default
    ``MARKED_SPECULATION``. The original record is never mutated.
    """
    if tier is None:
        tier = tier_from_source_type(
            source_type if source_type is not None else record.get("source_type")
        )
    elif isinstance(tier, str):
        tier = EvidenceTier[tier] if tier in EvidenceTier.__members__ else EvidenceTier(tier)
    annotated = dict(record)
    annotated["evidence_tier"] = tier.value
    return annotated
