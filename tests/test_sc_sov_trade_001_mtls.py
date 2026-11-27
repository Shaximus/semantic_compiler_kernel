"""Item 5: loopback mutual TLS with locally generated test CAs."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography

pytestmark = pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)

if have_cryptography():
    from semantic_compiler.sov_trade.mtls import (
        client_context,
        generate_ca,
        handshake_loopback,
        issue_cert,
        server_context,
    )


@pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)
class TestMutualTLS:
    def _pair(self):
        now = datetime.now(timezone.utc)
        ca_a = generate_ca("Nation-A", now=now)
        ca_b = generate_ca("Nation-B", now=now)
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        client = issue_cert(ca_a, "nation-a.example", now=now, server=False)
        return ca_a, ca_b, server, client

    def test_valid_handshake(self) -> None:
        ca_a, ca_b, server, client = self._pair()
        # Each side trusts the other's CA and presents its own cert.
        server_ctx = server_context(ca_a.cert_pem, server)
        client_ctx = client_context(ca_b.cert_pem, client)
        result = handshake_loopback(server_ctx, client_ctx)
        assert result.ok, result.error
        # client_peer is the server certificate as seen by the client.
        assert result.client_peer == "nation-b.example"
        assert result.server_peer == "nation-a.example"

    def test_expired_cert_rejected(self) -> None:
        now = datetime.now(timezone.utc)
        ca_a = generate_ca("Nation-A", now=now)
        ca_b = generate_ca("Nation-B", now=now)
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        expired = issue_cert(ca_a, "nation-a.example", now=now, days=-1, server=False)
        server_ctx = server_context(ca_a.cert_pem, server)
        client_ctx = client_context(ca_b.cert_pem, expired)
        result = handshake_loopback(server_ctx, client_ctx)
        assert result.ok is False
        assert result.error is not None

    def test_wrong_ca_rejected(self) -> None:
        ca_a, ca_b, server, client = self._pair()
        stranger = generate_ca("Stranger")
        # Client trusts the wrong CA (stranger) instead of Nation B's CA.
        server_ctx = server_context(ca_a.cert_pem, server)
        client_ctx = client_context(stranger.cert_pem, client)
        result = handshake_loopback(server_ctx, client_ctx)
        assert result.ok is False
        assert result.error is not None

    def test_revoked_cert_rejected(self) -> None:
        now = datetime.now(timezone.utc)
        ca_a = generate_ca("Nation-A", now=now)
        ca_b = generate_ca("Nation-B", now=now)
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        client = issue_cert(ca_a, "nation-a.example", now=now, server=False)
        crl = ca_a.crl_pem([client.cert], now)
        server_ctx = server_context(ca_a.cert_pem, server, crl_pem=crl)
        client_ctx = client_context(ca_b.cert_pem, client)
        result = handshake_loopback(server_ctx, client_ctx)
        assert result.ok is False
        assert result.error is not None
