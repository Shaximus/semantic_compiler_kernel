import pytest

from semantic_compiler.expansion.build_optimizer import EvidenceStatus
from semantic_compiler.expansion.party_value_optimizer import (
    AuraCategory,
    PartyConstraints,
    PartyLoadoutCandidate,
    PartyRole,
    PartyUpgradeCandidate,
    best_aura_by_category,
    best_party_upgrade,
    evaluate_party_upgrade,
    greatest_party_throughput_per_cad,
    rank_party_loadouts,
)


def _candidate(**overrides):
    values = dict(
        name="lifeboat-aura",
        workload_id="offline-agent-swarm-v1",
        baseline_party_id="ark-plus-lifeboat-current",
        node_role=PartyRole.AURABOT,
        aura_categories=(AuraCategory.MEMORY,),
        landed_cost_cad=1000,
        direct_tps_gain=10,
        carry_tps_reclaimed=20,
        concurrency_gain_tps_equivalent=5,
        stall_tps_recovered=5,
        available_link_gib_per_s=1.0,
        baseline_quality_score=0.9,
        candidate_quality_score=0.9,
        evidence=EvidenceStatus.MEASURED,
    )
    values.update(overrides)
    return PartyUpgradeCandidate(**values)


def test_party_gain_includes_aura_and_carry_reclamation():
    result = evaluate_party_upgrade(_candidate())
    assert result.gross_party_gain_tps == 40
    assert result.net_party_gain_tps == 40
    assert result.raw_party_tps_per_cad == pytest.approx(0.04)


def test_link_sync_and_integration_penalties_are_charged():
    result = evaluate_party_upgrade(
        _candidate(link_penalty_tps=3, synchronization_penalty_tps=2, integration_penalty_tps=5)
    )
    assert result.total_penalty_tps == 10
    assert result.net_party_gain_tps == 30


def test_link_capacity_violation_blocks_remote_memory_fiction():
    result = evaluate_party_upgrade(
        _candidate(required_link_gib_per_s=8, available_link_gib_per_s=1.25)
    )
    assert not result.feasible
    assert {v.code for v in result.violations} == {"LINK_CAPACITY_EXCEEDED"}


def test_offline_emergency_mode_rejects_cloud_dependency():
    result = evaluate_party_upgrade(
        _candidate(required_internet=True),
        PartyConstraints(require_offline_capability=True),
    )
    assert not result.feasible
    assert {v.code for v in result.violations} == {"INTERNET_DEPENDENCY"}


def test_best_party_upgrade_can_be_support_node_not_direct_dps():
    direct_gpu = _candidate(
        name="solo-gpu",
        node_role=PartyRole.HYBRID,
        aura_categories=(AuraCategory.DRAFTING,),
        landed_cost_cad=2500,
        direct_tps_gain=80,
        carry_tps_reclaimed=0,
        concurrency_gain_tps_equivalent=0,
        stall_tps_recovered=0,
    )
    aurabot = _candidate(
        name="memory-storage-network-aura",
        aura_categories=(AuraCategory.MEMORY, AuraCategory.STORAGE, AuraCategory.NETWORK),
        landed_cost_cad=1200,
        direct_tps_gain=5,
        carry_tps_reclaimed=35,
        concurrency_gain_tps_equivalent=20,
        stall_tps_recovered=10,
    )
    winner = best_party_upgrade([direct_gpu, aurabot])
    assert winner is not None
    assert winner.candidate.name == "memory-storage-network-aura"


def test_best_aura_by_category_returns_shared_compound_winner():
    compound = _candidate(
        name="compound-aura",
        aura_categories=(AuraCategory.MEMORY, AuraCategory.STORAGE),
        landed_cost_cad=500,
    )
    weaker = _candidate(
        name="weaker-storage",
        aura_categories=(AuraCategory.STORAGE,),
        landed_cost_cad=2000,
    )
    winners = best_aura_by_category([weaker, compound])
    assert winners[AuraCategory.MEMORY].candidate.name == "compound-aura"
    assert winners[AuraCategory.STORAGE].candidate.name == "compound-aura"


def test_party_upgrades_require_same_baseline():
    with pytest.raises(ValueError, match="shared workload_id and baseline_party_id"):
        best_party_upgrade([_candidate(), _candidate(baseline_party_id="other-party")])


def test_complete_party_loadouts_use_end_to_end_measurements():
    ark_only = PartyLoadoutCandidate(
        name="ark-only",
        workload_id="offline-agent-swarm-v1",
        nodes={"ark": PartyRole.CARRY},
        links={},
        total_landed_cost_cad=10000,
        accepted_tokens_per_s=100,
        quality_score=0.9,
        evidence=EvidenceStatus.MEASURED,
    )
    linked_party = PartyLoadoutCandidate(
        name="linked-party",
        workload_id="offline-agent-swarm-v1",
        nodes={"ark": PartyRole.CARRY, "lifeboat": PartyRole.AURABOT},
        links={"ark-lifeboat": "25GbE"},
        total_landed_cost_cad=12000,
        accepted_tokens_per_s=150,
        quality_score=0.9,
        evidence=EvidenceStatus.MEASURED,
    )
    winner = greatest_party_throughput_per_cad([ark_only, linked_party])
    assert winner is not None
    assert winner.candidate.name == "linked-party"


def test_party_loadouts_reject_mixed_workloads():
    first = PartyLoadoutCandidate(
        name="first",
        workload_id="chat",
        nodes={},
        links={},
        total_landed_cost_cad=1000,
        accepted_tokens_per_s=100,
        quality_score=0.9,
    )
    second = PartyLoadoutCandidate(
        name="second",
        workload_id="embedding",
        nodes={},
        links={},
        total_landed_cost_cad=1000,
        accepted_tokens_per_s=100,
        quality_score=0.9,
    )
    with pytest.raises(ValueError, match="shared workload_id"):
        rank_party_loadouts([first, second])
