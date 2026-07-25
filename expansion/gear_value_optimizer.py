"""Slot-aware throughput-per-CAD optimizer for inference hardware.

The optimizer never predicts performance from a product name or specification sheet.
It ranks caller-supplied benchmark observations for either:

1. one-slot upgrades against the same baseline build and workload; or
2. complete, benchmarked loadouts.

This distinction prevents additive-item-score fiction: accelerator, host, memory,
storage, fabric, power, and cooling effects may interact non-linearly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Iterable, Mapping

from semantic_compiler.expansion.build_optimizer import EvidenceStatus


class GearSlot(str, Enum):
    """Canonical PoE-style equipment slots for hardware purchase analysis."""

    WEAPON_PRIMARY = "WEAPON_PRIMARY"
    WEAPON_OFFHAND = "WEAPON_OFFHAND"
    BODY_ARMOUR = "BODY_ARMOUR"
    HELMET = "HELMET"
    GLOVES = "GLOVES"
    BOOTS = "BOOTS"
    AMULET = "AMULET"
    RING_LEFT = "RING_LEFT"
    RING_RIGHT = "RING_RIGHT"
    BELT = "BELT"


@dataclass(frozen=True)
class ValueConstraints:
    """Hard constraints applied before any value ranking."""

    maximum_net_cost_cad: float | None = None
    minimum_quality_score: float = 0.0
    minimum_quality_retention: float = 0.0
    maximum_p95_latency_ms: float | None = None
    maximum_power_watts: float | None = None
    require_measured_evidence: bool = False
    require_positive_throughput_gain: bool = True


@dataclass(frozen=True)
class ValueViolation:
    code: str
    detail: str


@dataclass(frozen=True)
class UpgradeCandidate:
    """Observed effect of replacing one slot while holding the baseline constant.

    `landed_cost_cad` should include purchase price, tax, shipping, duties, and
    currency-conversion fees. `resale_credit_cad` is the realizable sale value of
    displaced equipment, not its original purchase price.
    """

    name: str
    slot: GearSlot
    workload_id: str
    baseline_build_id: str
    landed_cost_cad: float
    baseline_accepted_tokens_per_s: float
    candidate_accepted_tokens_per_s: float
    baseline_quality_score: float
    candidate_quality_score: float
    required_addon_cost_cad: float = 0.0
    resale_credit_cad: float = 0.0
    candidate_availability: float = 1.0
    candidate_p95_latency_ms: float = 0.0
    candidate_power_watts: float | None = None
    evidence: EvidenceStatus = EvidenceStatus.ASSUMED
    compatibility_violations: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluatedUpgrade:
    candidate: UpgradeCandidate
    feasible: bool
    net_cost_cad: float
    throughput_gain: float
    quality_retention: float
    absolute_tps_per_cad: float | None
    marginal_tps_per_cad: float | None
    risk_adjusted_marginal_tps_per_cad: float | None
    violations: tuple[ValueViolation, ...]


@dataclass(frozen=True)
class LoadoutCandidate:
    """A complete build with observed end-to-end performance."""

    name: str
    workload_id: str
    items: Mapping[GearSlot, str]
    total_landed_cost_cad: float
    accepted_tokens_per_s: float
    quality_score: float
    availability: float = 1.0
    p95_latency_ms: float = 0.0
    power_watts: float | None = None
    evidence: EvidenceStatus = EvidenceStatus.ASSUMED
    compatibility_violations: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluatedLoadout:
    candidate: LoadoutCandidate
    feasible: bool
    throughput_per_cad: float | None
    risk_adjusted_throughput_per_cad: float | None
    violations: tuple[ValueViolation, ...]


_EVIDENCE_MULTIPLIER = {
    EvidenceStatus.MEASURED: 1.0,
    EvidenceStatus.PROJECTED: 0.7,
    EvidenceStatus.ASSUMED: 0.4,
}


def _require_nonnegative(name: str, value: float) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")


def _require_unit_interval(name: str, value: float) -> None:
    if not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")


def validate_upgrade(candidate: UpgradeCandidate) -> None:
    for name in (
        "landed_cost_cad",
        "required_addon_cost_cad",
        "resale_credit_cad",
        "baseline_accepted_tokens_per_s",
        "candidate_accepted_tokens_per_s",
        "candidate_p95_latency_ms",
    ):
        _require_nonnegative(name, float(getattr(candidate, name)))
    if candidate.candidate_power_watts is not None:
        _require_nonnegative("candidate_power_watts", candidate.candidate_power_watts)
    _require_unit_interval("baseline_quality_score", candidate.baseline_quality_score)
    _require_unit_interval("candidate_quality_score", candidate.candidate_quality_score)
    _require_unit_interval("candidate_availability", candidate.candidate_availability)


def evaluate_upgrade(
    candidate: UpgradeCandidate,
    constraints: ValueConstraints | None = None,
) -> EvaluatedUpgrade:
    """Evaluate one observed slot replacement.

    Raw marginal value is:

        (candidate throughput - baseline throughput) / net acquisition cost

    Risk-adjusted marginal value additionally discounts non-measured evidence,
    availability loss, and quality loss. The raw metric is always retained.
    """

    validate_upgrade(candidate)
    constraints = constraints or ValueConstraints()
    violations: list[ValueViolation] = []

    net_cost = candidate.landed_cost_cad + candidate.required_addon_cost_cad - candidate.resale_credit_cad
    throughput_gain = candidate.candidate_accepted_tokens_per_s - candidate.baseline_accepted_tokens_per_s
    quality_retention = (
        candidate.candidate_quality_score / candidate.baseline_quality_score
        if candidate.baseline_quality_score > 0
        else 1.0
    )

    if net_cost <= 0:
        violations.append(ValueViolation("NONPOSITIVE_NET_COST", f"net cost is CAD {net_cost:.2f}"))
    if constraints.maximum_net_cost_cad is not None and net_cost > constraints.maximum_net_cost_cad:
        violations.append(
            ValueViolation(
                "BUDGET_EXCEEDED",
                f"CAD {net_cost:.2f} > CAD {constraints.maximum_net_cost_cad:.2f}",
            )
        )
    if candidate.candidate_quality_score < constraints.minimum_quality_score:
        violations.append(
            ValueViolation(
                "QUALITY_FLOOR",
                f"{candidate.candidate_quality_score:.3f} < {constraints.minimum_quality_score:.3f}",
            )
        )
    if quality_retention < constraints.minimum_quality_retention:
        violations.append(
            ValueViolation(
                "QUALITY_RETENTION",
                f"{quality_retention:.3f} < {constraints.minimum_quality_retention:.3f}",
            )
        )
    if (
        constraints.maximum_p95_latency_ms is not None
        and candidate.candidate_p95_latency_ms > constraints.maximum_p95_latency_ms
    ):
        violations.append(
            ValueViolation(
                "LATENCY_CEILING",
                f"{candidate.candidate_p95_latency_ms:.2f} > {constraints.maximum_p95_latency_ms:.2f} ms",
            )
        )
    if (
        constraints.maximum_power_watts is not None
        and candidate.candidate_power_watts is not None
        and candidate.candidate_power_watts > constraints.maximum_power_watts
    ):
        violations.append(
            ValueViolation(
                "POWER_CEILING",
                f"{candidate.candidate_power_watts:.1f} > {constraints.maximum_power_watts:.1f} W",
            )
        )
    if constraints.require_measured_evidence and candidate.evidence is not EvidenceStatus.MEASURED:
        violations.append(ValueViolation("MEASURED_EVIDENCE_REQUIRED", candidate.evidence.value))
    if constraints.require_positive_throughput_gain and throughput_gain <= 0:
        violations.append(ValueViolation("NO_POSITIVE_GAIN", f"throughput gain is {throughput_gain:.3f} tok/s"))
    for detail in candidate.compatibility_violations:
        violations.append(ValueViolation("COMPATIBILITY", detail))

    if net_cost <= 0:
        absolute = marginal = adjusted = None
    else:
        absolute = candidate.candidate_accepted_tokens_per_s / net_cost
        marginal = throughput_gain / net_cost
        quality_discount = min(1.0, quality_retention)
        adjusted = (
            marginal
            * _EVIDENCE_MULTIPLIER[candidate.evidence]
            * candidate.candidate_availability
            * quality_discount
        )

    return EvaluatedUpgrade(
        candidate=candidate,
        feasible=not violations,
        net_cost_cad=net_cost,
        throughput_gain=throughput_gain,
        quality_retention=quality_retention,
        absolute_tps_per_cad=absolute,
        marginal_tps_per_cad=marginal,
        risk_adjusted_marginal_tps_per_cad=adjusted,
        violations=tuple(violations),
    )


def rank_upgrades(
    candidates: Iterable[UpgradeCandidate],
    constraints: ValueConstraints | None = None,
) -> list[EvaluatedUpgrade]:
    """Rank comparable one-slot observations by risk-adjusted marginal value."""

    evaluated = [evaluate_upgrade(candidate, constraints) for candidate in candidates]
    return sorted(
        evaluated,
        key=lambda result: (
            not result.feasible,
            -(result.risk_adjusted_marginal_tps_per_cad or float("-inf")),
            -(result.marginal_tps_per_cad or float("-inf")),
            result.net_cost_cad,
            result.candidate.name,
        ),
    )


def _assert_comparable(candidates: Iterable[UpgradeCandidate]) -> list[UpgradeCandidate]:
    materialized = list(candidates)
    identities = {(candidate.workload_id, candidate.baseline_build_id) for candidate in materialized}
    if len(identities) > 1:
        raise ValueError("slot winners require one shared workload_id and baseline_build_id")
    return materialized


def best_upgrade_by_slot(
    candidates: Iterable[UpgradeCandidate],
    constraints: ValueConstraints | None = None,
) -> dict[GearSlot, EvaluatedUpgrade]:
    """Return the highest-value feasible upgrade for each equipment slot."""

    materialized = _assert_comparable(candidates)
    winners: dict[GearSlot, EvaluatedUpgrade] = {}
    for result in rank_upgrades(materialized, constraints):
        if result.feasible and result.candidate.slot not in winners:
            winners[result.candidate.slot] = result
    return winners


def best_overall_upgrade(
    candidates: Iterable[UpgradeCandidate],
    constraints: ValueConstraints | None = None,
) -> EvaluatedUpgrade | None:
    """Return the single highest-value feasible slot upgrade across the build."""

    ranked = rank_upgrades(_assert_comparable(candidates), constraints)
    return next((result for result in ranked if result.feasible), None)


def validate_loadout(candidate: LoadoutCandidate) -> None:
    _require_nonnegative("total_landed_cost_cad", candidate.total_landed_cost_cad)
    _require_nonnegative("accepted_tokens_per_s", candidate.accepted_tokens_per_s)
    _require_nonnegative("p95_latency_ms", candidate.p95_latency_ms)
    if candidate.power_watts is not None:
        _require_nonnegative("power_watts", candidate.power_watts)
    _require_unit_interval("quality_score", candidate.quality_score)
    _require_unit_interval("availability", candidate.availability)


def evaluate_loadout(
    candidate: LoadoutCandidate,
    constraints: ValueConstraints | None = None,
) -> EvaluatedLoadout:
    """Evaluate a complete observed loadout without summing item claims."""

    validate_loadout(candidate)
    constraints = constraints or ValueConstraints(require_positive_throughput_gain=False)
    violations: list[ValueViolation] = []

    if candidate.total_landed_cost_cad <= 0:
        violations.append(ValueViolation("NONPOSITIVE_TOTAL_COST", "complete loadout cost must be positive"))
    if (
        constraints.maximum_net_cost_cad is not None
        and candidate.total_landed_cost_cad > constraints.maximum_net_cost_cad
    ):
        violations.append(
            ValueViolation(
                "BUDGET_EXCEEDED",
                f"CAD {candidate.total_landed_cost_cad:.2f} > CAD {constraints.maximum_net_cost_cad:.2f}",
            )
        )
    if candidate.quality_score < constraints.minimum_quality_score:
        violations.append(
            ValueViolation(
                "QUALITY_FLOOR",
                f"{candidate.quality_score:.3f} < {constraints.minimum_quality_score:.3f}",
            )
        )
    if (
        constraints.maximum_p95_latency_ms is not None
        and candidate.p95_latency_ms > constraints.maximum_p95_latency_ms
    ):
        violations.append(
            ValueViolation(
                "LATENCY_CEILING",
                f"{candidate.p95_latency_ms:.2f} > {constraints.maximum_p95_latency_ms:.2f} ms",
            )
        )
    if (
        constraints.maximum_power_watts is not None
        and candidate.power_watts is not None
        and candidate.power_watts > constraints.maximum_power_watts
    ):
        violations.append(
            ValueViolation(
                "POWER_CEILING",
                f"{candidate.power_watts:.1f} > {constraints.maximum_power_watts:.1f} W",
            )
        )
    if constraints.require_measured_evidence and candidate.evidence is not EvidenceStatus.MEASURED:
        violations.append(ValueViolation("MEASURED_EVIDENCE_REQUIRED", candidate.evidence.value))
    for detail in candidate.compatibility_violations:
        violations.append(ValueViolation("COMPATIBILITY", detail))

    if candidate.total_landed_cost_cad <= 0:
        raw = adjusted = None
    else:
        raw = candidate.accepted_tokens_per_s / candidate.total_landed_cost_cad
        adjusted = (
            raw
            * _EVIDENCE_MULTIPLIER[candidate.evidence]
            * candidate.availability
            * candidate.quality_score
        )

    return EvaluatedLoadout(candidate, not violations, raw, adjusted, tuple(violations))


def rank_loadouts(
    candidates: Iterable[LoadoutCandidate],
    constraints: ValueConstraints | None = None,
) -> list[EvaluatedLoadout]:
    """Rank complete loadouts by risk-adjusted end-to-end throughput per CAD."""

    evaluated = [evaluate_loadout(candidate, constraints) for candidate in candidates]
    workloads = {result.candidate.workload_id for result in evaluated}
    if len(workloads) > 1:
        raise ValueError("loadout ranking requires one shared workload_id")
    return sorted(
        evaluated,
        key=lambda result: (
            not result.feasible,
            -(result.risk_adjusted_throughput_per_cad or float("-inf")),
            -(result.throughput_per_cad or float("-inf")),
            result.candidate.total_landed_cost_cad,
            result.candidate.name,
        ),
    )


def greatest_throughput_per_cad(
    candidates: Iterable[LoadoutCandidate],
    constraints: ValueConstraints | None = None,
) -> EvaluatedLoadout | None:
    """Return the single best feasible complete build for the shared workload."""

    return next((result for result in rank_loadouts(candidates, constraints) if result.feasible), None)
