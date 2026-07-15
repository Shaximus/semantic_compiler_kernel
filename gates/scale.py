"""
Reflexion Semantic Compiler v2.0.0 — Scale Separation Gate

Hard gate: properties cannot cross scale without an explicit
aggregation or decomposition rule.

No property crosses scale merely because the metaphor sounds elegant.

Citation: v1.0 Spec Section 10 — Scale Transform
Global Law: scale_separation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from semantic_compiler.core.types import ScaleType, ScaleTransform


# Scale ordering for distance calculation
SCALE_ORDER = [
    ScaleType.QUANTUM,
    ScaleType.CELLULAR,
    ScaleType.COMPONENT,
    ScaleType.PROCESS,
    ScaleType.AGENT,
    ScaleType.TEAM,
    ScaleType.DEPARTMENTAL,
    ScaleType.ORGANIZATIONAL,
    ScaleType.INSTITUTIONAL,
    ScaleType.NATIONAL,
    ScaleType.CIVILIZATIONAL,
    ScaleType.COSMOLOGICAL,
]


def scale_distance(source: ScaleType, target: ScaleType) -> int:
    """
    Calculate the ordinal distance between two scales.
    Higher distance means more transformation rules are required.
    """
    if source in (ScaleType.EVENT, ScaleType.SYMBOLIC):
        return -1  # EVENT and SYMBOLIC are orthogonal, not ordinal
    if target in (ScaleType.EVENT, ScaleType.SYMBOLIC):
        return -1

    try:
        s_idx = SCALE_ORDER.index(source)
        t_idx = SCALE_ORDER.index(target)
        return abs(t_idx - s_idx)
    except ValueError:
        return -1


def validate_scale_transform(transform: ScaleTransform) -> dict[str, Any]:
    """
    Validate a scale transformation.

    Rules:
    - Must have explicit preserved invariants
    - Must have explicit changed variables
    - Must have aggregation/decomposition rule for distance > 1
    - Must acknowledge information loss
    - Must list new failure modes introduced by scale change
    - Confidence decreases with scale distance

    Citation: v1.0 Spec Section 10
    """
    errors: list[str] = []
    warnings: list[str] = []
    gate_passed = True

    dist = scale_distance(transform.source_scale, transform.target_scale)

    # HARD GATE: No preserved invariants = no valid transform
    if not transform.preserved_invariants:
        errors.append(
            "Scale transform has no preserved invariants. "
            "Cannot validate what survives the transformation."
        )
        gate_passed = False

    # HARD GATE: No changed variables = claiming everything transfers
    if not transform.changed_variables and dist > 0:
        errors.append(
            "Scale transform claims no variables change across scales. "
            "This is almost certainly a scale collapse."
        )
        gate_passed = False

    # Large distance requires aggregation/decomposition rules
    if dist > 1:
        if not transform.aggregation_rule and not transform.decomposition_rule:
            errors.append(
                f"Scale distance is {dist} but no aggregation or decomposition "
                f"rule provided. Properties cannot jump {dist} scale levels "
                f"without explicit transformation rules."
            )
            gate_passed = False

    # Information loss should be acknowledged for any scale change
    if dist > 0 and not transform.information_lost:
        warnings.append(
            "Scale transform does not acknowledge information loss. "
            "All scale transformations lose some information."
        )

    # New failure modes should be identified
    if dist > 0 and not transform.new_failure_modes:
        warnings.append(
            "Scale transform does not identify new failure modes. "
            "Different scales typically introduce different failure modes."
        )

    # Confidence penalty for large scale jumps
    max_confidence = 1.0
    if dist > 0:
        max_confidence = max(0.1, 1.0 - (dist * 0.08))
    if transform.confidence > max_confidence:
        warnings.append(
            f"Confidence {transform.confidence:.2f} exceeds maximum "
            f"{max_confidence:.2f} for scale distance {dist}."
        )

    return {
        "gate_passed": gate_passed,
        "scale_distance": dist,
        "max_confidence": max_confidence,
        "errors": errors,
        "warnings": warnings,
        "source_scale": transform.source_scale.name,
        "target_scale": transform.target_scale.name,
        "preserved_count": len(transform.preserved_invariants),
        "changed_count": len(transform.changed_variables),
    }


def enforce_scale_separation(packet: Any) -> dict[str, Any]:
    """
    Master scale separation gate.

    Processes all scale-related claims in a packet and enforces
    that no property crosses scale without explicit transformation.

    Citation: v1.0 Spec Section 8, step 5
    """
    if hasattr(packet, "fractal_mappings"):
        mappings = packet.fractal_mappings
    else:
        mappings = packet.get("fractal_mappings", [])

    results: list[dict[str, Any]] = []
    any_failure = False

    for mapping in mappings:
        source_scale_str = mapping.get("source_scale", "")
        target_scale_str = mapping.get("target_scale", "")

        # Try to resolve scale types
        try:
            source_scale = ScaleType[source_scale_str.upper()] if source_scale_str else None
            target_scale = ScaleType[target_scale_str.upper()] if target_scale_str else None
        except (KeyError, AttributeError):
            source_scale = None
            target_scale = None

        if source_scale and target_scale:
            transform = ScaleTransform(
                source_scale=source_scale,
                target_scale=target_scale,
                preserved_invariants=mapping.get("preserved_invariants", []),
                changed_variables=mapping.get("changed_variables", []),
                aggregation_rule=mapping.get("aggregation_rule", ""),
                decomposition_rule=mapping.get("decomposition_rule", ""),
                information_lost=mapping.get("information_lost", ""),
                new_failure_modes=mapping.get("new_failure_modes", []),
                confidence=mapping.get("confidence", 0.5),
            )
            result = validate_scale_transform(transform)
        else:
            result = {
                "gate_passed": True,
                "warnings": ["Scale types not specified; cannot validate transform."],
                "errors": [],
            }

        if not result["gate_passed"]:
            any_failure = True

        results.append({
            "mapping": mapping.get("source", "") + "→" + mapping.get("target", ""),
            **result,
        })

    return {
        "transforms": results,
        "any_gate_failure": any_failure,
        "gate_status": "FAILED" if any_failure else "PASSED",
    }
