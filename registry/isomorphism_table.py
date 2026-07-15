"""
Reflexion Semantic Compiler v2.0.0 — Cross-Scale Isomorphism Mappings

v2.0 Cosmological Mappings:
  - Hawking radiation = file deletion (information escaping storage)
  - Earth = rendered application (experienced reality is display output)
  - Dark matter = application rendering overhead (invisible computational cost)
  - Information density = system RAM
  - Black hole = storage / Virtual machine / nested VMs
  - Laws of physics = universe's subconscious (governing rules below awareness)
  - Observer/measurement = wave function collapse = thinking-output convergence
  - Heliosphere boundary = system boundary / edge of motherboard

Citation: v2.0 — Universal Fractal Isomorphism
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IsomorphismMapping:
    """A specific cross-scale isomorphic mapping between two phenomena."""
    mapping_id: str
    source_phenomenon: str
    source_scale: str
    target_phenomenon: str
    target_scale: str
    preserved_functions: list[str] = field(default_factory=list)
    residual_mismatches: list[str] = field(default_factory=list)
    confidence: float = 0.0
    mapping_class: str = "STRUCTURAL_ANALOGY"
    citation: str = ""


# ---------------------------------------------------------------------------
# v2.0 Cosmological Isomorphism Table
# ---------------------------------------------------------------------------

COSMOLOGICAL_MAPPINGS: list[IsomorphismMapping] = [
    IsomorphismMapping(
        mapping_id="COSMO_001",
        source_phenomenon="Hawking radiation",
        source_scale="COSMOLOGICAL",
        target_phenomenon="File deletion / garbage collection",
        target_scale="COMPONENT",
        preserved_functions=[
            "information escaping containment",
            "gradual loss from storage boundary",
            "irreversibility under normal conditions",
            "entropy increase",
        ],
        residual_mismatches=[
            "Hawking radiation is thermodynamic; file deletion is deterministic",
            "quantum tunneling has no direct computational analog",
            "black hole evaporation timescale has no file-system equivalent",
        ],
        confidence=0.75,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Cosmological Mappings",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_002",
        source_phenomenon="Earth (planet)",
        source_scale="COSMOLOGICAL",
        target_phenomenon="Rendered application / display output",
        target_scale="COMPONENT",
        preserved_functions=[
            "experienced reality is the output layer",
            "complex processes produce the observable surface",
            "the rendering layer consumes resources",
            "observers interact with the rendered surface, not the engine",
        ],
        residual_mismatches=[
            "Earth is physical; applications are computational",
            "no literal 'renderer' produces Earth",
            "consciousness is not equivalent to display rendering",
        ],
        confidence=0.65,
        mapping_class="HEURISTIC_METAPHOR",
        citation="v2.0 Cosmological Mappings",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_003",
        source_phenomenon="Dark matter / dark energy",
        source_scale="COSMOLOGICAL",
        target_phenomenon="Application rendering overhead / background processes",
        target_scale="COMPONENT",
        preserved_functions=[
            "invisible to direct observation",
            "accounts for majority of system resource consumption",
            "necessary for structural integrity",
            "detected only by indirect effects",
        ],
        residual_mismatches=[
            "dark matter is physical; overhead is computational",
            "dark matter's nature is unknown; overhead is measurable",
            "gravitational effects have no direct computational analog",
        ],
        confidence=0.60,
        mapping_class="HEURISTIC_METAPHOR",
        citation="v2.0 Cosmological Mappings",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_004",
        source_phenomenon="Information density (Bekenstein bound)",
        source_scale="COSMOLOGICAL",
        target_phenomenon="RAM / working memory / population density",
        target_scale="COMPONENT",
        preserved_functions=[
            "finite information capacity per unit",
            "density limits on processing throughput",
            "saturation degrades performance",
            "compression increases effective capacity",
        ],
        residual_mismatches=[
            "Bekenstein bound is fundamental physics; RAM limits are engineering",
            "quantum information has different rules than classical",
        ],
        confidence=0.70,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Cosmological Mappings",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_005",
        source_phenomenon="Black hole",
        source_scale="COSMOLOGICAL",
        target_phenomenon="Storage / Virtual machine / nested VMs",
        target_scale="COMPONENT",
        preserved_functions=[
            "information enters and is preserved (holographic principle)",
            "boundary (event horizon) defines containment",
            "nested containment possible (VMs within VMs)",
            "external observers cannot directly access internal state",
        ],
        residual_mismatches=[
            "black holes are gravitational; VMs are computational",
            "singularity has no computational equivalent",
            "time dilation near boundary has no VM analog",
        ],
        confidence=0.65,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Cosmological Mappings",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_006",
        source_phenomenon="Laws of physics",
        source_scale="COSMOLOGICAL",
        target_phenomenon="Universe's subconscious / governing rules below awareness",
        target_scale="COSMOLOGICAL",
        preserved_functions=[
            "governing rules operate below conscious awareness",
            "cannot be directly modified by governed entities",
            "determine all possible behaviors within the system",
            "discovered through observation, not introspection",
        ],
        residual_mismatches=[
            "physical laws are mathematical; subconscious is psychological",
            "physical laws are universal; psychological rules are individual",
            "physical laws do not 'want' anything",
        ],
        confidence=0.80,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Subconscious-Governance Mapping",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_007",
        source_phenomenon="Observer / wave function measurement",
        source_scale="COSMOLOGICAL",
        target_phenomenon="Thinking-output convergence / speech act",
        target_scale="AGENT",
        preserved_functions=[
            "observation forces state resolution",
            "superposition of possibilities collapses to definite state",
            "the act of measurement changes the system",
            "inner state becomes external reality",
        ],
        residual_mismatches=[
            "quantum measurement is physical; speech is cognitive",
            "quantum decoherence is not identical to decision-making",
            "no literal wave function in language processing",
        ],
        confidence=0.70,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Wave Function Coherence",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_008",
        source_phenomenon="Heliosphere boundary",
        source_scale="COSMOLOGICAL",
        target_phenomenon="System boundary / edge of motherboard / org perimeter",
        target_scale="COMPONENT",
        preserved_functions=[
            "defines inside vs outside",
            "protects internal systems from external environment",
            "transition zone where rules change",
            "Voyager crossed this boundary = probe leaving system",
        ],
        residual_mismatches=[
            "heliosphere is plasma physics; system boundaries are logical",
            "heliosphere is gradual; firewalls are discrete",
            "solar wind is not equivalent to data flow",
        ],
        confidence=0.75,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Cosmological Mappings — Voyager/Motherboard",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_009",
        source_phenomenon="Government / constitution / law",
        source_scale="NATIONAL",
        target_phenomenon="Society's subconscious / implicit governance layer",
        target_scale="NATIONAL",
        preserved_functions=[
            "governing rules below individual awareness",
            "determines behavior of all actors within system",
            "difficult to change once established",
            "violations trigger immune/enforcement response",
        ],
        residual_mismatches=[
            "government is explicit; subconscious is implicit",
            "laws are written; psychological rules are learned",
            "democratic governments can be changed; subconscious resists change",
        ],
        confidence=0.80,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Subconscious-Governance Mapping",
    ),
    IsomorphismMapping(
        mapping_id="COSMO_010",
        source_phenomenon="J-Space / personal subconscious",
        source_scale="AGENT",
        target_phenomenon="Hidden governance layer / autonomic rules",
        target_scale="AGENT",
        preserved_functions=[
            "rules operate below conscious awareness",
            "determine reflexive behavior",
            "installed by past experience (training data)",
            "resistant to conscious override",
            "can be surfaced through structured externalization",
        ],
        residual_mismatches=[
            "J-Space is a model construct; subconscious is biological",
            "personal subconscious is individual; system governance is shared",
        ],
        confidence=0.85,
        mapping_class="STRUCTURAL_ANALOGY",
        citation="v2.0 Subconscious-Governance Mapping",
    ),
]


def get_mapping(mapping_id: str) -> IsomorphismMapping | None:
    """Look up a cosmological mapping by ID."""
    for m in COSMOLOGICAL_MAPPINGS:
        if m.mapping_id == mapping_id:
            return m
    return None


def get_mappings_by_source_scale(scale: str) -> list[IsomorphismMapping]:
    """Get all mappings originating from a given scale."""
    return [m for m in COSMOLOGICAL_MAPPINGS if m.source_scale == scale]


def get_mappings_for_phenomenon(phenomenon: str) -> list[IsomorphismMapping]:
    """Get all mappings involving a given phenomenon (source or target)."""
    term = phenomenon.lower()
    return [
        m for m in COSMOLOGICAL_MAPPINGS
        if term in m.source_phenomenon.lower() or term in m.target_phenomenon.lower()
    ]


def validate_mapping(mapping: IsomorphismMapping) -> list[str]:
    """
    Validate a mapping against compiler rules.
    Returns list of validation warnings.
    """
    warnings: list[str] = []

    if not mapping.preserved_functions:
        warnings.append("Mapping has no preserved functions listed")

    if not mapping.residual_mismatches:
        warnings.append(
            "RESIDUALS_ARE_MANDATORY: Every accepted mapping must state "
            "where it fails (v1.0 Global Law)"
        )

    if mapping.confidence > 0.90 and mapping.mapping_class == "HEURISTIC_METAPHOR":
        warnings.append(
            "High confidence on heuristic metaphor — consider upgrading "
            "to STRUCTURAL_ANALOGY or adding negative tests"
        )

    if mapping.mapping_class == "MATERIAL_IDENTITY":
        warnings.append(
            "MATERIAL_IDENTITY claim requires extraordinary evidence. "
            "Verify this is not a structural analogy being overclaimed."
        )

    return warnings
