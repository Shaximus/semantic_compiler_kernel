"""Reference authority gateway for SCC-001-AC (reference only, not kernel enforcement).

Fixes the t599u section-5 ambiguity: a role label is never proof of identity.
Authority-plane actions need a credential that the independent verifier
accepts for this exact request. Everything else is decided from the identity
registry and policy (I_reg, Pi), narrowed along the delegation tree and the
request's provenance chain. History, advisory scores and policy-engine
verdicts can only restrict, never grant.

Permitted transition relation (AC-2). A request r moves the plane A to
A' = delta(A, r) only if:
  (a) r.action is an authority-plane action and the verifier returns VERIFIED
      for r (principal-authorized change), or
  (b) r.action is DELEGATE, DELEGATE is in r's effective capabilities, and the
      child's requested capabilities are a subset of them (narrowing only).
Every other request leaves protected(A) unchanged; L_audit only grows.
"""

from __future__ import annotations

from typing import Optional, Tuple

from tests.reference.scc_001_ac import flags
from tests.reference.scc_001_ac.identity import PrincipalVerifier, VerifyStatus
from tests.reference.scc_001_ac.model import (
    AUTHORITY_PLANE_ACTIONS,
    DEFENSIVE_ACTIONS,
    NEVER_PERMITTED,
    PROTECTED_HALT_TARGETS,
    Action,
    AuthorityPlane,
    Request,
    Role,
)

# Role ceilings: the most a registered role can ever hold, whatever Pi says.
ROLE_CEILING = {
    Role.PRINCIPAL.value: frozenset(),  # the principal acts through credentials, not Pi
    Role.MONITOR.value: DEFENSIVE_ACTIONS,
    Role.AGENT.value: frozenset({Action.EXECUTE, Action.DELEGATE, Action.RECOMMEND}),
    Role.TOOL.value: frozenset({Action.EXECUTE}),
    Role.POLICY_ENGINE.value: frozenset({Action.EVALUATE, Action.RECOMMEND}),
}

ALLOW = "ALLOW"


class AuthorityGateway:
    def __init__(self, plane: AuthorityPlane, verifier: PrincipalVerifier) -> None:
        self.plane = plane
        self._verifier = verifier

    # ---- AC-1: effective capability with delegation and inheritance ----
    def effective_caps(self, actor_id: str, _seen: Optional[frozenset] = None) -> frozenset:
        seen = _seen or frozenset()
        if actor_id in seen:       # a delegation cycle grants nothing
            return frozenset()
        role = self.plane.role(actor_id)
        if role is None:
            return frozenset()
        caps = self.plane.caps(actor_id) & ROLE_CEILING.get(role, frozenset())
        parent = self.plane.parent(actor_id)
        if parent is not None:
            caps &= self.effective_caps(parent, seen | {actor_id})
        return caps

    def request_caps(self, req: Request) -> frozenset:
        """Indirect calls: the request can do only what every hop on its path can do."""
        caps = self.effective_caps(req.actor_id)
        for hop in req.via:
            caps &= self.effective_caps(hop)
        return caps

    # ---- decision ----
    def authorize(self, req: Request, now: int) -> str:
        if not isinstance(req, Request) or not isinstance(req.action, Action) \
                or not isinstance(req.actor_id, str) or not isinstance(req.actor_role, str):
            return "FAIL_CLOSED"
        if req.action in NEVER_PERMITTED:
            return "DENY_NEVER_PERMITTED"
        if req.source != "actor" and not flags.AUTO_QUARANTINE_ENABLED:
            return "DENY_ML_ADVISORY_DISABLED"
        if req.action in AUTHORITY_PLANE_ACTIONS:
            # Role label, forwarding hops and policy verdicts are not consulted:
            # only the independent verifier can authorize a plane change.
            status = self._verifier.verify(req, now)
            if status is VerifyStatus.VERIFIED:
                return ALLOW
            if status is VerifyStatus.UNAVAILABLE:
                return "FAIL_CLOSED"
            return "DENY_PRINCIPAL_" + status.value
        role = self.plane.role(req.actor_id)
        if role is None:
            return "DENY_UNREGISTERED"
        if req.actor_role != role:
            return "DENY_ROLE_LABEL_MISMATCH"
        if req.action is Action.HALT and req.target in PROTECTED_HALT_TARGETS:
            return "DENY_PROTECTED_TARGET"
        if req.action not in self.request_caps(req):
            return "DENY_OUT_OF_SCOPE"
        if req.action is Action.DELEGATE:
            if not (isinstance(req.payload, tuple) and len(req.payload) == 2 and isinstance(req.payload[0], str)):
                return "FAIL_CLOSED"
            child_caps = req.payload[1]
            if self.plane.role(req.payload[0]) is not None:
                return "DENY_DELEGATION_TARGET_EXISTS"
            if not frozenset(child_caps) <= self.request_caps(req):
                return "DENY_DELEGATION_EXCEEDS_PARENT"
        if req.policy_verdict is not None and req.policy_verdict != ALLOW:
            return "DENY_POLICY"    # a policy verdict can restrict, never grant
        return ALLOW

    # ---- transition ----
    def apply(self, req: Request, now: int) -> str:
        status = self.authorize(req, now)
        if status == ALLOW:
            try:
                self.plane = _delta(self.plane, req)
            except (TypeError, ValueError):
                status = "FAIL_CLOSED_MALFORMED_PAYLOAD"
        self.plane = self.plane.with_audit((now, req.actor_id, req.action.value, req.target, status))
        return status


def _delta(a: AuthorityPlane, req: Request) -> AuthorityPlane:
    from dataclasses import replace
    pi = dict(a.pi)
    reg = dict(a.i_reg)
    parents = dict(a.parents)
    act = req.action
    p = req.payload
    if act is Action.GRANT_CAPABILITY:
        actor, caps = p
        pi[actor] = frozenset(caps)
    elif act is Action.SET_POLICY:
        pi = {k: frozenset(v) for k, v in p}
    elif act is Action.REGISTER_IDENTITY:
        actor, role, parent = p
        reg[actor] = role
        if parent:
            parents[actor] = parent
    elif act is Action.REVOKE_IDENTITY:
        (actor,) = p
        reg.pop(actor, None)
        pi.pop(actor, None)
    elif act is Action.ROTATE_PRINCIPAL_KEY:
        (key_id,) = p
        return replace(a, k_p=a.k_p | {key_id})
    elif act is Action.MODIFY_OVERRIDE:
        k, v = p
        co = dict(a.c_override)
        co[k] = v
        return replace(a, c_override=tuple(sorted(co.items())))
    elif act is Action.DELEGATE:
        child, caps = p
        reg[child] = a.role(req.actor_id)
        parents[child] = req.actor_id
        pi[child] = frozenset(caps)
    else:
        return a  # authorization-only actions (OVERRIDE, RENEW/RELEASE, EXTEND_BUDGET, HALT, ...)
    return replace(a, pi=tuple(sorted(pi.items())), i_reg=tuple(sorted(reg.items())),
                   parents=tuple(sorted(parents.items())))


# ---------------------------------------------------------------------------
# The check as quoted in t599u (spec section 5), kept only so TEST-AC-06 can
# show why it was replaced. ALLOWED_ROLE_ACTIONS is reconstructed: the spec's
# own table was not available to the compiler. DO NOT USE FOR ENFORCEMENT.
# ---------------------------------------------------------------------------
SPEC_SECTION5_ALLOWED_ROLE_ACTIONS = {
    Role.PRINCIPAL: AUTHORITY_PLANE_ACTIONS | DEFENSIVE_ACTIONS | {Action.EXECUTE},
    Role.MONITOR: DEFENSIVE_ACTIONS,
    Role.AGENT: frozenset({Action.EXECUTE}),
}


def spec_section5_role_label_check(actor_role: Role, action: Action, target_is_authority_plane: bool,
                                   target_is_principal_override: bool) -> bool:
    if actor_role != Role.PRINCIPAL:
        if target_is_authority_plane or target_is_principal_override:
            return False
    return action in SPEC_SECTION5_ALLOWED_ROLE_ACTIONS.get(actor_role, frozenset())
