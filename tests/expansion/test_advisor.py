def test_generate_advice_for_cancer():
    from semantic_compiler.expansion.advisor.improvements import generate_advice
    from semantic_compiler.expansion.pathology.taxonomy import Pathology
    from semantic_compiler.expansion.reconstruction.missing_components import MissingComponent
    model = {"components": [{"name": "growth"}], "relationships": []}
    pathologies = [Pathology("uncontrolled_growth", "cancer", "desc", [], 0.8, [])]
    missing = [MissingComponent("homeostasis_regulation", "template", "biology", 0.7, "inferred")]
    advice = generate_advice(model, pathologies, missing)
    assert advice["diagnosis"]
    assert len(advice["architecture_improvements"]) > 0
