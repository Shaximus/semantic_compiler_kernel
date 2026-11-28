"""Adversarial tests for SC-SOV-TRADE-001: replay, forgery, escalation, capture, tampering."""

from __future__ import annotations

import copy

import pytest

from semantic_compiler.sov_trade import (
    CaptureError,
    DelegationScope,
    DocClass,
    FrozenClock,
    Nation,
    Outcome,
    ReasonCode,
    merge_public_keys,
    verify_receipt_offline,
)
from semantic_compiler.sov_trade.crypto import generate_ed25519
from semantic_compiler.sov_trade.types import CheckName
from tests.sov_trade_cases import (
    ORIGIN,
    _happy,
    _issue,
    _pair,
    _scope,
    _subject,
)


class TestAdversarialReplay:
    def test_old_license_on_new_shipment(self) -> None:
        a, b, ctx, _ = _pair()
        ch1, sae, first = _happy(a, b, ctx)
        assert first.verification_passed
        ch2 = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-new-shipment")
        # Replay the old envelope against a new challenge/transaction.
        result = b.verify_assertion(
            sae,
            challenge=ch2,
            issuer_keys=a.export_public_keys(),
            issuer_status=a.status.current(),
        )
        assert result.verification_passed is False
        assert result.reason_for(CheckName.BINDING) in {
            ReasonCode.CHALLENGE_MISMATCH,
            ReasonCode.TXN_BINDING_MISMATCH,
        }

    def test_same_assertion_same_transaction_replayed(self) -> None:
        a, b, ctx, _ = _pair()
        ch, sae, first = _happy(a, b, ctx)
        assert first.verification_passed
        second = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert second.reason_for(CheckName.REPLAY) is ReasonCode.REPLAYED


class TestAdversarialForgedSignature:
    def test_forged_signature_rejected(self) -> None:
        a, b, ctx, _ = _pair()
        ch, sae, _ = _happy(a, b, ctx)
        # Happy path already accepted this assertion_id; use a fresh txn.
        a2, b2, ctx2, _ = _pair()
        ch = b2.verifier.issue_challenge(issuer_domain=a2.domain, txn_id="txn-forge")
        sae = _issue(a2, ctx2["signer_a"], ch)
        rogue = generate_ed25519()
        sae.signatures[0].signature = rogue.sign(sae.signed_bytes()).hex()
        result = b2.verify_assertion(
            sae, challenge=ch, issuer_keys=a2.export_public_keys(), issuer_status=a2.status.current()
        )
        assert result.reason_for(CheckName.SIGNATURE) is ReasonCode.SIGNATURE_INVALID
        assert result.outcome is Outcome.REJECTED

    def test_channel_is_not_a_trust_anchor(self) -> None:
        """Authenticity is not inferred from who delivered the envelope."""
        a, b, ctx, _ = _pair()
        ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-channel")
        sae = _issue(a, ctx["signer_a"], ch)
        # Delivered "over a trusted courier" but with a broken signature.
        sae.signatures[0].signature = "00" * 64
        result = b.verify_assertion(
            sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=a.status.current()
        )
        assert result.reason_for(CheckName.SIGNATURE) is ReasonCode.SIGNATURE_INVALID


class TestAdversarialDelegationEscalation:
    def test_delegate_cannot_widen_scope(self) -> None:
        a, b, ctx, clock = _pair()
        parent = a.authority.current_for(ctx["signer_a"].identifier)
        from semantic_compiler.sov_trade.types import TradeError

        wider = DelegationScope(
            doc_classes=parent.scope.doc_classes | {DocClass.CUSTOMS_DECLARATION.value},
            commodity_codes=parent.scope.commodity_codes,
            counterparty_domains=parent.scope.counterparty_domains,
            value_ceiling=parent.scope.value_ceiling,
        )
        # A new child under the operational signer cannot hold more than the grantor.
        child, _ = None, None
        with pytest.raises(TradeError) as exc:
            child_prin = a.identity.create_principal(
                ctx["signer_a"].kind,
                "escalator",
                a.officers["alpha"],
                a.officers["bravo"],
                parent=ctx["signer_a"].identifier,
            )
            a.authority.issue(
                ctx["signer_a"],
                child_prin,
                wider,
                mode="operational",
                not_before=clock.now_ts(),
                not_after=clock.now_ts() + 60,
                now=clock.now_ts(),
                parent=parent,
                first=a.officers["alpha"],
                second=a.officers["bravo"],
            )
        assert exc.value.reason in {ReasonCode.SCOPE_WIDENED, ReasonCode.CAPTURE_SELF_ESCALATION}
        _ = child


class TestAdversarialCapturedAuthority:
    def test_verifier_cannot_grant_itself_authority(self) -> None:
        _, b, _, _ = _pair()
        with pytest.raises(CaptureError):
            b.authority.verifier_modify_policy()

    def test_proxy_cannot_launder_escalation_through_self(self) -> None:
        a, _, ctx, clock = _pair()
        with pytest.raises(CaptureError):
            a.authority.issue(
                ctx["signer_a"],
                ctx["signer_a"],
                _scope(b.domain if False else "nation-b"),
                mode="operational",
                not_before=clock.now_ts(),
                not_after=clock.now_ts() + 10,
                now=clock.now_ts(),
                parent=a.authority.current_for(ctx["signer_a"].identifier),
                first=a.officers["alpha"],
                second=a.officers["bravo"],
            )


class TestAdversarialTamperedReceipt:
    def test_tampered_receipt_fails_offline_verification(self) -> None:
        a, b, ctx, _ = _pair()
        _, sae, result = _happy(a, b, ctx)
        receipt = b.issue_receipt(sae, result, ctx["receipt_b"])
        a.acknowledge(receipt, ctx["receipt_a"])
        keys = merge_public_keys(a, b)
        assert verify_receipt_offline(receipt, keys) is ReasonCode.OK
        tampered = copy.deepcopy(receipt)
        tampered.fields["outcome"] = "accepted" if receipt.fields["outcome"] != "accepted" else "rejected"
        assert verify_receipt_offline(tampered, keys) is ReasonCode.SIGNATURE_INVALID

    def test_stripped_counterparty_signature_fails_when_both_required(self) -> None:
        a, b, ctx, _ = _pair()
        _, sae, result = _happy(a, b, ctx)
        receipt = b.issue_receipt(sae, result, ctx["receipt_b"])
        a.acknowledge(receipt, ctx["receipt_a"])
        keys = merge_public_keys(a, b)
        stripped = copy.deepcopy(receipt)
        stripped.signatures = [s for s in stripped.signatures if s["party"] != "issuer"]
        assert verify_receipt_offline(stripped, keys, require_both_parties=True) is ReasonCode.SIGNATURE_INVALID
