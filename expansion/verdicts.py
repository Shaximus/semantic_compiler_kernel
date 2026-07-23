"""
Verdict vocabulary translation layer (V2.2 expansion).

The frozen core emits two verdict vocabularies:

- Mapping verdicts (:func:`semantic_compiler.core.dataset._mapping_verdict`):
  ``STRONG_STRUCTURAL_MATCH`` / ``STRUCTURALLY_PLAUSIBLE`` / ``HEURISTIC`` /
  ``INVALID`` / ``UNRESOLVED``
- Negative-test results (dataset rows and pipeline attack results):
  ``SURVIVED`` / ``WEAKENED`` / ``FAILED`` / ``UNTESTED`` (dataset rows) and
  ``SURVIVED`` / ``WEAK`` / ``SUSPICIOUS`` / ``UNTESTED`` (pipeline
  ``attack_result`` values).

The corpus-mapping mission needs one coarse, decision-facing vocabulary:
``HOLDS`` / ``STRAINS`` / ``UNRESOLVED``. This module is a pure translation
layer; it changes no frozen machinery.

Mapping table
=============

===========================  ==================================  ===========
Mapping verdict              Negative-test posture               Corpus verdict
===========================  ==================================  ===========
STRONG_STRUCTURAL_MATCH      >=1 tested, all SURVIVED            HOLDS
STRUCTURALLY_PLAUSIBLE       >=1 tested, all SURVIVED            HOLDS
STRONG / PLAUSIBLE           any WEAKENED/FAILED/WEAK/SUSPICIOUS STRAINS
STRONG / PLAUSIBLE           nothing tested (all UNTESTED/none)  UNRESOLVED
HEURISTIC                    any                                 STRAINS
INVALID                      any tested negative                 STRAINS
INVALID                      nothing tested (insufficient evid.) UNRESOLVED
UNRESOLVED / unknown         any                                 UNRESOLVED
===========================  ==================================  ===========

Note on vocabulary drift: the design brief referenced negative-test results
``WEAK``/``SUSPICIOUS``; those are the *pipeline* ``attack_result`` values
(``core/pipeline.py:run_negative_isomorphism_tests``). Dataset-row results use
``WEAKENED``/``FAILED``. Both are normalized here.
"""

from __future__ import annotations

from enum import Enum, unique
from typing import Any, Iterable, Optional


@unique
class CorpusVerdict(Enum):
    """Mission-facing verdict for a mapping or cross-document invariant."""

    HOLDS = "HOLDS"
    STRAINS = "STRAINS"
    UNRESOLVED = "UNRESOLVED"


ALL_VERDICT_VALUES: tuple[str, ...] = tuple(v.value for v in CorpusVerdict)

# Normalized negative-test result buckets (both vocabularies accepted).
_SURVIVED = {"SURVIVED"}
_STRAINED = {"WEAKENED", "FAILED", "WEAK", "SUSPICIOUS"}
_UNTESTED = {"UNTESTED", ""}

_STRONG_VERDICTS = {"STRONG_STRUCTURAL_MATCH", "STRUCTURALLY_PLAUSIBLE"}


def _normalize_result(result: Any) -> str:
    return str(result or "").strip().upper()


def summarize_negative_results(
    results: Iterable[Any],
) -> dict[str, int]:
    """
    Bucket negative-test results (either vocabulary) into counts.

    Returns ``{"survived": n, "strained": n, "untested": n}``.
    """
    summary = {"survived": 0, "strained": 0, "untested": 0}
    for r in results:
        normalized = _normalize_result(r)
        if normalized in _SURVIVED:
            summary["survived"] += 1
        elif normalized in _STRAINED:
            summary["strained"] += 1
        else:
            summary["untested"] += 1
    return summary


def translate_verdict(
    mapping_verdict: Optional[str],
    negative_results: Optional[Iterable[Any]] = None,
) -> CorpusVerdict:
    """
    Translate a frozen-core mapping verdict plus negative-test results into a
    :class:`CorpusVerdict` per the mapping table in the module docstring.
    """
    verdict = _normalize_result(mapping_verdict)
    summary = summarize_negative_results(negative_results or [])
    tested = summary["survived"] + summary["strained"]

    if verdict in _STRONG_VERDICTS:
        if summary["strained"] > 0:
            return CorpusVerdict.STRAINS
        if tested == 0:
            return CorpusVerdict.UNRESOLVED
        return CorpusVerdict.HOLDS
    if verdict == "HEURISTIC":
        return CorpusVerdict.STRAINS
    if verdict == "INVALID":
        return CorpusVerdict.STRAINS if tested > 0 else CorpusVerdict.UNRESOLVED
    return CorpusVerdict.UNRESOLVED


def verdict_for_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    """
    Translate one dataset-row mapping dict (the shape produced by
    ``core.dataset._build_mappings``) into a corpus verdict with an auditable
    rationale.
    """
    negative_tests = mapping.get("negative_tests") or []
    results = [t.get("result") if isinstance(t, dict) else t for t in negative_tests]
    summary = summarize_negative_results(results)
    corpus_verdict = translate_verdict(mapping.get("verdict"), results)
    return {
        "verdict": corpus_verdict.value,
        "mapping_verdict": _normalize_result(mapping.get("verdict")) or None,
        "negative_test_summary": summary,
        "rationale": (
            f"mapping_verdict={_normalize_result(mapping.get('verdict')) or 'MISSING'}, "
            f"survived={summary['survived']}, strained={summary['strained']}, "
            f"untested={summary['untested']}"
        ),
    }
