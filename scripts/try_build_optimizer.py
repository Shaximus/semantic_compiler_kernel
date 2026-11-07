"""Run a bounded demonstration of the build optimizer.

Values are illustrative inputs, not benchmark claims. Replace them with receipts
from the local model inventory and benchmark harness before operational use.
"""

from semantic_compiler.expansion.build_optimizer import (
    BuildCandidate,
    EvidenceStatus,
    ResourceBudget,
    rank_builds,
)


budget = ResourceBudget(
    vram_gib=96.0,
    host_ram_gib=256.0,
    pcie_gib_per_s=26.0,
)

candidates = [
    BuildCandidate(
        name="Qwen 27B MTP K5 — measured baseline fixture",
        vram_gib=82.0,
        host_ram_gib=48.0,
        pcie_gib_per_s=2.0,
        accepted_tokens_per_s=90.0,
        quality_score=0.86,
        availability=0.98,
        p95_latency_ms=120.0,
        evidence=EvidenceStatus.MEASURED,
    ),
    BuildCandidate(
        name="MiniMax M2.5 BCC + precognition — projected fixture",
        vram_gib=91.0,
        host_ram_gib=180.0,
        pcie_gib_per_s=18.0,
        accepted_tokens_per_s=319.0,
        quality_score=0.92,
        availability=0.85,
        p95_latency_ms=180.0,
        activation_latency_ms=5.0,
        prefetch_lead_ms=6.0,
        evidence=EvidenceStatus.PROJECTED,
    ),
    BuildCandidate(
        name="Oversized model — rejection fixture",
        vram_gib=140.0,
        host_ram_gib=300.0,
        pcie_gib_per_s=40.0,
        accepted_tokens_per_s=1000.0,
        quality_score=0.95,
        evidence=EvidenceStatus.ASSUMED,
    ),
]


for result in rank_builds(candidates, budget, minimum_quality=0.80):
    status = "FEASIBLE" if result.feasible else "REJECTED"
    score = f"{result.score:.2f}" if result.score is not None else "—"
    print(f"{status:8} score={score:>8}  {result.candidate.name}")
    if result.visible_stall_ms:
        print(f"         visible staging stall: {result.visible_stall_ms:.2f} ms")
    for violation in result.violations:
        print(f"         {violation.code}: {violation.detail}")
