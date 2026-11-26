"""SCC-001 Symbiotic Consent Classifier reference helpers.

REFERENCE ONLY. Not kernel enforcement, not loaded by the runtime router, not
packaged. Proposed / unvalidated, like SC-MAFUBA-001. See docs/SCC-001.md.
"""

from tests.reference.scc_001.classifier import classify
from tests.reference.scc_001.model import (
    ConsentClass,
    ConsentDecision,
    ConsentState,
    Event,
    Grant,
    GrantStatus,
    Trace,
    may_execute,
)

__all__ = [
    "classify", "ConsentClass", "ConsentDecision", "ConsentState",
    "Event", "Grant", "GrantStatus", "Trace", "may_execute",
]
