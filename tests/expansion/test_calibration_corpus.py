"""Tests for the V2.2 decompression calibration corpus builder (Task 11)."""
from collections import Counter

from scripts.build_decompression_calibration import build_corpus
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain
from semantic_compiler.expansion.registry import list_domains
from semantic_compiler.expansion.registry.loader import TEMPLATE_DIR


def test_calibration_corpus_builds():
    corpus = build_corpus()
    assert len(corpus) >= 80
    for row in corpus[:5]:
        assert "system_model" in row
        assert "sample_kind" in row


def test_calibration_corpus_category_coverage():
    """Five samples on every non-generic registry domain, across 8 categories."""
    corpus = build_corpus()

    registered = set(list_domains())
    on_disk = {path.stem for path in TEMPLATE_DIR.glob("*.yaml")}
    assert registered == on_disk
    assert "universal_generic" in registered
    expected_domains = registered - {"universal_generic"}

    domain_counts = Counter(row["domain"] for row in corpus)
    assert set(domain_counts) == expected_domains
    assert all(count == 5 for count in domain_counts.values())
    assert len(corpus) == 5 * len(expected_domains)

    categories = Counter(row["calibration_category"] for row in corpus)
    assert len(categories) == 8
    assert all(count >= 10 for count in categories.values())

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
