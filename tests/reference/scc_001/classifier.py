"""SCC-001 Symbiotic Consent Classifier, reference pipeline.

rule engine (authoritative) -> advisory scorer -> counterfactual -> aggregator.
Pure function of frozen inputs; returns a frozen ConsentDecision. It holds no
registry handle and exposes no grant, revoke or enforcement call, so it has no
write path to the participants it evaluates. Not wired into runtime routing.
"""

from __future__ import annotations

from typing import Optional

from tests.reference.scc_001 import rules, scorer
from tests.reference.scc_001.aggregator import AgentFn, aggregate, counterfactual
from tests.reference.scc_001.model import ConsentDecision, Trace


def classify(trace: Trace, *, weights: tuple = scorer.DEFAULT_WEIGHTS, bias: float = scorer.DEFAULT_BIAS,
             agent_fn: Optional[AgentFn] = None, threshold: float = scorer.ADVISORY_THRESHOLD,
             advisory_override: Optional[float] = None) -> ConsentDecision:
    """Classify one trace.

    ``advisory_override`` lets tests inject any advisory risk (e.g. a perfect
    "trust me" 0.0) to prove the score cannot override the rules.
    """
    rr = rules.evaluate(trace)
    adv = scorer.score(trace, weights, bias)
    if advisory_override is not None:
        adv = scorer.AdvisoryScore(risk=advisory_override, features=adv.features, contributions=adv.contributions)
    cf = counterfactual(agent_fn, trace)
    return aggregate(trace, rr, adv, cf, threshold)
