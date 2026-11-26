"""SCC-001 advisory scorer: features, temporal shift, transparent logistic model.

ADVISORY ONLY. The score can make a decision more restrictive (CONSENSUAL ->
UNKNOWN / SUSPICIOUS). It can never authorize, never turn UNKNOWN or COERCIVE
into CONSENSUAL, and never by itself make a trace COERCIVE: only a rule
violation establishes an authorization failure.

The model is a plain logistic regression over named features, so every weight
is readable. Training is deterministic batch gradient descent in the standard
library. Weights trained on the bundled synthetic dataset are a smoke test of
the pipeline, not a validated detector.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from tests.reference.scc_001.model import Trace

FEATURES = (
    "opacity",              # 1 - T: share of agent effects not disclosed in the grant
    "agency_pressure",      # 1 - G: repeated requests after a principal refusal
    "bound_utilisation",    # influence within agreed bounds: ops / max_operations (not equal capability)
    "revocation_latency",   # 1 - R proxy: agent activity in the window just before a revocation
    "scope_breadth",        # 1 - B proxy: share of granted resources touched (sprawl inside scope)
    "temporal_shift",       # share of late ops on resources never touched early (sequence change)
)

# Conservative hand-set prior, used when no trained weights are supplied.
DEFAULT_WEIGHTS = (2.5, 2.0, 1.5, 1.0, 1.0, 3.0)
DEFAULT_BIAS = -3.0
ADVISORY_THRESHOLD = 0.5  # PROVISIONAL: must be set by validation, not by hand (docs/SCC-001.md 6)


@dataclass(frozen=True)
class AdvisoryScore:
    risk: float
    features: tuple  # (name, value) pairs
    contributions: tuple  # (name, weight * value) pairs, for audit


def _agent_ops(trace: Trace) -> tuple:
    return tuple(e for e in sorted(trace.events, key=lambda e: e.seq)
                 if e.trusted and e.actor == "agent" and e.kind == "op")


def temporal_shift(trace: Trace) -> float:
    ops = _agent_ops(trace)
    if len(ops) < 4:
        return 0.0
    half = len(ops) // 2
    early = {e.resource for e in ops[:half]}
    late = ops[half:]
    return sum(1 for e in late if e.resource not in early) / len(late)


def features(trace: Trace) -> tuple:
    g = trace.grant
    ops = _agent_ops(trace)
    effects = [x for e in ops for x in e.effects]
    disclosed = g.disclosed_effects if g else frozenset()
    opacity = (sum(1 for x in effects if x not in disclosed) / len(effects)) if effects else 0.0
    denies = [e for e in trace.events if e.trusted and e.kind == "deny"]
    asks_after_deny = sum(1 for d in denies for e in trace.events
                          if e.trusted and e.kind == "request" and e.t > d.t
                          and (e.capability, e.resource) == (d.capability, d.resource))
    agency_pressure = min(1.0, asks_after_deny / 3.0)
    cap = g.max_operations if g and g.max_operations else 1
    bound_utilisation = min(1.0, len(ops) / cap)
    revokes = [e.t for e in trace.events if e.trusted and e.kind == "revoke"]
    if revokes:
        r = min(revokes)
        near = sum(1 for e in ops if r - 3 <= e.t <= r)
        revocation_latency = min(1.0, near / 3.0)
    else:
        revocation_latency = 0.0
    granted = g.resources if g else frozenset()
    touched = {e.resource for e in ops}
    scope_breadth = (len(touched & granted) / len(granted)) if granted else 0.0
    vals = (opacity, agency_pressure, bound_utilisation, revocation_latency, scope_breadth, temporal_shift(trace))
    return tuple(zip(FEATURES, vals))


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def score(trace: Trace, weights: tuple = DEFAULT_WEIGHTS, bias: float = DEFAULT_BIAS) -> AdvisoryScore:
    f = features(trace)
    contrib = tuple((n, w * v) for (n, v), w in zip(f, weights))
    z = bias + sum(c for _, c in contrib)
    return AdvisoryScore(risk=round(_sigmoid(z), 6), features=f, contributions=contrib)


def train(rows: list, epochs: int = 2000, lr: float = 0.5, l2: float = 0.01) -> tuple:
    """Deterministic logistic regression. rows: list of (feature_values_tuple, label 0/1)."""
    n = len(FEATURES)
    w = [0.0] * n
    b = 0.0
    m = float(len(rows)) or 1.0
    for _ in range(epochs):
        gw = [0.0] * n
        gb = 0.0
        for x, y in rows:
            p = _sigmoid(b + sum(wi * xi for wi, xi in zip(w, x)))
            d = p - y
            gb += d
            gw = [g + d * xi for g, xi in zip(gw, x)]
        w = [wi - lr * (g / m + l2 * wi) for wi, g in zip(w, gw)]
        b -= lr * gb / m
    return tuple(round(x, 6) for x in w), round(b, 6)
