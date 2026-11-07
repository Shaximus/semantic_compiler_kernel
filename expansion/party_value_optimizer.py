"""Topology-aware party/aura throughput-per-CAD optimizer.

This module evaluates infrastructure as a linked inference party rather than as
independent machines. A support node may be valuable because it performs work
itself, reclaims capacity on the carry, removes stalls, or enables additional
concurrency. Link, synchronization, integration, and failure-domain costs are
charged explicitly.

The optimizer never infers performance from product names or specification
sheets. Every gain or penalty is supplied by a benchmark, projection, or stated
assumption and retains its evidence status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Iterable, Mapping

from semantic_compiler.expansion.build_optimizer import EvidenceStatus


class PartyRole(str, Enum):
    CARRY = "CARRY"
    AURABOT = "AURABOT"
    HYBRID = "HYBRID"
    CONTROL_PLANE = "CONTROL_PLANE"
    ARCHIVE = "ARCHIVE"
    DRAFT_ENGINE = "DRAFT_ENGINE"
    RETRIEVAL_ENGINE = "RETRIEVAL_ENGINE"


class AuraCategory(str, Enum):
    MEMORY = "MEMORY"
    STORAGE = "STORAGE"
    NETWORK = "NETWORK"
    RETRIEVAL = "RETRIEVAL"
    DRAFTING = "DRAFTING"
    ORCHESTRATION = "ORCHESTRATION"
    PREPROCESSING = "PREPROCESSING"
    COMPILATION = "COMPILATION"
    FAILOVER = "FAILOVER"
    POWER_THERMAL = "POWER_THERMAL"


@dataclass(frozen=True)
class PartyConstraints:
    maximum_net_cost_cad: float | None = None
    minimum_quality_retention: float = 0.0
    minimum_party_availability: float = 0.0
    maximum_p95_latency_ms: float | None = None
    maximum_added_power_watts: float | None = None
    require_measured_evidence: bool = False
    require_positive_party_gain: bool = True
    require_offline_capability: bool = False
    maximum_new_shared_failure_domains: int | None = None


@dataclass(frozen=True)
class PartyViolation:
    code: str
    detail: str


@dataclass(frozen=True)
class PartyUpgradeCandidate:
    """Observed or projected effect of adding one linked party component.

    All throughput fields are accepted-token-equivalent rates for one shared
    workload and baseline. `concurrency_gain_tps_equivalent` may be used only
    when the caller has an explicit conversion from additional completed work
    to the same throughput unit.
    """

    name: str
    workload_id: str
    baseline_party_id: str
    node_role: PartyRole
    aura_categories: tuple[AuraCategory, ...]
    landed_cost_cad: float
    required_addon_cost_cad: float = 0.0
    resale_credit_cad: float = 0.0

    direct_tps_gain: float = 0.0
    carry_tps_reclaimed: float = 0.0
    concurrency_gain_tps_equivalent: float = 0.0
    stall_tps_recovered: float = 0.0

    link_penalty_tps: float = 0.0
    synchronization_penalty_tps: float = 0.0
    integration_penalty_tps: float = 0.0

    baseline_quality_score: float = 1.0
    candidate_quality_score: float = 1.0
    party_availability: float = 1.0
    candidate_p95_latency_ms: float = 0.0
    added_power_watts: float | None = None

    required_link_gib_per_s: float = 0.0
    available_link_gib_per_s: float = 0.0
    required_internet: bool = False
    new_shared_failure_domains: int = 0
    compatibility_violations: tuple[str, ...] = ()
    evidence: EvidenceStatus = EvidenceStatus.ASSUMED
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluatedPartyUpgrade:
    candidate: PartyUpgradeCandidate
    feasible: bool
    net_cost_cad: float
    gross_party_gain_tps: float
    total_penalty_tps: float
    net_party_gain_tps: float
    quality_retention: float
    raw_party_tps_per_cad: float | None
    risk_adjusted_party_tps_per_cad: float | None
    violations: tuple[PartyViolation, ...]


@dataclass(frozen=True)
class PartyLoadoutCandidate:
    """One complete, end-to-end observed party topology."""

    name: str
    workload_id: str
    nodes: Mapping[str, PartyRole]
    links: Mapping[str, str]
    total_landed_cost_cad: float
    accepted_tokens_per_s: float
    quality_score: float
    availability: float = 1.0
    p95_latency_ms: float = 0.0
    power_watts: float | None = None
    required_internet: bool = False
    shared_failure_domains: int = 0
    compatibility_violations: tuple[str, ...] = ()
    evidence: EvidenceStatus = EvidenceStatus.ASSUMED
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluatedPartyLoadout:
    candidate: PartyLoadoutCandidate
    feasible: bool
    throughput_per_cad: float | None
    risk_adjusted_throughput_per_cad: float | None
    violations: tuple[PartyViolation, ...]


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


def validate_party_upgrade(candidate: PartyUpgradeCandidate) -> None:
    for name in (
        "landed_cost_cad",
        "required_addon_cost_cad",
        "resale_credit_cad",
        "direct_tps_gain",
        "carry_tps_reclaimed",
        "concurrency_gain_tps_equivalent",
        "stall_tps_recovered",
        "link_penalty_tps",
        "synchronization_penalty_tps",
        "integration_penalty_tps",
        "candidate_p95_latency_ms",
        "required_link_gib_per_s",
        "available_link_gib_per_s",
    ):
        _require_nonnegative(name, float(getattr(candidate, name)))
    if candidate.added_power_watts is not None:
        _require_nonnegative("added_power_watts", candidate.added_power_watts)
    if candidate.new_shared_failure_domains < 0:
        raise ValueError("new_shared_failure_domains must be non-negative")
    _require_unit_interval("baseline_quality_score", candidate.baseline_quality_score)
    _require_unit_interval("candidate_quality_score", candidate.candidate_quality_score)
    _require_unit_interval("party_availability", candidate.party_availability)


def evaluate_party_upgrade(
    candidate: PartyUpgradeCandidate,
    constraints: PartyConstraints | None = None,
) -> EvaluatedPartyUpgrade:
    """Evaluate one linked party upgrade against a shared baseline.

    gross_party_gain = direct work + carry capacity reclaimed + concurrency value
                       + recovered stalls
    net_party_gain   = gross_party_gain - link/sync/integration penalties
    """

    validate_party_upgrade(candidate)
    constraints = constraints or PartyConstraints()
    violations: list[PartyViolation] = []

    net_cost = candidate.landed_cost_cad + candidate.required_addon_cost_cad - candidate.resale_credit_cad
    gross_gain = (
        candidate.direct_tps_gain
        + candidate.carry_tps_reclaimed
        + candidate.concurrency_gain_tps_equivalent
        + candidate.stall_tps_recovered
    )
    total_penalty = (
        candidate.link_penalty_tps
        + candidate.synchronization_penalty_tps
        + candidate.integration_penalty_tps
    )
    net_gain = gross_gain - total_penalty
    quality_retention = (
        candidate.candidate_quality_score / candidate.baseline_quality_score
        if candidate.baseline_quality_score > 0
        else 1.0
    )

    if net_cost <= 0:
        violations.append(PartyViolation("NONPOSITIVE_NET_COST", f"net cost is CAD {net_cost:.2f}"))
    if constraints.maximum_net_cost_cad is not None and net_cost > constraints.maximum_net_cost_cad:
        violations.append(
            PartyViolation(
                "BUDGET_EXCEEDED",
                f"CAD {net_cost:.2f} > CAD {constraints.maximum_net_cost_cad:.2f}",
            )
        )
    if quality_retention < constraints.minimum_quality_retention:
        violations.append(
            PartyViolation(
                "QUALITY_RETENTION",
                f"{quality_retention:.3f} < {constraints.minimum_quality_retention:.3f}",
            )
        )
    if candidate.party_availability < constraints.minimum_party_availability:
        violations.append(
            PartyViolation(
                "AVAILABILITY_FLOOR",
                f"{candidate.party_availability:.3f} < {constraints.minimum_party_availability:.3f}",
            )
        )
    if (
        constraints.maximum_p95_latency_ms is not None
        and candidate.candidate_p95_latency_ms > constraints.maximum_p95_latency_ms
    ):
        violations.append(
            PartyViolation(
                "LATENCY_CEILING",
                f"{candidate.candidate_p95_latency_ms:.2f} > {constraints.maximum_p95_latency_ms:.2f} ms",
            )
        )
    if (
        constraints.maximum_added_power_watts is not None
        and candidate.added_power_watts is not None
        and candidate.added_power_watts > constraints.maximum_added_power_watts
    ):
        violations.append(
            PartyViolation(
                "POWER_CEILING",
                f"{candidate.added_power_watts:.1f} > {constraints.maximum_added_power_watts:.1f} W",
            )
        )
    if candidate.required_link_gib_per_s > candidate.available_link_gib_per_s:
        violations.append(
            PartyViolation(
                "LINK_CAPACITY_EXCEEDED",
                f"{candidate.required_link_gib_per_s:.3f} > {candidate.available_link_gib_per_s:.3f} GiB/s",
            )
        )
    if constraints.require_offline_capability and candidate.required_internet:
        violations.append(PartyViolation("INTERNET_DEPENDENCY", "candidate cannot operate in offline mode"))
    if (
        constraints.maximum_new_shared_failure_domains is not None
        and candidate.new_shared_failure_domains > constraints.maximum_new_shared_failure_domains
    ):
        violations.append(
            PartyViolation(
                "FAILURE_DOMAIN_LIMIT",
                f"{candidate.new_shared_failure_domains} > {constraints.maximum_new_shared_failure_domains}",
            )
        )
    if constraints.require_measured_evidence and candidate.evidence is not EvidenceStatus.MEASURED:
        violations.append(PartyViolation("MEASURED_EVIDENCE_REQUIRED", candidate.evidence.value))
    if constraints.require_positive_party_gain and net_gain <= 0:
        violations.append(PartyViolation("NO_POSITIVE_PARTY_GAIN", f"net gain is {net_gain:.3f} tok/s"))
    for detail in candidate.compatibility_violations:
        violations.append(PartyViolation("COMPATIBILITY", detail))

    if net_cost <= 0:
        raw_value = adjusted_value = None
    else:
        raw_value = net_gain / net_cost
        adjusted_value = (
            raw_value
            * _EVIDENCE_MULTIPLIER[candidate.evidence]
            * candidate.party_availability
            * min(1.0, quality_retention)
        )

    return EvaluatedPartyUpgrade(
        candidate=candidate,
        feasible=not violations,
        net_cost_cad=net_cost,
        gross_party_gain_tps=gross_gain,
        total_penalty_tps=total_penalty,
        net_party_gain_tps=net_gain,
        quality_retention=quality_retention,
        raw_party_tps_per_cad=raw_value,
        risk_adjusted_party_tps_per_cad=adjusted_value,
        violations=tuple(violations),
    )


def _assert_comparable_party_upgrades(
    candidates: Iterable[PartyUpgradeCandidate],
) -> list[PartyUpgradeCandidate]:
    materialized = list(candidates)
    identities = {(candidate.workload_id, candidate.baseline_party_id) for candidate in materialized}
    if len(identities) > 1:
        raise ValueError("party upgrades require one shared workload_id and baseline_party_id")
    return materialized


def rank_party_upgrades(
    candidates: Iterable[PartyUpgradeCandidate],
    constraints: PartyConstraints | None = None,
) -> list[EvaluatedPartyUpgrade]:
    """Rank comparable party upgrades by risk-adjusted net party throughput per CAD."""

    materialized = _assert_comparable_party_upgrades(candidates)
    evaluated = [evaluate_party_upgrade(candidate, constraints) for candidate in materialized]
    return sorted(
        evaluated,
        key=lambda result: (
            not result.feasible,
            -(result.risk_adjusted_party_tps_per_cad or float("-inf")),
            -(result.raw_party_tps_per_cad or float("-inf")),
            result.net_cost_cad,
            result.candidate.name,
        ),
    )


def best_party_upgrade(
    candidates: Iterable[PartyUpgradeCandidate],
    constraints: PartyConstraints | None = None,
) -> EvaluatedPartyUpgrade | None:
    """Return the single greatest feasible party-level throughput-per-CAD upgrade."""

    return next((result for result in rank_party_upgrades(candidates, constraints) if result.feasible), None)


def best_aura_by_category(
    candidates: Iterable[PartyUpgradeCandidate],
    constraints: PartyConstraints | None = None,
) -> dict[AuraCategory, EvaluatedPartyUpgrade]:
    """Return the highest-value feasible upgrade affecting each aura category."""

    winners: dict[AuraCategory, EvaluatedPartyUpgrade] = {}
    for result in rank_party_upgrades(candidates, constraints):
        if not result.feasible:
            continue
        for category in result.candidate.aura_categories:
            winners.setdefault(category, result)
    return winners


def validate_party_loadout(candidate: PartyLoadoutCandidate) -> None:
    _require_nonnegative("total_landed_cost_cad", candidate.total_landed_cost_cad)
    _require_nonnegative("accepted_tokens_per_s", candidate.accepted_tokens_per_s)
    _require_nonnegative("p95_latency_ms", candidate.p95_latency_ms)
    if candidate.power_watts is not None:
        _require_nonnegative("power_watts", candidate.power_watts)
    if candidate.shared_failure_domains < 0:
        raise ValueError("shared_failure_domains must be non-negative")
    _require_unit_interval("quality_score", candidate.quality_score)
    _require_unit_interval("availability", candidate.availability)


def evaluate_party_loadout(
    candidate: PartyLoadoutCandidate,
    constraints: PartyConstraints | None = None,
) -> EvaluatedPartyLoadout:
    """Evaluate one complete topology from end-to-end measurements."""

    validate_party_loadout(candidate)
    constraints = constraints or PartyConstraints(require_positive_party_gain=False)
    violations: list[PartyViolation] = []

    if candidate.total_landed_cost_cad <= 0:
        violations.append(PartyViolation("NONPOSITIVE_TOTAL_COST", "party loadout cost must be positive"))
    if (
        constraints.maximum_net_cost_cad is not None
        and candidate.total_landed_cost_cad > constraints.maximum_net_cost_cad
    ):
        violations.append(
            PartyViolation(
                "BUDGET_EXCEEDED",
                f"CAD {candidate.total_landed_cost_cad:.2f} > CAD {constraints.maximum_net_cost_cad:.2f}",
            )
        )
    if candidate.quality_score < constraints.minimum_quality_retention:
        violations.append(
            PartyViolation(
                "QUALITY_FLOOR",
                f"{candidate.quality_score:.3f} < {constraints.minimum_quality_retention:.3f}",
            )
        )
    if candidate.availability < constraints.minimum_party_availability:
        violations.append(
            PartyViolation(
                "AVAILABILITY_FLOOR",
                f"{candidate.availability:.3f} < {constraints.minimum_party_availability:.3f}",
            )
        )
    if (
        constraints.maximum_p95_latency_ms is not None
        and candidate.p95_latency_ms > constraints.maximum_p95_latency_ms
    ):
        violations.append(
            PartyViolation(
                "LATENCY_CEILING",
                f"{candidate.p95_latency_ms:.2f} > {constraints.maximum_p95_latency_ms:.2f} ms",
            )
        )
    if (
        constraints.maximum_added_power_watts is not None
        and candidate.power_watts is not None
        and candidate.power_watts > constraints.maximum_added_power_watts
    ):
        violations.append(
            PartyViolation(
                "POWER_CEILING",
                f"{candidate.power_watts:.1f} > {constraints.maximum_added_power_watts:.1f} W",
            )
        )
    if constraints.require_offline_capability and candidate.required_internet:
        violations.append(PartyViolation("INTERNET_DEPENDENCY", "party loadout cannot operate offline"))
    if (
        constraints.maximum_new_shared_failure_domains is not None
        and candidate.shared_failure_domains > constraints.maximum_new_shared_failure_domains
    ):
        violations.append(
            PartyViolation(
                "FAILURE_DOMAIN_LIMIT",
                f"{candidate.shared_failure_domains} > {constraints.maximum_new_shared_failure_domains}",
            )
        )
    if constraints.require_measured_evidence and candidate.evidence is not EvidenceStatus.MEASURED:
        violations.append(PartyViolation("MEASURED_EVIDENCE_REQUIRED", candidate.evidence.value))
    for detail in candidate.compatibility_violations:
        violations.append(PartyViolation("COMPATIBILITY", detail))

    if candidate.total_landed_cost_cad <= 0:
        raw_value = adjusted_value = None
    else:
        raw_value = candidate.accepted_tokens_per_s / candidate.total_landed_cost_cad
        adjusted_value = (
            raw_value
            * _EVIDENCE_MULTIPLIER[candidate.evidence]
            * candidate.availability
            * candidate.quality_score
        )

    return EvaluatedPartyLoadout(
        candidate=candidate,
        feasible=not violations,
        throughput_per_cad=raw_value,
        risk_adjusted_throughput_per_cad=adjusted_value,
        violations=tuple(violations),
    )


def rank_party_loadouts(
    candidates: Iterable[PartyLoadoutCandidate],
    constraints: PartyConstraints | None = None,
) -> list[EvaluatedPartyLoadout]:
    materialized = list(candidates)
    workloads = {candidate.workload_id for candidate in materialized}
    if len(workloads) > 1:
        raise ValueError("party loadouts require one shared workload_id")
    evaluated = [evaluate_party_loadout(candidate, constraints) for candidate in materialized]
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


def greatest_party_throughput_per_cad(
    candidates: Iterable[PartyLoadoutCandidate],
    constraints: PartyConstraints | None = None,
) -> EvaluatedPartyLoadout | None:
    return next((result for result in rank_party_loadouts(candidates, constraints) if result.feasible), None)
