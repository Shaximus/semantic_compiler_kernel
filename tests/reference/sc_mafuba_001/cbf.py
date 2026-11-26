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

Failure modes (all non-proceed, so all halt under allowlist branching):

    FAIL_CLOSED / PROVEN_INFEASIBLE   admissible set is empty
    FAIL_CLOSED / OUTSIDE_SAFE_SET    h(x) < 0 on entry; the CBF condition only
                                      guarantees forward invariance FROM INSIDE
                                      the safe set, so the state is not trusted
    NUMERICAL_TOLERANCE_FAILURE       any non-finite or ill-formed input

This helper does not simulate a QP solver timeout.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BarrierDecision:
    status: str
    u: Optional[float]
    h: float
    upper_bound: float
    reason: str = ""


def toy_1d_robust_cbf(
    x: float,
    u_nom: float,
    *,
    x_max: float = 1.0,
    r_max: float = 0.2,
    u_max: float = 1.0,
    alpha_gain: float = 1.0,
) -> BarrierDecision:
    params = (x, u_nom, x_max, r_max, u_max, alpha_gain)
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in params) \
            or r_max < 0 or u_max < 0 or alpha_gain < 0:
        return BarrierDecision(
            status="NUMERICAL_TOLERANCE_FAILURE",
            u=None,
            h=float("nan"),
            upper_bound=float("nan"),
            reason="NON_FINITE_OR_ILL_FORMED_INPUT",
        )
    h = x_max - x
    if h < 0:
        return BarrierDecision(
            status="FAIL_CLOSED",
            u=None,
            h=h,
            upper_bound=float("nan"),
            reason="OUTSIDE_SAFE_SET",
        )
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
            reason="PROVEN_INFEASIBLE",
        )
    u = min(max(u_nom, feasible_lo), feasible_hi)
    return BarrierDecision(status="CONTINUE", u=u, h=h, upper_bound=upper)
