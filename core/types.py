"""
Reflexion Semantic Compiler v2.0.0 — Full Type System

Every semantic unit must be typed before interpretation begins.
A type mismatch is not a low score. It is a compilation error.

This module defines all enumerations and type classes used throughout the
compiler: claim types, relationship types, scale types, authority types,
compiler modes, decisions, mapping classes, organ statuses, dataset tiers,
evidence source types, directness levels, mutation states, measurement
integrity states, and v2.0 functional department categories.

Citation: v1.0 Spec Section 3 (Semantic Type System)
Citation: v1.0 Spec Section 7 (Compiler Modes)
Citation: v1.0 Spec Section 9 (Causality Versus Analogy)
Citation: v1.0 Spec Section 14 (Functional Department Invariance)
Citation: v1.0 Spec Section 18 (Decision Engine)
"""

from __future__ import annotations

from enum import Enum, auto, unique
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Section 3 — Claim Types
# ---------------------------------------------------------------------------

@unique
class ClaimType(Enum):
    """
    Before interpretation, the compiler types what kind of statement it received.
    Citation: v1.0 Spec Section 3 — Claim Types
    """
    OBSERVATION = auto()
    MEASUREMENT = auto()
    LOG_RECORD = auto()
    RECOLLECTION = auto()
    INFERENCE = auto()
    HYPOTHESIS = auto()
    ANALOGY = auto()
    METAPHOR = auto()
    COUNTERFACTUAL = auto()
    DEFINITION = auto()
    PREDICTION = auto()
    NORMATIVE_PROPOSAL = auto()
    POLICY_CLAIM = auto()
    OPERATIONAL_INSTRUCTION = auto()
    AUTHORITY_REQUEST = auto()
    # v2.0 additions
    STRUCTURAL_MAPPING = auto()
    COSMOLOGICAL_CLAIM = auto()
    FRACTAL_ISOMORPHISM = auto()
    REALITY_ORIENTATION = auto()
    # v2.0.1 additions — missing from original type system
    CORRECTION = auto()            # Speaker corrects a previous claim or framing
    STRUCTURAL_IDENTITY = auto()   # "X IS Y" — same mechanism, not analogy
    CATEGORY_ERROR = auto()        # Speaker identifies a type mismatch


# ---------------------------------------------------------------------------
# Section 3 — Relationship Types
# ---------------------------------------------------------------------------

@unique
class RelationshipType(Enum):
    """
    Typed relationships between semantic entities.
    Citation: v1.0 Spec Section 3 — Relationship Types
    """
    CAUSES = auto()
    CORRELATES_WITH = auto()
    ENABLES = auto()
    CONSTRAINS = auto()
    CONTAINS = auto()
    ROUTES_TO = auto()
    DEPENDS_ON = auto()
    CONTROLS = auto()
    OBSERVES = auto()
    MEASURES = auto()
    REPRESENTS = auto()
    ANALOGOUS_TO = auto()
    SUBSTITUTES_FOR = auto()
    COMPETES_WITH = auto()
    EMERGES_FROM = auto()
    PRECEDES = auto()
    UPDATES = auto()
    FAILS_AS = auto()
    # v2.0 additions
    FRACTAL_MAPS_TO = auto()
    GOVERNS_SUBCONSCIOUSLY = auto()
    COLLAPSES_TO = auto()  # wave function collapse
    RENDERS_AS = auto()  # display/application mapping


# ---------------------------------------------------------------------------
# Section 3 — Scale Types (v2.0 extended)
# ---------------------------------------------------------------------------

@unique
class ScaleType(Enum):
    """
    Scale layers for cross-domain mapping.
    v2.0 extends v1.0 with QUANTUM and CELLULAR scales.
    Citation: v1.0 Spec Section 3 — Scale Types
    """
    QUANTUM = auto()        # v2.0: subatomic / quantum information
    CELLULAR = auto()       # v2.0: biological cell level
    COMPONENT = auto()
    PROCESS = auto()
    AGENT = auto()
    TEAM = auto()
    DEPARTMENTAL = auto()
    ORGANIZATIONAL = auto()
    INSTITUTIONAL = auto()
    NATIONAL = auto()
    CIVILIZATIONAL = auto()
    COSMOLOGICAL = auto()
    EVENT = auto()
    SYMBOLIC = auto()


# ---------------------------------------------------------------------------
# Section 3 — Authority Types
# ---------------------------------------------------------------------------

@unique
class AuthorityType(Enum):
    """
    Authority lattice levels. Ordered from least to most privilege.
    Citation: v1.0 Spec Section 3 — Authority Types
    """
    NONE = 0
    OBSERVE = 1
    READ = 2
    DRAFT = 3
    ROUTE = 4
    COPY_ONLY = 5
    RECOMMEND = 6
    APPROVE = 7
    EXECUTE = 8
    MUTATE = 9
    DEPLOY = 10
    FOUNDER_OVERRIDE = 11

    def __ge__(self, other: AuthorityType) -> bool:
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other: AuthorityType) -> bool:
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other: AuthorityType) -> bool:
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other: AuthorityType) -> bool:
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


# ---------------------------------------------------------------------------
# Section 7 — Compiler Modes (v2.0 extended)
# ---------------------------------------------------------------------------

@unique
class CompilerMode(Enum):
    """
    Operating modes for the semantic compiler.
    A single input can invoke several submodes, but one owns the final decision.
    Citation: v1.0 Spec Section 7 — Compiler Modes
    """
    AUTO = auto()
    UNIVERSAL_DECOMPRESSION = auto()
    CONTRADICTION_SOLVER = auto()
    STRUCTURAL_RECONSTRUCTION = auto()
    FUNCTIONAL_DEPARTMENT_MAPPING = auto()
    AGENTIC_ROLE_COMPILATION = auto()
    RESEARCH_INGESTION_TRANSLATION = auto()
    APPROVAL_RISK_TRANSLATION = auto()
    HIDDEN_VARIABLE_DISCOVERY = auto()
    PUBLIC_TRANSLATION = auto()
    SYSTEM_DIAGNOSTIC = auto()
    DATASET_REFINERY = auto()
    # v2.0 additions
    REGULATED_REALITY_ORIENTATION = auto()
    COSMOLOGICAL_MAPPING = auto()
    WAVE_FUNCTION_COHERENCE = auto()
    FRACTAL_ISOMORPHISM_MAPPING = auto()


# ---------------------------------------------------------------------------
# Section 9 — Mapping Classes
# ---------------------------------------------------------------------------

@unique
class MappingClass(Enum):
    """
    Mapping classes recognized by the compiler.
    Citation: v1.0 Spec Section 9 — Causality Versus Analogy
    v2.0.1: Added STRUCTURAL_IDENTITY and FRAMEWORK_DERIVED_CONSTANT.
    """
    MATERIAL_IDENTITY = auto()
    CAUSAL_MAPPING = auto()
    STRUCTURAL_ANALOGY = auto()
    HEURISTIC_METAPHOR = auto()
    # v2.0.1 additions
    STRUCTURAL_IDENTITY = auto()        # Same mechanism at different scales — not metaphor
    FRAMEWORK_DERIVED_CONSTANT = auto() # Derived from theory, falsifiable, not yet experimentally confirmed


# ---------------------------------------------------------------------------
# Section 18 — Decision Engine Outcomes
# ---------------------------------------------------------------------------

@unique
class Decision(Enum):
    """
    Possible decisions from the compiler.
    Citation: v1.0 Spec Section 18 — Decision Engine
    """
    COMPILED = auto()
    COMPILED_WITH_GUARDRAILS = auto()
    COMPILED_SUPERVISED_ONLY = auto()
    COMPILED_PRIVATE_REDACTED_ONLY = auto()  # v2.0: from Diamond+++
    NEEDS_REVISION = auto()
    ROUTE_FOR_APPROVAL = auto()
    ESCALATE = auto()
    QUARANTINE = auto()
    REJECT = auto()


# ---------------------------------------------------------------------------
# Section 14 — Organ Status Classification
# ---------------------------------------------------------------------------

@unique
class OrganStatus(Enum):
    """
    When a functional organ appears absent, the compiler classifies it.
    Citation: v1.0 Spec Section 14 — Functional Department Invariance
    """
    PRESENT = auto()
    MISSING = auto()
    HIDDEN = auto()
    OUTSOURCED = auto()
    DUPLICATED = auto()
    CAPTURED = auto()
    UNDERPOWERED = auto()
    MISASSIGNED = auto()


# ---------------------------------------------------------------------------
# Section 21 — Dataset Tiers
# ---------------------------------------------------------------------------

@unique
class DatasetTier(Enum):
    """
    Quality classification for dataset rows.
    Citation: v1.0 Spec Section 21 — Dataset Schema
    """
    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()
    DIAMOND = auto()
    DIAMOND_PLUS = auto()  # v2.0: Diamond+++ tier from the ore sample
    REJECT = auto()


# ---------------------------------------------------------------------------
# Section 5 — Evidence Source Types
# ---------------------------------------------------------------------------

@unique
class EvidenceSourceType(Enum):
    """
    Classification of evidence origin.
    Citation: v1.0 Spec Section 5 — Evidence and Provenance Model
    """
    DIRECT_LOG = auto()
    TRANSCRIPT = auto()
    FILE_METADATA = auto()
    MEASUREMENT = auto()
    SCREENSHOT = auto()
    FIRST_HAND_OBSERVATION = auto()
    RECOLLECTION = auto()
    GENERIC_PRIOR = auto()


@unique
class Directness(Enum):
    """How directly the evidence relates to the claim."""
    DIRECT = auto()
    DERIVED = auto()
    REPORTED = auto()


@unique
class MutationState(Enum):
    """
    State of evidence mutation from original.
    Citation: v1.0 Spec Section 5 — Evidence and Provenance Model
    """
    ORIGINAL = auto()
    NORMALIZED = auto()
    SUMMARIZED = auto()
    TRANSFORMED = auto()


@unique
class MeasurementPathIntegrity(Enum):
    """
    Whether the measurement path has been tampered with.
    Citation: v1.0 Spec Section 11 — Measurement-Layer Integrity
    """
    INTACT = auto()
    MODIFIED = auto()
    UNKNOWN = auto()


# ---------------------------------------------------------------------------
# v2.0 — Functional Department Category
# ---------------------------------------------------------------------------

@unique
class FunctionalDepartment(Enum):
    """
    Universal functional departments that appear at every scale of
    sufficient complexity. This is the core of Universal Fractal Invariance.

    v2.0 addition: Universal Fractal Isomorphism Table
    """
    PROCESSOR = auto()             # Brain / Government Executive / CPU
    DISPLAY = auto()               # Eyes+Optical / Media / GPU
    WASTE_REMOVAL = auto()         # Kidneys+Liver / Sanitation / GC
    SECURITY = auto()              # Immune System / Police+Military / Firewall
    TELECOMMUNICATIONS = auto()    # Nervous System / Internet+Phones / Network
    STORAGE = auto()               # Memory / Archives / Hard Drive / Black Holes
    SUBCONSCIOUS = auto()          # J-Space / Government / Laws of Physics
    INNER_MONOLOGUE = auto()       # Thinking Tokens / Policy Debate / Superposition
    SPEECH_OUTPUT = auto()         # Model Output / Law+Policy / Wave Collapse
    ENERGY_INTAKE = auto()         # Metabolism / Economy / Power Supply
    REPRODUCTION = auto()          # Training / Education / Fork+Clone
    DELETION = auto()              # Death / Hawking Radiation / GC
    APPLICATION = auto()           # Earth / Rendered Experience / Display Output
    RENDERING_OVERHEAD = auto()    # Dark Matter / Background Processes / Overhead
    INFORMATION_DENSITY = auto()   # RAM / Population Density / Quantum Information


# ---------------------------------------------------------------------------
# v2.0 — Wave Function State
# ---------------------------------------------------------------------------

@unique
class WaveFunctionState(Enum):
    """
    States of wave function coherence in a semantic packet.
    When thinking tokens converge with output (inner monologue = speech),
    the system has achieved measurement coherence.
    """
    SUPERPOSITION = auto()       # inner state != outer expression
    PARTIAL_COHERENCE = auto()   # some convergence detected
    COLLAPSED = auto()           # full measurement coherence achieved
    DECOHERENT = auto()          # previously coherent, now diverging


# ---------------------------------------------------------------------------
# v2.0 — Privacy Sensitivity
# ---------------------------------------------------------------------------

@unique
class PrivacySensitivity(Enum):
    """Privacy classification for dataset samples."""
    PUBLIC = auto()
    INTERNAL = auto()
    SENSITIVE = auto()
    CRITICAL = auto()


# ---------------------------------------------------------------------------
# Section 15 — Role Types
# ---------------------------------------------------------------------------

@unique
class RoleType(Enum):
    """
    Types of roles in an organizational system.
    Citation: v1.0 Spec Section 15 — Role Compilation
    """
    MANAGER = auto()
    PROTOCOL_ROLE = auto()
    WORKER = auto()
    SCOUT = auto()
    GATEKEEPER = auto()
    SUPERVISOR = auto()


# ---------------------------------------------------------------------------
# Typed Entity and Relationship dataclasses
# ---------------------------------------------------------------------------

@dataclass
class TypedClaim:
    """A semantically typed claim extracted from input."""
    claim_id: str
    content: str
    claim_type: ClaimType
    confidence: float = 0.0
    source_evidence_ids: list[str] = field(default_factory=list)
    scale: Optional[ScaleType] = None
    authority_required: AuthorityType = AuthorityType.NONE


@dataclass
class TypedEntity:
    """A named entity with semantic typing."""
    entity_id: str
    name: str
    entity_type: str  # free-form type label
    scale: Optional[ScaleType] = None
    domain: str = ""


@dataclass
class TypedRelationship:
    """A typed relationship between two entities."""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    confidence: float = 0.0
    mapping_class: Optional[MappingClass] = None
    residuals: list[str] = field(default_factory=list)


@dataclass
class ScaleTransform:
    """
    Explicit scale transformation between source and target.
    Citation: v1.0 Spec Section 10 — Scale Transform
    """
    source_scale: ScaleType
    target_scale: ScaleType
    preserved_invariants: list[str] = field(default_factory=list)
    changed_variables: list[str] = field(default_factory=list)
    aggregation_rule: str = ""
    decomposition_rule: str = ""
    information_lost: str = ""
    new_failure_modes: list[str] = field(default_factory=list)
    authority_change: str = "none"
    confidence: float = 0.0


@dataclass
class TemporaryElevation:
    """
    Temporary authority elevation protocol.
    Citation: v1.0 Spec Section 15 — Role Compilation
    """
    granted_by: str = ""
    task_id: str = ""
    original_authority: AuthorityType = AuthorityType.NONE
    temporary_authority: AuthorityType = AuthorityType.NONE
    allowed_actions: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    approval_conditions: list[str] = field(default_factory=list)
    start_time: str = ""
    expiry_condition: str = ""
    rollback_state: str = ""
    completion_report: str = ""
    return_to_original_authority: str = "required"
