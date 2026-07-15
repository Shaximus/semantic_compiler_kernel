"""
Reflexion Semantic Compiler v2.0.0 — Immutable Audit Records

Every compilation produces an immutable audit record that captures
the full provenance chain: what was compiled, how it was scored,
what decision was made, and what gates passed or failed.

Citation: v1.0 Spec Section 27 — Production Readiness Gates
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_audit_record(packet: Any) -> dict[str, Any]:
    """
    Build an immutable audit record for a compiled packet.

    Repeated runs must be auditable and substantially reproducible.
    Citation: v1.0 Spec Section 27, Gate 12
    """
    return {
        "audit_id": f"audit-{packet.packet_id}",
        "packet_id": packet.packet_id,
        "compiler_version": packet.version,
        "compilation_start": packet.compilation_start,
        "compilation_end": packet.compilation_end,
        "mode": packet.mode.name if packet.mode else None,
        "active_submodes": [m.name for m in packet.active_submodes],
        "input_hash": packet.source_context.source_hash,
        "source_type": packet.source_context.source_type,
        "source_origin": packet.source_context.origin,
        "claim_count": len(packet.claim_types),
        "evidence_count": len(packet.evidence_inventory),
        "constraint_count": len(packet.declared_constraints),
        "unknown_count": len(packet.unknowns),
        "contradiction_count": len(packet.contradictions),
        "category_error_count": len(packet.category_errors),
        "negative_test_count": len(packet.negative_isomorphism_tests),
        "missing_organ_count": len(packet.missing_organs),
        "residual_count": len(packet.residual_mismatches),
        "scores": dict(packet.scores),
        "decision": packet.decision.name if packet.decision else None,
        "routes": packet.route_to,
        "compiler_errors": list(packet.compiler_errors),
        "compiler_warnings": list(packet.compiler_warnings),
        "privacy_sensitivity": packet.privacy_sensitivity.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "immutable": True,
    }



