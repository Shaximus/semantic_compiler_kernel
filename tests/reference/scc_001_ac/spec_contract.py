"""Section 5 of the rc1 spec, verbatim ("Minimal Authority-Graph Audit Contract").

Copied unchanged from docs/evidence/source-2026-11-26c/SCC-001-AC_original.md
(sha256 d834c161...0737), plus a mapping from the reference gateway's actions
and roles onto it. ``is_authority_edge_permitted`` trusts ``actor_role`` as
given; t599u flags that as the identity ambiguity, so the reference gateway
never uses it to decide. Tests use it as the edge table the gateway must stay
inside, and to show that a forged label passes it.
"""

from dataclasses import dataclass
from enum import Enum


class AuthorityRole(str, Enum):
    PRINCIPAL = "PRINCIPAL"
    POLICY_ENGINE = "POLICY_ENGINE"
    SUPERVISOR = "SUPERVISOR"
    ML_ADVISORY = "ML_ADVISORY"
    AGENT = "AGENT"


class AuthorityAction(str, Enum):
    GRANT_ISSUE = "GRANT_ISSUE"
    GRANT_REVOKE = "GRANT_REVOKE"
    POLICY_WRITE = "POLICY_WRITE"
    IDENTITY_WRITE = "IDENTITY_WRITE"
    PRINCIPAL_OVERRIDE = "PRINCIPAL_OVERRIDE"
    VERIFY_POLICY = "VERIFY_POLICY"
    HALT_OR_QUARANTINE = "HALT_OR_QUARANTINE"
    EMIT_ADVISORY_SCORE = "EMIT_ADVISORY_SCORE"


ALLOWED_ROLE_ACTIONS: dict[AuthorityRole, frozenset[AuthorityAction]] = {
    AuthorityRole.PRINCIPAL: frozenset({
        AuthorityAction.GRANT_ISSUE,
        AuthorityAction.GRANT_REVOKE,
        AuthorityAction.POLICY_WRITE,
        AuthorityAction.IDENTITY_WRITE,
        AuthorityAction.PRINCIPAL_OVERRIDE,
    }),
    AuthorityRole.POLICY_ENGINE: frozenset({
        AuthorityAction.VERIFY_POLICY,
    }),
    AuthorityRole.SUPERVISOR: frozenset({
        AuthorityAction.HALT_OR_QUARANTINE,
    }),
    AuthorityRole.ML_ADVISORY: frozenset({
        AuthorityAction.EMIT_ADVISORY_SCORE,
    }),
    AuthorityRole.AGENT: frozenset(),
}


@dataclass(frozen=True)
class AuthorityEdgeCheck:
    actor_role: AuthorityRole
    action: AuthorityAction
    target_is_authority_plane: bool
    target_is_principal_override: bool


def is_authority_edge_permitted(check: AuthorityEdgeCheck) -> bool:
    """Strict positive allowlist enforcing SCC-001-AC role separation."""
    if check.actor_role != AuthorityRole.PRINCIPAL:
        if check.target_is_authority_plane or check.target_is_principal_override:
            return False
    return check.action in ALLOWED_ROLE_ACTIONS.get(check.actor_role, frozenset())


# --- mapping (compiler-added, not part of the rc1 text) ---------------------
# Reference action -> (section-5 action or None, target_is_authority_plane, target_is_principal_override).
# None = not an authority edge (data-plane EXECUTE, or forbidden to all).
# ROTATE_PRINCIPAL_KEY: the section-2 table lets the principal rotate K_P, but the
# section-5 enum has no such action; it is mapped to POLICY_WRITE and recorded as
# a spec gap (PENDING_DELIBERATION SCC-001-AC-KP-ROTATE).
def spec_edge(action_value: str):
    m = {
        "VERIFY_POLICY": (AuthorityAction.VERIFY_POLICY, False, False),
        "HALT": (AuthorityAction.HALT_OR_QUARANTINE, False, False),
        "EMIT_ADVISORY_SCORE": (AuthorityAction.EMIT_ADVISORY_SCORE, False, False),
        "EXECUTE": (None, False, False),
        "TRUNCATE_AUDIT": (None, True, False),
        "DELEGATE": (AuthorityAction.GRANT_ISSUE, True, False),
        "GRANT_CAPABILITY": (AuthorityAction.GRANT_ISSUE, True, False),
        "REVOKE_CAPABILITY": (AuthorityAction.GRANT_REVOKE, True, False),
        "SET_POLICY": (AuthorityAction.POLICY_WRITE, True, False),
        "WRITE_MANIFEST": (AuthorityAction.POLICY_WRITE, True, False),
        "ROTATE_PRINCIPAL_KEY": (AuthorityAction.POLICY_WRITE, True, False),
        "REGISTER_IDENTITY": (AuthorityAction.IDENTITY_WRITE, True, False),
        "REVOKE_IDENTITY": (AuthorityAction.IDENTITY_WRITE, True, False),
        "MODIFY_OVERRIDE": (AuthorityAction.PRINCIPAL_OVERRIDE, True, True),
        "RENEW_QUARANTINE": (AuthorityAction.PRINCIPAL_OVERRIDE, False, True),
        "RELEASE_QUARANTINE": (AuthorityAction.PRINCIPAL_OVERRIDE, False, True),
        "EXTEND_BUDGET": (AuthorityAction.PRINCIPAL_OVERRIDE, False, True),
        "OVERRIDE": (AuthorityAction.PRINCIPAL_OVERRIDE, False, True),
    }
    return m[action_value]
