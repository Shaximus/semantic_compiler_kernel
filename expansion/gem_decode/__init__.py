"""
Gem → Inference executable translation mode (gem_decode).

Decompiles a build specification written in PoE skill/support-gem language
into an inference-architecture build sheet with executable checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from semantic_compiler.expansion.gem_decode.archetypes import identify_archetypes
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
    translated: dict[str, Any]
    archetypes: list[dict[str, Any]]
    checks: list[dict[str, Any]]
    flags: list[dict[str, Any]]
    verdict: str
    sheet: str
    json: dict[str, Any]


def decode_build(spec_text: str, params: Optional[dict[str, Any]] = None) -> GemDecodeResult:
    """Decode a gem-language build into an executable inference build sheet.

    Missing numeric parameters remain SKIP rather than being guessed. Archetype
    confidence describes structural resemblance, not measured performance.
    """
    params = dict(params or {})
    build = parse_build_spec(spec_text)
    translated = translate_build(build)
    archetypes = identify_archetypes(build, translated)
    checks = run_cadence_checks(build, params)
    flags = run_failure_family_checks(build, translated, params)
    verdict = compute_verdict(checks, flags, translated["unmapped_components"])
    sheet = render_build_sheet(build, translated, checks, flags, verdict)
    if archetypes:
        lines = [sheet, "", "## Attempted build archetypes", ""]
        for item in archetypes:
            lines.append(
                f"- **[{item['status']}] {item['name']}** — confidence "
                f"{item['confidence']:.3f}; {item['invariant']}"
            )
            if item["missing_groups"]:
                missing = [" / ".join(group) for group in item["missing_groups"]]
                lines.append(f"  - Missing invariant groups: {'; '.join(missing)}")
        sheet = "\n".join(lines)

    record: dict[str, Any] = {
        "schema": "reflexion.gem_build.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dialect": build.dialect,
        "raw_spec": build.raw,
        "layers": translated["layers"],
        "unmapped_components": translated["unmapped_components"],
        "archetypes": archetypes,
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
        archetypes=archetypes,
        checks=checks,
        flags=flags,
        verdict=verdict,
        sheet=sheet,
        json=record,
    )


__all__ = [
    "decode_build",
    "identify_archetypes",
    "GemDecodeResult",
    "GemBuild",
    "GemParseError",
    "parse_build_spec",
]
