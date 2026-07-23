"""V2.2 Medical-Ontology System Decompression."""
from dataclasses import dataclass
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion.registry import get_template
from semantic_compiler.expansion.pathology import detect_pathologies
from semantic_compiler.expansion.isomorphism import build_functional_graph
from semantic_compiler.expansion.reconstruction import reconstruct_missing, assess_completeness
from semantic_compiler.expansion.advisor import generate_advice
from semantic_compiler.expansion.schema.v2_2_system_model import validate_system_model
from semantic_compiler.expansion.gem_decode import decode_build, GemDecodeResult

@dataclass(frozen=True)
class SystemModel:
    domain: str
    decompression_version: str
    components: list[dict]
    relationships: list[dict]
    universal_functional_graph: dict
    pathology_profile: dict
    reconstruction: dict
    advisor: dict

def decompress(packet: SemanticPacket) -> dict:
    """Decompress a SemanticPacket into a V2.2 system model."""
    # Infer domain from packet (simple heuristic; can be improved)
    domain = _infer_domain(packet)
    template = get_template(domain)

    # Build system model from packet skeleton/relationships
    components = _extract_components(packet, template)
    relationships = _extract_relationships(packet)

    # Build graph, detect pathologies, reconstruct, advise
    graph = build_functional_graph({"components": components, "relationships": relationships}, template)
    pathologies = detect_pathologies({"components": components, "relationships": relationships}, template)
    missing = reconstruct_missing({"components": components, "relationships": relationships}, template)
    completeness = assess_completeness({"components": components, "relationships": relationships}, template)
    advice = generate_advice({"components": components, "relationships": relationships}, pathologies, missing, failure_modes=template.failure_modes)

    model = {
        "domain": domain,
        "decompression_version": "2.2.0-rc1",
        "components": components,
        "relationships": relationships,
        "universal_functional_graph": {
            "nodes": list(graph.nodes),
            "edges": graph.edges,
            "coverage_ratio": graph.coverage_ratio,
        },
        "pathology_profile": {
            "detected_pathologies": [p.name for p in pathologies],
            "medical_diagnoses": [
                {
                    "pathology": p.name,
                    "medical_map": p.medical_map,
                    "evidence": p.evidence,
                    "confidence": p.confidence,
                } for p in pathologies
            ],
        },
        "reconstruction": {
            "missing_components": [
                {
                    "function": m.function,
                    "inferred_by": m.inferred_by,
                    "source_domain": m.source_domain,
                    "confidence": m.confidence,
                    "status": m.status,
                } for m in missing
            ],
            "completeness_scope": completeness,
        },
        "advisor": {
            "diagnosis": [s.description for s in advice["diagnosis"]],
            "prescriptions": [s.description for s in advice["prescriptions"]],
            "architecture_improvements": [s.description for s in advice["architecture_improvements"]],
            "resilience_training": [s.description for s in advice["resilience_training"]],
            "prognosis": advice["prognosis"],
        },
    }

    errors = validate_system_model(model)
    if errors:
        raise ValueError(f"Invalid system model: {errors}")
    return model

def _infer_domain(packet: SemanticPacket) -> str:
    """Simple domain inference from packet text."""
    # NOTE: frozen core SemanticPacket stores the input text in `raw_input`
    # (there is no `input_text` field); heuristic otherwise per brief.
    text = (packet.raw_input or "").lower()
    if any(k in text for k in ["firewall", "network", "server", "api", "database"]):
        return "computation"
    if any(k in text for k in ["cell", "organism", "immune", "metabolism"]):
        return "biology"
    return "universal_generic"

def _extract_components(packet: SemanticPacket, template) -> list[dict]:
    """Extract components from packet skeleton."""
    components = []
    for comp in template.components:
        components.append({
            "name": comp["name"],
            "function": comp["function"],
            "medical_map": _infer_medical_map(comp["name"]),
            "status": "inferred_by_analogy",
            "confidence": 0.6,
        })
    return components

def _extract_relationships(packet: SemanticPacket) -> list[dict]:
    """Extract relationships from packet."""
    return []

def _infer_medical_map(component_name: str) -> str:
    """Infer medical ontology mapping for a component."""
    mapping = {
        "input_layer": "immune_boundary",
        "processing_core": "processing_core",
        "memory_store": "memory_store",
        "defense_boundary": "immune_system",
        "output_layer": "output_layer",
        "cell_membrane": "immune_boundary",
        "metabolism": "homeostasis_regulation",
        "immune_system": "immune_system",
        "genetic_code": "memory_store",
        "homeostasis_regulation": "homeostasis_regulation",
    }
    return mapping.get(component_name, "unknown")
