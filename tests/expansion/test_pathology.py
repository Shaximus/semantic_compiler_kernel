def test_detect_cancer_pattern():
    from expansion.pathology.profiles import detect_pathologies
    from expansion.registry import get_template
    model = {"components": [{"name": "growth", "medical_map": "growth_process"}], "relationships": []}
    template = get_template("biology")
    pathologies = detect_pathologies(model, template)
    assert any(p.medical_map == "cancer" for p in pathologies)
