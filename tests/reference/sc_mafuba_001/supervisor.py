"""Process-local reserve budget and emergency supervisor (reference only).

This is not cgroup v2 isolation and not kernel enforcement. It exists so
offline tests can check:

- admission is allowed only if R_execution + R_enforcement + R_reserve < R_budget
  (STRICT, a PROVISIONAL_DEFAULT with pending_deliberation); work that would
  land exactly on the reserve is refused with PREEMPTIVE_FAIL_CLOSED, is not
  billed, and the result carries needs_review / BOUNDARY_EDGE_PENDING_DELIBERATION
- if free budget ever reaches the reserve for any reason, the supervisor fires
  immediately (edge-driven defence in depth)
- the D2 shutdown path actually runs on the reserve: stop accepting work,
  terminate, isolate, keep bounded audit evidence, quarantine, and refuse
  automatic resumption
- an optional override partition (r_override, SCC-001-AC AC-3) is held apart
  from everything else: admission, enforcement, the shutdown reserve and
  direct counter writes cannot consume it; only draw_override(path="override")
  can

REFERENCE ONLY.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Optional

from tests.reference.sc_mafuba_001.allowlist import resolve_branch


@dataclass(frozen=True)
class AdmitResult:
    """Allowlist-compatible admission result.

    `status` is the value the allowlist branches on and must be passed as a
    plain str (type(status) is str). Equality with a string compares `status`
    only, so existing `assertEqual(result, "CONTINUE")` checks keep working.
    The STRICT equality edge also sets needs_review and diagnostic.
    """

    status: str
    needs_review: bool = False
    diagnostic: Optional[str] = None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AdmitResult):
            return (self.status, self.needs_review, self.diagnostic) == (
                other.status,
                other.needs_review,
                other.diagnostic,
            )
        if isinstance(other, str):
            return self.status == other
        return NotImplemented


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


class ResourceBudget:
    """Process-local budget: execution, enforcement, reserve, and an override partition.

    r_used is the derived sum of the execution and enforcement counters.
    The reserve is not billed by admit(); it is an untouchable envelope.
    r_override (keyword-only, default 0.0 = no partition, which keeps the
    three-term rc2 behaviour exactly) is reserved for the principal override
    path: ordinary admission is capped below r_budget - r_reserve - r_override,
    and only draw_override(path="override") can spend it.
    """

    def __init__(
        self,
        r_budget: float,
        r_reserve: float,
        r_used: float = 0.0,
        r_execution: Optional[float] = None,
        r_enforcement: float = 0.0,
        accepting_work: bool = True,
        *,
        r_override: float = 0.0,
    ) -> None:
        if not isinstance(r_override, (int, float)) or isinstance(r_override, bool) \
                or not math.isfinite(r_override) or r_override < 0:
            raise ValueError("r_override must be a finite number >= 0")
        self.r_budget = r_budget
        self.r_reserve = r_reserve
        self._r_override = float(r_override)
        self._r_override_used = 0.0
        self.r_enforcement = r_enforcement
        self.r_execution = r_used - r_enforcement if r_execution is None else r_execution
        self.accepting_work = accepting_work
        self.reserve_edge_handler: Optional[Callable[[], None]] = None

    @property
    def r_used(self) -> float:
        return self.r_execution + self.r_enforcement

    @r_used.setter
    def r_used(self, value: float) -> None:
        # Direct assignment is an accounting path other than admit(). If it
        # lands on or past the reserve, the edge-driven supervisor must fire
        # immediately (defence in depth).
        self.r_execution = value - self.r_enforcement
        self._fire_if_at_reserve()

    @property
    def r_override(self) -> float:
        """Capacity of the override partition (read-only after construction)."""
        return self._r_override

    @property
    def r_override_available(self) -> float:
        return self._r_override - self._r_override_used

    @property
    def r_free(self) -> float:
        # Ordinary free budget: the override partition is never part of it.
        return self.r_budget - self._r_override - self.r_used

    def draw_override(self, amount: float, path: str = "") -> str:
        """Spend from the override partition. Only the override path may draw."""
        if path != "override":
            return "DENY_OVERRIDE_PARTITION_ISOLATED"
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) \
                or not math.isfinite(amount) or amount < 0:
            return "FAIL_CLOSED"
        if self._r_override_used + amount > self._r_override:
            return "OVERRIDE_PARTITION_EXHAUSTED"
        self._r_override_used += amount
        return "CONTINUE"

    def _at_or_below_reserve(self) -> bool:
        return self.r_free <= self.r_reserve

    def _fire_if_at_reserve(self) -> None:
        if self._at_or_below_reserve() and self.reserve_edge_handler is not None:
            self.reserve_edge_handler()

    def admit(self, amount: float, purpose: str = "execution") -> AdmitResult:
        """Try to reserve `amount` for new work. Allowlist-compatible status.

        An admission is allowed only if, after the debit,
        R_execution + R_enforcement + R_reserve < R_budget. The STRICT
        equality-edge refusal is a provisional default: the result then also
        carries needs_review and BOUNDARY_EDGE_PENDING_DELIBERATION.
        Pass result.status to the allowlist (it requires type(status) is str).
        """
        if not self.accepting_work:
            return AdmitResult("PREEMPTIVE_FAIL_CLOSED")
        # NaN/inf/negative amounts must never be admitted: a NaN debit would
        # poison the counters and make every later comparison False (permanent fail-open).
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) \
                or not math.isfinite(amount) or amount < 0:
            return AdmitResult("FAIL_CLOSED")
        if purpose not in ("execution", "enforcement"):
            return AdmitResult("FAIL_CLOSED")
        # Already at or below the reserve: refuse and fire immediately.
        # This is observed state, not the open equality-vs-strict admit question.
        if self._at_or_below_reserve():
            self._fire_if_at_reserve()
            return AdmitResult("PREEMPTIVE_FAIL_CLOSED")
        # STRICT provisional default: refuse work that would land exactly on,
        # or past, the reserve. Do not bill, and do not fire the supervisor —
        # free has not reached the reserve; this is the admission gate, not
        # the edge trigger. The equality edge carries needs_review.
        cap = self.r_budget - self.r_reserve - self._r_override
        proposed = self.r_used + amount
        if proposed == cap:
            return AdmitResult(
                "PREEMPTIVE_FAIL_CLOSED",
                needs_review=True,
                diagnostic="BOUNDARY_EDGE_PENDING_DELIBERATION",
            )
        if proposed > cap:
            return AdmitResult("PREEMPTIVE_FAIL_CLOSED")
        if purpose == "execution":
            self.r_execution += amount
        else:
            self.r_enforcement += amount
        return AdmitResult("CONTINUE")


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
        self._armed_worker: Optional[Worker] = None
        self._armed_evidence: Optional[bytes] = None
        budget.reserve_edge_handler = self._on_reserve_edge

    def arm(self, worker: Worker, evidence: bytes) -> None:
        """Bind the worker and evidence the edge-driven trigger will shut down with."""
        self._armed_worker = worker
        self._armed_evidence = evidence

    def _on_reserve_edge(self) -> None:
        """Defence in depth: fire as soon as free budget reaches the reserve."""
        self.stop_accepting_work()
        if self.last_shutdown is not None:
            return
        if self._armed_worker is None:
            return
        self.run_shutdown(self._armed_worker, self._armed_evidence or b"")

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
        """Drive the D2 scenario: free reaches the reserve, supervisor fires immediately.

        Setting r_used so that r_free == r_reserve models the reserve being
        reached for a reason other than a successful admit. The edge-driven
        handler must shut down at that moment, not wait for a later admission.
        """
        self.arm(worker, evidence)
        self.budget.r_used = self.budget.r_budget - self.budget.r_reserve
        if self.last_shutdown is not None:
            return self.last_shutdown
        # Fallback if the edge hook was not attached: still refuse and shut down.
        result = self.budget.admit(0.0)
        branch, reason = resolve_branch(result.status)
        if branch != "HALT" or reason != "PREEMPTIVE_FAIL_CLOSED":
            raise AssertionError(
                f"reserve trigger must halt as PREEMPTIVE_FAIL_CLOSED, got {branch}/{reason}"
            )
        return self.run_shutdown(worker, evidence)
