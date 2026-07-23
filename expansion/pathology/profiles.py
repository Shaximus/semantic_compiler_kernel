"""Detect pathologies in a system model."""
from semantic_compiler.expansion.pathology.taxonomy import Pathology
from semantic_compiler.expansion.registry.loader import DomainTemplate

def _tokens(text: str) -> set[str]:
    """Split a string into lowercase word tokens on whitespace and underscores."""
    return {t for t in text.lower().replace("_", " ").split() if t}

def detect_pathologies(system_model: dict, template: DomainTemplate) -> list[Pathology]:
    """Detect pathologies by matching system model against template failure modes."""
    detected: list[Pathology] = []
    components = system_model.get("components", [])
    component_names = {c.get("name") for c in components if c.get("name")}
    medical_maps = {c.get("medical_map") for c in components if c.get("medical_map")}

    # Tokens from component names and medical_map values, e.g. "growth_process" -> {"growth", "process"}
    component_tokens: set[str] = set()
    for value in component_names | medical_maps:
        component_tokens |= _tokens(str(value))

    for fm in template.failure_modes:
        # Simple heuristic: if a component or indicator matches the failure mode name or indicators
        indicators = set(fm.get("indicators", []))
        matched = (component_names & indicators) | (medical_maps & {fm.get("medical_map")})
        # Component name / medical_map tokens matched against the failure mode's own text
        fm_tokens = _tokens(" ".join([
            str(fm.get("name", "")),
            str(fm.get("medical_map", "")),
            str(fm.get("description", "")),
            *(str(i) for i in indicators),
        ]))
        matched |= component_tokens & fm_tokens
        if matched:
            detected.append(Pathology(
                name=fm["name"],
                medical_map=fm["medical_map"],
                description=fm["description"],
                indicators=sorted(matched),
                confidence=0.75,
                evidence=[f"matched indicators: {sorted(matched)}"],
            ))
    return detected
