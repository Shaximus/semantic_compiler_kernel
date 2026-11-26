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
        if amount < 0:
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

    def __init__(self, budget: ResourceBudget, max_evidence_bytes: int = 256) -> None:
        self.budget = budget
        self.max_evidence_bytes = max_evidence_bytes
        self.last_shutdown: Optional[ShutdownRecord] = None
        self._evidence: List[bytes] = []

    def stop_accepting_work(self) -> None:
        self.budget.accepting_work = False

    def run_shutdown(self, worker: Worker, evidence: bytes) -> ShutdownRecord:
        """D2 path: must be callable when only the reserve remains."""
        self.stop_accepting_work()
        bounded = evidence[: self.max_evidence_bytes]
        self._evidence.append(bounded)
        worker.terminate()
        worker.isolated = True
        # Quarantine is terminal in this reference model: no auto-resume.
        record = ShutdownRecord(
            stopped_admissions=not self.budget.accepting_work,
            worker_terminated=not worker.running,
            isolated=worker.isolated,
            evidence=bounded,
            quarantined=True,
            automatic_resumption=False,
            reserve_used=self.budget.r_reserve,
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
