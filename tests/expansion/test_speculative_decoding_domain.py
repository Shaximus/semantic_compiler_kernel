"""Tests for the speculative_decoding domain template and routing."""
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.registry import get_template, list_domains


def test_speculative_decoding_template_registered_and_valid():
    assert "speculative_decoding" in list_domains()
    tmpl = get_template("speculative_decoding")
    assert tmpl.domain == "speculative_decoding"
    assert tmpl.version == 1.0

    comp_names = {c["name"] for c in tmpl.components}
    assert {
        "draft_model",
        "target_model",
        "rejection_sampler",
        "tree_attention_verifier",
        "kv_cache_rollback_manager",
    } <= comp_names

    comp_maps = {c.get("medical_map") for c in tmpl.components}
    fm_maps = {f.get("medical_map") for f in tmpl.failure_modes}
    assert comp_maps.isdisjoint(fm_maps)
    assert all(m in MEDICAL_ONTOLOGY for m in comp_maps if m)
    assert all(m in MEDICAL_ONTOLOGY for m in fm_maps if m)

    inv_text = " ".join(tmpl.invariants)
    assert "CONSCIOUSNESS_COGNITION_LINK" in inv_text
    assert "CLIENT_SERVER_LINK" in inv_text


def test_speculative_decoding_routing_and_decompression():
    pkt = SemanticPacket(
        raw_input=(
            "Speculative decoding runs a draft model and target model with "
            "rejection sampling, tree attention verification, and KV cache rollback."
        )
    )
    assert _infer_domain(pkt) == "speculative_decoding"
    model = decompress(pkt)
    assert model["domain"] == "speculative_decoding"
    comp_names = {c["name"] for c in model["components"]}
    assert "target_model" in comp_names
    assert "rejection_sampler" in comp_names
