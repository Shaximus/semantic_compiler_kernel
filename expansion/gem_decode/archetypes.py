"""Deterministic build-archetype inference for gem_decode.

The original decoder translates declared components. This module answers the next
question: what established build pattern is the supplied system attempting to become?
It scores invariant feature sets, reports evidence and missing pieces, and never turns
an incomplete resemblance into a confident identification.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from semantic_compiler.expansion.gem_decode.parser import GemBuild


@dataclass(frozen=True)
class ArchetypeRule:
    archetype_id: str
    name: str
    required_any: tuple[tuple[str, ...], ...]
    optional: tuple[str, ...]
    invariant: str
    failure_families: tuple[str, ...] = ()


_RULES: tuple[ArchetypeRule, ...] = (
    ArchetypeRule(
        "COC_TRIGGER_CASCADE",
        "Cospri / Cast-on-Crit trigger cascade",
        required_any=(("cast on critical strike", "coc", "speculative decoding", "mtp"),
                      ("draft", "drafter", "cyclone"),
                      ("verifier", "qwen", "minimax", "llm", "ice nova")),
        optional=("cospri", "rtx 3080 ti", "frostbolt", "scheduler", "expert precognition", "prefetch"),
        invariant="continuous cheap proposals qualify through an acceptance gate and automatically trigger expensive verified execution",
        failure_families=("F", "M", "T"),
    ),
    ArchetypeRule(
        "AURA_STACKER",
        "Aura-stacked shared-service build",
        required_any=(("bcc", "memory"), ("tokenrouter", "arda", "scheduler", "semantic compiler"),
                      ("kv reuse", "shared world state", "receipts", "auris", "doctrine")),
        optional=("quantization policy", "kernel selection", "tool permissions", "provenance"),
        invariant="persistent shared modifiers amplify several otherwise independent capabilities or party members",
        failure_families=("N", "B", "S"),
    ),
    ArchetypeRule(
        "MOE_PRECOGNITION",
        "MoE expert-precognition build",
        required_any=(("expert precognition", "prefetch", "routing prefetch"),
                      ("expert compression", "quantization", "compression"),
                      ("tokenrouter", "arda", "routing", "moe")),
        optional=("bcc", "cache", "kv cache", "triton", "direct dma", "hugepage"),
        invariant="future expert demand is predicted early enough to hydrate only the required routed weights before execution reaches them",
        failure_families=("E", "F", "T"),
    ),
    ArchetypeRule(
        "MTP_PROJECTILE_SCALER",
        "Multi-projectile speculative throughput build",
        required_any=(("mtp", "multi token prediction", "greater multiple projectiles", "gmp"),
                      ("verifier", "qwen", "minimax", "llm")),
        optional=("draft", "speculative decoding", "dying sun", "auxiliary i9", "batching"),
        invariant="one expensive forward opportunity emits several candidates whose net value depends on verifier acceptance capacity",
        failure_families=("M", "F", "T"),
    ),
    ArchetypeRule(
        "DYING_SUN_FANOUT",
        "Dying Sun temporary fan-out build",
        required_any=(("dying sun", "auxiliary i9", "auxiliary pc", "lifeboat"),
                      ("mtp", "draft", "retrieval", "fanout", "fan out")),
        optional=("network", "merge bandwidth", "scheduler", "verifier"),
        invariant="bounded auxiliary capacity temporarily widens candidate, retrieval, or tool trajectories",
        failure_families=("E", "M", "T"),
    ),
    ArchetypeRule(
        "WARDLOOP_RECURSION",
        "Wardloop-style self-triggering recursion",
        required_any=(("self trigger", "recursive", "loop", "cast when damage taken", "cwdt"),
                      ("tool", "agent", "model", "inference")),
        optional=("cognitive leech", "budget refill", "recovery", "receipts"),
        invariant="an output creates the condition that automatically funds or triggers the next output",
        failure_families=("D", "E", "Q"),
    ),
    ArchetypeRule(
        "PROXY_COST_BYPASS",
        "Hateforge / proxy-cost-bypass build",
        required_any=(("proxy", "proxy casting", "totem", "trap", "mine"),
                      ("authority", "budget", "cost", "flask", "vaal")),
        optional=("tool permissions", "receipts", "calibrated dissent"),
        invariant="a proxy executes premium work while attempting to avoid the authority or resource cost assigned to the primary actor",
        failure_families=("E", "H"),
    ),
)


def _component_text(build: GemBuild, translated: dict[str, Any]) -> str:
    terms: list[str] = [name.casefold() for _, name in build.all_components()]
    layers = translated.get("layers", {})
    for value in layers.values():
        records = value if isinstance(value, list) else ([value] if value else [])
        for record in records:
            for key in ("canonical", "compute_analogue", "note", "scope"):
                item = record.get(key)
                if item:
                    terms.append(str(item).casefold())
    return " | ".join(terms)


def _group_match(text: str, group: tuple[str, ...]) -> tuple[bool, list[str]]:
    hits = [term for term in group if term.casefold() in text]
    return bool(hits), hits


def identify_archetypes(build: GemBuild, translated: dict[str, Any]) -> list[dict[str, Any]]:
    """Rank archetypes the build is attempting to express.

    Confidence is structural coverage, not a performance claim. Results below 0.34 are
    omitted; incomplete candidates are returned as ATTEMPTING with explicit missing
    invariant groups.
    """
    text = _component_text(build, translated)
    results: list[dict[str, Any]] = []
    for rule in _RULES:
        matched_groups: list[list[str]] = []
        missing_groups: list[list[str]] = []
        for group in rule.required_any:
            matched, hits = _group_match(text, group)
            if matched:
                matched_groups.append(hits)
            else:
                missing_groups.append(list(group))
        optional_hits = [term for term in rule.optional if term.casefold() in text]
        required_coverage = len(matched_groups) / len(rule.required_any)
        optional_bonus = min(0.15, 0.03 * len(optional_hits))
        confidence = min(1.0, round(required_coverage * 0.85 + optional_bonus, 3))
        if confidence < 0.34:
            continue
        status = "IDENTIFIED" if not missing_groups else "ATTEMPTING"
        results.append({
            "archetype_id": rule.archetype_id,
            "name": rule.name,
            "status": status,
            "confidence": confidence,
            "invariant": rule.invariant,
            "matched_evidence": matched_groups + ([optional_hits] if optional_hits else []),
            "missing_groups": missing_groups,
            "failure_families": list(rule.failure_families),
        })
    return sorted(results, key=lambda item: (-item["confidence"], item["archetype_id"]))


__all__ = ["identify_archetypes", "ArchetypeRule"]
