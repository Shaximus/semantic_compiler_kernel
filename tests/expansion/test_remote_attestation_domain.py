"""Contract tests for remote_attestation (RFC 9334 RATS) domain template."""
from __future__ import annotations

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.pathology import detect_pathologies
from semantic_compiler.expansion.registry import get_template, list_domains


def test_remote_attestation_template_contract():
    assert "remote_attestation" in list_domains()
    template = get_template("remote_attestation")
    assert template.domain == "remote_attestation"
    assert template.version == 1.0
    assert len(template.components) >= 7
    assert len(template.invariants) >= 6
    assert len(template.failure_modes) >= 4
    assert len(template.architecture_patterns) >= 4

    comp_names = {c["name"] for c in template.components}
    assert {
        "hardware_root_of_trust",
        "attester",
        "endorser",
        "reference_value_provider",
        "verifier",
        "relying_party",
        "freshness_nonce_service",
    } <= comp_names

    for edge in template.relationships:
        assert edge["from"] in comp_names
        assert edge["to"] in comp_names
        assert len(edge["type"]) > 0

    comp_maps = {c.get("medical_map") for c in template.components if c.get("medical_map")}
    fm_maps = {f.get("medical_map") for f in template.failure_modes if f.get("medical_map")}
    assert comp_maps.isdisjoint(fm_maps)
    assert all(m in MEDICAL_ONTOLOGY for m in comp_maps)
    assert all(m in MEDICAL_ONTOLOGY for m in fm_maps)


def test_remote_attestation_routing_and_analogy():
    pkt = SemanticPacket(
        raw_input="RFC 9334 RATS remote attestation binds a freshness nonce into the attester quote before the relying party grants access."
    )
    assert _infer_domain(pkt) == "remote_attestation"
    model = decompress(pkt)
    assert model["domain"] == "remote_attestation"
    pathologies = detect_pathologies(model, get_template("remote_attestation"))
    assert isinstance(pathologies, list)

    analogy = SemanticPacket(
        raw_input="An attester freshness nonce challenge works like an immune memory verification handshake."
    )
    assert _infer_domain(analogy) == "remote_attestation"
