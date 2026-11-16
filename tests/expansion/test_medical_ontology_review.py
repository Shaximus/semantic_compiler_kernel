"""Regression and contract tests from the 2026-11 medical-ontology / decompression review."""

import pytest

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, _infer_medical_map, decompress
from semantic_compiler.expansion.advisor.improvements import (
    _MEDICAL_MAP_REMEDIATION,
    generate_advice,
    remediation_for,
)
from semantic_compiler.expansion.ontology.medical_ontology import (
    FUNCTIONAL_ROLE_TAGS,
    MEDICAL_ONTOLOGY,
    ONTOLOGY_ALIASES,
    classify_medical_map,
    get_concept,
    is_valid_medical_map,
    normalize_concept_name,
    resolve_concept,
)
from semantic_compiler.expansion.pathology.profiles import (
    CONFIDENCE_CIRCUMSTANTIAL,
    CONFIDENCE_DIRECT,
    detect_pathologies,
)
from semantic_compiler.expansion.pathology.taxonomy import Pathology
from semantic_compiler.expansion.reconstruction.missing_components import MissingComponent
from semantic_compiler.expansion.registry.loader import load_templates

TEMPLATES = load_templates()


class _Text:
    def __init__(self, text: str) -> None:
        self.raw_input = text


def test_concept_names_match_their_keys():
    for key, concept in MEDICAL_ONTOLOGY.items():
        assert concept.name == key
        assert concept.description and concept.cross_domain_meaning


def test_every_template_medical_map_is_a_canonical_concept():
    for domain, template in TEMPLATES.items():
        for item in [*template.failure_modes, *template.architecture_patterns]:
            assert is_valid_medical_map(item["medical_map"]), (domain, item["name"], item["medical_map"])


def test_aliases_point_at_canonical_concepts_and_never_shadow_them():
    for alias, target in ONTOLOGY_ALIASES.items():
        assert target in MEDICAL_ONTOLOGY
        assert alias not in MEDICAL_ONTOLOGY
    assert not (FUNCTIONAL_ROLE_TAGS & set(MEDICAL_ONTOLOGY))
    assert not (FUNCTIONAL_ROLE_TAGS & set(ONTOLOGY_ALIASES))


def test_lookup_is_tolerant_and_alias_aware_but_still_strict_for_unknowns():
    assert get_concept("Immune System").name == "immune_system"
    assert get_concept("immune-boundary").name == "immune_system"
    assert get_concept("homeostasis_regulation").name == "homeostasis"
    assert resolve_concept("nonsense") is None
    with pytest.raises(KeyError):
        get_concept("nonsense")
    assert normalize_concept_name("  Cross-Domain  Map ") == "cross_domain_map"


def test_is_valid_medical_map_is_exact_canonical_only():
    assert is_valid_medical_map("sepsis")
    assert not is_valid_medical_map("immune_boundary")
    assert not is_valid_medical_map("Sepsis")


def test_medical_map_classification_is_honest_about_role_tags():
    assert classify_medical_map("sepsis") == "ontology"
    assert classify_medical_map("Sepsis") == "ontology"
    assert classify_medical_map("immune_boundary") == "alias"
    assert classify_medical_map("processing_core") == "functional_role"
    assert classify_medical_map("unknown") == "unknown"


def test_component_extractor_only_emits_classifiable_maps_except_unknown():
    for template in TEMPLATES.values():
        for comp in template.components:
            assert classify_medical_map(_infer_medical_map(comp["name"])) in {
                "ontology", "alias", "functional_role", "unknown",
            }
    assert _infer_medical_map("diagnosis") == "diagnosis"
    assert _infer_medical_map("immune_system") == "immune_system"


def test_every_ontology_concept_has_specific_remediation():
    default = remediation_for("definitely_not_a_concept")
    for name in MEDICAL_ONTOLOGY:
        assert remediation_for(name) != default, name


def test_remediation_keys_are_resolvable():
    for key in _MEDICAL_MAP_REMEDIATION:
        assert classify_medical_map(key) in {"ontology", "alias", "functional_role"}, key


def test_remediation_lookup_is_tolerant_and_keeps_legacy_text():
    assert remediation_for("Immune Boundary") == "re-establish the boundary's filtering function"
    assert remediation_for("sepsis").startswith("break the cascade")
    assert remediation_for("processing_core") == "simplify and re-verify the core transform path"


def test_advisor_ontology_references_are_resolvable():
    pathologies = [Pathology("hospital_acquired_infection", "sepsis", "d", ["hygiene_breaches"], 0.75, [])]
    missing = [MissingComponent("defense_boundary", "template_expectation", "computation", 0.7, "inferred_by_analogy")]
    advice = generate_advice({}, pathologies, missing)
    for bucket in ("diagnosis", "prescriptions", "architecture_improvements", "resilience_training"):
        for suggestion in advice[bucket]:
            assert resolve_concept(suggestion.medical_ontology_reference) is not None, suggestion


def test_missing_defense_boundary_is_architecturally_critical():
    missing = [MissingComponent("defense_boundary", "template_expectation", "computation", 0.7, "inferred_by_analogy")]
    advice = generate_advice({}, [], missing)
    assert [s.description for s in advice["architecture_improvements"]] == ["Add missing defense_boundary"]
    unrelated = [MissingComponent("output_layer", "template_expectation", "computation", 0.7, "inferred_by_analogy")]
    assert generate_advice({}, [], unrelated)["architecture_improvements"] == []


def test_benign_generic_model_yields_no_pathologies_in_any_template():
    benign = {"components": [{"name": n} for n in ("service", "data", "the_team", "system", "of")], "relationships": []}
    offenders = {d: [p.name for p in detect_pathologies(benign, t)] for d, t in TEMPLATES.items()}
    assert {d: v for d, v in offenders.items() if v} == {}


def test_every_failure_mode_is_detectable_from_its_own_indicator():
    for domain, template in TEMPLATES.items():
        for fm in template.failure_modes:
            model = {"components": [{"name": fm["indicators"][0]}]}
            found = {p.name for p in detect_pathologies(model, template)}
            assert fm["name"] in found, (domain, fm["name"])


def test_confidence_reflects_evidence_strength():
    template = TEMPLATES["biology"]
    direct = detect_pathologies({"components": [{"name": "unregulated_mitosis"}]}, template)
    by_tag = detect_pathologies({"components": [{"name": "x", "medical_map": "cancer"}]}, template)
    weak = detect_pathologies({"components": [{"name": "growth", "medical_map": "growth_process"}]}, template)
    assert {p.confidence for p in direct if p.name == "cancer"} == {CONFIDENCE_DIRECT}
    assert {p.confidence for p in by_tag if p.name == "cancer"} == {CONFIDENCE_DIRECT}
    cancer = [p for p in weak if p.name == "cancer"]
    assert cancer and cancer[0].confidence == CONFIDENCE_CIRCUMSTANTIAL
    assert CONFIDENCE_CIRCUMSTANTIAL < CONFIDENCE_DIRECT
    assert any(e.startswith("basis:") for e in cancer[0].evidence)


@pytest.mark.parametrize(
    "text,domain",
    [
        ("The patient developed rapid onset sepsis after surgery.", "medical"),
        ("The hospital triage nurse reviewed the observer notes.", "medical"),
        ("An excellent leadership team ran the company.", "universal_generic"),
        ("The therapist reviewed the capital budget.", "universal_generic"),
        ("The doctor diagnosed the patient and prescribed treatment.", "medical"),
        ("The APIs and servers are down.", "computation"),
        ("A network firewall is like a cell membrane", "computation"),
        ("A corporate legal department is like an immune system", "corporate"),
        ("Cells and organisms metabolise.", "biology"),
    ],
)
def test_domain_inference_uses_whole_words(text, domain):
    assert _infer_domain(_Text(text)) == domain


def test_medical_text_reaches_the_medical_template():
    model = decompress(SemanticPacket(raw_input="The patient developed sepsis after surgery."))
    assert model["domain"] == "medical"
    assert {c["name"] for c in model["components"]} == {c["name"] for c in TEMPLATES["medical"].components}


def test_decompress_output_depends_on_domain_only_known_limitation():
    """Pins a known limitation: components come from the domain template, not the packet."""
    a = decompress(SemanticPacket(raw_input="The firewall blocks hostile packets at the network edge."))
    b = decompress(SemanticPacket(raw_input="Our server has no backups and nothing monitors the database."))
    assert a == b
    assert a["reconstruction"]["missing_components"] == []
