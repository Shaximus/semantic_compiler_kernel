"""Tests for the V2.2 system model schema validator."""


def _valid_model():
    return {
        "domain": "computation",
        "decompression_version": "2.2.0-rc1",
        "components": [],
        "relationships": [],
        "universal_functional_graph": {"nodes": [], "edges": [], "coverage_ratio": 0.0},
        "pathology_profile": {"detected_pathologies": [], "medical_diagnoses": []},
        "reconstruction": {"missing_components": [], "completeness_scope": "unknown"},
        "advisor": {"diagnosis": [], "prescriptions": [], "architecture_improvements": [], "resilience_training": [], "prognosis": "stable"},
    }


def test_valid_system_model_passes():
    from expansion.schema.v2_2_system_model import validate_system_model
    model = {
        "domain": "computation",
        "decompression_version": "2.2.0-rc1",
        "components": [],
        "relationships": [],
        "universal_functional_graph": {"nodes": [], "edges": [], "coverage_ratio": 0.0},
        "pathology_profile": {"detected_pathologies": [], "medical_diagnoses": []},
        "reconstruction": {"missing_components": [], "completeness_scope": "unknown"},
        "advisor": {"diagnosis": [], "prescriptions": [], "architecture_improvements": [], "resilience_training": [], "prognosis": "stable"},
    }
    assert validate_system_model(model) == []


def test_missing_top_level_field_reported():
    from expansion.schema.v2_2_system_model import validate_system_model
    model = _valid_model()
    del model["advisor"]
    errors = validate_system_model(model)
    assert any("advisor" in e for e in errors)


def test_missing_nested_fields_reported():
    from expansion.schema.v2_2_system_model import validate_system_model
    model = _valid_model()
    del model["universal_functional_graph"]["coverage_ratio"]
    del model["pathology_profile"]["medical_diagnoses"]
    del model["reconstruction"]["completeness_scope"]
    del model["advisor"]["prognosis"]
    errors = validate_system_model(model)
    assert any("coverage_ratio" in e for e in errors)
    assert any("medical_diagnoses" in e for e in errors)
    assert any("completeness_scope" in e for e in errors)
    assert any("prognosis" in e for e in errors)


def test_schema_constant_matches_json_contract():
    import json
    from expansion.schema.v2_2_system_model import V2_2_SYSTEM_MODEL_SCHEMA, SCHEMA_PATH
    with open(SCHEMA_PATH) as f:
        on_disk = json.load(f)
    assert V2_2_SYSTEM_MODEL_SCHEMA == on_disk
    assert "universal_functional_graph" in V2_2_SYSTEM_MODEL_SCHEMA["required"]
