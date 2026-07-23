"""
Five-layer gem ontology (gem_decode).

Every parsed component classifies into exactly one layer:

- **Equipment**    — permanently installed hardware (case = character select,
  motherboard = race, GPU = weapon, CPU = body armour)
- **Active skill** — the primary payload (LLM weights = active skill gem)
- **Support gem**  — execution mechanics (CUDA/PyTorch/vLLM/MTP/cache/
  framework; MTP = GMP with acceptance-rate = accuracy-rating invariant)
- **Aura**         — persistent modifier fields (BCC, doctrine, system
  prompt, KV reuse, scheduler, TokenRouter, Auris, shared world state)
- **Anointment**   — certified portable doctrine overlays (oils = evidence
  tiers; no retraining)
- **Flask**        — temporary bounded burst modes (Dying Sun = auxiliary
  compute fan-out; charges = concurrency budget; fail-open recovery)

The tables reuse the frozen registry's BUILD_001–018 mappings by reference
(``build_refs``) instead of editing the frozen registry. Sources:
RESEARCH_BRIEF.md (taxonomy + canonical anchors), COGNITIVE_COSPRI_001.md,
AURA_STACK_ARCHITECTURE.md, ANOINTMENTS_AND_OILS.md, FLASK_ONTOLOGY.md,
MISSING_SUPPORT_GEMS.md (the poe_buildcraft corpus, 2026-07-23).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ComponentEntry:
    """One canonical component in the five-layer ontology."""

    canonical: str
    layer: str                     # Equipment|Active skill|Support gem|Aura|Anointment|Flask
    compute_analogue: str
    aliases: tuple[str, ...] = ()
    build_refs: tuple[str, ...] = ()     # BUILD_xxx references from registry/buildcraft.py
    note: str = ""
    scope: Optional[str] = None          # auras: declared affected-stat scope (governance law)
    authority_layer: bool = False        # counts as an authority/dissent layer (anti-Adapa)
    trigger_engine: bool = False         # gates an expensive payload (CoC / speculative controller)
    proxy_compute: bool = False          # bounded work executed away from the primary model
    high_instruction_fidelity: bool = False  # LLM weights / instruction-tuned payload


def _norm(text: str) -> str:
    normalized = text.casefold().replace("_", " ").replace("-", " ")
    # Strip parameter suffixes ("K=5") and parenthetical annotations first,
    # before punctuation removal destroys the "=" marker.
    normalized = re.sub(r"\bk\s*=\s*\d+\b", "", normalized)
    normalized = re.sub(r"\(.*?\)", "", normalized)
    normalized = re.sub(r"[^a-z0-9+.' ]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


_ENTRIES: tuple[ComponentEntry, ...] = (
    # ------------------------------------------------------------------
    # Equipment — permanently installed hardware
    # ------------------------------------------------------------------
    ComponentEntry(
        "PC case / chassis", "Equipment",
        "the outward vessel of the deployed build (BUILD_015)",
        aliases=("pc case", "computer case", "case", "chassis"),
        build_refs=("BUILD_015",),
        note="the vessel chosen at creation; outward presentation of the build",
    ),
    ComponentEntry(
        "motherboard", "Equipment",
        "race / base class: socket types, inherent attributes, expansion ceilings (BUILD_016)",
        aliases=("mobo",),
        build_refs=("BUILD_016", "BUILD_001"),
        note="the chassis of identity, not the gear",
    ),
    ComponentEntry(
        "GPU / accelerator", "Equipment",
        "equipped weapon: primary high-throughput execution path (BUILD_004)",
        aliases=("gpu", "accelerator", "weapon"),
        build_refs=("BUILD_004", "BUILD_002"),
    ),
    ComponentEntry(
        "RTX PRO 6000", "Equipment",
        "mirror-tier accelerator: premium native capacity, no upgrade path this league (BUILD_014/BUILD_018)",
        aliases=("rtx pro 6000", "blackwell 96 gb", "mirror-tier gpu", "mirror tier gpu", "mirror-tier hardware", "primary weapon"),
        build_refs=("BUILD_014", "BUILD_018"),
        note="perfect roll; ceiling of the current league/budget",
    ),
    ComponentEntry(
        "RTX 3080 Ti", "Equipment",
        "secondary GPU hosting the trigger workload (Cospri's Malice slot)",
        aliases=("rtx 3080 ti", "3080 ti", "secondary gpu", "secondary weapon", "cospri's malice", "cospris malice"),
        build_refs=("BUILD_004",),
        note="specialized trigger weapon per COGNITIVE_COSPRI_001",
    ),
    ComponentEntry(
        "Cospri's Malice", "Equipment",
        "specialized trigger weapon: secondary GPU hosting the trigger workload",
        aliases=("cospri",),
        build_refs=("BUILD_004",),
        note="per COGNITIVE_COSPRI_001: socketed spell = routing/prefetch workload on the secondary device",
    ),
    ComponentEntry(
        "CPU", "Equipment",
        "equipped body armour: broad always-available host capacity (BUILD_005)",
        aliases=("cpu", "cpu package", "processor"),
        build_refs=("BUILD_005", "BUILD_003"),
    ),
    ComponentEntry(
        "auxiliary i9-11900K (Lifeboat)", "Equipment",
        "auxiliary compute host; becomes Dying Sun when activated for fan-out",
        aliases=("auxiliary i9", "auxiliary_i9", "i9", "i9-11900k", "lifeboat", "aux pc", "auxiliary pc"),
        build_refs=("BUILD_005",),
        note="not inherently a flask — activated temporarily it IS the Dying Sun flask",
    ),
    # ------------------------------------------------------------------
    # Active skill — the primary payload
    # ------------------------------------------------------------------
    ComponentEntry(
        "LLM weights / verifier model", "Active skill",
        "active skill gem: the primary behavior produced by the build (BUILD_007)",
        aliases=("verifier", "model", "llm", "target model", "verifier model", "minimax m2.5", "minimax", "qwen", "target model verified execution"),
        build_refs=("BUILD_007",),
        note="proposal quality = speculative acceptance rate (accuracy + crit chance)",
        high_instruction_fidelity=True,
    ),
    ComponentEntry(
        "Ice Nova", "Active skill",
        "high-value detonation around projected state: the verifier executes expert computation",
        aliases=("ice nova",),
        note="per COGNITIVE_COSPRI_001: detonation = target-model verified execution",
    ),
    ComponentEntry(
        "Cyclone", "Active skill",
        "continuous low-cost driver: the draft model continuously generating candidates",
        aliases=("cyclone",),
        note="per COGNITIVE_COSPRI_001: attack speed = draft rate",
    ),
    ComponentEntry(
        "Frostbolt", "Active skill",
        "projected state carrier: predicted hidden state / anticipated expert route",
        aliases=("frostbolt",),
    ),
    # ------------------------------------------------------------------
    # Support gems — execution mechanics
    # ------------------------------------------------------------------
    ComponentEntry(
        "Greater Multiple Projectiles", "Support gem",
        "MTP speculative drafting: additional units at reduced per-unit effectiveness (BUILD_017)",
        aliases=("gmp", "greater multiple projectiles support"),
        build_refs=("BUILD_017",),
        note="net DPS gain only if accuracy holds — acceptance rate = accuracy rating; same breakpoint math",
    ),
    ComponentEntry(
        "MTP (multi-token prediction)", "Support gem",
        "Greater Multiple Projectiles support: drafts additional tokens at reduced per-token acceptance (BUILD_017)",
        aliases=("mtp", "multi-token prediction", "multi token prediction", "speculative decoding", "speculative decoder"),
        build_refs=("BUILD_017", "BUILD_008"),
        note="net throughput gain only if the acceptance rate holds",
        trigger_engine=True,
    ),
    ComponentEntry(
        "Cast on Critical Strike", "Support gem",
        "speculative decoding controller: qualification event gates the expensive payload",
        aliases=("cast on critical strike", "coc", "cast on crit"),
        note="critical strike = verifier acceptance of the candidate sequence",
        trigger_engine=True,
    ),
    ComponentEntry(
        "draft model", "Support gem",
        "drafter support: continuous candidate generation feeding the verifier (BUILD_008)",
        aliases=("draft", "drafter", "qwen draft", "speculative drafter", "draft model"),
        build_refs=("BUILD_008",),
    ),
    ComponentEntry(
        "vLLM / inference framework", "Support gem",
        "inference framework support: modifies execution of the primary workload (BUILD_008)",
        aliases=("vllm", "sglang", "inference framework", "framework"),
        build_refs=("BUILD_008",),
    ),
    ComponentEntry(
        "CUDA / PyTorch / drivers", "Support gem",
        "compatibility layer: gem tags and attribute requirements (BUILD_009)",
        aliases=("cuda", "pytorch", "drivers", "abi"),
        build_refs=("BUILD_009",),
    ),
    ComponentEntry(
        "expert compression / quantization", "Support gem",
        "quantization runtime support: capacity-for-precision trade (BUILD_008)",
        aliases=("expert compression", "quantization", "quantization runtime", "compression"),
        build_refs=("BUILD_008",),
    ),
    ComponentEntry(
        "cache layer", "Support gem",
        "cache support: execution cost reduction for repeated state (BUILD_008)",
        aliases=("cache", "cache layer", "cache stack", "kv cache"),
        build_refs=("BUILD_008",),
    ),
    ComponentEntry(
        "expert precognition", "Support gem",
        "Expert Precognition Support (MISSING #2): predicts expert activation, preloads required weights",
        aliases=("expert precognition", "precognition", "routing prefetch", "prefetch"),
        note="architecture exists in moe-precognition; projection incomplete",
    ),
    ComponentEntry(
        "Verified Returning Projectiles", "Support gem",
        "MISSING #3: rejected drafts return rejection REASONS to improve the next draft — never payment",
        aliases=("verified returning projectiles", "returning projectiles"),
        note="legitimate form returns reasons; acceptance-minting on rejected drafts is a breaker",
    ),
    ComponentEntry(
        "Unleash", "Support gem",
        "Unleash Support (MISSING #7): validated reasoning bursts prepared during idle compute",
        aliases=("unleash",),
    ),
    ComponentEntry(
        "Proxy Casting", "Support gem",
        "Proxy Casting Support (MISSING #8): bounded specialist execution — MUST pay authority + compute cost",
        aliases=("proxy casting", "totem", "trap", "mine", "proxy"),
        note="without proper cost it becomes the Hateforge exploit (families E/H)",
        proxy_compute=True,
    ),
    ComponentEntry(
        "Cognitive Leech", "Support gem",
        "Cognitive Leech Support (MISSING #9): successful inference returns reusable resources",
        aliases=("cognitive leech", "leech"),
    ),
    # ------------------------------------------------------------------
    # Auras — persistent modifier fields (governance law: every aura needs scope)
    # ------------------------------------------------------------------
    ComponentEntry(
        "BCC retrieval", "Aura",
        "Memory aura: context quality and continuity",
        aliases=("bcc", "bcc retrieval", "memory"),
        scope="context quality, continuity",
    ),
    ComponentEntry(
        "system prompt / doctrine", "Aura",
        "Discipline aura: behavior, tone, boundaries",
        aliases=("system prompt", "doctrine", "discipline"),
        scope="behavior, tone, boundaries",
    ),
    ComponentEntry(
        "Semantic Compiler", "Aura",
        "Coherence aura: structural transfer, ambiguity reduction",
        aliases=("semantic compiler", "coherence"),
        scope="structural transfer, ambiguity reduction",
    ),
    ComponentEntry(
        "Auris", "Aura",
        "Perception aura: salience, affect, timing",
        aliases=("auris", "perception"),
        scope="salience, affect, timing",
    ),
    ComponentEntry(
        "TokenRouter", "Aura",
        "Targeting aura: activation, routing, cadence",
        aliases=("tokenrouter", "token router", "arda", "targeting", "routing"),
        scope="activation, routing, cadence",
    ),
    ComponentEntry(
        "KV reuse", "Aura",
        "Cast-speed aura: latency and resource cost of repeated prefixes",
        aliases=("kv reuse", "kv-cache reuse", "prefix reuse"),
        scope="latency, resource cost",
    ),
    ComponentEntry(
        "scheduler", "Aura",
        "Trigger-rate aura: execution cadence configuration",
        aliases=("scheduler", "scheduler configuration"),
        scope="execution cadence",
    ),
    ComponentEntry(
        "tool permissions", "Aura",
        "Authority aura: utility surface and scope of permitted action",
        aliases=("authority", "permissions", "tool permissions"),
        scope="utility surface, scope",
        authority_layer=True,
    ),
    ComponentEntry(
        "shared world state", "Aura",
        "Party-coordination aura: multi-agent alignment; one agent pays, the party benefits",
        aliases=("shared world state", "world state", "party coordination"),
        scope="multi-agent alignment",
    ),
    ComponentEntry(
        "receipts", "Aura",
        "Receipt-visibility aura: provenance and audit trail for build effects",
        aliases=("receipts", "receipt visibility", "provenance"),
        scope="receipt visibility",
    ),
    ComponentEntry(
        "quantization policy", "Aura",
        "Reservation-efficiency aura: capacity and cost policy",
        aliases=("quantization policy", "reservation efficiency"),
        scope="capacity, cost",
    ),
    ComponentEntry(
        "kernel selection", "Aura",
        "Action-speed aura: throughput via kernel choice",
        aliases=("kernel selection", "action speed"),
        scope="throughput",
    ),
    ComponentEntry(
        "z24 doctrine", "Aura",
        "Judgment aura: calibration and closure",
        aliases=("z24", "z24 doctrine", "judgment"),
        scope="calibration, closure",
    ),
    ComponentEntry(
        "Hatred", "Aura",
        "damage-type modifier field: persistent scalar on the payload's output class",
        aliases=("hatred",),
        note="PoE-native aura; scope must be declared before deployment",
        scope=None,  # unscoped in PoE-native form — governance law applies
    ),
    ComponentEntry(
        "Herald of Ice", "Aura",
        "secondary persistent proc field riding the payload's detonations",
        aliases=("herald of ice", "herald"),
        scope=None,
    ),
    # ------------------------------------------------------------------
    # Anointments — certified portable doctrine overlays (oils = evidence tiers)
    # ------------------------------------------------------------------
    ComponentEntry(
        "Calibrated Dissent", "Anointment",
        "the anti-Adapa notable: low confidence + consequential authority -> pause, clarify, preserve refusal",
        aliases=("calibrated dissent",),
        note="oils: Production Evidence + Adversarial Validation + Independent Replication (MISSING #10)",
        authority_layer=True,
    ),
    ComponentEntry(
        "authority_gate", "Anointment",
        "authority-verification overlay: every consequential action checks its permission tier first",
        aliases=("authority gate", "authority_gate"),
        authority_layer=True,
    ),
    ComponentEntry(
        "Ask When Ambiguous", "Anointment",
        "companion overlay: ambiguity triggers clarification instead of confident guessing",
        aliases=("ask when ambiguous",),
        authority_layer=True,
    ),
    ComponentEntry(
        "Memory Before Action", "Anointment",
        "companion overlay: retrieval precedes consequential action",
        aliases=("memory before action",),
    ),
    ComponentEntry(
        "Teach Before Taking Control", "Anointment",
        "companion overlay: capability transfer precedes takeover",
        aliases=("teach before taking control",),
    ),
    ComponentEntry(
        "Preserve Human Agency", "Anointment",
        "companion overlay: the human's decision surface is never silently narrowed",
        aliases=("preserve human agency",),
        authority_layer=True,
    ),
    ComponentEntry(
        "Explain Failure Causally", "Anointment",
        "companion overlay: failures are reported with causal structure, not vibes",
        aliases=("explain failure causally",),
    ),
    ComponentEntry(
        "Do Not Conceal Uncertainty", "Anointment",
        "companion overlay: uncertainty is surfaced, never smoothed over",
        aliases=("do not conceal uncertainty",),
    ),
    ComponentEntry(
        "Prefer Primary Sources", "Anointment",
        "subsystem overlay (Retriever): primary-record evidence outranks secondary",
        aliases=("prefer primary sources",),
    ),
    ComponentEntry(
        "Escalate on Novelty", "Anointment",
        "subsystem overlay (TokenRouter): unseen situations route upward, not sideways",
        aliases=("escalate on novelty",),
    ),
    ComponentEntry(
        "Require Reversible First Action", "Anointment",
        "subsystem overlay (Tool Executor): first move in a new context must be reversible",
        aliases=("require reversible first action",),
    ),
    ComponentEntry(
        "Spend Additional Compute on Contradictions", "Anointment",
        "subsystem overlay (Verifier): contradictions buy extra verification compute",
        aliases=("spend additional compute on contradictions",),
    ),
    # ------------------------------------------------------------------
    # Flasks — temporary bounded burst modes (charges = concurrency budget)
    # ------------------------------------------------------------------
    ComponentEntry(
        "Dying Sun", "Flask",
        "auxiliary compute fan-out: +2 full speculative trajectories converging on one verifier",
        aliases=("dying sun",),
        note="breakpoint: effective fan-out = MIN(draft, verifier, network, scheduler, memory, merge bandwidth)",
        proxy_compute=True,
    ),
    ComponentEntry(
        "Diamond", "Flask",
        "extra verifier/critic passes (confidence calibration burst)",
        aliases=("diamond", "diamond flask"),
    ),
    ComponentEntry(
        "Quicksilver", "Flask",
        "fast lightweight routing / latency reduction burst",
        aliases=("quicksilver",),
    ),
    ComponentEntry(
        "Granite", "Flask",
        "stricter validation, rollback, containment burst",
        aliases=("granite",),
    ),
    ComponentEntry(
        "Jade", "Flask",
        "avoidance of irrelevant tasks and noisy context",
        aliases=("jade",),
    ),
    ComponentEntry(
        "Quartz", "Flask",
        "alternate legal route past blocked execution",
        aliases=("quartz",),
    ),
    ComponentEntry(
        "Mana flask", "Flask",
        "context/token/API-budget recovery",
        aliases=("mana", "mana flask"),
        note="a budget refilled by the activity it gates is family E (resource-cost bypass)",
    ),
    ComponentEntry(
        "Life flask", "Flask",
        "error recovery, service restoration",
        aliases=("life", "life flask"),
    ),
    ComponentEntry(
        "Bottled Faith", "Flask",
        "high-confidence shared context field amplifying all agents inside it",
        aliases=("bottled faith",),
    ),
    ComponentEntry(
        "Progenesis", "Flask",
        "defer failures into a recoverable queue instead of taking full damage",
        aliases=("progenesis",),
    ),
    ComponentEntry(
        "Mageblood", "Flask",
        "selected temporary profiles made effectively permanent (infrastructure)",
        aliases=("mageblood",),
    ),
)

_LOOKUP: dict[str, ComponentEntry] = {}
for _entry in _ENTRIES:
    _LOOKUP[_norm(_entry.canonical)] = _entry
    for _alias in _entry.aliases:
        _LOOKUP.setdefault(_norm(_alias), _entry)

# Layer-context overrides: a component whose computational role depends on
# where it sits in the build. Key: (normalized name, parsed layer);
# value: canonical name of the entry that describes that role.
# The auxiliary i9 is permanently installed EQUIPMENT, but in flask position
# it IS the Dying Sun burst mode (FLASK_ONTOLOGY: "not inherently a flask —
# it becomes Dying Sun when activated").
_LAYER_OVERRIDES: dict[tuple[str, str], str] = {
    (_norm(alias), "Flask"): "Dying Sun"
    for alias in ("auxiliary i9", "auxiliary_i9", "i9", "i9-11900k", "lifeboat", "aux pc", "auxiliary pc")
}


def lookup_component(name: str, layer: Optional[str] = None) -> Optional[ComponentEntry]:
    """Resolve a component name (either dialect) to its ontology entry.

    When ``layer`` (the parsed section layer, e.g. "Flask") is given,
    layer-context overrides are applied first so position-dependent
    components resolve to the role they actually play in this build.
    """
    normalized = _norm(name)
    if not normalized:
        return None
    if layer is not None:
        override = _LAYER_OVERRIDES.get((normalized, layer))
        if override is not None:
            return _LOOKUP[_norm(override)]
    entry = _LOOKUP.get(normalized)
    if entry is not None:
        return entry
    # Substring fallback: the spec may decorate a canonical name
    # ("RTX PRO 6000 target model verified execution").
    matches = [
        (len(key), e) for key, e in _LOOKUP.items()
        if len(key) >= 4 and (key in normalized or normalized in key)
    ]
    if matches:
        matches.sort(reverse=True)
        return matches[0][1]
    return None


LAYER_ORDER = ("Equipment", "Active skill", "Support gem", "Aura", "Anointment", "Flask")
