"""Regression tests added during the t616u verification pass.

Each test pins a defect found by KATs, property tests, fuzzing, the
OpenSSL cross-check, or a surviving mutation (see
docs/evidence/sov-trade-verify-2026-11-27/MUTATION_TABLE.md).
"""

from __future__ import annotations

import pytest

from tests.sov_trade_deps import (
    CRYPTOGRAPHY_SKIP,
    TIMESTAMP_SKIP,
    have_asn1crypto,
    have_cryptography,
)

pytestmark = pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)


def test_empty_child_scope_under_constrained_parent_is_widening() -> None:
    """Property test finding: an empty (unconstrained) child set passed
    is_subset_of a constrained parent, so a grant could widen at issuance."""
    from semantic_compiler.sov_trade.authority import DelegationScope

    parent = DelegationScope(frozenset({"certificate_of_origin"}), frozenset({"0901"}), frozenset({"b"}), 100)
    for child in (
        DelegationScope(frozenset(), frozenset({"0901"}), frozenset({"b"}), 100),
        DelegationScope(frozenset({"certificate_of_origin"}), frozenset(), frozenset({"b"}), 100),
        DelegationScope(frozenset({"certificate_of_origin"}), frozenset({"0901"}), frozenset(), 100),
    ):
        assert not child.is_subset_of(parent)
    assert DelegationScope(frozenset({"certificate_of_origin"}), frozenset({"0901"}), frozenset({"b"}), 50).is_subset_of(parent)


def test_value_ceiling_cannot_grow() -> None:
    from semantic_compiler.sov_trade.authority import DelegationScope

    parent = DelegationScope(frozenset({"x"}), frozenset({"y"}), frozenset({"z"}), 100)
    assert not DelegationScope(frozenset({"x"}), frozenset({"y"}), frozenset({"z"}), 101).is_subset_of(parent)
    assert not parent.covers("x", "y", "z", 101)
    assert parent.covers("x", "y", "z", 100)


def test_two_of_five_shares_fail_on_the_quorum_rule_itself() -> None:
    """Mutation finding: with only the commitment check, lowering the quorum
    rule still raised (tampered-commitment path). Pin the quorum message."""
    from semantic_compiler.sov_trade.ceremony import CeremonyError, reconstruct_secret, run_root_ceremony

    ceremony = run_root_ceremony(n=5, k=3)
    for pair in ((0, 1), (1, 4), (2, 3)):
        shares = [ceremony.shares[i] for i in pair]
        with pytest.raises(CeremonyError) as info:
            ceremony.sign_with_quorum(b"m", shares)
        assert "quorum not met: 2 of 3" in str(info.value)
        with pytest.raises(CeremonyError, match="quorum not met"):
            reconstruct_secret(shares, k=3)


def test_duplicate_share_does_not_count_twice() -> None:
    from semantic_compiler.sov_trade.ceremony import CeremonyError, run_root_ceremony

    ceremony = run_root_ceremony(n=5, k=3)
    s = ceremony.shares
    with pytest.raises(CeremonyError, match="quorum not met"):
        ceremony.sign_with_quorum(b"m", [s[0], s[0], s[1]])


def test_hybrid_rejects_bad_mldsa_half_with_good_ed25519_half() -> None:
    from semantic_compiler.sov_trade.crypto import (
        ALG_ED25519,
        ALG_ML_DSA_65,
        decode_hybrid_map,
        encode_hybrid_signature,
        generate_hybrid,
        sign_hybrid,
        verify_hybrid,
    )

    pair = generate_hybrid()
    sig = decode_hybrid_map(sign_hybrid(pair, b"msg"), "sig")
    other = decode_hybrid_map(sign_hybrid(pair, b"other"), "sig")
    mixed = encode_hybrid_signature({ALG_ED25519: sig[ALG_ED25519], ALG_ML_DSA_65: other[ALG_ML_DSA_65]})
    assert not verify_hybrid(pair.public_only(), b"msg", mixed)
    mixed2 = encode_hybrid_signature({ALG_ED25519: other[ALG_ED25519], ALG_ML_DSA_65: sig[ALG_ML_DSA_65]})
    assert not verify_hybrid(pair.public_only(), b"msg", mixed2)
    assert verify_hybrid(pair.public_only(), b"msg", sign_hybrid(pair, b"msg"))


def test_mldsa_context_is_bound() -> None:
    """A signature made under a different FIPS 204 context must not verify."""
    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

    from semantic_compiler.sov_trade.crypto import ALGORITHMS, ALG_ML_DSA_65, ML_DSA_CONTEXT

    key = MLDSA65PrivateKey.generate()
    pub = key.public_key().public_bytes_raw()
    assert ALGORITHMS[ALG_ML_DSA_65].verify(pub, b"m", key.sign(b"m", ML_DSA_CONTEXT))
    assert not ALGORITHMS[ALG_ML_DSA_65].verify(pub, b"m", key.sign(b"m", b"other-context"))
    assert not ALGORITHMS[ALG_ML_DSA_65].verify(pub, b"m", key.sign(b"m"))


def test_hybrid_member_type_confusion_is_value_error() -> None:
    import json

    from semantic_compiler.sov_trade.crypto import SUITE_ED25519_MLDSA65, decode_hybrid_map

    blob = json.dumps({"suite": SUITE_ED25519_MLDSA65, "members": [{"alg": ["x"], "sig": "00"}]}).encode()
    with pytest.raises(ValueError):
        decode_hybrid_map(blob, "sig")


@pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP)
class TestTimestampHardening:
    def _token(self):
        from semantic_compiler.sov_trade.timestamp import build_request, generate_test_tsa, issue_token

        tsa = generate_test_tsa()
        req = build_request(b"data", nonce=42)
        return tsa, req, issue_token(tsa, req)

    def test_token_carries_ess_signing_certificate_v2(self) -> None:
        import hashlib

        from asn1crypto import tsp

        tsa, _req, token = self._token()
        si = tsp.TimeStampResp.load(token.der)["time_stamp_token"]["content"]["signer_infos"][0]
        attrs = {a["type"].native: a["values"] for a in si["signed_attrs"]}
        cert_id = attrs["signing_certificate_v2"][0]["certs"][0]
        assert bytes(cert_id["cert_hash"]) == hashlib.sha256(tsa.tsa_der).digest()

    def test_wrong_nonce_rejected(self) -> None:
        from semantic_compiler.sov_trade.timestamp import TimestampError, verify_token

        tsa, _req, token = self._token()
        with pytest.raises(TimestampError, match="nonce"):
            verify_token(token, data=b"data", nonce=43, trusted_ca=tsa.ca_cert)

    def test_tsa_without_timestamping_eku_rejected(self) -> None:
        """A cert from the trusted CA but without id-kp-timeStamping must not
        be accepted as a TSA (RFC 3161 2.3)."""
        from datetime import datetime, timedelta, timezone

        from cryptography import x509
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

        from semantic_compiler.sov_trade.timestamp import (
            TimestampAuthority,
            TimestampError,
            build_request,
            generate_test_tsa,
            issue_token,
            verify_token,
        )

        good = generate_test_tsa()
        now = datetime.now(timezone.utc)
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        ca_key = good.ca_key
        assert ca_key is not None
        cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "not a TSA")]))
            .issuer_name(good.ca_cert.subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=1))
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=True)
            .sign(ca_key, hashes.SHA256())
        )
        rogue = TimestampAuthority(ca_cert=good.ca_cert, tsa_cert=cert, tsa_key=key, ca_key=ca_key)
        req = build_request(b"data", nonce=7)
        token = issue_token(rogue, req)
        with pytest.raises(TimestampError, match="EKU"):
            verify_token(token, data=b"data", nonce=7, trusted_ca=good.ca_cert)


def test_unsigned_or_forged_status_list_is_rejected() -> None:
    """Review finding: verify_status_list existed but the verifier never
    called it, so an unsigned status list claiming 'active' was trusted."""
    import copy

    from tests.sov_trade_cases import _happy, _issue, _pair  # type: ignore[attr-defined]
    from semantic_compiler.sov_trade.types import Outcome, ReasonCode

    a, b, ctx, _clock = _pair()
    _happy(a, b, ctx)
    ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-status-forged")
    sae = _issue(a, ctx["signer_a"], ch)
    forged = copy.deepcopy(a.status.current())
    assert forged is not None
    forged.signature = "00" * 64
    result = b.verify_assertion(
        sae, challenge=ch, issuer_keys=a.export_public_keys(), issuer_status=forged
    )
    assert result.outcome is Outcome.REJECTED
    assert ReasonCode.SIGNATURE_INVALID.value in result.reasons


def test_malformed_signature_hex_fails_closed() -> None:
    import copy

    from tests.sov_trade_cases import _happy, _pair  # type: ignore[attr-defined]
    from semantic_compiler.sov_trade.assertion import verify_sae_signatures
    from semantic_compiler.sov_trade.receipts import verify_receipt
    from semantic_compiler.sov_trade.types import ReasonCode

    a, b, ctx, _clock = _pair()
    _ch, sae, result = _happy(a, b, ctx)
    bad = copy.deepcopy(sae)
    bad.signatures[0].signature = "zz-not-hex"
    assert verify_sae_signatures(bad, a.export_public_keys()) is ReasonCode.SIGNATURE_INVALID
    receipt = b.issue_receipt(sae, result, ctx["receipt_b"])
    bad_r = copy.deepcopy(receipt)
    bad_r.signatures[0]["signature"] = "zz"
    keys = {**a.export_public_keys(), **b.export_public_keys()}
    assert verify_receipt(bad_r, keys, require_both_parties=False) is ReasonCode.SIGNATURE_INVALID


def test_authority_gate_unavailable_fails_closed(monkeypatch) -> None:
    """Static-review finding: _lattice_check returned gate_passed=True when
    the authority gate could not be imported (fail open)."""
    import sys

    from semantic_compiler.sov_trade.authority import _lattice_check

    import semantic_compiler.gates as gates_pkg

    monkeypatch.setitem(sys.modules, "semantic_compiler.gates.authority", None)
    monkeypatch.delattr(gates_pkg, "authority", raising=False)
    result = _lattice_check("ii", "os", delegated=True, scoped=True)
    assert result["gate_passed"] is False
    assert not result.get("skipped")


# ---------------------------------------------------------------------------
# Tests written for mutations that survived the full sov_trade suite
# (mutation_check.py M11, M14, M25, M33, M34; M24 is equivalent, see
# MUTATION_TABLE.md).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP)
def test_timestamp_policy_mismatch_rejected() -> None:
    """M11: a token issued under another TSA policy must not verify."""
    from semantic_compiler.sov_trade.timestamp import (
        TEST_TSA_POLICY,
        TimestampError,
        build_request,
        generate_test_tsa,
        issue_token,
        verify_token,
    )

    tsa = generate_test_tsa()
    other_policy = TEST_TSA_POLICY + ".999"
    tsa.policy = other_policy
    token = issue_token(tsa, build_request(b"data", nonce=5))
    with pytest.raises(TimestampError, match="policy"):
        verify_token(token, data=b"data", nonce=5, trusted_ca=tsa.ca_cert)
    verify_token(token, data=b"data", nonce=5, trusted_ca=tsa.ca_cert, policy=other_policy)


@pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP)
def test_timestamp_ess_hash_must_match_tsa_certificate(monkeypatch: pytest.MonkeyPatch) -> None:
    """M14: a correctly signed token whose ESSCertIDv2 hash names a different
    certificate must be rejected (RFC 5816 binding)."""
    import hashlib

    from semantic_compiler.sov_trade import timestamp as ts

    tsa = ts.generate_test_tsa()
    target = tsa.tsa_der

    class _Shim:
        def __getattr__(self, name: str):
            return getattr(hashlib, name)

        @staticmethod
        def sha256(data: bytes = b"", **kw):
            if data == target:
                return hashlib.sha256(b"some other certificate")
            return hashlib.sha256(data, **kw)

    with monkeypatch.context() as m:
        m.setattr(ts, "hashlib", _Shim())
        token = ts.issue_token(tsa, ts.build_request(b"data", nonce=9))
    with pytest.raises(ts.TimestampError, match="ESS"):
        ts.verify_token(token, data=b"data", nonce=9, trusted_ca=tsa.ca_cert)
    good = ts.issue_token(tsa, ts.build_request(b"data", nonce=9))
    ts.verify_token(good, data=b"data", nonce=9, trusted_ca=tsa.ca_cert)


def test_quorum_from_another_ceremony_cannot_sign() -> None:
    """M25: a self-consistent share set from a different ceremony passes the
    commitment check; only the published-key comparison stops it."""
    from semantic_compiler.sov_trade.ceremony import CeremonyError, run_root_ceremony

    published = run_root_ceremony(n=5, k=3)
    other = run_root_ceremony(n=5, k=3)
    with pytest.raises(CeremonyError, match="does not match the ceremony publication"):
        published.sign_with_quorum(b"m", list(other.shares[:3]))
    assert published.sign_with_quorum(b"m", list(published.shares[:3]))


def test_tampered_extra_share_rejected() -> None:
    """M24 context: with k+1 shares, a tampered extra share is rejected. The
    k-subset comparison is defence in depth: the recursive commitment check
    already rejects it, so M24 is an equivalent mutation."""
    from dataclasses import replace

    from semantic_compiler.sov_trade.ceremony import CeremonyError, run_root_ceremony

    c = run_root_ceremony(n=5, k=3)
    bad = replace(c.shares[3], data=bytes(b ^ 1 for b in c.shares[3].data))
    with pytest.raises(CeremonyError):
        c.sign_with_quorum(b"m", [c.shares[0], c.shares[1], c.shares[2], bad])


def _verify_with(challenge_override: dict):
    from dataclasses import replace

    from tests.sov_trade_cases import _issue, _pair  # type: ignore[attr-defined]

    a, b, ctx, _clock = _pair()
    ch = b.verifier.issue_challenge(issuer_domain=a.domain, txn_id="txn-bind")
    sae = _issue(a, ctx["signer_a"], ch)
    return b.verify_assertion(
        sae,
        challenge=replace(ch, **challenge_override),
        issuer_keys=a.export_public_keys(),
        issuer_status=a.status.current(),
    )


def test_wrong_challenge_nonce_rejected() -> None:
    """M33: an assertion answering another challenge nonce must be rejected."""
    from semantic_compiler.sov_trade.types import Outcome, ReasonCode

    result = _verify_with({"nonce": "00" * 32})
    assert result.outcome is Outcome.REJECTED
    assert ReasonCode.CHALLENGE_MISMATCH.value in result.reasons
    assert _verify_with({}).outcome is Outcome.ACCEPTED


def test_wrong_transaction_binding_rejected() -> None:
    """M34: same nonce, different transaction id must be rejected."""
    from semantic_compiler.sov_trade.types import Outcome, ReasonCode

    result = _verify_with({"txn_id": "txn-other"})
    assert result.outcome is Outcome.REJECTED
    assert ReasonCode.TXN_BINDING_MISMATCH.value in result.reasons


@pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP)
def test_timestamp_response_must_be_der() -> None:
    """Fuzz finding (make verify, 5000 examples): flipping the high bit of
    the status INTEGER length (0x01 -> 0x81, a zero-length INTEGER) still
    verified, because the unsigned TimeStampResp wrapper was parsed as BER."""
    from semantic_compiler.sov_trade.timestamp import (
        TimestampError,
        build_request,
        generate_test_tsa,
        issue_token,
        verify_token,
    )

    tsa = generate_test_tsa()
    token = issue_token(tsa, build_request(b"data", nonce=11))
    verify_token(token, data=b"data", nonce=11, trusted_ca=tsa.ca_cert)
    bad = bytearray(token.der)
    assert bad[4:9] == bytes.fromhex("3003020100")  # status SEQUENCE { INTEGER 0 }
    bad[7] ^= 0x80
    with pytest.raises(TimestampError):
        verify_token(bytes(bad), data=b"data", nonce=11, trusted_ca=tsa.ca_cert)


@pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP)
def test_timestamp_message_digest_binds_tstinfo() -> None:
    """M12: a change to TSTInfo that leaves imprint, nonce and policy intact
    must still be rejected. The CMS signature covers signedAttrs, so only
    the signed message-digest attribute binds those attributes to the
    encapsulated TSTInfo. The bit-flip fuzz test found this only when it
    happened to hit that content; this case is deterministic.
    """
    from asn1crypto import tsp

    from semantic_compiler.sov_trade.timestamp import (
        TimestampError,
        build_request,
        generate_test_tsa,
        issue_token,
        verify_token,
    )

    tsa = generate_test_tsa()
    token = issue_token(tsa, build_request(b"data", nonce=5))
    raw = token.der
    verify_token(raw, data=b"data", nonce=5, trusted_ca=tsa.ca_cert)
    encap = tsp.TimeStampResp.load(raw, strict=True)["time_stamp_token"]["content"]["encap_content_info"]
    old = bytes(encap["content"])
    info = tsp.TSTInfo.load(old, strict=True)
    info["serial_number"] = int(info["serial_number"].native) + 1
    new = info.dump()
    if len(new) != len(old):
        serial_der = tsp.TSTInfo.load(old, strict=True)["serial_number"].dump()
        idx = old.find(serial_der)
        assert idx >= 0
        buf = bytearray(old)
        buf[idx + len(serial_der) - 1] ^= 0x01
        new = bytes(buf)
    assert old in raw and new != old
    mutated = raw.replace(old, new, 1)
    with pytest.raises(TimestampError, match="digest"):
        verify_token(mutated, data=b"data", nonce=5, trusted_ca=tsa.ca_cert)
