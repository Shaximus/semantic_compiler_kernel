"""Short fuzz pass over SC-SOV-TRADE-001 parsers (hypothesis).

Every parser that takes untrusted bytes or structures must either return
a fail-closed result or raise its documented error type, never another
exception. SOV_TRADE_FUZZ_EXAMPLES raises the example count (make verify
uses 5000); the default keeps the suite fast.
"""

from __future__ import annotations

import os

import pytest

from tests.sov_trade_deps import (
    HYPOTHESIS_SKIP,
    TIMESTAMP_SKIP,
    have_asn1crypto,
    have_hypothesis,
)

pytestmark = [
    pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP),
    pytest.mark.skipif(not have_hypothesis(), reason=HYPOTHESIS_SKIP),
]

if have_asn1crypto() and have_hypothesis():
    from hypothesis import HealthCheck, given, settings
    from hypothesis import strategies as st

    from semantic_compiler.sov_trade.canonical import CanonicalizationError, canonical_json
    from semantic_compiler.sov_trade.crypto import (
        SUITE_ED25519_MLDSA65,
        PublicKey,
        decode_hybrid_map,
        generate_hybrid,
        sign_hybrid,
        verify_hybrid,
    )
    from semantic_compiler.sov_trade.ledger import (
        verify_consistency,
        verify_inclusion,
        verify_inclusion_proof,
    )
    from semantic_compiler.sov_trade.protocol import _scope_check
    from semantic_compiler.sov_trade.timestamp import (
        TimestampError,
        build_request,
        generate_test_tsa,
        issue_token,
        verify_token,
    )
    from semantic_compiler.sov_trade.types import ReasonCode

    N = int(os.environ.get("SOV_TRADE_FUZZ_EXAMPLES", "200"))
    FUZZ = settings(max_examples=N, deadline=None, suppress_health_check=list(HealthCheck))

    any_json = st.recursive(
        st.none() | st.booleans() | st.integers() | st.floats() | st.text(max_size=8) | st.binary(max_size=8),
        lambda c: st.lists(c, max_size=4) | st.dictionaries(st.text(max_size=6) | st.integers(), c, max_size=4),
        max_leaves=20,
    )

    _TSA = generate_test_tsa()
    _DATA = b"fuzz data"
    _REQ = build_request(_DATA, nonce=1234567)
    _TOKEN = issue_token(_TSA, _REQ).der
    _HYB = generate_hybrid()
    _HSIG = sign_hybrid(_HYB, b"m")

    class TestParserFuzz:
        @FUZZ
        @given(st.binary(max_size=512))
        def test_hybrid_decode_random_bytes(self, blob) -> None:
            for field in ("public", "sig"):
                try:
                    decode_hybrid_map(blob, field)
                except ValueError:
                    pass

        @FUZZ
        @given(any_json)
        def test_hybrid_decode_random_json(self, value) -> None:
            import json
            try:
                blob = json.dumps({"suite": SUITE_ED25519_MLDSA65, "members": value}, default=repr).encode()
            except (ValueError, TypeError):
                return
            try:
                decode_hybrid_map(blob, "sig")
            except ValueError:
                pass

        @FUZZ
        @given(st.binary(max_size=256), st.integers(min_value=0, max_value=len(_HSIG) - 1), st.integers(1, 255))
        def test_hybrid_verify_mutated(self, msg, pos, flip) -> None:
            bad = bytearray(_HSIG)
            bad[pos] ^= flip
            assert verify_hybrid(_HYB.public_only(), b"m", bytes(bad)) in (True, False)
            assert verify_hybrid(PublicKey(algorithm=SUITE_ED25519_MLDSA65, public_key=msg), b"m", _HSIG) is False

        @FUZZ
        @given(any_json)
        def test_canonical_json_arbitrary(self, value) -> None:
            try:
                canonical_json(value)
            except CanonicalizationError:
                pass

        def test_canonical_json_deep_nesting(self) -> None:
            value: list = []
            for _ in range(5000):
                value = [value]
            with pytest.raises(CanonicalizationError):
                canonical_json(value)

        @FUZZ
        @given(st.binary(max_size=600))
        def test_timestamp_random_bytes(self, blob) -> None:
            with pytest.raises(TimestampError):
                verify_token(blob, data=_DATA, nonce=1234567, trusted_ca=_TSA.ca_cert)

        @FUZZ
        @given(st.integers(min_value=0, max_value=len(_TOKEN) - 1), st.integers(1, 255))
        def test_timestamp_bit_flips(self, pos, flip) -> None:
            bad = bytearray(_TOKEN)
            bad[pos] ^= flip
            try:
                verify_token(bytes(bad), data=_DATA, nonce=1234567, trusted_ca=_TSA.ca_cert)
            except TimestampError:
                return
            # A flip that still verifies must be in a part of the DER that is
            # not covered by the signature AND not semantically checked.
            # Record it: the only acceptable case is an unsigned, unchecked
            # byte (none are expected).
            pytest.fail(f"bit flip at {pos} (xor {flip}) still verified")

        @FUZZ
        @given(st.dictionaries(st.sampled_from(["seq", "leaf", "tree_size", "proof", "root", "entry", "x"]), any_json, max_size=7))
        def test_inclusion_proof_dict(self, proof) -> None:
            assert verify_inclusion_proof(proof) in (True, False)

        @FUZZ
        @given(any_json, any_json, any_json, any_json, any_json)
        def test_inclusion_and_consistency_args(self, a, b, c, d, e) -> None:
            assert verify_inclusion(a, b, c, d, e) in (True, False)
            assert verify_consistency(a, b, c, d, e) in (True, False)

        @FUZZ
        @given(any_json, any_json)
        def test_scope_check_random_chain(self, chain, subject) -> None:
            fields = {"authority_chain": chain, "doc_class": "x", "subject": subject, "txn_binding": {}}
            try:
                reason = _scope_check(fields, "v")
            except Exception as exc:  # noqa: BLE001
                pytest.fail(f"_scope_check raised {type(exc).__name__}: {exc}")
            assert isinstance(reason, ReasonCode)
