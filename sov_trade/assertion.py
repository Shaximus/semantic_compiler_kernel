"""Signed Assertion Envelope (SAE)."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from typing import Any

from .canonical import CanonicalizationError, canonical_json
from .crypto import ALG_ED25519, PublicKey, sha256, verify_all_signatures
from .custody import KeyStore
from .identity import Principal, domain_of
from .types import ActorKind, ReasonCode, TradeError

SAE_VERSION = "1.0"
SAE_MAJOR = 1


def _uuid7() -> str:
    if hasattr(uuid, "uuid7"):
        return str(uuid.uuid7())
    # Minimal RFC 9562 UUIDv7 for Python 3.12 (CI).
    ts = int.from_bytes(os.urandom(0), "big")  # keep import used if clock injected
    import time

    unix_ms = int(time.time() * 1000)
    rand = int.from_bytes(os.urandom(10), "big")
    unix_ms &= 0xFFFFFFFFFFFF
    time_hi = (unix_ms >> 12) & 0xFFFFFFFF
    time_mid = unix_ms & 0xFFF
    # version 7
    a = (time_hi << 16) | (time_mid << 4) | 0x7
    # variant 10, 62 random bits packed into the rest — construct via UUID bytes
    b = bytearray(16)
    b[0:6] = unix_ms.to_bytes(6, "big")
    b[6] = 0x70 | ((rand >> 56) & 0x0F)
    b[7] = (rand >> 48) & 0xFF
    b[8] = 0x80 | ((rand >> 45) & 0x3F)
    b[9:16] = (rand & 0xFFFFFFFFFFFFFF).to_bytes(7, "big")
    return str(uuid.UUID(bytes=bytes(b)))


def make_assertion_id(issuer_prefix: str) -> str:
    return f"{issuer_prefix}:{_uuid7()}"


def salted_commitment(value: str, salt: bytes) -> str:
    return sha256(salt + b"|" + value.encode("utf-8"))


@dataclass
class Signature:
    algorithm: str
    key_id: str
    signature: str  # hex

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "signature": self.signature,
        }


@dataclass
class SignedAssertionEnvelope:
    fields: dict[str, Any]
    signatures: list[Signature] = field(default_factory=list)

    @property
    def assertion_id(self) -> str:
        return str(self.fields["assertion_id"])

    @property
    def domain(self) -> str:
        return str(self.fields["domain"])

    def unsigned_payload(self) -> dict[str, Any]:
        return dict(self.fields)

    def to_dict(self) -> dict[str, Any]:
        body = dict(self.fields)
        body["signatures"] = [s.to_dict() for s in self.signatures]
        return body

    def envelope_hash(self) -> str:
        return sha256(canonical_json(self.to_dict()))

    def signed_bytes(self) -> bytes:
        return canonical_json(self.unsigned_payload())


def build_sae_fields(
    *,
    issuer_prefix: str,
    domain: str,
    doc_class: str,
    subject: dict[str, Any],
    claims: list[dict[str, Any]],
    evidence_refs: list[dict[str, Any]],
    issued_at: int,
    not_before: int,
    not_after: int,
    txn_binding: dict[str, Any],
    challenge: str | None,
    authority_chain: list[dict[str, Any]],
    status_ref: dict[str, Any],
    source_hash: str,
    sae_version: str = SAE_VERSION,
    assertion_id: str | None = None,
) -> dict[str, Any]:
    return {
        "sae_version": sae_version,
        "assertion_id": assertion_id or make_assertion_id(issuer_prefix),
        "domain": domain,
        "doc_class": doc_class,
        "subject": subject,
        "claims": claims,
        "evidence_refs": evidence_refs,
        "issued_at": issued_at,
        "not_before": not_before,
        "not_after": not_after,
        "txn_binding": txn_binding,
        "challenge": challenge,
        "authority_chain": authority_chain,
        "status_ref": status_ref,
        "source_hash": source_hash,
    }


def sign_sae(
    fields: dict[str, Any],
    store: KeyStore,
    signer: Principal,
    *,
    now: int,
    extra_signers: list[tuple[Principal, KeyStore]] | None = None,
) -> SignedAssertionEnvelope:
    if signer.kind is ActorKind.NATIONAL_ROOT:
        raise TradeError(ReasonCode.ROOT_SIGNED_ASSERTION, "national root never signs assertions")
    if signer.kind is ActorKind.VERIFIER_AGENT:
        raise TradeError(
            ReasonCode.VERIFIER_SIGNED_ASSERTION,
            "verifier agent holds no signing authority over assertions",
        )
    if signer.kind is ActorKind.TRANSLATION_SIGNER:
        raise TradeError(
            ReasonCode.VERIFIER_SIGNED_ASSERTION,
            "translation layer holds no signing authority over assertions",
        )
    if domain_of(signer.identifier) != fields["domain"]:
        raise TradeError(ReasonCode.CROSS_ISSUANCE, "signer domain does not match envelope")
    # Reject floats early via canonicalization.
    try:
        payload = canonical_json(fields)
    except CanonicalizationError as exc:
        raise TradeError(ReasonCode.CANONICAL_FORM_MISMATCH, str(exc)) from exc
    env = SignedAssertionEnvelope(fields=dict(fields), signatures=[])
    signers = [(signer, store)] + list(extra_signers or [])
    for prin, ks in signers:
        sig = ks.sign(prin.key_id, payload, now=now)
        env.signatures.append(
            Signature(algorithm=ALG_ED25519, key_id=prin.key_id, signature=sig.hex())
        )
    return env


def verify_sae_signatures(
    envelope: SignedAssertionEnvelope,
    keys: dict[str, PublicKey],
) -> ReasonCode:
    try:
        payload = canonical_json(envelope.unsigned_payload())
    except CanonicalizationError:
        return ReasonCode.CANONICAL_FORM_MISMATCH
    if not envelope.signatures:
        return ReasonCode.SIGNATURE_INVALID
    triples = []
    for sig in envelope.signatures:
        pub = keys.get(sig.key_id)
        if pub is None:
            return ReasonCode.SIGNATURE_INVALID
        triples.append((pub, payload, bytes.fromhex(sig.signature)))
    if not verify_all_signatures(triples):
        return ReasonCode.HYBRID_INCOMPLETE if len(triples) > 1 else ReasonCode.SIGNATURE_INVALID
    return ReasonCode.OK
