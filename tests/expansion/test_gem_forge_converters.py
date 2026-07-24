"""Tests for the gate-5 mechanic-family converters and corpus coverage."""

from semantic_compiler.expansion.gem_forge import load_pinned_corpus, translate_corpus, translate_gem
from semantic_compiler.expansion.gem_forge.models import PoeGem


def _translate_line(line: str):
    gem = PoeGem(gem_id="t", name="T", kind="support", wording=(line,), source="fixture")
    result = translate_gem(gem)
    return result.line_pairs[0]


def test_damage_family_converts_qualification_vocabulary():
    pair = _translate_line("20% increased Critical Strike Chance")
    assert pair.status == "CONVERTED"
    assert "Qualification Probability" in pair.converted
    pair = _translate_line("Supported Skills deal 30% increased Damage")
    assert "Output Effectiveness" in pair.converted


def test_stat_id_lines_route_exclusively_to_stat_converter():
    pair = _translate_line("skill_effect_duration_+%: 30")
    assert pair.status == "CONVERTED"  # not PARTIAL: exclusive routing
    assert "skill_effect_duration_+%" in pair.converted
    assert "state-retention duration" in pair.converted


def test_stat_id_family_mapping():
    pair = _translate_line("attack_speed_+%: 12")
    assert "execution cadence" in pair.converted
    assert "SCALE_CADENCE" in pair.primitives
    pair = _translate_line("minion_damage_+%: 40")
    assert "Output Effectiveness" in pair.converted


def test_boolean_flag_fallback_preserves_flag_verbatim():
    pair = _translate_line("base_deal_no_damage: 1")
    assert pair.status == "CONVERTED"
    assert "base_deal_no_damage" in pair.converted
    assert "no direct output effect" in pair.converted  # family pattern wins
    pair = _translate_line("console_skill_dont_chase: 1")
    assert pair.status == "CONVERTED"
    assert "console_skill_dont_chase" in pair.converted
    assert "= ON" in pair.converted  # generic flag fallback preserves verbatim


def test_minion_ailment_charge_families():
    pair = _translate_line("Minions deal 30% increased Damage")
    assert "proxy workers" in pair.converted
    assert "Output Effectiveness" in pair.converted
    pair = _translate_line("25% chance to Poison on Hit")
    assert "deferred residual effect" in pair.converted
    pair = _translate_line("10% chance to gain a Power Charge on Critical Strike")
    assert "qualification counters" in pair.converted


def test_annotation_and_unmapped_stay_honest():
    pair = _translate_line("[UNUSED] Not used")
    assert pair.status == "CONVERTED"
    assert "non-mechanical annotation" in pair.converted
    pair = _translate_line("completely_unknown_stat_xyz: 5")
    assert pair.status == "UNRESOLVED"


def test_pinned_corpus_coverage_regression():
    """Corpus-level coverage gate: converters must hold the measured floor."""
    gems = load_pinned_corpus()
    translations = translate_corpus(gems)
    total = converted = unresolved = 0
    for translation in translations:
        for pair in translation.line_pairs:
            total += 1
            converted += pair.status == "CONVERTED"
            unresolved += pair.status == "UNRESOLVED"
    assert total > 7000
    assert converted / total >= 0.70, f"CONVERTED coverage fell below floor: {converted}/{total}"
    assert unresolved / total <= 0.15, f"UNRESOLVED above ceiling: {unresolved}/{total}"
