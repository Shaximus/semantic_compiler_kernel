"""Process-local reserve budget and emergency supervisor (reference only).

This is not cgroup v2 isolation and not kernel enforcement. It exists so
offline tests can check:

- free budget <= reserve => PREEMPTIVE_FAIL_CLOSED, never success
- the D2 shutdown path actually runs on the reserve: stop accepting work,
  terminate, isolate, keep bounded audit evidence, quarantine, and refuse
  automatic resumption

REFERENCE ONLY.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from tests.reference.sc_mafuba_001.allowlist import resolve_branch


@dataclass
class Worker:
    name: str
    running: bool = True
    isolated: bool = False

    def terminate(self) -> None:
        self.running = False


@dataclass
class ShutdownRecord:
    stopped_admissions: bool
    worker_terminated: bool
    isolated: bool
    evidence: bytes
    quarantined: bool
    automatic_resumption: bool
    reserve_used: float
    completed: bool = True
    status: str = "QUARANTINED"


@dataclass
class ResourceBudget:
    r_budget: float
    r_reserve: float
    r_used: float = 0.0
    accepting_work: bool = True

    @property
    def r_free(self) -> float:
        return self.r_budget - self.r_used

    def admit(self, amount: float) -> str:
        """Try to reserve `amount` for new work. Allowlist-compatible status."""
        if not self.accepting_work:
            return "PREEMPTIVE_FAIL_CLOSED"
        # NaN/inf/negative amounts must never be admitted: a NaN debit would
        # poison r_used and make every later comparison False (permanent fail-open).
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) \
                or not math.isfinite(amount) or amount < 0:
            return "FAIL_CLOSED"
        # Already at or below the reserve: stop, even for a zero-cost admit.
        if self.r_free <= self.r_reserve:
            return "PREEMPTIVE_FAIL_CLOSED"
        # Admission must leave the reserve untouched.
        if self.r_used + amount > (self.r_budget - self.r_reserve):
            return "PREEMPTIVE_FAIL_CLOSED"
        self.r_used += amount
        return "CONTINUE"


class EmergencySupervisor:
    """Owns the reserve conceptually; does not spend the worker budget."""

    def __init__(
        self,
        budget: ResourceBudget,
        max_evidence_bytes: int = 256,
        *,
        shutdown_fixed_cost: float = 0.5,
        evidence_cost_per_byte: float = 0.01,
    ) -> None:
        """shutdown_* are MODEL parameters (abstract resource units), not measured costs."""
        self.budget = budget
        self.max_evidence_bytes = max_evidence_bytes
        self.shutdown_fixed_cost = shutdown_fixed_cost
        self.evidence_cost_per_byte = evidence_cost_per_byte
        self.last_shutdown: Optional[ShutdownRecord] = None
        self._evidence: List[bytes] = []

    def stop_accepting_work(self) -> None:
        self.budget.accepting_work = False

    def run_shutdown(self, worker: Worker, evidence: bytes) -> ShutdownRecord:
        """D2 path: debits its cost from the reserve, and can fail if the reserve is too small.

        Stopping admissions and terminating the worker are modelled as zero-cost
        primitives that are ALWAYS attempted. Isolation and evidence retention are
        charged against the reserve; evidence shrinks to what the reserve affords,
        and if even the fixed cost is unaffordable the record says completed=False.
        """
        self.stop_accepting_work()
        worker.terminate()
        reserve = self.budget.r_reserve
        if self.shutdown_fixed_cost > reserve:
            record = ShutdownRecord(
                stopped_admissions=not self.budget.accepting_work,
                worker_terminated=not worker.running,
                isolated=False,
                evidence=b"",
                quarantined=True,
                automatic_resumption=False,
                reserve_used=reserve,
                completed=False,
                status="RESERVE_INSUFFICIENT",
            )
            self.last_shutdown = record
            return record
        affordable = int((reserve - self.shutdown_fixed_cost) / self.evidence_cost_per_byte) \
            if self.evidence_cost_per_byte > 0 else self.max_evidence_bytes
        bounded = evidence[: max(0, min(self.max_evidence_bytes, affordable))]
        worker.isolated = True
        self._evidence.append(bounded)
        cost = self.shutdown_fixed_cost + self.evidence_cost_per_byte * len(bounded)
        record = ShutdownRecord(
            stopped_admissions=not self.budget.accepting_work,
            worker_terminated=not worker.running,
            isolated=worker.isolated,
            evidence=bounded,
            quarantined=True,
            automatic_resumption=False,
            reserve_used=cost,
        )
        self.last_shutdown = record
        return record

    def try_resume(self) -> str:
        """Automatic resumption is forbidden."""
        return "QUARANTINE_LOCKED"

    def reserve_trigger_shutdown(self, worker: Worker, evidence: bytes) -> ShutdownRecord:
        """Drive the D2 scenario: consume down to the reserve, then shut down.

        Setting r_used = r_budget - r_reserve makes the next admit return
        PREEMPTIVE_FAIL_CLOSED. The shutdown handler then actually runs.
        """
        self.budget.r_used = self.budget.r_budget - self.budget.r_reserve
        status = self.budget.admit(0.0)
        branch, reason = resolve_branch(status)
        if branch != "HALT" or reason != "PREEMPTIVE_FAIL_CLOSED":
            raise AssertionError(
                f"reserve trigger must halt as PREEMPTIVE_FAIL_CLOSED, got {branch}/{reason}"
            )
        return self.run_shutdown(worker, evidence)
