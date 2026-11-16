"""Regression tests for bug fixes identified in codebase audit."""
from __future__ import annotations

from types import SimpleNamespace

from semantic_compiler.expansion.consciousness import (
    detect_category_error,
    detect_hotfix,
    evaluate_alignment,
)
from semantic_compiler.expansion.corpus import chunk_text, compile_corpus
from semantic_compiler.expansion.gear_value_optimizer import (
    GearSlot,
    UpgradeCandidate,
    ValueConstraints,
    rank_upgrades,
)
from semantic_compiler.expansion.gem_forge.translator import PoeGem, translate_gem
from semantic_compiler.expansion.isomorphism.overlay import build_functional_graph
from semantic_compiler.modes.coherence import check_alignment_signal
from semantic_compiler.modes.defense_pathology import build_micro_packet
from semantic_compiler.modes.reality_orientation import detect_avoidance_pattern
from semantic_compiler.translation.fractal import identify_missing_departments


def test_gem_charges_line_converts_without_duplicate_partial():
    gem = PoeGem(
        gem_id="audit_charges",
        name="Charge Test Support",
        kind="support",
        tags=("Support",),
        description="Charge generation support.",
        wording=("20% chance to gain a Power Charge on Kill",),
        quality_wording=(),
    )
    translation = translate_gem(gem)
    assert len(translation.line_pairs) == 1
    assert translation.line_pairs[0].status == "CONVERTED"
    assert translation.line_pairs[0].confidence == 0.9


def test_rank_upgrades_ranks_zero_score_ahead_of_negative():
    constraints = ValueConstraints(require_positive_throughput_gain=False)
    zero_cand = UpgradeCandidate(
        name="zero_avail",
        slot=GearSlot.WEAPON_PRIMARY,
        workload_id="w1",
        baseline_build_id="b1",
        landed_cost_cad=150.0,
        baseline_accepted_tokens_per_s=100.0,
        candidate_accepted_tokens_per_s=110.0,
        baseline_quality_score=0.9,
        candidate_quality_score=0.9,
        candidate_availability=0.0,
    )
    neg_cand = UpgradeCandidate(
        name="negative_gain",
        slot=GearSlot.WEAPON_PRIMARY,
        workload_id="w1",
        baseline_build_id="b1",
        landed_cost_cad=150.0,
        baseline_accepted_tokens_per_s=100.0,
        candidate_accepted_tokens_per_s=95.0,
        baseline_quality_score=0.9,
        candidate_quality_score=0.9,
        candidate_availability=1.0,
    )
    ranked = rank_upgrades([neg_cand, zero_cand], constraints)
    assert [r.candidate.name for r in ranked] == ["zero_avail", "negative_gain"]


def test_chunk_text_attaches_consecutive_markdown_headings_to_body():
    chunks = chunk_text("# Heading 1\n\n# Heading 2\n\nBody paragraph", max_chars=50)
    assert len(chunks) == 1
    assert chunks[0].text == "# Heading 1\n\n# Heading 2\n\nBody paragraph"


def test_compile_corpus_distinct_negative_test_ids_and_timezone_bounds():
    doc1 = (
        "d1",
        "The server firewall enforces packet filtering.",
        {"captured_at": "2026-11-15T05:00:00+02:00", "evidence_tier": "PRIMARY_RECORD"},
    )
    doc2 = (
        "d2",
        "The patient symptoms indicate inflammation.",
        {"captured_at": "2026-11-15T04:00:00Z", "evidence_tier": "PRIMARY_RECORD"},
    )
    report = compile_corpus([doc1, doc2])
    reg = report["invariant_registry"]
    nt_ids = [
        d["test_id"]
        for entry in reg
        for d in entry["disconfirmations"]
    ]
    assert len(nt_ids) == len(set(nt_ids))


def test_build_functional_graph_caps_coverage_with_duplicate_template_components():
    tmpl = SimpleNamespace(
        components=[
            {"name": "firewall"},
            {"name": "firewall"},
        ]
    )
    graph = build_functional_graph(
        {
            "components": [{"name": "firewall", "medical_map": "immune_system"}],
            "relationships": [],
        },
        tmpl,
    )
    assert graph.coverage_ratio <= 1.0


def test_check_alignment_signal_handles_negative_input():
    res = check_alignment_signal(-0.5, 0.5, 0.5)
    assert isinstance(res["composite_alignment"], float)
    assert res["signal_detected"] is False


def test_consciousness_and_reality_none_content_and_hotfix_none_keys():
    cat = detect_category_error("", [{"content": None, "claim_type": "STRUCTURAL_MAPPING"}])
    assert cat["status"] == "CLEAN"

    avoid = detect_avoidance_pattern(
        [{"content": None, "claim_type": "plan"}],
        ["budget limit"],
    )
    assert avoid == []

    hotfix = detect_hotfix({"a": 1}, {"a": 1, "b": None})
    assert hotfix["hotfix_detected"] is True
    assert hotfix["change_count"] == 1

    ind = ["friction"]
    align = evaluate_alignment("ok", 0.8, 0.8, resistance_indicators=ind)
    align["resistance_indicators"].append("mutated")
    assert len(ind) == 1


def test_defense_pathology_non_numeric_and_fractal_non_string():
    pkt = build_micro_packet("vram", 16, "unknown")
    assert pkt["deficit"] == "N/A"
    assert pkt["status"] == "BLOCKED"

    pkt_bool = build_micro_packet("vram", True, 1)
    assert pkt_bool["deficit"] == "N/A"
    assert pkt_bool["status"] == "BLOCKED"

    findings = identify_missing_departments(
        {"present_functions": [123, {"name": "firewall"}, "SECURITY"]},
        scale="computational",
    )
    assert isinstance(findings, list)


def test_avoidance_emits_at_most_one_magical_planning_per_claim():
    patterns = detect_avoidance_pattern(
        [{"content": "expand compute budget capacity now", "claim_type": "plan"}],
        ["compute constraint", "budget limit"],
    )
    magical = [p for p in patterns if p.startswith("MAGICAL_PLANNING:")]
    assert len(magical) == 1
