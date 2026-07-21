"""Universal functional graph translation."""
from dataclasses import dataclass
from expansion.registry.loader import DomainTemplate

@dataclass(frozen=True)
class FunctionalGraph:
    nodes: set[str]
    edges: list[dict]
    coverage_ratio: float

UNIVERSAL_FUNCTIONS = {
    "boundary", "processing", "memory", "control", "growth_regulation", "defense", "output"
}

MEDICAL_TO_UNIVERSAL = {
    "immune_boundary": "boundary",
    "immune_system": "defense",
    "homeostasis": "growth_regulation",
    "homeostasis_regulation": "growth_regulation",
    "control_center": "control",
    "processing_core": "processing",
    "memory_store": "memory",
    "output_layer": "output",
}

def _tokens(text: str) -> set[str]:
    """Split a string into lowercase word tokens on whitespace and underscores."""
    return {t for t in text.lower().replace("_", " ").split() if t}

def build_functional_graph(system_model: dict, template: DomainTemplate) -> FunctionalGraph:
    """Translate a system model into a universal functional graph."""
    nodes: set[str] = set()
    edges: list[dict] = []

    for comp in system_model.get("components", []):
        medical_map = comp.get("medical_map")
        if medical_map:
            universal = MEDICAL_TO_UNIVERSAL.get(medical_map, medical_map)
            # Nodes carry both the medical ontology label and its universal function.
            nodes.add(medical_map)
            nodes.add(universal)

    for rel in system_model.get("relationships", []):
        edges.append(rel)

    # Coverage is calculated against the template's expected components. Exact name
    # matches count first (brief's original); an expected component is also covered
    # when its name tokens appear in the model's component names or medical_map
    # functional labels (e.g. immune_boundary covers defense_boundary via "boundary").
    expected = {c["name"] for c in template.components}
    observed = {c.get("name") for c in system_model.get("components", []) if c.get("name")}

    observed_tokens: set[str] = set()
    for comp in system_model.get("components", []):
        for value in (comp.get("name"), comp.get("medical_map")):
            if value:
                observed_tokens |= _tokens(str(value))

    covered = 0
    for comp in template.components:
        if comp["name"] in observed or _tokens(comp["name"]) & observed_tokens:
            covered += 1
    coverage = covered / max(len(expected), 1)

    return FunctionalGraph(nodes=nodes, edges=edges, coverage_ratio=coverage)
