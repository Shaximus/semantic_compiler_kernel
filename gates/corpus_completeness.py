"""
Reflexion Semantic Compiler v2.0.0 — Corpus Completeness Gate

Prevents "not found in current context" from being misreported as confirmed
absence. The gate distinguishes:

- PRESENT_IN_CURRENT_CONTEXT
- FOUND_IN_LINKED_CORPUS
- NOT_FOUND_WITHIN_SEARCH_SCOPE
- SEARCH_NOT_PERFORMED
- SEARCH_UNAVAILABLE
- ABSENT_FROM_VERSION_LOCKED_CORPUS

Citation: Kestrel V2.1 Calibration Review — Corpus Completeness Patch
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class CorpusState(Enum):
    """Bounded states for corpus-completeness assertions."""

    PRESENT_IN_CURRENT_CONTEXT = "PRESENT_IN_CURRENT_CONTEXT"
    FOUND_IN_LINKED_CORPUS = "FOUND_IN_LINKED_CORPUS"
    NOT_FOUND_WITHIN_SEARCH_SCOPE = "NOT_FOUND_WITHIN_SEARCH_SCOPE"
    SEARCH_NOT_PERFORMED = "SEARCH_NOT_PERFORMED"
    SEARCH_UNAVAILABLE = "SEARCH_UNAVAILABLE"
    ABSENT_FROM_VERSION_LOCKED_CORPUS = "ABSENT_FROM_VERSION_LOCKED_CORPUS"


@dataclass
class CorpusSearchRecord:
    """Auditable record of a corpus-completeness search."""

    corpus_manifest_hash: str = ""
    corpus_version: str = ""
    queries_used: list[str] = field(default_factory=list)
    documents_searched: list[str] = field(default_factory=list)
    linked_documents_unavailable: list[str] = field(default_factory=list)
    coverage_ratio: float = 0.0
    search_completed_at: str = ""
    absence_confidence: float = 0.0


class CorpusCompletenessGate:
    """
    Evaluate whether a claimed component is present, found in linked corpus,
    not found within search scope, or confirmed absent from a locked corpus.
    """

    def __init__(
        self,
        manifest: dict[str, Any] | None = None,
        search_fn: Callable[[list[str]], list[dict[str, Any]]] | None = None,
        search_record: CorpusSearchRecord | None = None,
    ):
        self.manifest = manifest or {}
        self.search_fn = search_fn
        self.search_record = search_record or CorpusSearchRecord()

    def check(
        self,
        claim_component: str,
        query_terms: list[str],
    ) -> dict[str, Any]:
        """
        Return the corpus-completeness state for a claim component.

        The gate never returns ABSENT_FROM_VERSION_LOCKED_CORPUS automatically;
        that state must be requested explicitly by a caller who has performed
        a complete, locked-corpus search.
        """
        current_context = self.manifest.get("current_context", {})
        if claim_component in current_context:
            return {
                "state": CorpusState.PRESENT_IN_CURRENT_CONTEXT.value,
                "passed": True,
                "search_record": self.search_record,
            }

        if self.search_fn is None:
            return {
                "state": CorpusState.SEARCH_NOT_PERFORMED.value,
                "passed": None,
                "search_record": self.search_record,
            }

        try:
            results = self.search_fn(query_terms)
        except Exception as exc:  # pragma: no cover — search infrastructure failure
            return {
                "state": CorpusState.SEARCH_UNAVAILABLE.value,
                "passed": None,
                "search_record": self.search_record,
                "error": str(exc),
            }

        self.search_record.queries_used = query_terms
        self.search_record.search_completed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        if results:
            return {
                "state": CorpusState.FOUND_IN_LINKED_CORPUS.value,
                "passed": True,
                "search_record": self.search_record,
                "hits": [r.get("path") or r.get("id") for r in results],
            }

        return {
            "state": CorpusState.NOT_FOUND_WITHIN_SEARCH_SCOPE.value,
            "passed": None,
            "search_record": self.search_record,
        }

    def confirm_absent_from_locked_corpus(
        self,
        claim_component: str,
        query_terms: list[str],
        coverage_ratio: float,
        corpus_manifest_hash: str,
        corpus_version: str,
    ) -> dict[str, Any]:
        """
        Explicitly assert absence from a version-locked, fully-searched corpus.

        This is the only path to ABSENT_FROM_VERSION_LOCKED_CORPUS. Callers
        must supply audit metadata proving the search was complete.
        """
        record = CorpusSearchRecord(
            corpus_manifest_hash=corpus_manifest_hash,
            corpus_version=corpus_version,
            queries_used=query_terms,
            coverage_ratio=coverage_ratio,
            search_completed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            absence_confidence=coverage_ratio,
        )
        return {
            "state": CorpusState.ABSENT_FROM_VERSION_LOCKED_CORPUS.value,
            "passed": False,
            "search_record": record,
        }
