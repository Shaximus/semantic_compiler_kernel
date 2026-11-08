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

# Specific domains precede broad ones so Android and protocol vocabulary
# cannot be swallowed by the generic computation router.
_DOMAIN_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    # HID / controller translation. Its phrases are narrower than "android" or
    # "bluetooth", so it routes first.
    ("input_semantic_adapter", (
        "hid usage", "usage page", "consumer control", "usb keyboard",
        "composite usb gadget", "controller layout", "input adapter", "gamepad",
    )),
    # Named chain-of-trust phrases outrank the Android vocabulary they often
    # mention (bootloader). "remote attestation" stays Android-side.
    ("trust_chain", (
        "chain of trust", "root of trust", "trust anchor",
        "key attestation", "certificate chain", "verified delegation",
        "signing service", "key rollover", "verifies the signature",
    )),
    ("mobile_security", (
        "android", "knox", "trustzone", "bootloader", "selinux", "keystore",
        "keymint", "verified boot", "secure boot", "secure world", "strongbox",
        "gatekeeper", "weaver", "dm-verity", "vbmeta", "pKVM", "mte",
    )),
    # Handset companions. "android" stays on mobile_security; these phrases
    # are the connectivity and radio terms that do not belong there.
    ("android_connectivity", (
        "apn", "tethering", "rndis",
    )),
    ("bluetooth", (
        "bluetooth", "ble", "gatt", "a2dp",
    )),
    ("networking", (
        "bgp", "dns", "dnssec", "rpki", "tcp", "udp", "autonomous system",
        "route origin authorization", "route authorization", "validating resolver",
        "unauthorized origin", "prefix hijack",
    )),
    # Narrow on purpose: bare "path of exile" is not a keyword. Buildcraft and
    # gem-decode use PoE shorthand for computation builds.
    ("poe_chaos_inoculation", (
        "chaos inoculation", "energy shield", "eldritch battery", "ghost reaver",
    )),
    # Wireless power transfer. Phrases only: bare "tesla" (a car company) and
    # bare "charging" or "wireless" are not keywords.
    ("wireless_power", (
        "wireless power", "wireless charging", "wireless charger", "inductive charging",
        "inductive coupling", "resonant coupling", "magnetic resonance",
        "rotating magnetic field", "tesla coil", "rectenna", "wardenclyffe",
        "coupling coefficient", "resonator", "coil pair",
    )),
    # Reinforcement and reward-hijacking vocabulary. Phrases only: bare
    # "reward" or "addiction" are too broad to route on.
    ("reward_hijacking", (
        "reward hacking", "reward hijacking", "reward channel", "reward signal",
        "reward model", "reward function", "prediction error", "specification gaming",
        "wireheading", "reward tampering", "incentive salience", "reinforcement learning",
        "rlhf", "reference policy", "dopamine",
    )),
    # Domains below previously had no router vocabulary and were reachable only
    # by explicit name. Phrases are the domain's own vocabulary; order resolves
    # overlaps (specific settlement and quota terms before generic banking,
    # ecology before environmental, social before military).
    ("quota_bypass_mechanics", (
        "online charging system", "ocs", "imsi", "esim", "sim switch", "quota",
        "data allowance", "credit control", "upf",
    )),
    ("epistemic_ledger_verification", (
        "ledger", "bank statement", "settlement", "dpan", "card token",
        "credit card token", "gift card", "app store",
    )),
    ("finance_economics", (
        "central bank", "commercial bank", "bank", "capital market", "regulator",
        "stress test", "leverage", "asset bubble", "bubble", "deposit", "treasury",
    )),
    ("economic", (
        "economy", "inflation", "labor market", "supply chain", "trade balance",
        "fiscal policy", "hedge fund", "pricing", "currency", "recession",
    )),
    ("psychology", (
        "mind", "remember", "trauma", "therapy", "threat detector", "anxiety",
        "defense mechanism", "cognition", "emotion",
    )),
    ("reflexion", (
        "reflexion", "self-checking", "self-check", "checks its own", "its own output",
        "its own suggestion", "review pipeline", "audit stage", "external evaluation",
        "self-correction",
    )),
    ("informational", (
        "knowledge platform", "information ecosystem", "indexing", "ingestion", "ingest",
        "document archive", "records platform", "recommendation feedback", "retrieval",
        "misinformation",
    )),
    ("corporate", (
        "corporate", "corporation", "executive board", "board of directors", "payroll",
        "legal department", "ownership structure", "family business", "shareholder",
    )),
    ("organizational", (
        "middle management", "reporting line", "coordination meeting", "weekly meeting",
        "open-source project", "maintainer", "org chart", "feedback channel",
    )),
    ("government", (
        "government", "legislature", "ministry", "bureaucracy", "agency", "permitting",
        "constitutional", "election", "public service",
    )),
    ("law", (
        "court", "legal system", "precedent", "contract", "legal review", "jurisdiction",
        "litigation", "appeal",
    )),
    ("social", (
        "neighborhood", "neighbor", "community", "group chat", "friends", "social norm",
    )),
    ("military", (
        "military", "radar", "command structure", "logistics command", "coast guard",
        "navy", "perimeter", "patrol", "intelligence warning",
    )),
    ("construction", (
        "building", "foundation", "load-bearing", "crane", "beam", "hvac", "plumbing",
        "floor plan", "structural reinforcement", "built structure",
    )),
    ("ecology", (
        "ecosystem", "food web", "invasive species", "predator", "herbivore",
        "mycorrhizal", "endangered species", "pond", "algal", "algae",
    )),
    ("environmental", (
        "watershed", "groundwater", "eutrophication", "runoff", "wetland", "storm surge",
        "climate change", "water utility", "dead zone", "sediment",
    )),
    ("evolutionary", (
        "evolution", "natural selection", "selection pressure", "genetic drift", "gene flow",
        "speciation", "inbreeding", "niche", "selective breeding", "selective-breeding",
    )),
    ("computation", ("firewall", "network", "server", "api", "database", "monolith", "garbage collector", "software")),
    ("medical", (
        "patient", "hospital", "clinical", "clinician", "clinic", "surgery",
        "surgeon", "diagnosis", "diagnosed", "prognosis", "triage", "nurse",
        "physician", "doctor", "symptom", "sepsis", "autoimmune",
    )),
    ("biology", ("cell", "organism", "immune", "immunity", "immunology", "metabolism", "mitochondria", "atp", "microbiome", "synthetic biology", "virus", "genome")),
)


def _keyword_pattern(keywords: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile(
        r"(?<![a-z])(?:" + "|".join(map(re.escape, keywords)) + r")(?:s|es)?(?![a-z])",
        re.IGNORECASE,
    )


_DOMAIN_PATTERNS = tuple((domain, _keyword_pattern(words)) for domain, words in _DOMAIN_KEYWORDS)


# "X is like Y", "X works like Y", "X acts as Y": X is the system being
# described; Y is the analogy source. Route on X first.
_ANALOGY_MARKER = re.compile(r"\b(?:like|acts as|act as|as if)\b", re.IGNORECASE)


def _route_text(text: str) -> str:
    for domain, pattern in _DOMAIN_PATTERNS:
        if pattern.search(text):
            return domain
    return "universal_generic"


def _infer_domain(packet: SemanticPacket) -> str:
    """Infer a domain using ordered, whole-word vocabulary matching.

    For analogies the subject clause (before the marker) decides the domain;
    the full text is used only when the subject carries no domain vocabulary.
    """
    text = packet.raw_input or ""
    marker = _ANALOGY_MARKER.search(text)
    if marker:
        subject_domain = _route_text(text[:marker.start()])
        if subject_domain != "universal_generic":
            return subject_domain
    return _route_text(text)

def _extract_components(packet: SemanticPacket, template) -> list[dict]:
    """Extract components, honoring only canonical template medical concepts."""
    components = []
    for comp in template.components:
        declared = comp.get("medical_map")
        medical_map = declared if declared in MEDICAL_ONTOLOGY else _infer_medical_map(comp["name"])
        components.append({
            "name": comp["name"],
            "function": comp["function"],
            "medical_map": medical_map,
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
    if component_name in mapping:
        return mapping[component_name]
    if component_name in MEDICAL_ONTOLOGY:
        return component_name
    return "unknown"


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
