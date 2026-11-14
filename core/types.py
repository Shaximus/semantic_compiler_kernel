"""Core type definitions for the Reflexion Semantic Compiler."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

class ClaimType(str, Enum):
    FACT = "FACT"
    OPINION = "OPINION"
    PREDICTION = "PREDICTION"
    INSTRUCTION = "INSTRUCTION"
    QUESTION = "QUESTION"
    # ... more types from the package

class RelationshipType(str, Enum):
    CAUSES = "CAUSES"
    ENABLES = "ENABLES"
    INHIBITS = "INHIBITS"
    IS_A = "IS_A"
    PART_OF = "PART_OF"
    # ... 

class ScaleType(str, Enum):
    MICRO = "MICRO"
    MESO = "MESO"
    MACRO = "MACRO"
    COSMIC = "COSMIC"

class AuthorityType(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"
    SELF = "SELF"

class CompilerMode(str, Enum):
    STANDARD = "STANDARD"
    DEFENSE = "DEFENSE"
    REALITY_ORIENTATION = "REALITY_ORIENTATION"
    COHERENCE = "COHERENCE"

class Decision(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    PENDING = "PENDING"
    QUARANTINE = "QUARANTINE"

class MappingClass(str, Enum):
    ISOMORPHIC = "ISOMORPHIC"
    ANALOGOUS = "ANALOGOUS"
    METAPHORICAL = "METAPHORICAL"
    NONE = "NONE"

class DatasetTier(str, Enum):
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"
    REJECT = "REJECT"
