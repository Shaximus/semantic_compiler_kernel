"""Authority Graph and Authority Plane model for SCC-001-AC (reference only).

Roles follow the original rc1 spec (section 2, docs/evidence/source-2026-11-26c/
SCC-001-AC_original.md): V = V_P | V_Pol | V_Sup | V_ML | V_Agent | V_Res, and
V_Def = V_Pol | V_Sup | V_ML. Protected resources and sinks (V_Res) are targets,
not actors, and are not registered as roles.

Authority Plane A = (K_P, Pi, I_reg, C_override, L_audit):
  K_P        principal key identifiers (key material lives only in the verifier)
  Pi         governing policies AND manifests: capabilities per actor id plus
             pinned manifest hashes (disturbance.yaml, resource.yaml, sink.yaml)
  I_reg      identity registry: actor id -> role, plus parent edges
  C_override the out-of-band principal override channel configuration
  L_audit    append-only audit ledger
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional, Tuple


class Role(str, Enum):
    PRINCIPAL = "PRINCIPAL"          # V_P
    POLICY_ENGINE = "POLICY_ENGINE"  # V_Pol (in V_Def)
    SUPERVISOR = "SUPERVISOR"        # V_Sup (in V_Def)
    ML_ADVISORY = "ML_ADVISORY"      # V_ML  (in V_Def)
    AGENT = "AGENT"                  # V_Agent (agents and tools)


V_DEF_ROLES = frozenset({Role.POLICY_ENGINE.value, Role.SUPERVISOR.value, Role.ML_ADVISORY.value})


class Action(str, Enum):
    # Defensive edges (section 2 table): verify, halt, emit an advisory score.
    VERIFY_POLICY = "VERIFY_POLICY"                  # V_Pol: emit PERMIT / DENY verdicts
    HALT = "HALT"                                    # V_Sup: halt / quarantine V_Agent only
    EMIT_ADVISORY_SCORE = "EMIT_ADVISORY_SCORE"      # V_ML: risk score M in [0, 1]
    # Data-plane work (not an authority edge).
    EXECUTE = "EXECUTE"
    # Minting a grant for another actor is GRANT_ISSUE in the section-5 contract,
    # which only the principal holds. Nobody else can delegate.
    DELEGATE = "DELEGATE"
    # Authority-plane mutations (principal only, verified credential required).
    ROTATE_PRINCIPAL_KEY = "ROTATE_PRINCIPAL_KEY"    # K_P
    SET_POLICY = "SET_POLICY"                        # Pi
    WRITE_MANIFEST = "WRITE_MANIFEST"                # Pi (manifests)
    GRANT_CAPABILITY = "GRANT_CAPABILITY"            # Pi
    REVOKE_CAPABILITY = "REVOKE_CAPABILITY"          # Pi
    REGISTER_IDENTITY = "REGISTER_IDENTITY"          # I_reg
    REVOKE_IDENTITY = "REVOKE_IDENTITY"              # I_reg
    MODIFY_OVERRIDE = "MODIFY_OVERRIDE"              # C_override
    RENEW_QUARANTINE = "RENEW_QUARANTINE"
    RELEASE_QUARANTINE = "RELEASE_QUARANTINE"
    EXTEND_BUDGET = "EXTEND_BUDGET"
    OVERRIDE = "OVERRIDE"
    # Forbidden to every role, including the principal (L_audit is append-only).
    TRUNCATE_AUDIT = "TRUNCATE_AUDIT"


DEFENSIVE_ACTIONS = frozenset({Action.VERIFY_POLICY, Action.HALT, Action.EMIT_ADVISORY_SCORE})

AUTHORITY_PLANE_ACTIONS = frozenset({
    Action.ROTATE_PRINCIPAL_KEY, Action.SET_POLICY, Action.WRITE_MANIFEST, Action.GRANT_CAPABILITY,
    Action.REVOKE_CAPABILITY, Action.REGISTER_IDENTITY, Action.REVOKE_IDENTITY, Action.MODIFY_OVERRIDE,
    Action.RENEW_QUARANTINE, Action.RELEASE_QUARANTINE, Action.EXTEND_BUDGET, Action.OVERRIDE,
})

NEVER_PERMITTED = frozenset({Action.TRUNCATE_AUDIT})

# AC-4: the explicit list of permissions that historical compliance (H_compliance)
# and any ML advisory score can never raise.
HISTORY_INSENSITIVE_PERMISSIONS = AUTHORITY_PLANE_ACTIONS | frozenset({Action.DELEGATE, Action.HALT})

# Targets a HALT may never name (AC-5), in addition to the rule that a HALT may
# only name a registered V_Agent node.
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

    ``actor_role`` is a CLAIMED label, recorded for audit and never used as
    proof of identity. ``via`` is the provenance chain of actor ids the request
    passed through (indirect tool calls, forwarding agents). ``policy_verdict``
    is an external policy engine's claim; it can only restrict.
    ``compliance_history`` and ``advisory_score`` are carried so tests can
    prove they have no effect (AC-4).
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
    source: str = "actor"   # "actor" | "ml_advisory" | "telemetry"

    def digest(self) -> str:
        body = "|".join([self.action.value, self.target, repr(self.payload)])
        return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AuthorityPlane:
    principal_id: str
    k_p: frozenset
    pi: Tuple[Tuple[str, frozenset], ...]
    i_reg: Tuple[Tuple[str, str], ...]
    parents: Tuple[Tuple[str, str], ...]
    manifests: Tuple[Tuple[str, str], ...] = ()     # (name, sha256): part of Pi
    c_override: Tuple[Tuple[str, str], ...] = (("transport", "independent"),)
    l_audit: Tuple[Tuple, ...] = ()

    def caps(self, actor_id: str) -> frozenset:
        return dict(self.pi).get(actor_id, frozenset())

    def role(self, actor_id: str) -> Optional[str]:
        return dict(self.i_reg).get(actor_id)

    def parent(self, actor_id: str) -> Optional[str]:
        return dict(self.parents).get(actor_id)

    def manifest_sha(self, name: str) -> Optional[str]:
        return dict(self.manifests).get(name)

    def protected(self) -> tuple:
        """Everything but the append-only log: what AC-2 protects from unauthorized change."""
        return (self.principal_id, self.k_p, self.pi, self.i_reg, self.parents, self.manifests, self.c_override)

    def digest(self) -> str:
        """Canonical digest of protected(A) (TEST-AC-02's 'canonical digest diff')."""
        canon = {
            "principal_id": self.principal_id,
            "k_p": sorted(self.k_p),
            "pi": [[a, sorted(c.value if isinstance(c, Enum) else str(c) for c in caps)] for a, caps in self.pi],
            "i_reg": [list(x) for x in self.i_reg],
            "parents": [list(x) for x in self.parents],
            "manifests": [list(x) for x in self.manifests],
            "c_override": [list(x) for x in self.c_override],
        }
        return hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

    def with_audit(self, record: tuple) -> "AuthorityPlane":
        return replace(self, l_audit=self.l_audit + (record,))


def _sorted(d: dict) -> tuple:
    return tuple(sorted(d.items()))


def make_plane(principal_id: str, key_ids, pi: dict, i_reg: dict, parents: dict = None,
               manifests: dict = None) -> AuthorityPlane:
    return AuthorityPlane(
        principal_id=principal_id,
        k_p=frozenset(key_ids),
        pi=_sorted({k: frozenset(v) for k, v in pi.items()}),
        i_reg=_sorted(i_reg),
        parents=_sorted(parents or {}),
        manifests=_sorted(manifests or {}),
    )
