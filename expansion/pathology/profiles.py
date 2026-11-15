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
    "state states type types kind kinds thing things part parts item items "
    "client server cache protocol signal packet token frame block window mode "
    "agent action value path policy rule check input output update request response".split()
)

_PATHOLOGY_MEDICAL_MAPS = frozenset({
    "pathogen", "cancer", "autoimmune", "sepsis",
    "inflammation", "metastasis", "acute", "chronic",
})
_HIGH_SIGNAL_SHORT_TOKENS = frozenset({"l1", "l2", "l3", "l4", "5g", "kl", "io"})

CONFIDENCE_DIRECT = 0.75
CONFIDENCE_CIRCUMSTANTIAL = 0.6
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    """Meaningful lowercase tokens, excluding filler and generic structural words."""
    words = _TOKEN_RE.findall(text.lower())
    return {
        w
        for w in words
        if (len(w) >= 3 or w in _HIGH_SIGNAL_SHORT_TOKENS)
        and w not in _STOPWORDS
        and w not in _GENERIC_WORDS
    }


def detect_pathologies(system_model: dict, template: DomainTemplate) -> list[Pathology]:
    """Detect pathologies using direct indicators and lower-confidence token overlap."""
    detected: list[Pathology] = []
    components = system_model.get("components", [])
    template_comp_names = {c.get("name") for c in template.components if c.get("name")}
    component_names = {c.get("name") for c in components if c.get("name")}
    pathology_maps = {
        c.get("medical_map")
        for c in components
        if c.get("medical_map") in _PATHOLOGY_MEDICAL_MAPS
    }

    component_tokens: set[str] = set()
    for comp in components:
        name = comp.get("name")
        med = comp.get("medical_map")
        is_healthy_template_comp = name in template_comp_names and med not in _PATHOLOGY_MEDICAL_MAPS
        if name and not is_healthy_template_comp:
            component_tokens |= _tokens(str(name))
        if med and med in _PATHOLOGY_MEDICAL_MAPS:
            component_tokens |= _tokens(str(med))

    for fm in template.failure_modes:
        indicators = set(fm.get("indicators", []))
        fm_med = fm.get("medical_map")
        direct_med = pathology_maps & ({fm_med} if fm_med in _PATHOLOGY_MEDICAL_MAPS else set())
        direct = (component_names & indicators) | direct_med
        fm_tokens = _tokens(" ".join([
            str(fm.get("name", "")),
            str(fm_med or "") if fm_med in _PATHOLOGY_MEDICAL_MAPS else "",
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
                    "basis: " + ("direct (indicator or pathology medical_map match)" if direct else "token overlap with failure-mode text"),
                ],
            ))
    return detected
