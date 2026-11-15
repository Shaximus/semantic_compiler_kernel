"""Contract tests for kv_cache_inference and distributed_consensus domain templates."""
from __future__ import annotations

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.pathology import detect_pathologies
from semantic_compiler.expansion.registry import get_template, list_domains


def _check_domain_contract(domain: str, expected_components: set[str]) -> None:
    assert domain in list_domains()
    template = get_template(domain)
    assert template.domain == domain
    assert template.version == 1.0
    assert len(template.components) >= 6
    assert len(template.invariants) >= 5
    assert len(template.failure_modes) >= 4
    assert len(template.architecture_patterns) >= 4

    comp_names = {c["name"] for c in template.components}
    assert expected_components <= comp_names

    for edge in template.relationships:
        assert edge["from"] in comp_names, edge
        assert edge["to"] in comp_names, edge
        assert len(edge["type"]) > 0

    comp_maps = {c.get("medical_map") for c in template.components if c.get("medical_map")}
    fm_maps = {f.get("medical_map") for f in template.failure_modes if f.get("medical_map")}
    assert comp_maps.isdisjoint(fm_maps)
    assert all(m in MEDICAL_ONTOLOGY for m in comp_maps)
    assert all(m in MEDICAL_ONTOLOGY for m in fm_maps)


def test_kv_cache_inference_contract():
    _check_domain_contract(
        "kv_cache_inference",
        {
            "request_scheduler",
            "radix_prefix_tree",
            "logical_kv_table",
            "physical_block_pool",
            "prefill_engine",
            "decode_engine",
        },
    )


def test_distributed_consensus_contract():
    _check_domain_contract(
        "distributed_consensus",
        {
            "term_epoch_clock",
            "consensus_leader",
            "quorum_voters",
            "replicated_log",
            "fencing_token_issuer",
            "state_machine",
        },
    )


def test_new_domains_route_and_decompress():
    kv_pkt = SemanticPacket(
        raw_input="PagedAttention and RadixAttention share KV cache block tables during continuous batching prefill."
    )
    assert _infer_domain(kv_pkt) == "kv_cache_inference"
    kv_model = decompress(kv_pkt)
    assert kv_model["domain"] == "kv_cache_inference"

    cons_pkt = SemanticPacket(
        raw_input="A Raft cluster uses majority quorum intersection and monotonic fencing tokens to prevent split-brain writes."
    )
    assert _infer_domain(cons_pkt) == "distributed_consensus"
    cons_model = decompress(cons_pkt)
    assert cons_model["domain"] == "distributed_consensus"

    template = get_template("distributed_consensus")
    pathologies = detect_pathologies(cons_model, template)
    assert isinstance(pathologies, list)


def test_analogy_preserves_new_domain_subject():
    analogy = SemanticPacket(
        raw_input="RadixAttention prefix caching works like an immune vaccination memory against repeated prefill compute."
    )
    assert _infer_domain(analogy) == "kv_cache_inference"
