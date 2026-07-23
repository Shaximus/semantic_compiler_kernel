"""Tests for expansion.verdicts."""

from semantic_compiler.expansion.verdicts import (
    CorpusVerdict,
    summarize_negative_results,
    translate_verdict,
    verdict_for_mapping,
)


def test_holds_requires_strong_verdict_and_survived_tests():
    assert translate_verdict("STRONG_STRUCTURAL_MATCH", ["SURVIVED"]) is CorpusVerdict.HOLDS
    assert translate_verdict("STRUCTURALLY_PLAUSIBLE", ["SURVIVED", "SURVIVED"]) is CorpusVerdict.HOLDS


def test_strong_verdict_with_no_tests_is_unresolved():
    assert translate_verdict("STRONG_STRUCTURAL_MATCH", []) is CorpusVerdict.UNRESOLVED
    assert translate_verdict("STRUCTURALLY_PLAUSIBLE", ["UNTESTED"]) is CorpusVerdict.UNRESOLVED


def test_strained_negatives_demote_strong_verdicts():
    assert translate_verdict("STRONG_STRUCTURAL_MATCH", ["FAILED"]) is CorpusVerdict.STRAINS
    assert translate_verdict("STRUCTURALLY_PLAUSIBLE", ["WEAKENED"]) is CorpusVerdict.STRAINS
    # pipeline attack_result vocabulary is also accepted
    assert translate_verdict("STRONG_STRUCTURAL_MATCH", ["SUSPICIOUS"]) is CorpusVerdict.STRAINS
    assert translate_verdict("STRUCTURALLY_PLAUSIBLE", ["WEAK"]) is CorpusVerdict.STRAINS


def test_heuristic_is_strains():
    assert translate_verdict("HEURISTIC", ["SURVIVED"]) is CorpusVerdict.STRAINS
    assert translate_verdict("HEURISTIC", []) is CorpusVerdict.STRAINS


def test_invalid_depends_on_evidence():
    assert translate_verdict("INVALID", ["FAILED"]) is CorpusVerdict.STRAINS
    assert translate_verdict("INVALID", []) is CorpusVerdict.UNRESOLVED
    assert translate_verdict("INVALID", ["UNTESTED"]) is CorpusVerdict.UNRESOLVED


def test_unresolved_and_unknown():
    assert translate_verdict("UNRESOLVED", ["SURVIVED"]) is CorpusVerdict.UNRESOLVED
    assert translate_verdict(None, ["SURVIVED"]) is CorpusVerdict.UNRESOLVED
    assert translate_verdict("GIBBERISH", []) is CorpusVerdict.UNRESOLVED


def test_summarize_negative_results_buckets():
    summary = summarize_negative_results(["SURVIVED", "WEAKENED", "FAILED", "UNTESTED", None])
    assert summary == {"survived": 1, "strained": 2, "untested": 2}


def test_verdict_for_mapping_end_to_end():
    mapping = {
        "verdict": "STRUCTURALLY_PLAUSIBLE",
        "negative_tests": [
            {"test_id": "nt-0", "result": "SURVIVED"},
            {"test_id": "nt-1", "result": "UNTESTED"},
        ],
    }
    out = verdict_for_mapping(mapping)
    assert out["verdict"] == "HOLDS"
    assert out["mapping_verdict"] == "STRUCTURALLY_PLAUSIBLE"
    assert out["negative_test_summary"] == {"survived": 1, "strained": 0, "untested": 1}
    assert "rationale" in out

    mapping["negative_tests"].append({"test_id": "nt-2", "result": "FAILED"})
    assert verdict_for_mapping(mapping)["verdict"] == "STRAINS"
