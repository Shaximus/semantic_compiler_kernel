"""Composite synthesis attribution: per-primitive, line-by-line provenance.

Every composite gem emitted by :func:`forge_component` must be able to show
WHICH source gems contributed WHICH mechanic primitives, line by line. This
module derives that receipt from the forge result plus the gem translations:

- for each covered primitive, every contributing source gem is listed with the
  exact source wording line(s) whose conversion carries that primitive;
- primitives carried only by gem-level vocabulary (name/tags/description,
  i.e. no wording line) are attributed explicitly as gem-level, never
  fabricated into a line;
- the matcher floor is re-verified at the attribution layer: a COMPOSITE or
  SINGLE_SOURCE synthesis backed by fewer than two distinct attributed
  primitives is a single-primitive composite and is demoted to NOVEL here,
  with the demotion recorded. ``floor_violations`` surfaces any such case so
  tests can assert the floor holds.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from semantic_compiler.expansion.gem_forge.models import ForgeResult, GemTranslation
from semantic_compiler.expansion.gem_forge.taxonomy import canonical_primitive


@dataclass(frozen=True)
class PrimitiveContributor:
    gem_id: str
    gem_name: str
    source_line: str | None  # None => gem-level vocabulary attribution (name/tags/description)
    converted_wording: str | None
    line_status: str | None
    attribution_level: str  # "line" | "gem"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompositeAttribution:
    component_name: str
    composition: str  # composition AFTER attribution-layer floor verification
    original_composition: str
    demoted_single_primitive: bool
    source_gems: tuple[str, ...]
    primitive_attributions: dict[str, tuple[PrimitiveContributor, ...]] = field(default_factory=dict)
    novel_primitives: tuple[str, ...] = ()

    def attributed_primitive_count(self) -> int:
        return len(self.primitive_attributions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_name": self.component_name,
            "composition": self.composition,
            "original_composition": self.original_composition,
            "demoted_single_primitive": self.demoted_single_primitive,
            "source_gems": list(self.source_gems),
            "attributed_primitive_count": self.attributed_primitive_count(),
            "primitive_attributions": {
                primitive: [c.to_dict() for c in contributors]
                for primitive, contributors in sorted(self.primitive_attributions.items())
            },
            "novel_primitives": list(self.novel_primitives),
        }


def attribute_composite(
    result: ForgeResult,
    translations: Iterable[GemTranslation],
) -> CompositeAttribution:
    """Attribute every covered primitive of a forge result to source-gem lines."""
    by_id: dict[str, GemTranslation] = {t.gem_id: t for t in translations}
    attributions: dict[str, list[PrimitiveContributor]] = {}

    for match in result.matches:
        translation = by_id.get(match.gem_id)
        for primitive in match.matched_primitives:
            canonical = canonical_primitive(primitive)
            contributors = attributions.setdefault(canonical, [])
            line_hit = False
            if translation is not None:
                for pair in translation.line_pairs:
                    if canonical in {canonical_primitive(p) for p in pair.primitives}:
                        contributors.append(PrimitiveContributor(
                            gem_id=match.gem_id,
                            gem_name=match.gem_name,
                            source_line=pair.source,
                            converted_wording=pair.converted,
                            line_status=pair.status,
                            attribution_level="line",
                        ))
                        line_hit = True
            if not line_hit:
                contributors.append(PrimitiveContributor(
                    gem_id=match.gem_id,
                    gem_name=match.gem_name,
                    source_line=None,
                    converted_wording=None,
                    line_status=None,
                    attribution_level="gem",
                ))

    frozen = {p: tuple(cs) for p, cs in attributions.items()}
    original = result.composite_gem.composition
    # Attribution-layer floor verification: a synthesis backed by fewer than
    # two distinct attributed primitives is a single-primitive composite and
    # demotes to NOVEL with the demotion recorded (never silently kept).
    demoted = original in ("COMPOSITE", "SINGLE_SOURCE") and len(frozen) < 2
    composition = "NOVEL" if demoted else original
    return CompositeAttribution(
        component_name=result.component.name,
        composition=composition,
        original_composition=original,
        demoted_single_primitive=demoted,
        source_gems=result.composite_gem.source_gems if not demoted else (),
        primitive_attributions=frozen if not demoted else {},
        novel_primitives=result.composite_gem.novel_effects,
    )


def floor_violations(attributions: Iterable[CompositeAttribution]) -> list[str]:
    """Names of records that remain single-primitive composites after verification.

    An empty return means the floor holds: no single-primitive composites.
    """
    violations = []
    for record in attributions:
        if record.composition in ("COMPOSITE", "SINGLE_SOURCE") and record.attributed_primitive_count() < 2:
            violations.append(record.component_name)
    return sorted(violations)
