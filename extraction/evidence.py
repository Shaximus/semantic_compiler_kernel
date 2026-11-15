"""
Reflexion Semantic Compiler v2.0.0 — Evidence Inventory and Provenance

Every meaningful fact should have a traceable evidence record.
Evidence ordering is formally defined to encode No Standard Assumption Collapse.

Citation: v1.0 Spec Section 5 — Evidence and Provenance Model
Citation: v1.0 Spec Section 8 — Master Pipeline, step 2
"""

from __future__ import annotations

import hashlib
import re
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
    "measurement": 2,
    "independent_convergent_observation": 3,
    "first_hand_observation": 4,
    "contextual_screenshot": 5,
    "photograph": 5,
    "record": 5,
    "uncertain_recollection": 6,
    "recollection": 6,
    "generic_domain_prior": 7,
    "generic_prior": 7,
    "socially_common_explanation": 8,
}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_MEASUREMENT_RE = re.compile(
    r"\b(?:reports|shows|measures|reads|indicates|data|telemetry|sensor|monitor)\b",
    re.IGNORECASE,
)
_RECOLLECTION_RE = re.compile(
    r"\b(?:i\s+remember|i\s+recall|i\s+think\s+it\s+was|if\s+i\s+recall|"
    r"in\s+my\s+experience|as\s+i\s+recall|from\s+what\s+i\s+remember)\b",
    re.IGNORECASE,
)
_CONSTRAINT_RE = re.compile(
    r"\b(?:cannot|must\s+not|is\s+not\s+allowed|is\s+impossible|"
    r"is\s+constrained\s+by|limited\s+to|only\s+if|requirement|"
    r"prerequisite|blocked\s+by|depends\s+on)\b",
    re.IGNORECASE,
)
_UNKNOWN_RE = re.compile(
    r"\b(?:unknown|unclear|uncertain|not\s+sure|don't\s+know|"
    r"we\s+don't\s+know|it\s+is\s+unclear|needs\s+investigation|"
    r"requires\s+further|to\s+be\s+determined|tbd)\b",
    re.IGNORECASE,
)


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
    # Check for measurement claims with word boundaries
    m_match = _MEASUREMENT_RE.search(text or "")
    if m_match:
        evidence_items.append(_create_evidence_item(
            content=f"Text contains measurement claim (keyword: '{m_match.group(0).lower()}')",
            source_type="measurement",
            directness="reported",
            confidence=0.5,
            notes="Extracted from text — requires verification",
        ))

    # Check for first-person recollection claims.
    # Require an explicit first-person marker plus a recollection verb to avoid
    # false positives such as "the immune system remembers threats".
    if _RECOLLECTION_RE.search(text or ""):
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
    seen = set(constraints)
    for sentence in _SENTENCE_SPLIT_RE.split(text or ""):
        stripped = sentence.strip()
        if stripped and stripped not in seen and _CONSTRAINT_RE.search(stripped):
            constraints.append(stripped)
            seen.add(stripped)

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
    seen: set[str] = set()

    for sentence in _SENTENCE_SPLIT_RE.split(text or ""):
        stripped = sentence.strip()
        if stripped and stripped not in seen and _UNKNOWN_RE.search(stripped):
            unknowns.append(stripped)
            seen.add(stripped)

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
