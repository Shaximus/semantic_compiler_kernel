"""Contract tests for cellular_middlebox_tethering domain template."""
from __future__ import annotations

import pytest

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.pathology import detect_pathologies
from semantic_compiler.expansion.registry import get_template, list_domains

DOMAIN = "cellular_middlebox_tethering"


def packet(text: str) -> SemanticPacket:
    return SemanticPacket(raw_input=text)


def test_cellular_middlebox_template_is_registered():
    assert DOMAIN in list_domains()
    template = get_template(DOMAIN)
    assert template.domain == DOMAIN
    assert template.version == 1.0
    assert len(template.components) >= 8
    assert len(template.invariants) >= 8
    assert len(template.failure_modes) >= 5
    assert len(template.architecture_patterns) >= 4


def test_cellular_middlebox_components_and_criticalities():
    template = get_template(DOMAIN)
    comp_names = {c["name"] for c in template.components}
    expected = {
        "cellular_uplink",
        "downstream_tether",
        "sgi_l4_steering",
        "transparent_proxy_cluster",
        "quic_transport_path",
        "carrier_resolver_detour",
        "host_firewall_clamp",
        "stack_fingerprint_verifier",
    }
    assert expected <= comp_names
    for comp in template.components:
        assert comp["criticality"] in {"high", "medium", "low"}
        assert len(comp["function"]) > 10


def test_cellular_middlebox_relationships_endpoints_exist():
    template = get_template(DOMAIN)
    names = {c["name"] for c in template.components}
    for edge in template.relationships:
        assert edge["from"] in names, edge
        assert edge["to"] in names, edge
        assert len(edge["type"]) > 0


def test_cellular_middlebox_medical_maps_disjoint():
    template = get_template(DOMAIN)
    component_maps = {c.get("medical_map") for c in template.components}
    failure_maps = {f.get("medical_map") for f in template.failure_modes}
    assert component_maps.isdisjoint(failure_maps)
    assert all(m in MEDICAL_ONTOLOGY for m in component_maps if m)
    assert all(m in MEDICAL_ONTOLOGY for m in failure_maps if m)


def test_cellular_middlebox_invariants_and_failure_modes():
    template = get_template(DOMAIN)
    inv_text = " ".join(template.invariants)
    assert "Cisco Nexus PBR" in inv_text
    assert "TTL 64 vs 128" in inv_text
    assert "TCP MSS to 1360 bytes" in inv_text
    assert "ICMP port-unreachable rejection" in inv_text
    assert "OONI" in inv_text

    fm_names = {fm["name"] for fm in template.failure_modes}
    expected_fms = {
        "quic_path_mtu_blackhole",
        "l4_middlebox_tcp_hijack",
        "transcontinental_dns_latency",
        "tcp_segmentation_fragmentation_stall",
        "middlebox_evasion_failure",
    }
    assert expected_fms <= fm_names


@pytest.mark.parametrize(
    "text, expected_domain",
    [
        (
            "A cellular middlebox intercepts cleartext traffic entering the carrier packet core.",
            DOMAIN,
        ),
        (
            "The SGi interface applies policy-based routing steering on port 80.",
            DOMAIN,
        ),
        (
            "Hotspot slowdown occurs when clients experience a quic blackhole.",
            DOMAIN,
        ),
        (
            "Host firewall installs an mss clamp to prevent cellular MTU fragmentation.",
            DOMAIN,
        ),
        (
            "OONI measurement confirmed middlebox tampering across five test vectors.",
            DOMAIN,
        ),
    ],
)
def test_cellular_middlebox_vocabulary_routing(text, expected_domain):
    assert _infer_domain(packet(text)) == expected_domain


def test_cellular_middlebox_pathology_detection():
    template = get_template(DOMAIN)
    system_model = {
        "components": [
            {"name": "downstream_tether", "medical_map": "homeostasis"},
            {"name": "quic_packet_loss", "medical_map": "acute"},
            {"name": "browser_initial_stall", "medical_map": "acute"},
        ],
        "relationships": [],
    }
    pathologies = detect_pathologies(system_model, template)
    detected_names = {p.name for p in pathologies}
    assert "quic_path_mtu_blackhole" in detected_names


def test_cellular_middlebox_decompression_end_to_end():
    text = (
        "A cellular hotspot system with cellular uplink, downstream tether, "
        "SGi-LAN Layer 4 steering, transparent proxy cluster, host firewall clamp, "
        "and stack fingerprint verification maintaining throughput."
    )
    result = decompress(packet(text))
    assert result["domain"] == DOMAIN
    assert len(result["components"]) > 0
    assert "universal_functional_graph" in result
    assert "pathology_profile" in result
    assert "advisor" in result
    assert "prognosis" in result["advisor"]
