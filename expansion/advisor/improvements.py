"""Architecture improvement advisor."""
from dataclasses import dataclass
from semantic_compiler.expansion.pathology.taxonomy import Pathology
from semantic_compiler.expansion.reconstruction.missing_components import MissingComponent

@dataclass(frozen=True)
class AdvisorSuggestion:
    kind: str
    description: str
    medical_ontology_reference: str
    confidence: float
    evidence: list[str]
    domain_specific_translation: str
    estimated_impact: str

def generate_advice(system_model: dict, pathologies: list[Pathology], missing: list[MissingComponent]) -> dict:
    """Generate treatment-protocol advice from pathologies and missing components."""
    advice = {
        "diagnosis": [],
        "prescriptions": [],
        "architecture_improvements": [],
        "resilience_training": [],
        "prognosis": "stable" if not pathologies else "at_risk",
    }

    for p in pathologies:
        advice["diagnosis"].append(AdvisorSuggestion(
            kind="diagnosis",
            description=f"{p.name}: {p.description}",
            medical_ontology_reference=p.medical_map,
            confidence=p.confidence,
            evidence=p.evidence,
            domain_specific_translation=f"Detected {p.medical_map} pattern",
            estimated_impact="high" if p.confidence > 0.7 else "medium",
        ))

    for m in missing:
        if m.function in ("homeostasis_regulation", "defense", "control"):
            advice["architecture_improvements"].append(AdvisorSuggestion(
                kind="architecture_improvement",
                description=f"Add missing {m.function}",
                medical_ontology_reference=m.function,
                confidence=m.confidence,
                evidence=[f"inferred from {m.source_domain} template"],
                domain_specific_translation=f"Introduce {m.function} component",
                estimated_impact="high",
            ))

    return advice
