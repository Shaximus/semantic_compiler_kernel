"""Tests for advisor prescriptions and resilience training content."""

from semantic_compiler.expansion.advisor.improvements import generate_advice
from semantic_compiler.expansion.pathology.taxonomy import Pathology
from semantic_compiler.expansion.reconstruction.missing_components import MissingComponent


def test_prescriptions_generated_from_pathologies():
    pathologies = [Pathology("prompt_injection", "pathogen", "malicious instruction override", ["boundary_bypass"], 0.8, ["matched"])]
    advice = generate_advice({}, pathologies, [])
    assert advice["prescriptions"]
    p = advice["prescriptions"][0]
    assert p.kind == "prescription"
    assert "prompt_injection" in p.description
    assert "pathogen" in p.description


def test_prescriptions_use_template_failure_modes():
    pathologies = [Pathology("data_corruption", "inflammation", "desc", ["error_cascades"], 0.75, [])]
    failure_modes = [{
        "name": "data_corruption",
        "medical_map": "inflammation",
        "description": "degraded input causes downstream stress",
        "indicators": ["error_cascades", "validation_failures"],
    }]
    advice = generate_advice({}, pathologies, [], failure_modes=failure_modes)
    prescription = advice["prescriptions"][0]
    assert "error_cascades" in prescription.domain_specific_translation
    assert "validation_failures" in prescription.domain_specific_translation


def test_resilience_training_from_pathologies_and_missing():
    pathologies = [Pathology("prompt_injection", "pathogen", "desc", ["boundary_bypass"], 0.8, [])]
    missing = [MissingComponent("homeostasis_regulation", "inferred_by_analogy", "biology", 0.7, "inferred")]
    failure_modes = [{"name": "prompt_injection", "medical_map": "pathogen",
                      "description": "d", "indicators": ["boundary_bypass"]}]
    advice = generate_advice({}, pathologies, missing, failure_modes=failure_modes)
    kinds = {s.kind for s in advice["resilience_training"]}
    assert kinds == {"resilience_training"}
    descriptions = " ".join(s.description for s in advice["resilience_training"])
    assert "boundary_bypass" in descriptions  # vaccination drill
    assert "homeostasis_regulation" in descriptions  # restored-component drill


def test_no_pathologies_no_missing_still_valid_shape():
    advice = generate_advice({}, [], [])
    assert advice["prognosis"] == "stable"
    assert advice["prescriptions"] == []
    assert advice["resilience_training"] == []
