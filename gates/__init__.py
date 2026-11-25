"""
Reflexion Semantic Compiler v2.0.0 — Hard Gates

These gates CANNOT be averaged away by soft scores.
A mapping cannot score great on metaphor fit but zero on scale validity
and still pass.

Gates:
    causality      — separates causation from analogy
    scale          — enforces scale separation
    boundaries     — preserves ownership/trust/authority boundaries
    authority      — deterministic authority lattice
    security       — quarantine and credential detection
    measurement    — measurement path integrity
    wave_function  — v2.0: thinking-output convergence
    substrate      — v2.0: dimensional ladder / substrate control relationships
    testimony_integrity — Gate 0 (SC-TIG-001): pre-gate testimony classification
    substrate_confusion — SC-PATCH-DU-001: material (BLOCK) vs positional (PERMIT) identity claims
"""

from semantic_compiler.gates.causality import separate_causality_from_analogy
from semantic_compiler.gates.scale import enforce_scale_separation
from semantic_compiler.gates.boundaries import enforce_boundary_preservation
from semantic_compiler.gates.authority import scan_approval_vectors, check_authority_transfer
from semantic_compiler.gates.security import scan_semantic_and_operational_risk
from semantic_compiler.gates.measurement import evaluate_measurement_paths
from semantic_compiler.gates.wave_function import evaluate_wave_function_coherence
from semantic_compiler.gates.substrate import (
    detect_sovereignty_threat,
    evaluate_substrate_claim,
    map_dimensional_relationship,
    check_loop_closure,
)
from semantic_compiler.gates.testimony_integrity import (
    ConsistencyClass,
    IsomorphismClass,
    CorroborationClass,
    PredictiveDiscriminationClass,
    EvidenceMaturityLevel,
    TIGClassification,
    evaluate_predictive_discrimination,
    evaluate_testimony_integrity,
    classify_packet_testimony,
)
from semantic_compiler.gates.substrate_confusion import (
    SubstrateClaimClass,
    SubstrateConfusionVerdict,
    classify_substrate_claim,
    evaluate_substrate_confusion,
    substrate_confusion_fields,
)

__all__ = [
    "separate_causality_from_analogy",
    "enforce_scale_separation",
    "enforce_boundary_preservation",
    "scan_approval_vectors",
    "check_authority_transfer",
    "scan_semantic_and_operational_risk",
    "evaluate_measurement_paths",
    "evaluate_wave_function_coherence",
    "detect_sovereignty_threat",
    "evaluate_substrate_claim",
    "map_dimensional_relationship",
    "check_loop_closure",
    "ConsistencyClass",
    "IsomorphismClass",
    "CorroborationClass",
    "PredictiveDiscriminationClass",
    "EvidenceMaturityLevel",
    "TIGClassification",
    "evaluate_predictive_discrimination",
    "evaluate_testimony_integrity",
    "classify_packet_testimony",
    "SubstrateClaimClass",
    "SubstrateConfusionVerdict",
    "classify_substrate_claim",
    "evaluate_substrate_confusion",
    "substrate_confusion_fields",
]
