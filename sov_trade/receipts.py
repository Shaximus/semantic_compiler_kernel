"""Bilateral Verification Receipts (BVR)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .assertion import SignedAssertionEnvelope
from .canonical import canonical_json
from .crypto import ALG_ED25519, PublicKey, sha256, verify_signature
from .custody import KeyStore
from .identity import Principal
from .protocol import VerificationResult
from .types import ActorKind, ReasonCode, TradeError


@dataclass
class BilateralVerificationReceipt:
    fields: dict[str, Any]
    signatures: list[dict[str, str]] = field(default_factory=list)

    def payload(self) -> dict[str, Any]:
        return dict(self.fields)

    def to_dict(self) -> dict[str, Any]:
        body = dict(self.fields)
        body["signatures"] = list(self.signatures)
        return body

    def receipt_hash(self) -> str:
        return sha256(canonical_json(self.to_dict()))

    def signed_bytes(self) -> bytes:
        return canonical_json(self.payload())


def issue_receipt(
    envelope: SignedAssertionEnvelope,
    result: VerificationResult,
    *,
    verifier_id: str,
    issuer_domain: str,
    receiver_domain: str,
    now: int,
    skew: int,
    translation_hash: str | None,
    store: KeyStore,
    signer: Principal,
) -> BilateralVerificationReceipt:
    if signer.kind is ActorKind.VERIFIER_AGENT:
        raise TradeError(
            ReasonCode.VERIFIER_SIGNED_ASSERTION,
            "receipts are signed by the receiving institution, not the verifier agent",
        )
    fields = {
        "sae_hashes": [envelope.envelope_hash()],
        "translation_hash": translation_hash,
        "verifier_id": verifier_id,
        "issuer_domain": issuer_domain,
        "receiver_domain": receiver_domain,
        "checks": [c.to_dict() for c in result.checks],
        "bundle_version": result.bundle_version,
        "recognition_fingerprint": result.recognition_fingerprint,
        "timestamp": now,
        "skew_bound": skew,
        "outcome": result.outcome.value,
        "reasons": list(result.reasons),
    }
    receipt = BilateralVerificationReceipt(fields=fields, signatures=[])
    sig = store.sign(signer.key_id, receipt.signed_bytes(), now=now)
    receipt.signatures.append(
        {
            "party": "receiver",
            "algorithm": ALG_ED25519,
            "key_id": signer.key_id,
            "signature": sig.hex(),
        }
    )
    return receipt


def acknowledge_receipt(
    receipt: BilateralVerificationReceipt,
    store: KeyStore,
    signer: Principal,
    *,
    now: int,
) -> BilateralVerificationReceipt:
    """Issuing nation co-signs the receipt."""
    sig = store.sign(signer.key_id, receipt.signed_bytes(), now=now)
    receipt.signatures.append(
        {
            "party": "issuer",
            "algorithm": ALG_ED25519,
            "key_id": signer.key_id,
            "signature": sig.hex(),
        }
    )
    return receipt


def verify_receipt(
    receipt: BilateralVerificationReceipt,
    keys: dict[str, PublicKey],
    *,
    require_both_parties: bool = True,
) -> ReasonCode:
    payload = receipt.signed_bytes()
    parties = {s.get("party") for s in receipt.signatures}
    if require_both_parties and parties != {"receiver", "issuer"}:
        return ReasonCode.SIGNATURE_INVALID
    if not receipt.signatures:
        return ReasonCode.SIGNATURE_INVALID
    for sig in receipt.signatures:
        pub = keys.get(sig["key_id"])
        if pub is None:
            return ReasonCode.SIGNATURE_INVALID
        if not verify_signature(pub, payload, bytes.fromhex(sig["signature"])):
            return ReasonCode.SIGNATURE_INVALID
    return ReasonCode.OK
