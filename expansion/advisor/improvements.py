"""Architecture improvement advisor."""
from dataclasses import dataclass
from semantic_compiler.expansion.ontology.medical_ontology import normalize_concept_name, resolve_concept
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
_ONTOLOGY_REMEDIATION = {
    "homeostasis": "define safe operating ranges and add alarms with automatic correction when a variable leaves them",
    "cancer": "reintroduce regulatory feedback on the runaway growth: cap its resource use and make it justify its allocation",
    "autoimmune": "narrow the defense mechanism's targeting so it stops acting on healthy components; add self-recognition checks",
    "sepsis": "break the cascade: isolate failing components and add circuit breakers and bulkheads so local failure cannot become systemic",
    "diagnosis": "instrument the failure surface and trace the fault to its root cause before changing anything",
    "prognosis": "estimate the failure trajectory and set early-warning thresholds before the next degradation",
    "treatment": "apply the smallest verified repair and confirm the failure indicators clear",
    "vaccination": "harden against the known threat by rehearsing it in controlled drills",
    "quarantine": "isolate the affected component and cut its links to the rest of the system until it is verified clean",
    "metastasis": "cut the spread path: restrict privileges and lateral links from the origin component and audit what it already reached",
    "remission": "keep monitoring after recovery; define relapse criteria and the rollback path",
    "chronic": "schedule remediation of the persistent low-level dysfunction instead of working around it; track it with an owner",
    "acute": "contain first: stop the spread, then restore service and investigate",
    "physiotherapy": "reintroduce the restored component under graduated load, one step at a time",
}
_MEDICAL_MAP_REMEDIATION = {**_ONTOLOGY_REMEDIATION, **_MEDICAL_MAP_REMEDIATION}
_DEFAULT_REMEDIATION = "remove the matched indicators and re-test the failure surface"


def remediation_for(medical_map: str) -> str:
    """Use exact key, tolerant/alias lookup, then a safe default."""
    key = normalize_concept_name(medical_map)
    if key in _MEDICAL_MAP_REMEDIATION:
        return _MEDICAL_MAP_REMEDIATION[key]
    concept = resolve_concept(medical_map)
    if concept is not None and concept.name in _MEDICAL_MAP_REMEDIATION:
        return _MEDICAL_MAP_REMEDIATION[concept.name]
    return _DEFAULT_REMEDIATION


_CRITICAL_COMPONENT_CONCEPTS = {
    "homeostasis": "homeostasis",
    "control": "homeostasis",
    "defense": "immune_system",
}


def _critical_concept(function: str) -> str | None:
    """Ontology concept represented by a critical missing component."""
    for token in function.lower().replace("-", "_").split("_"):
        if token in _CRITICAL_COMPONENT_CONCEPTS:
            return _CRITICAL_COMPONENT_CONCEPTS[token]
    return None


def generate_advice(
    system_model: dict,
    pathologies: list[Pathology],
    missing: list[MissingComponent],
    failure_modes: list[dict] | None = None,
) -> dict:
    """Generate treatment-protocol advice from pathologies and missing components."""
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
        remediation = remediation_for(p.medical_map)
        indicators = fm.get("indicators", p.indicators)
        advice["prescriptions"].append(AdvisorSuggestion(
            kind="prescription",
            description=f"Treat {p.name} ({p.medical_map}): {remediation}",
            medical_ontology_reference=p.medical_map,
            confidence=p.confidence,
            evidence=list(p.evidence),
            domain_specific_translation=(
                f"Address indicators: {', '.join(indicators)}" if indicators else remediation
            ),
            estimated_impact="high" if p.confidence > 0.7 else "medium",
        ))
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
        critical_concept = _critical_concept(m.function)
        if critical_concept is not None:
            advice["architecture_improvements"].append(AdvisorSuggestion(
                kind="architecture_improvement",
                description=f"Add missing {m.function}",
                medical_ontology_reference=critical_concept,
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
