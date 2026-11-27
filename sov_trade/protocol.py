"""Bilateral exchange protocol: challenge, eight checks, policy decision."""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Any

from .assertion import (
    SAE_MAJOR,
    SignedAssertionEnvelope,
    verify_sae_signatures,
)
from .authority import DelegationRecord, DelegationScope
from .canonical import CanonicalizationError, canonical_json
from .clock import DEFAULT_SKEW_SECONDS, Clock
from .crypto import ALG_ED25519, PublicKey
from .identity import IdentityRegistry, domain_of
from .ledger import Ledger
from .status import DEFAULT_STATUS_FRESHNESS, StatusList, evaluate_status
from .types import CheckName, Outcome, ReasonCode


@dataclass
class Challenge:
    nonce: str
    txn_id: str
    verifier_domain: str
    issuer_domain: str
    issued_at: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "nonce": self.nonce,
            "txn_id": self.txn_id,
            "verifier_domain": self.verifier_domain,
            "issuer_domain": self.issuer_domain,
            "issued_at": self.issued_at,
        }


@dataclass
class CheckResult:
    name: CheckName
    passed: bool
    reason: ReasonCode

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name.value,
            "passed": self.passed,
            "reason": self.reason.value,
        }


@dataclass
class VerificationResult:
    checks: list[CheckResult]
    verification_passed: bool
    outcome: Outcome
    reasons: list[str]
    policy_notes: list[str] = field(default_factory=list)
    bundle_version: int | None = None
    recognition_fingerprint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [c.to_dict() for c in self.checks],
            "verification_passed": self.verification_passed,
            "outcome": self.outcome.value,
            "reasons": list(self.reasons),
            "policy_notes": list(self.policy_notes),
            "bundle_version": self.bundle_version,
            "recognition_fingerprint": self.recognition_fingerprint,
        }

    def reason_for(self, name: CheckName) -> ReasonCode | None:
        for check in self.checks:
            if check.name == name:
                return check.reason
        return None


def issue_challenge(
    *,
    verifier_domain: str,
    issuer_domain: str,
    txn_id: str,
    now: int,
) -> Challenge:
    return Challenge(
        nonce=secrets.token_hex(32),
        txn_id=txn_id,
        verifier_domain=verifier_domain,
        issuer_domain=issuer_domain,
        issued_at=now,
    )


def _check(name: CheckName, reason: ReasonCode) -> CheckResult:
    return CheckResult(name=name, passed=reason is ReasonCode.OK, reason=reason)


def _schema_check(envelope: SignedAssertionEnvelope) -> ReasonCode:
    fields = envelope.fields
    required = {
        "sae_version",
        "assertion_id",
        "domain",
        "doc_class",
        "subject",
        "claims",
        "evidence_refs",
        "issued_at",
        "not_before",
        "not_after",
        "txn_binding",
        "challenge",
        "authority_chain",
        "status_ref",
        "source_hash",
    }
    if not required <= set(fields):
        return ReasonCode.UNKNOWN_MAJOR_VERSION
    version = str(fields["sae_version"])
    try:
        major = int(version.split(".", 1)[0])
    except ValueError:
        return ReasonCode.UNKNOWN_MAJOR_VERSION
    if major != SAE_MAJOR:
        return ReasonCode.UNKNOWN_MAJOR_VERSION
    try:
        canonical_json(fields)
    except CanonicalizationError:
        return ReasonCode.CANONICAL_FORM_MISMATCH
    return ReasonCode.OK


def _validity_check(fields: dict[str, Any], now: int, skew: int) -> ReasonCode:
    try:
        not_before = int(fields["not_before"])
        not_after = int(fields["not_after"])
        issued_at = int(fields["issued_at"])
    except (KeyError, TypeError, ValueError):
        return ReasonCode.CANONICAL_FORM_MISMATCH
    # issued_at may legitimately sit well in the past (a still-valid
    # licence). CLOCK_DRIFT is reserved for a future-dated issuance
    # beyond the agreed skew. Window edges have their own reason codes.
    if issued_at - now > skew:
        return ReasonCode.CLOCK_DRIFT
    if now + skew < not_before:
        return ReasonCode.NOT_YET_VALID
    if now - skew >= not_after:
        return ReasonCode.EXPIRED
    return ReasonCode.OK


def _binding_check(
    fields: dict[str, Any],
    challenge: Challenge | None,
) -> ReasonCode:
    txn = fields.get("txn_binding") or {}
    if not isinstance(txn, dict):
        return ReasonCode.TXN_BINDING_MISMATCH
    if challenge is None:
        # Interactive flows require a challenge (spec section 5).
        if fields.get("challenge"):
            return ReasonCode.CHALLENGE_MISMATCH
        return ReasonCode.OK
    if fields.get("challenge") != challenge.nonce:
        return ReasonCode.CHALLENGE_MISMATCH
    if txn.get("txn_id") != challenge.txn_id:
        return ReasonCode.TXN_BINDING_MISMATCH
    if txn.get("counterparty_domain") != challenge.verifier_domain:
        return ReasonCode.TXN_BINDING_MISMATCH
    if fields.get("domain") != challenge.issuer_domain:
        return ReasonCode.TXN_BINDING_MISMATCH
    return ReasonCode.OK


def _scope_check(fields: dict[str, Any], verifier_domain: str) -> ReasonCode:
    chain = fields.get("authority_chain") or []
    if not isinstance(chain, list) or not chain:
        return ReasonCode.CHAIN_INVALID
    doc_class = fields["doc_class"]
    subject = fields.get("subject") or {}
    commodity = str(subject.get("commodity_code", ""))
    value = int(subject.get("value", 0))
    counterparty = str((fields.get("txn_binding") or {}).get("counterparty_domain", verifier_domain))
    # The envelope stores the chain leaf-to-root. Walk root-to-leaf so
    # each link can only narrow the grant above it.
    parent_scope: DelegationScope | None = None
    found_delegation = False
    links = [link for link in reversed(chain) if "root" not in link]
    for link in links:
        found_delegation = True
        try:
            rec = DelegationRecord(
                grantor=link["grantor"],
                grantee=link["grantee"],
                scope=DelegationScope.from_dict(link["scope"]),
                mode=link["mode"],
                not_before=int(link["not_before"]),
                not_after=int(link["not_after"]),
                serial=int(link["serial"]),
                emergency=bool(link.get("emergency", False)),
                signature=link.get("signature", ""),
                key_id=link.get("key_id", ""),
            )
        except (KeyError, TypeError, ValueError):
            return ReasonCode.CHAIN_INVALID
        if parent_scope is not None and not rec.scope.is_subset_of(parent_scope):
            return ReasonCode.SCOPE_WIDENED
        if not rec.scope.covers(doc_class, commodity, counterparty, value):
            return ReasonCode.DELEGATION_SCOPE
        parent_scope = rec.scope
    if not found_delegation:
        return ReasonCode.CHAIN_INVALID
    return ReasonCode.OK


def _chain_and_recognition(
    fields: dict[str, Any],
    identity: IdentityRegistry,
    now: int,
) -> tuple[ReasonCode, int | None, str | None]:
    issuer_domain = fields["domain"]
    if issuer_domain == identity.domain:
        return ReasonCode.CROSS_ISSUANCE, None, None
    rec = identity.recognition_for(issuer_domain)
    if rec is None:
        return ReasonCode.UNRECOGNIZED_ANCHOR, None, None
    # Find the institutional issuer in the chain (the first non-root
    # grantor's parent is the issuer, or a link grantor of kind ii).
    issuer_ids: list[str] = []
    try:
        for link in fields.get("authority_chain") or []:
            if not isinstance(link, dict):
                return ReasonCode.CHAIN_INVALID, rec.bundle_version, rec.bundle_fingerprint
            if "root" in link:
                root = link["root"]
                if not isinstance(root, dict) or "identifier" not in root:
                    return ReasonCode.CHAIN_INVALID, rec.bundle_version, rec.bundle_fingerprint
                if domain_of(root["identifier"]) != issuer_domain:
                    return ReasonCode.CROSS_ISSUANCE, rec.bundle_version, rec.bundle_fingerprint
                continue
            issuer_ids.append(link["grantor"])
            issuer_ids.append(link["grantee"])
    except (KeyError, TypeError, ValueError):
        return ReasonCode.CHAIN_INVALID, rec.bundle_version, rec.bundle_fingerprint
    # The institutional issuer is a grantor that appears in the recognition set.
    matched = [i for i in issuer_ids if i in rec.accepted_issuer_ids]
    if not matched:
        return ReasonCode.UNRECOGNIZED_ANCHOR, rec.bundle_version, rec.bundle_fingerprint
    cover = rec.covers(matched[0], fields["doc_class"], now)
    return cover, rec.bundle_version, rec.bundle_fingerprint


class VerifierAgent:
    """Local verifier. Holds no signing authority over assertions."""

    def __init__(
        self,
        identity: IdentityRegistry,
        ledger: Ledger,
        clock: Clock,
        *,
        skew: int = DEFAULT_SKEW_SECONDS,
        status_freshness: int = DEFAULT_STATUS_FRESHNESS,
    ) -> None:
        self.identity = identity
        self.ledger = ledger
        self.clock = clock
        self.skew = skew
        self.status_freshness = status_freshness
        self._replay: set[tuple[str, str]] = set()  # (assertion_id, txn_id)
        self.signing_assertions_forbidden = True

    def issue_challenge(self, *, issuer_domain: str, txn_id: str) -> Challenge:
        return issue_challenge(
            verifier_domain=self.identity.domain,
            issuer_domain=issuer_domain,
            txn_id=txn_id,
            now=self.clock.now_ts(),
        )

    def verify(
        self,
        envelope: SignedAssertionEnvelope,
        *,
        challenge: Challenge | None,
        keys: dict[str, PublicKey],
        status: StatusList | None,
        status_required: bool = True,
        policy_accept: bool | None = None,
        conditions: list[str] | None = None,
    ) -> VerificationResult:
        now = self.clock.now_ts()
        checks: list[CheckResult] = []

        if self.ledger.acceptance_halted:
            checks.append(_check(CheckName.CHAIN, ReasonCode.LEDGER_FORK))
            return VerificationResult(
                checks=checks,
                verification_passed=False,
                outcome=Outcome.REJECTED,
                reasons=[ReasonCode.LEDGER_FORK.value],
            )

        schema_reason = _schema_check(envelope)
        checks.append(_check(CheckName.SCHEMA, schema_reason))

        sig_reason = (
            verify_sae_signatures(envelope, keys)
            if schema_reason is ReasonCode.OK
            else ReasonCode.FAIL_CLOSED
        )
        checks.append(_check(CheckName.SIGNATURE, sig_reason))

        chain_reason, bundle_version, rec_fp = (
            _chain_and_recognition(envelope.fields, self.identity, now)
            if schema_reason is ReasonCode.OK
            else (ReasonCode.FAIL_CLOSED, None, None)
        )
        checks.append(_check(CheckName.CHAIN, chain_reason))

        scope_reason = (
            _scope_check(envelope.fields, self.identity.domain)
            if schema_reason is ReasonCode.OK
            else ReasonCode.FAIL_CLOSED
        )
        checks.append(_check(CheckName.SCOPE, scope_reason))

        window_reason = (
            _validity_check(envelope.fields, now, self.skew)
            if schema_reason is ReasonCode.OK
            else ReasonCode.FAIL_CLOSED
        )
        checks.append(_check(CheckName.VALIDITY_WINDOW, window_reason))

        status_reason = evaluate_status(
            status,
            envelope.fields.get("authority_chain", [{}])[0].get("grantee")
            if envelope.fields.get("authority_chain")
            else envelope.assertion_id,
            now=now,
            freshness=self.status_freshness,
            required=status_required,
        )
        # Also evaluate the operational signer (last non-root grantee).
        if status_reason is ReasonCode.OK:
            for link in envelope.fields.get("authority_chain") or []:
                if "grantee" in link:
                    status_reason = evaluate_status(
                        status,
                        link["grantee"],
                        now=now,
                        freshness=self.status_freshness,
                        required=status_required,
                    )
                    if status_reason is not ReasonCode.OK:
                        break
        checks.append(_check(CheckName.REVOCATION, status_reason))

        bind_reason = _binding_check(envelope.fields, challenge)
        checks.append(_check(CheckName.BINDING, bind_reason))

        txn_id = ""
        if isinstance(envelope.fields.get("txn_binding"), dict):
            txn_id = str(envelope.fields["txn_binding"].get("txn_id") or "")
        replay_key = (envelope.assertion_id, txn_id)
        if replay_key in self._replay:
            replay_reason = ReasonCode.REPLAYED
        else:
            replay_reason = ReasonCode.OK
        checks.append(_check(CheckName.REPLAY, replay_reason))

        failed = [c for c in checks if not c.passed]
        verification_passed = not failed

        # Fail-closed default: unknown facts are deferred, hard failures rejected.
        deferred_codes = {
            ReasonCode.STATUS_UNKNOWN,
            ReasonCode.STATUS_STALE,
        }
        if failed and all(c.reason in deferred_codes for c in failed):
            outcome = Outcome.DEFERRED
        elif failed:
            outcome = Outcome.REJECTED
        else:
            # A passing verification never forces acceptance (section 7).
            if policy_accept is False:
                outcome = Outcome.REJECTED
            elif conditions:
                outcome = Outcome.ACCEPTED_WITH_CONDITIONS
            elif policy_accept is None:
                # Caller has not made a policy decision; verification can
                # still stand alone. Default policy in this reference is
                # accept when verification passed (tests override).
                outcome = Outcome.ACCEPTED
            else:
                outcome = Outcome.ACCEPTED

        if verification_passed and outcome in {
            Outcome.ACCEPTED,
            Outcome.ACCEPTED_WITH_CONDITIONS,
        }:
            self._replay.add(replay_key)

        reasons = [c.reason.value for c in failed] or [ReasonCode.OK.value]
        return VerificationResult(
            checks=checks,
            verification_passed=verification_passed,
            outcome=outcome,
            reasons=reasons,
            policy_notes=list(conditions or []),
            bundle_version=bundle_version,
            recognition_fingerprint=rec_fp,
        )
