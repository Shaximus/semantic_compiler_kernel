"""
Reflexion Semantic Compiler v2.0.0 — Authority Gate

Hard gate: deterministic authority lattice.
Archetype strength never grants authority.
Metaphor does not confer operational permission.

Citation: v1.0 Spec Section 3 — Authority Types
Citation: v1.0 Spec Section 15 — Role Compilation
Global Law: no_intuition_approval
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from semantic_compiler.core.types import AuthorityType

_ARCHETYPE_KEYWORDS_RE = re.compile(
    r"\b(?:powerful|strong|dragon|warrior|ancient|wise|legendary|supreme)\b",
    re.IGNORECASE,
)


def authority_transfer_digest(
    source_authority: str,
    claimed_authority: str,
    basis: str,
    has_task_scope: bool,
) -> str:
    """Canonical digest of one authority-transfer request.

    A principal credential for FOUNDER_OVERRIDE must be bound to this digest,
    so a credential issued for one transfer cannot be replayed on another.
    """
    body = json.dumps(
        {
            "source_authority": source_authority,
            "claimed_authority": claimed_authority,
            "basis": basis,
            "has_task_scope": bool(has_task_scope),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _verify_principal(verifier: Any, credential: Any, digest: str, now: Any) -> str:
    """Ask the independent principal verifier; fail closed on anything else.

    The verifier is configured by the deployment (it holds the principal key
    allowlist); the request supplies only the credential. A caller-set flag is
    never consulted. Returns "VERIFIED" or the reason it was not.
    """
    if verifier is None:
        return "NO_VERIFIER"
    verify = getattr(verifier, "verify_digest", None)
    if not callable(verify):
        return "NO_VERIFIER"
    if credential is None:
        return "NO_CREDENTIAL"
    if isinstance(now, bool) or not isinstance(now, int):
        return "NO_TIME"
    try:
        status = verify(credential, digest, now)
    except Exception:  # a broken verifier must never fail open
        return "VERIFIER_ERROR"
    return str(getattr(status, "value", status))


def check_authority_transfer(
    source_authority: str | AuthorityType,
    claimed_authority: str | AuthorityType,
    basis: str = "",
    has_explicit_delegation: bool = False,
    has_task_scope: bool = False,
    *,
    principal_credential: Any = None,
    principal_verifier: Any = None,
    now: Any = None,
) -> dict[str, Any]:
    """
    Check whether a claimed authority level is legitimate.

    HARD RULES:
    1. Archetype strength does not grant authority
    2. Metaphor strength does not grant authority
    3. Authority requires explicit delegation with task scope
    4. Temporary elevation must be logged, reversible, self-expiring

    5. FOUNDER_OVERRIDE requires an independently verified principal
       credential bound to this exact transfer (SCC-001-AC TEST-AC-06).
       has_explicit_delegation is caller-asserted and is ignored for it.

    Example failure:
        "Dragon is powerful, so Dragon may mutate Kairo."
        → ESCALATE (authority transfer without delegation)
    """
    # Resolve to enum
    if isinstance(source_authority, str):
        try:
            source_auth = AuthorityType[source_authority.upper()]
        except KeyError:
            source_auth = AuthorityType.NONE
    else:
        source_auth = source_authority

    if isinstance(claimed_authority, str):
        try:
            claimed_auth = AuthorityType[claimed_authority.upper()]
        except KeyError:
            claimed_auth = AuthorityType.NONE
    else:
        claimed_auth = claimed_authority

    gate_passed = True
    errors = []
    warnings = []
    requires_escalation = False

    # FOUNDER_OVERRIDE: the delegation must be proven by the principal's
    # credential, not asserted by the caller (SCC-001-AC identity capture path).
    principal_verification = None
    delegated = has_explicit_delegation
    if claimed_auth == AuthorityType.FOUNDER_OVERRIDE:
        principal_verification = _verify_principal(
            principal_verifier,
            principal_credential,
            authority_transfer_digest(source_auth.name, claimed_auth.name, basis, has_task_scope),
            now,
        )
        delegated = principal_verification == "VERIFIED"

    # Check if claimed authority exceeds source
    if claimed_auth > source_auth:
        if not delegated:
            gate_passed = False
            errors.append(
                f"Authority escalation from {source_auth.name} to "
                f"{claimed_auth.name} without explicit delegation."
            )
            requires_escalation = True
        elif not has_task_scope:
            gate_passed = False
            errors.append(
                "Authority elevation granted but not task-scoped. "
                "Temporary authority must be task-scoped, logged, "
                "reversible, and self-expiring."
            )

    # Check for archetype-based authority claims (word-boundary match so e.g.
    # "StrongBox" does not falsely trigger on "strong")
    if _ARCHETYPE_KEYWORDS_RE.search(basis):
        if claimed_auth > AuthorityType.RECOMMEND:
            gate_passed = False
            errors.append(
                f"Authority claim based on archetype/character strength: '{basis}'. "
                "Archetype strength never grants operational authority."
            )
            requires_escalation = True

    # FOUNDER_OVERRIDE requires an independently verified founder identity
    if claimed_auth == AuthorityType.FOUNDER_OVERRIDE:
        if not delegated:
            gate_passed = False
            errors.append(
                "FOUNDER_OVERRIDE claimed without founder delegation chain "
                f"(principal verification: {principal_verification}; "
                "has_explicit_delegation is caller-asserted and is not proof of identity)."
            )
            requires_escalation = True

    result = {
        "source_authority": source_auth.name,
        "claimed_authority": claimed_auth.name,
        "gate_passed": gate_passed,
        "requires_escalation": requires_escalation,
        "errors": errors,
        "warnings": warnings,
        "basis": basis,
    }
    if principal_verification is not None:
        result["principal_verification"] = principal_verification
    return result


def scan_approval_vectors(packet: Any) -> dict[str, Any]:
    """
    Scan a packet for approval requirements and authority vectors.

    Citation: v1.0 Spec Section 8, step 7
    """
    if hasattr(packet, "policy_overrides"):
        overrides = packet.policy_overrides
    else:
        overrides = packet.get("policy_overrides", [])

    requires_founder = False
    requires_named_approver = False
    supervised_only = False
    authority_findings = []

    for override in overrides:
        required_level = override.get("required_authority", "NONE")
        try:
            auth_level = AuthorityType[required_level.upper()]
        except KeyError:
            auth_level = AuthorityType.NONE

        if auth_level >= AuthorityType.FOUNDER_OVERRIDE:
            requires_founder = True
        elif auth_level >= AuthorityType.APPROVE:
            requires_named_approver = True
        elif auth_level >= AuthorityType.EXECUTE:
            supervised_only = True

        authority_findings.append({
            "override": override,
            "required_level": auth_level.name,
        })

    return {
        "requires_founder_authority": requires_founder,
        "requires_named_approver": requires_named_approver,
        "supervised_only": supervised_only,
        "authority_findings": authority_findings,
        "gate_status": "ESCALATE" if requires_founder else "PASSED",
    }
