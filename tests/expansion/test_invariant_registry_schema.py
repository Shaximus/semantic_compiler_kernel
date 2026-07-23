"""Tests for the V2.2 invariant registry schema + validator."""

import json

from semantic_compiler.expansion.corpus import compile_corpus
from semantic_compiler.expansion.schema.v2_2_invariant_registry import (
    SCHEMA_PATH,
    V2_2_INVARIANT_REGISTRY_SCHEMA,
    validate_corpus_report,
    validate_invariant_registry,
)


def _two_doc_report():
    return compile_corpus([
        ("doc_a", "The immune system defends the body.", {"evidence_tier": "PRIMARY_RECORD"}),
        ("doc_b", "A firewall defends the network.", {"evidence_tier": "MARKED_SPECULATION"}),
    ], parallel_exposure_at="2030-01-01T00:00:00+00:00")


def test_schema_file_is_draft_2020_12_and_loads():
    with open(SCHEMA_PATH) as f:
        on_disk = json.load(f)
    assert on_disk == V2_2_INVARIANT_REGISTRY_SCHEMA
    assert "2020-12" in on_disk["$schema"]


def test_valid_report_passes():
    assert validate_corpus_report(_two_doc_report()) == []
    assert validate_invariant_registry(_two_doc_report()["invariant_registry"]) == []


def test_missing_top_level_field_reported():
    report = _two_doc_report()
    del report["invariant_registry"]
    errors = validate_corpus_report(report)
    assert any("invariant_registry" in e for e in errors)


def test_bad_verdict_and_tier_rejected():
    report = _two_doc_report()
    report["invariant_registry"][0]["verdict"] = "PROVEN"  # not in vocabulary
    report["invariant_registry"][0]["evidence_tier"] = "GOLD"  # wrong axis
    errors = validate_corpus_report(report)
    assert any("verdict" in e for e in errors)
    assert any("evidence_tier" in e for e in errors)


def test_invariant_missing_required_fields_rejected():
    report = _two_doc_report()
    inv = report["invariant_registry"][0]
    del inv["disconfirmations"]
    del inv["derivation_event_log"]
    errors = validate_invariant_registry([inv])
    assert any("disconfirmations" in e for e in errors)
    assert any("derivation_event_log" in e for e in errors)


def test_document_metadata_requires_evidence_tier_enum():
    report = _two_doc_report()
    report["corpus"]["documents"][0]["evidence_tier"] = "DIAMOND"
    errors = validate_corpus_report(report)
    assert any("evidence_tier" in e for e in errors)
