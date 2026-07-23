"""
Layer classifier + translator (gem_decode).

Maps every parsed :class:`GemBuild` component onto its computational
analogue via the five-layer ontology (reusing BUILD_001–018 by reference),
and renders the translated build in two forms:

- a human-readable build sheet (markdown-ish — the founder reads these)
- a machine-readable JSON dict conforming to
  ``expansion/schemas/v2_2_gem_build.schema.json``

Deterministic only; no LLM calls.
"""

from __future__ import annotations

from typing import Any, Optional

from semantic_compiler.expansion.gem_decode.ontology import (
    ComponentEntry,
    LAYER_ORDER,
    lookup_component,
)
from semantic_compiler.expansion.gem_decode.parser import GemBuild

_FIELD_TO_LAYER = {
    "equipment": "Equipment",
    "active_skill": "Active skill",
    "support_gems": "Support gem",
    "auras": "Aura",
    "anointments": "Anointment",
    "flasks": "Flask",
}

_LAYER_TO_FIELD = {v: k for k, v in _FIELD_TO_LAYER.items()}


def translate_component(name: str, layer_field: str) -> dict[str, Any]:
    """Translate one component into its annotated build-sheet record."""
    layer = _FIELD_TO_LAYER[layer_field]
    entry = lookup_component(name, layer=layer)
    if entry is None:
        return {
            "name": name,
            "layer": layer,
            "mapped": False,
            "compute_analogue": None,
            "build_refs": [],
            "note": "unmapped component — manual review required",
            "scope": None,
        }
    return {
        "name": name,
        "layer": layer,
        "mapped": True,
        "canonical": entry.canonical,
        "compute_analogue": entry.compute_analogue,
        "build_refs": list(entry.build_refs),
        "note": entry.note,
        "scope": entry.scope,
    }


def translate_build(build: GemBuild) -> dict[str, Any]:
    """Translate a parsed build into the layered machine-readable record."""
    layers: dict[str, Any] = {
        "equipment": [],
        "active_skill": None,
        "support_gems": [],
        "auras": [],
        "anointments": [],
        "flasks": [],
    }
    unmapped: list[str] = []
    for field_name, name in build.all_components():
        record = translate_component(name, field_name)
        if not record["mapped"]:
            unmapped.append(name)
        if field_name == "active_skill":
            layers["active_skill"] = record
        else:
            layers[field_name].append(record)
    return {"layers": layers, "unmapped_components": unmapped}


def resolve_entry(name: str, layer_field: str) -> Optional[ComponentEntry]:
    """Layer-aware ontology lookup (used by the checks module)."""
    return lookup_component(name, layer=_FIELD_TO_LAYER[layer_field])


# ---------------------------------------------------------------------------
# Human-readable build sheet
# ---------------------------------------------------------------------------

def render_build_sheet(
    build: GemBuild,
    translated: dict[str, Any],
    checks: list[dict[str, Any]],
    flags: list[dict[str, Any]],
    verdict: str,
) -> str:
    """Render the founder-readable markdown build sheet."""
    lines: list[str] = []
    lines.append("# Gem Decode — Build Sheet")
    lines.append("")
    lines.append(f"**Dialect:** {build.dialect}  ")
    lines.append(f"**Verdict:** {verdict}")
    lines.append("")

    layer_sections = (
        ("Equipment", "equipment", "Permanently installed hardware"),
        ("Active skill", "active_skill", "The primary payload"),
        ("Support gems", "support_gems", "Execution mechanics"),
        ("Auras", "auras", "Persistent modifier fields"),
        ("Anointments", "anointments", "Certified portable doctrine overlays"),
        ("Flasks", "flasks", "Temporary bounded burst modes"),
    )
    layers = translated["layers"]
    for title, field_name, subtitle in layer_sections:
        records = layers[field_name]
        if field_name == "active_skill":
            records = [records] if records else []
        if not records:
            continue
        lines.append(f"## {title} — {subtitle}")
        lines.append("")
        lines.append("| Gem language | Computational analogue | Refs | Notes |")
        lines.append("|---|---|---|---|")
        for r in records:
            analogue = r["compute_analogue"] or "⚠ UNMAPPED"
            refs = ", ".join(r["build_refs"]) if r["build_refs"] else "—"
            note = r["note"] or ""
            lines.append(f"| {r['name']} | {analogue} | {refs} | {note} |")
        lines.append("")

    if checks:
        lines.append("## Executable checks")
        lines.append("")
        for c in checks:
            lines.append(f"- **[{c['status']}]** `{c['check_id']}` — {c['reason']}")
        lines.append("")

    if flags:
        lines.append("## Failure-family flags")
        lines.append("")
        for f in flags:
            families = "/".join(f["families"])
            lines.append(
                f"- **[{f['severity'].upper()}] {f['code']}** (family {families}) — {f['description']}"
            )
        lines.append("")
    else:
        lines.append("## Failure-family flags")
        lines.append("")
        lines.append("- none")
        lines.append("")

    if translated["unmapped_components"]:
        lines.append("## Unmapped components (manual review)")
        lines.append("")
        for name in translated["unmapped_components"]:
            lines.append(f"- {name}")
        lines.append("")

    return "\n".join(lines)
