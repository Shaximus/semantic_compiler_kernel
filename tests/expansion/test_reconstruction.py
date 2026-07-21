def test_reconstruct_missing_components():
    from expansion.reconstruction.missing_components import reconstruct_missing
    from expansion.registry import get_template
    model = {"components": [{"name": "input_layer"}], "relationships": []}
    template = get_template("computation")
    missing = reconstruct_missing(model, template)
    assert len(missing) > 0
    assert any(m.function == "processing_core" for m in missing)


def test_reconstruct_missing_nothing_when_complete():
    from expansion.reconstruction.missing_components import reconstruct_missing
    from expansion.registry import get_template
    template = get_template("computation")
    model = {
        "components": [{"name": c["name"]} for c in template.components],
        "relationships": [],
    }
    assert reconstruct_missing(model, template) == []


def test_assess_completeness():
    from expansion.reconstruction.completeness import assess_completeness
    from expansion.registry import get_template
    template = get_template("computation")
    assert assess_completeness(
        {"components": [], "claims_complete_system": True}, template
    ) == "whole_system_claimed"
    assert assess_completeness({"components": [{"name": "input_layer"}]}, template) == "fragmentary"
    assert assess_completeness(
        {"components": [{"name": "input_layer"}, {"name": "output_layer"}]}, template
    ) == "unknown"
