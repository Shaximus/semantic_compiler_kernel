"""Rx Arena /skill decompression mode.

Transforms a semantic description of a tactic into a bounded, auditable skill
scaffold. This is design-time compilation only: it never executes game effects
and never grants authority. The output is intended for Arena validation,
simulation, review, and receipt generation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any


SKILL_SCHEMA_ID = "rx.skill.v1"
ALLOWED_TRIGGER_TYPES = {"manual", "event", "state_transition", "combo"}
ALLOWED_CONDITION_TYPES = {"resource", "entity_state", "tag", "distance", "line_of_sight", "authority"}
ALLOWED_EFFECT_OPS = {
    "apply_tag",
    "remove_tag",
    "set_tag",
    "set_modifier",
    "emit_signal",
    "request_action",
    "open_combo_window",
    "record_observation",
}


@dataclass(frozen=True)
class SkillDecompressionResult:
    skill: dict[str, Any]
    missing_fields: tuple[str, ...]
    assumptions: tuple[str, ...]
    residual_risks: tuple[str, ...]


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", text.casefold()).strip("_")
    return value[:64] or "unnamed_skill"


def _extract_name(text: str) -> str:
    quoted = re.search(r"[\"']([^\"']{3,80})[\"']", text)
    if quoted:
        return quoted.group(1).strip()
    first = re.split(r"[.!?\n]", text.strip(), maxsplit=1)[0]
    return first[:80].strip() or "Unnamed Skill"


def _infer_tags(text: str) -> list[str]:
    vocabulary = {
        "feint", "bait", "setup", "punish", "defense", "mobility", "control",
        "information", "recording", "combo", "pressure", "retreat", "rescue",
        "support", "counter", "interrupt", "sacrifice", "recovery", "corruption",
    }
    words = set(re.findall(r"[a-z]+", text.casefold()))
    tags = sorted(vocabulary & words)
    return tags[:8] or ["unclassified"]


def _infer_effects(text: str) -> list[dict[str, Any]]:
    lower = text.casefold()
    effects: list[dict[str, Any]] = []
    if any(term in lower for term in ("observe", "record", "learn", "read the enemy", "pattern")):
        effects.append({"op": "record_observation", "params": {"scope": "bounded_combat_context"}})
    if any(term in lower for term in ("bait", "feint", "false opening")):
        effects.append({"op": "apply_tag", "params": {"tag": "false_opening", "duration_ticks": None}})
    if any(term in lower for term in ("combo", "follow up", "follow-up", "window")):
        effects.append({"op": "open_combo_window", "params": {"tag": "combo_window_open", "duration_ticks": None}})
    if any(term in lower for term in ("signal", "warn", "call out", "notify")):
        effects.append({"op": "emit_signal", "params": {"signal": "skill_signal"}})
    if any(term in lower for term in ("move", "attack", "retreat", "guard", "repair", "build")):
        effects.append({"op": "request_action", "params": {"action": "UNRESOLVED_ACTION", "authority_gate": "required"}})
    return effects or [{"op": "set_tag", "params": {"tag": "skill_active", "duration_ticks": None}}]


def decompress_skill(text: str, *, source_receipt_id: str | None = None) -> SkillDecompressionResult:
    """Compile free-form tactical intent into a closed skill scaffold."""
    name = _extract_name(text)
    effects = _infer_effects(text)
    tags = _infer_tags(text)
    missing: list[str] = ["costs.resources", "costs.cooldown_ticks"]
    assumptions = ["manual trigger selected unless explicit event semantics are supplied"]
    residuals = [
        "effect magnitudes and durations require simulation-backed tuning",
        "request_action effects must pass Arena authority and command validation",
        "no generated skill is ranked-legal until canonical validation and signing",
    ]

    for effect in effects:
        params = effect.get("params", {})
        for key, value in params.items():
            if value is None or value == "UNRESOLVED_ACTION":
                missing.append(f"effects.{effect['op']}.{key}")

    skill = {
        "$schema": SKILL_SCHEMA_ID,
        "skill_id": f"skill.{_slug(name)}",
        "name": name,
        "version": "0.1.0-draft",
        "status": "DRAFT_REQUIRES_VALIDATION",
        "provenance": {
            "source_receipt_id": source_receipt_id,
            "source_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "compiler": "semantic_compiler.skill_decompression.v1",
        },
        "triggers": [{"type": "manual"}],
        "conditions": [],
        "effects": effects,
        "costs": {
            "resources": None,
            "authority": 0,
            "cooldown_ticks": None,
            "commitment_window_ticks": None,
        },
        "combo_tags": tags,
        "authority_requirement": "validated_request_only" if any(e["op"] == "request_action" for e in effects) else "none",
        "validation": {
            "schema_valid": False,
            "simulation_valid": False,
            "ranked_legal": False,
            "validation_hash": None,
        },
    }
    return SkillDecompressionResult(skill, tuple(dict.fromkeys(missing)), tuple(assumptions), tuple(residuals))


def validate_skill_shape(skill: dict[str, Any]) -> list[str]:
    """Perform deterministic structural validation without executing effects."""
    errors: list[str] = []
    if skill.get("$schema") != SKILL_SCHEMA_ID:
        errors.append("unsupported schema")
    for trigger in skill.get("triggers", []):
        if trigger.get("type") not in ALLOWED_TRIGGER_TYPES:
            errors.append(f"illegal trigger: {trigger.get('type')}")
    for condition in skill.get("conditions", []):
        if condition.get("type") not in ALLOWED_CONDITION_TYPES:
            errors.append(f"illegal condition: {condition.get('type')}")
    for effect in skill.get("effects", []):
        if effect.get("op") not in ALLOWED_EFFECT_OPS:
            errors.append(f"illegal effect op: {effect.get('op')}")
    costs = skill.get("costs", {})
    for key in ("resources", "cooldown_ticks"):
        if costs.get(key) is None:
            errors.append(f"missing cost: {key}")
    return errors


def canonical_skill_hash(skill: dict[str, Any]) -> str:
    """Hash a completed skill definition for signing and receipts."""
    payload = json.loads(json.dumps(skill))
    payload.setdefault("validation", {})["validation_hash"] = None
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
