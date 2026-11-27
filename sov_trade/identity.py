"""Sovereign identity, trust bundles and recognition records.

Identifiers are DID-style (PROVISIONAL_DEFAULT; section 16 leaves the
credential model open): ``did:sov:{domain}:{kind}:{local}``.
Recognition is stored only in the recognizing nation's domain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .canonical import canonical_json
from .crypto import sha256, verify_signature
from .custody import KeyStore, Officer
from .types import ActorKind, DocClass, ReasonCode, Role, TradeError


def make_did(domain: str, kind: ActorKind | str, local: str) -> str:
    kind_value = kind.value if isinstance(kind, ActorKind) else kind
    if ":" in domain or "/" in domain or not domain:
        raise ValueError("invalid domain")
    if ":" in local or "/" in local or not local:
        raise ValueError("invalid local identifier")
    return f"did:sov:{domain}:{kind_value}:{local}"


def domain_of(identifier: str) -> str:
    parts = identifier.split(":")
    if len(parts) != 5 or parts[0] != "did" or parts[1] != "sov":
        raise ValueError(f"not a did:sov identifier: {identifier}")
    return parts[2]


@dataclass
class Principal:
    identifier: str
    kind: ActorKind
    domain: str
    key_id: str
    public_hex: str
    parent: str | None = None  # identifier of the issuer that created this principal

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "kind": self.kind.value,
            "domain": self.domain,
            "key_id": self.key_id,
            "public_hex": self.public_hex,
            "parent": self.parent,
        }


@dataclass
class TrustBundle:
    """Signed publication of a nation's root and institutional registry."""

    domain: str
    version: int
    root: dict[str, Any]
    issuers: list[dict[str, Any]]
    issued_at: int
    signature: str = ""
    key_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "version": self.version,
            "root": self.root,
            "issuers": self.issuers,
            "issued_at": self.issued_at,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload()
        body["signature"] = self.signature
        body["key_id"] = self.key_id
        return body

    def fingerprint(self) -> str:
        return sha256(canonical_json(self.payload()))


@dataclass
class RecognitionRecord:
    """Held only by the recognizing nation. Not a grant in the grantor's domain."""

    recognizer_domain: str
    recognized_domain: str
    bundle_version: int
    bundle_fingerprint: str
    accepted_issuer_ids: list[str]
    accepted_doc_classes: list[str]
    not_before: int
    not_after: int
    withdrawn: bool = False
    withdrawn_at: int | None = None
    signature: str = ""
    key_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "recognizer_domain": self.recognizer_domain,
            "recognized_domain": self.recognized_domain,
            "bundle_version": self.bundle_version,
            "bundle_fingerprint": self.bundle_fingerprint,
            "accepted_issuer_ids": list(self.accepted_issuer_ids),
            "accepted_doc_classes": list(self.accepted_doc_classes),
            "not_before": self.not_before,
            "not_after": self.not_after,
            "withdrawn": self.withdrawn,
            "withdrawn_at": self.withdrawn_at,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload()
        body["signature"] = self.signature
        body["key_id"] = self.key_id
        return body

    def covers(
        self,
        issuer_id: str,
        doc_class: DocClass | str,
        now: int,
    ) -> ReasonCode:
        if self.withdrawn:
            return ReasonCode.RECOGNITION_WITHDRAWN
        if now < self.not_before:
            return ReasonCode.NOT_YET_VALID
        if now >= self.not_after:
            return ReasonCode.EXPIRED
        if issuer_id not in self.accepted_issuer_ids:
            return ReasonCode.UNRECOGNIZED_ANCHOR
        klass = doc_class.value if isinstance(doc_class, DocClass) else doc_class
        if klass not in self.accepted_doc_classes:
            return ReasonCode.RECOGNITION_SCOPE
        return ReasonCode.OK


@dataclass
class IdentityRegistry:
    domain: str
    store: KeyStore
    principals: dict[str, Principal] = field(default_factory=dict)
    bundle_version: int = 0
    # Recognition records this nation has issued about others.
    recognitions: dict[str, RecognitionRecord] = field(default_factory=dict)
    # Bundles received (authenticated out of band in this reference by signature).
    received_bundles: dict[str, TrustBundle] = field(default_factory=dict)

    def add_principal(self, principal: Principal) -> None:
        if principal.domain != self.domain:
            raise TradeError(ReasonCode.CROSS_ISSUANCE, "principal belongs to another domain")
        self.principals[principal.identifier] = principal

    def create_principal(
        self,
        kind: ActorKind,
        local: str,
        first: Officer,
        second: Officer,
        *,
        parent: str | None,
        expires_at: int | None = None,
    ) -> Principal:
        identifier = make_did(self.domain, kind, local)
        rec = self.store.generate_key(
            identifier, kind, first, second, expires_at=expires_at
        )
        principal = Principal(
            identifier=identifier,
            kind=kind,
            domain=self.domain,
            key_id=rec.key_id,
            public_hex=rec.public.public_hex(),
            parent=parent,
        )
        if kind is ActorKind.NATIONAL_ROOT and parent is not None:
            raise TradeError(ReasonCode.CHAIN_INVALID, "national root has no parent")
        # Translation signers have no delegation chain to a national root (section 9).
        if kind is ActorKind.TRANSLATION_SIGNER and parent is not None:
            raise TradeError(ReasonCode.CHAIN_INVALID, "translation signer must not chain to a root")
        if kind not in {ActorKind.NATIONAL_ROOT, ActorKind.TRANSLATION_SIGNER} and parent is None:
            raise TradeError(ReasonCode.CHAIN_INVALID, "non-root principal needs a parent")
        self.add_principal(principal)
        return principal

    def publish_bundle(self, root_id: str, first: Officer, second: Officer, *, now: int) -> TrustBundle:
        self.store.require_dual_control(first, second, frozenset({Role.APPROVE, Role.DEPLOY}))
        root = self.principals[root_id]
        if root.kind is not ActorKind.NATIONAL_ROOT:
            raise TradeError(ReasonCode.CHAIN_INVALID, "bundle must be signed by the national root")
        issuers = [
            p.to_public_dict()
            for p in self.principals.values()
            if p.kind is ActorKind.INSTITUTIONAL_ISSUER
        ]
        self.bundle_version += 1
        bundle = TrustBundle(
            domain=self.domain,
            version=self.bundle_version,
            root=root.to_public_dict(),
            issuers=issuers,
            issued_at=now,
            key_id=root.key_id,
        )
        sig = self.store.sign(root.key_id, canonical_json(bundle.payload()), now=now)
        bundle.signature = sig.hex()
        return bundle

    def receive_bundle(self, bundle: TrustBundle, *, expected_fingerprint: str | None = None) -> None:
        """Store a foreign bundle after checking its signature and fingerprint.

        The 'ceremony' in this reference is: the caller supplies the bundle
        and may pin the expected fingerprint (out-of-band check).
        """
        if bundle.domain == self.domain:
            raise TradeError(ReasonCode.CROSS_ISSUANCE, "cannot receive own bundle as foreign")
        payload = canonical_json(bundle.payload())
        from .crypto import PublicKey, ALG_ED25519

        pub = PublicKey(algorithm=ALG_ED25519, public_key=bytes.fromhex(bundle.root["public_hex"]))
        if not verify_signature(pub, payload, bytes.fromhex(bundle.signature)):
            raise TradeError(ReasonCode.SIGNATURE_INVALID, "trust bundle signature failed")
        if expected_fingerprint is not None and bundle.fingerprint() != expected_fingerprint:
            raise TradeError(ReasonCode.CANONICAL_FORM_MISMATCH, "trust bundle fingerprint mismatch")
        self.received_bundles[bundle.domain] = bundle

    def recognize(
        self,
        foreign_domain: str,
        first: Officer,
        second: Officer,
        signer_id: str,
        *,
        accepted_issuer_ids: list[str],
        accepted_doc_classes: list[str],
        not_before: int,
        not_after: int,
        now: int,
    ) -> RecognitionRecord:
        self.store.require_dual_control(first, second, frozenset({Role.APPROVE, Role.DEPLOY}))
        if foreign_domain not in self.received_bundles:
            raise TradeError(ReasonCode.UNRECOGNIZED_ANCHOR, "no bundle received for domain")
        bundle = self.received_bundles[foreign_domain]
        known_issuers = {iss["identifier"] for iss in bundle.issuers}
        for iss in accepted_issuer_ids:
            if iss not in known_issuers:
                raise TradeError(ReasonCode.UNRECOGNIZED_ANCHOR, f"issuer not in bundle: {iss}")
            if domain_of(iss) != foreign_domain:
                raise TradeError(ReasonCode.CROSS_ISSUANCE, "issuer domain mismatch")
        record = RecognitionRecord(
            recognizer_domain=self.domain,
            recognized_domain=foreign_domain,
            bundle_version=bundle.version,
            bundle_fingerprint=bundle.fingerprint(),
            accepted_issuer_ids=list(accepted_issuer_ids),
            accepted_doc_classes=list(accepted_doc_classes),
            not_before=not_before,
            not_after=not_after,
            key_id=signer_id,
        )
        sig = self.store.sign(signer_id, canonical_json(record.payload()), now=now)
        record.signature = sig.hex()
        self.recognitions[foreign_domain] = record
        return record

    def withdraw_recognition(
        self,
        foreign_domain: str,
        first: Officer,
        second: Officer,
        signer_id: str,
        *,
        now: int,
    ) -> RecognitionRecord:
        self.store.require_dual_control(first, second, frozenset({Role.APPROVE, Role.DEPLOY}))
        rec = self.recognitions.get(foreign_domain)
        if rec is None:
            raise TradeError(ReasonCode.UNRECOGNIZED_ANCHOR, "no recognition to withdraw")
        rec.withdrawn = True
        rec.withdrawn_at = now
        sig = self.store.sign(signer_id, canonical_json(rec.payload()), now=now)
        rec.signature = sig.hex()
        rec.key_id = signer_id
        return rec

    def recognition_for(self, foreign_domain: str) -> RecognitionRecord | None:
        return self.recognitions.get(foreign_domain)
