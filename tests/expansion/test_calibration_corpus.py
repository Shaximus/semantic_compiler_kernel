"""Tests for the V2.2 decompression calibration corpus builder (Task 11)."""
from collections import Counter

from scripts.build_decompression_calibration import build_corpus
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain
from semantic_compiler.expansion.registry import list_domains


def test_calibration_corpus_builds():
    corpus = build_corpus()
    assert len(corpus) >= 80
    for row in corpus[:5]:
        assert "system_model" in row
        assert "sample_kind" in row


def test_calibration_corpus_category_coverage():
    """120 samples: 8 calibration categories, spread over the 24 non-generic domains."""
    corpus = build_corpus()
    assert len(corpus) == 120

    categories = Counter(row["calibration_category"] for row in corpus)
    assert len(categories) == 8
    assert all(count >= 10 for count in categories.values())

    expected_domains = {d for d in list_domains() if d != "universal_generic"}
    assert len(expected_domains) == 24
    covered_domains = {row["domain"] for row in corpus}
    assert covered_domains == expected_domains

    for row in corpus:
        assert row["system_model"]["domain"]
        assert row["system_model"]["components"]

    # Rows added with this integration must actually decompress into the
    # domain they are labeled with. Older rows keep the historical contract
    # that the stored label and the router can differ.
    wired = {"android_connectivity", "bluetooth", "poe_chaos_inoculation"}
    for row in corpus:
        if row["domain"] in wired:
            assert _infer_domain(SemanticPacket(raw_input=row["input_text"])) == row["domain"]
            assert row["system_model"]["domain"] == row["domain"]
