"""Tests for Numerology and Astrology domain templates and V3.5.0 compilation."""
import dataclasses
import json
from pathlib import Path
import pytest

from semantic_compiler.core.dataset import validate_dataset_row
from semantic_compiler.core.pipeline import build_dataset_row, compile_semantic_packet
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.registry import get_template, list_domains
from semantic_compiler.expansion.schema import validate_domain_template


def test_numerology_and_astrology_in_registry():
    domains = set(list_domains())
    assert "numerology" in domains
    assert "astrology" in domains


def test_templates_schema_validation():
    for domain_name in ["numerology", "astrology"]:
        tmpl = get_template(domain_name)
        assert tmpl is not None
        assert tmpl.domain == domain_name
        assert tmpl.version >= 1.0
        assert len(tmpl.components) >= 5
        assert len(tmpl.relationships) >= 5
        assert len(tmpl.invariants) >= 5
        assert len(tmpl.failure_modes) >= 3
        assert len(tmpl.architecture_patterns) >= 3

        # Validate with jsonschema
        errs = validate_domain_template(dataclasses.asdict(tmpl))
        assert not errs, f"Validation errors in {domain_name}: {errs}"


def test_domain_routing():
    num_packet = SemanticPacket(raw_input="Calculating the life path number using Pythagorean reduction and master numbers.")
    assert _infer_domain(num_packet) == "numerology"

    astro_packet = SemanticPacket(raw_input="Analyzing natal chart aspects including grand trine and grand cross configurations.")
    assert _infer_domain(astro_packet) == "astrology"


def test_decompression_system_model():
    packet = SemanticPacket(raw_input="A numerology blueprint with life path number, expression number, and karmic debt.")
    model = decompress(packet)
    assert model["domain"] == "numerology"
    assert len(model["components"]) >= 5

    packet_astro = SemanticPacket(raw_input="A natal chart with sun sign, moon sign, ascendant, and grand trine.")
    model_astro = decompress(packet_astro)
    assert model_astro["domain"] == "astrology"
    assert len(model_astro["components"]) >= 5


def test_v3_5_0_dataset_compilation_and_validation():
    guide_excerpt = (
        "All multi-digit numbers reduce to a single digit by summing their digits, "
        "EXCEPT master numbers 11, 22, 33, and 44. Karmic debt numbers 13, 14, 16, "
        "and 19 carry specific developmental obligations."
    )
    packet = compile_semantic_packet(guide_excerpt)
    row = build_dataset_row(packet)
    assert row["schema_version"] == "3.5.0"
    validation = validate_dataset_row(row)
    assert validation["valid"] is True, f"Validation errors: {validation['errors']}"
