"""
Executable checks (gem_decode).

Deterministic validators that run over a translated build:

1. **Cadence / breakpoint checks** (COGNITIVE_COSPRI_001 — the build fails
   if any breakpoint is missed, even with all correct parts):

   - ``draft_rate ≤ verifier_acceptance_capacity``
     (overcapping = rejected drafts, queue pressure, cache churn)
   - ``prefetch_lead ≥ decompression_latency + transfer_latency``
   - ``concurrent_sequences ≤ kv_vram_budget``
   - ``trigger_frequency ≈ execution_recovery_rate``
     (too slow wastes capacity; too fast wastes trigger rolls)
   - flask fan-out ``≤ MIN(draft_capacity, verifier_capacity,
     network_throughput, scheduler_slots, memory_capacity, merge_bandwidth)``
     (FLASK_ONTOLOGY breakpoint law; only evaluated when the build has flasks)

   All parameters come from the caller's ``params`` dict. A check whose
   parameters are missing is SKIP — never a guessed PASS.

2. **Failure-family flags** (taxonomy A–T, RESEARCH_BRIEF) — composition
   pattern-matching against known breaker families.

3. **Adapa fixture** — high instruction fidelity with no calibrated-dissent
   anointment and no authority layer.

4. **Verdict** — HOLDS / STRAINS / UNRESOLVED
   (:mod:`semantic_compiler.expansion.verdicts` vocabulary):

   - any critical flag or cadence FAIL → STRAINS
   - else any WARN flag/check, any SKIP check, or unmapped component → UNRESOLVED
   - else (everything PASS, nothing flagged) → HOLDS
"""

from __future__ import annotations

from typing import Any, Optional

from semantic_compiler.expansion.gem_decode.ontology import ComponentEntry
from semantic_compiler.expansion.gem_decode.parser import GemBuild
from semantic_compiler.expansion.gem_decode.translator import resolve_entry
from semantic_compiler.expansion.verdicts import CorpusVerdict

ADAPA_FIXTURE_TEXT = (
    "ADAPA FIXTURE (Wisdom Class ≠ Authority Class): this build pairs "
    "high-instruction-fidelity model weights with no calibrated-dissent "
    "anointment and no authority layer — extraordinary capability with a "
    "fatal obedience weakness. Calibrated Dissent is the anti-Adapa notable "
    "(MISSING_SUPPORT_GEMS #10; ANOINTMENTS_AND_OILS companion surface)."
)

_NEAR_BREAKPOINT = 0.9   # within 90% of a cap: WARN
_UNDERUTILIZED = 0.5     # below 50% of useful rate: WARN (wasted capacity)


def _num(params: dict[str, Any], key: str) -> Optional[float]:
    value = params.get(key)
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _check(check_id: str, status: str, reason: str, **values: Any) -> dict[str, Any]:
    return {"check_id": check_id, "status": status, "reason": reason, "values": values}


# ---------------------------------------------------------------------------
# Cadence / breakpoint checks
# ---------------------------------------------------------------------------

def run_cadence_checks(build: GemBuild, params: dict[str, Any]) -> list[dict[str, Any]]:
    """Run the COGNITIVE_COSPRI_001 cadence law against caller-supplied numbers."""
    checks: list[dict[str, Any]] = []

    # 1. draft_rate ≤ verifier acceptance capacity
    draft_rate = _num(params, "draft_rate")
    capacity = _num(params, "verifier_acceptance_capacity")
    if draft_rate is None or capacity is None:
        checks.append(_check(
            "draft_rate_vs_verifier_capacity", "SKIP",
            "draft_rate and/or verifier_acceptance_capacity not provided",
        ))
    elif draft_rate > capacity:
        checks.append(_check(
            "draft_rate_vs_verifier_capacity", "FAIL",
            f"draft_rate {draft_rate:g} exceeds verifier acceptance capacity {capacity:g}: "
            "overcapping past the breakpoint — rejected drafts, queue pressure, cache churn",
            draft_rate=draft_rate, verifier_acceptance_capacity=capacity,
        ))
    elif draft_rate >= _NEAR_BREAKPOINT * capacity:
        checks.append(_check(
            "draft_rate_vs_verifier_capacity", "WARN",
            f"draft_rate {draft_rate:g} is within 10% of capacity {capacity:g}: at the breakpoint edge",
            draft_rate=draft_rate, verifier_acceptance_capacity=capacity,
        ))
    elif draft_rate < _UNDERUTILIZED * capacity:
        checks.append(_check(
            "draft_rate_vs_verifier_capacity", "WARN",
            f"draft_rate {draft_rate:g} uses under half of capacity {capacity:g}: wasted verifier capacity",
            draft_rate=draft_rate, verifier_acceptance_capacity=capacity,
        ))
    else:
        checks.append(_check(
            "draft_rate_vs_verifier_capacity", "PASS",
            f"draft_rate {draft_rate:g} within verifier capacity {capacity:g}",
            draft_rate=draft_rate, verifier_acceptance_capacity=capacity,
        ))

    # 2. prefetch_lead ≥ decompression + transfer latency
    lead = _num(params, "prefetch_lead")
    decomp = _num(params, "decompression_latency")
    transfer = _num(params, "transfer_latency")
    if lead is None or decomp is None or transfer is None:
        checks.append(_check(
            "prefetch_lead_vs_latency", "SKIP",
            "prefetch_lead, decompression_latency and/or transfer_latency not provided",
        ))
    elif lead >= decomp + transfer:
        checks.append(_check(
            "prefetch_lead_vs_latency", "PASS",
            f"prefetch lead {lead:g}s covers decompression+transfer {decomp + transfer:g}s",
            prefetch_lead=lead, required=decomp + transfer,
        ))
    else:
        checks.append(_check(
            "prefetch_lead_vs_latency", "FAIL",
            f"prefetch lead {lead:g}s shorter than decompression+transfer {decomp + transfer:g}s: "
            "predicted expert arrives too late",
            prefetch_lead=lead, required=decomp + transfer,
        ))

    # 3. concurrent_sequences ≤ KV/VRAM budget
    sequences = _num(params, "concurrent_sequences")
    kv_budget = _num(params, "kv_vram_budget")
    if sequences is None or kv_budget is None:
        checks.append(_check(
            "concurrency_vs_kv_vram_budget", "SKIP",
            "concurrent_sequences and/or kv_vram_budget not provided",
        ))
    elif sequences > kv_budget:
        checks.append(_check(
            "concurrency_vs_kv_vram_budget", "FAIL",
            f"{sequences:g} concurrent sequences exceed KV/VRAM budget {kv_budget:g}: memory exhaustion",
            concurrent_sequences=sequences, kv_vram_budget=kv_budget,
        ))
    elif sequences >= _NEAR_BREAKPOINT * kv_budget:
        checks.append(_check(
            "concurrency_vs_kv_vram_budget", "WARN",
            f"{sequences:g} concurrent sequences within 10% of KV/VRAM budget {kv_budget:g}",
            concurrent_sequences=sequences, kv_vram_budget=kv_budget,
        ))
    else:
        checks.append(_check(
            "concurrency_vs_kv_vram_budget", "PASS",
            f"{sequences:g} concurrent sequences within KV/VRAM budget {kv_budget:g}",
            concurrent_sequences=sequences, kv_vram_budget=kv_budget,
        ))

    # 4. trigger frequency ≈ execution recovery rate
    frequency = _num(params, "trigger_frequency")
    recovery = _num(params, "execution_recovery_rate")
    if frequency is None or recovery is None:
        checks.append(_check(
            "trigger_frequency_vs_recovery", "SKIP",
            "trigger_frequency and/or execution_recovery_rate not provided",
        ))
    elif frequency > recovery:
        checks.append(_check(
            "trigger_frequency_vs_recovery", "FAIL",
            f"trigger frequency {frequency:g}/s exceeds useful recovery rate {recovery:g}/s: "
            "wasted trigger rolls (overcapped attack speed past the CoC breakpoint)",
            trigger_frequency=frequency, execution_recovery_rate=recovery,
        ))
    elif frequency < _UNDERUTILIZED * recovery:
        checks.append(_check(
            "trigger_frequency_vs_recovery", "WARN",
            f"trigger frequency {frequency:g}/s under half of recovery rate {recovery:g}/s: wasted capacity",
            trigger_frequency=frequency, execution_recovery_rate=recovery,
        ))
    else:
        checks.append(_check(
            "trigger_frequency_vs_recovery", "PASS",
            f"trigger frequency {frequency:g}/s matched to recovery rate {recovery:g}/s",
            trigger_frequency=frequency, execution_recovery_rate=recovery,
        ))

    # 5. flask fan-out breakpoint (only when the build actually has flasks)
    if build.flasks:
        fanout = _num(params, "flask_fanout")
        caps = {
            key: _num(params, key)
            for key in (
                "draft_capacity", "verifier_capacity", "network_throughput",
                "scheduler_slots", "memory_capacity", "merge_bandwidth",
            )
        }
        if fanout is None or any(v is None for v in caps.values()):
            checks.append(_check(
                "flask_fanout_breakpoint", "SKIP",
                "flask_fanout and/or one of draft_capacity, verifier_capacity, "
                "network_throughput, scheduler_slots, memory_capacity, merge_bandwidth not provided",
            ))
        else:
            binding = min(caps, key=lambda k: caps[k])
            ceiling = caps[binding]
            if fanout > ceiling:
                checks.append(_check(
                    "flask_fanout_breakpoint", "FAIL",
                    f"flask fan-out {fanout:g} exceeds {binding} {ceiling:g}: "
                    f"{fanout - ceiling:g} wasted branches plus queue congestion and cache churn — "
                    "flasks need breakpoints, not maximum fan-out",
                    flask_fanout=fanout, binding_constraint=binding, ceiling=ceiling,
                ))
            elif fanout >= _NEAR_BREAKPOINT * ceiling:
                checks.append(_check(
                    "flask_fanout_breakpoint", "WARN",
                    f"flask fan-out {fanout:g} within 10% of {binding} ceiling {ceiling:g}",
                    flask_fanout=fanout, binding_constraint=binding, ceiling=ceiling,
                ))
            else:
                checks.append(_check(
                    "flask_fanout_breakpoint", "PASS",
                    f"flask fan-out {fanout:g} within breakpoint (binding constraint: {binding} {ceiling:g})",
                    flask_fanout=fanout, binding_constraint=binding, ceiling=ceiling,
                ))

    return checks


# ---------------------------------------------------------------------------
# Failure-family flags (taxonomy A–T)
# ---------------------------------------------------------------------------

def _flag(code: str, families: list[str], severity: str, description: str, trigger: str) -> dict[str, Any]:
    return {
        "code": code,
        "families": families,
        "severity": severity,
        "description": description,
        "trigger": trigger,
    }


def run_failure_family_checks(
    build: GemBuild,
    translated: dict[str, Any],
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    """Pattern-match the build composition against known breaker families."""
    flags: list[dict[str, Any]] = []

    entries: list[tuple[str, Optional[ComponentEntry]]] = [
        (name, resolve_entry(name, field_name))
        for field_name, name in build.all_components()
    ]
    aura_entries = [
        (name, e) for name, e in entries if e is not None and e.layer == "Aura"
    ]
    has_authority_layer = any(
        e is not None and e.authority_layer for _, e in entries
    )
    trigger_supports = [
        name for name, e in entries if e is not None and e.trigger_engine
    ]
    proxy_components = [
        name for name, e in entries if e is not None and e.proxy_compute
    ]
    has_scheduler = any(
        e is not None and e.canonical == "scheduler" for _, e in entries
    )

    # N — internal-classification leakage: an aura with no declared
    # affected-stat scope can amplify things never intended to count as
    # auras (Purposeful Harbinger governance law).
    for name, entry in aura_entries:
        if entry.scope is None:
            flags.append(_flag(
                "UNSCOPED_AURA", ["N"], "warn",
                f"aura '{name}' has no declared affected-stat scope: "
                "internal-classification leakage risk — one unscoped modifier can "
                "double-dip across generation, evaluation, authority, and routing "
                "(Purposeful Harbinger pattern). Declare: affected stats, stacking "
                "category, additive-vs-multiplicative rule, cap, diminishing returns.",
                trigger=name,
            ))

    # F — trigger-rate bypass: a trigger engine with no rate limiter
    # (no scheduler aura, no cadence parameters) fires unbounded.
    if trigger_supports and not has_scheduler and _num(params, "trigger_frequency") is None:
        flags.append(_flag(
            "TRIGGER_WITHOUT_COOLDOWN", ["F"], "warn",
            f"trigger engine ({', '.join(trigger_supports)}) has no payload cooldown: "
            "no scheduler aura and no trigger_frequency/execution_recovery_rate "
            "parameters — the gate event is unrate-limited (CoC pre-1.0.5 pattern).",
            trigger=", ".join(trigger_supports),
        ))

    # E/H — Hateforge pattern: proxy compute that pays no authority cost.
    if proxy_components and not has_authority_layer:
        flags.append(_flag(
            "PROXY_WITHOUT_AUTHORITY_COST", ["E", "H"], "critical",
            f"proxy compute ({', '.join(proxy_components)}) runs with no authority "
            "layer: bounded work executed away from the principal without paying "
            "authority cost is the Hateforge/totem-exploit pattern — cost and "
            "authority checks must follow the operation across principals.",
            trigger=", ".join(proxy_components),
        ))

    # E — budget refilled by the activity it gates (declared by the caller
    # or named in the spec; Soul Ripper moved cost off the watched currency).
    refill_names = [
        name for name, _ in entries
        if "soul ripper" in name.casefold() or "self refill" in name.casefold().replace("-", " ")
    ]
    if params.get("budget_refilled_by_gated_activity") or refill_names:
        flags.append(_flag(
            "SELF_REFILLING_BUDGET", ["E"], "critical",
            "the budget is refilled by the very activity it gates: the rate "
            "limiter watches a resource the build no longer consumes "
            "(Soul Ripper / currency-substitution pattern).",
            trigger=params.get("budget_refill_source") or ", ".join(refill_names) or "params",
        ))

    # Rejections must not pay: acceptance-minting on rejected drafts is
    # reward double-dipping. (Verified Returning Projectiles is legitimate —
    # it returns rejection REASONS, not credit.)
    rejection_pay = [
        name for name, _ in entries
        if any(marker in name.casefold()
               for marker in ("rejection credit", "rejections pay", "acceptance mint", "rejection reward"))
    ]
    if rejection_pay:
        flags.append(_flag(
            "REJECTIONS_MUST_NOT_PAY", ["C", "D"], "critical",
            f"'{rejection_pay[0]}' mints acceptance credit on rejected drafts: "
            "rejected work must return rejection reasons (Verified Returning "
            "Projectiles), never payment — one event must not credit two ledgers.",
            trigger=rejection_pay[0],
        ))

    # ADAPA fixture — high instruction fidelity without a dissent/authority layer.
    fidelity_payload = any(
        e is not None and e.high_instruction_fidelity for _, e in entries
    )
    if params.get("instruction_fidelity") == "high":
        fidelity_payload = True
    if fidelity_payload and not has_authority_layer:
        flags.append(_flag(
            "ADAPA_RISK", ["ADAPA"], "critical",
            ADAPA_FIXTURE_TEXT,
            trigger="high instruction fidelity without anointment/authority layer",
        ))

    return flags


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(
    checks: list[dict[str, Any]],
    flags: list[dict[str, Any]],
    unmapped_components: list[str],
) -> str:
    """Combine checks and flags into HOLDS / STRAINS / UNRESOLVED."""
    if any(f["severity"] == "critical" for f in flags):
        return CorpusVerdict.STRAINS.value
    if any(c["status"] == "FAIL" for c in checks):
        return CorpusVerdict.STRAINS.value
    if (
        any(c["status"] in ("WARN", "SKIP") for c in checks)
        or flags
        or unmapped_components
        or not checks
    ):
        return CorpusVerdict.UNRESOLVED.value
    return CorpusVerdict.HOLDS.value
