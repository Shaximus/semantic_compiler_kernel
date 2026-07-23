def test_loader_loads_computation_template():
    from semantic_compiler.expansion.registry.loader import load_templates
    templates = load_templates()
    assert "computation" in templates
    assert templates["computation"].domain == "computation"
    assert len(templates["computation"].components) > 0

def test_get_template_falls_back_to_universal_generic():
    from semantic_compiler.expansion.registry.index import get_template
    assert get_template("nonexistent_domain").domain == "universal_generic"

def test_load_templates_raises_on_invalid(tmp_path):
    import pytest
    from semantic_compiler.expansion.registry.loader import load_templates
    (tmp_path / "broken.yaml").write_text("domain: broken\nversion: 1.0\n")
    with pytest.raises(ValueError):
        load_templates(tmp_path)

def test_list_domains():
    from semantic_compiler.expansion.registry.index import list_domains
    domains = list_domains()
    assert "computation" in domains
    assert "biology" in domains
    assert "universal_generic" in domains
