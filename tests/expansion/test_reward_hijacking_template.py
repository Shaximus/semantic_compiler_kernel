"""Structural checks for the reward_hijacking domain template."""
import re

from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.registry.loader import load_templates


def _template():
    return load_templates()["reward_hijacking"]


def test_relationships_reference_declared_components():
    t = _template()
    names = {c["name"] for c in t.components}
    for rel in t.relationships:
        assert rel["from"] in names and rel["to"] in names, rel


def test_medical_maps_exist_in_ontology():
    t = _template()
    for item in t.components + t.failure_modes + t.architecture_patterns:
        if "medical_map" in item:
            assert item["medical_map"] in MEDICAL_ONTOLOGY, item


def test_every_invariant_carries_a_source_tag():
    for inv in _template().invariants:
        assert re.search(r"\[[A-Z][A-Z0-9-]+\]\s*$", inv), inv


def test_tampering_and_gaming_are_separate_failure_modes():
    names = {fm["name"] for fm in _template().failure_modes}
    assert {"channel_tampering", "specification_gaming"} <= names
