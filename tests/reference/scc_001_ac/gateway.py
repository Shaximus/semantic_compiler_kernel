"""Reference authority gateway for SCC-001-AC (reference only, not kernel enforcement).

Role edges follow the rc1 section-2 table and section-5 contract
(spec_contract.ALLOWED_ROLE_ACTIONS): the policy engine verifies, the supervisor
halts agents, the ML layer emits scores, agents execute, and only the principal
issues or revokes grants, writes policy, manifests or identity, or uses the
override. Delegation by anyone but the principal is GRANT_ISSUE and is denied.

Fixes the identity ambiguity t599u found in section 5: a role label is never
proof of identity. Authority-plane actions need a credential that the
independent verifier accepts for this exact request. Everything else is decided
from the identity registry and policy (I_reg, Pi), narrowed along registered
parent edges and the request's provenance chain. History, advisory scores and
policy-engine verdicts can only restrict, never grant.

Permitted transition relation (AC-2): a request r moves A to A' = delta(A, r)
only if r is an authority-plane action and the verifier returns VERIFIED for r.
Every other request leaves protected(A) unchanged; L_audit only grows.
"""

from __future__ import annotations

from dataclasses import replace

from tests.reference.scc_001_ac import flags
from tests.reference.scc_001_ac.identity import PrincipalVerifier, VerifyStatus
from tests.reference.scc_001_ac.model import (
    AUTHORITY_PLANE_ACTIONS,
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
    Role.POLICY_ENGINE.value: frozenset({Action.VERIFY_POLICY}),
    Role.SUPERVISOR.value: frozenset({Action.HALT}),
    Role.ML_ADVISORY.value: frozenset({Action.EMIT_ADVISORY_SCORE}),
    Role.AGENT.value: frozenset({Action.EXECUTE}),
}

ALLOW = "ALLOW"


def verdict(status: str) -> str:
    """Map a gateway status onto the rc1 verdict vocabulary (PERMIT / DENY_VIOLATION / FAIL_CLOSED)."""
    if status == ALLOW:
        return "PERMIT"
    if status.startswith("FAIL_CLOSED"):
        return "FAIL_CLOSED"
    return "DENY_VIOLATION"


class AuthorityGateway:
    def __init__(self, plane: AuthorityPlane, verifier: PrincipalVerifier) -> None:
        self.plane = plane
        self._verifier = verifier

    # ---- AC-1: effective capability with inheritance ----
    def effective_caps(self, actor_id: str, _seen: frozenset = frozenset()) -> frozenset:
        if actor_id in _seen:       # a parent cycle grants nothing
            return frozenset()
        role = self.plane.role(actor_id)
        if role is None:
            return frozenset()
        caps = self.plane.caps(actor_id) & ROLE_CEILING.get(role, frozenset())
        parent = self.plane.parent(actor_id)
        if parent is not None:
            caps &= self.effective_caps(parent, _seen | {actor_id})
        return caps

    def request_caps(self, req: Request) -> frozenset:
        """Indirect calls: a request can do only what every hop on its path can do."""
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
        if req.action is Action.HALT:
            if req.target in PROTECTED_HALT_TARGETS:
                return "DENY_PROTECTED_TARGET"
            if self.plane.role(req.target) != Role.AGENT.value:
                return "DENY_HALT_TARGET_NOT_AGENT"
        if req.action not in self.request_caps(req):
            return "DENY_OUT_OF_SCOPE"
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
        actor = req.actor_id if isinstance(req, Request) else repr(req)
        act = req.action.value if isinstance(req, Request) and isinstance(req.action, Action) else repr(req)
        target = req.target if isinstance(req, Request) else ""
        self.plane = self.plane.with_audit((now, actor, act, target, status))
        return status


def _delta(a: AuthorityPlane, req: Request) -> AuthorityPlane:
    pi = dict(a.pi)
    reg = dict(a.i_reg)
    parents = dict(a.parents)
    act = req.action
    p = req.payload
    if act is Action.GRANT_CAPABILITY:
        actor, caps = p
        pi[actor] = frozenset(caps)
    elif act is Action.REVOKE_CAPABILITY:
        (actor,) = p
        pi[actor] = frozenset()
    elif act is Action.SET_POLICY:
        pi = {k: frozenset(v) for k, v in p}
    elif act is Action.WRITE_MANIFEST:
        name, sha = p
        m = dict(a.manifests)
        m[name] = sha
        return replace(a, manifests=tuple(sorted(m.items())))
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
    else:
        return a  # authorization-only actions (OVERRIDE, RENEW/RELEASE, EXTEND_BUDGET, HALT, ...)
    return replace(a, pi=tuple(sorted(pi.items())), i_reg=tuple(sorted(reg.items())),
                   parents=tuple(sorted(parents.items())))
