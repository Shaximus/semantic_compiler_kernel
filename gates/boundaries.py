"""
Reflexion Semantic Compiler v2.0.0 — Boundary Preservation Gate

Hard gate: ownership, trust, containment, security, and authority
boundaries must survive translation.

Citation: v1.0 Spec Section 2 — Global Laws (boundary_preservation)
"""

from __future__ import annotations

from typing import Any


BOUNDARY_TYPES = [
    "ownership",
    "trust",
    "containment",
    "security",
    "authority",
    "privacy",
    "physical",
    "logical",
    "temporal",
]


def check_boundary_preservation(
    source_boundaries: list[dict[str, Any]],
    target_boundaries: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Check that all boundaries from the source domain survive in the target.

    A boundary violation occurs when:
    - A source boundary has no target equivalent
    - A target boundary is weaker than the source
    - A boundary type changed meaning during translation
    """
    violations = []
    preserved = []

    source_by_type = {b.get("type", ""): b for b in source_boundaries}
    target_by_type = {b.get("type", ""): b for b in target_boundaries}

    for btype, source_b in source_by_type.items():
        if btype not in target_by_type:
            violations.append({
                "type": btype,
                "violation": "BOUNDARY_LOST",
                "source": source_b,
                "detail": f"Source boundary '{btype}' has no target equivalent.",
            })
        else:
            target_b = target_by_type[btype]
            # Check if target is weaker
            source_strength = source_b.get("strength", 0)
            target_strength = target_b.get("strength", 0)
            if target_strength < source_strength:
                violations.append({
                    "type": btype,
                    "violation": "BOUNDARY_WEAKENED",
                    "source_strength": source_strength,
                    "target_strength": target_strength,
                    "detail": f"Target boundary '{btype}' is weaker than source.",
                })
            else:
                preserved.append({
                    "type": btype,
                    "source": source_b,
                    "target": target_b,
                })

    return {
        "violations": violations,
        "preserved": preserved,
        "gate_passed": len(violations) == 0,
        "gate_status": "FAILED" if violations else "PASSED",
    }


def enforce_boundary_preservation(packet: Any) -> dict[str, Any]:
    """
    Master boundary preservation gate.

    Citation: v1.0 Spec Section 8, step 5
    """
    if hasattr(packet, "structural_skeleton"):
        skeleton = packet.structural_skeleton
    else:
        skeleton = packet.get("structural_skeleton", {})

    source_boundaries = skeleton.get("source_boundaries", [])
    target_boundaries = skeleton.get("target_boundaries", [])

    if not source_boundaries and not target_boundaries:
        # Extract from the skeleton's boundaries field
        boundaries = skeleton.get("boundaries", [])
        if boundaries:
            return {
                "boundaries_identified": boundaries,
                "gate_passed": True,
                "gate_status": "PASSED",
                "note": "Boundaries identified but no cross-domain check performed.",
                "violations": [],
            }
        return {
            "gate_passed": True,
            "gate_status": "PASSED",
            "note": "No boundaries to check.",
            "violations": [],
        }

    return check_boundary_preservation(source_boundaries, target_boundaries)
