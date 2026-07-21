"""Infer missing components using cross-domain analogy."""
from dataclasses import dataclass
from expansion.registry.loader import DomainTemplate

@dataclass(frozen=True)
class MissingComponent:
    function: str
    inferred_by: str
    source_domain: str
    confidence: float
    status: str  # observed | inferred_by_analogy | absent_confirmed | unobserved

def reconstruct_missing(system_model: dict, template: DomainTemplate) -> list[MissingComponent]:
    """Identify components expected by the template but missing from the model."""
    observed = {c.get("name") for c in system_model.get("components", [])}
    missing: list[MissingComponent] = []

    for comp in template.components:
        if comp["name"] not in observed:
            missing.append(MissingComponent(
                function=comp["name"],
                inferred_by="template_expectation",
                source_domain=template.domain,
                confidence=0.7,
                status="inferred_by_analogy",
            ))
    return missing
