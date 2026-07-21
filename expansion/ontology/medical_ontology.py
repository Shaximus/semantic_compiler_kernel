"""Canonical medical ontology for cross-domain system reasoning."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MedicalConcept:
    name: str
    description: str
    cross_domain_meaning: str


MEDICAL_ONTOLOGY: dict[str, MedicalConcept] = {
    "homeostasis": MedicalConcept("homeostasis", "System stability / equilibrium maintenance", "Keeps variables within safe operating ranges."),
    "immune_system": MedicalConcept("immune_system", "Defense mechanisms, threat detection, boundary integrity", "Detects and responds to threats; maintains self/non-self boundary."),
    "pathogen": MedicalConcept("pathogen", "External attack vector", "Malicious input, hostile actor, or invasive instruction."),
    "cancer": MedicalConcept("cancer", "Uncontrolled growth / resource capture", "Growth without resource feedback or regulatory control."),
    "autoimmune": MedicalConcept("autoimmune", "Self-attack / internal sabotage", "System attacks its own healthy components."),
    "sepsis": MedicalConcept("sepsis", "Systemic cascade / cascading failure", "Local failure propagates into systemic collapse."),
    "inflammation": MedicalConcept("inflammation", "Stress response / overload", "Response to damage or stress; may become harmful if chronic."),
    "diagnosis": MedicalConcept("diagnosis", "Fault detection / root-cause analysis", "Identifies the underlying cause of failure."),
    "prognosis": MedicalConcept("prognosis", "Failure prediction / risk assessment", "Estimates likely trajectory if untreated."),
    "treatment": MedicalConcept("treatment", "Repair / mitigation / architecture improvement", "Action taken to restore health or improve structure."),
    "vaccination": MedicalConcept("vaccination", "Pre-emptive hardening / resilience training", "Prepares system to resist known threats."),
    "quarantine": MedicalConcept("quarantine", "Isolation / containment", "Isolates affected component to prevent spread."),
    "metastasis": MedicalConcept("metastasis", "Lateral spread / privilege escalation", "Failure spreads from original site to other components."),
    "remission": MedicalConcept("remission", "Recovery / stabilization", "Pathology is controlled or absent."),
    "chronic": MedicalConcept("chronic", "Persistent degraded state / technical debt", "Long-term low-level dysfunction."),
    "acute": MedicalConcept("acute", "Sudden failure / crisis event", "Rapid-onset severe dysfunction."),
}


def get_concept(name: str) -> MedicalConcept:
    return MEDICAL_ONTOLOGY[name]


def is_valid_medical_map(name: str) -> bool:
    return name in MEDICAL_ONTOLOGY
