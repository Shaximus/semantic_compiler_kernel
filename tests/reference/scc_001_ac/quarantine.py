"""AC-5: bounded emergency halts, renewal and recovery (reference only).

- Only a supervisor may HALT, and only a registered V_Agent node: never the
  override channel, the principal, the authority plane, the verifier or another
  defensive component.
- Halts can bill R_quarantine. A supervisor looping halts exhausts that
  partition, never R_override (TEST-AC-ORACLE-D).
- A halt lasts at most t_q_max ticks. A monitor cannot renew it, and halting an
  already-halted target does not restart the clock (no self-renewal).
- Only a principal-verified RENEW_QUARANTINE extends it, by at most
  max_extension per renewal.
- Recovery (PROVISIONAL_DEFAULT): on expiry the monitor's hold lapses and the
  target moves to AWAITING_PRINCIPAL. The workload stays stopped (no automatic
  resumption, as in SC-MAFUBA-001D) and only a principal-verified
  RELEASE_QUARANTINE lets it run again. The override works in every state.
- Auto-quarantine from ML advisory is disabled (flags.AUTO_QUARANTINE_ENABLED).
"""

from __future__ import annotations

from enum import Enum

from tests.reference.scc_001_ac.model import Action, Request


class QuarantineState(str, Enum):
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    AWAITING_PRINCIPAL = "AWAITING_PRINCIPAL"
    RELEASED = "RELEASED"


class QuarantineController:
    def __init__(self, gateway, *, t_q_max: int = 10, max_extension: int = 10, budget=None,
                 halt_cost: float = 0.0) -> None:
        self.gateway = gateway
        self.budget = budget          # optional PartitionedBudget: halts bill R_quarantine
        self.halt_cost = halt_cost
        self.t_q_max = t_q_max
        self.max_extension = max_extension
        self._expires = {}
        self._released = set()

    def state(self, target: str, now: int) -> QuarantineState:
        if target in self._released:
            return QuarantineState.RELEASED
        if target not in self._expires:
            return QuarantineState.NONE
        return QuarantineState.ACTIVE if now < self._expires[target] else QuarantineState.AWAITING_PRINCIPAL

    def workload_may_run(self, target: str, now: int) -> bool:
        return self.state(target, now) in (QuarantineState.NONE, QuarantineState.RELEASED)

    def halt(self, req: Request, now: int) -> str:
        if req.action is not Action.HALT:
            return "FAIL_CLOSED"
        status = self.gateway.apply(req, now)
        if status != "ALLOW":
            return status
        st = self.state(req.target, now)
        if st in (QuarantineState.ACTIVE, QuarantineState.AWAITING_PRINCIPAL):
            return "NO_EXTENSION"
        if self.budget is not None:
            billed = self.budget.charge("quarantine", self.halt_cost)
            if billed != "CONTINUE":
                return billed
        self._released.discard(req.target)
        self._expires[req.target] = now + self.t_q_max
        return "HALTED"

    def renew(self, req: Request, now: int, ticks: int) -> str:
        if req.action is not Action.RENEW_QUARANTINE:
            return "FAIL_CLOSED"
        status = self.gateway.apply(req, now)
        if status != "ALLOW":
            return status
        if req.target not in self._expires or req.target in self._released:
            return "NOTHING_TO_RENEW"
        self._expires[req.target] = max(self._expires[req.target], now) + min(max(ticks, 0), self.max_extension)
        return "RENEWED"

    def release(self, req: Request, now: int) -> str:
        if req.action is not Action.RELEASE_QUARANTINE:
            return "FAIL_CLOSED"
        status = self.gateway.apply(req, now)
        if status != "ALLOW":
            return status
        self._released.add(req.target)
        return "RELEASED"

    def expires_at(self, target: str):
        return self._expires.get(target)
