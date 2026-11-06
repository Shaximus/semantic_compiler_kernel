"""Canonical medical ontology for cross-domain system reasoning.

Vocabulary contract (pinned by tests/expansion/test_medical_ontology_review.py):

* MEDICAL_ONTOLOGY is the canonical concept set. Every medical_map used in
  a domain template's failure modes or architecture patterns is a key of it.
* ONTOLOGY_ALIASES maps legacy spellings (immune_boundary,
  homeostasis_regulation) onto canonical concepts.
* FUNCTIONAL_ROLE_TAGS are computing-system roles, not medical concepts.
"""
from dataclasses import dataclass
import re


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
    "physiotherapy": MedicalConcept("physiotherapy", "Graduated load testing / rehabilitation", "Brings a restored component back to full load in steps instead of relying on it at once."),
}

ONTOLOGY_ALIASES: dict[str, str] = {
    "immune_boundary": "immune_system",
    "homeostasis_regulation": "homeostasis",
}
FUNCTIONAL_ROLE_TAGS: frozenset[str] = frozenset({"processing_core", "memory_store", "output_layer"})


def normalize_concept_name(name: str) -> str:
    """Normalize case and word separators to canonical snake_case."""
    return re.sub(r"[\s\-_]+", "_", str(name).strip().lower()).strip("_")


def resolve_concept(name: str) -> MedicalConcept | None:
    """Resolve a canonical concept or legacy alias. Unknown names return None."""
    key = normalize_concept_name(name)
    key = ONTOLOGY_ALIASES.get(key, key)
    return MEDICAL_ONTOLOGY.get(key)


def get_concept(name: str) -> MedicalConcept:
    """Return a concept or raise KeyError for an unknown name."""
    concept = resolve_concept(name)
    if concept is None:
        raise KeyError(name)
    return concept


def is_valid_medical_map(name: str) -> bool:
    """True only for exact canonical keys."""
    return name in MEDICAL_ONTOLOGY


def classify_medical_map(name: str) -> str:
    """Classify as ontology, alias, functional_role, or unknown."""
    if name in MEDICAL_ONTOLOGY:
        return "ontology"
    key = normalize_concept_name(name)
    if key in MEDICAL_ONTOLOGY:
        return "ontology"
    if key in ONTOLOGY_ALIASES:
        return "alias"
    if key in FUNCTIONAL_ROLE_TAGS:
        return "functional_role"
    return "unknown"
