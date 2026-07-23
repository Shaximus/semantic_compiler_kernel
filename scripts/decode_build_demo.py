#!/usr/bin/env python3
"""Decode the two dialect examples plus the COGNITIVE_COSPRI_001 fixture.

Usage: python scripts/decode_build_demo.py
"""
from semantic_compiler.expansion.gem_decode import decode_build

POE_NATIVE_SPEC = (
    "Ice Nova + Cast on Critical Strike + Greater Multiple Projectiles; "
    "weapon: Cospri's Malice; auras: Hatred, Herald of Ice; "
    "flask: Dying Sun; anointment: Calibrated Dissent"
)

REFLEXION_NATIVE_SPEC = (
    "verifier: MiniMax M2.5; draft: Qwen draft; "
    "supports: MTP K=5, vLLM, expert compression; "
    "auras: BCC, TokenRouter, receipts; flask: auxiliary_i9; "
    "anointment: authority_gate"
)

# COGNITIVE_COSPRI_001 — canonical build-reconstruction fixture
# (MoE precognition build; the founder's favorite, 3 seasons).
COSPRI_FIXTURE_SPEC = (
    "verifier: RTX PRO 6000 target model verified execution; "
    "draft: lightweight continuous draft model; "
    "supports: speculative decoder (MTP K=5), expert precognition, cache stack; "
    "weapon: RTX 3080 Ti secondary trigger GPU; "
    "auras: BCC retrieval, TokenRouter, KV reuse, scheduler; "
    "flask: auxiliary_i9 (Dying Sun); "
    "anointment: Calibrated Dissent"
)

# Measured-like parameters that satisfy every breakpoint of the cadence law.
COSPRI_FIXTURE_PARAMS = {
    "draft_rate": 4000,                       # tokens/s from the draft model
    "verifier_acceptance_capacity": 5000,     # tokens/s the PRO 6000 can verify
    "prefetch_lead": 0.050,                   # predicted expert lead time (s)
    "decompression_latency": 0.020,           # expert weight decompression (s)
    "transfer_latency": 0.010,                # cross-device transfer (s)
    "concurrent_sequences": 8,
    "kv_vram_budget": 16,                     # sequences that fit in KV/VRAM
    "trigger_frequency": 120,                 # speculative procs per second
    "execution_recovery_rate": 150,           # useful verified executions per second
    "flask_fanout": 3,                        # auxiliary trajectories when Dying Sun active
    "draft_capacity": 5,
    "verifier_capacity": 4,
    "network_throughput": 6,
    "scheduler_slots": 4,
    "memory_capacity": 10,
    "merge_bandwidth": 5,
}

# The same fixture deliberately overcapped past the CoC breakpoint.
COSPRI_OVERCAPPED_PARAMS = {
    **COSPRI_FIXTURE_PARAMS,
    "draft_rate": 9000,          # exceeds verifier capacity: rejected drafts
    "trigger_frequency": 400,    # exceeds useful recovery rate: wasted trigger rolls
    "flask_fanout": 9,           # exceeds verifier_capacity 4: wasted branches
}


def _show(title: str, spec: str, params: dict | None = None) -> None:
    print("=" * 78)
    print(title)
    print("=" * 78)
    result = decode_build(spec, params=params)
    print(result.sheet)
    print()


if __name__ == "__main__":
    _show("SPEC A — PoE-native dialect", POE_NATIVE_SPEC)
    _show("SPEC B — Reflexion-native dialect", REFLEXION_NATIVE_SPEC)
    _show("FIXTURE — COGNITIVE_COSPRI_001 (tuned to the cadence law)",
          COSPRI_FIXTURE_SPEC, COSPRI_FIXTURE_PARAMS)
    _show("FIXTURE — COGNITIVE_COSPRI_001 (overcapped past the breakpoint)",
          COSPRI_FIXTURE_SPEC, COSPRI_OVERCAPPED_PARAMS)
