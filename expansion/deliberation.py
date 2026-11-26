"""Provisional defaults that have not had real deliberation.

Compiled entries may carry ``pending_deliberation: true`` and
``deliberation_status: PROVISIONAL_DEFAULT``. When such an entry is
routed (explicit ID) or is the top compiled-entry match, the compiler
sets a visible ``needs_review`` flag on the output / trace and logs
the trigger so the lack of deliberation is not forgotten.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Iterable, Mapping, Sequence

logger = logging.getLogger("semantic_compiler.deliberation")

# Same shape as expansion.router._SC_ID_RE; kept local to avoid import cycles.
_SC_ID_RE = re.compile(r"\bSC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}\b", re.IGNORECASE)

PENDING_WARNING_PREFIX = "NEEDS_REVIEW:"


def _record_layers(record: Mapping[str, Any] | None) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    if not isinstance(record, Mapping):
        return {}, {}
    meta = record.get("metadata") if isinstance(record.get("metadata"), Mapping) else {}
    v2 = record.get("v2_extensions") if isinstance(record.get("v2_extensions"), Mapping) else {}
    deliberation = v2.get("deliberation") if isinstance(v2.get("deliberation"), Mapping) else {}
    return meta, deliberation


def pending_info(record: Mapping[str, Any] | None, *, entry_id: str | None = None) -> dict[str, Any] | None:
    """Return a needs_review payload if the compiled record is pending deliberation."""
    meta, deliberation = _record_layers(record)
    pending = bool(meta.get("pending_deliberation") or deliberation.get("pending_deliberation"))
    if not pending:
        return None
    eid = (
        entry_id
        or meta.get("entry_id")
        or (record or {}).get("entry_id")
        or deliberation.get("entry_id")
    )
    triggers = (
        meta.get("review_trigger_terms")
        or deliberation.get("review_trigger_terms")
        or ()
    )
    trigger_terms = tuple(str(x).lower() for x in triggers if str(x).strip())
    return {
        "entry_id": str(eid) if eid else "",
        "needs_review": True,
        "status": str(
            meta.get("deliberation_status")
            or deliberation.get("status")
            or "PROVISIONAL_DEFAULT"
        ),
        "reason": str(
            meta.get("pending_deliberation_reason")
            or deliberation.get("reason")
            or ""
        ),
        "review_trigger_terms": list(trigger_terms),
    }


def pending_info_for_entry(entry_id: str, elevator: Any | None = None) -> dict[str, Any] | None:
    if elevator is None:
        from semantic_compiler.expansion.elevator import get_default_elevator

        elevator = get_default_elevator()
        elevator._ensure_ready()
    slot = (getattr(elevator, "_compiled_entries", None) or {}).get(entry_id)
    if not slot:
        return None
    return pending_info(slot.get("record"), entry_id=entry_id)


def _dedupe(entries: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for raw in entries:
        if not isinstance(raw, Mapping):
            continue
        item = dict(raw)
        eid = str(item.get("entry_id") or "")
        key = eid + "|" + str(item.get("trigger") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out



# Weak overlapping tokens ("path", "beside") can make an unrelated prompt
# the numeric top compiled-entry hit. A top match only triggers review when
# it is actually about the pending entry: declared trigger terms, or a
# high-score multi-term match when no list is declared.
_FALLBACK_TOP_MATCH_MIN_SCORE = 48.0
_FALLBACK_TOP_MATCH_MIN_TERMS = 3


def _top_match_is_strong(match: Any, info: Mapping[str, Any], text: str) -> bool:
    eid = str(info.get("entry_id") or getattr(match, "entry_id", "") or "").lower()
    query = (text or "").lower()
    raw_terms = getattr(match, "matched_terms", None)
    if raw_terms is None and isinstance(match, Mapping):
        raw_terms = match.get("matched_terms") or ()
    matched = tuple(str(t).lower() for t in (raw_terms or ()))
    declared = tuple(str(t).lower() for t in (info.get("review_trigger_terms") or ()) if t)
    if declared:
        hits = [t for t in declared if t in query or t in matched or t.replace("-", " ") in query]
        if eid and any(t == eid or t.replace("_", "-") == eid for t in hits):
            return True
        return len(set(hits)) >= 2
    score = float(getattr(match, "score", 0) or (match.get("score") if isinstance(match, Mapping) else 0) or 0)
    return score >= _FALLBACK_TOP_MATCH_MIN_SCORE and len(matched) >= _FALLBACK_TOP_MATCH_MIN_TERMS


def collect_pending_triggers(
    text: str,
    *,
    compiled_matches: Sequence[Any] | None = None,
    elevator: Any | None = None,
) -> list[dict[str, Any]]:
    """Triggers: explicit compiled-entry IDs, or the top compiled-entry match."""
    if elevator is None:
        from semantic_compiler.expansion.elevator import get_default_elevator

        elevator = get_default_elevator()
        elevator._ensure_ready()

    found: list[dict[str, Any]] = []
    for match in _SC_ID_RE.finditer(text or ""):
        eid = match.group(0).upper()
        info = pending_info_for_entry(eid, elevator)
        if info:
            found.append(_public_trigger(info, "explicit_id"))

    if compiled_matches:
        top = compiled_matches[0]
        eid = getattr(top, "entry_id", None) or (top.get("entry_id") if isinstance(top, Mapping) else None)
        if eid:
            info = pending_info_for_entry(str(eid), elevator)
            if info and _top_match_is_strong(top, info, text or ""):
                found.append(_public_trigger(info, "top_compiled_match"))

    return _dedupe(found)


def _public_trigger(info: Mapping[str, Any], trigger: str) -> dict[str, Any]:
    return {
        "entry_id": info.get("entry_id"),
        "needs_review": True,
        "status": info.get("status"),
        "reason": info.get("reason"),
        "trigger": trigger,
    }


def log_needs_review(entries: Sequence[Mapping[str, Any]], *, source: str) -> None:
    for item in entries:
        logger.warning(
            "PENDING_DELIBERATION needs_review entry=%s source=%s status=%s trigger=%s reason=%s",
            item.get("entry_id"),
            source,
            item.get("status"),
            item.get("trigger"),
            item.get("reason"),
        )


def warning_text(item: Mapping[str, Any]) -> str:
    eid = item.get("entry_id") or "unknown"
    status = item.get("status") or "PROVISIONAL_DEFAULT"
    return f"{PENDING_WARNING_PREFIX} {eid} is a {status} (pending_deliberation)"


def annotate_routing_result(text: str, result: Any, elevator: Any | None = None) -> Any:
    """Copy needs_review onto a RoutingResult when an explicit pending ID is named."""
    triggers = collect_pending_triggers(text, elevator=elevator)
    if not triggers or result is None:
        return result
    log_needs_review(triggers, source="route")
    try:
        from dataclasses import replace

        return replace(result, needs_review=True, needs_review_entries=tuple(triggers))
    except TypeError:
        return result


def annotate_bay_delivery(delivery: Any, elevator: Any | None = None) -> Any:
    """Flag a summon() delivery when a pending entry is named or is the top match."""
    if delivery is None:
        return delivery
    triggers = collect_pending_triggers(
        getattr(delivery, "query", "") or "",
        compiled_matches=getattr(delivery, "compiled_entries", ()) or (),
        elevator=elevator,
    )
    if not triggers:
        return delivery
    log_needs_review(triggers, source="summon")
    try:
        from dataclasses import replace

        return replace(delivery, needs_review=True, needs_review_entries=tuple(triggers))
    except TypeError:
        return delivery


def apply_to_packet(packet: Any, text: str, *, elevator: Any | None = None) -> list[dict[str, Any]]:
    """Set visible needs_review fields on a SemanticPacket and log triggers."""
    from semantic_compiler.expansion.elevator import get_default_elevator, summon

    if elevator is None:
        elevator = get_default_elevator()
        elevator._ensure_ready()

    top_matches: Sequence[Any] = ()
    try:
        delivery = summon(text, top_k=3)
        top_matches = getattr(delivery, "compiled_entries", ()) or ()
    except Exception:  # noqa: BLE001 — review hook must never break compile
        top_matches = ()

    triggers = collect_pending_triggers(text, compiled_matches=top_matches, elevator=elevator)
    if not triggers:
        if hasattr(packet, "needs_review"):
            packet.needs_review = False
        if hasattr(packet, "needs_review_entries"):
            packet.needs_review_entries = []
        return []

    log_needs_review(triggers, source="compile")
    packet.needs_review = True
    packet.needs_review_entries = [dict(item) for item in triggers]
    if hasattr(packet, "compiler_warnings"):
        for item in triggers:
            text_w = warning_text(item)
            if text_w not in packet.compiler_warnings:
                packet.compiler_warnings.append(text_w)
    return list(packet.needs_review_entries)


__all__ = [
    "PENDING_WARNING_PREFIX",
    "annotate_bay_delivery",
    "annotate_routing_result",
    "apply_to_packet",
    "collect_pending_triggers",
    "log_needs_review",
    "pending_info",
    "pending_info_for_entry",
    "warning_text",
]
