"""V2.2 Medical-Ontology System Decompression."""
import re
from dataclasses import dataclass
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.registry import get_template
from semantic_compiler.expansion.pathology import detect_pathologies
from semantic_compiler.expansion.isomorphism import build_functional_graph
from semantic_compiler.expansion.reconstruction import reconstruct_missing, assess_completeness
from semantic_compiler.expansion.advisor import generate_advice
from semantic_compiler.expansion.schema.v2_2_system_model import validate_system_model
from semantic_compiler.expansion.gem_decode import decode_build, GemDecodeResult
from semantic_compiler.expansion.gem_forge import (
    ForgeResult,
    GemTranslation,
    PoeGem,
    SoftwareComponent,
    forge_component,
    load_gem_corpus,
    load_gem_corpus_file,
    translate_corpus,
    translate_gem,
)

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
    domain = _infer_domain(packet)
    template = get_template(domain)

    components = _extract_components(packet, template)
    relationships = _extract_relationships(packet)

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
            "detected": [p.to_dict() for p in pathologies],
            "severity": max((p.severity for p in pathologies), default=0),
        },
        "reconstruction": {
            "missing_components": missing,
            "completeness": completeness,
        },
        "advisor": advice,
    }
    validate_system_model(model)
    return model

# ... remaining helper functions and __all__ as in the package
# (full content synced from the v3.1.0 tar)

__all__ = [
    "SystemModel",
    "decompress",
    "decode_build",
    "GemDecodeResult",
    "PoeGem",
    "SoftwareComponent",
    "GemTranslation",
    "ForgeResult",
    "load_gem_corpus",
    "load_gem_corpus_file",
    "translate_gem",
    "translate_corpus",
    "forge_component",
]
