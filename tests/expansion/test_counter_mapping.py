"""Tests for expansion.counter_mapping."""

from semantic_compiler.core.dataset import _negative_tests
from semantic_compiler.core.pipeline import compile_semantic_packet
from semantic_compiler.expansion.counter_mapping import (
    attach_disconfirmations,
    attach_to_packet,
    counterexample_found,
    searched_but_not_found,
)
from semantic_compiler.gates.corpus_completeness import CorpusState


def test_searched_but_not_found_is_scoped_not_absent():
    disc = searched_but_not_found(
        "look for a boundary case where the mapping fails",
        queries_used=["boundary failure"],
        documents_searched=["doc_a", "doc_b"],
    )
    nt = disc.to_negative_test("nt-0")
    assert nt["result"] == "SURVIVED"
    assert nt["counterexample"] is None
    assert nt["search"]["state"] == CorpusState.NOT_FOUND_WITHIN_SEARCH_SCOPE.value
    assert nt["search"]["documents_searched"] == ["doc_a", "doc_b"]


def test_no_search_performed_stays_untested():
    disc = searched_but_not_found("unattempted attack")
    nt = disc.to_negative_test("nt-0")
    assert nt["result"] == "UNTESTED"
    assert nt["search"]["state"] == CorpusState.SEARCH_NOT_PERFORMED.value


def test_counterexample_found_fails_or_weakens():
    failed = counterexample_found("attack", "the Moon is not magnetically bound")
    assert failed.result == "FAILED"
    assert failed.counterexample == "the Moon is not magnetically bound"
    weakened = counterexample_found("attack", "partial counter", weakened_only=True)
    assert weakened.result == "WEAKENED"


def test_attach_disconfirmations_flows_through_frozen_dataset_shape():
    mapping = {"source": "a", "target": "b", "negative_tests": []}
    discs = [
        searched_but_not_found("attack-1", documents_searched=["doc_a"]),
        counterexample_found(
            "attack-2",
            "counter",
            source_only_features=["only-in-source"],
            target_only_features=["only-in-target"],
        ),
    ]
    annotated = attach_disconfirmations(mapping, discs)
    assert mapping["negative_tests"] == []  # original untouched
    assert len(annotated["negative_tests"]) == 2

    # The frozen dataset builder passes these through unchanged in shape.
    row_tests = _negative_tests(annotated)
    assert row_tests[0]["result"] == "SURVIVED"
    assert row_tests[1]["result"] == "FAILED"
    assert row_tests[1]["counterexample"] == "counter"
    assert row_tests[1]["source_only_features"] == ["only-in-source"]
    assert row_tests[1]["target_only_features"] == ["only-in-target"]
    assert row_tests[0]["test_id"] == "nt-0"
    assert row_tests[1]["test_id"] == "nt-1"


def test_attach_disconfirmations_appends_to_existing():
    mapping = {"negative_tests": [{"test_id": "nt-0", "attack": "old", "result": "UNTESTED"}]}
    annotated = attach_disconfirmations(
        mapping, [searched_but_not_found("new", documents_searched=["d"])]
    )
    assert len(annotated["negative_tests"]) == 2
    assert annotated["negative_tests"][1]["test_id"] == "nt-1"


def test_attach_to_packet_with_selector():
    packet = compile_semantic_packet(
        "The firewall defends the network like the immune system defends the body."
    )
    if not packet.fractal_mappings:
        packet.fractal_mappings = [
            {"source": "immune system", "target": "firewall"},
            {"source": "other", "target": "thing"},
        ]
    attach_to_packet(
        packet,
        [searched_but_not_found("attack", documents_searched=["doc_a"])],
        mapping_selector=lambda i, m: m.get("target") == "firewall",
    )
    targets = {
        m["target"]: len(m.get("negative_tests", [])) for m in packet.fractal_mappings
    }
    assert targets["firewall"] == 1
    assert targets["thing"] == 0
