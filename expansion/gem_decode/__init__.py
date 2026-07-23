"""
Gem → Inference executable translation mode (gem_decode).

Decompiles a build specification written in PoE skill/support-gem language
into an inference-architecture build sheet with executable checks.

PoE gem language is specifically and accurately formatted — a fixed
five-layer vocabulary with deterministic composition rules — making it one
of the cleanest possible executable translation/decompression domains:

- Equipment    → permanently installed hardware
- Active skill → the primary payload (LLM weights)
- Support gem  → execution mechanics (MTP = GMP; acceptance rate = accuracy rating)
- Aura         → persistent modifier fields (BCC, doctrine, scheduler, ...)
- Anointment   → certified portable doctrine overlays (oils = evidence tiers)
- Flask        → temporary bounded burst modes (charges = concurrency budget)

Public API: :func:`decode_build`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from semantic_compiler.expansion.gem_decode.checks import (
    compute_verdict,
    run_cadence_checks,
    run_failure_family_checks,
)
from semantic_compiler.expansion.gem_decode.parser import (
    GemBuild,
    GemParseError,
    parse_build_spec,
)
from semantic_compiler.expansion.gem_decode.schema import validate_gem_build
from semantic_compiler.expansion.gem_decode.translator import (
    render_build_sheet,
    translate_build,
)


@dataclass(frozen=True)
class GemDecodeResult:
    """Everything a decoded build produces."""

    build: GemBuild
    translated: dict[str, Any]          # layers + unmapped components
    checks: list[dict[str, Any]]        # cadence/breakpoint results
    flags: list[dict[str, Any]]         # failure-family flags
    verdict: str                        # HOLDS | STRAINS | UNRESOLVED
    sheet: str                          # human-readable markdown build sheet
    json: dict[str, Any]                # schema-validated machine-readable record


def decode_build(spec_text: str, params: Optional[dict[str, Any]] = None) -> GemDecodeResult:
    """
    Decode a gem-language build spec into an inference-architecture build sheet.

    Parameters
    ----------
    spec_text:
        The build specification, in either dialect (PoE-native gem chains or
        Reflexion-native keyed sections).
    params:
        Optional numeric parameters for the executable cadence checks, e.g.
        ``draft_rate``, ``verifier_acceptance_capacity``, ``prefetch_lead``,
        ``decompression_latency``, ``transfer_latency``,
        ``concurrent_sequences``, ``kv_vram_budget``, ``trigger_frequency``,
        ``execution_recovery_rate``, ``flask_fanout``, ``draft_capacity``,
        ``verifier_capacity``, ``network_throughput``, ``scheduler_slots``,
        ``memory_capacity``, ``merge_bandwidth``; plus the behavioral toggles
        ``budget_refilled_by_gated_activity`` and ``instruction_fidelity``.
        Checks with missing parameters report SKIP, never a guessed PASS.
    """
    params = dict(params or {})
    build = parse_build_spec(spec_text)
    translated = translate_build(build)
    checks = run_cadence_checks(build, params)
    flags = run_failure_family_checks(build, translated, params)
    verdict = compute_verdict(checks, flags, translated["unmapped_components"])
    sheet = render_build_sheet(build, translated, checks, flags, verdict)

    record: dict[str, Any] = {
        "schema": "reflexion.gem_build.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dialect": build.dialect,
        "raw_spec": build.raw,
        "layers": translated["layers"],
        "unmapped_components": translated["unmapped_components"],
        "checks": checks,
        "failure_flags": flags,
        "verdict": verdict,
        "params_used": {k: v for k, v in params.items() if isinstance(v, (int, float, str, bool))},
    }
    errors = validate_gem_build(record)
    if errors:
        raise ValueError(f"decoded gem build failed schema validation: {errors}")

    return GemDecodeResult(
        build=build,
        translated=translated,
        checks=checks,
        flags=flags,
        verdict=verdict,
        sheet=sheet,
        json=record,
    )


__all__ = [
    "decode_build",
    "GemDecodeResult",
    "GemBuild",
    "GemParseError",
    "parse_build_spec",
]
