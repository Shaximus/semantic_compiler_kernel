"""Tests for expansion.corpus (chunking, aggregation, invariant registry)."""

import pytest

from semantic_compiler.expansion.corpus import (
    compile_corpus,
    chunk_text,
    load_documents,
    signature_key,
    structural_signature,
)
from semantic_compiler.expansion.schema.v2_2_invariant_registry import (
    validate_corpus_report,
)


# --- chunking -------------------------------------------------------------

def test_chunk_text_respects_max_and_preserves_offsets():
    text = "# Title\n\nPara one.\n\nPara two is a bit longer.\n\n" + ("x" * 500) + "\n\nFinal."
    chunks = chunk_text(text, max_chars=200)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.text) <= 200
        assert text[c.start:c.end] == c.text  # offsets locate the exact source span


def test_chunk_text_keeps_heading_with_following_section():
    text = "# Section A\n\nalpha body text\n\n# Section B\n\nbeta body text"
    chunks = chunk_text(text, max_chars=40)
    assert len(chunks) == 2
    assert chunks[0].text.startswith("# Section A")
    assert chunks[1].text.startswith("# Section B")


def test_chunk_text_hard_splits_oversized_lines():
    chunks = chunk_text("y" * 450, max_chars=200)
    assert [len(c.text) for c in chunks] == [200, 200, 50]
    assert [c.start for c in chunks] == [0, 200, 400]


def test_chunk_text_edge_cases():
    assert chunk_text("") == []
    assert chunk_text("short", 200)[0].text == "short"
    with pytest.raises(ValueError):
        chunk_text("text", max_chars=0)


# --- document loading -----------------------------------------------------

def test_load_documents_from_tuples_and_dicts():
    docs = load_documents([
        ("doc_a", "text a", {"evidence_tier": "PRIMARY_RECORD", "captured_at": "2026-01-01T00:00:00+00:00", "author": "x"}),
        {"doc_id": "doc_b", "text": "text b"},
    ])
    a, b = docs
    assert a.metadata.doc_id == "doc_a"
    assert a.metadata.evidence_tier == "PRIMARY_RECORD"
    assert a.metadata.captured_at == "2026-01-01T00:00:00+00:00"
    assert a.metadata.extra == {"author": "x"}
    assert b.metadata.doc_id == "doc_b"
    assert b.metadata.captured_at  # auto-populated
    assert b.metadata.evidence_tier == "SELF_ASSESSED_ESTIMATE"  # default


def test_load_documents_from_path(tmp_path):
    p = tmp_path / "sample_doc.md"
    p.write_text("content here", encoding="utf-8")
    (doc,) = load_documents([p])
    assert doc.metadata.doc_id == "sample_doc"
    assert doc.metadata.source_path == str(p)
    assert doc.text == "content here"
    assert doc.metadata.captured_at  # from file mtime


# --- aggregation / invariant registry --------------------------------------

class _FakePacket:
    """Minimal packet stand-in so aggregation tests stay fast and deterministic."""

    def __init__(self, claim_type, frames):
        self.claim_types = [{"claim_type": claim_type}]
        self.structural_skeleton = {"actors": ["a"], "objects": []}
        self.source_frames = frames
        self.semantic_ir = None
        self.decision = None


def _fake_compile(claim_type="OBSERVATION", frames=("biology",)):
    def compile_fn(text, context=None):
        assert context and "document_metadata" in context  # metadata flows through
        return _FakePacket(claim_type, list(frames))
    return compile_fn


def test_compile_corpus_builds_cross_document_registry():
    report = compile_corpus(
        [
            ("doc_a", "alpha text", {"evidence_tier": "PRIMARY_RECORD", "captured_at": "2026-01-01T00:00:00+00:00"}),
            ("doc_b", "beta text", {"evidence_tier": "MARKED_SPECULATION", "captured_at": "2026-02-01T00:00:00+00:00"}),
        ],
        compile_fn=_fake_compile(),
    )
    assert report["corpus"]["document_count"] == 2
    assert len(report["invariant_registry"]) == 1  # same fingerprint in both docs

    inv = report["invariant_registry"][0]
    assert inv["invariant_id"] == "INV-0000"
    assert inv["verdict"] == "HOLDS"  # recurs in >= 2 documents
    assert inv["supporting_documents"] == ["doc_a", "doc_b"]
    assert inv["confirmations"] == 2
    assert {s["doc_id"] for s in inv["supporting"]} == {"doc_a", "doc_b"}
    # strongest tier across supporters wins
    assert inv["evidence_tier"] == "PRIMARY_RECORD"
    assert inv["first_seen_at"] == "2026-01-01T00:00:00+00:00"
    assert inv["last_seen_at"] == "2026-02-01T00:00:00+00:00"
    assert inv["disconfirmations"] == []  # no searched doc lacked the fingerprint


def test_single_document_invariant_is_unresolved_with_honest_disconfirmation():
    def compile_fn(text, context=None):
        frame = "biology" if context["document_metadata"]["doc_id"] == "doc_a" else "computation"
        return _FakePacket("OBSERVATION", [frame])

    report = compile_corpus([("doc_a", "alpha", {}), ("doc_b", "beta", {})], compile_fn=compile_fn)
    assert len(report["invariant_registry"]) == 2
    for inv in report["invariant_registry"]:
        assert inv["verdict"] == "UNRESOLVED"
        assert len(inv["disconfirmations"]) == 1
        disc = inv["disconfirmations"][0]
        assert disc["result"] == "SURVIVED"  # searched, not found — within scope
        assert disc["search"]["state"] == "NOT_FOUND_WITHIN_SEARCH_SCOPE"
        other = "doc_b" if inv["supporting_documents"] == ["doc_a"] else "doc_a"
        assert disc["search"]["documents_searched"] == [other]


def test_compile_corpus_chunking_and_context_metadata():
    long_text = ("Paragraph one has some content.\n\n" * 60).strip()
    captured = []

    def compile_fn(text, context=None):
        captured.append(context)
        return _FakePacket("OBSERVATION", ["biology"])

    report = compile_corpus(
        [("doc_long", long_text, {"evidence_tier": "PUBLISHED_RESEARCH"})],
        max_chunk_chars=200,
        compile_fn=compile_fn,
    )
    doc = report["documents"]["doc_long"]
    assert doc["chunk_count"] > 1
    assert len(captured) == doc["chunk_count"]
    for ctx in captured:
        assert ctx["document_metadata"]["doc_id"] == "doc_long"
        assert ctx["document_metadata"]["evidence_tier"] == "PUBLISHED_RESEARCH"
        assert ctx["chunk"]["chunk_count"] == doc["chunk_count"]
    # supporting locations carry document + chunk coordinates
    inv = report["invariant_registry"][0]
    assert all({"doc_id", "chunk_index", "start", "end"} <= set(s) for s in inv["supporting"])


def test_derivation_event_log_wired_when_exposure_given():
    report = compile_corpus(
        [("doc_a", "alpha", {})],
        compile_fn=_fake_compile(),
        parallel_exposure_at="2030-01-01T00:00:00+00:00",
    )
    inv = report["invariant_registry"][0]
    assert len(inv["derivation_event_log"]) == 1
    event = inv["derivation_event_log"][0]
    assert event["subject_id"] == "INV-0000"
    assert event["derived_before_exposure"] is True  # derived now, exposed in 2030

    report_no_exposure = compile_corpus([("doc_a", "alpha", {})], compile_fn=_fake_compile())
    assert report_no_exposure["invariant_registry"][0]["derivation_event_log"] == []


def test_corpus_report_validates_against_schema_with_real_compiler():
    report = compile_corpus([
        ("doc_a", "The immune system defends the body against pathogens.", {"evidence_tier": "PRIMARY_RECORD"}),
        ("doc_b", "A firewall defends the network against intrusions.", {"evidence_tier": "PUBLISHED_RESEARCH"}),
    ])
    assert validate_corpus_report(report) == []


def test_structural_signature_deterministic():
    packet = _FakePacket("OBSERVATION", ["computation", "biology"])
    sig1 = structural_signature(packet)
    sig2 = structural_signature(_FakePacket("OBSERVATION", ["biology", "computation"]))
    assert sig1 == sig2  # sorted, order-insensitive
    assert signature_key(sig1) == signature_key(sig2)
