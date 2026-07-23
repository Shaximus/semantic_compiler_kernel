"""
Derivation-order tracking (V2.2 expansion).

For every claim or cross-document invariant the mission needs to know whether
a structure was derived *before* or *after* the analyst was exposed to a
parallel account of the same structure. A "parallel" is an independent
document/artifact describing a matching structure; deriving before exposure is
evidence of independent convergence, deriving after exposure is not.

This module provides a small deterministic event log:

- :func:`compute_before_exposure` — pure timestamp comparison, returns
  ``True`` / ``False`` / ``None`` (``None`` = cannot be determined honestly).
- :class:`DerivationEvent` — one per-claim/per-invariant record.
- :func:`attach_derivation_event` — non-mutating annotation helper used by the
  corpus report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _parse_iso(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp; naive timestamps are assumed UTC."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str) and value.strip():
        try:
            dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def compute_before_exposure(
    derived_at: Any,
    exposed_to_parallel_at: Any,
) -> Optional[bool]:
    """
    Return whether derivation preceded exposure to the parallel account.

    ``None`` when either timestamp is missing or unparseable — the honest
    "cannot be determined" answer, never a guessed boolean.
    """
    derived = _parse_iso(derived_at)
    exposed = _parse_iso(exposed_to_parallel_at)
    if derived is None or exposed is None:
        return None
    return derived < exposed


@dataclass(frozen=True)
class DerivationEvent:
    """One derivation-order record for a claim or invariant."""

    subject_id: str
    derived_at: Optional[str] = None
    exposed_to_parallel_at: Optional[str] = None
    derived_before_exposure: Optional[bool] = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "derived_at": self.derived_at,
            "exposed_to_parallel_at": self.exposed_to_parallel_at,
            "derived_before_exposure": self.derived_before_exposure,
            "note": self.note,
        }


def make_event(
    subject_id: str,
    derived_at: Any = None,
    exposed_to_parallel_at: Any = None,
    note: str = "",
) -> DerivationEvent:
    """Build a :class:`DerivationEvent`, computing the before/after flag."""
    return DerivationEvent(
        subject_id=subject_id,
        derived_at=_format(derived_at),
        exposed_to_parallel_at=_format(exposed_to_parallel_at),
        derived_before_exposure=compute_before_exposure(
            derived_at, exposed_to_parallel_at
        ),
        note=note,
    )


def _format(value: Any) -> Optional[str]:
    dt = _parse_iso(value)
    return dt.isoformat() if dt is not None else (value if isinstance(value, str) and value.strip() else None)


def attach_derivation_event(
    record: dict[str, Any],
    event: DerivationEvent,
) -> dict[str, Any]:
    """
    Return a copy of ``record`` with ``event`` appended to its
    ``derivation_event_log`` list. The original record is never mutated.
    """
    annotated = dict(record)
    log = list(annotated.get("derivation_event_log") or [])
    log.append(event.to_dict())
    annotated["derivation_event_log"] = log
    return annotated


def build_event_log(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build a normalized event log from raw dicts with keys ``subject_id``,
    ``derived_at``, ``exposed_to_parallel_at``, ``note``.
    """
    return [
        make_event(
            subject_id=str(e.get("subject_id", "")),
            derived_at=e.get("derived_at"),
            exposed_to_parallel_at=e.get("exposed_to_parallel_at"),
            note=str(e.get("note", "")),
        ).to_dict()
        for e in entries
    ]
