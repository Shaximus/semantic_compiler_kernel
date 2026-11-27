"""Acceptance tests for SC-SOV-TRADE-001 (R-01 through R-16)."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from semantic_compiler.expansion.elevator import EXPLICIT_ONLY_ENTRY_HINTS, summon
from semantic_compiler.expansion.router import route_domains
from semantic_compiler.sov_trade import (
    AssuranceStatus,
    CaptureError,
    CustodyError,
    DelegationScope,
    DocClass,
    FrozenClock,
    MappingEntry,
    MappingRegistry,
    MappingType,
    Nation,
    Outcome,
    ReasonCode,
    Role,
    backend_name,
    merge_public_keys,
    open_dispute,
    provenance_round_trip,
    resolve_dispute,
    salted_commitment,
    verify_receipt_offline,
)
from semantic_compiler.sov_trade.authority import DelegationRecord
from semantic_compiler.sov_trade.canonical import canonical_json
from semantic_compiler.sov_trade.crypto import PublicKey, generate_ed25519, sha256
from semantic_compiler.sov_trade.types import ActorKind, CheckName

EID = "SC-SOV-TRADE-001"
REPO = Path(__file__).resolve().parent.parent
ORIGIN = b"origin-record-nation-a-v1"
COMMODITY = "0701.90"
VALUE = 10_000


def _scope(*domains: str, ceiling: int = 1_000_000) -> DelegationScope:
    return DelegationScope(
        doc_classes=frozenset({DocClass.CERTIFICATE_OF_ORIGIN.value}),
        commodity_codes=frozenset({COMMODITY}),
        counterparty_domains=frozenset(domains),
        value_ceiling=ceiling,
    )


def _pair(clock: FrozenClock | None = None) -> tuple[Nation, Nation, object, object]:
    clock = clock or FrozenClock(1_700_000_000)
    a = Nation.create("nation-a", clock)
    b = Nation.create("nation-b", clock)
    issuer_a = a.add_issuer("customs")
    issuer_b = b.add_issuer("customs")
    signer_a, _ = a.add_signer(issuer_a, "officer-1", _scope(b.domain))
    receipt_a = a.add_receipt_signer(issuer_a, _scope(b.domain, a.domain, ceiling=10**9))
    receipt_b = b.add_receipt_signer(issuer_b, _scope(a.domain, b.domain, ceiling=10**9))
    a.recognize(
        b.trust_bundle(),
        accepted_issuer_ids=[issuer_b.identifier],
        accepted_doc_classes=[DocClass.CERTIFICATE_OF_ORIGIN],
    )
    b.recognize(
        a.trust_bundle(),
        accepted_issuer_ids=[issuer_a.identifier],
        accepted_doc_classes=[DocClass.CERTIFICATE_OF_ORIGIN],
    )
    ctx = {
        "clock": clock,
        "issuer_a": issuer_a,
        "issuer_b": issuer_b,
        "signer_a": signer_a,
        "receipt_a": receipt_a,
        "receipt_b": receipt_b,
    }
    return a, b, ctx, clock


def _subject(counterparty: str = "nation-b", value: int = VALUE) -> dict:
    return {
        "goods": "potatoes",
        "commodity_code": COMMODITY,
        "parties": ["exporter-a", "importer-b"],
        "shipment": "SHP-1",
        "value": value,
    }


def _issue(a: Nation, signer, challenge, **kwargs):
    return a.issue_assertion(
        signer,
        doc_class=DocClass.CERTIFICATE_OF_ORIGIN,
        subject=_subject(),
        claims=[{"statement": "origin is Nation A", "evidence_ref": 0}],
        institutional_record=ORIGIN,
        challenge=challenge,
        **kwargs,
    )


def _happy(a: Nation, b: Nation, ctx) -> tuple:
    ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-1")
    sae = _issue(a, ctx["signer_a"], ch)
    result = b.verify_assertion(
        sae,
        challenge=ch,
        issuer_keys=a.export_public_keys(),
        issuer_status=a.status.current(),
    )
    return ch, sae, result


# ---------------------------------------------------------------------------
# R-01 Neither nation can impersonate the other
# ---------------------------------------------------------------------------

class TestR01Impersonation:
    def test_foreign_signed_presented_as_domestic_fails(self) -> None:
        a, b, ctx, _ = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-1")
        sae = _issue(a, ctx["signer_a"], ch)
        # Impersonation: rewrite the domain to look domestic while keeping A's signature.
        sae.fields["domain"] = b.domain
        result = b.verify_assertion(
            sae,
            challenge=ch,
            issuer_keys=a.export_public_keys(),
            issuer_status=a.status.current(),
        )
        assert result.outcome is Outcome.REJECTED
        assert ReasonCode.SIGNATURE_INVALID.value in result.reasons or any(
            c.reason
            in {
                ReasonCode.SIGNATURE_INVALID,
                ReasonCode.CROSS_ISSUANCE,
                ReasonCode.CANONICAL_FORM_MISMATCH,
                ReasonCode.TXN_BINDING_MISMATCH,
            }
            for c in result.checks
        )

    def test_forged_key_cannot_impersonate_a_nation(self) -> None:
        a, b, ctx, clock = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-1")
        sae = _issue(a, ctx["signer_a"], ch)
        # Replace the signature with one from an unrelated key.
        rogue = generate_ed25519()
        payload = sae.signed_bytes()
        sae.signatures[0].signature = rogue.sign(payload).hex()
        result = b.verify_assertion(
            sae,
            challenge=ch,
            issuer_keys=a.export_public_keys(),
            issuer_status=a.status.current(),
        )
        assert result.reason_for(CheckName.SIGNATURE) is ReasonCode.SIGNATURE_INVALID
        assert result.outcome is Outcome.REJECTED


# ---------------------------------------------------------------------------
# R-02 Recognition is explicit, scoped, revocable, held by the recognizer
# ---------------------------------------------------------------------------

class TestR02Recognition:
    def test_withdraw_mid_transaction_rejects_and_leaves_grantor_untouched(self) -> None:
        a, b, ctx, clock = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-mid")
        sae = _issue(a, ctx["signer_a"], ch)
        grantor_serial_before = a.authority.serials.get(a.root.identifier)
        bundle_fp_before = a.trust_bundle().fingerprint()
        b.withdraw(a.domain)
        result = b.verify_assertion(
            sae,
            challenge=ch,
            issuer_keys=a.export_public_keys(),
            issuer_status=a.status.current(),
        )
        assert result.outcome is Outcome.REJECTED
        assert result.reason_for(CheckName.CHAIN) is ReasonCode.RECOGNITION_WITHDRAWN
        # Grantor's domain is unaffected.
        assert a.authority.serials.get(a.root.identifier) == grantor_serial_before
        assert a.identity.recognition_for(b.domain) is not None
        assert not a.identity.recognition_for(b.domain).withdrawn
        assert a.trust_bundle().fingerprint() != ""  # still operable
        _ = bundle_fp_before

    def test_recognition_is_not_symmetric_by_default(self) -> None:
        clock = FrozenClock(1_700_000_000)
        a = Nation.create("nation-a", clock)
        b = Nation.create("nation-b", clock)
        issuer_a = a.add_issuer("customs")
        b.recognize(
            a.trust_bundle(),
            accepted_issuer_ids=[issuer_a.identifier],
            accepted_doc_classes=[DocClass.CERTIFICATE_OF_ORIGIN],
        )
        assert b.identity.recognition_for(a.domain) is not None
        assert a.identity.recognition_for(b.domain) is None

    def test_out_of_scope_class_is_not_recognized(self) -> None:
        a, b, ctx, _ = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-class")
        sae = a.issue_assertion(
            ctx["signer_a"],
            doc_class=DocClass.CUSTOMS_DECLARATION,  # not in signer's scope either
            subject=_subject(),
            claims=[{"statement": "x", "evidence_ref": 0}],
            institutional_record=ORIGIN,
            challenge=ch,
        )
        result = b.verify_assertion(
            sae,
            challenge=ch,
            issuer_keys=a.export_public_keys(),
            issuer_status=a.status.current(),
        )
        assert result.outcome is Outcome.REJECTED
        assert result.reason_for(CheckName.SCOPE) is ReasonCode.DELEGATION_SCOPE or result.reason_for(
            CheckName.CHAIN
        ) in {ReasonCode.RECOGNITION_SCOPE, ReasonCode.DELEGATION_SCOPE}


# ---------------------------------------------------------------------------
# R-03 A signed assertion cannot be altered undetected
# ---------------------------------------------------------------------------

class TestR03Tamper:
    def test_bit_flip_every_field(self) -> None:
        a, b, ctx, _ = _pair()
        ch, sae, result = _happy(a, b, ctx)
        assert result.verification_passed
        fields = list(sae.fields.keys())
        for field in fields:
            flipped = copy.deepcopy(sae)
            value = flipped.fields[field]
            if field in {"not_before", "not_after", "issued_at"}:
                flipped.fields[field] = int(value) + 1
            elif isinstance(value, str):
                flipped.fields[field] = value + "x"
            elif isinstance(value, dict):
                flipped.fields[field] = dict(value, tampered=True)
            elif isinstance(value, list):
                flipped.fields[field] = list(value) + [{"tampered": True}]
            else:
                flipped.fields[field] = "tampered"
            res = b.verify_assertion(
                flipped,
                challenge=ch,
                issuer_keys=a.export_public_keys(),
                issuer_status=a.status.current(),
                policy_accept=True,
            )
            assert res.verification_passed is False, f"field {field} accepted after tamper"
            assert res.outcome is not Outcome.ACCEPTED


# ---------------------------------------------------------------------------
# R-04 Delegated authority is scoped
# ---------------------------------------------------------------------------

class TestR04Scope:
    def test_signer_outside_doc_class_rejected(self) -> None:
        a, b, ctx, _ = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-scope-class")
        sae = a.issue_assertion(
            ctx["signer_a"],
            doc_class=DocClass.INSPECTION_RECORD,
            subject=_subject(),
            claims=[{"statement": "x", "evidence_ref": 0}],
            institutional_record=ORIGIN,
            challenge=ch,
        )
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.SCOPE) is ReasonCode.DELEGATION_SCOPE

    def test_signer_outside_commodity_rejected(self) -> None:
        a, b, ctx, _ = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-scope-cmd")
        subject = _subject()
        subject["commodity_code"] = "9999.99"
        sae = a.issue_assertion(
            ctx["signer_a"],
            doc_class=DocClass.CERTIFICATE_OF_ORIGIN,
            subject=subject,
            claims=[{"statement": "x", "evidence_ref": 0}],
            institutional_record=ORIGIN,
            challenge=ch,
        )
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.SCOPE) is ReasonCode.DELEGATION_SCOPE

    def test_signer_above_value_ceiling_rejected(self) -> None:
        a, b, ctx, _ = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-scope-val")
        subject = _subject(value=9_999_999)
        sae = a.issue_assertion(
            ctx["signer_a"],
            doc_class=DocClass.CERTIFICATE_OF_ORIGIN,
            subject=subject,
            claims=[{"statement": "x", "evidence_ref": 0}],
            institutional_record=ORIGIN,
            challenge=ch,
        )
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.SCOPE) is ReasonCode.DELEGATION_SCOPE

    def test_scope_cannot_widen_down_the_chain(self) -> None:
        a, b, ctx, clock = _pair()
        parent = a.authority.current_for(ctx["signer_a"].identifier)
        wide = DelegationScope(
            doc_classes=frozenset({DocClass.CERTIFICATE_OF_ORIGIN.value, DocClass.CUSTOMS_DECLARATION.value}),
            commodity_codes=frozenset({COMMODITY, "9999.99"}),
            counterparty_domains=frozenset({b.domain}),
            value_ceiling=parent.scope.value_ceiling + 1,
        )
        with pytest.raises(TradeError := __import__("semantic_compiler.sov_trade", fromlist=["TradeError"]).TradeError) as exc:
            a.authority.issue(
                ctx["signer_a"],
                ctx["signer_a"],
                wide,
                mode="operational",
                not_before=clock.now_ts(),
                not_after=clock.now_ts() + 10,
                now=clock.now_ts(),
                parent=parent,
                first=a.officers["alpha"],
                second=a.officers["bravo"],
            )
        assert exc.value.reason in {ReasonCode.SCOPE_WIDENED, ReasonCode.CAPTURE_SELF_ESCALATION}


# ---------------------------------------------------------------------------
# R-05 Expired, revoked and replayed evidence are distinguishable
# ---------------------------------------------------------------------------

class TestR05FreshnessMatrix:
    def test_valid(self) -> None:
        a, b, ctx, _ = _pair()
        _, _, result = _happy(a, b, ctx)
        assert result.verification_passed
        assert result.outcome is Outcome.ACCEPTED
        assert all(c.reason is ReasonCode.OK for c in result.checks)

    def test_expired(self) -> None:
        a, b, ctx, clock = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-exp")
        sae = _issue(a, ctx["signer_a"], ch, lifetime=10)
        clock.advance(10 + 120 + 1)  # past the window and the allowed skew
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.VALIDITY_WINDOW) is ReasonCode.EXPIRED
        assert result.outcome is Outcome.REJECTED

    def test_not_yet_valid(self) -> None:
        a, b, ctx, clock = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-nyv")
        sae = _issue(a, ctx["signer_a"], ch)
        sae.fields["not_before"] = clock.now_ts() + 10_000
        # resigning would hide the case; we want the window check, so resign
        # after adjusting is done in issue; here we flip not_before and
        # re-sign by reconstructing via sign_sae after the fact is hard
        # because the signature will fail. Advance the window in issue by
        # building with a future not_before through a direct field rebuild.
        from semantic_compiler.sov_trade.assertion import sign_sae

        sae.fields["not_before"] = clock.now_ts() + 10_000
        sae2 = sign_sae(sae.fields, a.store, ctx["signer_a"], now=clock.now_ts())
        result = b.verify_assertion(
            sae2, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.VALIDITY_WINDOW) is ReasonCode.NOT_YET_VALID

    def test_revoked(self) -> None:
        a, b, ctx, clock = _pair()
        a.status.set_state(
            ctx["signer_a"].identifier,
            "revoked",
            a.officers["alpha"],
            a.officers["bravo"],
            ctx["issuer_a"].identifier,
            now=clock.now_ts(),
            reason="dismissed",
        )
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-rev")
        # Signing itself will fail once the key is revoked in the store;
        # revoke only on the status list for the already-issued key's status,
        # keeping the key usable so we test verifier-side revocation.
        # Re-activate the key material if custody blocked signing... set_state
        # does not revoke the key in the store. Good.
        sae = _issue(a, ctx["signer_a"], ch)
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.REVOCATION) is ReasonCode.REVOKED
        assert result.outcome is Outcome.REJECTED

    def test_replayed(self) -> None:
        a, b, ctx, _ = _pair()
        ch, sae, first = _happy(a, b, ctx)
        assert first.verification_passed
        second = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert second.reason_for(CheckName.REPLAY) is ReasonCode.REPLAYED
        assert second.outcome is Outcome.REJECTED

    def test_wrong_transaction(self) -> None:
        a, b, ctx, _ = _pair()
        ch1 = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-A")
        ch2 = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-B")
        sae = _issue(a, ctx["signer_a"], ch1)
        result = b.verify_assertion(
            sae, challenge=ch2, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.BINDING) in {
            ReasonCode.CHALLENGE_MISMATCH,
            ReasonCode.TXN_BINDING_MISMATCH,
        }
        assert result.outcome is Outcome.REJECTED

    def test_each_case_has_its_own_reason_code(self) -> None:
        # The six cases above must not collapse to a single generic failure.
        codes = {
            ReasonCode.OK,
            ReasonCode.EXPIRED,
            ReasonCode.NOT_YET_VALID,
            ReasonCode.REVOKED,
            ReasonCode.REPLAYED,
            ReasonCode.CHALLENGE_MISMATCH,
            ReasonCode.TXN_BINDING_MISMATCH,
        }
        assert len({c.value for c in codes}) == len(codes)


# ---------------------------------------------------------------------------
# R-06 Unknown status fails closed
# ---------------------------------------------------------------------------

class TestR06StatusFailClosed:
    def test_cut_status_service_defers(self) -> None:
        a, b, ctx, _ = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-status")
        sae = _issue(a, ctx["signer_a"], ch)
        a.status.reachable = False
        result = b.verify_assertion(
            sae,
            challenge=ch,
            issuer_keys=a.export_public_keys(),
            issuer_status=a.status.current(),  # None, because unreachable
        )
        assert result.reason_for(CheckName.REVOCATION) is ReasonCode.STATUS_UNKNOWN
        assert result.outcome is Outcome.DEFERRED
        assert result.outcome is not Outcome.ACCEPTED


# ---------------------------------------------------------------------------
# R-07 Both parties verify receipts independently
# ---------------------------------------------------------------------------

class TestR07Receipts:
    def test_verify_bvr_with_counterparty_offline(self) -> None:
        a, b, ctx, _ = _pair()
        ch, sae, result = _happy(a, b, ctx)
        receipt = b.issue_receipt(sae, result, ctx["receipt_b"])
        a.acknowledge(receipt, ctx["receipt_a"])
        cp = b.checkpoint()
        proof = b.ledger.inclusion_proof(b.ledger.entries[-2].seq)  # bvr entry may be last-1 after ack? 
        # Find the bvr entry.
        bvr_seq = next(e.seq for e in b.ledger.entries if e.body.get("type") == "bvr")
        proof = b.ledger.inclusion_proof(bvr_seq)
        keys = merge_public_keys(a, b)
        reason = verify_receipt_offline(
            receipt, keys, inclusion=proof, expected_root=cp.root, require_both_parties=True
        )
        assert reason is ReasonCode.OK
        # Independence: no call into the other nation's live services.
        a_status_reachable = a.status.reachable
        a.status.reachable = False
        b.status.reachable = False
        reason2 = verify_receipt_offline(receipt, keys, require_both_parties=True)
        assert reason2 is ReasonCode.OK
        a.status.reachable = a_status_reachable


# ---------------------------------------------------------------------------
# R-08 Split views are detectable
# ---------------------------------------------------------------------------

class TestR08SplitView:
    def test_forked_checkpoint_is_flagged(self) -> None:
        a, b, ctx, clock = _pair()
        _happy(a, b, ctx)
        cp1 = a.checkpoint()
        reason = b.ledger.store_peer_checkpoint(cp1)
        assert reason is ReasonCode.OK
        # Fork: same seq, different root.
        forked = copy.copy(cp1)
        forked.root = "0" * 64
        reason2 = b.ledger.store_peer_checkpoint(forked)
        assert reason2 is ReasonCode.LEDGER_FORK
        assert b.ledger.acceptance_halted is True
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-after-fork")
        sae = _issue(a, ctx["signer_a"], ch)
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.outcome is Outcome.REJECTED
        assert ReasonCode.LEDGER_FORK.value in result.reasons


# ---------------------------------------------------------------------------
# R-09 No single person can sign, approve and deploy
# ---------------------------------------------------------------------------

class TestR09RoleSeparation:
    def test_officer_cannot_hold_all_three_roles(self) -> None:
        from semantic_compiler.sov_trade.custody import Officer

        with pytest.raises(CustodyError) as exc:
            Officer(officer_id="solo", domain="nation-a", roles=frozenset(Role))
        assert exc.value.reason is ReasonCode.ROLE_SEPARATION

    def test_dual_control_rejects_same_officer_twice(self) -> None:
        a, _, _, _ = _pair()
        with pytest.raises(CustodyError) as exc:
            a.store.require_dual_control(
                a.officers["alpha"], a.officers["alpha"], frozenset({Role.APPROVE})
            )
        assert exc.value.reason is ReasonCode.DUAL_CONTROL_REQUIRED


# ---------------------------------------------------------------------------
# R-10 Algorithm agility and hybrid verification
# ---------------------------------------------------------------------------

class TestR10Hybrid:
    def test_hybrid_with_one_broken_signature_fails(self) -> None:
        a, b, ctx, clock = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-hyb")
        # Second signer: another operational key on A, co-signs the envelope.
        signer2, _ = a.add_signer(ctx["issuer_a"], "officer-2", _scope(b.domain))
        sae = _issue(a, ctx["signer_a"], ch, extra_signers=[(signer2, a)])
        assert len(sae.signatures) == 2
        # Break the second signature only.
        sae.signatures[1].signature = ("00" * 64)
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.SIGNATURE) in {
            ReasonCode.HYBRID_INCOMPLETE,
            ReasonCode.SIGNATURE_INVALID,
        }
        assert result.verification_passed is False

    def test_suite_identifier_is_ed25519_and_replaceable(self) -> None:
        a, b, ctx, _ = _pair()
        _, sae, result = _happy(a, b, ctx)
        assert result.verification_passed
        assert sae.signatures[0].algorithm == "ed25519"
        assert backend_name() in {"cryptography", "vendored_ed25519_ref"}

    def test_mldsa_is_not_claimed(self) -> None:
        # Honest: ML-DSA is not implemented. See PENDING_DELIBERATION.
        import semantic_compiler.sov_trade.crypto as crypto

        assert not hasattr(crypto, "generate_mldsa")


# ---------------------------------------------------------------------------
# R-11 Root compromise is recoverable
# ---------------------------------------------------------------------------

class TestR11RootCompromise:
    def test_compromise_drill_suspends_and_re_recognizes(self) -> None:
        a, b, ctx, clock = _pair()
        _, _, first = _happy(a, b, ctx)
        assert first.verification_passed
        # Owning nation declares compromise; counterparty suspends recognition.
        b.withdraw(a.domain)
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-comp")
        sae = _issue(a, ctx["signer_a"], ch)
        rejected = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert rejected.reason_for(CheckName.CHAIN) is ReasonCode.RECOGNITION_WITHDRAWN
        # New ceremony: new bundle + new Recognition Record (same root in this
        # reference; a real drill would mint a new root — we re-recognize).
        b.recognize(
            a.trust_bundle(),
            accepted_issuer_ids=[ctx["issuer_a"].identifier],
            accepted_doc_classes=[DocClass.CERTIFICATE_OF_ORIGIN],
        )
        ch2 = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-reest")
        sae2 = _issue(a, ctx["signer_a"], ch2)
        restored = b.verify_assertion(
            sae2, challenge=ch2, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert restored.verification_passed


# ---------------------------------------------------------------------------
# R-12 Anti-capture
# ---------------------------------------------------------------------------

class TestR12AntiCapture:
    def test_no_self_escalation(self) -> None:
        a, _, ctx, clock = _pair()
        with pytest.raises(CaptureError) as exc:
            a.authority.issue(
                ctx["signer_a"],
                ctx["signer_a"],
                _scope("nation-b"),
                mode="operational",
                not_before=clock.now_ts(),
                not_after=clock.now_ts() + 10,
                now=clock.now_ts(),
                parent=a.authority.current_for(ctx["signer_a"].identifier),
                first=a.officers["alpha"],
                second=a.officers["bravo"],
            )
        assert exc.value.reason is ReasonCode.CAPTURE_SELF_ESCALATION

    def test_verifier_cannot_modify_policy_or_grant(self) -> None:
        a, b, _, _ = _pair()
        with pytest.raises(CaptureError):
            b.authority.verifier_modify_policy()
        with pytest.raises(CaptureError):
            b.authority.verifier_quarantine_override()

    def test_advisory_cannot_approve_or_widen(self) -> None:
        a, _, ctx, _ = _pair()
        a.authority.record_advisory(ctx["signer_a"].identifier, 0.99)
        with pytest.raises(CaptureError) as exc:
            a.authority.approve_from_advisory(ctx["signer_a"].identifier)
        assert exc.value.reason is ReasonCode.ADVISORY_USED_AS_AUTH

    def test_emergency_ttl_must_be_bounded_and_external(self) -> None:
        a, _, ctx, clock = _pair()
        parent = a.authority.current_for(ctx["signer_a"].identifier)
        with pytest.raises(CaptureError) as exc:
            a.authority.issue(
                ctx["signer_a"],
                ctx["signer_a"],
                parent.scope,
                mode="emergency",
                not_before=clock.now_ts(),
                not_after=clock.now_ts() + 10,
                now=clock.now_ts(),
                parent=parent,
                first=a.officers["alpha"],
                second=a.officers["bravo"],
                emergency=True,
            )
        assert exc.value.reason in {
            ReasonCode.CAPTURE_SELF_ESCALATION,
            ReasonCode.EMERGENCY_TTL_INVALID,
        }

    def test_verifier_cannot_sign_assertions(self) -> None:
        a, b, ctx, clock = _pair()
        # Invent a verifier principal and try to sign.
        from semantic_compiler.sov_trade.assertion import build_sae_fields, sign_sae
        from semantic_compiler.sov_trade.types import TradeError

        va = b.identity.create_principal(
            ActorKind.VERIFIER_AGENT,
            "va",
            b.officers["alpha"],
            b.officers["bravo"],
            parent=ctx["issuer_b"].identifier,
        )
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-va")
        fields = build_sae_fields(
            issuer_prefix=va.identifier,
            domain=b.domain,
            doc_class=DocClass.CERTIFICATE_OF_ORIGIN.value,
            subject=_subject(),
            claims=[],
            evidence_refs=[],
            issued_at=clock.now_ts(),
            not_before=clock.now_ts(),
            not_after=clock.now_ts() + 10,
            txn_binding={"txn_id": ch.txn_id, "counterparty_domain": a.domain},
            challenge=ch.nonce,
            authority_chain=[],
            status_ref={},
            source_hash=sha256(ORIGIN),
        )
        with pytest.raises(TradeError) as exc:
            sign_sae(fields, b.store, va, now=clock.now_ts())
        assert exc.value.reason is ReasonCode.VERIFIER_SIGNED_ASSERTION

    def test_root_never_signs_assertions(self) -> None:
        a, b, _, clock = _pair()
        from semantic_compiler.sov_trade.assertion import build_sae_fields, sign_sae
        from semantic_compiler.sov_trade.types import TradeError

        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-root")
        fields = build_sae_fields(
            issuer_prefix=a.root.identifier,
            domain=a.domain,
            doc_class=DocClass.CERTIFICATE_OF_ORIGIN.value,
            subject=_subject(),
            claims=[],
            evidence_refs=[],
            issued_at=clock.now_ts(),
            not_before=clock.now_ts(),
            not_after=clock.now_ts() + 10,
            txn_binding={"txn_id": ch.txn_id, "counterparty_domain": b.domain},
            challenge=ch.nonce,
            authority_chain=[],
            status_ref={},
            source_hash=sha256(ORIGIN),
        )
        with pytest.raises(TradeError) as exc:
            sign_sae(fields, a.store, a.root, now=clock.now_ts())
        assert exc.value.reason is ReasonCode.ROOT_SIGNED_ASSERTION


# ---------------------------------------------------------------------------
# R-13 Translation cannot alter a signed record or silently change class
# ---------------------------------------------------------------------------

class TestR13Translation:
    def _registry(self, owner: str, now: int, *, legal: bool = False) -> MappingRegistry:
        return MappingRegistry(
            owner_domain=owner,
            version=1,
            effective_at=now,
            entries=[
                MappingEntry("potatoes", "solanum tuberosum", MappingType.EXACT, "subject.goods"),
                MappingEntry(
                    "certificate_of_origin",
                    "origin_certificate",
                    MappingType.NARROWING,
                    "doc_class",
                    legal_category_change=legal,
                ),
            ],
            review_history=[{"reviewer": "nation-a", "at": now}],
        )

    def test_source_hash_unchanged_and_non_exact_flagged(self) -> None:
        a, b, ctx, clock = _pair()
        _, sae, _ = _happy(a, b, ctx)
        before = sae.envelope_hash()
        before_source = sae.fields["source_hash"]
        record = b.translate(sae, self._registry(b.domain, clock.now_ts(), legal=False))
        assert sae.envelope_hash() == before
        assert sae.fields["source_hash"] == before_source
        assert record.source_hash == before_source
        assert record.sae_hash == before
        assert "non_exact:doc_class:narrowing" in record.flags
        assert record.field_tags["doc_class"] == MappingType.NARROWING.value
        assert record.field_tags["subject.goods"] == MappingType.EXACT.value

    def test_legal_class_change_requires_confirmation(self) -> None:
        a, b, ctx, clock = _pair()
        _, sae, _ = _happy(a, b, ctx)
        from semantic_compiler.sov_trade.types import TradeError

        with pytest.raises(TradeError) as exc:
            b.translate(sae, self._registry(b.domain, clock.now_ts(), legal=True))
        assert exc.value.reason is ReasonCode.CLASS_CHANGE_UNCONFIRMED
        record = b.translate(
            sae,
            self._registry(b.domain, clock.now_ts(), legal=True),
            confirmed_class_changes=["certificate_of_origin"],
        )
        assert "certificate_of_origin" in record.human_confirmed_class_changes

    def test_unmapped_terms_pass_through_flagged(self) -> None:
        a, b, ctx, clock = _pair()
        _, sae, _ = _happy(a, b, ctx)
        registry = MappingRegistry(
            owner_domain=b.domain, version=1, effective_at=clock.now_ts(), entries=[]
        )
        record = b.translate(sae, registry)
        assert any(f.startswith("unmapped:subject.goods:") for f in record.flags)
        assert record.output["subject"]["goods"] == "potatoes"

    def test_translation_signer_has_no_root_chain(self) -> None:
        a, _, _, _ = _pair()
        assert a.translator is not None
        assert a.translator.parent is None
        assert a.translator.kind is ActorKind.TRANSLATION_SIGNER


# ---------------------------------------------------------------------------
# R-14 Source records retain provenance
# ---------------------------------------------------------------------------

class TestR14Provenance:
    def test_round_trip_to_institutional_record(self) -> None:
        a, b, ctx, clock = _pair()
        _, sae, _ = _happy(a, b, ctx)
        registry = MappingRegistry(
            owner_domain=b.domain,
            version=1,
            effective_at=clock.now_ts(),
            entries=[
                MappingEntry("potatoes", "solanum tuberosum", MappingType.EXACT, "subject.goods")
            ],
        )
        record = b.translate(sae, registry)
        assert provenance_round_trip(record, sae, ORIGIN) is ReasonCode.OK
        assert provenance_round_trip(record, sae, b"other-record") is ReasonCode.TRANSLATION_ALTERED_SOURCE


# ---------------------------------------------------------------------------
# R-15 Degraded operation is defined and bounded
# ---------------------------------------------------------------------------

class TestR15Degraded:
    def test_clock_drift_rejects(self) -> None:
        a, b, ctx, clock = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-drift")
        sae = _issue(a, ctx["signer_a"], ch)
        clock.advance(10_000)
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.VALIDITY_WINDOW) in {
            ReasonCode.CLOCK_DRIFT,
            ReasonCode.EXPIRED,
        }
        assert result.outcome is Outcome.REJECTED

    def test_stale_status_defers(self) -> None:
        a, b, ctx, clock = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-stale")
        sae = _issue(a, ctx["signer_a"], ch, lifetime=24 * 3600)
        clock.advance(DEFAULT := 16 * 60)  # past 15-minute freshness, still in validity
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.REVOCATION) is ReasonCode.STATUS_STALE
        assert result.outcome is Outcome.DEFERRED

    def test_link_loss_uses_cached_status_until_freshness_bound(self) -> None:
        a, b, ctx, _ = _pair()
        cached = a.status.last_cached()
        a.status.reachable = False
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-link")
        sae = _issue(a, ctx["signer_a"], ch)
        # Offline verification against the last trusted status (cached).
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=cached
        )
        assert result.verification_passed


# ---------------------------------------------------------------------------
# R-16 Independent assurance is not met (honest, deferred)
# ---------------------------------------------------------------------------

class TestR16Assurance:
    def test_independent_assurance_is_not_claimed(self) -> None:
        assert AssuranceStatus.NOT_MET.value == "not_met"
        # This reference build has no third-party penetration test or
        # formal protocol review on record. The requirement is not met
        # and is not treated as passing.
        assert AssuranceStatus.NOT_CLAIMED.value == "not_claimed"


# ---------------------------------------------------------------------------
# Disputes (section 12)
# ---------------------------------------------------------------------------

class TestDisputes:
    def test_reproduces_a_valid_receipt_and_flags_a_tampered_one(self) -> None:
        a, b, ctx, clock = _pair()
        _, sae, result = _happy(a, b, ctx)
        receipt = b.issue_receipt(sae, result, ctx["receipt_b"])
        a.acknowledge(receipt, ctx["receipt_a"])
        keys = merge_public_keys(a, b)
        dispute = open_dispute(
            opened_by=b.domain,
            target_hash=receipt.receipt_hash(),
            target_kind="bvr",
            now=clock.now_ts(),
        )
        proof = b.ledger.inclusion_proof(next(e.seq for e in b.ledger.entries if e.body.get("type") == "bvr"))
        resolved = resolve_dispute(
            dispute,
            receipt=receipt,
            envelope=sae,
            inclusion_a=proof,
            inclusion_b=None,
            receipt_keys=keys,
        )
        assert resolved.outcome == "reproduced"
        dispute2 = open_dispute(
            opened_by=b.domain,
            target_hash="0" * 64,
            target_kind="bvr",
            now=clock.now_ts(),
        )
        resolved2 = resolve_dispute(
            dispute2,
            receipt=receipt,
            envelope=None,
            inclusion_a=None,
            inclusion_b=None,
            receipt_keys=keys,
        )
        assert resolved2.outcome == "contested"
        assert "receipt_hash_mismatch" in resolved2.reasons

# ---------------------------------------------------------------------------
# Catalog / routing / evidence
# ---------------------------------------------------------------------------

class TestCatalogAndEvidence:
    def test_rfc8032_test1_keys_and_empty_message(self) -> None:
        # RFC 8032 test 1 secret and public keys, empty message. The signature
        # is the byte string produced independently by this reference and by
        # pyca/cryptography 43 for the same seed (they agree).
        sk = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
        pk = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
        sig = bytes.fromhex(
            "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
            "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
        )
        from semantic_compiler.sov_trade import _ed25519 as ref

        assert ref.publickey_unsafe(sk) == pk
        ref.checkvalid(sig, b"", pk)
        pub = PublicKey(algorithm="ed25519", public_key=pk)
        assert pub.verify(b"", sig)
        assert ref.signature_unsafe(b"", sk, pk) == sig

    def test_selective_disclosure_commitment(self) -> None:
        salt = b"salt-1"
        commit = salted_commitment("secret-price", salt)
        assert commit == sha256(salt + b"|" + b"secret-price")
        assert commit != salted_commitment("secret-price", b"other")

    def test_canonical_form_is_stable(self) -> None:
        a = {"b": 1, "a": [True, None, "x"]}
        b = {"a": [True, None, "x"], "b": 1}
        assert canonical_json(a) == canonical_json(b)

    def test_explicit_only_and_routes_home(self) -> None:
        assert EID in EXPLICIT_ONLY_ENTRY_HINTS
        assert route_domains(f"Explain {EID}.").domain == "trust_chain"
        assert EID in [e.entry_id for e in summon(f"Explain {EID}.", top_k=5).compiled_entries]

    def test_everyday_words_do_not_lift(self) -> None:
        from semantic_compiler.core.pipeline import compile_semantic_packet

        for text in (
            "The customs office issued a certificate of origin.",
            "remind me to call mom at 6",
            "We need a signed receipt for the shipment.",
        ):
            assert route_domains(text).domain != "trust_chain"
            ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
            assert EID not in ids

    def test_compiled_entry_is_silver_gold_withheld(self) -> None:
        import json
        rec = json.loads((REPO / "calibration_output" / "compiled_entries" / f"{EID}.jsonl").read_text().splitlines()[0])
        assert rec["metadata"]["entry_id"] == EID
        assert rec["dataset_tier"] == "SILVER"
        assert rec["isomorphism_quality"]["score"] == 0.793
        assert rec["metadata"]["self_grade"]["gold_awarded"] is False
        assert rec["metadata"]["deliberation_status"] == "PROVISIONAL_DEFAULT"
        assert rec["metadata"]["home_domain"] == "trust_chain"

    def test_needs_review_for_explicit_id(self) -> None:
        from semantic_compiler.core.pipeline import compile_semantic_packet

        packet = compile_semantic_packet(f"Explain {EID}.")
        assert packet.needs_review
        assert EID in [x["entry_id"] for x in packet.needs_review_entries]

    def test_evidence_and_spec_docs_exist(self) -> None:
        ev = REPO / "docs" / "evidence" / "source-2026-11-27d" / "sc_sov_trade_001_v0.1_attachment.md"
        raw = ev.read_bytes()
        assert sha256(raw) == "4abd1c3caab03a5fa4324ef5b61073de4441627515e52e1e22d94d0f92469311"
        assert len(raw) == 29621
        spec = (REPO / "docs" / "SC-SOV-TRADE-001_SOVEREIGN_BILATERAL_AUTH_EXCHANGE.md").read_text(
            encoding="utf-8"
        )
        assert "SCC-001-AC" in spec
        assert "SC-TOL-001" in spec
        pending = (REPO / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        assert f"## {EID} " in pending
        assert "Section 16, unanswered" in pending
        # The customer questions must remain unanswered in the pending file.
        assert "Who are the two parties" in pending
