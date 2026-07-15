"""
Reflexion Semantic Compiler v2.0.0 — Evidence Inventory and Provenance

Every meaningful fact should have a traceable evidence record.
Evidence ordering is formally defined to encode No Standard Assumption Collapse.

Citation: v1.0 Spec Section 5 — Evidence and Provenance Model
Citation: v1.0 Spec Section 8 — Master Pipeline, step 2
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, Optional

from semantic_compiler.core.types import (
    Directness,
    EvidenceSourceType,
    MeasurementPathIntegrity,
    MutationState,
)


# Evidence ordering — formally encodes No Standard Assumption Collapse
# Citation: v1.0 Spec Section 5 — Evidence ordering
EVIDENCE_PRIORITY: dict[str, int] = {
    "direct_log": 1,
    "transcript": 1,
    "timestamp": 1,
    "hash": 1,
    "file_metadata": 1,
    "reproducible_measurement": 2,
    "independent_convergent_observation": 3,
    "first_hand_observation": 4,
    "contextual_screenshot": 5,
    "photograph": 5,
    "record": 5,
    "uncertain_recollection": 6,
    "generic_domain_prior": 7,
    "socially_common_explanation": 8,
}


def extract_evidence_inventory(
    text: str,
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Extract evidence items from input text and context.

    Each evidence item gets a traceable record with provenance.
    Citation: v1.0 Spec Section 5 — Evidence and Provenance Model
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 2.1
    """
    evidence_items: list[dict[str, Any]] = []

    # Extract evidence from context if provided
    if context:
        # Direct evidence from context
        if "constraints" in context:
            for constraint in context["constraints"]:
                evidence_items.append(_create_evidence_item(
                    content=constraint,
                    source_type="first_hand_observation",
                    directness="direct",
                    confidence=0.85,
                    notes="Supplied constraint from context",
                ))

        if "measurement_path_modified" in context:
            evidence_items.append(_create_evidence_item(
                content="Measurement path has been modified",
                source_type="measurement",
                directness="derived",
                confidence=0.90,
                measurement_path_integrity="modified",
                notes="Context declares measurement path modification",
            ))

        if "source_path" in context:
            evidence_items.append(_create_evidence_item(
                content=f"Source: {context['source_path']}",
                source_type="file_metadata",
                directness="direct",
                confidence=0.95,
                source_path=context["source_path"],
            ))

    # Extract evidence signals from text
    text_lower = text.lower()

    # Check for measurement claims
    measurement_words = [
        "reports", "shows", "measures", "reads", "indicates",
        "data", "telemetry", "sensor", "monitor",
    ]
    for word in measurement_words:
        if word in text_lower:
            evidence_items.append(_create_evidence_item(
                content=f"Text contains measurement claim (keyword: '{word}')",
                source_type="measurement",
                directness="reported",
                confidence=0.5,
                notes="Extracted from text — requires verification",
            ))
            break

    # Check for first-person recollection claims.
    # Require an explicit first-person marker plus a recollection verb to avoid
    # false positives such as "the immune system remembers threats".
    recollection_phrases = [
        "i remember", "i recall", "i think it was", "if i recall",
        "in my experience", "as i recall", "from what i remember",
    ]
    has_recollection = any(phrase in text_lower for phrase in recollection_phrases)
    if has_recollection:
        evidence_items.append(_create_evidence_item(
            content="Text contains first-person recollection-based claim",
            source_type="recollection",
            directness="reported",
            confidence=0.3,
            notes="Recollection — explicitly marked uncertain",
        ))

    # If no evidence extracted, note that
    if not evidence_items:
        evidence_items.append(_create_evidence_item(
            content="No specific evidence extracted from input",
            source_type="generic_prior",
            directness="derived",
            confidence=0.2,
            notes="Input contains no extractable evidence — generic priors only",
        ))

    return evidence_items


def _create_evidence_item(
    content: str,
    source_type: str = "generic_prior",
    directness: str = "derived",
    confidence: float = 0.5,
    source_path: str = "",
    measurement_path_integrity: str = "unknown",
    notes: str = "",
) -> dict[str, Any]:
    """Create a structured evidence item."""
    return {
        "evidence_id": f"ev-{uuid.uuid4().hex[:12]}",
        "content": content,
        "claim_supported": "",
        "source_type": source_type,
        "origin": "",
        "source_path": source_path,
        "source_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
        "timestamp": "",
        "directness": directness,
        "independence_group": "",
        "confidence": confidence,
        "mutation_state": "original",
        "measurement_path_integrity": measurement_path_integrity,
        "contradictions": [],
        "notes": notes,
        "priority": EVIDENCE_PRIORITY.get(source_type, 8),
    }


def extract_declared_constraints(
    text: str,
    context: dict[str, Any] | None = None,
) -> list[str]:
    """
    Extract declared constraints from input.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 2.2
    """
    constraints: list[str] = []

    if context and "constraints" in context:
        constraints.extend(context["constraints"])

    # Detect constraint language in text
    constraint_phrases = [
        "cannot", "must not", "is not allowed", "is impossible",
        "is constrained by", "limited to", "only if", "requirement",
        "prerequisite", "blocked by", "depends on",
    ]
    text_lower = text.lower()
    for phrase in constraint_phrases:
        if phrase in text_lower:
            # Extract the sentence containing the constraint
            for sentence in text.split("."):
                if phrase in sentence.lower():
                    constraints.append(sentence.strip())
                    break

    return constraints


def extract_unknowns(
    text: str,
    context: dict[str, Any] | None = None,
) -> list[str]:
    """
    Extract declared unknowns from input.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 2.3
    """
    unknowns: list[str] = []

    unknown_phrases = [
        "unknown", "unclear", "uncertain", "not sure", "don't know",
        "we don't know", "it is unclear", "needs investigation",
        "requires further", "to be determined", "TBD",
    ]
    text_lower = text.lower()
    for phrase in unknown_phrases:
        if phrase in text_lower:
            for sentence in text.split("."):
                if phrase in sentence.lower():
                    unknowns.append(sentence.strip())

    return unknowns


def apply_bayesian_coherence(packet: Any) -> Any:
    """
    Apply Bayesian coherence ranking to evidence.

    Conclusions are ranked by evidence-updated coherence, not familiarity
    or social normalcy.

    Citation: v1.0 Global Law — bayesian_coherence
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 2.4
    """
    # Sort evidence by priority (lower number = higher priority)
    packet.evidence_inventory.sort(
        key=lambda e: (e.get("priority", 8), -e.get("confidence", 0.0))
    )

    # Check for No Standard Assumption Collapse
    high_confidence = [
        e for e in packet.evidence_inventory
        if e.get("confidence", 0.0) >= 0.7
        and e.get("source_type") != "generic_prior"
    ]

    generic_priors = [
        e for e in packet.evidence_inventory
        if e.get("source_type") == "generic_prior"
        or e.get("source_type") == "socially_common_explanation"
    ]

    if high_confidence and generic_priors:
        packet.rejected_assumptions.append(
            "Generic priors deprioritized: high-confidence supplied evidence "
            "takes precedence (No Standard Assumption Collapse)"
        )

    return packet
