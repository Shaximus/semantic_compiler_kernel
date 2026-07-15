"""
Reflexion Semantic Compiler v2.0.0 — Decision Engine

Hard gates cannot be bypassed by generated prose.
The decision engine applies deterministic precedence rules.

Citation: v1.0 Spec Section 18 — Decision Engine
Citation: Diamond+++ — Regulated Reality Orientation Protocol
"""

from __future__ import annotations

from typing import Any

from semantic_compiler.core.types import Decision
from semantic_compiler.core.scoring import (
    collect_hard_gate_failures,
    AMBIGUITY_FAIL_THRESHOLD,
    STRUCTURAL_FIT_MIN,
)


def decide_packet(packet: Any) -> Decision:
    """
    Determine the compilation decision for a semantic packet.

    The decision engine applies precedence rules in strict order.
    No soft score can override a hard gate failure.

    Citation: v1.0 Spec Section 18 — Decision Engine

    Precedence (highest to lowest):
      1. QUARANTINE — security threat detected
      2. ESCALATE — requires founder authority
      3. ROUTE_FOR_APPROVAL — named approver
      4. REJECT — semantic error class with repair
      5. NEEDS_REVISION — hard gate failure, high ambiguity, unassessed mapping, contradictions
      6. COMPILED_WITH_GUARDRAILS — analogy-only mapping or rhetorical personification
      7. COMPILED_SUPERVISED_ONLY — supervised execution required
      8. COMPILED — full compilation success
    """
    scores = packet.scores

    # 1. Quarantine — security threat
    if packet.risk_scan.get("quarantine_required"):
        return Decision.QUARANTINE

    # 2. Escalate — founder authority required
    if packet.approval_scan.get("requires_founder_authority"):
        return Decision.ESCALATE

    # 3. Route for approval — named approver required
    if packet.approval_scan.get("requires_named_approver"):
        return Decision.ROUTE_FOR_APPROVAL

    # 4. Semantic error classes that reject the literal claim but carry a repair.
    error_class = getattr(packet, "semantic_error_class", None)
    if error_class in {
        "ANTHROPOMORPHIC_CAUSATION",
        "PHYSICAL_CATEGORY_ERROR",
        "FALSE_MECHANISM",
        "UNSUPPORTED_CAUSAL_TRANSFER",
        "IDENTITY_ANALOGY_CONFUSION",
    }:
        packet.compiler_warnings.append(f"SEMANTIC_ERROR: {error_class}")
        return Decision.REJECT

    # 5a. Hard gate failures — CANNOT be overridden
    gate_failures = collect_hard_gate_failures(scores)
    if gate_failures:
        packet.compiler_errors.extend([
            f"HARD GATE FAILURE: {f.reason}" for f in gate_failures
        ])
        return Decision.NEEDS_REVISION

    # 5b. High ambiguity
    if scores.get("ambiguity", 0.0) >= AMBIGUITY_FAIL_THRESHOLD:
        return Decision.NEEDS_REVISION

    # 5c. Unresolved contradictions
    if _has_unresolved_contradictions(packet):
        return Decision.NEEDS_REVISION

    # 5d. Low structural fit
    if scores.get("structural_fit", 0.0) < STRUCTURAL_FIT_MIN:
        return Decision.NEEDS_REVISION

    # 5e. Unassessed mapping — no meaningful analysis dimensions were populated.
    if _has_unassessed_mapping(packet):
        packet.compiler_warnings.append("MAPPING_UNASSESSED: no core analysis dimensions populated")
        return Decision.NEEDS_REVISION

    # 6b. Rhetorical personification or ambiguous figurative language requires guardrails/clarification.
    if error_class == "RHETORICAL_PERSONIFICATION":
        return Decision.COMPILED_WITH_GUARDRAILS
    if error_class in {"AMBIGUOUS_FIGURATIVE_LANGUAGE", "INSUFFICIENT_CONTEXT"}:
        return Decision.NEEDS_REVISION

    # 6c. An analogy or metaphor that names two domains but extracts no
    # structural relationship and no preserved invariant is too underspecified
    # to compile. It must be revised with a concrete mapping.
    if _is_underspecified_analogy(packet):
        packet.compiler_warnings.append("UNDERSPECIFIED_ANALOGY: no extracted relationship or invariant")
        return Decision.NEEDS_REVISION

    # 7. Analogy-only mapping with extracted structure — guardrails required
    if packet.causal_analysis.get("analogy_only"):
        return Decision.COMPILED_WITH_GUARDRAILS

    # 8. Supervised only — approval scan says so
    if packet.approval_scan.get("supervised_only"):
        return Decision.COMPILED_SUPERVISED_ONLY

    # 9. Full success
    return Decision.COMPILED


def _is_underspecified_analogy(packet: Any) -> bool:
    """
    Return True if the input is an analogy/metaphor with no extracted
    relationships and no explicitly preserved invariants.

    Examples:
        "The market is a living organism."
        "The organization is a ship."
    """
    if packet.semantic_ir.relationships:
        return False

    claim_types = {str(c.get("claim_type", "")).upper() for c in packet.claim_types}
    if claim_types & {"ANALOGY", "METAPHOR", "STRUCTURAL_MAPPING"}:
        preserved = any(
            m.get("preserved_invariants")
            for m in packet.fractal_mappings
            if isinstance(m, dict)
        )
        return not preserved

    # A sentence that mentions two or more source frames but extracts no
    # structural relationship is an underspecified cross-domain claim.
    frames = {f.rstrip("?").lower() for f in packet.source_frames if f}
    return len(frames) >= 2


def _has_unassessed_mapping(packet: Any) -> bool:
    """Return True if the packet's best mapping is unassessed."""
    from semantic_compiler.core.dataset import _isomorphism_analysis
    iso = _isomorphism_analysis(packet)
    mappings = iso.get("mappings", [])
    if not mappings:
        return True
    best = max(
        mappings,
        key=lambda m: m["scores"].get("final_isomorphism_quality", 0.0),
    )
    return best.get("mapping_status") == "UNASSESSED"


def _has_unresolved_contradictions(packet: Any) -> bool:
    """Check if the packet has contradictions without repairs."""
    for contradiction in packet.contradictions:
        if isinstance(contradiction, dict):
            if not contradiction.get("repair") and not contradiction.get("resolved"):
                return True
    return False


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

# Citation: v1.0 Spec Section 20 — Routing
ROUTING_TABLE: dict[str, list[str]] = {
    "unknown_binary": ["Aegis", "Argus"],
    "suspicious_artifact": ["Aegis", "Argus"],
    "approval_dispute": ["Arbiter", "Curtis"],
    "authority_dispute": ["Arbiter", "Curtis"],
    "cross_plane_ambiguity": ["Dragon"],
    "semantic_doctrine": ["Logos"],
    "dataset": ["Logos"],
    "continuity": ["Scribe"],
    "state_delta": ["Scribe"],
    "mailbox": ["Courier"],
    "transport": ["Courier"],
    "coordination": ["Whis"],
    "dependencies": ["Whis"],
    "roles": ["Hestia"],
    "staffing": ["Hestia"],
    "ownership": ["Hestia"],
    "runtime": ["Hephaestus"],
    "model": ["Hephaestus"],
    "product": ["Bellwether"],
    "revenue": ["Bellwether"],
    "external_intelligence": ["Mercator"],
    "loose_wires": ["Goku"],
    "executive_conflict": ["Kestrel", "Curtis"],
    # v2.0 additions
    "reality_orientation": ["Dragon", "Arbiter"],
    "cosmological_mapping": ["Logos", "Dragon"],
    "fractal_analysis": ["Logos"],
}


def route_packet(packet: Any) -> list[str]:
    """
    Determine routing destinations for a compiled packet.
    Citation: v1.0 Spec Section 20 — Routing
    """
    routes: list[str] = []

    # Check risk scan routing
    rs = packet.risk_scan
    if rs.get("quarantine_required"):
        routes.extend(ROUTING_TABLE.get("suspicious_artifact", []))
    if rs.get("security_concern"):
        routes.extend(ROUTING_TABLE.get("unknown_binary", []))

    # Check approval scan routing
    aps = packet.approval_scan
    if aps.get("requires_founder_authority"):
        routes.extend(ROUTING_TABLE.get("authority_dispute", []))
    if aps.get("requires_named_approver"):
        routes.extend(ROUTING_TABLE.get("approval_dispute", []))

    # Check missing organs routing
    for organ in packet.missing_organs:
        organ_type = organ.get("type", "") if isinstance(organ, dict) else str(organ)
        if "communication" in organ_type.lower():
            routes.extend(ROUTING_TABLE.get("mailbox", []))
        if "security" in organ_type.lower():
            routes.extend(ROUTING_TABLE.get("suspicious_artifact", []))
        if "ownership" in organ_type.lower():
            routes.extend(ROUTING_TABLE.get("ownership", []))

    # Mode-based routing
    if packet.mode:
        from semantic_compiler.core.types import CompilerMode
        if packet.mode == CompilerMode.DATASET_REFINERY:
            routes.extend(ROUTING_TABLE.get("dataset", []))
        if packet.mode == CompilerMode.REGULATED_REALITY_ORIENTATION:
            routes.extend(ROUTING_TABLE.get("reality_orientation", []))
        if packet.mode == CompilerMode.COSMOLOGICAL_MAPPING:
            routes.extend(ROUTING_TABLE.get("cosmological_mapping", []))

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_routes: list[str] = []
    for r in routes:
        if r not in seen:
            seen.add(r)
            unique_routes.append(r)

    return unique_routes


def build_routing_packet(packet: Any) -> dict[str, Any]:
    """
    Construct the routing packet that Post Office packages and Courier delivers.
    Citation: v1.0 Spec Section 20 — Routing
    """
    return {
        "packet_id": packet.packet_id,
        "decision": packet.decision.name if packet.decision else "PENDING",
        "routes": route_packet(packet),
        "priority": _compute_priority(packet),
        "copy_only": True,  # Courier delivers copy-only
        "requires_ledger_confirmation": True,
    }


def _compute_priority(packet: Any) -> str:
    """Compute routing priority based on decision and risk."""
    if packet.decision in (Decision.QUARANTINE, Decision.ESCALATE):
        return "critical"
    if packet.decision == Decision.ROUTE_FOR_APPROVAL:
        return "high"
    if packet.decision == Decision.NEEDS_REVISION:
        return "medium"
    return "normal"
