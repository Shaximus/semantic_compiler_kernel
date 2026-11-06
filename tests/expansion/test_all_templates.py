def test_all_templates_load_and_validate():
    from semantic_compiler.expansion.registry import list_domains
    domains = list_domains()
    expected = {
        "android_connectivity", "biology", "bluetooth", "computation", "construction",
        "corporate", "ecology", "economic", "environmental", "evolutionary",
        "finance_economics", "government", "informational", "law", "medical",
        "military", "mobile_security", "networking", "organizational",
        "poe_chaos_inoculation", "psychology", "reflexion", "social", "trust_chain",
        "universal_generic",
    }
    assert set(domains) == expected
