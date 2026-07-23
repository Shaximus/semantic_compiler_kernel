"""
Reflexion Semantic Compiler V2.1.3

An evidence-conditioned, cross-domain semantic compiler with a typed intermediate
representation, hard logical gates, calibrated uncertainty, non-executing governance,
and Universal Fractal Isomorphism mapping.

The compiler does not search for the prettiest metaphor. It searches for the
highest-coherence structure that survives evidence, causality, scale, boundary,
contradiction, measurement, authority, and wave-function coherence checks.
"""

__version__ = "2.1.3"
__compiler_name__ = "Reflexion Semantic Compiler"

from semantic_compiler.compat import compile_semantic_packet
from semantic_compiler.core.packet import SemanticPacket
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
