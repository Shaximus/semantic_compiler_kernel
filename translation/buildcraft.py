"""Resolve Path of Exile buildcraft shorthand into typed compute mappings.

Resolution is two-layered and deterministic:

1. **Structural layer** (PR #3, relation-aware): ontology concepts and typed
   relations are extracted from the text, and mapping rules are scored against
   concept coverage and relationship evidence. Matches carry auditable
   per-mapping scores in ``resolver_evidence``.
2. **Trigger layer** (legacy): trigger-phrase matching plus dense-signal
   hierarchy recovery, preserving the original recall contract — the
   structural layer enriches matches with evidence; it does not erase
   trigger-based resolution.
"""
from __future__ import annotations

import re

from semantic_compiler.registry.buildcraft import BUILDCRAFT_MAPPINGS, BuildcraftMapping
from semantic_compiler.translation.structural_resolver import (
    RelationPattern,
    StructuralRule,
    resolve_rules,
)


ALIASES = {
    "pcie_slot": ("pcie", "pcie slot", "pcie slots", "accelerator slot"),
    "weapon_slot": ("weapon slot", "weapon slots", "weapon sockets", "weapon links"),
    "gpu": ("gpu", "gpus", "accelerator", "graphics card"),
    "weapon": ("weapon", "equipped weapon"),
    "cpu_socket": ("cpu socket", "cpu slot", "host compute position"),
    "armour_slot": ("armor slot", "armour slot", "body armor slot", "body armour slot"),
    "cpu": ("cpu", "cpus", "processor", "host compute"),
    "armour": ("armor", "armour", "body armor", "body armour"),
    "integration_capacity": ("linked sockets", "gem slots", "six link", "6 link", "ten link", "10 link"),
    "llm": ("llm", "model", "primary application", "active workload"),
    "active_skill": ("active skill", "active skill gem", "active skill gems", "skill gem", "skill gems"),
    "support_runtime": ("support gem", "support gems", "mtp", "drafter", "speculative drafter", "cache layer", "vllm", "sglang", "inference framework"),
    "compatibility": ("cuda", "pytorch", "driver", "drivers", "abi", "runtime compatibility", "gem tags"),
    "vram": ("vram", "accelerator memory", "gpu memory"),
    "reservation": ("mana reservation", "reserved mana", "resource reservation", "allocation"),
    "repository": ("repo", "repository", "package", "docker profile"),
    "complete_build": ("complete build", "compute build", "architecture build", "path of building", "reflexion of building"),
    "delivery_proliferation": ("too many builds", "twenty viable builds", "20 viable builds", "before reaching maps", "league starter reaches maps"),
    "premium_accelerator": ("rtx pro 6000", "blackwell 96 gb"),
    "mirror_item": ("mirror-tier 10 link bow", "mirror tier ten link bow", "10 link bow", "ten link bow"),
    # Founder eureka 2026-07-23 (BUILD_015-BUILD_018).
    "pc_case": ("pc case", "computer case", "chassis"),
    "character_select": ("character selection screen", "character select screen", "character select"),
    "motherboard": ("motherboard",),
    "race_base_class": ("race", "base class"),
    "gmp": ("greater multiple projectiles", "gmp", "multi-projectile support", "multiple projectiles support"),
    "mtp": ("mtp", "multi-token prediction", "speculative decoding"),
    "mirror_hardware": ("mirror-tier gpu", "mirror tier gpu", "mirror-tier hardware"),
    "mirror_tier_item": ("mirror of kalandra", "mirror-of-kalandra", "mirror-tier item"),
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
    # Founder eureka 2026-07-23 (BUILD_015-BUILD_018).
    StructuralRule("BUILD_015", concepts_any=(frozenset({"pc_case"}), frozenset({"character_select"})), relations_any=(RelationPattern("equivalent_role", frozenset({"pc_case"}), frozenset({"character_select"})),), minimum_score=0.45),
    StructuralRule("BUILD_016", concepts_any=(frozenset({"motherboard"}), frozenset({"race_base_class"})), relations_any=(RelationPattern("equivalent_role", frozenset({"motherboard"}), frozenset({"race_base_class"})),), minimum_score=0.45),
    StructuralRule("BUILD_017", concepts_any=(frozenset({"mtp"}), frozenset({"gmp"})), relations_any=(RelationPattern("equivalent_role", frozenset({"mtp"}), frozenset({"gmp"})),), minimum_score=0.45),
    StructuralRule("BUILD_018", concepts_any=(frozenset({"mirror_hardware"}), frozenset({"mirror_tier_item"})), relations_any=(RelationPattern("equivalent_role", frozenset({"mirror_hardware"}), frozenset({"mirror_tier_item"})),), minimum_score=0.45),
)


# ---------------------------------------------------------------------------
# Trigger layer (legacy recall contract)
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    normalized = text.casefold().replace("’", "'").replace("–", "-").replace("—", "-")
    normalized = re.sub(r"[^a-z0-9+./' -]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _trigger_matches(text: str, trigger: str) -> bool:
    normalized_trigger = _normalize(trigger)
    return bool(normalized_trigger and normalized_trigger in text)


def _trigger_ids(normalized: str) -> list[str]:
    """Trigger-phrase matches plus dense-signal hierarchy recovery."""
    ids: list[str] = []

    def add(mapping_id: str) -> None:
        if mapping_id not in ids:
            ids.append(mapping_id)

    for mapping in BUILDCRAFT_MAPPINGS:
        if any(_trigger_matches(normalized, trigger) for trigger in mapping.triggers):
            add(mapping.mapping_id)

    # Recover the hierarchy from compressed founder shorthand.
    if "pcie" in normalized:
        add("BUILD_002")
    if "gpu" in normalized or "accelerator" in normalized:
        add("BUILD_004")
    if "cpu socket" in normalized or "cpu slot" in normalized:
        add("BUILD_003")
    if "cpu" in normalized and any(word in normalized for word in ("armor", "armour", "body")):
        add("BUILD_005")
    if "vram" in normalized and any(word in normalized for word in ("mana", "reserve", "allocation")):
        add("BUILD_010")
    if "llm" in normalized or "model" in normalized:
        if "gem" in normalized or "skill" in normalized:
            add("BUILD_007")
    if any(word in normalized for word in ("cuda", "pytorch", "pypi", "driver", "abi")):
        add("BUILD_009")
    if any(word in normalized for word in ("repo", "repository", "package")):
        add("BUILD_011")
    if "rtx pro 6000" in normalized or ("blackwell" in normalized and "96 gb" in normalized):
        add("BUILD_014")

    # A dense statement spanning three or more layers should preserve the
    # complete slot -> item -> component -> reservation chain.
    hierarchy_signals = sum(
        signal in normalized
        for signal in ("pcie", "gpu", "cpu", "llm", "gem", "vram", "cuda", "pytorch")
    )
    if hierarchy_signals >= 3:
        if "pcie" in normalized:
            add("BUILD_002")
        if "gpu" in normalized:
            add("BUILD_004")
        if "cpu" in normalized:
            add("BUILD_005")
        if "llm" in normalized or "model" in normalized:
            add("BUILD_007")
        if "gem" in normalized or "mtp" in normalized or "drafter" in normalized:
            add("BUILD_008")
        if "vram" in normalized:
            add("BUILD_010")

    return ids


# ---------------------------------------------------------------------------
# Combined resolution
# ---------------------------------------------------------------------------

def resolve_buildcraft_entries(text: str) -> list[BuildcraftMapping]:
    """Return buildcraft mappings supported by structural or trigger evidence.

    Structural (relation-aware, scored) matches come first, followed by
    trigger-layer matches, deduplicated.
    """
    _, matches = resolve_rules(text, ALIASES, RULES)
    by_id = {mapping.mapping_id: mapping for mapping in BUILDCRAFT_MAPPINGS}
    entries: list[BuildcraftMapping] = []
    seen: set[str] = set()
    for match in matches:
        entries.append(by_id[match.rule_id])
        seen.add(match.rule_id)
    normalized = _normalize(text)
    if normalized:
        for mapping_id in _trigger_ids(normalized):
            if mapping_id not in seen:
                entries.append(by_id[mapping_id])
                seen.add(mapping_id)
    return entries


def resolve_buildcraft_mappings(text: str) -> list[dict[str, object]]:
    evidence, matches = resolve_rules(text, ALIASES, RULES)
    scores = {match.rule_id: match for match in matches}
    output = []
    for entry in resolve_buildcraft_entries(text):
        item = entry.to_fractal_mapping()
        match = scores.get(entry.mapping_id)
        item["resolver_evidence"] = (
            {
                "score": match.score,
                "reasons": list(match.evidence),
                "concepts": sorted(evidence.concepts),
                "relations": [list(relation) for relation in evidence.relations],
            }
            if match is not None
            else {"score": None, "reasons": ["trigger_phrase_match"], "concepts": sorted(evidence.concepts), "relations": [list(relation) for relation in evidence.relations]}
        )
        output.append(item)
    return output


def summarize_buildcraft_ontology(text: str) -> dict[str, object]:
    evidence, matches = resolve_rules(text, ALIASES, RULES)
    return {
        "ontology": "BUILDCRAFT_COMPUTE_ONTOLOGY",
        "resolver": "RELATION_AWARE_STRUCTURAL_IR_V1+TRIGGER_RECALL",
        "mapping_ids": [entry.mapping_id for entry in resolve_buildcraft_entries(text)],
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
