"""Tests for the V2.2 decompression calibration corpus builder (Task 11)."""
from collections import Counter


def test_calibration_corpus_builds():
    from scripts.build_decompression_calibration import build_corpus
    corpus = build_corpus()
    assert len(corpus) >= 80
    for row in corpus[:5]:
        assert "system_model" in row
        assert "sample_kind" in row


def test_calibration_corpus_category_coverage():
    """90 samples: 8 calibration categories, spread over the 18 domains."""
    from scripts.build_decompression_calibration import build_corpus
    from expansion.registry import list_domains

    corpus = build_corpus()
    assert len(corpus) == 90

    categories = Counter(row["calibration_category"] for row in corpus)
    assert len(categories) == 8
    assert all(count >= 10 for count in categories.values())

    expected_domains = {d for d in list_domains() if d != "universal_generic"}
    assert len(expected_domains) == 18
    covered_domains = {row["domain"] for row in corpus}
    assert covered_domains == expected_domains

    for row in corpus:
        assert row["system_model"]["domain"]
        assert row["system_model"]["components"]
