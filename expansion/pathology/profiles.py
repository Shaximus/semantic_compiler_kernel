"""Detect pathologies in a system model."""
import re

from semantic_compiler.expansion.pathology.taxonomy import Pathology
from semantic_compiler.expansion.registry.loader import DomainTemplate

_STOPWORDS = frozenset(
    "the and for with from into onto over under about after before between through "
    "of to in on at by or is are was were be been being it its this that these those "
    "which what who whom whose but not nor so than then too very can will would could "
    "should may might must has have had does did done also only just such each every "
    "any all some more most other another both either neither one two three".split()
)
_GENERIC_WORDS = frozenset(
    "system systems data process processes service services component components "
    "model models structure function functions layer layers level levels unit units "
    "state states type types kind kinds thing things part parts item items".split()
)

CONFIDENCE_DIRECT = 0.75
CONFIDENCE_CIRCUMSTANTIAL = 0.6


def _tokens(text: str) -> set[str]:
    """Meaningful lowercase tokens, excluding filler and generic structural words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) >= 3 and w not in _STOPWORDS and w not in _GENERIC_WORDS}


def detect_pathologies(system_model: dict, template: DomainTemplate) -> list[Pathology]:
    """Detect pathologies using direct indicators and lower-confidence token overlap."""
    detected: list[Pathology] = []
    components = system_model.get("components", [])
    component_names = {c.get("name") for c in components if c.get("name")}
    medical_maps = {c.get("medical_map") for c in components if c.get("medical_map")}

    component_tokens: set[str] = set()
    for value in component_names | medical_maps:
        component_tokens |= _tokens(str(value))

    for fm in template.failure_modes:
        indicators = set(fm.get("indicators", []))
        direct = (component_names & indicators) | (medical_maps & {fm.get("medical_map")})
        fm_tokens = _tokens(" ".join([
            str(fm.get("name", "")),
            str(fm.get("medical_map", "")),
            str(fm.get("description", "")),
            *(str(i) for i in indicators),
        ]))
        circumstantial = component_tokens & fm_tokens
        matched = direct | circumstantial
        if matched:
            detected.append(Pathology(
                name=fm["name"],
                medical_map=fm["medical_map"],
                description=fm["description"],
                indicators=sorted(matched),
                confidence=CONFIDENCE_DIRECT if direct else CONFIDENCE_CIRCUMSTANTIAL,
                evidence=[
                    f"matched indicators: {sorted(matched)}",
                    "basis: " + ("direct (indicator or medical_map match)" if direct else "token overlap with failure-mode text"),
                ],
            ))
    return detected
