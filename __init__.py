"""
Reflexion Semantic Compiler V3.5.2

An evidence-conditioned, cross-domain semantic compiler with a typed intermediate
representation, hard logical gates, calibrated uncertainty, non-executing governance,
and Universal Fractal Isomorphism mapping.

The compiler does not search for the prettiest metaphor. It searches for the
highest-coherence structure that survives evidence, causality, scale, boundary,
contradiction, measurement, authority, and wave-function coherence checks.

V3.5.x capabilities (building on v1.0–v3.1.1):
  - Unified V3.5.0 schema & 44 domain templates (43 concrete domains + universal_generic)
  - Gate 0 Testimony Integrity Gate (SC-TIG-001) wired into Stage 1 pipeline
  - Consciousness / Cognition Split, Client-Server Reality Stack, and Circular Time /
    Octopus Protocol / Claim 8 Bootstrap Correction (SC-CT-001 v1.1.0)
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
