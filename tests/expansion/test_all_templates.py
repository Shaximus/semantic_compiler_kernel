def test_all_templates_load_and_validate():
    from expansion.registry import list_domains
    domains = list_domains()
    expected = {"corporate", "government", "law", "medical", "construction", "biology", "ecology", "environmental", "computation", "organizational", "economic", "reflexion", "social", "evolutionary", "informational", "military", "finance_economics", "psychology", "universal_generic"}
    assert set(domains) == expected
