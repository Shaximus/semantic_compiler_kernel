"""
Parser for gem-formatted build specifications (gem_decode).

Accepts build specs in either dialect and parses them into a structured
:class:`GemBuild`. Deterministic string processing only — no LLM calls.

Dialects
--------

(a) PoE-native — a gem chain plus keyed sections::

    "Ice Nova + Cast on Critical Strike + Greater Multiple Projectiles;
     weapon: Cospri's Malice; auras: Hatred, Herald of Ice;
     flask: Dying Sun; anointment: Calibrated Dissent"

(b) Reflexion-native — keyed sections naming compute components directly::

    "verifier: MiniMax M2.5; draft: Qwen draft;
     supports: MTP K=5, vLLM, expert compression;
     auras: BCC, TokenRouter, receipts; flask: auxiliary_i9;
     anointment: authority_gate"

Grammar
-------

- Sections are separated by ``;``.
- A section is either ``key: value, value, ...`` or a bare gem chain
  ``A + B + C``.
- In a bare chain the first item is the active skill and the rest are
  support gems (PoE link order).
- Keyed sections map onto layers via a fixed key vocabulary (below);
  an unknown key raises :class:`GemParseError` — silent misclassification
  is worse than a loud parse failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class GemParseError(ValueError):
    """Raised when a build spec cannot be parsed deterministically."""


# Key vocabulary -> GemBuild field. Keys are matched case-insensitively
# after normalization (lowercase, spaces/underscores collapsed).
_KEY_TO_FIELD: dict[str, str] = {
    # equipment (permanently installed hardware)
    "equipment": "equipment",
    "weapon": "equipment",
    "weapons": "equipment",
    "secondary weapon": "equipment",
    "primary weapon": "equipment",
    "gear": "equipment",
    "hardware": "equipment",
    "item": "equipment",
    "items": "equipment",
    "case": "equipment",
    "chassis": "equipment",
    "motherboard": "equipment",
    "gpu": "equipment",
    "cpu": "equipment",
    # active skill (the primary payload: LLM weights / the spell)
    "skill": "active_skill",
    "active": "active_skill",
    "active skill": "active_skill",
    "verifier": "active_skill",
    "model": "active_skill",
    "payload": "active_skill",
    # support gems (execution mechanics)
    "support": "support_gems",
    "supports": "support_gems",
    "support gem": "support_gems",
    "support gems": "support_gems",
    "draft": "support_gems",   # a draft model modifies execution of the verifier
    "drafter": "support_gems",
    # auras (persistent modifier fields)
    "aura": "auras",
    "auras": "auras",
    # flasks (temporary bounded burst modes)
    "flask": "flasks",
    "flasks": "flasks",
    # anointments (certified portable doctrine overlays)
    "anointment": "anointments",
    "anointments": "anointments",
    "anoint": "anointments",
}

# Keys that mark the Reflexion-native dialect.
_REFLEXION_KEYS = {"verifier", "draft", "drafter", "supports", "support", "support gem", "support gems", "model"}
# Keys/structures that mark the PoE-native dialect.
_POE_KEYS = {"weapon", "weapons", "secondary weapon", "primary weapon", "skill", "active", "active skill", "gear", "items", "item", "payload"}


def _normalize_key(text: str) -> str:
    return " ".join(text.strip().lower().replace("_", " ").replace("-", " ").split())


def _clean_item(text: str) -> str:
    return " ".join(text.strip().split())


@dataclass(frozen=True)
class GemBuild:
    """A parsed build specification in gem language."""

    equipment: tuple[str, ...] = ()
    active_skill: Optional[str] = None
    support_gems: tuple[str, ...] = ()
    auras: tuple[str, ...] = ()
    anointments: tuple[str, ...] = ()
    flasks: tuple[str, ...] = ()
    raw: str = ""
    dialect: str = "unknown"  # poe_native | reflexion_native | mixed | unknown

    def all_components(self) -> list[tuple[str, str]]:
        """Return (layer_field, name) pairs in canonical layer order."""
        out: list[tuple[str, str]] = [("equipment", e) for e in self.equipment]
        if self.active_skill:
            out.append(("active_skill", self.active_skill))
        out += [("support_gems", s) for s in self.support_gems]
        out += [("auras", a) for a in self.auras]
        out += [("anointments", a) for a in self.anointments]
        out += [("flasks", f) for f in self.flasks]
        return out

    def to_dict(self) -> dict:
        return {
            "equipment": list(self.equipment),
            "active_skill": self.active_skill,
            "support_gems": list(self.support_gems),
            "auras": list(self.auras),
            "anointments": list(self.anointments),
            "flasks": list(self.flasks),
            "raw": self.raw,
            "dialect": self.dialect,
        }


def parse_build_spec(spec_text: str) -> GemBuild:
    """Parse a gem-formatted build spec into a :class:`GemBuild`."""
    if not spec_text or not spec_text.strip():
        raise GemParseError("empty build spec")

    equipment: list[str] = []
    active_skill: Optional[str] = None
    support_gems: list[str] = []
    auras: list[str] = []
    anointments: list[str] = []
    flasks: list[str] = []
    seen_keys: set[str] = set()
    saw_chain = False

    fields = {
        "equipment": equipment,
        "support_gems": support_gems,
        "auras": auras,
        "anointments": anointments,
        "flasks": flasks,
    }

    for segment in spec_text.split(";"):
        segment = segment.strip()
        if not segment:
            continue
        if ":" in segment and "+" not in segment.split(":", 1)[0]:
            key, _, values = segment.partition(":")
            normalized_key = _normalize_key(key)
            if not normalized_key:
                raise GemParseError(f"empty section key in segment: {segment!r}")
            target = _KEY_TO_FIELD.get(normalized_key)
            if target is None:
                raise GemParseError(
                    f"unknown section key {key.strip()!r} in segment: {segment!r}"
                )
            seen_keys.add(normalized_key)
            items = [_clean_item(v) for v in values.split(",") if v.strip()]
            if not items:
                raise GemParseError(f"section {key.strip()!r} has no values")
            if target == "active_skill":
                if active_skill is not None:
                    raise GemParseError(
                        f"multiple active skills declared ({active_skill!r}, {items[0]!r})"
                    )
                active_skill = items[0]
                # Extra values in an active-skill section are its supports.
                support_gems.extend(items[1:])
            else:
                fields[target].extend(items)
        else:
            # Bare gem chain: first item is the active skill, rest are supports.
            saw_chain = True
            items = [_clean_item(v) for v in segment.split("+") if v.strip()]
            if not items:
                raise GemParseError(f"empty gem chain in segment: {segment!r}")
            if active_skill is None:
                active_skill = items[0]
                support_gems.extend(items[1:])
            else:
                support_gems.extend(items)

    if active_skill is None and not any(fields.values()):
        raise GemParseError("spec declares no components at all")

    dialect = _detect_dialect(seen_keys, saw_chain)
    return GemBuild(
        equipment=tuple(equipment),
        active_skill=active_skill,
        support_gems=tuple(support_gems),
        auras=tuple(auras),
        anointments=tuple(anointments),
        flasks=tuple(flasks),
        raw=spec_text,
        dialect=dialect,
    )


def _detect_dialect(seen_keys: set[str], saw_chain: bool) -> str:
    reflexion = bool(seen_keys & _REFLEXION_KEYS)
    poe = bool(seen_keys & _POE_KEYS) or saw_chain
    if reflexion and poe:
        return "mixed"
    if reflexion:
        return "reflexion_native"
    if poe:
        return "poe_native"
    return "unknown"
