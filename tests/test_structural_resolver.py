from semantic_compiler.translation.structural_resolver import (
    RelationPattern,
    StructuralRule,
    extract_evidence,
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
