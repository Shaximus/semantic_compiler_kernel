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


@pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)
class TestMutualTLSRejectionReasons:
    """Each rejection must fail for the RIGHT reason, not just fail."""

    def _setup(self):
        now = datetime.now(timezone.utc)
        ca_a = generate_ca("Nation-A", now=now)
        ca_b = generate_ca("Nation-B", now=now)
        return now, ca_a, ca_b

    def test_expired_client_cert_reason(self) -> None:
        now, ca_a, ca_b = self._setup()
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        expired = issue_cert(ca_a, "nation-a.example", now=now, days=-1)
        result = handshake_loopback(server_context(ca_a.cert_pem, server), client_context(ca_b.cert_pem, expired))
        assert result.ok is False
        assert "CERTIFICATE_EXPIRED" in (result.error or "").upper()

    def test_expired_server_cert_reason(self) -> None:
        now, ca_a, ca_b = self._setup()
        server = issue_cert(ca_b, "nation-b.example", now=now, days=-1, server=True)
        client = issue_cert(ca_a, "nation-a.example", now=now)
        result = handshake_loopback(server_context(ca_a.cert_pem, server), client_context(ca_b.cert_pem, client))
        assert result.ok is False
        assert "expired" in (result.error or "").lower()

    def test_client_without_certificate_is_rejected(self) -> None:
        import ssl

        now, ca_a, ca_b = self._setup()
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        bare = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        bare.load_verify_locations(cadata=ca_b.cert_pem.decode("ascii"))
        result = handshake_loopback(server_context(ca_a.cert_pem, server), bare)
        assert result.ok is False
        assert "CERTIFICATE_REQUIRED" in (result.error or "").upper()

    def test_tls12_client_is_rejected(self) -> None:
        import ssl

        from semantic_compiler.sov_trade import mtls

        now, ca_a, ca_b = self._setup()
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        client = issue_cert(ca_a, "nation-a.example", now=now)
        old = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        old.maximum_version = ssl.TLSVersion.TLSv1_2
        old.load_verify_locations(cadata=ca_b.cert_pem.decode("ascii"))
        mtls._load_issued_chain(old, client)
        result = handshake_loopback(server_context(ca_a.cert_pem, server), old)
        assert result.ok is False
        assert "PROTOCOL_VERSION" in (result.error or "").upper()

    def test_contexts_pin_tls13_and_require_peer_certs(self) -> None:
        import ssl

        now, ca_a, ca_b = self._setup()
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        client = issue_cert(ca_a, "nation-a.example", now=now)
        sctx = server_context(ca_a.cert_pem, server)
        cctx = client_context(ca_b.cert_pem, client)
        for ctx in (sctx, cctx):
            assert ctx.minimum_version is ssl.TLSVersion.TLSv1_3
            assert ctx.verify_mode is ssl.CERT_REQUIRED
        assert cctx.check_hostname is True

    def test_client_cert_cannot_act_as_server(self) -> None:
        now, ca_a, ca_b = self._setup()
        not_a_server = issue_cert(ca_b, "nation-b.example", now=now, server=False)
        client = issue_cert(ca_a, "nation-a.example", now=now)
        result = handshake_loopback(server_context(ca_a.cert_pem, not_a_server), client_context(ca_b.cert_pem, client))
        assert result.ok is False
        assert "purpose" in (result.error or "").lower()

    def test_hostname_mismatch_is_rejected(self) -> None:
        now, ca_a, ca_b = self._setup()
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        client = issue_cert(ca_a, "nation-a.example", now=now)
        result = handshake_loopback(
            server_context(ca_a.cert_pem, server),
            client_context(ca_b.cert_pem, client),
            server_hostname="attacker.example",
        )
        assert result.ok is False
        assert "hostname mismatch" in (result.error or "").lower()

    def test_revoked_client_reason(self) -> None:
        now, ca_a, ca_b = self._setup()
        server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
        client = issue_cert(ca_a, "nation-a.example", now=now)
        crl = ca_a.crl_pem([client.cert], now)
        result = handshake_loopback(
            server_context(ca_a.cert_pem, server, crl_pem=crl), client_context(ca_b.cert_pem, client)
        )
        assert result.ok is False
        assert "REVOKED" in (result.error or "").upper()


    def test_each_context_serves_its_own_certificate(self) -> None:
        """Regression: contexts must never pick up another (garbage-collected)
        certificate's files. Build many short-lived certs and check the peer
        names seen on both sides of every handshake."""
        import gc

        now, ca_a, ca_b = self._setup()
        for i in range(12):
            server = issue_cert(ca_b, f"server-{i}.example", now=now, server=True)
            client = issue_cert(ca_a, f"client-{i}.example", now=now)
            result = handshake_loopback(
                server_context(ca_a.cert_pem, server), client_context(ca_b.cert_pem, client)
            )
            assert result.ok, result.error
            assert result.client_peer == f"server-{i}.example"
            assert result.server_peer == f"client-{i}.example"
            del server, client
            gc.collect()


@pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)
def test_crl_enabled_server_accepts_unrevoked_client() -> None:
    """Regression: CRLs passed via cadata were silently dropped, so CRL
    checking rejected EVERY client (unknown CA) and the revoked-cert test
    passed for the wrong reason."""
    now = datetime.now(timezone.utc)
    ca_a = generate_ca("Nation-A", now=now)
    ca_b = generate_ca("Nation-B", now=now)
    server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
    revoked = issue_cert(ca_a, "nation-a-old.example", now=now)
    good = issue_cert(ca_a, "nation-a.example", now=now)
    crl = ca_a.crl_pem([revoked.cert], now)
    sctx = server_context(ca_a.cert_pem, server, crl_pem=crl)
    assert sctx.cert_store_stats()["crl"] == 1
    result = handshake_loopback(sctx, client_context(ca_b.cert_pem, good))
    assert result.ok, result.error
