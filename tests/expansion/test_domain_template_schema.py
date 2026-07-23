def test_valid_template_passes():
    from semantic_compiler.expansion.schema import validate_domain_template
    template = {
        "domain": "computation",
        "version": 1.0,
        "description": "test",
        "components": [{"name": "a", "function": "b", "criticality": "high"}],
        "relationships": [],
        "invariants": [],
        "failure_modes": [{"name": "x", "medical_map": "pathogen", "description": "d", "indicators": []}],
        "architecture_patterns": [],
    }
    assert validate_domain_template(template) == []
