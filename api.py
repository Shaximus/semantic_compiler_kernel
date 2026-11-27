"""Compact, JSON-ready public facade for hosted MCP / HTTP and mobile SDKs.

``compile_semantic_packet`` remains the canonical compile entry point and still
returns a full ``SemanticPacket``. This module adds:

- ``summary_v1(packet)`` — a stable, compact dict for tool results and
  on-device bridges. Raw input, normalized input, and ``forward_text`` are
  omitted unless explicitly opted in. ``unknowns``, ``next_questions``, and
  ``compiler_warnings`` may still carry input excerpts of up to 200 characters.
- ``compile_json(text, ...)`` — compile then return that summary.

This module is not imported by ``semantic_compiler.__init__``, so
``import semantic_compiler`` is unchanged.
"""

from __future__ import annotations

from typing import Any, Optional

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.core.pipeline import compile_semantic_packet

SUMMARY_SCHEMA = "summary_v1"
_MAX_CANDIDATES = 5
_MAX_LIST_ITEMS = 5
_MAX_TEXT = 200

# Allowlist is exactly the keys that producers put on packet.contradictions
# and packet.category_errors (no fallback).
# contradictions: type, resolved (gates/contradiction_repair.py). Nested
# claim_a/claim_b/repair are omitted. ruling/law do not flow into these lists
# (measurement-gate records live on packet.measurement_integrity).
# category_errors: error, detail (core/pipeline.py detect_category_errors).
# mapping is omitted: on category-error records it is the whole mapping dict;
# on negative-isomorphism tests it is a source→target string built from input.
_RECORD_KEYS = (
    "type",
    "resolved",
    "error",
)
_RECORD_TEXT_KEYS = ("detail",)


def _enum_name(value: Any) -> Optional[str]:
    if value is None:
        return None
    name = getattr(value, "name", None)
    return name if isinstance(name, str) else str(value)


def _truncate(value: Any) -> Any:
    if isinstance(value, str) and len(value) > _MAX_TEXT:
        return value[:_MAX_TEXT]
    return value


def _compact_records(items: list[Any] | None) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for item in list(items or [])[:_MAX_LIST_ITEMS]:
        if not isinstance(item, dict):
            compact.append({"value": _truncate(str(item))})
            continue
        row: dict[str, Any] = {}
        for key in _RECORD_KEYS:
            if key in item:
                row[key] = item[key]
        for key in _RECORD_TEXT_KEYS:
            if key in item:
                row[key] = _truncate(item[key])
                break
        compact.append(row)
    return compact


def _compact_candidates(items: list[Any] | None) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for item in list(items or [])[:_MAX_CANDIDATES]:
        if not isinstance(item, dict):
            continue
        compact.append(
            {
                "domain": item.get("domain"),
                "score": item.get("score"),
                "confidence": item.get("confidence"),
            }
        )
    return compact


def _compact_testimony(gate: dict[str, Any] | None) -> Optional[dict[str, Any]]:
    if not gate:
        return None
    return {
        "is_testimony": gate.get("is_testimony"),
        "consistency": gate.get("consistency"),
        "isomorphism": gate.get("isomorphism"),
        "corroboration": gate.get("corroboration"),
        "composite_classification": gate.get("composite_classification"),
    }


def _risk_flags(scan: dict[str, Any] | None) -> dict[str, Any]:
    scan = scan or {}
    return {
        "quarantine_required": bool(scan.get("quarantine_required")),
        "gate_status": scan.get("gate_status"),
    }


def summary_v1(
    packet: SemanticPacket,
    *,
    include_raw_input: bool = False,
) -> dict[str, Any]:
    """Return a compact ``summary_v1`` dict for a compiled packet.

    By default this omits ``raw_input``, ``normalized_input``, and
    ``forward_text``. Pass ``include_raw_input=True`` to include them;
    ``forward_text`` is always present on opt-in and may be ``None``.

    ``unknowns``, ``next_questions``, and ``compiler_warnings`` may still
    carry input excerpts of up to 200 characters.
    """
    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA,
        "compiler": packet.compiler,
        "version": packet.version,
        "decision": _enum_name(packet.decision),
        "status": packet.status,
        "dataset_tier": _enum_name(packet.dataset_tier),
        "mode": _enum_name(packet.mode),
        "selected_target": packet.selected_target,
        "target_systems": list(packet.target_systems or []),
        "source_frames": list(packet.source_frames or []),
        "routing_candidates": _compact_candidates(packet.routing_candidates),
        "scores": dict(packet.scores or {}),
        "unknowns": [_truncate(item) for item in list(packet.unknowns or [])[:_MAX_LIST_ITEMS]],
        "contradictions": _compact_records(packet.contradictions),
        "category_errors": _compact_records(packet.category_errors),
        "semantic_error_class": packet.semantic_error_class,
        "semantic_error_confidence": packet.semantic_error_confidence,
        "testimony_integrity": _compact_testimony(packet.testimony_integrity_gate),
        "risk_flags": _risk_flags(packet.risk_scan),
        "needs_review": bool(packet.needs_review),
        "route_to": list(packet.route_to or []),
        "next_questions": [
            _truncate(item) for item in list(packet.next_questions or [])[:_MAX_LIST_ITEMS]
        ],
        "compiler_warnings": [
            _truncate(item) for item in list(packet.compiler_warnings or [])[:_MAX_LIST_ITEMS]
        ],
    }
    if include_raw_input:
        summary["raw_input"] = packet.raw_input
        summary["normalized_input"] = packet.normalized_input
        summary["forward_text"] = packet.forward_text
    return summary


def compile_json(
    text: str,
    registry: Any = None,
    context: Optional[dict[str, Any]] = None,
    mode: str = "AUTO",
    *,
    include_raw_input: bool = False,
) -> dict[str, Any]:
    """Compile ``text`` and return a compact ``summary_v1`` dict.

    Positional and default arguments match ``compile_semantic_packet``.
    The result is a dict (JSON-ready), not a JSON string, so hosts can
    inspect it before serializing.
    """
    packet = compile_semantic_packet(
        text, registry=registry, context=context, mode=mode
    )
    return summary_v1(packet, include_raw_input=include_raw_input)


__all__ = [
    "SUMMARY_SCHEMA",
    "compile_json",
    "summary_v1",
]
