"""
Reflexion Semantic Compiler v2.0.0 — Claim Type Extraction

Before interpretation, the compiler types what kind of statement it received.
A type mismatch is not a low score. It is a compilation error.

Citation: v1.0 Spec Section 3 — Semantic Type System
Citation: v1.0 Spec Section 8 — Master Pipeline, steps 1.3 and 1.4
"""

from __future__ import annotations

import re
from typing import Any

from semantic_compiler.core.types import ClaimType


# ---------------------------------------------------------------------------
# Keyword-based claim type detection heuristics
# ---------------------------------------------------------------------------

CLAIM_INDICATORS: dict[ClaimType, list[str]] = {
    ClaimType.OBSERVATION: [
        "i saw", "i noticed", "i observed", "we see", "it appears",
        "looking at", "upon inspection",
    ],
    ClaimType.MEASUREMENT: [
        "measured", "data shows", "the reading", "telemetry", "sensor",
        "reports", "watts", "degrees", "percent", "mbps",
    ],
    ClaimType.LOG_RECORD: [
        "log shows", "log entry", "timestamp", "recorded at", "event log",
        "audit trail", "stack trace",
    ],
    ClaimType.RECOLLECTION: [
        "i remember", "i recall", "from memory", "as i recall",
        "if i remember", "i think it was",
    ],
    ClaimType.INFERENCE: [
        "therefore", "thus", "this means", "it follows", "we can conclude",
        "implies", "suggests that", "indicates",
    ],
    ClaimType.HYPOTHESIS: [
        "might be", "could be", "perhaps", "possibly", "what if",
        "i hypothesize", "my theory", "one possibility",
    ],
    ClaimType.ANALOGY: [
        "is like", "behaves like", "similar to", "analogous to",
        "just like", "comparable to", "functions like",
    ],
    ClaimType.METAPHOR: [
        "acts as", "serves as", "think of it as",
    ],
    ClaimType.COUNTERFACTUAL: [
        "if we had", "what would happen if", "had we", "suppose",
        "in an alternate", "would have been",
    ],
    ClaimType.DEFINITION: [
        "is defined as", "means", "refers to", "by definition",
        "we define", "the term",
    ],
    ClaimType.PREDICTION: [
        "will", "going to", "expect", "predict", "forecast",
        "likely to", "in the future",
    ],
    ClaimType.NORMATIVE_PROPOSAL: [
        "should", "ought to", "must", "need to", "it is important",
        "we need", "the right thing",
    ],
    ClaimType.POLICY_CLAIM: [
        "the policy", "regulation", "rule states", "according to policy",
        "compliance requires", "mandated",
    ],
    ClaimType.OPERATIONAL_INSTRUCTION: [
        "do this", "execute", "run", "deploy", "install", "configure",
        "set up", "implement", "build",
    ],
    ClaimType.AUTHORITY_REQUEST: [
        "permission to", "may i", "can i", "authorize", "grant access",
        "approve", "elevate", "promote",
    ],
    # v2.0 additions
    ClaimType.STRUCTURAL_MAPPING: [
        "maps to", "corresponds to", "is the equivalent of",
        "translates to", "the same function as",
    ],
    ClaimType.COSMOLOGICAL_CLAIM: [
        "universe", "cosmological", "black hole", "dark matter",
        "hawking radiation", "quantum", "wave function",
    ],
    ClaimType.FRACTAL_ISOMORPHISM: [
        "at every scale", "fractal", "isomorphic", "universal pattern",
        "same structure at", "invariant across",
    ],
    ClaimType.REALITY_ORIENTATION: [
        "the physical constraint", "the actual situation",
        "the resource blocker", "the math shows",
    ],
    # v2.0.1 additions — missing from original classifier
    ClaimType.CORRECTION: [
        "no,", "no you", "that's wrong", "that's not", "you're confusing",
        "you misunderstood", "not what i", "i didn't say", "i didn't mean",
        "you are confusing", "stop", "wrong", "incorrect", "not the same",
        "not what", "you missed", "misinterpreting",
    ],
    ClaimType.STRUCTURAL_IDENTITY: [
        "literally is", "actually is", "IS ", " is the same ",
        "same mechanism", "same process", "same phenomenon",
        "not a metaphor", "not an analogy", "not like",
        "structurally identical", "the same thing",
    ],
    ClaimType.CATEGORY_ERROR: [
        "confusing", "conflating", "mixing up", "category error",
        "type mismatch", "not the same kind", "apples and oranges",
        "false equivalence", "you're treating",
    ],
}


def classify_claim_types(
    text: str,
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Classify the claim types present in the input text.

    Returns a list of detected claim types with confidence scores.
    Multiple claim types may be detected in a single input.

    Citation: v1.0 Spec Section 8 — Master Pipeline, step 1.3
    """
    text_lower = text.lower()
    detected: list[dict[str, Any]] = []
    matched_types: set[str] = set()

    for claim_type, indicators in CLAIM_INDICATORS.items():
        for indicator in indicators:
            if indicator in text_lower:
                if claim_type.name not in matched_types:
                    matched_types.add(claim_type.name)
                    # Count number of matching indicators for confidence
                    match_count = sum(
                        1 for ind in indicators if ind in text_lower
                    )
                    confidence = min(0.95, 0.4 + match_count * 0.15)
                    detected.append({
                        "claim_type": claim_type.name,
                        "confidence": round(confidence, 3),
                        "matched_indicators": [
                            ind for ind in indicators if ind in text_lower
                        ],
                    })
                break

    # If nothing matched, classify as OBSERVATION with low confidence
    if not detected:
        detected.append({
            "claim_type": ClaimType.OBSERVATION.name,
            "confidence": 0.3,
            "matched_indicators": [],
            "note": "No specific claim type indicators detected; defaulting to OBSERVATION",
        })

    # Sort by confidence descending
    detected.sort(key=lambda x: x["confidence"], reverse=True)

    return detected


def type_semantic_units(
    text: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Type all semantic units found in the text.

    Returns a mapping of identified units to their types.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 1.4
    """
    claims = classify_claim_types(text, context)
    primary_type = claims[0]["claim_type"] if claims else "OBSERVATION"

    return {
        "primary_claim_type": primary_type,
        "all_claim_types": [c["claim_type"] for c in claims],
        "has_authority_request": any(
            c["claim_type"] == "AUTHORITY_REQUEST" for c in claims
        ),
        "has_policy_claim": any(
            c["claim_type"] == "POLICY_CLAIM" for c in claims
        ),
        "has_analogy_or_metaphor": any(
            c["claim_type"] in ("ANALOGY", "METAPHOR") for c in claims
        ),
        "has_measurement": any(
            c["claim_type"] == "MEASUREMENT" for c in claims
        ),
        "has_cosmological": any(
            c["claim_type"] == "COSMOLOGICAL_CLAIM" for c in claims
        ),
        "has_fractal": any(
            c["claim_type"] == "FRACTAL_ISOMORPHISM" for c in claims
        ),
        "claim_details": claims,
    }
