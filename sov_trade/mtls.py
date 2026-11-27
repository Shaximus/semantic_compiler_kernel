"""Loopback mutual TLS 1.3 between two sovereign domains.

Certificates and CAs are generated locally for tests with
`cryptography`. This is not a national PKI. Handshakes bind to
loopback only.
"""

from __future__ import annotations

import socket
import ssl
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


@dataclass
class IssuedCert:
    cert: x509.Certificate
    key: ec.EllipticCurvePrivateKey
    cert_pem: bytes
    key_pem: bytes


@dataclass
class DomainCA:
    name: str
    cert: x509.Certificate
    key: ec.EllipticCurvePrivateKey
    cert_pem: bytes

    def crl_pem(self, revoked: list[x509.Certificate], now: datetime) -> bytes:
        builder = (
            x509.CertificateRevocationListBuilder()
            .issuer_name(self.cert.subject)
            .last_update(now - timedelta(minutes=1))
            .next_update(now + timedelta(days=7))
        )
        for cert in revoked:
            builder = builder.add_revoked_certificate(
                x509.RevokedCertificateBuilder()
                .serial_number(cert.serial_number)
                .revocation_date(now - timedelta(minutes=1))
                .build()
            )
        crl = builder.sign(private_key=self.key, algorithm=hashes.SHA256())
        return crl.public_bytes(serialization.Encoding.PEM)


def _name(common: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common)])


def generate_ca(name: str, *, now: datetime | None = None, days: int = 365) -> DomainCA:
    now = now or datetime.now(timezone.utc)
    key = ec.generate_private_key(ec.SECP256R1())
    cert = (
        x509.CertificateBuilder()
        .subject_name(_name(f"{name} Test Root CA"))
        .issuer_name(_name(f"{name} Test Root CA"))
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(private_key=key, algorithm=hashes.SHA256())
    )
    return DomainCA(
        name=name,
        cert=cert,
        key=key,
        cert_pem=cert.public_bytes(serialization.Encoding.PEM),
    )


def issue_cert(
    ca: DomainCA,
    common_name: str,
    *,
    now: datetime | None = None,
    days: int = 30,
    server: bool = False,
    loopback: bool = True,
) -> IssuedCert:
    now = now or datetime.now(timezone.utc)
    key = ec.generate_private_key(ec.SECP256R1())
    eku = [ExtendedKeyUsageOID.CLIENT_AUTH]
    if server:
        eku.append(ExtendedKeyUsageOID.SERVER_AUTH)
    san_names: list[x509.GeneralName] = [x509.DNSName("localhost")]
    if loopback:
        san_names.append(x509.IPAddress(ip_address("127.0.0.1")))
    builder = (
        x509.CertificateBuilder()
        .subject_name(_name(common_name))
        .issuer_name(ca.cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1) if days > 0 else now - timedelta(days=abs(days) + 1))
        .not_valid_after(now + timedelta(days=days) if days > 0 else now - timedelta(minutes=1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage(eku), critical=False)
        .add_extension(x509.SubjectAlternativeName(san_names), critical=False)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.CRLDistributionPoints([
            x509.DistributionPoint(
                full_name=[x509.UniformResourceIdentifier("http://127.0.0.1/crl")],
                relative_name=None,
                reasons=None,
                crl_issuer=None,
            )
        ]), critical=False)
    )
    cert = builder.sign(private_key=ca.key, algorithm=hashes.SHA256())
    return IssuedCert(
        cert=cert,
        key=key,
        cert_pem=cert.public_bytes(serialization.Encoding.PEM),
        key_pem=key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ),
    )


def client_context(
    ca_pem: bytes,
    cert: IssuedCert,
    *,
    crl_pem: bytes | None = None,
    check_hostname: bool = True,
) -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.check_hostname = check_hostname
    ctx.verify_mode = ssl.CERT_REQUIRED
    bundle = ca_pem if crl_pem is None else ca_pem + crl_pem
    ctx.load_verify_locations(cadata=bundle.decode("ascii"))
    if crl_pem is not None:
        ctx.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF
    ctx.load_cert_chain(certfile=_as_temp_pair(cert)[0], keyfile=_as_temp_pair(cert)[1])
    return ctx


# load_cert_chain needs paths; keep a tiny in-memory workaround via temp files
# scoped to the process. Callers that need many handshakes should use
# context_from_paths.

_temp_paths: dict[int, tuple[str, str]] = {}


def _as_temp_pair(cert: IssuedCert) -> tuple[str, str]:
    key = id(cert)
    if key in _temp_paths:
        return _temp_paths[key]
    import tempfile
    directory = tempfile.mkdtemp(prefix="sov-mtls-")
    cert_path = f"{directory}/cert.pem"
    key_path = f"{directory}/key.pem"
    with open(cert_path, "wb") as fh:
        fh.write(cert.cert_pem)
    with open(key_path, "wb") as fh:
        fh.write(cert.key_pem)
    _temp_paths[key] = (cert_path, key_path)
    return cert_path, key_path


def server_context(
    ca_pem: bytes,
    cert: IssuedCert,
    *,
    crl_pem: bytes | None = None,
) -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.verify_mode = ssl.CERT_REQUIRED
    bundle = ca_pem if crl_pem is None else ca_pem + crl_pem
    ctx.load_verify_locations(cadata=bundle.decode("ascii"))
    if crl_pem is not None:
        ctx.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF
    cert_path, key_path = _as_temp_pair(cert)
    ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
    return ctx


@dataclass
class HandshakeResult:
    ok: bool
    error: str | None
    server_peer: str | None
    client_peer: str | None


def handshake_loopback(
    server_ctx: ssl.SSLContext,
    client_ctx: ssl.SSLContext,
    *,
    server_hostname: str = "localhost",
    timeout: float = 3.0,
) -> HandshakeResult:
    """Run a mutual TLS handshake on 127.0.0.1 and tear the sockets down."""

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.listen(1)
    host, port = server_sock.getsockname()
    holder: dict[str, object] = {}

    def serve() -> None:
        try:
            server_sock.settimeout(timeout)
            conn, _addr = server_sock.accept()
            conn.settimeout(timeout)
            with server_ctx.wrap_socket(conn, server_side=True) as tls:
                holder["server_peer"] = tls.getpeercert()
                tls.sendall(b"ok")
        except Exception as exc:  # handshake failures are the test signal
            holder["server_error"] = f"{type(exc).__name__}: {exc}"
        finally:
            server_sock.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    client_error = None
    client_peer = None
    try:
        raw = socket.create_connection((host, port), timeout=timeout)
        raw.settimeout(timeout)
        with client_ctx.wrap_socket(raw, server_hostname=server_hostname) as tls:
            client_peer = tls.getpeercert()
            tls.recv(16)
    except Exception as exc:
        client_error = f"{type(exc).__name__}: {exc}"
    thread.join(timeout=timeout)
    server_error = holder.get("server_error")
    error = client_error or (str(server_error) if server_error else None)
    return HandshakeResult(
        ok=error is None and client_peer is not None,
        error=error,
        server_peer=_cn(holder.get("server_peer")),
        client_peer=_cn(client_peer),
    )


def _cn(cert: object) -> str | None:
    if not isinstance(cert, dict):
        return None
    subject = cert.get("subject") or ()
    for part in subject:
        for key, value in part:
            if key == "commonName":
                return str(value)
    return None
