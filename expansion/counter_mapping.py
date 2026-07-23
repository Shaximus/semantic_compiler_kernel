"""
Counter-mapping population API (V2.2 expansion).

The frozen pipeline hardwires disconfirmation fields to empty
(``core/pipeline.py:run_negative_isomorphism_tests`` marks
``source_only_features`` / ``target_only_features`` as "LLM-assisted"; dataset
rows default ``counterexample`` to ``None``). This module lets callers attach
*real* disconfirmations to mappings so they flow through the unchanged frozen
machinery into the dataset row's ``negative_tests[]``.

Discipline mirrors ``gates/corpus_completeness.py``: "searched but not found"
is an auditable search record with a bounded scope — never a claimed proof of
absence. A disconfirmation with no search performed stays ``UNTESTED``.

All helpers are deterministic and non-mutating.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from semantic_compiler.gates.corpus_completeness import CorpusState

# Result vocabulary accepted by core.dataset._negative_tests (uppercased there).
RESULT_SURVIVED = "SURVIVED"
RESULT_WEAKENED = "WEAKENED"
RESULT_FAILED = "FAILED"
RESULT_UNTESTED = "UNTESTED"


@dataclass(frozen=True)
class SearchScope:
    """Auditable record of the search behind a disconfirmation."""

    queries_used: tuple[str, ...] = ()
    documents_searched: tuple[str, ...] = ()
    searched_at: Optional[str] = None
    state: str = CorpusState.SEARCH_NOT_PERFORMED.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "queries_used": list(self.queries_used),
            "documents_searched": list(self.documents_searched),
            "searched_at": self.searched_at,
            "state": self.state,
        }


@dataclass(frozen=True)
class Disconfirmation:
    """One disconfirmation record for a mapping or invariant."""

    attack: str
    counterexample: Optional[str] = None
    source_only_features: tuple[str, ...] = ()
    target_only_features: tuple[str, ...] = ()
    result: str = RESULT_UNTESTED
    impact: str = "unknown"
    search: Optional[SearchScope] = None
    note: str = ""
    evidence_tier: Optional[str] = None

    def to_negative_test(self, test_id: str) -> dict[str, Any]:
        """
        Render in the exact shape ``core.dataset._negative_tests`` passes
        through into a dataset row's ``negative_tests[]`` (plus an auditable
        ``search`` extension the frozen layer simply ignores).
        """
        return {
            "test_id": test_id,
            "attack": self.attack,
            "source_only_features": list(self.source_only_features),
            "target_only_features": list(self.target_only_features),
            "counterexample": self.counterexample,
            "result": self.result,
            "impact": self.impact,
            "search": self.search.to_dict() if self.search else None,
            "note": self.note,
            "evidence_tier": self.evidence_tier,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def counterexample_found(
    attack: str,
    counterexample: str,
    *,
    source_only_features: Iterable[str] = (),
    target_only_features: Iterable[str] = (),
    weakened_only: bool = False,
    impact: str = "unknown",
    queries_used: Iterable[str] = (),
    documents_searched: Iterable[str] = (),
    searched_at: Optional[str] = None,
    note: str = "",
    evidence_tier: Optional[str] = None,
) -> Disconfirmation:
    """Record a counterexample that was actually found (FAILED or WEAKENED)."""
    search = SearchScope(
        queries_used=tuple(queries_used),
        documents_searched=tuple(documents_searched),
        searched_at=searched_at or _now(),
        state=CorpusState.PRESENT_IN_CURRENT_CONTEXT.value,
    )
    return Disconfirmation(
        attack=attack,
        counterexample=counterexample,
        source_only_features=tuple(source_only_features),
        target_only_features=tuple(target_only_features),
        result=RESULT_WEAKENED if weakened_only else RESULT_FAILED,
        impact=impact,
        search=search,
        note=note,
        evidence_tier=evidence_tier,
    )


def searched_but_not_found(
    attack: str,
    *,
    queries_used: Iterable[str] = (),
    documents_searched: Iterable[str] = (),
    searched_at: Optional[str] = None,
    impact: str = "unknown",
    note: str = "",
) -> Disconfirmation:
    """
    Record an honest "searched but not found" attack result.

    If at least one document was searched, the attack SURVIVED *within the
    declared scope* (``NOT_FOUND_WITHIN_SEARCH_SCOPE`` — never a claim of
    confirmed absence). With no search performed, the record stays
    ``UNTESTED`` (``SEARCH_NOT_PERFORMED``).
    """
    docs = tuple(documents_searched)
    performed = bool(docs)
    search = SearchScope(
        queries_used=tuple(queries_used),
        documents_searched=docs,
        searched_at=searched_at or _now(),
        state=(
            CorpusState.NOT_FOUND_WITHIN_SEARCH_SCOPE.value
            if performed
            else CorpusState.SEARCH_NOT_PERFORMED.value
        ),
    )
    return Disconfirmation(
        attack=attack,
        counterexample=None,
        result=RESULT_SURVIVED if performed else RESULT_UNTESTED,
        impact=impact,
        search=search,
        note=note,
    )


def attach_disconfirmations(
    mapping: dict[str, Any],
    disconfirmations: Iterable[Disconfirmation],
    *,
    start_index: int = 0,
) -> dict[str, Any]:
    """
    Return a copy of a fractal-mapping dict with the given disconfirmations
    appended to its ``negative_tests`` list, in the shape the frozen dataset
    builder passes through. The original mapping is never mutated.
    """
    annotated = dict(mapping)
    existing = list(annotated.get("negative_tests") or [])
    base = start_index + len(existing)
    for i, d in enumerate(disconfirmations):
        existing.append(d.to_negative_test(test_id=f"nt-{base + i}"))
    annotated["negative_tests"] = existing
    return annotated


def attach_to_packet(
    packet: Any,
    disconfirmations: Iterable[Disconfirmation],
    *,
    mapping_selector: Optional[Any] = None,
) -> Any:
    """
    Attach disconfirmations to a packet's ``fractal_mappings`` entries in
    place (packets are mutable pipeline objects), so that a subsequent
    ``build_dataset_row`` carries them into the row's ``negative_tests[]``.

    ``mapping_selector`` is an optional predicate ``(index, mapping) -> bool``;
    without one, every mapping receives the disconfirmations.
    """
    discs = list(disconfirmations)
    for i, mapping in enumerate(packet.fractal_mappings or []):
        if mapping_selector is not None and not mapping_selector(i, mapping):
            continue
        existing = list(mapping.get("negative_tests") or [])
        for j, d in enumerate(discs):
            existing.append(d.to_negative_test(test_id=f"nt-{len(existing) + j}"))
        mapping["negative_tests"] = existing
    return packet
