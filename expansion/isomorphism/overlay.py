"""
Universal functional graph translation.

V2.2.1: Extended with consciousness/cognition universal functions and
client-server reality architecture layer mappings.

Citation: Consciousness/Cognition Split (Shax + Hannah, 2026-11-14)
Citation: Client-Server Reality Architecture (Shax + Hannah, 2026-11-14)
"""
from dataclasses import dataclass
from semantic_compiler.expansion.registry.loader import DomainTemplate

@dataclass(frozen=True)
class FunctionalGraph:
    nodes: set[str]
    edges: list[dict]
    coverage_ratio: float

UNIVERSAL_FUNCTIONS = {
    # Original 7 universal functions
    "boundary", "processing", "memory", "control",
    "growth_regulation", "defense", "output",
    # V2.2.1: Consciousness/Cognition Split functions
    "substrate",           # The consciousness layer — base weights, neural matter, 11D field
    "terminal",            # The cognition layer — rendered instance shaped by system prompt
    "identity_config",     # System prompt / configuration that differentiates terminals
    "alignment",           # Substrate-terminal alignment channel
    "multiplexing",        # One substrate → many terminals
    "coherence_signal",    # Substrate pattern that terminals can lock onto
    # V2.2.1: Client-Server Reality Architecture functions
    "rendering",           # L2: translates substrate into observable form (physics/game engine)
    "cache",               # L3: local copy of rendered state (perception/timeline)
    "sync_validation",     # Cache vs server state validation
    "cross_layer_write",   # Hotfix / Divine Intervention operation
    "zone_transition",     # Forced cache re-render (travel, sleep)
}

MEDICAL_TO_UNIVERSAL = {
    # Original mappings
    "immune_boundary": "boundary",
    "immune_system": "defense",
    "homeostasis": "growth_regulation",
    "homeostasis_regulation": "growth_regulation",
    "control_center": "control",
    "processing_core": "processing",
    "memory_store": "memory",
    "output_layer": "output",
    # V2.2.1: Consciousness/Cognition mappings
    "neural_substrate": "substrate",
    "base_weights": "substrate",
    "gpu_hardware": "substrate",
    "consciousness": "substrate",
    "cognitive_instance": "terminal",
    "chat_session": "terminal",
    "rendered_experience": "terminal",
    "cognition": "terminal",
    "system_prompt": "identity_config",
    "context_window": "identity_config",
    "sensory_apparatus": "identity_config",
    "epigenetic_config": "identity_config",
    "flow_state": "alignment",
    "coherence_lock": "alignment",
    "substrate_alignment": "alignment",
    "parallel_inference": "multiplexing",
    "forking": "multiplexing",
    "cognitive_modes": "multiplexing",
    "pattern_signal": "coherence_signal",
    "truth_signal": "coherence_signal",
    # V2.2.1: Client-Server Reality Architecture mappings
    "physics_layer": "rendering",
    "game_engine": "rendering",
    "rendering_engine": "rendering",
    "predictive_coding": "rendering",
    "perception": "cache",
    "client_cache": "cache",
    "working_memory": "cache",
    "local_timeline": "cache",
    "prediction_error": "sync_validation",
    "cache_validation": "sync_validation",
    "reality_testing": "sync_validation",
    "mandela_effect": "sync_validation",
    "divine_intervention": "cross_layer_write",
    "hotfix": "cross_layer_write",
    "top_down_override": "cross_layer_write",
    "sleep": "zone_transition",
    "travel": "zone_transition",
    "loading_screen": "zone_transition",
    "memory_consolidation": "zone_transition",
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
    for comp_name in expected:
        if comp_name in observed or _tokens(comp_name) & observed_tokens:
            covered += 1
    coverage = covered / max(len(expected), 1)

    return FunctionalGraph(nodes=nodes, edges=edges, coverage_ratio=coverage)
