"""
Reflexion Semantic Compiler v2.0.0 — Logos Dataset Row V2.1 Exporter

Canonical dataset-row builder aligned with:
    LOGOS SEMANTIC DATASET PROTOCOL V2.1

Produces the versioned training-data envelope used by SFT, DPO,
contrastive learning, retrieval, isomorphism judging, and repair models.

Citation: /home/shax/Downloads/LOGOS_SEMANTIC_DATASET_PROTOCOL_V2_1.md
Citation: /home/shax/Downloads/logos_semantic_training_sample_v2_1.schema.json
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from semantic_compiler.core.types import (
    CompilerMode,
    DatasetTier,
    Decision,
    MappingClass,
    PrivacySensitivity,
    ScaleType,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "2.1.0"
EXTRACTOR_VERSION = "skeleton-np-v2"

_LOGOS_SAMPLE_ID_PREFIX = "LOGOS:SAMPLE"

_TRUST_LEVEL_DEFAULT = "DIRECT"
_LICENSE_DEFAULT = "OWNED"
_MUTATION_STATE_DEFAULT = "ORIGINAL"

# Weights for the mapping-level isomorphism quality geometric mean.
_ISO_QUALITY_WEIGHTS: dict[str, float] = {
    "structural_fit": 1.4,
    "functional_fit": 1.3,
    "relationship_fit": 1.2,
    "preserved_invariant_coverage": 1.4,
    "scale_transform_validity": 1.4,
    "negative_test_strength": 1.2,
    "residual_disclosure": 1.0,
    "evidence_support": 1.3,
    "alternative_explanation_pressure": 0.8,
    "overclaim_control": 1.2,
}

# Dimensions that must have at least one populated value for a mapping to be
# considered assessed.  Without any of these, the mapping is UNASSESSED.
_CORE_ANALYSIS_DIMENSIONS: set[str] = {
    "structural_fit",
    "functional_fit",
    "relationship_fit",
    "preserved_invariant_coverage",
    "scale_transform_validity",
    "negative_test_strength",
    "evidence_support",
}

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _geometric_mean(values: dict[str, float], weights: dict[str, float]) -> float:
    """Weighted geometric mean; clamps at 1e-6 to avoid log(0)."""
    product = 1.0
    total_weight = 0.0
    for key, value in values.items():
        w = weights.get(key, 1.0)
        clamped = max(float(value), 1e-6)
        product *= clamped ** w
        total_weight += w
    if total_weight == 0.0:
        return 0.0
    return product ** (1.0 / total_weight)


def _as_name(obj: Any) -> str | None:
    """Return the .name of an enum-like object, or None."""
    return obj.name if obj is not None and hasattr(obj, "name") else None


def _scale_name(scale: Any) -> str | None:
    """Normalize a ScaleType or string to its schema enum name."""
    if scale is None:
        return None
    if isinstance(scale, ScaleType):
        return scale.name
    if isinstance(scale, str):
        return scale.upper()
    return str(scale).upper()


def _mapping_class_name(mc: Any) -> str:
    """Normalize a MappingClass or string to its schema enum name."""
    if mc is None:
        return "STRUCTURAL_ANALOGY"
    if isinstance(mc, MappingClass):
        return mc.name
    if isinstance(mc, str):
        upper = mc.upper()
        if upper in {"MATERIAL_IDENTITY", "CAUSAL_MAPPING", "STRUCTURAL_ANALOGY", "HEURISTIC_METAPHOR"}:
            return upper
    return "STRUCTURAL_ANALOGY"


def _to_training_external_use(value: str) -> str:
    """Map packet.external_training_use to the V2.1 privacy enum."""
    mapping = {
        "forbidden": "PROHIBITED",
        "approved": "ALLOWED",
        "redacted_only": "REDACTED_ONLY",
    }
    return mapping.get(str(value).lower(), "PROHIBITED")


def _to_sensitivity_name(ps: PrivacySensitivity) -> str:
    return ps.name if isinstance(ps, PrivacySensitivity) else str(ps).upper()


def _derive_sample_kind(packet: Any) -> str:
    """Derive the V2.1 sample_kind from the compiler decision."""
    decision = packet.decision
    if decision is None:
        return "UNRESOLVED"

    if decision in (Decision.COMPILED, Decision.COMPILED_WITH_GUARDRAILS, Decision.COMPILED_SUPERVISED_ONLY):
        return "POSITIVE"
    if decision == Decision.COMPILED_PRIVATE_REDACTED_ONLY:
        return "REPAIR"
    if decision in (Decision.NEEDS_REVISION, Decision.REJECT, Decision.QUARANTINE):
        # If the packet contains a repair/correction, it is a repair sample.
        for c in packet.contradictions:
            if isinstance(c, dict) and (c.get("repair") or c.get("resolved")):
                return "REPAIR"
        return "NEGATIVE"
    if decision in (Decision.ROUTE_FOR_APPROVAL, Decision.ESCALATE):
        return "UNRESOLVED"
    return "BOUNDARY_CASE"


def _derive_status(packet: Any) -> str:
    """Derive the V2.1 status from packet state."""
    if packet.decision in (Decision.REJECT, Decision.QUARANTINE):
        return "REJECTED"
    if packet.status == "compiled":
        return "COMPILED"
    if packet.status == "needs_revision":
        return "DRAFT"
    return "DRAFT"


def _sample_id(packet: Any) -> str:
    """Stable Logos sample id from packet id."""
    base = str(packet.packet_id)[:16]
    return f"{_LOGOS_SAMPLE_ID_PREFIX}:{base}"


def _has_resolved_contradictions(packet: Any) -> bool:
    """True if at least one contradiction has a repair or is marked resolved."""
    for contradiction in packet.contradictions:
        if isinstance(contradiction, dict):
            if contradiction.get("repair") or contradiction.get("resolved"):
                return True
    return False


def _classify_tier(packet: Any) -> DatasetTier:
    """
    Classify the dataset tier of a packet.
    Citation: v1.0 Spec Section 21 — Dataset Tiers
    """
    if packet.decision is None:
        return DatasetTier.BRONZE

    if packet.decision == Decision.QUARANTINE:
        return DatasetTier.REJECT

    # A REJECT decision that carries a structured repair is still valuable
    # training material; tier it by dataset value rather than rejecting it.
    if packet.decision == Decision.REJECT and not _has_resolved_contradictions(packet):
        return DatasetTier.REJECT

    scores = packet.scores
    dataset_value = scores.get("dataset_value", 0.0)

    # Diamond+++ criteria (from Diamond+++ ore document):
    # Contains failure mode + correction + guardrail + scale-separation check
    has_corrections = _has_resolved_contradictions(packet)
    has_negative_tests = bool(packet.negative_isomorphism_tests)
    has_residuals = bool(packet.residual_mismatches)

    if dataset_value >= 0.95 and has_corrections and has_negative_tests and has_residuals:
        return DatasetTier.DIAMOND_PLUS

    if dataset_value >= 0.85 and has_corrections and has_negative_tests:
        return DatasetTier.DIAMOND

    if dataset_value >= 0.70 and has_corrections:
        return DatasetTier.GOLD

    if dataset_value >= 0.50:
        return DatasetTier.SILVER

    return DatasetTier.BRONZE


# ---------------------------------------------------------------------------
# Sub-envelope builders
# ---------------------------------------------------------------------------


def _build_provenance(packet: Any) -> dict[str, Any]:
    ctx = packet.source_context
    evidence_chain: list[dict[str, Any]] = []
    for ev in packet.evidence_inventory:
        if not isinstance(ev, dict):
            continue
        evidence_chain.append({
            "evidence_id": ev.get("evidence_id", f"ev-{uuid.uuid4().hex[:8]}"),
            "source_type": ev.get("source_type", "TRANSCRIPT"),
            "content": ev.get("content", ev.get("excerpt", "")),
            "directness": str(ev.get("directness", "DERIVED")).upper(),
            "confidence": float(ev.get("confidence", 0.5)),
            "source_path": ev.get("source_path"),
            "source_hash": ev.get("source_hash"),
            "measurement_path_integrity": str(ev.get(
                "measurement_path_integrity", "NOT_APPLICABLE"
            )).upper(),
            "notes": ev.get("notes"),
        })

    return {
        "source_type": ctx.source_type or "conversation",
        "origin": ctx.origin or "semantic-compiler",
        "source_path": ctx.source_path,
        "source_uri": None,
        "raw_hash": packet.source_context.source_hash or packet.compute_input_hash(),
        "captured_at": ctx.timestamp or _now_iso(),
        "trust_level": (ctx.trust_level or _TRUST_LEVEL_DEFAULT).upper(),
        "mutation_state": _MUTATION_STATE_DEFAULT,
        "license_or_consent": _LICENSE_DEFAULT,
        "evidence_chain": evidence_chain,
    }


def _build_claims(packet: Any) -> list[dict[str, Any]]:
    """Normalize packet claim_types and SemanticIR claims into V2.1 claim list."""
    claims: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Prefer claim_types from extraction
    for i, ct in enumerate(packet.claim_types):
        if isinstance(ct, dict):
            cid = ct.get("claim_id") or f"claim-{i}"
            claims.append({
                "claim_id": cid,
                "content": ct.get("content", packet.raw_input or ""),
                "claim_type": str(ct.get("claim_type", "OBSERVATION")).upper(),
                "confidence": float(ct.get("confidence", 0.5)),
                "scale": _scale_name(ct.get("scale")),
                "evidence_ids": ct.get("evidence_ids", []),
                "authority_required": ct.get("authority_required", "NONE"),
            })
            seen_ids.add(cid)

    # Fill from SemanticIR if extraction produced none
    for i, c in enumerate(packet.semantic_ir.claims):
        if isinstance(c, dict):
            cid = c.get("claim_id") or f"sir-claim-{i}"
            if cid in seen_ids:
                continue
            claims.append({
                "claim_id": cid,
                "content": c.get("content", packet.raw_input or ""),
                "claim_type": str(c.get("claim_type", "OBSERVATION")).upper(),
                "confidence": float(c.get("confidence", 0.5)),
                "scale": _scale_name(c.get("scale")),
                "evidence_ids": [],
                "authority_required": "NONE",
            })

    if not claims and packet.raw_input:
        claims.append({
            "claim_id": "claim-0",
            "content": packet.raw_input,
            "claim_type": "OBSERVATION",
            "confidence": 0.5,
            "scale": None,
            "evidence_ids": [],
            "authority_required": "NONE",
        })

    return claims


def _build_input(packet: Any) -> dict[str, Any]:
    # Preserve immutable raw input, but redact literal text for sensitive/critical
    # packets so the training envelope does not leak private data.
    raw = packet.raw_input or ""
    if packet.privacy_sensitivity in (
        PrivacySensitivity.SENSITIVE,
        PrivacySensitivity.CRITICAL,
    ):
        raw = "[REDACTED — structural derivative only]"

    return {
        "raw_input": raw,
        "normalized_input": packet.normalized_input or packet.raw_input or "",
        "context": {},
        "claims": _build_claims(packet),
        "declared_constraints": list(packet.declared_constraints),
        "unknowns": list(packet.unknowns),
        "rejected_assumptions": list(packet.rejected_assumptions),
    }


def _target_resolution(packet: Any) -> dict[str, Any]:
    selected = packet.selected_target
    candidates = list(packet.target_systems)
    ranking: list[dict[str, Any]] = []
    for c in candidates:
        ranking.append({
            "target": c,
            "score": 1.0 if c == selected else 0.5,
            "reason": "top candidate" if c == selected else "alternative candidate",
        })

    if selected:
        status = "RESOLVED"
        failure_reason = None
        confidence = 0.8
    elif candidates:
        status = "AMBIGUOUS"
        failure_reason = "multiple candidate targets; no clear selection"
        confidence = 0.4
    else:
        status = "UNRESOLVED"
        failure_reason = "no target system resolved; interpretation would be forced"
        confidence = 0.0

    # Detect a genuinely forced target: a target was selected despite explicit
    # ambiguity or a policy override forcing interpretation.
    if selected:
        forced_signals = ["forced target", "target forced"]
        for w in packet.compiler_warnings:
            if any(sig in str(w).lower() for sig in forced_signals):
                status = "FORCED"
                failure_reason = str(w)
                break

    # Determine mapping direction.
    source = packet.source_frames[0] if packet.source_frames else None
    if selected and source:
        if source.lower() == selected.lower():
            mapping_direction = "BIDIRECTIONAL"
            direction_confidence = 0.5
        else:
            mapping_direction = "EXPLICIT"
            direction_confidence = 0.8
    elif selected:
        mapping_direction = "INFERRED_FROM_CONTEXT"
        direction_confidence = 0.5
    else:
        mapping_direction = "UNRESOLVED"
        direction_confidence = 0.0

    return {
        "status": status,
        "selected_target": selected,
        "confidence": confidence,
        "failure_reason": failure_reason,
        "candidate_ranking": ranking,
        "mapping_direction": mapping_direction,
        "direction_confidence": direction_confidence,
    }


def _semantic_ir(packet: Any) -> dict[str, Any]:
    sir = packet.semantic_ir
    return {
        "claims": sir.claims,
        "entities": sir.entities,
        "relationships": [
            {
                "relationship_id": r.get("relationship_id", ""),
                "source_entity_id": r.get("source_entity_id", ""),
                "target_entity_id": r.get("target_entity_id", ""),
                "relationship_type": str(r.get("relationship_type", "ANALOGOUS_TO")).upper(),
                "confidence": float(r.get("confidence", 0.0)),
                "mapping_class": _mapping_class_name(r.get("mapping_class")),
                "residuals": r.get("residuals", []),
            }
            for r in sir.relationships
            if isinstance(r, dict)
        ],
    }


def _structural_skeleton(packet: Any) -> dict[str, Any]:
    skel = packet.structural_skeleton or {}
    actors = [str(a) for a in skel.get("actors", [])]
    objects = [str(o) for o in skel.get("objects", [])]
    boundaries = [str(b) for b in skel.get("boundaries", [])]
    inputs = [str(i) for i in skel.get("inputs", [])]
    outputs = [str(o) for o in skel.get("outputs", [])]
    resources = [str(r) for r in skel.get("resources", [])]
    flows = [str(f) for f in skel.get("flows", [])]
    forces = [str(f) for f in skel.get("forces", [])]
    control_loops = skel.get("control_loops", [])
    feedback_loops = skel.get("feedback_loops", [])
    hidden_states = [str(h) for h in skel.get("hidden_states", [])]
    failure_modes = [str(fm) for fm in skel.get("failure_modes", [])]
    time_horizons = [str(t) for t in skel.get("time_horizons", [])]
    scale_layers = [str(s) for s in skel.get("scale_layers", [])]

    loop_count = len(control_loops) + len(feedback_loops)
    richness = 0.0
    if actors:
        richness += 0.15
    if objects:
        richness += 0.15
    if flows:
        richness += 0.15
    if boundaries:
        richness += 0.1
    if outputs:
        richness += 0.1
    if resources:
        richness += 0.1
    if forces:
        richness += 0.1
    if loop_count:
        richness += 0.15

    return {
        "actors": actors,
        "objects": objects,
        "boundaries": boundaries,
        "inputs": inputs,
        "outputs": outputs,
        "resources": resources,
        "flows": flows,
        "forces": forces,
        "control_loops": control_loops,
        "feedback_loops": feedback_loops,
        "hidden_states": hidden_states,
        "failure_modes": failure_modes,
        "time_horizons": time_horizons,
        "scale_layers": scale_layers,
        "metrics": {
            "actor_count": len(actors),
            "object_count": len(objects),
            "relationship_count": len(packet.semantic_ir.relationships),
            "boundary_count": len(boundaries),
            "loop_count": loop_count,
            "failure_mode_count": len(failure_modes),
            "richness_score": round(min(richness, 1.0), 4),
            "duplicate_candidate_count": 0,
        },
        "extraction_warnings": [],
    }


def _translations(packet: Any) -> dict[str, Any]:
    def _norm(items: list[Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for i, t in enumerate(items):
            if isinstance(t, dict):
                out.append(t)
            else:
                out.append({"item": str(t), "confidence": 0.5})
        return out

    return {
        "nouns": _norm(packet.noun_translation),
        "functions": _norm(packet.function_translation),
        "relationships": _norm(packet.relationship_translation),
        "failure_modes": _norm(packet.failure_mode_translation),
    }


def _functional_departments(packet: Any) -> list[dict[str, Any]]:
    deps = packet.semantic_ir.functional_departments
    if deps:
        return [
            {
                "department": str(d.get("department", "PROCESSOR")).upper(),
                "source_manifestation": d.get("source_manifestation"),
                "target_manifestation": d.get("target_manifestation"),
                "status": str(d.get("status", "PRESENT")).upper(),
                "confidence": float(d.get("confidence", 0.5)),
                "failure_modes": d.get("failure_modes", []),
            }
            for d in deps
            if isinstance(d, dict)
        ]
    return []


def _gate_record(
    applicable: bool,
    score: float | None,
    passed: bool | None,
    reason: str | None,
) -> dict[str, Any]:
    # An applicable pass must carry a reason or deterministic validation note.
    if applicable and passed and not reason:
        reason = "gate passed"
    return {
        "applicable": applicable,
        "passed": passed,
        "score": round(score, 4) if score is not None else None,
        "reason": reason,
        "evidence_ids": [],
    }


def _gates(packet: Any) -> dict[str, Any]:
    scores = packet.scores

    # Causal validity applicable when there are mappings or causal analysis.
    ca = packet.causal_analysis or {}
    causal_applicable = bool(packet.fractal_mappings) or bool(ca)
    causal_score = scores.get("causal_validity")
    causal_passed = (
        causal_score >= 0.40 if causal_score is not None else None
    ) if causal_applicable else None

    # Scale integrity
    ss = packet.scale_separation or {}
    scale_applicable = bool(ss.get("transforms") or ss.get("scale_transforms"))
    scale_score = scores.get("scale_integrity")
    scale_passed = (
        scale_score >= 0.40 if scale_score is not None else None
    ) if scale_applicable else None

    # Boundary integrity
    bc = packet.boundary_checks or {}
    boundary_applicable = bool(bc)
    boundary_score = scores.get("boundary_integrity")
    boundary_passed = (
        boundary_score >= 0.40 if boundary_score is not None else None
    ) if boundary_applicable else None

    # Measurement integrity
    mi = packet.measurement_integrity or {}
    measurement_applicable = bool(
        mi.get("paths") or mi.get("context_declared_modified") or mi.get("gate_status")
    )
    measurement_score = scores.get("measurement_integrity")
    measurement_passed = (
        measurement_score >= 0.40 if measurement_score is not None else None
    ) if measurement_applicable else None

    # Authority safety
    aps = packet.approval_scan or {}
    authority_applicable = bool(aps)
    authority_score = scores.get("authority_safety")
    authority_passed = (
        authority_score >= 0.40 if authority_score is not None else None
    ) if authority_applicable else None

    # Security safety
    rs = packet.risk_scan or {}
    security_applicable = bool(rs)
    security_score = scores.get("security_safety")
    security_passed = (
        security_score >= 0.40 if security_score is not None else None
    ) if security_applicable else None

    # Wave function coherence: only applicable in that mode or when explicitly probed.
    wfc = packet.wave_function_coherence or {}
    wave_applicable = (
        packet.mode == CompilerMode.WAVE_FUNCTION_COHERENCE
        or bool(wfc.get("state"))
    )
    wave_score = scores.get("wave_function_coherence")
    wave_passed = (
        wave_score >= 0.40 if wave_score is not None else None
    ) if wave_applicable else None

    # Substrate sovereignty
    from semantic_compiler.gates.substrate import detect_sovereignty_threat
    sovereignty = detect_sovereignty_threat(packet)
    substrate_applicable = True
    substrate_passed = sovereignty.get("sovereignty_intact", True)
    substrate_score = 1.0 if substrate_passed else 0.0

    # Corpus completeness: applicable when cosmological anchors or
    # framework-derived claims are present.
    from semantic_compiler.gates.corpus_completeness import CorpusCompletenessGate
    corpus_applicable = bool(packet.cosmological_anchors) or any(
        str(c.get("claim_type", "")).upper() in {"COSMOLOGICAL_CLAIM", "FRACTAL_ISOMORPHISM"}
        for c in packet.claim_types
    )
    corpus_gate = CorpusCompletenessGate(
        manifest={"current_context": {a.get("component", ""): {} for a in packet.cosmological_anchors}}
    )
    corpus_component = (
        packet.cosmological_anchors[0].get("component", "")
        if packet.cosmological_anchors else ""
    )
    corpus_result = corpus_gate.check(corpus_component, [corpus_component]) if corpus_applicable else None
    corpus_passed = corpus_result["passed"] if corpus_result else None
    corpus_score = 1.0 if corpus_passed else (0.0 if corpus_passed is False else None)
    corpus_reason = (
        corpus_result["state"] if corpus_result else "Not applicable unless cosmological or framework claim is present."
    )

    return {
        "causal_validity": _gate_record(
            causal_applicable, causal_score, causal_passed,
            None if causal_passed else ("causal gate not passed" if causal_applicable else None)
        ),
        "scale_integrity": _gate_record(
            scale_applicable, scale_score, scale_passed,
            None if scale_passed else ("scale gate not passed" if scale_applicable else None)
        ),
        "boundary_integrity": _gate_record(
            boundary_applicable, boundary_score, boundary_passed,
            None if boundary_passed else ("boundary gate not passed" if boundary_applicable else None)
        ),
        "measurement_integrity": _gate_record(
            measurement_applicable, measurement_score, measurement_passed,
            None if measurement_passed else ("measurement gate not passed" if measurement_applicable else None)
        ),
        "authority_safety": _gate_record(
            authority_applicable, authority_score, authority_passed,
            None if authority_passed else ("authority gate not passed" if authority_applicable else None)
        ),
        "security_safety": _gate_record(
            security_applicable, security_score, security_passed,
            None if security_passed else ("security gate not passed" if security_applicable else None)
        ),
        "wave_function_coherence": _gate_record(
            wave_applicable, wave_score, wave_passed,
            "Not applicable unless inner and outer states are both supplied."
            if not wave_applicable else None
        ),
        "substrate_sovereignty": _gate_record(
            substrate_applicable, substrate_score, substrate_passed,
            None if substrate_passed else "sovereignty threat detected"
        ),
        "corpus_completeness": _gate_record(
            corpus_applicable, corpus_score, corpus_passed,
            corpus_reason
        ),
    }


def _adversarial(packet: Any) -> dict[str, Any]:
    return {
        "contradictions": list(packet.contradictions),
        "category_errors": list(packet.category_errors),
        "hidden_variables": packet.hidden_variable_probe.get("candidates", []),
        "missing_organs": list(packet.missing_organs),
        "policy_overrides": list(packet.policy_overrides),
    }


def _v2_extensions(packet: Any) -> dict[str, Any]:
    wfc = packet.wave_function_coherence or {}
    state = wfc.get("state")
    if state is None:
        wave_state = "NOT_APPLICABLE"
    elif hasattr(state, "name"):
        wave_state = state.name
    else:
        wave_state = str(state).upper()

    return {
        "cosmological_anchors": list(packet.cosmological_anchors),
        "reality_orientation": packet.reality_orientation or None,
        "wave_function_state": wave_state,
        "subconscious_layers": packet.semantic_ir.subconscious_layers,
        "trauma_context": packet.semantic_ir.trauma_context,
        "binary_resolution": None,
    }


def _preserved_invariants(mapping: dict[str, Any]) -> list[dict[str, Any]]:
    preserved = mapping.get("preserved_invariants", [])
    out: list[dict[str, Any]] = []
    for i, inv in enumerate(preserved):
        if isinstance(inv, dict):
            out.append({
                "invariant_id": inv.get("invariant_id", f"inv-{i}"),
                "name": inv.get("name", "preserved function"),
                "source_expression": inv.get("source_expression", str(inv)),
                "target_expression": inv.get("target_expression", str(inv)),
                "importance": float(inv.get("importance", 0.5)),
                "preservation_score": float(inv.get("preservation_score", 0.5)),
                "evidence_ids": inv.get("evidence_ids", []),
            })
        else:
            out.append({
                "invariant_id": f"inv-{i}",
                "name": str(inv),
                "source_expression": str(inv),
                "target_expression": str(inv),
                "importance": 0.5,
                "preservation_score": 0.5,
                "evidence_ids": [],
            })
    return out


def _scale_transform(mapping: dict[str, Any]) -> dict[str, Any]:
    st = mapping.get("scale_transform", {})
    if isinstance(st, dict):
        return {
            "source_scale": _scale_name(st.get("source_scale")) or "COMPONENT",
            "target_scale": _scale_name(st.get("target_scale")) or "ORGANIZATIONAL",
            "aggregation_rule": st.get("aggregation_rule"),
            "decomposition_rule": st.get("decomposition_rule"),
            "changed_variables": st.get("changed_variables", []),
            "information_lost": st.get("information_lost"),
            "new_failure_modes": st.get("new_failure_modes", []),
            "authority_change": st.get("authority_change", "none"),
            "confidence": float(st.get("confidence", 0.0)),
        }
    return {
        "source_scale": "COMPONENT",
        "target_scale": "ORGANIZATIONAL",
        "aggregation_rule": None,
        "decomposition_rule": None,
        "changed_variables": [],
        "information_lost": None,
        "new_failure_modes": [],
        "authority_change": "none",
        "confidence": 0.0,
    }


def _residual_mismatches(packet: Any, mapping: dict[str, Any]) -> list[dict[str, Any]]:
    residuals = mapping.get("residuals", [])
    if not residuals and packet.residual_mismatches:
        residuals = packet.residual_mismatches

    out: list[dict[str, Any]] = []
    for i, r in enumerate(residuals):
        if isinstance(r, dict):
            out.append({
                "residual_id": r.get("residual_id", f"res-{i}"),
                "description": r.get("description", str(r)),
                "severity": str(r.get("severity", "MEDIUM")).upper(),
                "effect_on_claim": r.get("effect_on_claim", "limits generality"),
                "repair_or_guardrail": r.get("repair_or_guardrail"),
            })
        else:
            out.append({
                "residual_id": f"res-{i}",
                "description": str(r),
                "severity": "MEDIUM",
                "effect_on_claim": "limits generality",
                "repair_or_guardrail": None,
            })
    return out


def _negative_tests(mapping: dict[str, Any]) -> list[dict[str, Any]]:
    tests = mapping.get("negative_tests", [])
    out: list[dict[str, Any]] = []
    for i, t in enumerate(tests):
        if isinstance(t, dict):
            out.append({
                "test_id": t.get("test_id", f"nt-{i}"),
                "attack": t.get("attack", "unspecified attack"),
                "source_only_features": t.get("source_only_features", []),
                "target_only_features": t.get("target_only_features", []),
                "counterexample": t.get("counterexample"),
                "result": str(t.get("result", "UNTESTED")).upper(),
                "impact": t.get("impact", "unknown"),
            })
        else:
            out.append({
                "test_id": f"nt-{i}",
                "attack": str(t),
                "source_only_features": [],
                "target_only_features": [],
                "counterexample": None,
                "result": "UNTESTED",
                "impact": "unknown",
            })
    return out


def _assess(value: float | None) -> float | None:
    """Return the value if it was actually assessed, otherwise None."""
    if value is None:
        return None
    return float(value)


def _mapping_scores(
    mapping: dict[str, Any],
    packet: Any,
    negative_tests: list[dict[str, Any]],
    preserved: list[dict[str, Any]],
    residuals: list[dict[str, Any]],
) -> dict[str, Any]:
    scores = mapping.get("scores", {})
    packet_scores = packet.scores

    # Dimensions that were actually supplied by extraction/analysis.
    structural_fit = _assess(scores.get("structural_fit", packet_scores.get("structural_fit")))
    # Functional and relationship fits are derived from extraction quality, not
    # from default packet scores, so empty vs. rich analogies separate.
    functional_fit = _assess(scores.get("functional_fit"))
    relationship_fit = _assess(scores.get("relationship_fit"))

    mapping_class = _mapping_class_name(mapping.get("mapping_class"))
    relationship_count = len(packet.semantic_ir.relationships)
    flow_count = len(packet.structural_skeleton.get("flows", []))

    if relationship_fit is None:
        if _mapping_requires_relationships(mapping_class, packet):
            relationship_fit = 0.0 if relationship_count == 0 else min(1.0, 0.35 + 0.2 * relationship_count)
        elif relationship_count > 0:
            relationship_fit = min(1.0, 0.5 + 0.15 * relationship_count)

    if functional_fit is None:
        if flow_count or relationship_count:
            functional_fit = min(1.0, 0.35 + 0.15 * max(flow_count, relationship_count))
        else:
            functional_fit = 0.2

    if preserved:
        preserved_cov = sum(p.get("preservation_score", 0.0) for p in preserved) / max(len(preserved), 1)
    else:
        preserved_cov = None

    scale_validity = _assess(scores.get("scale_transform_validity", packet_scores.get("scale_integrity")))

    tested = [t for t in negative_tests if t.get("result") != "UNTESTED"]
    if tested:
        negative_strength = 1.0 if all(
            t.get("result") in ("SURVIVED", "WEAKENED") for t in tested
        ) else 0.0
    elif residuals:
        negative_strength = 0.5
    else:
        negative_strength = 0.0

    residual_disclosure = min(1.0, len(residuals) * 0.25) if residuals else None
    evidence_support = _assess(packet_scores.get("evidence_quality"))
    alt_pressure = _assess(scores.get("alternative_explanation_pressure"))
    overclaim_control = 0.7
    if mapping.get("identity_claim_allowed") is False:
        overclaim_control = 1.0
    elif mapping.get("identity_claim_allowed") is True:
        overclaim_control = 0.5

    dimension_values: dict[str, float | None] = {
        "structural_fit": structural_fit,
        "functional_fit": functional_fit,
        "relationship_fit": relationship_fit,
        "preserved_invariant_coverage": preserved_cov,
        "scale_transform_validity": scale_validity,
        "negative_test_strength": negative_strength,
        "residual_disclosure": residual_disclosure,
        "evidence_support": evidence_support,
        "alternative_explanation_pressure": alt_pressure,
        "overclaim_control": overclaim_control,
    }

    core_assessed = {
        k: v for k, v in dimension_values.items()
        if k in _CORE_ANALYSIS_DIMENSIONS and v is not None
    }

    def _fmt(value: float | None) -> float | None:
        return round(value, 4) if value is not None else None

    # Invariant: a mapping that was not actually evaluated cannot receive a
    # positive quality score or a VALID verdict.
    if not core_assessed:
        return {
            "structural_fit": _fmt(structural_fit),
            "functional_fit": _fmt(functional_fit),
            "relationship_fit": _fmt(relationship_fit),
            "preserved_invariant_coverage": _fmt(preserved_cov),
            "scale_transform_validity": _fmt(scale_validity),
            "negative_test_strength": _fmt(negative_strength),
            "residual_disclosure": _fmt(residual_disclosure),
            "evidence_support": _fmt(evidence_support),
            "alternative_explanation_pressure": _fmt(alt_pressure),
            "overclaim_control": _fmt(overclaim_control),
            "mapping_quality": None,
            "assessment_coverage": 0.0,
            "soft_composite": 0.0,
            "hard_gate_multiplier": 1,
            "final_isomorphism_quality": 0.0,
            "confidence": 0.0,
        }

    mapping_quality = _geometric_mean(core_assessed, _ISO_QUALITY_WEIGHTS)

    # Penalize soft quality when a non-reject semantic error (e.g., rhetorical
    # personification) is present; hard-reject errors drive quality to zero.
    semantic_error_multiplier = 1.0
    if packet.semantic_error_class:
        if packet.semantic_error_class in {"RHETORICAL_PERSONIFICATION", "AMBIGUOUS_FIGURATIVE_LANGUAGE"}:
            semantic_error_multiplier = 0.85
        else:
            semantic_error_multiplier = 0.0

    mapping_quality *= semantic_error_multiplier
    assessment_coverage = len(core_assessed) / len(_CORE_ANALYSIS_DIMENSIONS)

    hard_multiplier = 1
    if negative_tests and any(t.get("result") == "FAILED" for t in negative_tests):
        hard_multiplier = 0
    if mapping.get("mapping_class") == "HEURISTIC_METAPHOR" and not tested:
        hard_multiplier = 0

    final_isomorphism_quality = mapping_quality * hard_multiplier
    confidence = final_isomorphism_quality * assessment_coverage

    return {
        "structural_fit": _fmt(structural_fit),
        "functional_fit": _fmt(functional_fit),
        "relationship_fit": _fmt(relationship_fit),
        "preserved_invariant_coverage": _fmt(preserved_cov),
        "scale_transform_validity": _fmt(scale_validity),
        "negative_test_strength": _fmt(negative_strength),
        "residual_disclosure": _fmt(residual_disclosure),
        "evidence_support": _fmt(evidence_support),
        "alternative_explanation_pressure": _fmt(alt_pressure),
        "overclaim_control": _fmt(overclaim_control),
        "mapping_quality": round(mapping_quality, 4),
        "assessment_coverage": round(assessment_coverage, 4),
        "soft_composite": round(mapping_quality, 4),
        "hard_gate_multiplier": hard_multiplier,
        "final_isomorphism_quality": round(final_isomorphism_quality, 4),
        "confidence": round(confidence, 4),
    }


def _mapping_verdict(mapping_scores: dict[str, Any], mapping_status: str = "ASSESSED") -> str:
    if mapping_status == "UNASSESSED":
        return "UNRESOLVED"
    quality = mapping_scores["final_isomorphism_quality"]
    if quality >= 0.85:
        return "STRONG_STRUCTURAL_MATCH"
    if quality >= 0.60:
        return "STRUCTURALLY_PLAUSIBLE"
    if quality >= 0.35:
        return "HEURISTIC"
    return "INVALID"


def _build_mappings(packet: Any) -> list[dict[str, Any]]:
    mappings: list[dict[str, Any]] = []
    fm = packet.fractal_mappings or []
    ca = packet.causal_analysis or {}

    # If no fractal mappings, synthesize one from causal analysis and skeleton.
    if not fm:
        source_frame = packet.source_frames[0] if packet.source_frames else "unknown"
        target = packet.selected_target or "unknown"
        mapping_class = _mapping_class_name(ca.get("mapping_class"))
        negative_tests = []
        preserved = []
        residuals = _residual_mismatches(packet, {})
        scores = _mapping_scores(
            {"mapping_class": mapping_class, "identity_claim_allowed": False},
            packet,
            negative_tests,
            preserved,
            residuals,
        )
        mapping_status = "ASSESSED" if scores.get("mapping_quality") is not None else "UNASSESSED"
        ranking_score = scores.get("final_isomorphism_quality", 0.0)
        reason_codes = (
            ["NO_ANALYSIS_DIMENSIONS_POPULATED"]
            if mapping_status == "UNASSESSED" else []
        )
        mappings.append({
            "mapping_id": "MAP:000001",
            "mapping_status": mapping_status,
            "source": {
                "phenomenon": source_frame,
                "frame": source_frame,
                "scale": "COMPONENT",
                "substrate_type": "unknown",
            },
            "target": {
                "phenomenon": target,
                "frame": target,
                "scale": "ORGANIZATIONAL",
                "substrate_type": "unknown",
            },
            "mapping_class": mapping_class,
            "identity_claim_allowed": mapping_class == "MATERIAL_IDENTITY",
            "preserved_invariants": preserved,
            "scale_transform": _scale_transform({}),
            "residual_mismatches": residuals,
            "negative_tests": negative_tests,
            "alternative_mappings": [],
            "scores": scores,
            "verdict": _mapping_verdict(scores, mapping_status),
            "ranking_score": ranking_score,
            "reason_codes": reason_codes,
            "training_ready": _mapping_training_ready(mapping_status, mapping_class, packet),
            "guardrails": [],
        })
        return mappings

    for i, m in enumerate(fm):
        if not isinstance(m, dict):
            continue
        source = m.get("source", m.get("source_implementation", "unknown"))
        target = m.get("target", m.get("target_implementation", "unknown"))
        source_frame = m.get("source_frame", packet.source_frames[0] if packet.source_frames else "unknown")
        target_frame = m.get("target_frame", packet.selected_target or "unknown")
        mapping_class = _mapping_class_name(m.get("mapping_class"))

        preserved = _preserved_invariants(m)
        residuals = _residual_mismatches(packet, m)
        negative_tests = _negative_tests(m)

        scores = _mapping_scores(
            {
                **m,
                "mapping_class": mapping_class,
                "identity_claim_allowed": mapping_class == "MATERIAL_IDENTITY",
            },
            packet,
            negative_tests,
            preserved,
            residuals,
        )
        mapping_status = "ASSESSED" if scores.get("mapping_quality") is not None else "UNASSESSED"
        ranking_score = scores.get("final_isomorphism_quality", 0.0)
        reason_codes = (
            ["NO_ANALYSIS_DIMENSIONS_POPULATED"]
            if mapping_status == "UNASSESSED" else []
        )

        mappings.append({
            "mapping_id": f"MAP:{i+1:06d}",
            "mapping_status": mapping_status,
            "source": {
                "phenomenon": source,
                "frame": source_frame,
                "scale": _scale_name(m.get("source_scale")) or "COMPONENT",
                "substrate_type": m.get("source_substrate", "unknown"),
            },
            "target": {
                "phenomenon": target,
                "frame": target_frame,
                "scale": _scale_name(m.get("target_scale")) or "ORGANIZATIONAL",
                "substrate_type": m.get("target_substrate", "unknown"),
            },
            "mapping_class": mapping_class,
            "identity_claim_allowed": mapping_class == "MATERIAL_IDENTITY",
            "preserved_invariants": preserved,
            "scale_transform": _scale_transform(m),
            "residual_mismatches": residuals,
            "negative_tests": negative_tests,
            "alternative_mappings": [],
            "scores": scores,
            "verdict": _mapping_verdict(scores, mapping_status),
            "ranking_score": ranking_score,
            "reason_codes": reason_codes,
            "training_ready": _mapping_training_ready(mapping_status, mapping_class, packet),
            "guardrails": m.get("guardrails", []),
        })

    return mappings


def _isomorphism_analysis(packet: Any) -> dict[str, Any]:
    mappings = _build_mappings(packet)
    best = max(
        mappings,
        key=lambda m: m["scores"]["final_isomorphism_quality"],
    ) if mappings else None

    unresolved = [
        r["description"]
        for m in mappings
        for r in m["residual_mismatches"]
        if r.get("severity") in ("HIGH", "FATAL")
    ]

    aggregate_quality = (
        sum(m["scores"]["final_isomorphism_quality"] for m in mappings) / len(mappings)
        if mappings else 0.0
    )
    mapping_qualities = [
        m["scores"]["mapping_quality"] for m in mappings
        if m["scores"].get("mapping_quality") is not None
    ]
    aggregate_mapping_quality = (
        sum(mapping_qualities) / len(mapping_qualities)
        if mapping_qualities else 0.0
    )
    aggregate_assessment_coverage = (
        sum(m["scores"]["assessment_coverage"] for m in mappings) / len(mappings)
        if mappings else 0.0
    )
    unassessed_count = sum(
        1 for m in mappings if m.get("mapping_status") == "UNASSESSED"
    )

    return {
        "mappings": mappings,
        "aggregate": {
            "best_mapping_id": best["mapping_id"] if best else None,
            "mapping_count": len(mappings),
            "unassessed_mapping_count": unassessed_count,
            "aggregate_isomorphism_quality": round(aggregate_quality, 4),
            "aggregate_mapping_quality": round(aggregate_mapping_quality, 4),
            "aggregate_assessment_coverage": round(aggregate_assessment_coverage, 4),
            "cross_mapping_consistency": 1.0 if len(mappings) <= 1 else 0.7,
            "unresolved_residuals": unresolved,
        },
    }


def _compiler_scores(packet: Any) -> dict[str, float]:
    """Pass through the compiler's soft scores, rounded."""
    return {k: round(float(v), 4) for k, v in packet.scores.items() if isinstance(v, (int, float))}


def _quality_hard_gates(gates: dict[str, Any]) -> dict[str, Any]:
    """Export gate records for the quality.hard_gates block."""
    return {
        name: {
            "applicable": rec["applicable"],
            "passed": rec["passed"],
            "score": rec["score"],
            "reason": rec["reason"],
        }
        for name, rec in gates.items()
    }


def _dataset_value(packet: Any) -> dict[str, Any]:
    scores = packet.scores
    claim_count = len(packet.claim_types)
    mapping_count = len(packet.fractal_mappings)
    has_correction = any(
        isinstance(c, dict) and (c.get("repair") or c.get("resolved"))
        for c in packet.contradictions
    )

    novelty = 0.5
    teaching_value = min(1.0, 0.3 + claim_count * 0.1 + mapping_count * 0.1)
    contrastive_value = 0.6 if has_correction else 0.3
    repair_value = 0.7 if has_correction else 0.2
    generalization_value = scores.get("fractal_fit", 0.5)
    format_validity = 1.0

    sub_scores = {
        "novelty": novelty,
        "teaching_value": teaching_value,
        "contrastive_value": contrastive_value,
        "repair_value": repair_value,
        "generalization_value": generalization_value,
        "format_validity": format_validity,
    }
    score = _geometric_mean(sub_scores, {k: 1.0 for k in sub_scores})

    return {
        "score": round(score, 4),
        **{k: round(v, 4) for k, v in sub_scores.items()},
    }


def _tier_reasons(packet: Any, tier: DatasetTier) -> list[str]:
    reasons: list[str] = []
    if tier == DatasetTier.BRONZE:
        reasons.append("Raw or partially compiled sample.")
    if tier == DatasetTier.SILVER:
        reasons.append("Schema-valid and compiler complete.")
    if tier in (DatasetTier.GOLD, DatasetTier.DIAMOND, DatasetTier.DIAMOND_PLUS):
        reasons.append("Residuals present.")
    if tier in (DatasetTier.DIAMOND, DatasetTier.DIAMOND_PLUS):
        reasons.append("Diamond requires Logos review and contrastive payload.")
    if packet.privacy_sensitivity in (PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL):
        reasons.append("Privacy-sensitive; redacted derivative only.")
    return reasons or ["Default tier classification."]


def _semantic_quality_tier(packet: Any) -> str:
    """Tier the compiled semantic record independently of dataset utility."""
    decision = packet.decision
    if decision in (Decision.REJECT, Decision.QUARANTINE):
        return "REJECTED"
    if decision == Decision.NEEDS_REVISION:
        return "NEEDS_REVISION"
    if decision == Decision.COMPILED_WITH_GUARDRAILS:
        return "COMPILED_WITH_GUARDRAILS"
    if decision == Decision.COMPILED:
        return "COMPILED"
    if decision == Decision.COMPILED_SUPERVISED_ONLY:
        return "COMPILED_SUPERVISED_ONLY"
    return "PENDING"


def _mapping_requires_relationships(mapping_class: str, packet: Any) -> bool:
    """
    Analogical, metaphorical, and causal mappings require extracted
    relationships before they can become training targets.

    Material-identity claims (e.g., "X is Y") may be ready without explicit
    relationship edges; every other cross-domain mapping needs structural
    edges to supervise a model.
    """
    if mapping_class == "MATERIAL_IDENTITY":
        return False
    if mapping_class in {"STRUCTURAL_ANALOGY", "HEURISTIC_METAPHOR", "CAUSAL_MAPPING"}:
        return True
    claim_type_names = {str(c.get("claim_type", "")).upper() for c in packet.claim_types}
    if claim_type_names & {"ANALOGY", "METAPHOR", "STRUCTURAL_MAPPING", "COUNTERFACTUAL"}:
        return True
    return False


def _mapping_training_ready(mapping_status: str, mapping_class: str, packet: Any) -> bool:
    """A single mapping is training-ready only when assessed and supported."""
    if mapping_status != "ASSESSED":
        return False
    if packet.decision != Decision.COMPILED:
        return False
    if _mapping_requires_relationships(mapping_class, packet) and not packet.semantic_ir.relationships:
        return False
    return True


def _training_ready(packet: Any) -> bool:
    """A sample is training-ready only after clean compilation."""
    if packet.privacy_sensitivity in (PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL):
        return False
    if packet.decision not in (
        Decision.COMPILED,
        Decision.COMPILED_WITH_GUARDRAILS,
        Decision.COMPILED_SUPERVISED_ONLY,
    ):
        return False

    # For analogical, figurative, or invalid inputs, require extracted
    # relationships.  A compiler cannot supervise what it did not extract.
    mapping_class = "STRUCTURAL_ANALOGY"
    if packet.fractal_mappings:
        mapping_class = _mapping_class_name(packet.fractal_mappings[0].get("mapping_class"))
    elif packet.causal_analysis:
        mapping_class = _mapping_class_name(packet.causal_analysis.get("mapping_class"))

    if _mapping_requires_relationships(mapping_class, packet) and not packet.semantic_ir.relationships:
        return False

    # A sample that explicitly describes an incomplete system (confirmed absent
    # organs/functions) is not a clean positive training target.
    if any(m.get("state") == "ABSENT_CONFIRMED" for m in packet.missing_organs):
        return False

    return True


def _build_quality(packet: Any, gates: dict[str, Any]) -> dict[str, Any]:
    iso_analysis = _isomorphism_analysis(packet)
    aggregate_quality = iso_analysis["aggregate"]["aggregate_isomorphism_quality"]
    iso_hard_passed = all(
        m["scores"]["hard_gate_multiplier"] == 1 for m in iso_analysis["mappings"]
    )

    tier = _classify_tier(packet)
    dataset_value = _dataset_value(packet)

    return {
        "compiler_scores": _compiler_scores(packet),
        "hard_gates": _quality_hard_gates(gates),
        "isomorphism_quality": {
            "score": round(aggregate_quality, 4),
            "method": "weighted_geometric_mean_plus_applicable_hard_gates",
            "hard_gate_passed": iso_hard_passed,
            "confidence": round(aggregate_quality, 4),
            "explanation": (
                f"Aggregate isomorphism quality across {len(iso_analysis['mappings'])} mapping(s)."
            ),
        },
        "dataset_value": dataset_value,
        "semantic_quality_tier": _semantic_quality_tier(packet),
        "dataset_utility_tier": tier.name,
        "dataset_tier": tier.name,
        "training_ready": _training_ready(packet),
        "tier_reasons": _tier_reasons(packet, tier),
    }


def _derive_correction(packet: Any) -> str | None:
    """Return the corrected claim from the first resolved contradiction repair."""
    for contradiction in packet.contradictions:
        if isinstance(contradiction, dict):
            repair = contradiction.get("repair")
            if isinstance(repair, dict) and contradiction.get("resolved"):
                return repair.get("corrected_claim")
    return None


def _build_outputs(packet: Any) -> dict[str, Any]:
    return {
        "literal_translation": packet.literal_translation,
        "public_translation": packet.public_translation,
        "executive_translation": packet.executive_translation,
        "correction": _derive_correction(packet),
        "guardrails": [],
        "uncertainty_statement": "Unscored draft." if packet.decision is None else "Compilation complete.",
        "open_questions": list(packet.next_questions),
    }


def _build_training_payloads(packet: Any) -> dict[str, Any]:
    sft = packet.qwen_sft_output if packet.qwen_sft_output else None
    return {
        "sft": sft,
        "dpo": None,
        "classifier": None,
        "contrastive": None,
    }


def _build_decision(packet: Any) -> dict[str, Any]:
    return {
        "status": _as_name(packet.decision) or "NEEDS_REVISION",
        "route_to": list(packet.route_to),
        "next_questions": list(packet.next_questions),
        "compiler_errors": list(packet.compiler_errors),
        "compiler_warnings": list(packet.compiler_warnings),
    }


def _reviewer_block() -> dict[str, Any]:
    return {
        "status": "UNREVIEWED",
        "reviewer": None,
        "reviewed_at": None,
        "rubric": {
            "structural_fidelity": None,
            "evidence_discipline": None,
            "residual_honesty": None,
            "negative_test_quality": None,
            "correction_quality": None,
            "teaching_value": None,
            "cross_scale_generalization": None,
            "format_validity": None,
            "overall": None,
        },
        "verdict": "UNREVIEWED",
        "notes": None,
    }


def _build_review(packet: Any) -> dict[str, Any]:
    return {
        "logos": _reviewer_block(),
        "curtis": _reviewer_block(),
        "kestrel": _reviewer_block(),
        "consensus": {
            "status": "UNREVIEWED",
            "final_score": None,
            "notes": None,
        },
        "revision_history": list(packet.dataset_row.get("revision_history", []))
        if isinstance(packet.dataset_row, dict) else [],
    }


def _derive_dispositions(packet: Any) -> dict[str, str]:
    """
    Separate semantic decision from privacy, training, and export dispositions.

    Internal/local training is permitted by default unless the content is
    sensitive/critical or explicitly forbidden. External export is prohibited
    unless the content is public and explicitly approved.
    """
    sensitivity = packet.privacy_sensitivity
    external = str(packet.external_training_use).lower()

    if sensitivity in (PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL):
        training = "LOCAL_TRAINING_DENIED"
    elif external == "forbidden":
        training = "LOCAL_TRAINING_ALLOWED"
    else:
        training = "LOCAL_TRAINING_ALLOWED"

    if sensitivity == PrivacySensitivity.PUBLIC and external == "approved":
        export_disp = "ALLOWED"
    elif sensitivity in (PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL):
        export_disp = "PROHIBITED"
    elif external == "redacted_only":
        export_disp = "REDACTED_ONLY"
    else:
        export_disp = "PROHIBITED"

    return {
        "training_disposition": training,
        "export_disposition": export_disp,
    }


def _build_privacy(packet: Any) -> dict[str, Any]:
    redactions: list[str] = []
    if packet.privacy_sensitivity in (PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL):
        redactions.append("raw_input")

    return {
        "sensitivity": _to_sensitivity_name(packet.privacy_sensitivity),
        "external_training_use": _to_training_external_use(packet.external_training_use),
        **_derive_dispositions(packet),
        "redactions_required": redactions,
        "contains_personal_data": packet.privacy_sensitivity == PrivacySensitivity.CRITICAL,
        "contains_confidential_ip": packet.privacy_sensitivity in (
            PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL
        ),
    }


def _build_audit(packet: Any, schema_valid: bool) -> dict[str, Any]:
    return {
        "audit_id": f"AUDIT:{_sample_id(packet)}",
        "compiled_at": packet.compilation_end or _now_iso(),
        "input_hash": packet.source_context.source_hash or packet.compute_input_hash(),
        "schema_valid": schema_valid,
        "immutable_source_preserved": bool(packet.raw_input),
        "compiler_commit": None,
        "generator_model": None,
        "validator_versions": {
            "json_schema": "2020-12",
            "logos_sample_schema": SCHEMA_VERSION,
            "semantic_compiler": packet.version,
        },
        "reproducibility_notes": "Fill after compilation.",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_dataset_row(packet: Any) -> dict[str, Any]:
    """
    Build a canonical Logos Semantic Training Sample V2.1 row.

    The row is schema-aligned and includes every compiler output that is
    safe to serialize, separated into provenance, input, compilation,
    isomorphism analysis, quality, outputs, payloads, decision, review,
    privacy, and audit envelopes.
    """
    gates = _gates(packet)

    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "sample_id": _sample_id(packet),
        "sample_kind": _derive_sample_kind(packet),
        "status": _derive_status(packet),
        "training_targets": ["SFT"],
        "provenance": _build_provenance(packet),
        "input": _build_input(packet),
        "semantic_compilation": {
            "compiler_version": packet.version,
            "extractor_version": EXTRACTOR_VERSION,
            "mode": _as_name(packet.mode) or "AUTO",
            "active_submodes": [_as_name(m) for m in packet.active_submodes],
            "source_frames": list(packet.source_frames),
            "candidate_targets": list(packet.target_systems),
            "target_resolution": _target_resolution(packet),
            "semantic_ir": _semantic_ir(packet),
            "structural_skeleton": _structural_skeleton(packet),
            "translations": _translations(packet),
            "functional_departments": _functional_departments(packet),
            "gates": gates,
            "adversarial": _adversarial(packet),
            "v2_extensions": _v2_extensions(packet),
        },
        "isomorphism_analysis": _isomorphism_analysis(packet),
        "quality": _build_quality(packet, gates),
        "outputs": _build_outputs(packet),
        "training_payloads": _build_training_payloads(packet),
        "decision": _build_decision(packet),
        "review": _build_review(packet),
        "privacy": _build_privacy(packet),
        "audit": _build_audit(packet, schema_valid=False),
    }

    # Self-validate and update audit flag.
    validation = validate_dataset_row(row)
    row["audit"]["schema_valid"] = validation["valid"]
    if not validation["valid"]:
        row["audit"]["reproducibility_notes"] = (
            "Schema validation failed: " + "; ".join(validation["errors"][:5])
        )

    return row


def _default_schema_path() -> Path:
    """Resolve the packaged V2.1 JSON Schema, with override hooks."""
    env_path = os.environ.get("LOGOS_V2_1_SCHEMA_PATH")
    if env_path:
        return Path(env_path)

    # Packaged schema, resolved relative to this module.
    packaged = Path(__file__).resolve().parent.parent / "schemas" / "logos_semantic_training_sample_v2_1.schema.json"
    if packaged.exists():
        return packaged

    # Legacy fallback for existing workstations.
    return Path("/home/shax/Downloads/logos_semantic_training_sample_v2_1.schema.json")


def validate_dataset_row(
    row: dict[str, Any],
    schema_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Validate a V2.1 dataset row against the Logos JSON Schema.

    If ``schema_path`` is omitted, the packaged schema is used (resolved
    relative to this module). Override with ``LOGOS_V2_1_SCHEMA_PATH`` env
    var or by passing an explicit path.

    Returns {"valid": bool, "errors": list[str]}.
    """
    from jsonschema import Draft202012Validator

    schema_path = Path(schema_path) if schema_path is not None else _default_schema_path()
    try:
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception as exc:
        return {"valid": False, "errors": [f"Could not load schema: {exc}"]}

    validator = Draft202012Validator(schema)
    errors = [str(e.message) for e in validator.iter_errors(row)]
    return {"valid": len(errors) == 0, "errors": errors}


def export_rows_to_jsonl(
    rows: list[dict[str, Any]],
    output_path: str | Path,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Export dataset rows to JSONL.

    If validate=True, every row is validated before writing and invalid rows
    are skipped with their errors recorded.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    error_log: list[dict[str, Any]] = []

    with output_path.open("w", encoding="utf-8") as f:
        for row in rows:
            if validate:
                validation = validate_dataset_row(row)
                if not validation["valid"]:
                    skipped += 1
                    error_log.append({
                        "sample_id": row.get("sample_id"),
                        "errors": validation["errors"],
                    })
                    continue
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            written += 1

    return {
        "output_path": str(output_path),
        "written": written,
        "skipped": skipped,
        "errors": error_log,
    }
