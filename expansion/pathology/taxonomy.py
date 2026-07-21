"""Universal pathology classes."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Pathology:
    name: str
    medical_map: str
    description: str
    indicators: list[str]
    confidence: float
    evidence: list[str]
