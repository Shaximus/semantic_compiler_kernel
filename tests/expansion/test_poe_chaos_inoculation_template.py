"""Contract tests for the Chaos Inoculation domain template.

The template and its provenance note are research-derived from the attached
2026-11-06 review. These tests check that the attached template is present,
that routing reaches it, and that the guardrails stated in
docs/POE_CHAOS_INOCULATION_INVARIANTS.md hold. They do not independently
verify Path of Exile mechanics.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.decode_build_demo import POE_NATIVE_SPEC
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import (
    _DOMAIN_PATTERNS,
    _extract_components,
    _infer_domain,
    decompress,
)
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.registry import get_template, list_domains

POE = "poe_chaos_inoculation"
DOC = Path(__file__).resolve().parents[2] / "docs" / "POE_CHAOS_INOCULATION_INVARIANTS.md"
TAG = re.compile(r"\[([A-Z0-9-]+)\]")
TRAILING_TAGS = re.compile(r"(?:\[[A-Z0-9-]+\])+$")
# Router groups added after computation/biology/medical, plus later companion
# domains that are not part of the pre-review calibration set.
ROUTER_SPECIFIC = (
    "mobile_security",
    "android_connectivity",
    "bluetooth",
    "networking",
    "trust_chain",
    "poe_chaos_inoculation",
    "wireless_power",
    "epistemic_ledger_verification",
    "quota_bypass_mechanics",
    "input_semantic_adapter",
    "reward_hijacking",
)
SAMPLE_DOMAINS_OUTSIDE_LEGACY_CHECK = ROUTER_SPECIFIC + (
    "android_connectivity",
    "bluetooth",
)


def packet(text: str) -> SemanticPacket:
    return SemanticPacket(raw_input=text)


def test_poe_domain_is_registered():
    assert POE in list_domains()
    template = get_template(POE)
    assert template.domain == POE
    assert len(template.components) >= 8
    assert len(template.invariants) >= 10
    assert len(template.failure_modes) >= 6
    assert len(template.architecture_patterns) >= 5


def test_every_poe_invariant_ends_with_a_defined_source_tag():
    doc_text = DOC.read_text()
    seen: set[str] = set()
    for invariant in get_template(POE).invariants:
        assert TRAILING_TAGS.search(invariant), invariant
        tags = TAG.findall(invariant)
        assert tags, invariant
        seen.update(tags)
        for tag in tags:
            row = next((line for line in doc_text.splitlines() if line.startswith(f"| `{tag}` |")), None)
            assert row is not None, tag
            assert "http" in row
    defined = set(re.findall(r"^\| `([A-Z0-9-]+)` \|", doc_text, re.M))
    assert seen == defined


@pytest.mark.parametrize(
    "text, expected",
    [
        ("A Chaos Inoculation character has one life.", "poe_chaos_inoculation"),
        ("Energy shield absorbs damage before life.", "poe_chaos_inoculation"),
        ("Eldritch Battery moves energy shield onto mana.", "poe_chaos_inoculation"),
        ("Ghost Reaver turns life leech into shield.", "poe_chaos_inoculation"),
        ("An energy shield server is immune to chaos.", "poe_chaos_inoculation"),
    ],
)
def test_poe_vocabulary_routes_to_the_template(text, expected):
    assert _infer_domain(packet(text)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("A Path of Exile build with Ice Nova and Hatred.", "universal_generic"),
        ("The shield server handles requests.", "computation"),
        ("The energy shielding tape is installed.", "universal_generic"),
        ("The Android bootloader verifies vbmeta.", "mobile_security"),
    ],
)
def test_poe_keywords_do_not_capture_neighbouring_phrases(text, expected):
    assert _infer_domain(packet(text)) == expected


def test_gem_decode_poe_build_spec_still_routes_as_before():
    assert _infer_domain(packet(POE_NATIVE_SPEC)) == "universal_generic"


def test_new_vocabulary_does_not_move_preexisting_calibration_samples():
    from scripts.build_decompression_calibration import SAMPLES

    legacy = [(domain, pattern) for domain, pattern in _DOMAIN_PATTERNS if domain not in ROUTER_SPECIFIC]
    assert [domain for domain, _pattern in legacy] == ["computation", "biology", "medical"]

    def legacy_infer(text: str) -> str:
        lowered = text.lower()
        for domain, pattern in legacy:
            if pattern.search(lowered):
                return domain
        return "universal_generic"

    moved = [
        (text, legacy_infer(text), _infer_domain(packet(text)))
        for text, intended, _category in SAMPLES
        if intended not in SAMPLE_DOMAINS_OUTSIDE_LEGACY_CHECK
        and legacy_infer(text) != _infer_domain(packet(text))
    ]
    assert moved == []


def test_decompress_poe_uses_template_components():
    model = decompress(packet(
        "Chaos Inoculation sets life to one and leaves energy shield as the only buffer."
    ))
    assert model["domain"] == POE
    template = get_template(POE)
    declared = {component["name"]: component.get("medical_map") for component in template.components}
    by_name = {component["name"]: component for component in model["components"]}
    assert set(by_name) == set(declared)
    for name, concept in declared.items():
        expected = concept if concept in MEDICAL_ONTOLOGY else "unknown"
        assert by_name[name]["medical_map"] == expected, name
    assert all(
        diagnosis["confidence"] < 0.75
        for diagnosis in model["pathology_profile"]["medical_diagnoses"]
    )


def test_component_medical_map_falls_back_when_not_canonical():
    class FakeTemplate:
        components = [
            {"name": "input_layer", "function": "x", "criticality": "high", "medical_map": "not_a_concept"},
            {"name": "mystery", "function": "y", "criticality": "low", "medical_map": "quarantine"},
            {"name": "plain", "function": "z", "criticality": "low"},
        ]

    maps = {component["name"]: component["medical_map"] for component in _extract_components(packet("x"), FakeTemplate())}
    assert maps == {"input_layer": "immune_boundary", "mystery": "quarantine", "plain": "unknown"}


def test_poe_invariants_name_a_game_version():
    invariants = get_template(POE).invariants
    for invariant in invariants:
        assert re.search(r"PoE 1|PoE 2", invariant), invariant
    joined = " ".join(invariants)
    assert "PoE 1" in joined and "PoE 2" in joined


def test_poe_invariants_do_not_pin_patch_dependent_numbers():
    for invariant in get_template(POE).invariants:
        assert not re.search(r"\d\s*(%|seconds?\b)|per second", invariant), invariant


def test_poe_template_states_that_it_preserves_structure_not_numbers():
    description = get_template(POE).description
    assert "not their numbers" in description
    assert "designed game rules" in description


def test_poe_keystone_trade_and_buffer_are_present():
    template = get_template(POE)
    names = {component["name"] for component in template.components}
    assert {
        "chaos_inoculation_keystone",
        "lethal_pool",
        "energy_shield_pool",
        "chaos_immunity",
        "damage_ordering_rule",
        "recharge_regulator",
    } <= names
    joined = " ".join(template.invariants).lower()
    for phrase in (
        "maximum life becomes 1",
        "immune to chaos damage",
        "energy shield first",
        "interrupts it",
        "no effect on a chaos-immune character",
    ):
        assert phrase in joined, phrase


def test_poe_doc_states_the_guardrail_and_the_limits():
    text = DOC.read_text()
    for heading in (
        "## Structure versus literal mechanics (the guardrail)",
        "### What transfers to other systems, and what does not",
        "## What was not read or not established",
        "## Specification and derived properties (author reasoning, not sourced)",
    ):
        assert heading in text, heading
    assert "has not been reviewed by an expert player" in text


def test_poe_composite_failure_mode_names_its_parts():
    modes = {mode["name"]: mode for mode in get_template(POE).failure_modes}
    composite = modes["spike_after_chip"]
    assert "recharge_starvation" in composite["description"]
    assert "oversized_hit_overflow" in composite["description"]
    assert {"recharge_starvation", "oversized_hit_overflow"} <= set(modes)


def test_poe_refill_is_stated_in_terms_of_quiet_time():
    template = get_template(POE)
    regulator = next(component for component in template.components if component["name"] == "recharge_regulator")
    assert "quiet time" in regulator["function"] and "gaps between hits" in regulator["function"]
    patterns = {pattern["name"]: pattern["description"] for pattern in template.architecture_patterns}
    assert "quiet-time requirement" in patterns["convert_recovery_into_buffer"]
    assert "constant" in patterns["audit_predicates_on_fixed_value"]


def test_poe_relationships_and_concepts_stay_separated():
    template = get_template(POE)
    names = {component["name"] for component in template.components}
    assert len(names) == len(template.components)
    for edge in template.relationships:
        assert edge["from"] in names, edge
        assert edge["to"] in names, edge
    component_maps = {component.get("medical_map") for component in template.components}
    failure_maps = {mode.get("medical_map") for mode in template.failure_modes}
    assert component_maps.isdisjoint(failure_maps)
    assert all(concept in MEDICAL_ONTOLOGY for concept in component_maps if concept)
    assert all(concept in MEDICAL_ONTOLOGY for concept in failure_maps if concept)
