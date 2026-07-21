def test_build_functional_graph():
    from expansion.isomorphism.overlay import build_functional_graph
    from expansion.registry import get_template
    model = {
        "components": [
            {"name": "api_gateway", "medical_map": "immune_boundary"},
            {"name": "rate_limiter", "medical_map": "homeostasis_regulation"},
        ],
        "relationships": [{"from": "api_gateway", "to": "rate_limiter", "type": "guards"}],
    }
    template = get_template("computation")
    graph = build_functional_graph(model, template)
    assert "immune_boundary" in graph.nodes
    assert "homeostasis_regulation" in graph.nodes
    assert graph.coverage_ratio > 0
