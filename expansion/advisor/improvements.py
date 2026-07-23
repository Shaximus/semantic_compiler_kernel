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

# Deterministic remediation heuristics keyed by medical_map. Simple by design:
# the medical ontology tells you the *class* of treatment, the template
# failure mode supplies the specifics.
_MEDICAL_MAP_REMEDIATION = {
    "pathogen": "isolate the input boundary and add validation filtering",
    "inflammation": "reduce error cascades; add input sanitation and circuit breakers",
    "immune_system": "restore layered boundary defense",
    "immune_boundary": "re-establish the boundary's filtering function",
    "homeostasis_regulation": "add feedback-driven stabilization loops",
    "memory_store": "repair state persistence and integrity checks",
    "processing_core": "simplify and re-verify the core transform path",
    "output_layer": "add output verification before emission",
}
_DEFAULT_REMEDIATION = "remove the matched indicators and re-test the failure surface"


def generate_advice(
    system_model: dict,
    pathologies: list[Pathology],
    missing: list[MissingComponent],
    failure_modes: list[dict] | None = None,
) -> dict:
    """Generate treatment-protocol advice from pathologies and missing components.

    ``failure_modes`` (from the domain template) enriches prescriptions and
    resilience drills with the template's own descriptions and indicators.
    """
    failure_modes = failure_modes or []
    fm_by_name = {fm.get("name"): fm for fm in failure_modes}

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

        fm = fm_by_name.get(p.name, {})
        remediation = _MEDICAL_MAP_REMEDIATION.get(p.medical_map, _DEFAULT_REMEDIATION)
        indicators = fm.get("indicators", p.indicators)
        advice["prescriptions"].append(AdvisorSuggestion(
            kind="prescription",
            description=f"Treat {p.name} ({p.medical_map}): {remediation}",
            medical_ontology_reference=p.medical_map,
            confidence=p.confidence,
            evidence=list(p.evidence),
            domain_specific_translation=(
                f"Address indicators: {', '.join(indicators)}" if indicators
                else remediation
            ),
            estimated_impact="high" if p.confidence > 0.7 else "medium",
        ))

        # Vaccination pattern: controlled exposure to the failure mode's
        # indicators before they occur in production.
        if indicators:
            advice["resilience_training"].append(AdvisorSuggestion(
                kind="resilience_training",
                description=(
                    f"Stress-test against {p.name}: inject its indicators "
                    f"({', '.join(indicators)}) in controlled drills"
                ),
                medical_ontology_reference="vaccination",
                confidence=0.85,
                evidence=[f"derived from failure mode: {p.name}"],
                domain_specific_translation="adversarial input testing",
                estimated_impact="medium",
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
        advice["resilience_training"].append(AdvisorSuggestion(
            kind="resilience_training",
            description=(
                f"Drill the restored {m.function} component under load before "
                f"relying on it (inferred via {m.inferred_by})"
            ),
            medical_ontology_reference="physiotherapy",
            confidence=m.confidence,
            evidence=[f"missing component inferred from {m.source_domain} template"],
            domain_specific_translation=f"graduated load testing of {m.function}",
            estimated_impact="medium",
        ))

    return advice
