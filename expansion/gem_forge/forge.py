"""Many-to-many software -> gem matching and synthetic gem generation."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from semantic_compiler.expansion.gem_forge.models import (
    ForgeResult,
    GemMatch,
    GemTranslation,
    SoftwareComponent,
    SyntheticGem,
)
from semantic_compiler.expansion.gem_forge.taxonomy import extract_domains, extract_primitives


def _component_primitives(component: SoftwareComponent) -> tuple[str, ...]:
    explicit = tuple(component.traits)
    inferred = extract_primitives((component.name, component.description, *component.relationships, *component.capability_domains))
    return tuple(dict.fromkeys((*explicit, *inferred)))


def _component_domains(component: SoftwareComponent) -> tuple[str, ...]:
    explicit = tuple(component.capability_domains)
    inferred = extract_domains((component.name, component.description, *component.traits, *component.relationships))
    return tuple(dict.fromkeys((*explicit, *inferred)))


def _score_match(component_primitives: set[str], translation: GemTranslation) -> GemMatch | None:
    gem_primitives = set(translation.primitives)
    overlap = component_primitives & gem_primitives
    if not overlap:
        return None
    precision = len(overlap) / max(1, len(gem_primitives))
    coverage = len(overlap) / max(1, len(component_primitives))
    score = round((0.55 * coverage) + (0.45 * precision), 4)
    uncovered = tuple(sorted(component_primitives - gem_primitives))
    return GemMatch(
        gem_id=translation.gem_id,
        gem_name=translation.poe_name,
        gem_kind="support" if translation.poe_name.casefold().endswith("support") else "active_or_meta",
        score=score,
        matched_primitives=tuple(sorted(overlap)),
        uncovered_component_primitives=uncovered,
        explanation=(
            f"Matches {len(overlap)} mechanic primitive(s): {', '.join(sorted(overlap))}. "
            f"Score combines component coverage and gem-mechanic precision."
        ),
    )


def match_component(
    component: SoftwareComponent,
    translations: Iterable[GemTranslation],
    *,
    top_n: int = 8,
    minimum_score: float = 0.18,
) -> tuple[GemMatch, ...]:
    primitives = set(_component_primitives(component))
    matches = [
        match
        for translation in translations
        if (match := _score_match(primitives, translation)) is not None and match.score >= minimum_score
    ]
    matches.sort(key=lambda item: (-item.score, item.gem_name.casefold(), item.gem_id))
    return tuple(matches[:top_n])


def _synthetic_name(component: SoftwareComponent, matches: tuple[GemMatch, ...]) -> str:
    if not matches:
        return f"{component.name} Support"
    if len(matches) == 1:
        return f"{component.name} — {matches[0].gem_name} Variant"
    anchors = " + ".join(match.gem_name.replace(" Support", "") for match in matches[:3])
    return f"{component.name} — Composite of {anchors}"


def forge_component(
    component: SoftwareComponent,
    translations: Iterable[GemTranslation],
    *,
    top_n: int = 8,
) -> ForgeResult:
    """Identify source-gem traits and forge a composite inference gem.

    No component is forced into a single gem. Any primitive not covered by the
    selected source gems is emitted under ``novel_effects`` rather than discarded.
    """
    translations = tuple(translations)
    primitives = _component_primitives(component)
    domains = _component_domains(component)
    matches = match_component(component, translations, top_n=top_n)

    covered: set[str] = set()
    for match in matches:
        covered.update(match.matched_primitives)
    novel = tuple(sorted(set(primitives) - covered))

    wording: list[str] = []
    if "EMIT_ADDITIONAL_CANDIDATES" in primitives:
        wording.append("Supported Inference predicts additional candidate Token Positions or trajectories per execution opportunity.")
    if "TRIGGER_ON_QUALIFICATION" in primitives:
        wording.append("Qualified proposals automatically trigger the supported verified payload.")
    if "REDUCE_RESERVATION" in primitives:
        wording.append("Persistent services supported by this component reserve less active execution capacity.")
    if "RETURN_BRANCH_FEEDBACK" in primitives:
        wording.append("Rejected or completed branches return structured evidence to the next inference cycle.")
    if "PRELOAD_FUTURE_STATE" in primitives:
        wording.append("Predicted future state is prepared before canonical execution reaches it.")
    if "PERSISTENT_SHARED_MODIFIER" in primitives:
        wording.append("Applies a persistent modifier field to all compatible inference operations in scope.")
    if "ADAPT_PARAMETER" in primitives:
        wording.append("Key execution parameters are selected dynamically from measured runtime state.")
    if "MERGE_RESULTS" in primitives:
        wording.append("Parallel results are reconciled into one canonical output.")
    if "DEDUPLICATE_RESULTS" in primitives:
        wording.append("Equivalent outputs are de-duplicated before affecting canonical state.")
    if "RECORD_RECEIPT" in primitives:
        wording.append("Execution produces a provenance receipt describing applied effects and measured cost.")
    if not wording:
        wording.append("Modifies compatible inference operations according to its declared mechanic primitives.")

    source_gems = tuple(match.gem_name for match in matches)
    synthetic = SyntheticGem(
        name=_synthetic_name(component, matches),
        tags=tuple(dict.fromkeys((*component.deployment_slots, *domains))),
        supports=component.description,
        wording=tuple(wording),
        source_gems=source_gems,
        novel_effects=novel,
        composition="COMPOSITE" if len(matches) > 1 else ("SINGLE_SOURCE" if matches else "NOVEL"),
    )

    record = {
        "schema": "reflexion.gem_forge.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "component": component.to_dict(),
        "primitives": list(primitives),
        "capability_domains": list(domains),
        "matches": [match.to_dict() for match in matches],
        "synthetic_gem": synthetic.to_dict(),
        "epistemic_status": {
            "mapping": "STRUCTURAL_ANALOGY",
            "performance": "UNMEASURED_UNLESS_RECEIPT_ATTACHED",
            "novel_effect_policy": "PRESERVE_EXPLICITLY",
        },
    }
    return ForgeResult(component, primitives, domains, matches, synthetic, record)
