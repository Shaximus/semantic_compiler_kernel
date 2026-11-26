"""Toy 1-D closed-form robust CBF (reference only, not kernel enforcement).

State x in R. Safe set h(x) = x_max - x >= 0 (stay at or below x_max).
Dynamics: xdot = u + d, |d| <= r_max, u in [-u_max, u_max].
alpha(h) = alpha_gain * h.

grad h = -1, so inf_{|d|<=r_max} (grad h)*d = -r_max,
and the robust CBF inequality reduces to:

    -u + alpha(h) - r_max >= 0
    i.e.  u <= alpha(h) - r_max

The filtered u is the projection of a nominal u_nom onto the
intersection of [-u_max, u_max] and (-inf, alpha(h) - r_max].
If that set is empty, the decision is FAIL_CLOSED (proven infeasible).

This helper does not simulate a QP solver timeout or a numerical
tolerance failure; those modes are still specified to fail closed at
runtime in v1.1.0-rc1. The offline tests of this helper assert the
feasible and proven-infeasible modes only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BarrierDecision:
    status: str
    u: Optional[float]
    h: float
    upper_bound: float


def toy_1d_robust_cbf(
    x: float,
    u_nom: float,
    *,
    x_max: float = 1.0,
    r_max: float = 0.2,
    u_max: float = 1.0,
    alpha_gain: float = 1.0,
) -> BarrierDecision:
    h = x_max - x
    upper = alpha_gain * h - r_max  # u must be <= upper
    # Feasible set: u in [-u_max, u_max] and u <= upper.
    feasible_hi = min(u_max, upper)
    feasible_lo = -u_max
    if feasible_lo > feasible_hi:
        return BarrierDecision(
            status="FAIL_CLOSED",
            u=None,
            h=h,
            upper_bound=upper,
        )
    u = min(max(u_nom, feasible_lo), feasible_hi)
    return BarrierDecision(status="CONTINUE", u=u, h=h, upper_bound=upper)
