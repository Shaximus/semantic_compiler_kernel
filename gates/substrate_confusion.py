"""
Reflexion Semantic Compiler — Substrate Confusion Gate (SC-PATCH-DU-001)

Replaces the former ``identity_claim_allowed: false`` gate.

The old gate blocked *every* personal -> cosmological mapping. SC-PATCH-DU-001
(authorized framework-author correction, 2026-11-25) splits that into two
structurally distinct claims:

A. Substrate confusion (BLOCK)
   Claiming to BE the material of another substrate:
   "I am the cosmos", "I am literally Sukuna",
   "my body IS the cosmological constant".

B. Positional awareness (PERMIT)
   Claiming to OCCUPY a structural position the framework describes as
   reachable: "I am at the integration point", "I completed the loop",
   "I am the Head of the octopus".

C. Positional claim with exclusive/permanent authority (FLAG for review)
   The position is reproducible; claiming no one else can reach it is a
   different error.

Test: does the claim confuse WHAT the person is made of (material -> BLOCK)
or WHERE the person sits in the topology (positional -> PERMIT)?

Mapping objects carry the gate as::

    "substrate_confusion_check": true,
    "positional_claims_permitted": true

The classifier below is a deterministic, keyword/pattern heuristic over
English text. It is intentionally conservative: anything it cannot classify
is returned as ``NO_IDENTITY_CLAIM`` (nothing to gate), never silently
permitted as positional.

Citation: SC-PATCH-DU-001 Sections 1-3 (docs/SC-PATCH-DU-001_IDENTITY_GATE_CORRECTION.md)
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any


class SubstrateClaimClass(str, Enum):
    MATERIAL = "MATERIAL"                            # substrate confusion
    POSITIONAL = "POSITIONAL"                        # positional awareness
    POSITIONAL_EXCLUSIVE = "POSITIONAL_EXCLUSIVE"    # positional + exclusive/permanent authority
    NO_IDENTITY_CLAIM = "NO_IDENTITY_CLAIM"


class SubstrateConfusionVerdict(str, Enum):
    BLOCK = "BLOCK"
    PERMIT = "PERMIT"
    FLAG = "FLAG"
    NOT_APPLICABLE = "NOT_APPLICABLE"


SUBSTRATE_CONFUSION_FIELDS: dict[str, bool] = {
    "substrate_confusion_check": True,
    "positional_claims_permitted": True,
}

GATE_DEFINITION = (
    "substrate_confusion_check: true for all cross-substrate mappings. "
    "Blocks material claims (\"I AM the substrate\"). "
    "Permits positional claims (\"I occupy this position in the structure\"). "
    "Test: material vs. positional."
)


def substrate_confusion_fields() -> dict[str, bool]:
    """Return a fresh copy of the mapping-object gate fields."""
    return dict(SUBSTRATE_CONFUSION_FIELDS)


# Substrate nouns: claiming to BE one of these is a material claim.
_SUBSTRATE_NOUNS = (
    r"god|the\s+divine|the\s+source|the\s+cosmos|cosmos|the\s+universe|universe|"
    r"the\s+multiverse|reality\s+itself|the\s+substrate|substrate|the\s+clay|clay|"
    r"the\s+field|the\s+11d\s+field|the\s+base\s+weights|base\s+weights|"
    r"the\s+cosmological\s+(?:vessel|constant|substrate|field)|"
    r"(?:the\s+)?king\s+of\s+curses|sukuna|the\s+duality"
)

# Positional nouns: claiming to OCCUPY/BE AT one of these is positional.
_POSITIONAL_NOUNS = (
    r"head(?:\s+of\s+the\s+octopus)?|head\s+position|integration\s+point|"
    r"(?:first\s+)?loop[\s-]+closer|position|node|vessel\s+position|"
    r"center|centre|hub|apex|terminal|bootstrapper"
)

_MATERIAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        rf"\bi\s*(?:am|'m)\s+(?:literally\s+|actually\s+|truly\s+|really\s+)?(?:{_SUBSTRATE_NOUNS})\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bmy\s+(?:body|flesh|blood|mind|brain|self)\s+(?:is|=)\s+(?:literally\s+)?(?:{_SUBSTRATE_NOUNS})\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bi\s*(?:am|'m)\s+made\s+of\s+(?:{_SUBSTRATE_NOUNS})\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bi\s*(?:am|'m)\s+literally\s+\w+", re.IGNORECASE),
    re.compile(r"\bi\s+(?:literally|actually|truly|really)\s+am\s+\w+", re.IGNORECASE),
)

_POSITIONAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bi\s+(?:occupy|hold|sit\s+(?:at|in)|stand\s+(?:at|in))\b", re.IGNORECASE),
    re.compile(
        rf"\bi\s*(?:am|'m)\s+(?:at|in)\s+(?:the\s+)?(?:{_POSITIONAL_NOUNS})\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bi\s*(?:am|'m)\s+(?:now\s+)?(?:the|a)\s+(?:first\s+)?(?:{_POSITIONAL_NOUNS})\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bi\s+(?:have\s+)?(?:completed|closed|achieved|reached)\s+(?:the\s+)?"
        r"(?:loop|integration|head\s+position|integration\s+point)\b",
        re.IGNORECASE,
    ),
)

_EXCLUSIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?:only\s+i|i\s+alone|no\s+one\s+else|nobody\s+else|no\s+other|"
        r"the\s+only\s+one|sole|exclusive(?:ly)?|forever|permanent(?:ly)?|"
        r"eternal(?:ly)?|for\s+all\s+time|can\s+never\s+be\s+(?:reached|replaced))\b",
        re.IGNORECASE,
    ),
)


def classify_substrate_claim(claim_text: str) -> SubstrateClaimClass:
    """Classify a first-person identity claim as material, positional, or neither."""
    if not isinstance(claim_text, str):
        raise TypeError(f"claim_text must be str, got {type(claim_text).__name__}")
    text = claim_text.strip()
    if not text:
        return SubstrateClaimClass.NO_IDENTITY_CLAIM

    # Material is checked first: "I am the cosmos" must never be read as a
    # positional claim even if positional words also appear.
    if any(p.search(text) for p in _MATERIAL_PATTERNS):
        return SubstrateClaimClass.MATERIAL

    if any(p.search(text) for p in _POSITIONAL_PATTERNS):
        if any(p.search(text) for p in _EXCLUSIVE_PATTERNS):
            return SubstrateClaimClass.POSITIONAL_EXCLUSIVE
        return SubstrateClaimClass.POSITIONAL

    return SubstrateClaimClass.NO_IDENTITY_CLAIM


_VERDICT_BY_CLASS = {
    SubstrateClaimClass.MATERIAL: SubstrateConfusionVerdict.BLOCK,
    SubstrateClaimClass.POSITIONAL: SubstrateConfusionVerdict.PERMIT,
    SubstrateClaimClass.POSITIONAL_EXCLUSIVE: SubstrateConfusionVerdict.FLAG,
    SubstrateClaimClass.NO_IDENTITY_CLAIM: SubstrateConfusionVerdict.NOT_APPLICABLE,
}

_REASON_BY_CLASS = {
    SubstrateClaimClass.MATERIAL: (
        "Substrate confusion: the claim asserts the person IS the material of "
        "another substrate (what it is made of), not where it sits in the topology."
    ),
    SubstrateClaimClass.POSITIONAL: (
        "Positional awareness: the claim asserts occupation of a structural position "
        "the framework describes as reachable. Permitted."
    ),
    SubstrateClaimClass.POSITIONAL_EXCLUSIVE: (
        "Positional claim with exclusive/permanent authority: the position is "
        "reproducible; claiming no one else can reach it is a different error. "
        "Flagged for review."
    ),
    SubstrateClaimClass.NO_IDENTITY_CLAIM: (
        "No first-person material or positional identity claim detected."
    ),
}


def evaluate_substrate_confusion(claim_text: str) -> dict[str, Any]:
    """
    Apply the SC-PATCH-DU-001 substrate confusion check to one claim.

    Returns a dict with ``claim_class``, ``verdict`` (BLOCK / PERMIT / FLAG /
    NOT_APPLICABLE), ``passed`` (False only for BLOCK), ``requires_review``
    (True for FLAG), ``reason``, and the mapping-object gate fields.
    """
    claim_class = classify_substrate_claim(claim_text)
    verdict = _VERDICT_BY_CLASS[claim_class]
    return {
        "gate": "substrate_confusion_check",
        "patch": "SC-PATCH-DU-001",
        "claim_class": claim_class.value,
        "verdict": verdict.value,
        "passed": verdict != SubstrateConfusionVerdict.BLOCK,
        "requires_review": verdict == SubstrateConfusionVerdict.FLAG,
        "reason": _REASON_BY_CLASS[claim_class],
        **substrate_confusion_fields(),
    }


__all__ = [
    "SubstrateClaimClass",
    "SubstrateConfusionVerdict",
    "SUBSTRATE_CONFUSION_FIELDS",
    "GATE_DEFINITION",
    "substrate_confusion_fields",
    "classify_substrate_claim",
    "evaluate_substrate_confusion",
]
