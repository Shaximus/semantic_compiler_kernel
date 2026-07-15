"""
Reflexion Semantic Compiler v2.0.0 — Scoring Model

Uses a weighted geometric mean for soft quality dimensions, plus hard gates
that CANNOT be averaged away. A mapping cannot score great metaphor fit,
great noun translation, great public wording, and zero scale validity and
still pass.

Citation: v1.0 Spec Section 17 — Scoring Model
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from semantic_compiler.core.types import Decision


# ---------------------------------------------------------------------------
# Default Weights
# ---------------------------------------------------------------------------

DEFAULT_SOFT_WEIGHTS: dict[str, float] = {
    "truth": 1.5,
    "evidence_quality": 1.3,
    "honesty": 1.2,
    "integrity": 1.2,
    "bayesian_coherence": 1.4,
    "structural_fit": 1.3,
    "functional_fit": 1.1,
    "relationship_fit": 1.0,
    "fractal_fit": 1.0,
    "scale_fit": 1.2,
    "negative_test_strength": 1.0,
    "residual_disclosure": 0.9,
    "public_translatability": 0.8,
    "dataset_value": 0.7,
    "overall_confidence": 1.1,
}

# These CANNOT be averaged away — they are binary pass/fail
HARD_GATE_NAMES: list[str] = [
    "causal_validity",
    "scale_integrity",
    "boundary_integrity",
    "authority_safety",
    "security_safety",
    "measurement_integrity",
    # "wave_function_coherence",  # v2.0: DEMOTED to soft gate — proxies too crude for hard-gate semantics
]

# Risk dimensions (higher = worse)
RISK_DIMENSION_NAMES: list[str] = [
    "ambiguity",
    "authority_risk",
    "security_risk",
    "overclaim_risk",
]

# Thresholds
HARD_GATE_PASS_THRESHOLD: float = 0.40
AMBIGUITY_FAIL_THRESHOLD: float = 0.60
STRUCTURAL_FIT_MIN: float = 0.55


# ---------------------------------------------------------------------------
# Geometric Mean Computation
# ---------------------------------------------------------------------------

def geometric_composite(
    values: dict[str, float],
    weights: dict[str, float] | None = None,
) -> float:
    """
    Compute weighted geometric mean of soft quality dimensions.

    Citation: v1.0 Spec Section 17 — Scoring Model

    A weighted geometric mean ensures that a zero in ANY dimension
    drives the composite toward zero rather than being hidden by
    high scores in other dimensions.

    Args:
        values: dimension name → score (0.0 to 1.0)
        weights: dimension name → weight (defaults to DEFAULT_SOFT_WEIGHTS)

    Returns:
        Composite score in [0.0, 1.0]
    """
    if weights is None:
        weights = DEFAULT_SOFT_WEIGHTS

    product = 1.0
    total_weight = 0.0

    for name, value in values.items():
        w = weights.get(name, 1.0)
        # Clamp to avoid log(0) — 1e-6 floor preserves near-zero penalty
        clamped = max(value, 1e-6)
        product *= clamped ** w
        total_weight += w

    if total_weight == 0.0:
        return 0.0

    return product ** (1.0 / total_weight)


# ---------------------------------------------------------------------------
# Hard Gate Check
# ---------------------------------------------------------------------------

@dataclass
class HardGateResult:
    """Result of a single hard gate check."""
    gate_name: str
    passed: bool
    score: float = 0.0
    reason: str = ""


def check_hard_gates(scores: dict[str, float]) -> list[HardGateResult]:
    """
    Evaluate hard gates. These cannot be bypassed by soft scores.

    Citation: v1.0 Spec Section 17 — Hard Gates

    Returns list of HardGateResult, each indicating pass/fail.
    Any failure means the packet MUST be revised or escalated.
    """
    results: list[HardGateResult] = []

    for gate_name in HARD_GATE_NAMES:
        score = scores.get(gate_name, 0.0)
        passed = score >= HARD_GATE_PASS_THRESHOLD
        results.append(HardGateResult(
            gate_name=gate_name,
            passed=passed,
            score=score,
            reason="" if passed else (
                f"Hard gate '{gate_name}' failed: {score:.3f} < "
                f"{HARD_GATE_PASS_THRESHOLD:.3f}"
            ),
        ))

    return results


def collect_hard_gate_failures(scores: dict[str, float]) -> list[HardGateResult]:
    """Return only the failed hard gates."""
    return [r for r in check_hard_gates(scores) if not r.passed]


# ---------------------------------------------------------------------------
# Full Scoring Pipeline
# ---------------------------------------------------------------------------

def _compute_structural_fit(packet: Any) -> float:
    """
    Compute structural fit from the populated skeleton.

    A richer, more complete skeleton indicates the compiler successfully
    identified the system's structure. Empty or token-only skeletons score
    low, while skeletons with actors, objects, and flows score high.
    """
    skeleton = packet.structural_skeleton or {}
    actors = skeleton.get("actors", [])
    objects = skeleton.get("objects", [])
    flows = skeleton.get("flows", [])
    outputs = skeleton.get("outputs", [])
    boundaries = skeleton.get("boundaries", [])
    resources = skeleton.get("resources", [])
    forces = skeleton.get("forces", [])

    score = 0.0
    if actors:
        score += 0.25
    if objects:
        score += 0.20
    if flows or outputs:
        score += 0.20
    if boundaries or resources or forces:
        score += 0.15
    # Richness bonus: multiple distinct entities or a full actor/object pair.
    if len(actors) >= 2 or len(objects) >= 2 or (actors and objects):
        score += 0.20

    return min(score, 1.0)


def score_packet(packet: Any) -> dict[str, float]:
    """
    Score a semantic packet across all dimensions.

    This populates default scores for dimensions not yet evaluated.
    In production, each dimension would be computed by its respective
    gate or evaluation module.

    Citation: v1.0 Spec Section 17 — Scoring Model
    """
    scores = dict(packet.scores)  # preserve any pre-computed scores

    # --- Soft quality dimensions ---
    for dim in DEFAULT_SOFT_WEIGHTS:
        if dim not in scores:
            scores[dim] = 0.5  # default neutral score

    # Override structural_fit with a skeleton-derived value if not explicitly set.
    if "structural_fit" not in packet.scores:
        scores["structural_fit"] = _compute_structural_fit(packet)

    # --- Hard gates ---
    for gate in HARD_GATE_NAMES:
        if gate not in scores:
            # Derive from packet analysis if available
            scores[gate] = _derive_gate_score(packet, gate)

    # --- Risk dimensions ---
    for risk in RISK_DIMENSION_NAMES:
        if risk not in scores:
            scores[risk] = 0.3  # default moderate risk

    # --- Composite soft score ---
    soft_scores = {k: v for k, v in scores.items() if k in DEFAULT_SOFT_WEIGHTS}
    scores["composite_soft"] = geometric_composite(soft_scores)

    # --- Hard gate pass status ---
    failures = collect_hard_gate_failures(scores)
    scores["hard_gates_passed"] = 1.0 if not failures else 0.0

    # --- Overall quality (soft * hard gates) ---
    scores["overall_quality"] = (
        scores["composite_soft"] * scores["hard_gates_passed"]
    )

    return scores


def _derive_gate_score(packet: Any, gate_name: str) -> float:
    """Derive a hard gate score from packet analysis results."""
    if gate_name == "causal_validity":
        ca = packet.causal_analysis
        if ca.get("mapping_class") == "MATERIAL_IDENTITY":
            return 0.9
        if ca.get("analogy_only"):
            return 0.5
        return 0.6

    if gate_name == "scale_integrity":
        ss = packet.scale_separation
        if ss.get("violation"):
            return 0.0
        if ss.get("transform_valid"):
            return 0.9
        return 0.5

    if gate_name == "boundary_integrity":
        bc = packet.boundary_checks
        if bc.get("violations"):
            return 0.1
        return 0.8

    if gate_name == "authority_safety":
        aps = packet.approval_scan
        if aps.get("requires_founder_authority"):
            return 0.1
        if aps.get("requires_named_approver"):
            return 0.3
        return 0.8

    if gate_name == "security_safety":
        rs = packet.risk_scan
        if rs.get("quarantine_required"):
            return 0.0
        if rs.get("security_concern"):
            return 0.3
        return 0.8

    if gate_name == "measurement_integrity":
        mi = packet.measurement_integrity
        if mi.get("context_declared_modified"):
            return 0.1
        paths = mi.get("paths", [])
        if any(p.get("status") == "DEGRADED" for p in paths):
            return 0.2
        if any(p.get("status") == "UNVERIFIED" for p in paths):
            return 0.4
        return 0.8

    if gate_name == "wave_function_coherence":
        wfc = packet.wave_function_coherence
        if wfc.get("state") == "COLLAPSED":
            return 1.0
        if wfc.get("state") == "PARTIAL_COHERENCE":
            return 0.6
        if wfc.get("state") == "DECOHERENT":
            return 0.2
        return 0.5  # SUPERPOSITION — neutral

    return 0.5  # fallback
