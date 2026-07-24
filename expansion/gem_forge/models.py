"""Typed records for Gem Forge.

Gem Forge is deliberately many-to-many. A PoE gem may encode several inference
primitives, and one inference component may express several gem traits plus novel
effects that do not exist in the PoE vocabulary.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PoeGem:
    gem_id: str
    name: str
    kind: str  # active | support | meta
    tags: tuple[str, ...] = ()
    description: str = ""
    wording: tuple[str, ...] = ()
    quality_wording: tuple[str, ...] = ()
    release_state: str = "released"
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SoftwareComponent:
    name: str
    description: str
    deployment_slots: tuple[str, ...] = ()
    capability_domains: tuple[str, ...] = ()
    traits: tuple[str, ...] = ()
    relationships: tuple[str, ...] = ()
    version: str | None = None
    source: str = "user_or_registry"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineTranslation:
    source: str
    converted: str
    confidence: float
    status: str  # CONVERTED | PARTIAL | UNRESOLVED
    primitives: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GemTranslation:
    gem_id: str
    poe_name: str
    inference_name: str
    source_tags: tuple[str, ...]
    inference_domains: tuple[str, ...]
    primitives: tuple[str, ...]
    source_wording: tuple[str, ...]
    converted_wording: tuple[str, ...]
    line_pairs: tuple[LineTranslation, ...]
    unresolved_clauses: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["line_pairs"] = [pair.to_dict() for pair in self.line_pairs]
        return data


@dataclass(frozen=True)
class GemMatch:
    gem_id: str
    gem_name: str
    gem_kind: str
    score: float
    matched_primitives: tuple[str, ...]
    uncovered_component_primitives: tuple[str, ...]
    explanation: str
    wording_evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SyntheticGem:
    name: str
    tags: tuple[str, ...]
    supports: str
    wording: tuple[str, ...]
    source_gems: tuple[str, ...]
    novel_effects: tuple[str, ...]
    composition: str = "COMPOSITE"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForgeResult:
    component: SoftwareComponent
    primitives: tuple[str, ...]
    capability_domains: tuple[str, ...]
    matches: tuple[GemMatch, ...]
    composite_gem: SyntheticGem
    record: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return self.record
