"""Dispute handling against a BVR or assertion (section 12)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .assertion import SignedAssertionEnvelope
from .crypto import PublicKey, sha256
from .ledger import verify_inclusion_proof
from .protocol import VerifierAgent, Challenge
from .receipts import BilateralVerificationReceipt, verify_receipt
from .status import StatusList
from .types import ReasonCode


@dataclass
class Dispute:
    dispute_id: str
    opened_by: str
    target_hash: str
    target_kind: str  # bvr or sae
    opened_at: int
    notes: str = ""
    outcome: str | None = None
    failed_check: str | None = None
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dispute_id": self.dispute_id,
            "opened_by": self.opened_by,
            "target_hash": self.target_hash,
            "target_kind": self.target_kind,
            "opened_at": self.opened_at,
            "notes": self.notes,
            "outcome": self.outcome,
            "failed_check": self.failed_check,
            "reasons": list(self.reasons),
        }


def open_dispute(
    *,
    opened_by: str,
    target_hash: str,
    target_kind: str,
    now: int,
    notes: str = "",
) -> Dispute:
    ident = sha256(f"{opened_by}|{target_kind}|{target_hash}|{now}".encode("utf-8"))[:16]
    return Dispute(
        dispute_id=ident,
        opened_by=opened_by,
        target_hash=target_hash,
        target_kind=target_kind,
        opened_at=now,
        notes=notes,
    )


def resolve_dispute(
    dispute: Dispute,
    *,
    receipt: BilateralVerificationReceipt | None,
    envelope: SignedAssertionEnvelope | None,
    inclusion_a: dict[str, Any] | None,
    inclusion_b: dict[str, Any] | None,
    receipt_keys: dict[str, PublicKey],
    verifier: VerifierAgent | None = None,
    challenge: Challenge | None = None,
    keys: dict[str, PublicKey] | None = None,
    status_at_time: StatusList | None = None,
    # Re-run uses the archive clock (transaction time), not "now".
    transaction_time: int | None = None,
) -> Dispute:
    reasons: list[str] = []
    if inclusion_a is not None and not verify_inclusion_proof(inclusion_a):
        reasons.append("inclusion_proof_a_invalid")
    if inclusion_b is not None and not verify_inclusion_proof(inclusion_b):
        reasons.append("inclusion_proof_b_invalid")
    if receipt is not None:
        rec_reason = verify_receipt(receipt, receipt_keys, require_both_parties=False)
        if rec_reason is not ReasonCode.OK:
            reasons.append(rec_reason.value)
        if dispute.target_kind == "bvr" and receipt.receipt_hash() != dispute.target_hash:
            reasons.append("receipt_hash_mismatch")
    if verifier is not None and envelope is not None and keys is not None:
        # Re-run against the bundle and status as they stood at transaction time.
        # The verifier's clock is the injected clock; callers freeze it first.
        result = verifier.verify(
            envelope,
            challenge=challenge,
            keys=keys,
            status=status_at_time,
        )
        if not result.verification_passed:
            reasons.extend(result.reasons)
            failed = next((c for c in result.checks if not c.passed), None)
            dispute.failed_check = failed.name.value if failed else None
    dispute.reasons = reasons
    dispute.outcome = "contested" if reasons else "reproduced"
    # Liability is out of scope (section 12): the software records the
    # failed check, not who is liable.
    return dispute
