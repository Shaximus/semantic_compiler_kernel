"""Contract tests for sourced deep-system domain templates."""
from __future__ import annotations

import re
from pathlib import Path

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _DOMAIN_PATTERNS, _infer_domain
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.registry import get_template, list_domains, load_templates

NEW_DOMAINS = ("mobile_security", "networking", "trust_chain")
DOC = Path(__file__).resolve().parents[2] / "docs" / "DEEP_SYSTEM_INVARIANTS.md"
TAG = re.compile(r"\[([A-Z0-9-]+)\]")
TRAILING_TAGS = re.compile(r"(?:\[[A-Z0-9-]+\])+$")


def packet(text: str) -> SemanticPacket:
    return SemanticPacket(raw_input=text)


def test_new_domains_are_registered_and_valid():
    assert set(NEW_DOMAINS) <= set(list_domains())
    for domain in NEW_DOMAINS:
        template = get_template(domain)
        assert len(template.components) >= 8
        assert len(template.invariants) >= 8
        assert len(template.failure_modes) >= 5
        assert len(template.architecture_patterns) >= 4


def test_every_invariant_has_a_defined_source_tag():
    doc_text = DOC.read_text()
    for domain in NEW_DOMAINS:
        for invariant in get_template(domain).invariants:
            assert TRAILING_TAGS.search(invariant), (domain, invariant)
            for tag in TAG.findall(invariant):
                row = next((line for line in doc_text.splitlines() if line.startswith(f"| `{tag}` |")), None)
                assert row is not None, (domain, tag)
                assert "http" in row


def test_template_relationship_endpoints_exist():
    for domain in NEW_DOMAINS:
        template = get_template(domain)
        names = {c["name"] for c in template.components}
        for edge in template.relationships:
            assert edge["from"] in names, (domain, edge)
            assert edge["to"] in names, (domain, edge)


def test_component_and_failure_medical_maps_are_disjoint():
    for domain in NEW_DOMAINS:
        template = get_template(domain)
        component_maps = {c.get("medical_map") for c in template.components}
        failure_maps = {f.get("medical_map") for f in template.failure_modes}
        assert component_maps.isdisjoint(failure_maps), domain
        assert all(m in MEDICAL_ONTOLOGY for m in component_maps if m)
        assert all(m in MEDICAL_ONTOLOGY for m in failure_maps if m)


def test_android_domain_precedence_and_specificity():
    assert _infer_domain(packet("The Android bootloader verifies vbmeta.")) == "mobile_security"
    assert _infer_domain(packet("SELinux confines a root process.")) == "mobile_security"
    assert _infer_domain(packet("A resolver validates DNSSEC signatures.")) == "networking"
    assert _infer_domain(packet("A hardware root of trust anchors attestation.")) == "trust_chain"
    assert _infer_domain(packet("An Android server handles API requests.")) == "mobile_security"


def test_new_vocabulary_does_not_capture_unrelated_words():
    assert _infer_domain(packet("The dnsmasq and tcpdump utilities are installed.")) == "universal_generic"
    assert _infer_domain(packet("The observer checks a server response.")) == "computation"
    assert _infer_domain(packet("A patient has a heartbeat.")) == "medical"


def test_old_domain_patterns_remain_ordered_after_specific_domains():
    names = [name for name, _ in _DOMAIN_PATTERNS]
    assert names[:3] == list(NEW_DOMAINS)
    assert names[3:6] == ["computation", "biology", "medical"]


def test_mobile_security_has_explicit_scope_and_optional_controls():
    template = get_template("mobile_security")
    invariant_text = " ".join(template.invariants).lower()
    assert "device-specific" in template.description.lower()
    assert "optional" in template.description.lower()
    assert "security level" in invariant_text
    assert "file-based encryption" in invariant_text
    assert "mte" in invariant_text
    assert "pkvm" in invariant_text
    assert "exponential backoff" in invariant_text
