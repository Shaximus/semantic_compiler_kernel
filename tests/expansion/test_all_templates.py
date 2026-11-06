def test_all_templates_load_and_validate():
    from semantic_compiler.expansion.registry import list_domains
    domains = list_domains()
    expected = {"corporate", "government", "law", "medical", "construction", "biology", "ecology", "environmental", "computation", "organizational", "economic", "reflexion", "social", "evolutionary", "informational", "military", "finance_economics", "psychology", "mobile_security", "networking", "trust_chain", "universal_generic"}
    assert set(domains) == expected
