"""Deterministic resource-ledger and breakpoint optimizer for inference builds.

This module intentionally does not predict benchmark performance from model names.
It evaluates caller-supplied measured or explicitly projected configurations against
resource, cadence, and quality constraints, then ranks only feasible candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Iterable, Mapping


class EvidenceStatus(str, Enum):
    MEASURED = "MEASURED"
    PROJECTED = "PROJECTED"
    ASSUMED = "ASSUMED"


@dataclass(frozen=True)
class ResourceBudget:
    vram_gib: float
    host_ram_gib: float
    pcie_gib_per_s: float
    power_watts: float | None = None


@dataclass(frozen=True)
class BuildCandidate:
    name: str
    vram_gib: float
    host_ram_gib: float
    pcie_gib_per_s: float
    accepted_tokens_per_s: float
    quality_score: float
    availability: float = 1.0
    p95_latency_ms: float = 0.0
    power_watts: float | None = None
    prefetch_lead_ms: float = 0.0
    activation_latency_ms: float = 0.0
    evidence: EvidenceStatus = EvidenceStatus.ASSUMED
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ObjectiveWeights:
    throughput: float = 1.0
    quality: float = 1.0
    availability: float = 0.5
    latency: float = 0.25
    vram_headroom: float = 0.25
    host_ram_headroom: float = 0.10
    evidence: float = 0.25


@dataclass(frozen=True)
class ConstraintViolation:
    code: str
    detail: str


@dataclass(frozen=True)
class EvaluatedBuild:
    candidate: BuildCandidate
    feasible: bool
    score: float | None
    visible_stall_ms: float
    violations: tuple[ConstraintViolation, ...]
    headroom: Mapping[str, float]


_EVIDENCE_MULTIPLIER = {
    EvidenceStatus.MEASURED: 1.0,
    EvidenceStatus.PROJECTED: 0.7,
    EvidenceStatus.ASSUMED: 0.4,
}


def _require_nonnegative(name: str, value: float) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")


def validate_candidate(candidate: BuildCandidate) -> None:
    for name in (
        "vram_gib",
        "host_ram_gib",
        "pcie_gib_per_s",
        "accepted_tokens_per_s",
        "p95_latency_ms",
        "prefetch_lead_ms",
        "activation_latency_ms",
    ):
        _require_nonnegative(name, float(getattr(candidate, name)))
    if candidate.power_watts is not None:
        _require_nonnegative("power_watts", candidate.power_watts)
    if not 0 <= candidate.quality_score <= 1:
        raise ValueError("quality_score must be between 0 and 1")
    if not 0 <= candidate.availability <= 1:
        raise ValueError("availability must be between 0 and 1")


def evaluate_build(
    candidate: BuildCandidate,
    budget: ResourceBudget,
    *,
    minimum_quality: float = 0.0,
    maximum_p95_latency_ms: float | None = None,
    weights: ObjectiveWeights | None = None,
) -> EvaluatedBuild:
    """Evaluate one candidate without inventing missing measurements.

    The score is returned only when all hard constraints hold. Visible staging
    stall follows the Blood Magic / Arcanist Brand breakpoint law:

        max(0, activation_latency - prefetch_lead)
    """
    validate_candidate(candidate)
    weights = weights or ObjectiveWeights()
    violations: list[ConstraintViolation] = []

    if candidate.vram_gib > budget.vram_gib:
        violations.append(ConstraintViolation("VRAM_EXCEEDED", f"{candidate.vram_gib:.2f} > {budget.vram_gib:.2f} GiB"))
    if candidate.host_ram_gib > budget.host_ram_gib:
        violations.append(ConstraintViolation("HOST_RAM_EXCEEDED", f"{candidate.host_ram_gib:.2f} > {budget.host_ram_gib:.2f} GiB"))
    if candidate.pcie_gib_per_s > budget.pcie_gib_per_s:
        violations.append(ConstraintViolation("PCIE_EXCEEDED", f"{candidate.pcie_gib_per_s:.2f} > {budget.pcie_gib_per_s:.2f} GiB/s"))
    if budget.power_watts is not None and candidate.power_watts is not None and candidate.power_watts > budget.power_watts:
        violations.append(ConstraintViolation("POWER_EXCEEDED", f"{candidate.power_watts:.1f} > {budget.power_watts:.1f} W"))
    if candidate.quality_score < minimum_quality:
        violations.append(ConstraintViolation("QUALITY_FLOOR", f"{candidate.quality_score:.3f} < {minimum_quality:.3f}"))
    if maximum_p95_latency_ms is not None and candidate.p95_latency_ms > maximum_p95_latency_ms:
        violations.append(ConstraintViolation("LATENCY_CEILING", f"{candidate.p95_latency_ms:.2f} > {maximum_p95_latency_ms:.2f} ms"))

    visible_stall_ms = max(0.0, candidate.activation_latency_ms - candidate.prefetch_lead_ms)
    headroom = {
        "vram_gib": budget.vram_gib - candidate.vram_gib,
        "host_ram_gib": budget.host_ram_gib - candidate.host_ram_gib,
        "pcie_gib_per_s": budget.pcie_gib_per_s - candidate.pcie_gib_per_s,
    }

    if violations:
        return EvaluatedBuild(candidate, False, None, visible_stall_ms, tuple(violations), headroom)

    latency_penalty = candidate.p95_latency_ms + visible_stall_ms
    score = (
        weights.throughput * candidate.accepted_tokens_per_s
        + weights.quality * candidate.quality_score * 100.0
        + weights.availability * candidate.availability * 100.0
        - weights.latency * latency_penalty
        + weights.vram_headroom * max(0.0, headroom["vram_gib"])
        + weights.host_ram_headroom * max(0.0, headroom["host_ram_gib"])
        + weights.evidence * _EVIDENCE_MULTIPLIER[candidate.evidence] * 100.0
    )
    return EvaluatedBuild(candidate, True, score, visible_stall_ms, (), headroom)


def rank_builds(
    candidates: Iterable[BuildCandidate],
    budget: ResourceBudget,
    *,
    minimum_quality: float = 0.0,
    maximum_p95_latency_ms: float | None = None,
    weights: ObjectiveWeights | None = None,
) -> list[EvaluatedBuild]:
    """Return feasible builds first by descending score, then rejected builds."""
    evaluated = [
        evaluate_build(
            candidate,
            budget,
            minimum_quality=minimum_quality,
            maximum_p95_latency_ms=maximum_p95_latency_ms,
            weights=weights,
        )
        for candidate in candidates
    ]
    return sorted(
        evaluated,
        key=lambda result: (
            not result.feasible,
            -(result.score if result.score is not None else float("-inf")),
            result.candidate.name,
        ),
    )


def nearest_breakpoint(candidate: BuildCandidate, budget: ResourceBudget) -> dict[str, float | str]:
    """Identify the tightest resource or staging breakpoint for one build."""
    validate_candidate(candidate)
    margins = {
        "vram_gib": budget.vram_gib - candidate.vram_gib,
        "host_ram_gib": budget.host_ram_gib - candidate.host_ram_gib,
        "pcie_gib_per_s": budget.pcie_gib_per_s - candidate.pcie_gib_per_s,
        "prefetch_ms": candidate.prefetch_lead_ms - candidate.activation_latency_ms,
    }
    resource = min(margins, key=margins.get)
    return {"resource": resource, "margin": margins[resource]}
