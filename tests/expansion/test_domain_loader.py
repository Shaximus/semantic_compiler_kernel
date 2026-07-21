def test_loader_loads_computation_template():
    from expansion.registry.loader import load_templates
    templates = load_templates()
    assert "computation" in templates
    assert templates["computation"].domain == "computation"
    assert len(templates["computation"].components) > 0
