"""Tests for the gem mapper hardening modules (swarm/gem-mapper-hardening).

Covers: multi-source provenance + wording diffs (side-by-side, never
averaged), the named converter-family registry (no generic buckets), and
composite synthesis attribution (no single-primitive composites).
"""
from __future__ import annotations

import json

import pytest

from semantic_compiler.expansion.gem_forge.composite_attribution import (
    attribute_composite,
    floor_violations,
)
from semantic_compiler.expansion.gem_forge.converter_families import (
    UNCLASSIFIED,
    UnmatchedLine,
    build_family_registry,
    classify_line,
)
from semantic_compiler.expansion.gem_forge.corpus import CorpusPinError
from semantic_compiler.expansion.gem_forge.forge import forge_component
from semantic_compiler.expansion.gem_forge.models import PoeGem, SoftwareComponent
from semantic_compiler.expansion.gem_forge.multi_source import (
    SourceProvenance,
    ProvenancedSource,
    merge_sources,
    provenance_report,
    wording_diff_records,
    load_provenanced_source,
)
from semantic_compiler.expansion.gem_forge.translator import translate_corpus, translate_gem


def _gem(gem_id, name, wording, quality=(), kind="active"):
    return PoeGem(gem_id=gem_id, name=name, kind=kind, wording=tuple(wording), quality_wording=tuple(quality))


def _source(source_id, gems, sha="0" * 64):
    return ProvenancedSource(
        provenance=SourceProvenance(
            source_id=source_id,
            data_era="test-era",
            origin="test-fixture",
            retrieved_at="2026-07-24T00:00:00+00:00",
            sha256=sha,
            synthetic=True,
        ),
        gems=tuple(gems),
    )


# --- multi-source ----------------------------------------------------------


def test_merge_flags_value_only_and_wording_change():
    primary = _source("repoe-pinned", [_gem("G1", "Gem One", [
        "Deals 10 to 20 Physical Damage",
        "Maximum 3 Summoned Sentinels",
        "Base duration is 4 seconds",
    ])])
    secondary = _source("repoe-fork", [_gem("G1", "Gem One", [
        "Deals 15 to 25 Physical Damage",          # VALUE_ONLY
        "Maximum 3 Summoned Sentinels",            # exact match
        "Base duration is 4.00 seconds",           # VALUE_ONLY
        "25% chance to Summon on Hit",             # LINE_ADDED
    ])])
    result = merge_sources((primary, secondary))
    merged = result.gems[0]
    assert not merged.single_source
    kinds = {d.classification for d in merged.wording_diffs}
    assert "VALUE_ONLY" in kinds
    assert "LINE_ADDED" in kinds
    # side-by-side: modified pairs keep BOTH wordings verbatim
    pair = next(d for d in merged.wording_diffs if d.kind == "MODIFIED_PAIR")
    assert pair.primary_line is not None and pair.secondary_line is not None
    assert pair.primary_line != pair.secondary_line


def test_merge_marks_single_source_gems():
    primary = _source("repoe-pinned", [_gem("G1", "Gem One", ["Deals 10 Damage"])])
    secondary = _source("repoe-fork", [_gem("G2", "Gem Two", ["Deals 20 Damage"])])
    result = merge_sources((primary, secondary))
    assert all(g.single_source for g in result.gems)
    report = provenance_report(result)
    assert report["single_source_gem_counts"] == {"repoe-pinned": 1, "repoe-fork": 1}
    assert report["shared_gem_count"] == 0


def test_merge_missing_from_primary_diffs_against_earliest_source():
    s1 = _source("a", [_gem("G1", "One", ["x"])])
    s2 = _source("b", [_gem("G2", "Two", ["alpha line"])])
    s3 = _source("c", [_gem("G2", "Two", ["alpha line", "beta line"])])
    result = merge_sources((s1, s2, s3))
    g2 = next(g for g in result.gems if g.gem_id == "G2")
    assert g2.sources == ("b", "c")
    assert any(d.classification == "LINE_ADDED" for d in g2.wording_diffs)


def test_merge_is_deterministic():
    def build():
        a = _source("a", [_gem("G1", "One", ["Deals 10 Damage", "extra line", "shared"])])
        b = _source("b", [_gem("G1", "One", ["Deals 12 Damage", "shared", "fork only"])])
        return json.dumps([r for r in wording_diff_records(merge_sources((a, b)))], sort_keys=True)

    assert build() == build()


def test_load_provenanced_source_verifies_hash(tmp_path):
    snapshot = tmp_path / "snap.json"
    snapshot.write_text(json.dumps({"gems": [{"id": "G1", "name": "One", "wording": ["x"]}]}))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"snapshot_sha256": "f" * 64, "source": {}}))
    with pytest.raises(CorpusPinError):
        load_provenanced_source(snapshot, manifest, source_id="bad")


# --- converter families ----------------------------------------------------


def test_every_unclassified_line_aborts_registry():
    entries = [UnmatchedLine("G1", "One", "xyzzy-no-family-can-match-this-qqq", "UNRESOLVED")]
    with pytest.raises(ValueError):
        build_family_registry(entries)


def test_named_families_cover_founders_examples():
    assert classify_line("enemy_additional_critical_strike_multiplier_against_self: 41") == (
        "CONVERTER_FAMILY:curse_and_target_vulnerability_payload"
    )
    assert classify_line("glacial_hammer_shatter_frozen_enemies_at_33%_life: 1") == (
        "CONVERTER_FAMILY:ailment_threshold_scaling"
    )
    assert classify_line("Supported Skills have 0.5% increased Damage for each 200 Mana you have Spent Recently") == (
        "CONVERTER_FAMILY:per_recent_action_window"
    )
    assert classify_line("Supported Skills gain a Vaal Soul on Hit\nYou can only generate a Soul every 0.1 seconds") == (
        "CONVERTER_FAMILY:periodic_pulse_activation"
    )
    assert classify_line("Vaal Skills have 20% chance to regain consumed Souls when used") == (
        "CONVERTER_FAMILY:expendable_consumable_resource"
    )


def test_registry_examples_have_at_least_three_lines():
    entries = [
        UnmatchedLine("G1", "One", "1.0% chance to Impale Enemies on Hit", "UNRESOLVED"),
        UnmatchedLine("G2", "Two", "20% chance to Impale Enemies on Hit", "PARTIAL"),
        UnmatchedLine("G3", "Three", "60% chance to Impale Enemies on Hit", "UNRESOLVED"),
    ]
    registry = build_family_registry(entries)
    (family,) = registry["families"]
    assert family["family"] == "CONVERTER_FAMILY:impale_application_and_effect"
    assert len(family["example_unmatched_lines"]) >= 3
    assert family["gem_coverage"] == 3
    assert family["proposed_template"]


def test_pinned_corpus_unmatched_lines_fully_classified():
    """The whole pinned corpus: every PARTIAL/UNRESOLVED line gets a named family."""
    from semantic_compiler.expansion.gem_forge import load_pinned_corpus

    translations = translate_corpus(load_pinned_corpus())
    entries = [
        UnmatchedLine(t.gem_id, t.poe_name, pair.source, pair.status)
        for t in translations
        for pair in t.line_pairs
        if pair.status in ("PARTIAL", "UNRESOLVED")
    ]
    assert entries
    assert all(classify_line(e.line) != UNCLASSIFIED for e in entries)
    registry = build_family_registry(entries)
    assert registry["family_count"] >= 20
    assert all(len(f["example_unmatched_lines"]) >= 3 for f in registry["families"])


# --- composite attribution -------------------------------------------------


def test_composite_attribution_is_line_by_line():
    gems = (
        _gem("GMP", "Greater Multiple Projectiles Support", [
            "Supported Skills fire 4 additional Projectiles",
            "Supported Skills deal 25% less Projectile Damage",
        ], kind="support"),
        _gem("ECHO", "Spell Echo Support", [
            "Supported Skills Repeat an additional time",
        ], kind="support"),
    )
    translations = translate_corpus(gems)
    component = SoftwareComponent(
        name="Speculative Fan-Out Repeater",
        description=(
            "Predicts additional future token positions per decoding step and "
            "repeats execution; reduces per-candidate effectiveness."
        ),
        traits=("EMIT_ADDITIONAL_CANDIDATES", "REPEAT_EXECUTION"),
    )
    result = forge_component(component, translations)
    attribution = attribute_composite(result, translations)
    record = attribution.to_dict()
    assert record["attributed_primitive_count"] >= 2
    for primitive, contributors in record["primitive_attributions"].items():
        assert contributors, primitive
        line_contributors = [c for c in contributors if c["attribution_level"] == "line"]
        assert line_contributors, primitive
        for c in line_contributors:
            assert c["gem_id"] and c["source_line"]
    assert not floor_violations([attribution])


def test_single_primitive_composite_demotes_to_novel():
    """Floor holds: a synthesis backed by one primitive cannot stay COMPOSITE."""
    gems = (
        _gem("A", "Chain Support", ["Supported Skills chain 2 additional times"], kind="support"),
        _gem("B", "Fork Support", ["Supported Skills fork into 2 projectiles"], kind="support"),
    )
    translations = translate_corpus(gems)
    # Component with wording evidence for both gems but only ONE shared primitive.
    component = SoftwareComponent(
        name="Chain Fork Router",
        description="chain fork route onward eligible downstream tasks trajectories",
        traits=("CHAIN_TO_NEW_TARGET",),
    )
    result = forge_component(component, translations)
    attribution = attribute_composite(result, translations)
    if result.composite_gem.composition in ("COMPOSITE", "SINGLE_SOURCE") and attribution.original_composition != "NOVEL":
        # If the matcher floor passed on evidence tokens with <2 primitives,
        # the attribution layer must have demoted it.
        if attribution.attributed_primitive_count() < 2:
            assert attribution.demoted_single_primitive
            assert attribution.composition == "NOVEL"
    assert floor_violations([attribution]) == []


def test_no_single_primitive_composites_across_component_sweep():
    """Sweep: no forge output over this corpus slice is a single-primitive composite."""
    gems = (
        _gem("GMP", "Greater Multiple Projectiles Support", [
            "Supported Skills fire 4 additional Projectiles",
            "Supported Skills deal 25% less Projectile Damage",
        ], kind="support"),
        _gem("ECHO", "Spell Echo Support", ["Supported Skills Repeat an additional time"], kind="support"),
        _gem("CRIT", "Cast On Critical Strike Support", [
            "Supported Skills trigger verified payload when you deal a Critical Strike",
        ], kind="support"),
    )
    translations = translate_corpus(gems)
    components = [
        SoftwareComponent(name="MTP Fan-Out", description="multiple projectile branch fan out", traits=("EMIT_ADDITIONAL_CANDIDATES",)),
        SoftwareComponent(name="Echo Repeater", description="repeat spell echo re-execute", traits=("REPEAT_EXECUTION",)),
        SoftwareComponent(name="Crit Trigger", description="cast on crit acceptance gate qualified proposal", traits=("TRIGGER_ON_QUALIFICATION",)),
        SoftwareComponent(name="Novel Qbert", description="qqq zzz nothing matches", traits=("RECORD_RECEIPT",)),
    ]
    attributions = [attribute_composite(forge_component(c, translations), translations) for c in components]
    assert floor_violations(attributions) == []
