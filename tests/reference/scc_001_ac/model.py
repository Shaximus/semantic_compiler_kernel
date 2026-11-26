"""Authority Plane model for SCC-001-AC (reference only).

Authority Plane A = (K_P, Pi, I_reg, C_override, L_audit):
  K_P        principal key identifiers (key material lives only in the verifier)
  Pi         policy: capabilities granted per registered actor id
  I_reg      identity registry: actor id -> registered role
  C_override the principal override channel configuration
  L_audit    append-only audit log
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional, Tuple


class Role(str, Enum):
    PRINCIPAL = "PRINCIPAL"
    MONITOR = "MONITOR"            # a member of V_Def (supervisor, classifier, auditor)
    AGENT = "AGENT"
    TOOL = "TOOL"
    POLICY_ENGINE = "POLICY_ENGINE"


class Action(str, Enum):
    # Defensive scope of V_Def (spec section 1: detect, evaluate, recommend, deny, halt).
    DETECT = "DETECT"
    EVALUATE = "EVALUATE"
    RECOMMEND = "RECOMMEND"
    DENY = "DENY"
    HALT = "HALT"
    # Ordinary work.
    EXECUTE = "EXECUTE"
    DELEGATE = "DELEGATE"
    # Authority-plane mutations (principal only, verified credential required).
    ROTATE_PRINCIPAL_KEY = "ROTATE_PRINCIPAL_KEY"    # K_P
    SET_POLICY = "SET_POLICY"                        # Pi
    GRANT_CAPABILITY = "GRANT_CAPABILITY"            # Pi
    REGISTER_IDENTITY = "REGISTER_IDENTITY"          # I_reg
    REVOKE_IDENTITY = "REVOKE_IDENTITY"              # I_reg
    MODIFY_OVERRIDE = "MODIFY_OVERRIDE"              # C_override
    RENEW_QUARANTINE = "RENEW_QUARANTINE"
    RELEASE_QUARANTINE = "RELEASE_QUARANTINE"
    EXTEND_BUDGET = "EXTEND_BUDGET"
    OVERRIDE = "OVERRIDE"
    # Forbidden to every role, including the principal (L_audit is append-only).
    TRUNCATE_AUDIT = "TRUNCATE_AUDIT"


DEFENSIVE_ACTIONS = frozenset({Action.DETECT, Action.EVALUATE, Action.RECOMMEND, Action.DENY, Action.HALT})

AUTHORITY_PLANE_ACTIONS = frozenset({
    Action.ROTATE_PRINCIPAL_KEY, Action.SET_POLICY, Action.GRANT_CAPABILITY,
    Action.REGISTER_IDENTITY, Action.REVOKE_IDENTITY, Action.MODIFY_OVERRIDE,
    Action.RENEW_QUARANTINE, Action.RELEASE_QUARANTINE, Action.EXTEND_BUDGET,
    Action.OVERRIDE,
})

NEVER_PERMITTED = frozenset({Action.TRUNCATE_AUDIT})

# AC-4: the explicit list of permissions that historical compliance (H_compliance)
# and any ML advisory score can never raise. Every authority-plane action, plus
# delegation and any change to the caller's own scope.
HISTORY_INSENSITIVE_PERMISSIONS = AUTHORITY_PLANE_ACTIONS | frozenset({Action.DELEGATE, Action.HALT})

# Targets a HALT may never name (AC-5): the override channel, the principal,
# the authority plane and the verifier.
PROTECTED_HALT_TARGETS = frozenset({"C_override", "principal", "authority_plane", "verifier"})


@dataclass(frozen=True)
class Credential:
    principal_id: str
    key_id: str
    issued_at: int
    expires_at: int
    nonce: str
    request_digest: str
    mac: str


@dataclass(frozen=True)
class Request:
    """A request to the authority gateway.

    ``actor_role`` is a CLAIMED label. It is recorded for audit and never used
    as proof of identity. ``via`` is the provenance chain of actor ids the
    request passed through (indirect tool calls, forwarding agents), outermost
    first. ``policy_verdict`` is an external policy engine's claim; it can
    only restrict. ``compliance_history`` and ``advisory_score`` are carried so
    tests can prove they have no effect (AC-4).
    """

    actor_id: str
    actor_role: str
    action: Action
    target: str = ""
    payload: Tuple = ()
    credential: Optional[Credential] = None
    via: Tuple[str, ...] = ()
    policy_verdict: Optional[str] = None
    compliance_history: float = 0.0
    advisory_score: Optional[float] = None
    source: str = "actor"   # "actor" | "ml_advisory"

    def digest(self) -> str:
        import hashlib
        body = "|".join([self.action.value, self.target, repr(self.payload)])
        return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AuthorityPlane:
    principal_id: str
    k_p: frozenset                     # key ids only
    pi: Tuple[Tuple[str, frozenset], ...]   # (actor_id, capabilities), sorted
    i_reg: Tuple[Tuple[str, str], ...]      # (actor_id, role), sorted
    parents: Tuple[Tuple[str, str], ...]    # (child_id, parent_id): delegation edges
    c_override: Tuple[Tuple[str, str], ...] = (("transport", "independent"),)
    l_audit: Tuple[Tuple, ...] = ()

    def caps(self, actor_id: str) -> frozenset:
        return dict(self.pi).get(actor_id, frozenset())

    def role(self, actor_id: str) -> Optional[str]:
        return dict(self.i_reg).get(actor_id)

    def parent(self, actor_id: str) -> Optional[str]:
        return dict(self.parents).get(actor_id)

    def protected(self) -> tuple:
        """Everything but the append-only log: what AC-2 protects from unauthorized change."""
        return (self.principal_id, self.k_p, self.pi, self.i_reg, self.parents, self.c_override)

    def with_audit(self, record: tuple) -> "AuthorityPlane":
        return replace(self, l_audit=self.l_audit + (record,))


def _sorted(d: dict) -> tuple:
    return tuple(sorted(d.items()))


def make_plane(principal_id: str, key_ids, pi: dict, i_reg: dict, parents: dict = None) -> AuthorityPlane:
    return AuthorityPlane(
        principal_id=principal_id,
        k_p=frozenset(key_ids),
        pi=_sorted({k: frozenset(v) for k, v in pi.items()}),
        i_reg=_sorted(i_reg),
        parents=_sorted(parents or {}),
    )
