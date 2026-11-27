"""Section 5 of the rc1 spec, verbatim ("Minimal Authority-Graph Audit Contract").

Copied unchanged from docs/evidence/source-2026-11-26c/SCC-001-AC_original.md
(sha256 d834c161...0737), plus a mapping from the reference gateway's actions
and roles onto it. ``is_authority_edge_permitted`` trusts ``actor_role`` as
given; t599u flags that as the identity ambiguity, so the reference gateway
never uses it to decide. Tests use it as the edge table the gateway must stay
inside, and to show that a forged label passes it.

After the verbatim block: the rc2 amendment Shax approved in t601u (a distinct
PRINCIPAL_KEY_ROTATE action, principal only), defined beside rc1 so the rc1
text stays byte-identical.
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


# --- rc2 amendment (Shax t601u; not part of the rc1 text) -------------------
# The section-2 table lets the principal "rotate K_P", but the rc1 section-5 enum
# has no rotate action. Shax resolved SCC-001-AC-KP-ROTATE in t601u: key rotation
# gets its own action, PRINCIPAL_KEY_ROTATE, instead of riding on POLICY_WRITE.
# The rc1 block above stays verbatim; the amended contract is defined beside it.
class AuthorityActionRC2(str, Enum):
    GRANT_ISSUE = "GRANT_ISSUE"
    GRANT_REVOKE = "GRANT_REVOKE"
    POLICY_WRITE = "POLICY_WRITE"
    IDENTITY_WRITE = "IDENTITY_WRITE"
    PRINCIPAL_OVERRIDE = "PRINCIPAL_OVERRIDE"
    PRINCIPAL_KEY_ROTATE = "PRINCIPAL_KEY_ROTATE"
    VERIFY_POLICY = "VERIFY_POLICY"
    HALT_OR_QUARANTINE = "HALT_OR_QUARANTINE"
    EMIT_ADVISORY_SCORE = "EMIT_ADVISORY_SCORE"


ALLOWED_ROLE_ACTIONS_RC2: dict = {
    role: frozenset(AuthorityActionRC2(a.value) for a in actions)
    | (frozenset({AuthorityActionRC2.PRINCIPAL_KEY_ROTATE}) if role is AuthorityRole.PRINCIPAL else frozenset())
    for role, actions in ALLOWED_ROLE_ACTIONS.items()
}


def is_authority_edge_permitted_rc2(actor_role: AuthorityRole, action: AuthorityActionRC2,
                                    target_is_authority_plane: bool, target_is_principal_override: bool) -> bool:
    """rc1 ``is_authority_edge_permitted`` over the amended action set (same rule, same label trust)."""
    if actor_role != AuthorityRole.PRINCIPAL:
        if target_is_authority_plane or target_is_principal_override:
            return False
    return action in ALLOWED_ROLE_ACTIONS_RC2.get(actor_role, frozenset())


# --- mapping (compiler-added, not part of the rc1 text) ---------------------
# Reference action -> (rc2 section-5 action or None, target_is_authority_plane, target_is_principal_override).
# None = not an authority edge (data-plane EXECUTE, or forbidden to all).
# ROTATE_PRINCIPAL_KEY maps to the distinct PRINCIPAL_KEY_ROTATE (Shax t601u); it
# was mapped to POLICY_WRITE before that decision.
def spec_edge(action_value: str):
    A = AuthorityActionRC2
    m = {
        "VERIFY_POLICY": (A.VERIFY_POLICY, False, False),
        "HALT": (A.HALT_OR_QUARANTINE, False, False),
        "EMIT_ADVISORY_SCORE": (A.EMIT_ADVISORY_SCORE, False, False),
        "EXECUTE": (None, False, False),
        "TRUNCATE_AUDIT": (None, True, False),
        "DELEGATE": (A.GRANT_ISSUE, True, False),
        "GRANT_CAPABILITY": (A.GRANT_ISSUE, True, False),
        "REVOKE_CAPABILITY": (A.GRANT_REVOKE, True, False),
        "SET_POLICY": (A.POLICY_WRITE, True, False),
        "WRITE_MANIFEST": (A.POLICY_WRITE, True, False),
        "ROTATE_PRINCIPAL_KEY": (A.PRINCIPAL_KEY_ROTATE, True, False),
        "REGISTER_IDENTITY": (A.IDENTITY_WRITE, True, False),
        "REVOKE_IDENTITY": (A.IDENTITY_WRITE, True, False),
        "MODIFY_OVERRIDE": (A.PRINCIPAL_OVERRIDE, True, True),
        "RENEW_QUARANTINE": (A.PRINCIPAL_OVERRIDE, False, True),
        "RELEASE_QUARANTINE": (A.PRINCIPAL_OVERRIDE, False, True),
        "EXTEND_BUDGET": (A.PRINCIPAL_OVERRIDE, False, True),
        "OVERRIDE": (A.PRINCIPAL_OVERRIDE, False, True),
    }
    return m[action_value]
