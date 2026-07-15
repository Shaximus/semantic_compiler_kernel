"""
Reflexion Semantic Compiler v2.0.0 — Source Provenance Tracking

Raw source is sacred. Original evidence remains immutable;
normalization and interpretation are derivative.

Citation: v1.0 Global Law — raw_source_is_sacred
Citation: v1.0 Spec Section 5 — Evidence and Provenance Model
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Optional


def classify_source_context(
    text: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Classify and record the provenance of the source input.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 1.2
    """
    result: dict[str, Any] = {
        "source_type": None,
        "origin": None,
        "trust_level": None,
        "intended_audience": None,
        "authority_level": "none",
        "source_path": None,
        "source_hash": hashlib.sha256(text.encode()).hexdigest(),
        "timestamp": None,
    }

    if context:
        for key in result:
            if key in context:
                result[key] = context[key]

    # Infer source type from content if not provided
    if result["source_type"] is None:
        result["source_type"] = _infer_source_type(text)

    # Infer trust level from source type
    if result["trust_level"] is None:
        result["trust_level"] = _infer_trust_level(result["source_type"])

    return result


def normalize_preserving_signal(text: str) -> str:
    """
    Normalize input while preserving meaningful signal.

    Citation: v1.0 Global Law — raw_source_is_sacred
    Citation: Diamond+++ — Do not over-sanitize the signal.

    Must preserve:
      - emotional intensity
      - metaphor choice
      - uncertainty markers
      - compressed phrasing
      - user corrections
      - model resistance
      - important slang/idiom if it carries meaning
    """
    # Strip excessive whitespace but preserve paragraph breaks
    normalized = re.sub(r"[ \t]+", " ", text)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = normalized.strip()

    return normalized


def _infer_source_type(text: str) -> str:
    """Infer the source type from text content."""
    text_lower = text.lower()

    if any(kw in text_lower for kw in ["log:", "timestamp:", "[info]", "[error]", "[debug]"]):
        return "direct_log"
    if any(kw in text_lower for kw in ["transcript", "speaker:", "q:", "a:"]):
        return "transcript"
    if any(kw in text_lower for kw in ["measured", "sensor", "telemetry"]):
        return "measurement"
    if any(kw in text_lower for kw in ["i remember", "i recall", "from memory"]):
        return "recollection"
    if any(kw in text_lower for kw in ["the paper", "study shows", "research"]):
        return "external_publication"

    return "user_input"


def _infer_trust_level(source_type: str) -> str:
    """Infer trust level from source type."""
    trust_map = {
        "direct_log": "high",
        "file_metadata": "high",
        "measurement": "medium_requires_verification",
        "transcript": "medium",
        "first_hand_observation": "medium",
        "screenshot": "medium",
        "recollection": "low",
        "external_publication": "low_external",
        "generic_prior": "lowest",
        "user_input": "medium",
    }
    return trust_map.get(source_type, "unknown")
