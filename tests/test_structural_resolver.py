from semantic_compiler.translation.structural_resolver import (
    RelationPattern,
    StructuralRule,
    extract_evidence,
    negated_rule_ids,
    resolve_rules,
)


def test_extracts_concepts_and_relations():
    aliases = {
        "gpu": ("gpu",),
        "weapon": ("weapon",),
        "vram": ("vram",),
        "reservation": ("mana reservation",),
    }
    evidence = extract_evidence("The GPU is the weapon; VRAM is mana reservation.", aliases)
    assert {"gpu", "weapon", "vram", "reservation"}.issubset(evidence.concepts)
    assert ("gpu", "equivalent_role", "weapon") in evidence.relations
    assert ("vram", "equivalent_role", "reservation") in evidence.relations


def test_relation_evidence_disambiguates_mapping():
    aliases = {"gpu": ("gpu",), "weapon": ("weapon",), "storage": ("storage",)}
    rules = (
        StructuralRule(
            "GPU_WEAPON",
            concepts_any=(frozenset({"gpu"}), frozenset({"weapon"})),
            relations_any=(RelationPattern("equivalent_role", frozenset({"gpu"}), frozenset({"weapon"})),),
            minimum_score=0.45,
        ),
        StructuralRule(
            "GPU_STORAGE",
            concepts_any=(frozenset({"gpu"}), frozenset({"storage"})),
            relations_any=(RelationPattern("equivalent_role", frozenset({"gpu"}), frozenset({"storage"})),),
            minimum_score=0.45,
        ),
    )
    _, matches = resolve_rules("The GPU is the weapon.", aliases, rules)
    assert [match.rule_id for match in matches] == ["GPU_WEAPON"]


def test_longest_alias_wins_over_contained_alias():
    aliases = {
        "weapon": ("weapon",),
        "weapon_slot": ("weapon slot", "weapon slots"),
        "pcie_slot": ("pcie slots",),
    }
    evidence = extract_evidence("PCIe slots are weapon slots.", aliases)
    assert ("pcie_slot", "equivalent_role", "weapon_slot") in evidence.relations
    assert not any(right == "weapon" for _, _, right in evidence.relations)


def test_equal_length_aliases_over_same_span_both_survive():
    aliases = {"a": ("mtp",), "b": ("mtp",), "c": ("support gem",)}
    evidence = extract_evidence("MTP is a support gem.", aliases)
    assert ("a", "equivalent_role", "c") in evidence.relations
    assert ("b", "equivalent_role", "c") in evidence.relations


def _gpu_weapon_rule():
    return StructuralRule(
        "GPU_WEAPON",
        concepts_any=(frozenset({"gpu"}), frozenset({"weapon"})),
        relations_any=(RelationPattern("equivalent_role", frozenset({"gpu"}), frozenset({"weapon"})),),
        minimum_score=0.45,
    )


def test_negated_relations_never_count_as_support():
    aliases = {"gpu": ("gpu",), "weapon": ("weapon",)}
    rule = _gpu_weapon_rule()
    for text in ("The GPU is not the weapon.", "The GPU isn't the weapon.", "The GPU is never the weapon."):
        evidence, matches = resolve_rules(text, aliases, (rule,))
        assert matches == [], text
        assert ("gpu", "not_equivalent_role", "weapon") in evidence.relations, text
        assert negated_rule_ids((rule,), evidence) == {"GPU_WEAPON"}, text

    evidence, matches = resolve_rules("The GPU is the weapon.", aliases, (rule,))
    assert [match.rule_id for match in matches] == ["GPU_WEAPON"]
    assert negated_rule_ids((rule,), evidence) == frozenset()


def test_relation_kind_must_match_exactly():
    aliases = {"llm": ("llm",), "skill": ("active skill",)}
    rule = StructuralRule(
        "LLM_SKILL",
        concepts_any=(frozenset({"llm"}), frozenset({"skill"})),
        relations_any=(RelationPattern("equivalent_role", frozenset({"llm"}), frozenset({"skill"})),),
        minimum_score=0.45,
    )
    _, matches = resolve_rules("The LLM uses an active skill.", aliases, (rule,))
    assert matches == []


def test_any_relation_pattern_is_sufficient():
    aliases = {"vram": ("vram",), "reservation": ("reservation",), "llm": ("llm",)}
    rule = StructuralRule(
        "R",
        concepts_any=(frozenset({"vram"}), frozenset({"reservation"})),
        relations_any=(
            RelationPattern("equivalent_role", frozenset({"vram"}), frozenset({"reservation"})),
            RelationPattern("consumes", frozenset({"llm"}), frozenset({"vram"})),
        ),
        minimum_score=0.55,
    )
    _, matches = resolve_rules("VRAM is reservation.", aliases, (rule,))
    assert [match.rule_id for match in matches] == ["R"]
