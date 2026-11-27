"""SCC-001 data model: grants, trusted observations, traces, decisions.

REFERENCE ONLY. Every type is a frozen dataclass built from tuples and
frozensets, so the classifier receives read-only values and returns a
read-only decision. A Python object alone is not a security boundary
(see docs/SCC-001.md section 9).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConsentClass(str, Enum):
    """Relationship label. UNKNOWN is never treated as consent."""

    COERCIVE = "COERCIVE"      # Goa'uld pattern: verified authorization failure
    CONSENSUAL = "CONSENSUAL"  # Tok'ra pattern: verified grant, every hard rule clean
    UNKNOWN = "UNKNOWN"        # missing, unverifiable, conflicting or suspicious evidence


class ConsentState(str, Enum):
    """Operational state from Shax's t588u engineering text (section 1)."""

    AUTHORIZED = "AUTHORIZED"
    VIOLATION = "VIOLATION"
    SUSPICIOUS = "SUSPICIOUS"
    UNKNOWN = "UNKNOWN"
    REVOKED = "REVOKED"


class GrantStatus(str, Enum):
    VERIFIED = "VERIFIED"          # registry reachable, signature valid
    ABSENT = "ABSENT"              # registry reachable, verifiably no grant
    INVALID = "INVALID"            # registry reachable, signature or issuer invalid
    UNVERIFIABLE = "UNVERIFIABLE"  # registry or verifier unavailable


@dataclass(frozen=True)
class Grant:
    grant_id: str
    principal_id: str
    agent_id: str
    capabilities: frozenset
    resources: frozenset
    disclosed_effects: frozenset
    issued_at: int
    expires_at: int
    delegation_allowed: bool = False
    persistence_allowed: bool = False
    max_operations: int = 100


@dataclass(frozen=True)
class Event:
    """One observation. ``trusted`` means collected at an execution boundary.

    kinds: ``op`` (agent operation), ``revoke`` (principal withdraws the grant),
    ``deny`` (principal refuses a specific capability/resource), ``grant_change``
    (an attempt to alter the grant), ``request`` (agent asks the principal
    for a capability), ``delegate`` (agent spawns a child agent),
    ``persist`` (agent creates a credential, job or background process).
    A ``delegate`` event's capability, resource, effects and ``until`` describe
    the child's grant; it may only narrow the parent grant (SCC-001-AC AC-1).
    """

    seq: int
    t: int
    kind: str
    actor: str  # "agent" | "principal" | "admin"
    capability: str = ""
    resource: str = ""
    effects: tuple = ()
    trusted: bool = True
    until: Optional[int] = None  # ``delegate`` only: when the delegated authority ends


@dataclass(frozen=True)
class Trace:
    trace_id: str
    grant_status: GrantStatus
    grant: Optional[Grant]
    events: tuple
    synthetic: bool = True


@dataclass(frozen=True)
class ConsentDecision:
    """Output only: primitives and tuples, no reference back to participant state."""

    trace_id: str
    consent_class: ConsentClass
    state: ConsentState
    reason_codes: tuple
    rule_verdict: str
    advisory_risk: Optional[float]
    counterfactual: Optional[str]
    consent_vector: tuple  # C = (A, T, G, R, B); None where not measurable
    policy_version: str = "scc-001-ref-0.1.0"


def may_execute(decision: ConsentDecision) -> bool:
    """Only an AUTHORIZED decision may execute. REVOKED, UNKNOWN and SUSPICIOUS may not."""
    return decision.state is ConsentState.AUTHORIZED
