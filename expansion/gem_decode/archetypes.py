"""Deterministic build-archetype inference for gem_decode.

The decoder translates declared components and then asks two further questions:

1. What established build family is this system attempting to become?
2. Which invariant gem/aura layers are still missing to complete that family?

Completion layers are structural requirements distilled from reference build families. They
are not item recommendations, patch-specific DPS claims, or proof of measured performance.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from semantic_compiler.expansion.gem_decode.parser import GemBuild


@dataclass(frozen=True)
class CompletionLayer:
    """One structural layer repeatedly present across a reference build family."""

    layer_id: str
    name: str
    priority: str
    layer_type: str
    poe_anchors: tuple[str, ...]
    evidence_any: tuple[str, ...]
    inference_role: str


@dataclass(frozen=True)
class ArchetypeRule:
    archetype_id: str
    name: str
    required_any: tuple[tuple[str, ...], ...]
    optional: tuple[str, ...]
    invariant: str
    failure_families: tuple[str, ...] = ()
    reference_builds: tuple[str, ...] = ()
    completion_layers: tuple[CompletionLayer, ...] = ()


_COC_COMPLETION_LAYERS: tuple[CompletionLayer, ...] = (
    CompletionLayer(
        "QUALIFICATION_ACCURACY",
        "Qualification accuracy and critical reliability",
        "P0",
        "Aura / support / mark",
        ("Precision", "Increased Critical Strikes", "Assassin's Mark", "Power Charge on Critical"),
        (
            "precision", "accuracy", "hit chance", "increased critical strikes",
            "assassin's mark", "assassins mark", "power charge on critical",
            "critical reliability", "acceptance calibration", "qualification calibration",
        ),
        "Calibrate proposal confidence and token alignment so added MTP branches become accepted work rather than wider rejection fan-out.",
    ),
    CompletionLayer(
        "COOLDOWN_BREAKPOINT",
        "Cooldown recovery and cadence governor",
        "P0",
        "Support gem / control aura",
        ("Cooldown Recovery Support", "Cast on Critical Strike breakpoint", "attack-speed cap"),
        (
            "cooldown recovery", "cdr", "trigger recovery", "cadence governor",
            "adaptive k", "adaptive cadence", "attack speed cap", "breakpoint governor",
        ),
        "Align draft rate and MTP width with verifier recovery so proposals do not collide with an unavailable trigger window.",
    ),
    CompletionLayer(
        "RESOURCE_SUSTAIN",
        "Execution-cost sustain",
        "P0",
        "Support gem / aura",
        ("Inspiration", "Clarity", "Lifetap"),
        (
            "inspiration", "clarity", "lifetap", "mana sustain", "resource sustain",
            "cost reduction", "execution budget", "accepted sequence cache",
        ),
        "Lower and replenish the cost of continuous drafting, verification, and cache growth so peak throughput remains sustainable.",
    ),
    CompletionLayer(
        "RESERVATION_EFFICIENCY",
        "Reservation compression",
        "P0",
        "Support gem / policy aura",
        ("Enlighten", "reservation-efficiency passives"),
        (
            "enlighten", "reservation efficiency", "reservation compression",
            "mana reservation", "service reservation planner", "aura budget",
        ),
        "Fit persistent services such as BCC, routing, receipts, KV reuse, and scheduling without starving active KV/VRAM headroom.",
    ),
    CompletionLayer(
        "TARGET_PRECONDITIONING",
        "Low-cost target preconditioning",
        "P1",
        "Utility aura / side-agent package",
        ("Summon Skitterbots", "Bonechill", "Unbound Ailments"),
        (
            "skitterbots", "bonechill", "unbound ailments", "preconditioner",
            "constraint detector", "contradiction detector", "target preconditioning",
        ),
        "Use cheap side agents to expose uncertainty, contradictions, constraints, and salience before the expensive verifier executes.",
    ),
    CompletionLayer(
        "RETURN_FEEDBACK",
        "Returned-branch learning and merge",
        "P1",
        "Support gem / equipment interaction",
        ("Returning Projectiles", "Nimis"),
        (
            "returning projectiles", "nimis", "rejection reasons", "branch feedback",
            "return path", "returned branch", "verified returning projectiles",
        ),
        "Return rejection reasons and accepted-path evidence into the next proposal cycle, with de-duplication before merge.",
    ),
    CompletionLayer(
        "DEFENSIVE_HEADROOM",
        "Defensive and compatibility headroom",
        "P1",
        "Defensive aura envelope",
        ("Discipline", "Purity of Elements", "Grace", "Determination"),
        (
            "discipline", "purity of elements", "grace", "determination",
            "kv headroom", "vram headroom", "backpressure", "compatibility envelope",
            "crash containment", "rollback capacity",
        ),
        "Reserve memory, queue, compatibility, and rollback margin so a high-rate trigger cascade fails closed rather than collapsing the runtime.",
    ),
    CompletionLayer(
        "TARGET_MARKING",
        "Target-specific verification policy",
        "P1",
        "Mark / targeting aura",
        ("Assassin's Mark", "Sniper's Mark"),
        (
            "assassin's mark", "assassins mark", "sniper's mark", "snipers mark",
            "target mark", "target-specific evaluator", "target specific evaluator",
        ),
        "Apply additional verification and routing effort to the selected target rather than globally over-computing every request.",
    ),
    CompletionLayer(
        "TRIGGER_DUPLICATION",
        "Duplicated trigger loci",
        "P2",
        "Ascendancy / execution aura",
        ("Triggerbots",),
        (
            "triggerbots", "dual verifier", "duplicate trigger", "duplicated trigger",
            "two execution loci", "dual execution loci",
        ),
        "Duplicate qualified execution only after result de-duplication, merge bandwidth, and authority boundaries are proven.",
    ),
    CompletionLayer(
        "MULTISTAGE_TRIGGER_GRAPH",
        "Multi-stage preparation and execution graph",
        "P2",
        "Trigger support graph",
        ("Manaforged Arrows", "Desecrate + Detonate Dead", "Rain of Arrows / Blast Rain"),
        (
            "manaforged arrows", "desecrate", "detonate dead", "state preparation",
            "prepare state", "multi-stage trigger", "multistage trigger", "trigger graph",
        ),
        "Separate cheap state preparation from expensive payload execution and assign each stage its own cooldown and resource domain.",
    ),
    CompletionLayer(
        "LOOP_STABILIZATION",
        "Autonomous-loop stabilization",
        "P2",
        "Recovery / watchdog layer",
        ("Wardloop", "Cast when Damage Taken", "Cast on Ward Break"),
        (
            "wardloop", "cast when damage taken", "cwdt", "cast on ward break",
            "loop breaker", "watchdog", "bounded recursion", "recovery cadence",
        ),
        "Permit self-triggering recursion only with a bounded budget, recovery proof, watchdog, and deterministic loop breaker.",
    ),
)


_RULES: tuple[ArchetypeRule, ...] = (
    ArchetypeRule(
        "COC_TRIGGER_CASCADE",
        "Cast-on-Crit trigger cascade",
        required_any=(
            ("cast on critical strike", "coc", "speculative decoding", "mtp"),
            ("draft", "drafter", "cyclone"),
            ("verifier", "qwen", "minimax", "llm", "ice nova"),
        ),
        optional=(
            "cospri", "rtx 3080 ti", "frostbolt", "scheduler",
            "expert precognition", "prefetch", "greater multiple projectiles", "gmp",
        ),
        invariant="continuous cheap proposals qualify through an acceptance gate and automatically trigger expensive verified execution",
        failure_families=("F", "M", "T"),
        reference_builds=(
            "Cospri Ice Nova of Frostbolts CoC",
            "Forbidden Rite CoC",
            "Ice Spear / returning-projectile CoC",
            "Bow CoC Detonate Dead with Manaforged staging",
            "Triggerbots duplicated-trigger CoC",
        ),
        completion_layers=_COC_COMPLETION_LAYERS,
    ),
    ArchetypeRule(
        "AURA_STACKER",
        "Aura-stacked shared-service build",
        required_any=(
            ("bcc", "memory"),
            ("tokenrouter", "arda", "scheduler", "semantic compiler"),
            ("kv reuse", "shared world state", "receipts", "auris", "doctrine"),
        ),
        optional=("quantization policy", "kernel selection", "tool permissions", "provenance"),
        invariant="persistent shared modifiers amplify several otherwise independent capabilities or party members",
        failure_families=("N", "B", "S"),
        reference_builds=("reservation-efficient aura stacker",),
    ),
    ArchetypeRule(
        "MOE_PRECOGNITION",
        "MoE expert-precognition build",
        required_any=(
            ("expert precognition", "prefetch", "routing prefetch"),
            ("expert compression", "quantization", "compression"),
            ("tokenrouter", "arda", "routing", "moe"),
        ),
        optional=("bcc", "cache", "kv cache", "triton", "direct dma", "hugepage"),
        invariant="future expert demand is predicted early enough to hydrate only the required routed weights before execution reaches them",
        failure_families=("E", "F", "T"),
    ),
    ArchetypeRule(
        "MTP_PROJECTILE_SCALER",
        "Multi-projectile speculative throughput build",
        required_any=(
            ("mtp", "multi token prediction", "greater multiple projectiles", "gmp"),
            ("verifier", "qwen", "minimax", "llm"),
        ),
        optional=("draft", "speculative decoding", "dying sun", "auxiliary i9", "batching"),
        invariant="one expensive forward opportunity emits several candidates whose net value depends on verifier acceptance capacity",
        failure_families=("M", "F", "T"),
        reference_builds=("GMP projectile scaler", "returning-projectile overlap build"),
    ),
    ArchetypeRule(
        "DYING_SUN_FANOUT",
        "Dying Sun temporary fan-out build",
        required_any=(
            ("dying sun", "auxiliary i9", "auxiliary pc", "lifeboat"),
            ("mtp", "draft", "retrieval", "fanout", "fan out"),
        ),
        optional=("network", "merge bandwidth", "scheduler", "verifier"),
        invariant="bounded auxiliary capacity temporarily widens candidate, retrieval, or tool trajectories",
        failure_families=("E", "M", "T"),
    ),
    ArchetypeRule(
        "WARDLOOP_RECURSION",
        "Wardloop-style self-triggering recursion",
        required_any=(
            ("self trigger", "recursive", "loop", "cast when damage taken", "cwdt"),
            ("tool", "agent", "model", "inference"),
        ),
        optional=("cognitive leech", "budget refill", "recovery", "receipts"),
        invariant="an output creates the condition that automatically funds or triggers the next output",
        failure_families=("D", "E", "Q"),
    ),
    ArchetypeRule(
        "PROXY_COST_BYPASS",
        "Hateforge / proxy-cost-bypass build",
        required_any=(
            ("proxy", "proxy casting", "totem", "trap", "mine"),
            ("authority", "budget", "cost", "flask", "vaal"),
        ),
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


def _completion_status(text: str, layer: CompletionLayer) -> dict[str, Any]:
    hits = [term for term in layer.evidence_any if term.casefold() in text]
    return {
        "layer_id": layer.layer_id,
        "name": layer.name,
        "priority": layer.priority,
        "layer_type": layer.layer_type,
        "status": "PRESENT" if hits else "MISSING",
        "poe_anchors": list(layer.poe_anchors),
        "matched_evidence": hits,
        "inference_role": layer.inference_role,
    }


def identify_archetypes(build: GemBuild, translated: dict[str, Any]) -> list[dict[str, Any]]:
    """Rank archetypes and report reference-derived missing completion layers.

    Confidence is structural coverage, not a performance claim. Results below 0.34 are
    omitted; incomplete candidates are returned as ATTEMPTING with explicit missing
    invariant groups and completion-layer status.
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
            "reference_builds": list(rule.reference_builds),
            "completion_layers": [
                _completion_status(text, layer) for layer in rule.completion_layers
            ],
        })
    return sorted(results, key=lambda item: (-item["confidence"], item["archetype_id"]))


__all__ = ["identify_archetypes", "ArchetypeRule", "CompletionLayer"]
