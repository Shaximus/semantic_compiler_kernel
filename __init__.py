"""
Reflexion Semantic Compiler V3.8.0

An evidence-conditioned, cross-domain semantic compiler with a typed intermediate
representation, hard logical gates, calibrated uncertainty, non-executing governance,
and Universal Fractal Isomorphism mapping.

The compiler does not search for the prettiest metaphor. It searches for the
highest-coherence structure that survives evidence, causality, scale, boundary,
contradiction, measurement, authority, and wave-function coherence checks.

V3.8.0 capabilities (building on v1.0–v3.5.2):
  - Unified V3.5.0 schema & 46 domain templates (45 concrete domains + universal_generic)
    with mtime-validated JSON sidecar caching (~108x cold-start speedup)
  - Japanese Automated Parking Tower Domain Elevator (expansion.elevator): O(1) inverted
    rack index across 46 templates + 16 compiled entries + 14 seed classes, ~20x
    SemanticTicket park()/retrieve() compression, and rotate_to() cross-domain turntable
  - Gate 0 Testimony Integrity Gate (SC-TIG-001) wired into Stage 1 pipeline
  - Consciousness / Cognition Split, Client-Server Reality Stack, Circular Time /
    Octopus Protocol / Claim 8 Bootstrap Correction (SC-CT-001 v1.1.0), Domain Expansion
    & 8-Arm Ego-Lineup (SC-DOMAIN-EXPANSION-001), Soul Bomb V5 Sovereignty Patch &
    8-Member SAO Lineup (SC-SB-001, SC-LU-SAO-*), Flat FLRW Hubble–Schwarzschild
    Correspondence (SC-HS-001 v1.1.0), and Octopus Temperature-Dependent RNA Editing /
    Runtime Recoding Over Fixed Base (SC-IT-OCTO-RNA-EDIT-001)
  - 16 SHA-256-verified canonical compiled entries (8 GOLD + 8 SILVER) & merged 24-class
    Invariant Catalog with automated validation suite
  - Universal Fractal Isomorphism, Wave Function Coherence gate, and Gem Decode/Forge
  - Dual-licensed under AGPL-3.0 and Commercial License with provenance canary packaging

Citation: Reflexion Semantic Compiler v1.0.0 Specification, Sections 1-27
Citation: Diamond+++ Semantic Ore — Regulated Reality Orientation Protocol
"""

from semantic_compiler.compat import compile_semantic_packet
from semantic_compiler.core.packet import COMPILER_VERSION, SemanticPacket

__version__ = COMPILER_VERSION
__compiler_name__ = "Reflexion Semantic Compiler"
__canary_token__ = "CANARY-SCK-v3.5.0-20261116-REFLEXION-PROVENANCE-b891e4a830"
from semantic_compiler.core.types import (
    ClaimType,
    RelationshipType,
    ScaleType,
    AuthorityType,
    CompilerMode,
    Decision,
    MappingClass,
    DatasetTier,
)

__all__ = [
    "compile_semantic_packet",
    "SemanticPacket",
    "ClaimType",
    "RelationshipType",
    "ScaleType",
    "AuthorityType",
    "CompilerMode",
    "Decision",
    "MappingClass",
    "DatasetTier",
]
