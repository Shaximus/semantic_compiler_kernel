"""Resolve Path of Exile buildcraft shorthand into typed compute mappings.

Resolution is relation-aware: ontology concepts are extracted first, then mapping
rules are scored against concept coverage and relationship evidence. This avoids
one-off dense-signal recovery while preserving deterministic, auditable behavior.
"""
from __future__ import annotations

from semantic_compiler.registry.buildcraft import BUILDCRAFT_MAPPINGS, BuildcraftMapping
from semantic_compiler.translation.structural_resolver import (
    RelationPattern,
    StructuralRule,
    resolve_rules,
)


ALIASES = {
    "pcie_slot": ("pcie", "pcie slot", "accelerator slot"),
    "weapon_slot": ("weapon slot", "weapon sockets", "weapon links"),
    "gpu": ("gpu", "gpus", "accelerator", "graphics card"),
    "weapon": ("weapon", "equipped weapon"),
    "cpu_socket": ("cpu socket", "cpu slot", "host compute position"),
    "armour_slot": ("armor slot", "armour slot", "body armor slot", "body armour slot"),
    "cpu": ("cpu", "cpus", "processor", "host compute"),
    "armour": ("armor", "armour", "body armor", "body armour"),
    "integration_capacity": ("linked sockets", "gem slots", "six link", "6 link", "ten link", "10 link"),
    "llm": ("llm", "model", "primary application", "active workload"),
    "active_skill": ("active skill", "active skill gem", "skill gem"),
    "support_runtime": ("support gem", "mtp", "drafter", "speculative drafter", "cache layer", "vllm", "sglang", "inference framework"),
    "compatibility": ("cuda", "pytorch", "driver", "drivers", "abi", "runtime compatibility", "gem tags"),
    "vram": ("vram", "accelerator memory", "gpu memory"),
    "reservation": ("mana reservation", "reserved mana", "resource reservation", "allocation"),
    "repository": ("repo", "repository", "package", "docker profile"),
    "complete_build": ("complete build", "compute build", "architecture build", "path of building", "reflexion of building"),
    "delivery_proliferation": ("too many builds", "twenty viable builds", "20 viable builds", "before reaching maps", "league starter reaches maps"),
    "premium_accelerator": ("rtx pro 6000", "blackwell 96 gb"),
    "mirror_item": ("mirror-tier 10 link bow", "mirror tier ten link bow", "10 link bow", "ten link bow"),
}


RULES = (
    StructuralRule("BUILD_001", concepts_any=(frozenset({"complete_build"}),), minimum_score=0.25),
    StructuralRule("BUILD_002", concepts_any=(frozenset({"pcie_slot"}), frozenset({"weapon_slot"})), relations_any=(RelationPattern("equivalent_role", frozenset({"pcie_slot"}), frozenset({"weapon_slot"})),), minimum_score=0.45),
    StructuralRule("BUILD_003", concepts_any=(frozenset({"cpu_socket"}), frozenset({"armour_slot"})), relations_any=(RelationPattern("equivalent_role", frozenset({"cpu_socket"}), frozenset({"armour_slot"})),), minimum_score=0.45),
    StructuralRule("BUILD_004", concepts_any=(frozenset({"gpu"}), frozenset({"weapon"})), relations_any=(RelationPattern("equivalent_role", frozenset({"gpu"}), frozenset({"weapon"})),), minimum_score=0.45),
    StructuralRule("BUILD_005", concepts_any=(frozenset({"cpu"}), frozenset({"armour"})), relations_any=(RelationPattern("equivalent_role", frozenset({"cpu"}), frozenset({"armour"})),), minimum_score=0.45),
    StructuralRule("BUILD_006", concepts_any=(frozenset({"integration_capacity"}),), minimum_score=0.25),
    StructuralRule("BUILD_007", concepts_any=(frozenset({"llm"}), frozenset({"active_skill"})), relations_any=(RelationPattern("equivalent_role", frozenset({"llm"}), frozenset({"active_skill"})),), minimum_score=0.45),
    StructuralRule("BUILD_008", concepts_any=(frozenset({"support_runtime"}),), minimum_score=0.25),
    StructuralRule("BUILD_009", concepts_any=(frozenset({"compatibility"}),), minimum_score=0.25),
    StructuralRule("BUILD_010", concepts_any=(frozenset({"vram"}), frozenset({"reservation"})), relations_any=(RelationPattern("equivalent_role", frozenset({"vram"}), frozenset({"reservation"})), RelationPattern("consumes", frozenset({"llm", "support_runtime"}), frozenset({"vram"}))), minimum_score=0.45),
    StructuralRule("BUILD_011", concepts_any=(frozenset({"repository"}),), minimum_score=0.25),
    StructuralRule("BUILD_012", concepts_any=(frozenset({"complete_build"}),), minimum_score=0.25),
    StructuralRule("BUILD_013", concepts_any=(frozenset({"delivery_proliferation"}),), minimum_score=0.25),
    StructuralRule("BUILD_014", concepts_any=(frozenset({"premium_accelerator"}), frozenset({"mirror_item"})), relations_any=(RelationPattern("equivalent_role", frozenset({"premium_accelerator"}), frozenset({"mirror_item"})),), minimum_score=0.45),
)


def resolve_buildcraft_entries(text: str) -> list[BuildcraftMapping]:
    """Return buildcraft mappings supported by concept and relation evidence."""
    _, matches = resolve_rules(text, ALIASES, RULES)
    by_id = {mapping.mapping_id: mapping for mapping in BUILDCRAFT_MAPPINGS}
    return [by_id[match.rule_id] for match in matches]


def resolve_buildcraft_mappings(text: str) -> list[dict[str, object]]:
    evidence, matches = resolve_rules(text, ALIASES, RULES)
    by_id = {mapping.mapping_id: mapping for mapping in BUILDCRAFT_MAPPINGS}
    output = []
    for match in matches:
        item = by_id[match.rule_id].to_fractal_mapping()
        item["resolver_evidence"] = {
            "score": match.score,
            "reasons": list(match.evidence),
            "concepts": sorted(evidence.concepts),
            "relations": [list(relation) for relation in evidence.relations],
        }
        output.append(item)
    return output


def summarize_buildcraft_ontology(text: str) -> dict[str, object]:
    evidence, matches = resolve_rules(text, ALIASES, RULES)
    return {
        "ontology": "BUILDCRAFT_COMPUTE_ONTOLOGY",
        "resolver": "RELATION_AWARE_STRUCTURAL_IR_V1",
        "mapping_ids": [match.rule_id for match in matches],
        "scores": {match.rule_id: match.score for match in matches},
        "concepts": sorted(evidence.concepts),
        "relations": [list(relation) for relation in evidence.relations],
        "canonical_chain": [
            "motherboard/chassis topology -> equipment paper doll",
            "PCIe accelerator slot -> weapon slot",
            "CPU socket/host position -> body-armour slot",
            "GPU/accelerator -> equipped weapon",
            "CPU package -> equipped body armour",
            "hardware integration capacity -> item sockets and links",
            "LLM/application -> active skill gem",
            "runtime/drafter/cache/framework -> support gem",
            "CUDA/PyTorch/drivers/ABI -> compatibility requirements",
            "VRAM occupancy -> mana reservation",
            "deployed architecture -> complete build",
        ],
        "global_guardrail": "Preserve relationship grammar without claiming material identity.",
    }
