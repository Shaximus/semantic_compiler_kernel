"""Line-preserving PoE gem -> inference mechanic translation.

The source wording is retained exactly as supplied by the versioned corpus. Each
line is converted independently; unsupported clauses remain UNRESOLVED instead of
being smoothed into a persuasive but false analogue.
"""
from __future__ import annotations

import re
from typing import Callable

from semantic_compiler.expansion.gem_forge.models import GemTranslation, LineTranslation, PoeGem
from semantic_compiler.expansion.gem_forge.taxonomy import extract_domains, extract_primitives, normalize_text


Converter = Callable[[str], tuple[str, tuple[str, ...]] | None]


def _sub_numbers(line: str, replacement: str) -> str:
    match = re.search(r"\(([^)]+)\)", line)
    if match:
        replacement = replacement.replace("{range}", f"({match.group(1)})")
    else:
        replacement = replacement.replace("{range}", "")
    numbers = re.findall(r"\b\d+(?:\.\d+)?%?\b", line)
    for index, number in enumerate(numbers):
        replacement = replacement.replace(f"{{n{index}}}", number)
    return re.sub(r"\s+", " ", replacement).strip()


def _additional_projectiles(line: str):
    if "additional projectile" not in line.casefold():
        return None
    converted = re.sub(
        r"(?i)(fire|fires|has|have)?\s*(\d+)\s+additional projectiles?",
        lambda m: f"predicts {m.group(2)} additional future Token Positions per decoding step",
        line,
    )
    converted = converted.replace("Projectiles", "Token Positions").replace("projectiles", "Token Positions")
    return converted, ("EMIT_ADDITIONAL_CANDIDATES",)


def _less_projectile_damage(line: str):
    lower = line.casefold()
    if "less projectile damage" not in lower:
        return None
    converted = re.sub(
        r"(?i)supported skills deal\s*(\([^)]+\)|\d+(?:\.\d+)?%)\s*less projectile damage",
        r"Additional Token Positions have \1 less Acceptance-Weighted Effectiveness",
        line,
    )
    return converted, ("REDUCE_PER_CANDIDATE_EFFECTIVENESS", "SCALE_WITH_DISTANCE_OR_HORIZON")


def _increased_projectile_damage(line: str):
    lower = line.casefold()
    if "increased projectile damage" not in lower:
        return None
    converted = re.sub(
        r"(?i)supported skills deal\s*(\([^)]+\)|\d+(?:\.\d+)?%)\s*increased projectile damage",
        r"Additional Token Positions have \1 increased Acceptance-Weighted Effectiveness",
        line,
    )
    return converted, ("REDUCE_PER_CANDIDATE_EFFECTIVENESS",)


def _cost_multiplier(line: str):
    if "cost" not in line.casefold() or "multiplier" not in line.casefold():
        return None
    converted = re.sub(r"(?i)cost\s*(?:&|and)?\s*reservation multiplier", "Compute & KV Multiplier", line)
    converted = re.sub(r"(?i)cost multiplier", "Compute Multiplier", converted)
    return converted, ("INCREASE_EXECUTION_COST",)


def _supports_projectile_skills(line: str):
    if normalize_text((line,)) not in {"supports projectile skills", "supports projectile skills."}:
        return None
    return "Supports autoregressive inference skills with multi-position candidate generation.", ("FILTER_TARGETS",)


def _critical_trigger(line: str):
    lower = line.casefold()
    # Trigger semantics only: pure crit-chance stat lines belong to the
    # damage/qualification family, not the trigger controller.
    if "cast on crit" not in lower and "trigger" not in lower and "when you deal a critical strike" not in lower:
        return None
    converted = line
    converted = re.sub(r"(?i)critical strike", "accepted qualification event", converted)
    converted = re.sub(r"(?i)critical", "qualified", converted)
    converted = re.sub(r"(?i)cast", "execute", converted)
    converted = re.sub(r"(?i)spell", "verified payload", converted)
    converted = re.sub(r"(?i)attack", "draft proposal stream", converted)
    return converted, ("TRIGGER_ON_QUALIFICATION", "GATE_BY_CONFIDENCE")


def _cooldown(line: str):
    if "cooldown" not in line.casefold() and "recovery time" not in line.casefold():
        return None
    converted = re.sub(r"(?i)cooldown recovery rate", "Verifier Recovery Rate", line)
    converted = re.sub(r"(?i)cooldown", "execution recovery window", converted)
    return converted, ("APPLY_COOLDOWN", "RECOVER_COOLDOWN")


def _reservation(line: str):
    lower = line.casefold()
    if "reservation" not in lower:
        return None
    if "reduced" in lower or "less" in lower or "efficiency" in lower:
        converted = re.sub(r"(?i)mana reservation", "Persistent-Service Reservation", line)
        converted = re.sub(r"(?i)reservation", "Persistent-Service Reservation", converted)
        return converted, ("REDUCE_RESERVATION",)
    converted = re.sub(r"(?i)mana reservation", "Persistent-Service Reservation", line)
    return converted, ("RESERVE_CAPACITY",)


def _repeat(line: str):
    lower = line.casefold()
    if not any(term in lower for term in ("repeat", "repeats", "spell echo", "multistrike")):
        return None
    converted = re.sub(r"(?i)spell", "inference payload", line)
    converted = re.sub(r"(?i)attack", "inference action", converted)
    converted = re.sub(r"(?i)repeat", "re-execute", converted)
    return converted, ("REPEAT_EXECUTION",)


def _chain(line: str):
    if "chain" not in line.casefold():
        return None
    converted = re.sub(r"(?i)projectiles?", "candidate trajectories", line)
    converted = re.sub(r"(?i)enemies|targets", "eligible downstream tasks", converted)
    converted = re.sub(r"(?i)chain", "route onward", converted)
    return converted, ("CHAIN_TO_NEW_TARGET",)


def _return(line: str):
    if "return" not in line.casefold():
        return None
    converted = re.sub(r"(?i)projectiles?", "candidate branches", line)
    converted = re.sub(r"(?i)return", "return rejection and acceptance evidence", converted)
    return converted, ("RETURN_BRANCH_FEEDBACK", "MERGE_RESULTS", "DEDUPLICATE_RESULTS")


def _aura(line: str):
    lower = line.casefold()
    if "aura" not in lower and "nearby allies" not in lower:
        return None
    converted = re.sub(r"(?i)nearby allies", "compatible agents and services in the declared scope", line)
    converted = re.sub(r"(?i)aura", "persistent shared modifier field", converted)
    return converted, ("PERSISTENT_SHARED_MODIFIER", "SHARE_STATE")


def _proxy(line: str):
    lower = line.casefold()
    if not any(term in lower for term in ("totem", "trap", "mine")):
        return None
    converted = re.sub(r"(?i)totem|trap|mine", "bounded proxy worker", line)
    converted = re.sub(r"(?i)skill", "inference operation", converted)
    return converted, ("PROXY_EXECUTION",)


def _duration(line: str):
    lower = line.casefold()
    if "duration" not in lower:
        return None
    primitive = "EXTEND_DURATION" if "increased" in lower or "more" in lower else "REDUCE_DURATION"
    converted = re.sub(r"(?i)duration", "state-retention duration", line)
    return converted, (primitive,)


def _area(line: str):
    lower = line.casefold()
    if "damage" in lower:
        return None  # area-damage lines belong to the damage family
    if "area of effect" not in lower and "area" not in lower and "radius" not in lower and "range" not in lower:
        return None
    primitive = "REDUCE_AREA_OR_SCOPE" if "less" in lower or "reduced" in lower else "INCREASE_AREA_OR_SCOPE"
    converted = re.sub(r"(?i)area of effect", "affected inference scope", line)
    converted = re.sub(r"(?i)area", "scope", converted)
    converted = re.sub(r"(?i)radius", "scope radius", converted)
    converted = re.sub(r"(?i)range", "scope range", converted)
    return converted, (primitive,)


# ---------------------------------------------------------------------------
# Gate-5 mechanic-family converters (acceptance-gate corpus coverage).
# Ordered AFTER the swarm's specific converters so specialized translations
# keep their wording; predicates are designed to stay disjoint where the
# mechanics are genuinely different, and honest PARTIAL where they overlap.
# ---------------------------------------------------------------------------

def _annotation(line: str):
    stripped = line.strip()
    if stripped.startswith("[DNT]") or stripped.startswith("[UNUSED]") or stripped == "Not used":
        return f"non-mechanical annotation — excluded from mechanics: {stripped}", ()
    return None


def _maximum_cap(line: str):
    if not re.match(r"(?i)maximum \d+", line.strip()):
        return None
    converted = re.sub(r"(?i)^maximum (\d+)", r"Concurrency cap: \1", line.strip())
    return converted, ("CAP_CONCURRENCY",)


def _minion(line: str):
    lower = line.casefold()
    if not any(term in lower for term in ("minion", "golem", "spectre", "zombie", "skeleton", "animated guardian", "animated weapon")):
        return None
    converted = re.sub(r"(?i)minions?", "proxy workers", line)
    converted = re.sub(r"(?i)(golem|spectre|zombie|skeleton)s?", r"proxy \1s", converted)
    converted = re.sub(r"(?i)animated (guardian|weapon)", r"persistent proxy \1", converted)
    converted = re.sub(r"(?i)damage", "Output Effectiveness", converted)
    primitives = ["PROXY_EXECUTION"]
    if "output effectiveness" in converted.casefold():
        primitives.append("SCALE_OUTPUT_EFFECTIVENESS")
    return converted, tuple(primitives)


def _damage_offense(line: str):
    lower = line.casefold()
    if "damage" not in lower and "critical strike" not in lower and "accuracy" not in lower:
        return None
    # Disjointness: projectile/trigger lines are owned upstream; minion,
    # ailment, and leech lines are owned by their own family converters.
    if "projectile damage" in lower or "trigger" in lower or "cast on" in lower:
        return None
    if "minion" in lower or "leech" in lower:
        return None
    if any(term in lower for term in ("poison", "bleed", "ignite", "burn", "chill", "freeze", "shock", "ailment")):
        return None
    converted = re.sub(r"(?i)area damage", "Scoped Output Effectiveness", line)
    primitives: list[str] = []
    if "critical strike chance" in lower:
        converted = re.sub(r"(?i)critical strike chance", "Qualification Probability", converted)
        primitives.append("SCALE_QUALIFICATION_PROBABILITY")
    if "critical strike multiplier" in lower:
        converted = re.sub(r"(?i)critical strike multiplier", "Qualified-Payload Impact Multiplier", converted)
        primitives.append("SCALE_QUALIFICATION_PROBABILITY")
    if re.search(r"\bcritical strikes?\b", lower):
        converted = re.sub(r"(?i)critical strikes?", "qualified payloads", converted)
        primitives.append("SCALE_QUALIFICATION_PROBABILITY")
    if re.search(r"\baccuracy\b", lower):
        converted = re.sub(r"(?i)accuracy", "Proposal Alignment", converted)
        primitives.append("GATE_BY_CONFIDENCE")
    if "damage" in converted.casefold():
        converted = re.sub(r"(?i)damage", "Output Effectiveness", converted)
        primitives.append("SCALE_OUTPUT_EFFECTIVENESS")
    return converted, tuple(dict.fromkeys(primitives))


def _speed(line: str):
    lower = line.casefold()
    if "speed" not in lower or "cooldown" in lower:
        return None
    converted = re.sub(r"(?i)attack speed", "proposal cadence", line)
    converted = re.sub(r"(?i)cast speed", "generation cadence", converted)
    converted = re.sub(r"(?i)movement speed", "orchestration cadence", converted)
    converted = re.sub(r"(?i)action speed", "execution cadence", converted)
    converted = re.sub(r"(?i)speed", "cadence", converted)
    return converted, ("SCALE_CADENCE",)


def _charges(line: str):
    lower = line.casefold()
    if "charge" not in lower:
        return None
    converted = re.sub(r"(?i)power charges?", "qualification counters", line)
    converted = re.sub(r"(?i)frenzy charges?", "cadence counters", converted)
    converted = re.sub(r"(?i)endurance charges?", "resilience counters", converted)
    converted = re.sub(r"(?i)charges?", "success counters", converted)
    return converted, ("MINT_SUCCESS_COUNTER",)


def _ailment(line: str):
    lower = line.casefold()
    if not any(term in lower for term in ("poison", "bleed", "ignite", "burn", "chill", "freeze", "shock", "ailment")):
        return None
    converted = line
    for source, target in (
        ("poison", "deferred residual effect"),
        ("bleed", "deferred residual effect"),
        ("bleeding", "deferred residual effect"),
        ("ignite", "deferred residual effect"),
        ("burning", "deferred residual effect"),
        ("burn", "deferred residual effect"),
        ("chill", "degraded-state modifier"),
        ("freeze", "halted-state modifier"),
        ("shock", "amplified-susceptibility modifier"),
        ("ailments?", "residual state effects"),
    ):
        converted = re.sub(rf"(?i){source}", target, converted)
    converted = re.sub(r"(?i)damage", "Output Effectiveness", converted)
    primitives = ["APPLY_DEFERRED_EFFECT", "APPLY_STATE_MODIFIER"]
    if "output effectiveness" in converted.casefold():
        primitives.append("SCALE_OUTPUT_EFFECTIVENESS")
    return converted, tuple(primitives)


def _life_mana(line: str):
    lower = line.casefold()
    if not re.search(r"life|mana|energy shield|regenerat|leech|flask", lower):
        return None
    if "reservation" in lower:
        return None  # owned by _reservation
    converted = re.sub(r"(?i)energy shield", "protected reserve buffer", line)
    converted = re.sub(r"(?i)maximum mana", "maximum active budget", converted)
    converted = re.sub(r"(?i)mana", "active budget", converted)
    converted = re.sub(r"(?i)maximum life", "maximum primary resource pool", converted)
    converted = re.sub(r"(?i)life", "primary resource pool", converted)
    converted = re.sub(r"(?i)regenerat\w*", "replenish", converted)
    converted = re.sub(r"(?i)leech", "recoup", converted)
    converted = re.sub(r"(?i)flask", "bounded burst reserve", converted)
    return converted, ("EXPAND_RESOURCE_POOL", "RECOVER_RESOURCE")


def _defense(line: str):
    lower = line.casefold()
    if not re.search(r"armour|evasion|block|resist|ward\b|stun threshold", lower):
        return None
    converted = re.sub(r"(?i)armour", "structural resilience", line)
    converted = re.sub(r"(?i)evasion", "avoidance probability", converted)
    converted = re.sub(r"(?i)block", "rejection probability", converted)
    converted = re.sub(r"(?i)resist\w*", "tolerance", converted)
    converted = re.sub(r"(?i)ward\b", "integrity buffer", converted)
    converted = re.sub(r"(?i)stun threshold", "interruption threshold", converted)
    return converted, ("APPLY_STATE_MODIFIER",)


def _buff(line: str):
    lower = line.casefold()
    if "buff" not in lower:
        return None
    converted = re.sub(r"(?i)buff effect", "persistent modifier field effect", line)
    converted = re.sub(r"(?i)buffs?", "persistent modifier fields", converted)
    return converted, ("PERSISTENT_SHARED_MODIFIER",)


_STAT_ID_LINE_RE = re.compile(r"^[a-z0-9_+%]+:\s*-?[\d.]+$")

_STAT_ID_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (r"damage_\+?%|_dmg", "SCALE_OUTPUT_EFFECTIVENESS", "Output Effectiveness"),
    (r"critical_strike_chance", "SCALE_QUALIFICATION_PROBABILITY", "Qualification Probability"),
    (r"attack_speed|cast_speed|cooldown_speed|movement_speed|action_speed|_speed_\+?%", "SCALE_CADENCE", "execution cadence"),
    (r"area_of_effect|radius", "INCREASE_AREA_OR_SCOPE", "affected inference scope"),
    (r"duration", "EXTEND_DURATION", "state-retention duration"),
    (r"reservation_efficiency", "REDUCE_RESERVATION", "Persistent-Service Reservation efficiency"),
    (r"accuracy", "GATE_BY_CONFIDENCE", "Proposal Alignment"),
    (r"maximum_life|life_\+?%|life_regen", "EXPAND_RESOURCE_POOL", "primary resource pool"),
    (r"mana_\+?%|maximum_mana|mana_regen", "EXPAND_RESOURCE_POOL", "active budget"),
    (r"energy_shield", "EXPAND_RESOURCE_POOL", "protected reserve buffer"),
    (r"chance_to|_chance", "SCALE_QUALIFICATION_PROBABILITY", "event probability"),
    (r"charge", "MINT_SUCCESS_COUNTER", "success counters"),
    (r"minion|totem|golem", "PROXY_EXECUTION", "proxy workers"),
    (r"poison|bleed|ignite|burn|chill|freeze|shock|ailment", "APPLY_DEFERRED_EFFECT", "residual state effects"),
    (r"armour|evasion|block|resist|ward", "APPLY_STATE_MODIFIER", "defensive state modifiers"),
    (r"cooldown", "APPLY_COOLDOWN", "execution recovery window"),
    (r"cost|reservation", "INCREASE_EXECUTION_COST", "compute and reservation cost"),
    # Gate-5 second pass: mechanic-flag and class-marker families.
    (r"area_damage", "INCREASE_AREA_OR_SCOPE", "scoped-output class marker"),
    (r"is_projectile|projectile", "EMIT_ADDITIONAL_CANDIDATES", "candidate-trajectory class marker"),
    (r"deal_no_damage|no_damage", "FILTER_TARGETS", "no direct output effect (support-only payload)"),
    (r"trigger", "TRIGGER_ON_EVENT", "trigger gating"),
    (r"cast_on_|on_hit", "TRIGGER_ON_EVENT", "event-gated execution"),
    (r"reflect", "APPLY_STATE_MODIFIER", "reflected-output immunity modifier"),
    (r"pierce", "CHAIN_TO_NEW_TARGET", "trajectory pass-through"),
    (r"nova", "INCREASE_AREA_OR_SCOPE", "radial fan-out"),
    (r"trap|mine|summon|monster", "PROXY_EXECUTION", "proxy workers"),
    (r"curse|mark|doom|hex", "TARGET_SPECIFIC_MODIFIER", "target-specific modifier"),
    (r"pierce|arrow", "EMIT_ADDITIONAL_CANDIDATES", "candidate trajectories"),
    (r"show_|display_|visual_|icon|dummy", "RECORD_RECEIPT", "presentation annotation (non-mechanical)"),
)


def _stat_id(line: str):
    """Convert untranslated internal stat-id lines by mechanic family."""
    match = re.match(r"^([a-z0-9_+%]+):\s*(-?[\d.]+)$", line.strip())
    if not match:
        return None
    stat_id, value = match.group(1), match.group(2)
    for pattern, primitive, label in _STAT_ID_PATTERNS:
        if re.search(pattern, stat_id):
            sign = "+" if not value.startswith("-") else ""
            return (
                f"internal stat `{stat_id}` → {sign}{value} modifier to {label}",
                (primitive,),
            )
    # Boolean mechanic flags: preserve the flag verbatim without inventing
    # family semantics. This is a faithful structural translation, not an
    # equivalence claim.
    if value in ("0", "1") and re.match(r"^(is_|base_|can_|cannot_|skill_|always_|ignores_|spell_|melee_|console_)", stat_id):
        state = "ON" if value == "1" else "OFF"
        return (
            f"internal mechanic flag `{stat_id}` = {state} (flag preserved verbatim; family semantics not remapped)",
            (),
        )
    return None


def _curse(line: str):
    lower = line.casefold()
    if not any(term in lower for term in ("curse", "hex", "doom", "mark")):
        return None
    converted = re.sub(r"(?i)curses?", "target-specific modifier fields", line)
    converted = re.sub(r"(?i)hexes?", "target-specific modifier fields", converted)
    converted = re.sub(r"(?i)doom", "modifier intensity", converted)
    converted = re.sub(r"(?i)marks?", "target-specific priority fields", converted)
    return converted, ("TARGET_SPECIFIC_MODIFIER",)


def _pierce_and_arrows(line: str):
    lower = line.casefold()
    converted = line
    primitives: list[str] = []
    if "pierce" in lower:
        converted = re.sub(r"(?i)pierce", "pass through to", converted)
        primitives.append("CHAIN_TO_NEW_TARGET")
    if re.search(r"additional arrows?", lower):
        converted = re.sub(r"(?i)additional arrows?", "additional candidate trajectories", converted)
        primitives.append("EMIT_ADDITIONAL_CANDIDATES")
    if not primitives:
        return None
    return converted, tuple(primitives)


_CONVERTERS: tuple[Converter, ...] = (
    _supports_projectile_skills,
    _additional_projectiles,
    _less_projectile_damage,
    _increased_projectile_damage,
    _cost_multiplier,
    _critical_trigger,
    _cooldown,
    _reservation,
    _repeat,
    _chain,
    _return,
    _aura,
    _proxy,
    _duration,
    _area,
    # Gate-5 mechanic-family converters (acceptance-gate coverage pass).
    _annotation,
    _maximum_cap,
    _minion,
    _charges,
    _damage_offense,
    _speed,
    _charges,
    _ailment,
    _life_mana,
    _defense,
    _buff,
    _curse,
    _pierce_and_arrows,
    _stat_id,
)


def _inference_name(gem: PoeGem, primitives: tuple[str, ...]) -> str:
    explicit = {
        "Greater Multiple Projectiles Support": "Multi-Token Prediction Support",
        "Cast On Critical Strike Support": "Qualified Speculative Trigger Support",
        "Cast on Critical Strike Support": "Qualified Speculative Trigger Support",
        "Returning Projectiles Support": "Verified Returning Branches Support",
        "Enlighten Support": "Persistent-Service Reservation Support",
        "Inspiration Support": "Sustainable Speculation Support",
        "Spell Echo Support": "Inference Echo Support",
        "Unleash Support": "Prepared Reasoning Burst Support",
    }
    if gem.name in explicit:
        return explicit[gem.name]
    stem = re.sub(r"(?i)\s+support$", "", gem.name).strip()
    if gem.kind == "support":
        return f"{stem} Inference Support"
    if "PERSISTENT_SHARED_MODIFIER" in primitives:
        return f"{stem} Persistent Inference Field"
    return f"{stem} Inference Skill"


def translate_gem(gem: PoeGem) -> GemTranslation:
    """Translate one gem while preserving exact source lines side by side."""
    source_lines = tuple(line for line in (*gem.wording, *gem.quality_wording) if line)
    line_pairs: list[LineTranslation] = []
    converted_lines: list[str] = []
    unresolved: list[str] = []

    for source_line in source_lines:
        # Internal stat-id lines route exclusively to the stat-id converter:
        # keyword converters must not double-match raw ids (false PARTIAL).
        if _STAT_ID_LINE_RE.match(source_line.strip()):
            matches = [result for result in (_stat_id(source_line),) if result]
        else:
            matches = []
            for converter in _CONVERTERS:
                result = converter(source_line)
                if result:
                    matches.append(result)
        if not matches:
            unresolved.append(source_line)
            line_pairs.append(LineTranslation(source_line, "UNRESOLVED — requires mechanic-specific converter", 0.0, "UNRESOLVED"))
            continue
        converted = matches[0][0]
        primitives = tuple(dict.fromkeys(p for _, ps in matches for p in ps))
        status = "CONVERTED" if len(matches) == 1 else "PARTIAL"
        confidence = 0.9 if status == "CONVERTED" else 0.75
        converted_lines.append(converted)
        line_pairs.append(LineTranslation(source_line, converted, confidence, status, primitives))

    all_parts = (gem.name, gem.description, *gem.tags, *source_lines, *converted_lines)
    primitives = extract_primitives(all_parts)
    domains = extract_domains(all_parts)
    return GemTranslation(
        gem_id=gem.gem_id,
        poe_name=gem.name,
        inference_name=_inference_name(gem, primitives),
        source_tags=gem.tags,
        inference_domains=domains,
        primitives=primitives,
        source_wording=source_lines,
        converted_wording=tuple(converted_lines),
        line_pairs=tuple(line_pairs),
        unresolved_clauses=tuple(unresolved),
        notes=(
            "Source wording is retained exactly as supplied by the pinned corpus snapshot.",
            "Numeric values are not assumed to transfer literally unless separately benchmarked.",
        ),
    )


def translate_corpus(gems: tuple[PoeGem, ...]) -> tuple[GemTranslation, ...]:
    return tuple(translate_gem(gem) for gem in gems)
