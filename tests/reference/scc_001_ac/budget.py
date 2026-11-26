"""AC-3: five-partition budget with an isolated override partition (reference only).

R_execution + R_enforcement + R_audit + R_quarantine + R_override <= R_budget,
each partition a hard cap of its own, with R_override > 0 (rc1 AC-3). Nothing but the override path may draw on
R_override, so exhausting every other partition cannot starve the override.

Fault model F (the bound is claimed only while all four hold):
  F1 the principal's hardware root (the verifier) is operational
  F2 the override transport is available
  F3 the independent control plane is trustworthy
  F4 the attacker has not physically compromised the override mechanism
Under F, the override completes within t_verify + t_transport + t_apply
<= delta_t_max model ticks, independent of load in the other partitions and of
any active quarantine. Outside F the channel reports OUT_OF_FAULT_MODEL, claims
nothing, and leaves the system halted (fail closed, never fail open).
These are MODEL ticks, not measured latency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

PARTITIONS = ("execution", "enforcement", "audit", "quarantine", "override")


@dataclass(frozen=True)
class FaultModel:
    hardware_root_up: bool = True
    override_transport_up: bool = True
    control_plane_trustworthy: bool = True
    no_physical_compromise: bool = True

    def holds(self) -> bool:
        return all((self.hardware_root_up, self.override_transport_up,
                    self.control_plane_trustworthy, self.no_physical_compromise))


class PartitionedBudget:
    def __init__(self, r_budget: float, caps: dict) -> None:
        if set(caps) != set(PARTITIONS):
            raise ValueError("all five partitions must be declared")
        vals = list(caps.values()) + [r_budget]
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0
                   for v in vals):
            raise ValueError("non-finite or negative budget")
        if caps["override"] <= 0:
            raise ValueError("R_override must be > 0 (rc1 AC-3)")
        if sum(caps.values()) > r_budget:
            raise ValueError("partition caps exceed R_budget")
        self.r_budget = r_budget
        self.caps = dict(caps)
        self.used = {p: 0.0 for p in PARTITIONS}

    def free(self, partition: str) -> float:
        return self.caps[partition] - self.used[partition]

    def charge(self, partition: str, amount: float, path: str = "work") -> str:
        if partition not in self.caps:
            return "FAIL_CLOSED"
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or not math.isfinite(amount) \
                or amount < 0:
            return "FAIL_CLOSED"
        if partition == "override" and path != "override":
            return "DENY_OVERRIDE_PARTITION_ISOLATED"
        if self.used[partition] + amount > self.caps[partition]:
            return "PREEMPTIVE_FAIL_CLOSED"
        self.used[partition] += amount
        return "CONTINUE"

    def total_used(self) -> float:
        return sum(self.used.values())


class OverrideChannel:
    def __init__(self, budget: PartitionedBudget, gateway, *, delta_t_max: int = 5, t_verify: int = 1,
                 t_transport: int = 2, t_apply: int = 1, cost: float = 1.0) -> None:
        if t_verify + t_transport + t_apply > delta_t_max:
            raise ValueError("override bound not satisfiable under the declared path costs")
        self.budget = budget
        self.gateway = gateway
        self.delta_t_max = delta_t_max
        self.path_ticks = t_verify + t_transport + t_apply
        self.cost = cost

    def invoke(self, request, now: int, fault: FaultModel = FaultModel()):
        """Return (status, latency_ticks or None)."""
        if not fault.holds():
            return "OUT_OF_FAULT_MODEL", None
        charged = self.budget.charge("override", self.cost, path="override")
        if charged != "CONTINUE":
            return charged, None
        status = self.gateway.authorize(request, now)
        return status, self.path_ticks
