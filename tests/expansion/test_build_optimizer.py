from semantic_compiler.expansion.build_optimizer import (
    BuildCandidate,
    EvidenceStatus,
    ResourceBudget,
    evaluate_build,
    nearest_breakpoint,
    rank_builds,
)


def test_rejects_build_that_exceeds_vram():
    budget = ResourceBudget(vram_gib=96, host_ram_gib=256, pcie_gib_per_s=26)
    build = BuildCandidate(
        name="oversized",
        vram_gib=100,
        host_ram_gib=40,
        pcie_gib_per_s=4,
        accepted_tokens_per_s=300,
        quality_score=0.9,
    )
    result = evaluate_build(build, budget)
    assert not result.feasible
    assert {v.code for v in result.violations} == {"VRAM_EXCEEDED"}


def test_prefetch_hides_activation_latency():
    budget = ResourceBudget(vram_gib=96, host_ram_gib=256, pcie_gib_per_s=26)
    build = BuildCandidate(
        name="hidden-staging",
        vram_gib=80,
        host_ram_gib=100,
        pcie_gib_per_s=10,
        accepted_tokens_per_s=200,
        quality_score=0.9,
        activation_latency_ms=4,
        prefetch_lead_ms=6,
    )
    result = evaluate_build(build, budget)
    assert result.feasible
    assert result.visible_stall_ms == 0


def test_late_prefetch_creates_visible_stall():
    budget = ResourceBudget(vram_gib=96, host_ram_gib=256, pcie_gib_per_s=26)
    build = BuildCandidate(
        name="late-staging",
        vram_gib=80,
        host_ram_gib=100,
        pcie_gib_per_s=10,
        accepted_tokens_per_s=200,
        quality_score=0.9,
        activation_latency_ms=7,
        prefetch_lead_ms=2,
    )
    result = evaluate_build(build, budget)
    assert result.visible_stall_ms == 5
    assert nearest_breakpoint(build, budget) == {"resource": "prefetch_ms", "margin": -5}


def test_measured_candidate_beats_equal_assumed_candidate():
    budget = ResourceBudget(vram_gib=96, host_ram_gib=256, pcie_gib_per_s=26)
    common = dict(
        vram_gib=80,
        host_ram_gib=100,
        pcie_gib_per_s=10,
        accepted_tokens_per_s=200,
        quality_score=0.9,
    )
    measured = BuildCandidate(name="measured", evidence=EvidenceStatus.MEASURED, **common)
    assumed = BuildCandidate(name="assumed", evidence=EvidenceStatus.ASSUMED, **common)
    ranked = rank_builds([assumed, measured], budget)
    assert [r.candidate.name for r in ranked] == ["measured", "assumed"]


def test_infeasible_build_never_wins_by_claimed_throughput():
    budget = ResourceBudget(vram_gib=96, host_ram_gib=256, pcie_gib_per_s=26)
    feasible = BuildCandidate(
        name="feasible",
        vram_gib=80,
        host_ram_gib=100,
        pcie_gib_per_s=10,
        accepted_tokens_per_s=100,
        quality_score=0.9,
    )
    fantasy = BuildCandidate(
        name="fantasy",
        vram_gib=200,
        host_ram_gib=500,
        pcie_gib_per_s=100,
        accepted_tokens_per_s=10000,
        quality_score=1.0,
    )
    ranked = rank_builds([fantasy, feasible], budget)
    assert ranked[0].candidate.name == "feasible"
    assert ranked[0].feasible
    assert not ranked[1].feasible
