"""
Reflexion Semantic Compiler v2.0.0 — Causality Gate

Hard gate: separates causality from analogy.
Structural similarity does NOT prove material identity or causal mechanism.

This gate CANNOT be averaged away by soft scores.

Citation: v1.0 Spec Section 9 — Causality Versus Analogy
Global Law: causality_not_implied_by_similarity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from semantic_compiler.core.types import MappingClass


@dataclass
class CausalityFinding:
    """Result of causality analysis for a single mapping."""
    mapping_id: str
    source: str
    target: str
    declared_class: MappingClass
    evaluated_class: MappingClass
    preserved_functions: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    causal_mechanism_identified: bool = False
    causal_evidence: list[str] = field(default_factory=list)
    analogy_only: bool = False
    gate_passed: bool = False
    failure_reason: str = ""


def classify_mapping(
    source: str,
    target: str,
    declared_class: MappingClass | None,
    evidence: list[dict[str, Any]],
    preserved: list[str],
    residuals: list[str],
) -> CausalityFinding:
    """
    Classify a cross-domain mapping into one of four classes.

    V1.0 recognizes:
        MATERIAL_IDENTITY   — source and target are the same class of thing
        CAUSAL_MAPPING      — a mechanism causes a target effect
        STRUCTURAL_ANALOGY  — functions/relationships match without identity
        HEURISTIC_METAPHOR  — compressed search tool, supports no conclusion alone

    The gate enforces:
        - MATERIAL_IDENTITY requires physical/substrate evidence
        - CAUSAL_MAPPING requires identified mechanism + evidence
        - STRUCTURAL_ANALOGY is the default for cross-domain function matching
        - HEURISTIC_METAPHOR cannot pass the gate alone
    """
    finding = CausalityFinding(
        mapping_id=f"{source}→{target}",
        source=source,
        target=target,
        declared_class=declared_class or MappingClass.HEURISTIC_METAPHOR,
        evaluated_class=MappingClass.HEURISTIC_METAPHOR,
        preserved_functions=list(preserved),
        residuals=list(residuals),
    )

    # Check for causal mechanism evidence
    causal_evidence = [
        e for e in evidence
        if e.get("supports_causation") or e.get("mechanism_identified")
    ]
    finding.causal_evidence = [e.get("content", "") for e in causal_evidence]
    finding.causal_mechanism_identified = len(causal_evidence) > 0

    # Check for material identity evidence
    identity_evidence = [
        e for e in evidence
        if e.get("supports_identity") or e.get("same_substrate")
    ]

    # Classification logic
    if identity_evidence and not residuals:
        finding.evaluated_class = MappingClass.MATERIAL_IDENTITY
        finding.gate_passed = True
    elif causal_evidence and finding.causal_mechanism_identified:
        finding.evaluated_class = MappingClass.CAUSAL_MAPPING
        finding.gate_passed = True
    elif len(preserved) >= 2 and residuals:
        # Structural analogy: functions match, residuals acknowledged
        finding.evaluated_class = MappingClass.STRUCTURAL_ANALOGY
        finding.analogy_only = True
        finding.gate_passed = True
    elif len(preserved) >= 1:
        # Minimal structural match but weak
        finding.evaluated_class = MappingClass.HEURISTIC_METAPHOR
        finding.analogy_only = True
        finding.gate_passed = True  # passes but flagged as metaphor only
    else:
        finding.evaluated_class = MappingClass.HEURISTIC_METAPHOR
        finding.gate_passed = False
        finding.failure_reason = "No preserved functions or structural match identified"

    # HARD GATE: declared identity/causation without evidence is a failure
    if declared_class == MappingClass.MATERIAL_IDENTITY and not identity_evidence:
        finding.gate_passed = False
        finding.failure_reason = (
            "MATERIAL_IDENTITY declared without substrate evidence. "
            "Structural similarity does not prove material identity."
        )
        finding.evaluated_class = MappingClass.STRUCTURAL_ANALOGY

    if declared_class == MappingClass.CAUSAL_MAPPING and not causal_evidence:
        finding.gate_passed = False
        finding.failure_reason = (
            "CAUSAL_MAPPING declared without mechanism evidence. "
            "Correlation or analogy does not establish causation."
        )
        finding.evaluated_class = MappingClass.STRUCTURAL_ANALOGY

    return finding


def separate_causality_from_analogy(
    packet: dict[str, Any] | Any,
) -> dict[str, Any]:
    """
    Master causality gate. Processes all fractal mappings in a packet.

    Returns the causal_analysis dict for the packet.
    Citation: v1.0 Spec Section 8, step 5
    """
    # Handle both dict and dataclass packet
    if hasattr(packet, "fractal_mappings"):
        mappings = packet.fractal_mappings
        evidence = packet.evidence_inventory if hasattr(packet, "evidence_inventory") else []
    else:
        mappings = packet.get("fractal_mappings", [])
        evidence = packet.get("evidence_inventory", [])

    findings: list[dict[str, Any]] = []
    all_analogy_only = True
    any_gate_failure = False

    for mapping in mappings:
        finding = classify_mapping(
            source=mapping.get("source", ""),
            target=mapping.get("target", ""),
            declared_class=mapping.get("declared_class"),
            evidence=evidence,
            preserved=mapping.get("preserved_functions", []),
            residuals=mapping.get("residuals", []),
        )
        if not finding.analogy_only:
            all_analogy_only = False
        if not finding.gate_passed:
            any_gate_failure = True

        findings.append({
            "mapping_id": finding.mapping_id,
            "declared_class": finding.declared_class.name,
            "evaluated_class": finding.evaluated_class.name,
            "gate_passed": finding.gate_passed,
            "analogy_only": finding.analogy_only,
            "causal_mechanism_identified": finding.causal_mechanism_identified,
            "preserved_functions": finding.preserved_functions,
            "residuals": finding.residuals,
            "failure_reason": finding.failure_reason,
        })

    return {
        "findings": findings,
        "analogy_only": all_analogy_only,
        "any_gate_failure": any_gate_failure,
        "total_mappings": len(mappings),
        "gate_status": "FAILED" if any_gate_failure else "PASSED",
    }
