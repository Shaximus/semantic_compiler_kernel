"""Item 4: RFC 3161 timestamp client and local test TSA."""

from __future__ import annotations

import pytest

from tests.sov_trade_deps import TIMESTAMP_SKIP, have_asn1crypto

pytestmark = pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP)

if have_asn1crypto():
    from semantic_compiler.sov_trade.timestamp import (
        TEST_TSA_POLICY,
        TimestampError,
        build_request,
        generate_test_tsa,
        issue_token,
        verify_token,
    )


@pytest.mark.skipif(not have_asn1crypto(), reason=TIMESTAMP_SKIP)
class TestRFC3161:
    def test_valid_token(self) -> None:
        authority = generate_test_tsa()
        data = b"signed assertion bytes"
        request = build_request(data)
        token = issue_token(authority, request)
        verify_token(
            token,
            data=data,
            nonce=request.nonce,
            trusted_ca=authority.ca_cert,
            policy=TEST_TSA_POLICY,
        )

    def test_wrong_imprint_fails(self) -> None:
        authority = generate_test_tsa()
        request = build_request(b"original")
        token = issue_token(authority, request)
        with pytest.raises(TimestampError, match="imprint"):
            verify_token(
                token,
                data=b"tampered data",
                nonce=request.nonce,
                trusted_ca=authority.ca_cert,
            )

    def test_wrong_nonce_fails(self) -> None:
        authority = generate_test_tsa()
        request = build_request(b"original", nonce=123456789)
        token = issue_token(authority, request)
        with pytest.raises(TimestampError, match="nonce"):
            verify_token(
                token,
                data=b"original",
                nonce=request.nonce + 1,
                trusted_ca=authority.ca_cert,
            )

    def test_untrusted_tsa_cert_fails(self) -> None:
        authority = generate_test_tsa()
        other = generate_test_tsa()
        request = build_request(b"original")
        token = issue_token(authority, request)
        with pytest.raises(TimestampError, match="not chained|untrusted|trusted CA"):
            verify_token(
                token,
                data=b"original",
                nonce=request.nonce,
                trusted_ca=other.ca_cert,
            )

    def test_tampered_token_fails(self) -> None:
        authority = generate_test_tsa()
        request = build_request(b"original")
        token = issue_token(authority, request)
        raw = bytearray(token.der)
        # Flip a byte in the latter half, away from the ASN.1 header.
        raw[-20] ^= 0x01
        with pytest.raises(TimestampError):
            verify_token(
                bytes(raw),
                data=b"original",
                nonce=request.nonce,
                trusted_ca=authority.ca_cert,
            )
