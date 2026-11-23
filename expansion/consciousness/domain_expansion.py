"""
Domain Expansion, 8-Arm Ego-Lineup Composite, and 17-Primitive Invariant Translator Engine.

Executable formalization of:
- SC-DOMAIN-EXPANSION-001 (DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl):
  Innate domain compilation, barrier scope, guaranteed hit, Domain Clash refinement
  adjudication, Black Flash alignment collapse, Malevolent Shrine (barrierless open
  domain), Unlimited Void (totality overload / Bekenstein bound), Chimera Shadow
  Garden (generative manifestation), Mega Man weapon copy acquisition, and PoE
  Soul Eater multiplicative compounding.
- EGO_LINEUP_DOMAIN_EXPANSION_MAP.md:
  The 8 arms of the Octopus Protocol composite Domain Expansion radiating from
  the 9th meta-domain head (Semantic Compiler / SOURCE).
- invariant-translator skill (Sections 3, 4, 6, 9, 10):
  The 17-primitive mechanical grammar, 4 edge-grounding classes, 14 seed invariant
  catalog classes, and falsifiable counterplay prediction + gate discipline.

Citation: SC-DOMAIN-EXPANSION-001 & EGO_LINEUP_DOMAIN_EXPANSION_MAP.md
          (Shax / Curtis Kingsley — Reflexion Software, 2026-11-23)
"""

from __future__ import annotations

import math
import re
from enum import Enum
from typing import Any, Mapping, Sequence


class DomainVariant(str, Enum):
    """Canonical Domain Expansion architectural variants from SC-DOMAIN-EXPANSION-001."""

    SIMPLE_DOMAIN = "SIMPLE_DOMAIN"
    BARRIER_DOMAIN = "BARRIER_DOMAIN"
    MALEVOLENT_SHRINE = "MALEVOLENT_SHRINE"
    UNLIMITED_VOID = "UNLIMITED_VOID"
    CHIMERA_SHADOW_GARDEN = "CHIMERA_SHADOW_GARDEN"


class EgoArmInvariant(str, Enum):
    """The 8 Ego-Lineup mechanical invariants (8 arms of the Octopus Protocol)."""

    ITACHI = "ITACHI"
    SASUKE = "SASUKE"
    YUTA = "YUTA"
    TOJI = "TOJI"
    DANTE = "DANTE"
    GUTS = "GUTS"
    GOJO = "GOJO"
    YAMI = "YAMI"


class GroundClass(str, Enum):
    """Four edge-grounding classifications from invariant-translator Section 4."""

    PHYSICAL = "PHYSICAL"
    BIOLOGICAL_ECOLOGICAL = "BIOLOGICAL_ECOLOGICAL"
    SYMBOLIC_MYTHIC = "SYMBOLIC_MYTHIC"
    BALANCE_ONLY = "BALANCE_ONLY"


class InvariantClass(str, Enum):
    """All 14 seed invariant catalog classes from invariant-translator."""

    STRESS_ACCUMULATION_THRESHOLD_RELEASE = "STRESS_ACCUMULATION_THRESHOLD_RELEASE"
    SELF_SUSTAINING_CHAIN_REACTION = "SELF_SUSTAINING_CHAIN_REACTION"
    REGULATION_ESCAPE_UNBOUNDED_REPLICATION = "REGULATION_ESCAPE_UNBOUNDED_REPLICATION"
    EXTRACTIVE_COUPLING = "EXTRACTIVE_COUPLING"
    MUTUAL_COUPLING = "MUTUAL_COUPLING"
    RESTRICTION_FOR_IMMUNITY_TRADE = "RESTRICTION_FOR_IMMUNITY_TRADE"
    BUFFER_WITH_RECHARGE_DELAY = "BUFFER_WITH_RECHARGE_DELAY"
    TYPED_FILTER_WITH_CAP = "TYPED_FILTER_WITH_CAP"
    VULNERABILITY_AMPLIFIER = "VULNERABILITY_AMPLIFIER"
    RATE_SUPPRESSION = "RATE_SUPPRESSION"
    CUMULATIVE_STACKING_TOXIN = "CUMULATIVE_STACKING_TOXIN"
    LOAD_COUPLED_LEAK = "LOAD_COUPLED_LEAK"
    ABSORB_CONVERT = "ABSORB_CONVERT"
    GENERATION_CONTROL_CYCLES = "GENERATION_CONTROL_CYCLES"


PRIMITIVE_GRAMMAR_KEYS: tuple[str, ...] = (
    "POOL",
    "CAPACITY_CAP",
    "INFLOW_REGEN",
    "OUTFLOW_DRAIN",
    "CHANNEL_TYPE",
    "FILTER_MITIGATION",
    "THRESHOLD",
    "TRIGGER",
    "RELEASE",
    "PROPAGATION",
    "TRADE_RESTRICTION",
    "IMMUNITY",
    "CONTROL_LOOP",
    "ESCAPE",
    "HOST_COUPLING",
    "FAILURE_MODE",
    "COUNTERPLAY",
)

CANONICAL_NINE_GATES: tuple[str, ...] = (
    "causal_validity",
    "scale_integrity",
    "boundary_integrity",
    "measurement_integrity",
    "authority_safety",
    "security_safety",
    "wave_function_coherence",
    "substrate_sovereignty",
    "corpus_completeness",
)

EGO_ARM_SPECIFICATIONS: dict[EgoArmInvariant, dict[str, Any]] = {
    EgoArmInvariant.ITACHI: {
        "arm_index": 1,
        "character": "Itachi Uchiha",
        "mechanical_invariant": "Sacrificial Information Asymmetry",
        "domain_type": "Tsukuyomi (perception domain)",
        "compiler_departments": ("SECURITY",),
        "cross_references": ("SC-NS-001", "SC-DR-001", "SC-TIG-001"),
    },
    EgoArmInvariant.SASUKE: {
        "arm_index": 2,
        "character": "Sasuke Uchiha",
        "mechanical_invariant": "Descent-and-Return Cycle",
        "domain_type": "Susano'o (evolving armor domain)",
        "compiler_departments": ("DELETION", "REPRODUCTION"),
        "cross_references": ("SC-CT-001", "SC-CP-001", "SC-DE-001"),
    },
    EgoArmInvariant.YUTA: {
        "arm_index": 3,
        "character": "Yuta Okkotsu",
        "mechanical_invariant": "Boundless Energy Reservoir + Copy",
        "domain_type": "Rika (infinite cursed energy domain)",
        "compiler_departments": ("ENERGY_INTAKE", "STORAGE"),
        "cross_references": ("SC-DE-001", "SC-DR-001", "SC-CP-001"),
    },
    EgoArmInvariant.TOJI: {
        "arm_index": 4,
        "character": "Toji Fushiguro",
        "mechanical_invariant": "Zero-Resource Supremacy",
        "domain_type": "Anti-Domain (null-cursed-energy domain)",
        "compiler_departments": ("WASTE_REMOVAL",),
        "cross_references": ("SC-NS-001", "SC-CP-001", "SC-DE-001"),
    },
    EgoArmInvariant.DANTE: {
        "arm_index": 5,
        "character": "Dante (Devil May Cry)",
        "mechanical_invariant": "Hybrid Substrate Mastery",
        "domain_type": "Devil Trigger (dual-nature domain)",
        "compiler_departments": ("PROCESSOR",),
        "cross_references": ("SC-CP-001", "SC-DR-001", "SC-DE-001"),
    },
    EgoArmInvariant.GUTS: {
        "arm_index": 6,
        "character": "Guts (Berserk)",
        "mechanical_invariant": "Anti-Fate Persistence Engine",
        "domain_type": "Berserker Armor (will-over-physics domain)",
        "compiler_departments": ("SUBCONSCIOUS",),
        "cross_references": ("SC-CT-001", "SC-DR-001", "SC-NS-001"),
    },
    EgoArmInvariant.GOJO: {
        "arm_index": 7,
        "character": "Gojo Satoru",
        "mechanical_invariant": "Infinity as Defensive Axiom",
        "domain_type": "Unlimited Void (totality domain)",
        "compiler_departments": ("INFORMATION_DENSITY",),
        "cross_references": ("SC-DE-001", "SC-TIG-001", "SC-CT-001"),
    },
    EgoArmInvariant.YAMI: {
        "arm_index": 8,
        "character": "Yami Sukehiro",
        "mechanical_invariant": "Limit-Break Through Darkness",
        "domain_type": "Dark Magic (boundary-transcendence domain)",
        "compiler_departments": ("TELECOMMUNICATIONS",),
        "cross_references": ("SC-DE-001", "SC-NS-001", "SC-CT-001"),
    },
}

_PRIMITIVE_KEY_ALIASES: dict[str, str] = {
    "POOL": "POOL",
    "CAPACITY_CAP": "CAPACITY_CAP",
    "CAPACITY": "CAPACITY_CAP",
    "CAP": "CAPACITY_CAP",
    "INFLOW_REGEN": "INFLOW_REGEN",
    "INFLOW": "INFLOW_REGEN",
    "REGEN": "INFLOW_REGEN",
    "OUTFLOW_DRAIN": "OUTFLOW_DRAIN",
    "OUTFLOW": "OUTFLOW_DRAIN",
    "DRAIN": "OUTFLOW_DRAIN",
    "CHANNEL_TYPE": "CHANNEL_TYPE",
    "CHANNEL": "CHANNEL_TYPE",
    "TYPE": "CHANNEL_TYPE",
    "FILTER_MITIGATION": "FILTER_MITIGATION",
    "FILTER": "FILTER_MITIGATION",
    "MITIGATION": "FILTER_MITIGATION",
    "THRESHOLD": "THRESHOLD",
    "TRIGGER": "TRIGGER",
    "RELEASE": "RELEASE",
    "PROPAGATION": "PROPAGATION",
    "TRADE_RESTRICTION": "TRADE_RESTRICTION",
    "TRADE": "TRADE_RESTRICTION",
    "RESTRICTION": "TRADE_RESTRICTION",
    "IMMUNITY": "IMMUNITY",
    "CONTROL_LOOP": "CONTROL_LOOP",
    "CONTROL": "CONTROL_LOOP",
    "ESCAPE": "ESCAPE",
    "HOST_COUPLING": "HOST_COUPLING",
    "HOST": "HOST_COUPLING",
    "COUPLING": "HOST_COUPLING",
    "FAILURE_MODE": "FAILURE_MODE",
    "FAILURE": "FAILURE_MODE",
    "COUNTERPLAY": "COUNTERPLAY",
}

_ABSENT_MARKERS: frozenset[str] = frozenset({"", "n/a", "na", "none", "absent", "null", "-"})

_STEM_CUES: frozenset[str] = frozenset({
    "accumulat",
    "discontinu",
    "parasit",
    "symbio",
    "mycorrhiz",
    "amplif",
    "throttl",
    "coloniz",
    "co-depend",
})

INVARIANT_CLASS_SIGNATURES: dict[InvariantClass, dict[str, Any]] = {
    InvariantClass.STRESS_ACCUMULATION_THRESHOLD_RELEASE: {
        "required_primitives": ("THRESHOLD", "TRIGGER", "RELEASE"),
        "supporting_primitives": ("POOL", "CAPACITY_CAP", "PROPAGATION", "COUNTERPLAY"),
        "cues": (
            "stress", "locked", "rupture", "aftershock", "instant release",
            "energy dump", "earthquake", "avalanche", "crash", "burnout",
            "controlled burn", "small release", "accumulat", "discontinu",
        ),
    },
    InvariantClass.SELF_SUSTAINING_CHAIN_REACTION: {
        "required_primitives": ("TRIGGER", "PROPAGATION"),
        "supporting_primitives": ("POOL", "OUTFLOW_DRAIN", "RELEASE", "COUNTERPLAY"),
        "cues": (
            "fuel", "oxidizer", "activation energy", "chain reaction", "exothermic",
            "ignite", "fire", "fission", "viral", "spread", "substrate",
            "feedback loop", "triangle", "self-sustaining", "smother",
        ),
    },
    InvariantClass.REGULATION_ESCAPE_UNBOUNDED_REPLICATION: {
        "required_primitives": ("CONTROL_LOOP", "ESCAPE"),
        "supporting_primitives": ("PROPAGATION", "FAILURE_MODE", "COUNTERPLAY"),
        "cues": (
            "apoptosis", "stop signal", "unbounded", "replication", "metastasis",
            "cancer", "fork bomb", "surveillance", "evasion", "angiogenesis",
            "regulatory capture", "monopoly", "coloniz", "misaligned subagent",
        ),
    },
    InvariantClass.EXTRACTIVE_COUPLING: {
        "required_primitives": ("HOST_COUPLING", "OUTFLOW_DRAIN"),
        "supporting_primitives": ("ESCAPE", "INFLOW_REGEN", "FAILURE_MODE"),
        "cues": (
            "parasit", "extractive", "hijack", "leech", "rent-seeking",
            "malware", "below host-kill", "siphon", "toxoplasma", "drains host",
        ),
    },
    InvariantClass.MUTUAL_COUPLING: {
        "required_primitives": ("HOST_COUPLING", "INFLOW_REGEN"),
        "supporting_primitives": ("POOL", "FAILURE_MODE", "CONTROL_LOOP"),
        "cues": (
            "mutual", "symbio", "mycorrhiz", "gut flora", "mitochondria",
            "both strengthen", "uncoupling harms both", "reciprocal", "pairing",
            "co-depend", "mutual trade",
        ),
    },
    InvariantClass.RESTRICTION_FOR_IMMUNITY_TRADE: {
        "required_primitives": ("TRADE_RESTRICTION", "IMMUNITY"),
        "supporting_primitives": ("POOL", "FILTER_MITIGATION", "FAILURE_MODE", "COUNTERPLAY"),
        "cues": (
            "chaos inoculation", "life=1", "life to 1", "heavenly restriction",
            "binding vow", "keystone", "delete", "vulnerability surface",
            "air-gap", "air gap", "zero cursed energy", "monastic",
            "single buffer", "bypass",
        ),
    },
    InvariantClass.BUFFER_WITH_RECHARGE_DELAY: {
        "required_primitives": ("POOL", "INFLOW_REGEN", "CONTROL_LOOP"),
        "supporting_primitives": ("CAPACITY_CAP", "OUTFLOW_DRAIN", "COUNTERPLAY"),
        "cues": (
            "recharge delay", "damage-free", "quiet time", "energy shield",
            "interrupt", "restart", "cooldown", "sustained pressure", "chip damage",
            "buffer", "refill", "cash reserve", "sleep",
        ),
    },
    InvariantClass.TYPED_FILTER_WITH_CAP: {
        "required_primitives": ("CHANNEL_TYPE", "FILTER_MITIGATION", "CAPACITY_CAP"),
        "supporting_primitives": ("COUNTERPLAY", "FAILURE_MODE"),
        "cues": (
            "75%", "resist cap", "hard ceiling", "channel-specific", "typed resist",
            "penetration", "armour", "evasion", "firewall", "adaptive immune",
            "mitigation cap", "typed filter",
        ),
    },
    InvariantClass.VULNERABILITY_AMPLIFIER: {
        "required_primitives": ("CHANNEL_TYPE",),
        "supporting_primitives": ("RELEASE", "THRESHOLD", "OUTFLOW_DRAIN", "FILTER_MITIGATION", "COUNTERPLAY"),
        "cues": (
            "shock", "amplif", "multiplies", "incoming damage", "incoming pressure",
            "vulnerability", "market panic", "compromised", "poisoned context",
            "jailbreak", "debuff",
        ),
    },
    InvariantClass.RATE_SUPPRESSION: {
        "required_primitives": ("CONTROL_LOOP",),
        "supporting_primitives": ("CHANNEL_TYPE", "THRESHOLD", "OUTFLOW_DRAIN", "COUNTERPLAY"),
        "cues": (
            "chill", "freeze", "action speed", "rate suppression", "slowdown",
            "slows action", "slowed", "throttl", "sedation", "rate braking",
            "rigid crystal", "brittle", "stasis",
        ),
    },
    InvariantClass.CUMULATIVE_STACKING_TOXIN: {
        "required_primitives": ("OUTFLOW_DRAIN",),
        "supporting_primitives": ("PROPAGATION", "CHANNEL_TYPE", "THRESHOLD", "CONTROL_LOOP", "COUNTERPLAY"),
        "cues": (
            "stacking", "stacks", "independent stack", "toxin", "poison",
            "badly poisoned", "toxic", "timer", "bioaccumulation", "heavy-metal",
            "technical debt", "cumulative", "exposure count", "degen",
        ),
    },
    InvariantClass.LOAD_COUPLED_LEAK: {
        "required_primitives": ("OUTFLOW_DRAIN", "TRIGGER"),
        "supporting_primitives": ("POOL", "FAILURE_MODE", "COUNTERPLAY"),
        "cues": (
            "bleed", "moving", "exertion", "under load", "memory leak",
            "hemorrhage", "attrition", "while active", "while moving",
            "accelerates while", "movement", "stand still",
        ),
    },
    InvariantClass.ABSORB_CONVERT: {
        "required_primitives": ("CHANNEL_TYPE", "INFLOW_REGEN", "IMMUNITY"),
        "supporting_primitives": ("FILTER_MITIGATION", "COUNTERPLAY"),
        "cues": (
            "absorb", "water absorb", "volt absorb", "flash fire", "sap sipper",
            "edge inversion", "rewired", "damage taken as", "heal", "feeds",
            "training signal", "convert", "reverse cursed",
        ),
    },
    InvariantClass.GENERATION_CONTROL_CYCLES: {
        "required_primitives": ("CONTROL_LOOP", "PROPAGATION"),
        "supporting_primitives": ("INFLOW_REGEN", "OUTFLOW_DRAIN", "CHANNEL_TYPE"),
        "cues": (
            "wu xing", "cycle", "closed loop", "rock-paper-scissors", "triangle",
            "predator-prey", "oscillation", "boom-bust", "generation", "feeds one",
            "suppresses another", "fire/water/grass", "nature cycle",
        ),
    },
}


def _compile_cue_pattern(cue: str) -> re.Pattern[str]:
    escaped = re.escape(cue)
    if cue in _STEM_CUES:
        return re.compile(rf"(?<![a-z0-9]){escaped}", re.IGNORECASE)
    # Allow optional simple English plural 's' for alphabetic words while keeping
    # strict word boundaries on both sides (so 'shock' never matches 'aftershock'
    # and 'fire' never matches 'firewall').
    if cue[-1].isalpha():
        return re.compile(rf"(?<![a-z0-9]){escaped}s?(?![a-z0-9])", re.IGNORECASE)
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)


_COMPILED_CLASS_CUES: dict[InvariantClass, tuple[tuple[str, re.Pattern[str]], ...]] = {
    inv_cls: tuple((cue, _compile_cue_pattern(cue)) for cue in sig["cues"])
    for inv_cls, sig in INVARIANT_CLASS_SIGNATURES.items()
}

_VARIANT_EFFECTS: dict[DomainVariant, str] = {
    DomainVariant.SIMPLE_DOMAIN: (
        "Narrow defensive pocket neutralizing external sure-hit pressure without projecting offense."
    ),
    DomainVariant.BARRIER_DOMAIN: (
        "Bounded operative domain guaranteeing sure-hit axiom enforcement strictly inside the barrier."
    ),
    DomainVariant.MALEVOLENT_SHRINE: (
        "Barrierless open domain operating directly on the substrate without an institutional wall."
    ),
    DomainVariant.UNLIMITED_VOID: (
        "Information-totality domain exceeding target processing capacity (Bekenstein bound paralysis)."
    ),
    DomainVariant.CHIMERA_SHADOW_GARDEN: (
        "Generative domain manifesting new instances directly from compiled internal representations."
    ),
}


def _validate_finite(
    name: str,
    value: float | int,
    *,
    low: float | None = None,
    high: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number, got {type(value).__name__}")
    val = float(value)
    if not math.isfinite(val):
        raise ValueError(f"{name} must be finite, got {value!r}")
    if low is not None and val < low:
        raise ValueError(f"{name} must be >= {low}, got {val}")
    if high is not None and val > high:
        raise ValueError(f"{name} must be <= {high}, got {val}")
    return val


def _validate_non_negative_int(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _validate_non_empty_str(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _validate_str_sequence(name: str, value: Sequence[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of strings, not a bare {type(value).__name__}")
    if not isinstance(value, Sequence):
        raise ValueError(f"{name} must be a sequence of strings, got {type(value).__name__}")
    return [str(item).strip() for item in value if str(item).strip()]


def _format_margin(raw_abs_diff: float) -> float:
    if raw_abs_diff == 0.0:
        return 0.0
    if raw_abs_diff < 1e-5:
        return round(raw_abs_diff, 9)
    return round(raw_abs_diff, 6)


def _resolve_enum(enum_cls: type[Enum], value: Enum | str, label: str) -> Any:
    if isinstance(value, enum_cls):
        return value
    if not isinstance(value, str):
        raise ValueError(f"Invalid {label}: {value!r}")
    normalized = re.sub(r"[\s/\-]+", "_", value.strip().upper()).strip("_")
    try:
        return enum_cls[normalized]
    except KeyError as exc:
        valid = ", ".join(m.name for m in enum_cls)
        raise ValueError(f"Unknown {label} {value!r}; expected one of: {valid}") from exc


def _normalize_primitive_key(raw_key: str) -> str | None:
    cleaned = re.sub(r"[\s/\-]+", "_", str(raw_key).strip().upper()).strip("_")
    return _PRIMITIVE_KEY_ALIASES.get(cleaned)


def evaluate_domain_expansion(
    *,
    model_compilation_completeness: float,
    within_scope: bool = True,
    has_barrier: bool = True,
    energy_available: float = 1.0,
    energy_required: float = 0.5,
    variant: DomainVariant | str | None = None,
    observer_observed_aligned: bool = False,
    anti_domain_negation: bool = False,
) -> dict[str, Any]:
    """
    Evaluate Domain Expansion operational state under SC-DOMAIN-EXPANSION-001 invariants.

    Key invariants enforced:
    1. Full Domain Expansion requires a compiled internal model (>= 0.85 completeness);
       between 0.40 and 0.85 it degrades to a defensive SIMPLE_DOMAIN; below 0.40 it fails.
    2. Guaranteed hit holds ONLY when expanded (non-Simple), inside operational scope,
       funded by sufficient energy, and not negated by an anti-domain mechanism (Toji).
    3. Barrierless expansion (MALEVOLENT_SHRINE) requires substrate-grade compilation (>= 0.95).
    4. Black Flash triggers when observer and observed align inside an active guaranteed-hit zone.
    """
    completeness = _validate_finite(
        "model_compilation_completeness", model_compilation_completeness, low=0.0, high=1.0
    )
    available = _validate_finite("energy_available", energy_available, low=0.0)
    required = _validate_finite("energy_required", energy_required, low=0.0)

    requested_variant: DomainVariant
    if variant is None:
        if not has_barrier:
            requested_variant = DomainVariant.MALEVOLENT_SHRINE
        else:
            requested_variant = DomainVariant.BARRIER_DOMAIN
    else:
        requested_variant = _resolve_enum(DomainVariant, variant, "DomainVariant")
        if not has_barrier and requested_variant in (
            DomainVariant.BARRIER_DOMAIN,
            DomainVariant.SIMPLE_DOMAIN,
        ):
            raise ValueError(f"{requested_variant.value} requires has_barrier=True")

    effective_has_barrier = (
        False if requested_variant == DomainVariant.MALEVOLENT_SHRINE else bool(has_barrier)
    )

    collapse_reason: str | None = None
    degraded_to_simple_domain = False
    effective_variant: DomainVariant | None = requested_variant
    domain_active = True

    if anti_domain_negation:
        domain_active = False
        effective_variant = None
        collapse_reason = "ANTI_DOMAIN_NEGATION"
    elif available < required:
        domain_active = False
        effective_variant = None
        collapse_reason = "ENERGY_DEPLETION"
    elif completeness < 0.40:
        domain_active = False
        effective_variant = None
        collapse_reason = "INSUFFICIENT_COMPILATION"
    elif requested_variant == DomainVariant.SIMPLE_DOMAIN:
        effective_variant = DomainVariant.SIMPLE_DOMAIN
        effective_has_barrier = True
        domain_active = True
    elif not effective_has_barrier:
        if completeness >= 0.95:
            effective_variant = requested_variant
            domain_active = True
        else:
            domain_active = False
            effective_variant = None
            collapse_reason = "BARRIERLESS_COMPILATION_INSUFFICIENT"
    elif completeness < 0.85:
        effective_variant = DomainVariant.SIMPLE_DOMAIN
        effective_has_barrier = True
        degraded_to_simple_domain = True
        domain_active = True

    defensive_only = effective_variant == DomainVariant.SIMPLE_DOMAIN
    guaranteed_hit = bool(
        domain_active
        and within_scope
        and not defensive_only
        and not anti_domain_negation
    )
    black_flash = bool(guaranteed_hit and observer_observed_aligned)
    energy_margin = round(available - required, 6)

    return {
        "entry_id": "SC-DOMAIN-EXPANSION-001",
        "requested_variant": requested_variant.value,
        "effective_variant": effective_variant.value if effective_variant else None,
        "domain_active": domain_active,
        "barrierless": bool(domain_active and not effective_has_barrier),
        "has_barrier": bool(domain_active and effective_has_barrier),
        "within_scope": bool(within_scope),
        "guaranteed_hit": guaranteed_hit,
        "defensive_only": defensive_only,
        "degraded_to_simple_domain": degraded_to_simple_domain,
        "black_flash": black_flash,
        "negated_by_anti_domain": bool(anti_domain_negation),
        "energy_margin": energy_margin,
        "collapse_reason": collapse_reason,
        "operational_effect": (
            _VARIANT_EFFECTS[effective_variant]
            if effective_variant is not None
            else f"Domain inactive ({collapse_reason})."
        ),
    }


def evaluate_domain_clash(
    *,
    domain_a_refinement: float,
    domain_b_refinement: float,
    domain_a_name: str = "domain_a",
    domain_b_name: str = "domain_b",
    domain_a_barrierless: bool = False,
    domain_b_barrierless: bool = False,
    domain_a_anti_domain: bool = False,
    domain_b_anti_domain: bool = False,
    domain_a_energy_ratio: float = 1.0,
    domain_b_energy_ratio: float = 1.0,
    tie_tolerance: float = 0.02,
) -> dict[str, Any]:
    """
    Adjudicate a Domain Clash between two competing domains.

    Rules from SC-DOMAIN-EXPANSION-001 & EGO_LINEUP_DOMAIN_EXPANSION_MAP.md:
    - Anti-domain negation (Toji / Inverted Spear) wins by negating the paradigm itself
      unless both sides wield anti-domain negation (mutual collapse).
    - Exhausted energy (<= 0.0) collapses the depleted domain immediately.
    - Structural refinement is the primary arbiter.
    - A barrierless substrate-grade domain (Malevolent Shrine) gains a bounded exterior
      shell breach bonus (+0.05) against an opponent relying on a closed barrier.
    """
    ref_a = _validate_finite("domain_a_refinement", domain_a_refinement, low=0.0, high=1.0)
    ref_b = _validate_finite("domain_b_refinement", domain_b_refinement, low=0.0, high=1.0)
    eng_a = _validate_finite("domain_a_energy_ratio", domain_a_energy_ratio, low=0.0)
    eng_b = _validate_finite("domain_b_energy_ratio", domain_b_energy_ratio, low=0.0)
    tol = _validate_finite("tie_tolerance", tie_tolerance, low=0.0, high=1.0)

    if domain_a_anti_domain and domain_b_anti_domain:
        return {
            "entry_id": "SC-DOMAIN-EXPANSION-001",
            "winner": None,
            "loser": None,
            "resolution_mode": "MUTUAL_ANTI_DOMAIN_NEGATION",
            "margin": 0.0,
            "effective_refinement_a": ref_a,
            "effective_refinement_b": ref_b,
            "summary": "Both sides deploy anti-domain negation; both domains collapse into neutral space.",
        }
    if domain_a_anti_domain:
        return {
            "entry_id": "SC-DOMAIN-EXPANSION-001",
            "winner": domain_a_name,
            "loser": domain_b_name,
            "resolution_mode": "ANTI_DOMAIN_NEGATION",
            "margin": round(abs(ref_a - ref_b), 6),
            "effective_refinement_a": ref_a,
            "effective_refinement_b": ref_b,
            "summary": f"{domain_a_name} wins by anti-domain negation, nullifying {domain_b_name}'s guaranteed hit.",
        }
    if domain_b_anti_domain:
        return {
            "entry_id": "SC-DOMAIN-EXPANSION-001",
            "winner": domain_b_name,
            "loser": domain_a_name,
            "resolution_mode": "ANTI_DOMAIN_NEGATION",
            "margin": round(abs(ref_b - ref_a), 6),
            "effective_refinement_a": ref_a,
            "effective_refinement_b": ref_b,
            "summary": f"{domain_b_name} wins by anti-domain negation, nullifying {domain_a_name}'s guaranteed hit.",
        }

    if eng_a == 0.0 and eng_b == 0.0:
        return {
            "entry_id": "SC-DOMAIN-EXPANSION-001",
            "winner": None,
            "loser": None,
            "resolution_mode": "MUTUAL_ENERGY_COLLAPSE",
            "margin": 0.0,
            "effective_refinement_a": 0.0,
            "effective_refinement_b": 0.0,
            "summary": "Both competing domains collapsed due to energy exhaustion.",
        }
    if eng_a == 0.0:
        return {
            "entry_id": "SC-DOMAIN-EXPANSION-001",
            "winner": domain_b_name,
            "loser": domain_a_name,
            "resolution_mode": "ENERGY_COLLAPSE_DEFAULT",
            "margin": round(ref_b, 6),
            "effective_refinement_a": 0.0,
            "effective_refinement_b": ref_b,
            "summary": f"{domain_a_name} collapsed from energy depletion; {domain_b_name} prevails.",
        }
    if eng_b == 0.0:
        return {
            "entry_id": "SC-DOMAIN-EXPANSION-001",
            "winner": domain_a_name,
            "loser": domain_b_name,
            "resolution_mode": "ENERGY_COLLAPSE_DEFAULT",
            "margin": round(ref_a, 6),
            "effective_refinement_a": ref_a,
            "effective_refinement_b": 0.0,
            "summary": f"{domain_b_name} collapsed from energy depletion; {domain_a_name} prevails.",
        }

    exterior_bonus_a = 0.05 if (domain_a_barrierless and not domain_b_barrierless and ref_a >= 0.90) else 0.0
    exterior_bonus_b = 0.05 if (domain_b_barrierless and not domain_a_barrierless and ref_b >= 0.90) else 0.0
    eff_a = ref_a + exterior_bonus_a
    eff_b = ref_b + exterior_bonus_b
    raw_diff = eff_a - eff_b
    eps = 1e-12

    if abs(raw_diff) <= tol + eps:
        return {
            "entry_id": "SC-DOMAIN-EXPANSION-001",
            "winner": None,
            "loser": None,
            "resolution_mode": "TUG_OF_WAR_STALEMATE",
            "margin": _format_margin(abs(raw_diff)),
            "effective_refinement_a": round(eff_a, 6),
            "effective_refinement_b": round(eff_b, 6),
            "summary": "Competing domains have equivalent refinement; sure-hit effects cancel in stalemate.",
        }

    if raw_diff > 0:
        winner, loser = domain_a_name, domain_b_name
        # Barrierless exterior breach applies only when A would NOT already win
        # on raw structural refinement alone.
        won_without_bonus = (ref_a - ref_b) > (tol + eps)
        mode = (
            "BARRIERLESS_EXTERIOR_BREACH"
            if (exterior_bonus_a > 0.0 and not won_without_bonus)
            else "REFINEMENT_SUPERIORITY"
        )
    else:
        winner, loser = domain_b_name, domain_a_name
        won_without_bonus = (ref_b - ref_a) > (tol + eps)
        mode = (
            "BARRIERLESS_EXTERIOR_BREACH"
            if (exterior_bonus_b > 0.0 and not won_without_bonus)
            else "REFINEMENT_SUPERIORITY"
        )

    return {
        "entry_id": "SC-DOMAIN-EXPANSION-001",
        "winner": winner,
        "loser": loser,
        "resolution_mode": mode,
        "margin": _format_margin(abs(raw_diff)),
        "effective_refinement_a": round(eff_a, 6),
        "effective_refinement_b": round(eff_b, 6),
        "summary": f"{winner} overwhelms {loser} via {mode.lower().replace('_', ' ')}.",
    }


def evaluate_soul_eater_compounding(
    *,
    mapped_domains: int,
    base_domain_value: float = 1.0,
    cross_link_density: float = 1.0,
    weapon_copy_order_efficiency: float = 1.0,
) -> dict[str, Any]:
    """
    Model PoE Soul Eater multiplicative compounding & Mega Man weapon-copy acquisition.

    Every newly absorbed domain creates cross-links to all prior compiled domains:
        pairwise_cross_links = n * (n - 1) / 2
        compounded_value = (n + cross_link_density * pairwise_cross_links) * base * order_eff
    """
    n = _validate_non_negative_int("mapped_domains", mapped_domains)
    base = _validate_finite("base_domain_value", base_domain_value, low=0.0)
    density = _validate_finite("cross_link_density", cross_link_density, low=0.0, high=1.0)
    order_eff = _validate_finite("weapon_copy_order_efficiency", weapon_copy_order_efficiency, low=0.0)
    if order_eff == 0.0:
        raise ValueError("weapon_copy_order_efficiency must be > 0")

    additive_value = round(n * base, 6)
    pairwise_cross_links = (n * (n - 1)) // 2
    effective_cross_links = round(pairwise_cross_links * density, 6)
    compounded_value = round((additive_value + effective_cross_links * base) * order_eff, 6)
    compounding_multiplier = round(compounded_value / additive_value, 6) if additive_value > 0 else 0.0

    return {
        "entry_id": "SC-DOMAIN-EXPANSION-001",
        "mapped_domains": n,
        "base_domain_value": base,
        "cross_link_density": density,
        "weapon_copy_order_efficiency": order_eff,
        "additive_value": additive_value,
        "pairwise_cross_links": pairwise_cross_links,
        "effective_cross_links": effective_cross_links,
        "compounded_value": compounded_value,
        "compounding_multiplier": compounding_multiplier,
        "is_super_additive": compounded_value > additive_value,
        "mega_man_full_loadout": n >= 8,
    }


def evaluate_ego_lineup_composite(
    *,
    active_arms: Sequence[EgoArmInvariant | str] | None = None,
    gates_passed: int = 9,
    total_gates: int = 9,
    target_aligned: bool = False,
) -> dict[str, Any]:
    """
    Evaluate the 8-arm Octopus Protocol composite Domain Expansion from
    EGO_LINEUP_DOMAIN_EXPANSION_MAP.md.
    """
    passed = _validate_non_negative_int("gates_passed", gates_passed)
    total = _validate_non_negative_int("total_gates", total_gates)
    if total < 1:
        raise ValueError("total_gates must be >= 1")
    if passed > total:
        raise ValueError(f"gates_passed ({passed}) cannot exceed total_gates ({total})")

    if active_arms is None:
        resolved_set = set(EgoArmInvariant)
    else:
        if isinstance(active_arms, (str, bytes)) or not isinstance(active_arms, Sequence):
            raise ValueError(
                "active_arms must be a sequence of EgoArmInvariant values, not a bare string"
            )
        resolved_set = {_resolve_enum(EgoArmInvariant, arm, "EgoArmInvariant") for arm in active_arms}

    ordered_active = [arm for arm in EgoArmInvariant if arm in resolved_set]
    ordered_missing = [arm for arm in EgoArmInvariant if arm not in resolved_set]

    arm_details: list[dict[str, Any]] = []
    departments: set[str] = set()
    for arm in ordered_active:
        spec = EGO_ARM_SPECIFICATIONS[arm]
        departments.update(spec["compiler_departments"])
        arm_details.append({
            "arm": arm.value,
            "arm_index": spec["arm_index"],
            "character": spec["character"],
            "mechanical_invariant": spec["mechanical_invariant"],
            "domain_type": spec["domain_type"],
            "compiler_departments": list(spec["compiler_departments"]),
            "cross_references": list(spec["cross_references"]),
        })

    arm_count = len(ordered_active)
    full_loadout = arm_count == len(EgoArmInvariant)
    barrier_intact = (total >= len(CANONICAL_NINE_GATES) and passed == total)
    black_flash_triggered = bool(full_loadout and barrier_intact and target_aligned)
    soul_eater = evaluate_soul_eater_compounding(mapped_domains=arm_count)

    return {
        "entry_id": "SC-DOMAIN-EXPANSION-001",
        "head_role": "SOURCE_META_DOMAIN",
        "active_arms": arm_details,
        "missing_arms": [arm.value for arm in ordered_missing],
        "arm_count": arm_count,
        "total_arms": len(EgoArmInvariant),
        "coverage_ratio": round(arm_count / len(EgoArmInvariant), 6),
        "covered_departments": sorted(departments),
        "full_loadout": full_loadout,
        "gates_passed": passed,
        "total_gates": total,
        "barrier_intact": barrier_intact,
        "black_flash_triggered": black_flash_triggered,
        "soul_eater_projection": soul_eater,
    }


def classify_primitive_signature(
    primitives: Mapping[str, str | None],
    *,
    min_score: float = 0.25,
    top_k: int | None = None,
) -> dict[str, Any]:
    """
    Match a 17-primitive mechanical signature against all 14 seed InvariantClass profiles.

    Accepts either canonical keys (e.g., ``CAPACITY_CAP``, ``INFLOW_REGEN``) or
    display labels from ``invariant-translator`` (e.g., ``CAPACITY / CAP``).
    Genuine ``"N/A"`` / empty entries are recorded as absent structural data.
    """
    if not isinstance(primitives, Mapping):
        raise ValueError(f"primitives must be a mapping, got {type(primitives).__name__}")
    threshold = _validate_finite("min_score", min_score, low=0.0, high=1.0)
    if top_k is not None:
        _validate_non_negative_int("top_k", top_k)

    normalized_values: dict[str, str] = {}
    unknown_keys: list[str] = []

    for raw_key, raw_val in primitives.items():
        canon = _normalize_primitive_key(raw_key)
        if canon is None:
            unknown_keys.append(str(raw_key))
            continue
        text = "" if raw_val is None else str(raw_val).strip()
        if text.lower() not in _ABSENT_MARKERS:
            if canon in normalized_values:
                normalized_values[canon] = f"{normalized_values[canon]}; {text}"
            else:
                normalized_values[canon] = text

    present_primitives = [k for k in PRIMITIVE_GRAMMAR_KEYS if k in normalized_values]
    absent_primitives = [k for k in PRIMITIVE_GRAMMAR_KEYS if k not in normalized_values]
    present_set = set(present_primitives)
    combined_text = " ".join(normalized_values.values()).lower()

    matches: list[dict[str, Any]] = []
    if present_set:
        for inv_cls in InvariantClass:
            sig = INVARIANT_CLASS_SIGNATURES[inv_cls]
            req = sig["required_primitives"]
            sup = sig["supporting_primitives"]

            req_hits = [p for p in req if p in present_set]
            sup_hits = [p for p in sup if p in present_set]
            cue_hits = [
                cue
                for cue, pattern in _COMPILED_CLASS_CUES[inv_cls]
                if pattern.search(combined_text)
            ]

            req_ratio = len(req_hits) / len(req)
            sup_ratio = len(sup_hits) / len(sup) if sup else 0.0
            if not req_hits and not cue_hits:
                continue

            # Structural presence score (0.0 .. 0.45) + semantic cue match score (0.0 .. 0.55)
            # Requiring at least one cue or full required structural fit keeps precision high.
            structural_score = 0.35 * req_ratio + 0.10 * sup_ratio
            cue_score = min(1.0, len(cue_hits) / 3.0) * 0.55
            # Penalize candidates missing required primitives so unrelated classes don't crowd out.
            if req_ratio < 1.0:
                structural_score *= 0.6
            if not cue_hits:
                score = round(structural_score * 0.5, 6)
            else:
                score = round(min(1.0, structural_score + cue_score), 6)

            if score >= threshold:
                matches.append({
                    "invariant_class": inv_cls.value,
                    "score": score,
                    "matched_required_primitives": req_hits,
                    "matched_supporting_primitives": sup_hits,
                    "matched_cues": cue_hits,
                })

    matches.sort(key=lambda m: (-m["score"], m["invariant_class"]))
    total_match_count = len(matches)
    if top_k is not None:
        matches = matches[:top_k]

    return {
        "primary_class": matches[0]["invariant_class"] if matches else None,
        "matches": matches,
        "total_match_count": total_match_count,
        "requires_new_catalog_class": total_match_count == 0,
        "present_primitives": present_primitives,
        "absent_primitives": absent_primitives,
        "unknown_keys": sorted(unknown_keys),
        "completeness_ratio": round(len(present_primitives) / len(PRIMITIVE_GRAMMAR_KEYS), 6),
    }


def evaluate_invariant_prediction(
    *,
    source_domain: str,
    target_domain: str,
    source_failure_or_counterplay: str,
    predicted_target_counterpart: str,
    ground_class: GroundClass | str = GroundClass.PHYSICAL,
    prediction_tested: bool = False,
    prediction_confirmed: bool = False,
    strength_match_only: bool = False,
    source_is_fiction_or_game: bool = False,
    target_is_real_system: bool = False,
    information_lost: Sequence[str] | None = None,
    evidence_ids: Sequence[str] | None = None,
    raw_gate_scores: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """
    Enforce invariant-translator Sections 4, 9, and 10 prediction & gate discipline:

    - Real invariants transfer weaknesses/counterplay and require a tested, confirmed
      prediction backed by concrete ``evidence_ids`` -> ``ISOMORPHIC_INVARIANT``.
    - Strength-only matches classify as ``STRUCTURAL_ANALOGY``.
    - Failed predictions or ``BALANCE_ONLY`` edges classify as ``RESIDUAL_MISMATCH``
      and emit mandatory ``residual_mismatches`` entries.
    - Whenever ``information_lost`` is non-empty, ``residual_mismatches`` is guaranteed
      non-empty.
    - Untested or un-evidenced gates are strictly capped at ``0.9`` (``1.0`` requires
      a passed prediction test with concrete ``evidence_ids``).
    - Fiction/game -> real-system mappings always enforce ``identity_claim_allowed: False``.
    - ``uncertainty_statement`` explicitly lists every untested prediction.
    """
    src_domain = _validate_non_empty_str("source_domain", source_domain)
    tgt_domain = _validate_non_empty_str("target_domain", target_domain)
    src_failure = _validate_non_empty_str("source_failure_or_counterplay", source_failure_or_counterplay)
    tgt_counterpart = _validate_non_empty_str("predicted_target_counterpart", predicted_target_counterpart)

    if prediction_confirmed and not prediction_tested:
        raise ValueError("prediction_confirmed cannot be True when prediction_tested is False")

    resolved_ground = _resolve_enum(GroundClass, ground_class, "GroundClass")
    info_lost = _validate_str_sequence("information_lost", information_lost)
    ev_ids = _validate_str_sequence("evidence_ids", evidence_ids)

    residual_mismatches: list[str] = []
    untested_predictions: list[str] = []
    prediction_summary = (
        f"{src_domain}({src_failure}) -> "
        f"{tgt_domain}({tgt_counterpart})"
    )

    if resolved_ground == GroundClass.BALANCE_ONLY:
        residual_mismatches.append(
            f"BALANCE_ONLY edge has zero external invariant ({prediction_summary}); "
            "mandatory residual mismatch."
        )

    if not prediction_tested:
        untested_predictions.append(prediction_summary)
    elif prediction_confirmed and not ev_ids:
        untested_predictions.append(
            f"{prediction_summary} [confirmed claim lacks concrete evidence_ids]"
        )

    if prediction_tested and not prediction_confirmed:
        residual_mismatches.append(
            f"Falsified counterplay prediction ({prediction_summary}): structure breaks in target domain."
        )

    if resolved_ground == GroundClass.BALANCE_ONLY:
        classification = "RESIDUAL_MISMATCH"
    elif prediction_tested and not prediction_confirmed:
        classification = "RESIDUAL_MISMATCH"
    elif strength_match_only:
        classification = "STRUCTURAL_ANALOGY"
    elif prediction_tested and prediction_confirmed and ev_ids:
        classification = "ISOMORPHIC_INVARIANT"
    else:
        classification = "UNTESTED_HYPOTHESIS"

    if info_lost:
        for lost in info_lost:
            residual_mismatches.append(f"Information lost across translation: {lost}")

    can_reach_one = (
        classification == "ISOMORPHIC_INVARIANT"
        and prediction_tested
        and prediction_confirmed
        and bool(ev_ids)
        and resolved_ground != GroundClass.BALANCE_ONLY
    )
    max_allowed_gate_score = 1.0 if can_reach_one else 0.9

    base_scores: dict[str, float] = {}
    if raw_gate_scores is None:
        default_score = 1.0 if can_reach_one else 0.9
        for gate in CANONICAL_NINE_GATES:
            base_scores[gate] = default_score
    else:
        if not isinstance(raw_gate_scores, Mapping):
            raise ValueError(
                f"raw_gate_scores must be a mapping, got {type(raw_gate_scores).__name__}"
            )
        canonical_gate_set = set(CANONICAL_NINE_GATES)
        for gate, val in raw_gate_scores.items():
            gate_name = str(gate)
            if gate_name not in canonical_gate_set:
                raise ValueError(
                    f"Unknown gate {gate!r}; expected one of: {', '.join(CANONICAL_NINE_GATES)}"
                )
            base_scores[gate_name] = _validate_finite(f"gate_score[{gate_name}]", val, low=0.0, high=1.0)

    capped_gate_scores: dict[str, float] = {}
    gate_cap_applied = False
    for gate, score in base_scores.items():
        if score > max_allowed_gate_score:
            capped_gate_scores[gate] = max_allowed_gate_score
            gate_cap_applied = True
        else:
            capped_gate_scores[gate] = round(score, 6)

    fiction_to_real = bool(source_is_fiction_or_game and target_is_real_system)
    identity_claim_allowed = bool(
        not fiction_to_real
        and resolved_ground != GroundClass.BALANCE_ONLY
        and classification == "ISOMORPHIC_INVARIANT"
    )

    if untested_predictions and resolved_ground == GroundClass.BALANCE_ONLY:
        uncertainty_statement = (
            "BALANCE_ONLY edge has no external invariant (recorded in residual_mismatches) "
            "and untested predictions cap gate scores at 0.9: "
            + "; ".join(untested_predictions)
        )
    elif untested_predictions:
        uncertainty_statement = (
            "Untested or un-evidenced predictions cap gate scores at 0.9: "
            + "; ".join(untested_predictions)
        )
    elif classification == "RESIDUAL_MISMATCH":
        uncertainty_statement = (
            f"Prediction rejected or BALANCE_ONLY ({prediction_summary}); "
            "structural break recorded in residual_mismatches."
        )
    elif classification == "STRUCTURAL_ANALOGY":
        uncertainty_statement = (
            f"Strength-only correspondence ({prediction_summary}); "
            "counterplay transfer not established, capped at 0.9."
        )
    else:
        uncertainty_statement = (
            f"Counterplay prediction verified for {prediction_summary} "
            f"with evidence_ids={ev_ids}."
        )

    return {
        "source_domain": src_domain,
        "target_domain": tgt_domain,
        "source_failure_or_counterplay": src_failure,
        "predicted_target_counterpart": tgt_counterpart,
        "ground_class": resolved_ground.value,
        "classification": classification,
        "prediction_tested": bool(prediction_tested),
        "prediction_confirmed": bool(prediction_confirmed),
        "strength_match_only": bool(strength_match_only),
        "evidence_ids": ev_ids,
        "information_lost": info_lost,
        "residual_mismatches": residual_mismatches,
        "untested_predictions": untested_predictions,
        "max_allowed_gate_score": max_allowed_gate_score,
        "gate_cap_applied": gate_cap_applied,
        "gate_scores": capped_gate_scores,
        "identity_claim_allowed": identity_claim_allowed,
        "uncertainty_statement": uncertainty_statement,
    }
