"""High-level sovereign domain: one nation's roots, issuers, verifier and ledger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .assertion import (
    SignedAssertionEnvelope,
    build_sae_fields,
    sign_sae,
)
from .authority import AuthorityRegistry, DelegationScope, chain_from
from .ceremony import CeremonyResult
from .crypto import PublicKey, sha256
from .clock import DEFAULT_SKEW_SECONDS, Clock
from .custody import KeyStore, Officer
from .identity import IdentityRegistry, Principal, TrustBundle, make_did
from .ledger import Checkpoint, Ledger
from .protocol import Challenge, VerificationResult, VerifierAgent
from .receipts import (
    BilateralVerificationReceipt,
    acknowledge_receipt,
    issue_receipt,
    verify_receipt,
)
from .status import StatusList, StatusService
from .translation import MappingRegistry, TranslationRecord, translate
from .types import ActorKind, DocClass, ReasonCode, Role, TradeError


def _officer(domain: str, local: str, *roles: Role) -> Officer:
    return Officer(officer_id=f"{domain}:officer:{local}", domain=domain, roles=frozenset(roles))


@dataclass
class Nation:
    domain: str
    clock: Clock
    store: KeyStore
    identity: IdentityRegistry
    authority: AuthorityRegistry
    status: StatusService
    ledger: Ledger
    verifier: VerifierAgent
    officers: dict[str, Officer]
    root: Principal
    # Software-rehearsal 3-of-5 shares for the national root. Grants are
    # signed through this ceremony; the unsplit secret is not reused.
    root_ceremony: CeremonyResult | None = None
    # Translation signer: no delegation chain to the national root.
    translator: Principal | None = None

    @classmethod
    def create(cls, domain: str, clock: Clock) -> "Nation":
        store = KeyStore(domain=domain)
        identity = IdentityRegistry(domain=domain, store=store)
        # Three officers so dual control is possible without any one person
        # holding sign+approve+deploy (R-09).
        officers = {
            "alpha": _officer(domain, "alpha", Role.SIGN, Role.APPROVE),
            "bravo": _officer(domain, "bravo", Role.APPROVE, Role.DEPLOY),
            "charlie": _officer(domain, "charlie", Role.SIGN, Role.DEPLOY),
        }
        for off in officers.values():
            store.register_officer(off)
        now = clock.now_ts()
        root_id = make_did(domain, ActorKind.NATIONAL_ROOT, "root")
        rec, ceremony = store.generate_root(
            root_id,
            officers["alpha"],
            officers["bravo"],
            officers["charlie"],
        )
        root = Principal(
            identifier=root_id,
            kind=ActorKind.NATIONAL_ROOT,
            domain=domain,
            key_id=rec.key_id,
            public_hex=rec.public.public_hex(),
            parent=None,
        )
        identity.add_principal(root)
        authority = AuthorityRegistry(domain=domain, store=store, override_holder=root.identifier)
        status = StatusService(domain=domain, store=store)
        ledger = Ledger(domain=domain, store=store)
        verifier = VerifierAgent(identity, ledger, clock)
        nation = cls(
            domain=domain,
            clock=clock,
            store=store,
            identity=identity,
            authority=authority,
            status=status,
            ledger=ledger,
            verifier=verifier,
            officers=officers,
            root=root,
            root_ceremony=ceremony,
        )
        # Translation signer is created under the store but is NOT chained to the root.
        # We register it as a principal with a synthetic parent link that is
        # deliberately not a delegation; issue() is never called for it.
        translator = identity.create_principal(
            ActorKind.TRANSLATION_SIGNER,
            "translator",
            officers["alpha"],
            officers["bravo"],
            parent=None,
        )
        nation.translator = translator
        status.set_state(
            root.identifier,
            "active",
            officers["alpha"],
            officers["bravo"],
            root.identifier,
            now=now,
            reason="genesis",
            signer=officers["alpha"],
        )
        return nation

    def add_issuer(self, local: str, scope: DelegationScope | None = None) -> Principal:
        now = self.clock.now_ts()
        issuer = self.identity.create_principal(
            ActorKind.INSTITUTIONAL_ISSUER,
            local,
            self.officers["alpha"],
            self.officers["bravo"],
            parent=self.root.identifier,
        )
        wide = scope or DelegationScope(
            doc_classes=frozenset(c.value for c in DocClass),
            commodity_codes=frozenset(),
            counterparty_domains=frozenset(),
            value_ceiling=10**12,
        )
        if self.root_ceremony is None:
            raise TradeError(ReasonCode.FAIL_CLOSED, "national root has no ceremony")
        self.authority.issue(
            self.root,
            issuer,
            wide,
            mode="institutional",
            not_before=now,
            not_after=now + 365 * 24 * 3600,
            now=now,
            parent=None,
            first=self.officers["alpha"],
            second=self.officers["bravo"],
            signer=self.officers["charlie"],
            ceremony=self.root_ceremony,
            shares=list(self.root_ceremony.shares[: self.root_ceremony.threshold]),
        )
        self.status.set_state(
            issuer.identifier,
            "active",
            self.officers["alpha"],
            self.officers["bravo"],
            self.root.identifier,
            now=now,
            signer=self.officers["alpha"],
        )
        return issuer

    def add_signer(
        self,
        issuer: Principal,
        local: str,
        scope: DelegationScope,
        *,
        kind: ActorKind = ActorKind.OPERATIONAL_SIGNER,
        lifetime: int = 3600,
    ) -> tuple[Principal, Any]:
        now = self.clock.now_ts()
        signer = self.identity.create_principal(
            kind,
            local,
            self.officers["alpha"],
            self.officers["bravo"],
            parent=issuer.identifier,
            expires_at=now + lifetime,
        )
        parent = self.authority.current_for(issuer.identifier)
        dele = self.authority.issue(
            issuer,
            signer,
            scope,
            mode="operational",
            not_before=now,
            not_after=now + lifetime,
            now=now,
            parent=parent,
            first=self.officers["alpha"],
            second=self.officers["bravo"],
        )
        self.status.set_state(
            signer.identifier,
            "active",
            self.officers["alpha"],
            self.officers["bravo"],
            issuer.identifier,
            now=now,
        )
        return signer, dele

    def add_receipt_signer(self, issuer: Principal, scope: DelegationScope) -> Principal:
        signer, _ = self.add_signer(
            issuer, "receipts", scope, kind=ActorKind.RECEIPT_SIGNER, lifetime=365 * 24 * 3600
        )
        return signer

    def trust_bundle(self) -> TrustBundle:
        return self.identity.publish_bundle(
            self.root.identifier,
            self.officers["alpha"],
            self.officers["bravo"],
            now=self.clock.now_ts(),
            signer=self.officers["alpha"],
        )

    def recognize(
        self,
        bundle: TrustBundle,
        *,
        accepted_issuer_ids: Iterable[str],
        accepted_doc_classes: Iterable[DocClass | str],
        validity: int = 365 * 24 * 3600,
        expected_fingerprint: str | None = None,
    ) -> None:
        now = self.clock.now_ts()
        self.identity.receive_bundle(bundle, expected_fingerprint=expected_fingerprint)
        classes = [
            c.value if isinstance(c, DocClass) else c for c in accepted_doc_classes
        ]
        self.identity.recognize(
            bundle.domain,
            self.officers["alpha"],
            self.officers["bravo"],
            self.root.identifier,
            accepted_issuer_ids=list(accepted_issuer_ids),
            accepted_doc_classes=classes,
            not_before=now,
            not_after=now + validity,
            now=now,
            signer=self.officers["alpha"],
        )

    def withdraw(self, foreign_domain: str) -> None:
        self.identity.withdraw_recognition(
            foreign_domain,
            self.officers["alpha"],
            self.officers["bravo"],
            self.root.identifier,
            now=self.clock.now_ts(),
            signer=self.officers["alpha"],
        )

    def public_keys(self) -> dict[str, PublicKey]:
        return {kid: rec.public for kid, rec in self.store._keys.items()}

    def export_public_keys(self) -> dict[str, PublicKey]:
        return dict(self.public_keys())

    def issue_assertion(
        self,
        signer: Principal,
        *,
        doc_class: DocClass | str,
        subject: dict[str, Any],
        claims: list[dict[str, Any]],
        institutional_record: bytes,
        challenge: Challenge,
        evidence_refs: list[dict[str, Any]] | None = None,
        lifetime: int = 3600,
        extra_signers: list[tuple[Principal, "Nation"]] | None = None,
    ) -> SignedAssertionEnvelope:
        now = self.clock.now_ts()
        klass = doc_class.value if isinstance(doc_class, DocClass) else doc_class
        chain = chain_from(signer, self.identity.principals, self.authority.records)
        status = self.status.current()
        fields = build_sae_fields(
            issuer_prefix=signer.identifier,
            domain=self.domain,
            doc_class=klass,
            subject=subject,
            claims=claims,
            evidence_refs=evidence_refs
            or [{"hash": sha256(institutional_record), "alg": "sha-256"}],
            issued_at=now,
            not_before=now,
            not_after=now + lifetime,
            txn_binding={
                "txn_id": challenge.txn_id,
                "counterparty_domain": challenge.verifier_domain,
            },
            challenge=challenge.nonce,
            authority_chain=chain,
            status_ref={
                "domain": self.domain,
                "version": status.version if status else 0,
                "digest": status.digest() if status else "",
            },
            source_hash=sha256(institutional_record),
        )
        extras = None
        if extra_signers:
            extras = [(p, n.store) for p, n in extra_signers]
        env = sign_sae(fields, self.store, signer, now=now, extra_signers=extras)
        self.ledger.append({"type": "issued_sae", "hash": env.envelope_hash()}, now=now)
        return env

    def verify_assertion(
        self,
        envelope: SignedAssertionEnvelope,
        *,
        challenge: Challenge | None,
        issuer_keys: dict[str, PublicKey],
        issuer_status: StatusList | None,
        policy_accept: bool | None = True,
        conditions: list[str] | None = None,
        status_required: bool = True,
    ) -> VerificationResult:
        keys = dict(issuer_keys)
        keys.update(self.public_keys())
        result = self.verifier.verify(
            envelope,
            challenge=challenge,
            keys=keys,
            status=issuer_status,
            status_required=status_required,
            policy_accept=policy_accept,
            conditions=conditions,
        )
        self.ledger.append(
            {
                "type": "verification",
                "sae": envelope.envelope_hash(),
                "outcome": result.outcome.value,
                "reasons": result.reasons,
            },
            now=self.clock.now_ts(),
        )
        return result

    def issue_receipt(
        self,
        envelope: SignedAssertionEnvelope,
        result: VerificationResult,
        receipt_signer: Principal,
        *,
        translation: TranslationRecord | None = None,
    ) -> BilateralVerificationReceipt:
        now = self.clock.now_ts()
        receipt = issue_receipt(
            envelope,
            result,
            verifier_id=f"{self.domain}:verifier",
            issuer_domain=envelope.domain,
            receiver_domain=self.domain,
            now=now,
            skew=DEFAULT_SKEW_SECONDS,
            translation_hash=translation.digest() if translation else None,
            store=self.store,
            signer=receipt_signer,
        )
        self.ledger.append({"type": "bvr", "hash": receipt.receipt_hash()}, now=now)
        return receipt

    def acknowledge(self, receipt: BilateralVerificationReceipt, signer: Principal) -> BilateralVerificationReceipt:
        now = self.clock.now_ts()
        acknowledge_receipt(receipt, self.store, signer, now=now)
        self.ledger.append({"type": "bvr_ack", "hash": receipt.receipt_hash()}, now=now)
        return receipt

    def checkpoint(self) -> Checkpoint:
        return self.ledger.checkpoint(self.root.identifier, now=self.clock.now_ts(), signer=self.officers["alpha"])

    def translate(
        self,
        envelope: SignedAssertionEnvelope,
        registry: MappingRegistry,
        *,
        confirmed_class_changes: list[str] | None = None,
    ) -> TranslationRecord:
        if self.translator is None:
            raise TradeError(ReasonCode.CHAIN_INVALID, "no translation signer")
        return translate(
            envelope,
            registry,
            self.store,
            self.translator,
            now=self.clock.now_ts(),
            confirmed_class_changes=confirmed_class_changes,
        )


def merge_public_keys(*nations: Nation) -> dict[str, PublicKey]:
    keys: dict[str, PublicKey] = {}
    for nation in nations:
        keys.update(nation.export_public_keys())
    return keys


def verify_receipt_offline(
    receipt: BilateralVerificationReceipt,
    keys: dict[str, PublicKey],
    *,
    inclusion: dict[str, Any] | None = None,
    expected_root: str | None = None,
    require_both_parties: bool = True,
) -> ReasonCode:
    """R-07 / independence test: no live counterparty required."""
    from .ledger import verify_inclusion_proof

    reason = verify_receipt(receipt, keys, require_both_parties=require_both_parties)
    if reason is not ReasonCode.OK:
        return reason
    if inclusion is not None:
        if not verify_inclusion_proof(inclusion, expected_root):
            return ReasonCode.CANONICAL_FORM_MISMATCH
    return ReasonCode.OK
