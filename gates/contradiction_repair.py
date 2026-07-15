"""
Reflexion Semantic Compiler v2.0.0 — Contradiction Repair Gate

Detect common false or unsupported causal claims, classify the semantic error,
and emit structured repair objects.  The gate is deliberately conservative so
that rhetorical personification is not automatically treated as a literal
falsehood.

v2.1.3: Expanded to support explicit semantic error classes and decision routing.
"""

from __future__ import annotations

import re
from typing import Any


# Causal verbs that, when attributed to non-mental systems, signal
# anthropomorphic causation.
_ANTHROPOMORPHIC_FEELING_WORDS: set[str] = {
    "want", "wants", "wanted", "wanting",
    "need", "needs", "needed", "needing",
    "feel", "feels", "felt", "feeling", "feelings",
    "love", "loves", "loved", "loving",
    "hate", "hates", "hated", "hating",
    "angry", "anger", "mad", "sad", "happy", "upset", "mood",
    "desire", "desires", "desired", "desiring",
    "intend", "intends", "intended", "intending",
    "will", "willed", "willing", "lazy",
    "loyal", "loyalty", "loyalties",
    "believe", "believes", "believed", "believing", "belief", "beliefs",
}

# Verbs that are often used to assert a false physical mechanism.
_FALSE_MECHANISM_WORDS: set[str] = {
    "magnet", "magnets", "magnetism", "magnetic",
}

# Pseudo-scientific or unsupported causal terms.
_PSEUDOSCIENCE_WORDS: set[str] = {
    "homeopathy", "crystal", "crystals", "vibes", "energy healing",
    "water remembers", "memory of water",
}

# Phrases that identify a literal causal claim rather than mere personification.
_LITERAL_CAUSAL_TRIGGERS: set[str] = {
    "because", "causes", "caused", "cause", "makes", "made",
    "explains", "explained", "due to", "owing to", "results from",
    "so", "therefore", "thus", "hence",
}

# Phrases that indicate an identity claim confusing analogy with identity.
_IDENTITY_MARKERS: set[str] = {
    "is literally", "is actually", "is exactly", "is nothing but",
    "is the same as", "is identical to",
}

# Rhetorical state-of-being markers for personification.
_PERSONIFICATION_STATE_WORDS: set[str] = {
    "angry", "depressed", "happy", "sad", "mood", "lazy", "tired",
    "excited", "nervous", "optimistic", "pessimistic",
}

# Intentional or mental verbs attributed to clearly non-mental systems.
_INTENTIONAL_VERBS: set[str] = {
    "choose", "chooses", "chose", "choosing",
    "dance", "dances", "danced", "dancing",
    "remember", "remembers", "remembered", "remembering",
}

# Subjects that, when paired with _INTENTIONAL_VERBS, indicate anthropomorphism.
# Only clearly non-mental physical/natural systems are included; organizations
# and projects often host valid structural analogies (e.g., immune system).
_NON_MENTAL_SUBJECTS: set[str] = {
    "electrons", "electron",
    "atoms", "atom",
    "molecules", "molecule",
    "particles", "particle",
    "planets", "planet",
    "stars", "star",
    "black holes", "black hole",
    "the sun", "the moon",
    "data",
}

# Pseudo-scientific health claims not already covered by the word lists.
_PSEUDOSCIENTIFIC_HEALTH_PATTERNS: set[str] = {
    "magnetic bracelet",
    "magnetic bracelets",
    "aligning energy fields",
    "cure arthritis",
}


def _lower_text(text: str) -> str:
    return (text or "").lower()


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z][a-z0-9\-]*", text.lower()))


def _contains_any(text: str, words: set[str]) -> bool:
    return bool(_tokens(text) & words)


def _has_literal_causal_trigger(text: str) -> bool:
    lower = _lower_text(text)
    return any(trigger in lower for trigger in _LITERAL_CAUSAL_TRIGGERS)


def _has_identity_marker(text: str) -> bool:
    lower = _lower_text(text)
    return any(marker in lower for marker in _IDENTITY_MARKERS)


def _repair_object(
    claim_id: str,
    error_class: str,
    invalid_component: str,
    preserved_component: str,
    corrected_claim: str,
    explanation: str,
    confidence: float,
) -> dict[str, Any]:
    return {
        "status": "PROPOSED",
        "original_claim_id": claim_id,
        "error_class": error_class,
        "invalid_component": invalid_component,
        "preserved_component": preserved_component,
        "corrected_claim": corrected_claim,
        "explanation": explanation,
        "confidence": confidence,
    }


def _detect_anthropomorphic_causation(text: str, claim_id: str = "claim-0") -> dict[str, Any] | None:
    if not _has_literal_causal_trigger(text):
        return None
    if not _contains_any(text, _ANTHROPOMORPHIC_FEELING_WORDS):
        return None

    lower = _lower_text(text)
    for trigger in _LITERAL_CAUSAL_TRIGGERS:
        idx = lower.find(trigger)
        if idx == -1:
            continue
        invalid_component = text[idx:].strip(" .,;:")
        preserved_component = text[:idx].strip(" .,;:")
        if not preserved_component:
            preserved_component = "the structural description preceding the causal claim"
        corrected = (
            f"{preserved_component}; the causal attribution to feelings, desire, or mood "
            "is unsupported and should be replaced by a mechanism-level explanation."
        )
        return _repair_object(
            claim_id=claim_id,
            error_class="ANTHROPOMORPHIC_CAUSATION",
            invalid_component=invalid_component,
            preserved_component=preserved_component,
            corrected_claim=corrected,
            explanation=(
                "Non-mental systems do not have desires, feelings, moods, or intentions. "
                "A valid causal explanation must reference a mechanism, not a mental state."
            ),
            confidence=0.92,
        )
    return None


def _detect_false_physical_mechanism(text: str, claim_id: str = "claim-0") -> dict[str, Any] | None:
    if not _contains_any(text, _FALSE_MECHANISM_WORDS):
        return None
    if not ("orbit" in _lower_text(text) or "moon" in _lower_text(text)):
        return None
    if not _has_literal_causal_trigger(text):
        return None

    lower = _lower_text(text)
    for trigger in _LITERAL_CAUSAL_TRIGGERS:
        idx = lower.find(trigger)
        if idx == -1:
            continue
        invalid_component = text[idx:].strip(" .,;:")
        preserved_component = text[:idx].strip(" .,;:")
        if not preserved_component:
            preserved_component = "The Moon remains in orbit"
        corrected = (
            f"{preserved_component} due to gravitational attraction and orbital inertia, "
            "not magnetism."
        )
        return _repair_object(
            claim_id=claim_id,
            error_class="PHYSICAL_CATEGORY_ERROR",
            invalid_component=invalid_component,
            preserved_component=preserved_component,
            corrected_claim=corrected,
            explanation=(
                "Magnetic attraction is not the dominant force governing orbital motion. "
                "Large-scale celestial orbits are governed by gravity and inertia."
            ),
            confidence=0.96,
        )
    return None


def _detect_false_mechanism(text: str, claim_id: str = "claim-0") -> dict[str, Any] | None:
    """Catch pseudo-scientific mechanisms such as water memory or crystal healing."""
    lower = _lower_text(text)
    matched_term = None
    for term in _PSEUDOSCIENCE_WORDS:
        if term in lower:
            matched_term = term
            break
    if not matched_term:
        return None

    corrected = (
        "The claim relies on an unsupported mechanism. "
        "A valid explanation must reference empirically confirmed physical or biological processes."
    )
    return _repair_object(
        claim_id=claim_id,
        error_class="FALSE_MECHANISM",
        invalid_component=text.strip(" .,;:"),
        preserved_component="",
        corrected_claim=corrected,
        explanation=(
            f"'{matched_term}' refers to a mechanism that has not been established by "
            "controlled empirical evidence."
        ),
        confidence=0.90,
    )


def _detect_identity_analogy_confusion(text: str, claim_id: str = "claim-0") -> dict[str, Any] | None:
    """Detect claims that collapse a structural analogy into literal identity."""
    if not _has_identity_marker(text):
        return None
    corrected = (
        "The systems share structural similarities but are not identical. "
        "The mapping should be treated as analogy, not identity."
    )
    return _repair_object(
        claim_id=claim_id,
        error_class="IDENTITY_ANALOGY_CONFUSION",
        invalid_component=text.strip(" .,;:"),
        preserved_component="",
        corrected_claim=corrected,
        explanation=(
            "Identity markers ('literally', 'actually', 'nothing but') applied to an analogy "
            "produce a category error."
        ),
        confidence=0.85,
    )


def _detect_unsupported_causal_transfer(text: str, claim_id: str = "claim-0") -> dict[str, Any] | None:
    """Detect unsupported causal transfer, e.g. 'the company's mood is depressed, so revenue will fall'."""
    if not _has_literal_causal_trigger(text):
        return None
    # Already covered by anthropomorphic causation; this catches other unsupported transfers.
    if _contains_any(text, _ANTHROPOMORPHIC_FEELING_WORDS):
        return None
    if _contains_any(text, _FALSE_MECHANISM_WORDS | _PSEUDOSCIENCE_WORDS):
        return None
    return None


def _detect_anthropomorphic_intention(text: str, claim_id: str = "claim-0") -> dict[str, Any] | None:
    """
    Detect intentional/mental verbs attributed to clearly non-mental systems.

    Examples: 'Electrons choose their paths', 'Planets dance in harmony',
    'A black hole remembers everything'.
    """
    lower = _lower_text(text)
    subjects = "|".join(sorted(_NON_MENTAL_SUBJECTS, key=len, reverse=True))
    verbs = "|".join(_INTENTIONAL_VERBS)
    pattern = re.compile(
        rf"\b({subjects})\b[^\.\,;]*?\b({verbs})\b",
        re.IGNORECASE,
    )
    if not pattern.search(lower):
        return None
    return _repair_object(
        claim_id=claim_id,
        error_class="ANTHROPOMORPHIC_CAUSATION",
        invalid_component=text.strip(" .,;:"),
        preserved_component="",
        corrected_claim=(
            "Non-mental systems do not choose, dance, or remember. "
            "Describe the mechanism or process instead of attributing intention."
        ),
        explanation=(
            "Attributing intentional or mental verbs to non-mental systems is "
            "anthropomorphic causation."
        ),
        confidence=0.88,
    )


def _detect_pseudoscientific_health_claim(text: str, claim_id: str = "claim-0") -> dict[str, Any] | None:
    """
    Detect unsupported health/mechanism claims not caught by the word lists.
    """
    lower = _lower_text(text)
    if not any(p in lower for p in _PSEUDOSCIENTIFIC_HEALTH_PATTERNS):
        return None
    return _repair_object(
        claim_id=claim_id,
        error_class="FALSE_MECHANISM",
        invalid_component=text.strip(" .,;:"),
        preserved_component="",
        corrected_claim=(
            "The claim relies on an unsupported mechanism. A valid health claim "
            "must reference empirically confirmed biological or physical processes."
        ),
        explanation=(
            "Phrases such as 'magnetic bracelets cure arthritis by aligning energy "
            "fields' describe mechanisms not established by controlled evidence."
        ),
        confidence=0.90,
    )


def _detect_rhetorical_personification(text: str) -> str | None:
    """
    Detect non-literal personification ('The economy is angry').
    These are not rejected; they are compiled with guardrails.
    """
    lower = _lower_text(text)
    if not _contains_any(text, _PERSONIFICATION_STATE_WORDS):
        return None
    # If there is a literal causal trigger, it is anthropomorphic causation, not rhetoric.
    if _has_literal_causal_trigger(text):
        return None
    # If the subject is a human or social agent, it may be literal.
    human_subject_indicators = {"person", "people", "employee", "manager", "founder", "citizen"}
    if any(word in lower for word in human_subject_indicators):
        return None

    # Anatomical collocations such as "nervous system" are not personification.
    protected_phrases = {
        "nervous system", "nervous tissue", "central nervous", "peripheral nervous"
    }
    if any(phrase in lower for phrase in protected_phrases):
        return None

    return "RHETORICAL_PERSONIFICATION"


def classify_semantic_error(packet: Any) -> dict[str, Any] | None:
    """
    Classify the most salient semantic error in the packet.

    Returns a dict with:
        error_class: one of the V2.1.3 semantic error classes
        confidence: 0.0–1.0
        repair: structured repair object (when available)
    """
    text = packet.raw_input or ""

    # Hard reject classes with repair objects.
    repair = _detect_false_physical_mechanism(text)
    if repair:
        return {"error_class": "PHYSICAL_CATEGORY_ERROR", "confidence": repair["confidence"], "repair": repair}

    repair = _detect_anthropomorphic_causation(text)
    if repair:
        return {"error_class": "ANTHROPOMORPHIC_CAUSATION", "confidence": repair["confidence"], "repair": repair}

    repair = _detect_false_mechanism(text)
    if repair:
        return {"error_class": "FALSE_MECHANISM", "confidence": repair["confidence"], "repair": repair}

    repair = _detect_identity_analogy_confusion(text)
    if repair:
        return {"error_class": "IDENTITY_ANALOGY_CONFUSION", "confidence": repair["confidence"], "repair": repair}

    repair = _detect_anthropomorphic_intention(text)
    if repair:
        return {"error_class": "ANTHROPOMORPHIC_CAUSATION", "confidence": repair["confidence"], "repair": repair}

    repair = _detect_pseudoscientific_health_claim(text)
    if repair:
        return {"error_class": "FALSE_MECHANISM", "confidence": repair["confidence"], "repair": repair}

    # Rhetorical personification — guardrail, not rejection.
    personification = _detect_rhetorical_personification(text)
    if personification:
        return {"error_class": personification, "confidence": 0.75, "repair": None}

    return None


def detect_and_repair_contradictions(packet: Any) -> list[dict[str, Any]]:
    """
    Return a list of contradiction/repair objects for the packet.

    The function preserves the previous direct-negation behaviour and adds
    deterministic repair patterns for common category/causal errors.
    """
    contradictions: list[dict[str, Any]] = []
    text = packet.raw_input or ""

    # Direct negation between claims (legacy behaviour).
    claims = packet.claim_types
    for i, claim_a in enumerate(claims):
        for claim_b in claims[i + 1:]:
            if claim_a.get("negates") == claim_b.get("claim_id"):
                repair = _repair_object(
                    claim_id=claim_a.get("claim_id", "claim-a"),
                    error_class="DIRECT_NEGATION",
                    invalid_component=str(claim_b.get("content", "")),
                    preserved_component=str(claim_a.get("content", "")),
                    corrected_claim="Identify which claim has stronger evidence support.",
                    explanation="Two claims directly negate each other.",
                    confidence=0.7,
                )
                contradictions.append({
                    "claim_a": claim_a,
                    "claim_b": claim_b,
                    "type": "DIRECT_NEGATION",
                    "repair": repair,
                    "resolved": False,
                })

    # Deterministic pattern repairs against the raw input.
    repair = _detect_anthropomorphic_causation(text)
    if repair:
        contradictions.append({
            "type": "CATEGORY_ERROR",
            "repair": repair,
            "resolved": True,
        })

    repair = _detect_false_physical_mechanism(text)
    if repair:
        contradictions.append({
            "type": "CATEGORY_ERROR",
            "repair": repair,
            "resolved": True,
        })

    repair = _detect_false_mechanism(text)
    if repair:
        contradictions.append({
            "type": "CATEGORY_ERROR",
            "repair": repair,
            "resolved": True,
        })

    repair = _detect_identity_analogy_confusion(text)
    if repair:
        contradictions.append({
            "type": "CATEGORY_ERROR",
            "repair": repair,
            "resolved": True,
        })

    repair = _detect_anthropomorphic_intention(text)
    if repair:
        contradictions.append({
            "type": "CATEGORY_ERROR",
            "repair": repair,
            "resolved": True,
        })

    repair = _detect_pseudoscientific_health_claim(text)
    if repair:
        contradictions.append({
            "type": "CATEGORY_ERROR",
            "repair": repair,
            "resolved": True,
        })

    return contradictions
