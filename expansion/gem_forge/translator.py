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
    if "critical strike" not in lower and "cast on crit" not in lower:
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
    if "area of effect" not in lower and "area" not in lower:
        return None
    primitive = "REDUCE_AREA_OR_SCOPE" if "less" in lower or "reduced" in lower else "INCREASE_AREA_OR_SCOPE"
    converted = re.sub(r"(?i)area of effect", "affected inference scope", line)
    converted = re.sub(r"(?i)area", "scope", converted)
    return converted, (primitive,)


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
        matches: list[tuple[str, tuple[str, ...]]] = []
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
