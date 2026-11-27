"""RFC 3161 timestamp client and a local test TSA.

The client builds a TimeStampReq, parses the TimeStampResp, and verifies
the token: message imprint, nonce, TSA certificate chain and signature,
and the requested policy. The local TSA exists so tests can produce
valid and deliberately broken tokens without a network service.

This is a software test authority, not a public TSA or a legal time
source. Production deployments must point the client at an agreed
authority; that choice stays in section 16.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from .types import ReasonCode, TradeError

_ASN1_IMPORT_ERROR = (
    "sov_trade.timestamp requires the 'asn1crypto' package "
    "(tested with asn1crypto==1.5.1). Install it with: "
    "pip install 'asn1crypto==1.5.1'."
)

# Test-only policy OID. Not a registered public TSA policy.
TEST_TSA_POLICY = "1.3.6.1.4.1.55555.1.1"


def _asn1():
    try:
        from asn1crypto import algos, cms, core, tsp, x509 as ax509
    except ImportError as exc:
        raise ImportError(_ASN1_IMPORT_ERROR) from exc
    return algos, cms, core, tsp, ax509


class TimestampError(TradeError):
    """RFC 3161 request, token or verification failed."""


@dataclass
class TimestampAuthority:
    ca_cert: x509.Certificate
    tsa_cert: x509.Certificate
    tsa_key: rsa.RSAPrivateKey
    policy: str = TEST_TSA_POLICY

    @property
    def ca_der(self) -> bytes:
        return self.ca_cert.public_bytes(serialization.Encoding.DER)

    @property
    def tsa_der(self) -> bytes:
        return self.tsa_cert.public_bytes(serialization.Encoding.DER)


@dataclass(frozen=True)
class TimestampRequest:
    der: bytes
    imprint: bytes
    nonce: int
    policy: str
    hash_algorithm: str = "sha256"


@dataclass(frozen=True)
class TimestampToken:
    der: bytes  # TimeStampResp DER
    token_der: bytes  # TimeStampToken (ContentInfo) DER



def _signed_attrs_tbs(signed_attrs: Any) -> bytes:
    """RFC 5652: the signature is over signedAttrs encoded as SET OF, not IMPLICIT [0]."""
    der = signed_attrs.dump()
    if der and der[0] == 0xA0:
        return bytes([0x31]) + der[1:]
    return der


def generate_test_tsa(*, now: datetime | None = None) -> TimestampAuthority:
    now = now or datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "SC-SOV-TRADE-001 Test TSA CA")])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
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
        .sign(private_key=ca_key, algorithm=hashes.SHA256())
    )
    tsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    tsa_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "SC-SOV-TRADE-001 Test TSA")])
    tsa_cert = (
        x509.CertificateBuilder()
        .subject_name(tsa_name)
        .issuer_name(ca_name)
        .public_key(tsa_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.TIME_STAMPING]), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
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
        .sign(private_key=ca_key, algorithm=hashes.SHA256())
    )
    return TimestampAuthority(ca_cert=ca_cert, tsa_cert=tsa_cert, tsa_key=tsa_key)


def imprint_sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def build_request(
    data: bytes,
    *,
    nonce: int | None = None,
    policy: str = TEST_TSA_POLICY,
    cert_req: bool = True,
) -> TimestampRequest:
    algos, _cms, _core, tsp, _ax509 = _asn1()
    imprint = imprint_sha256(data)
    if nonce is None:
        nonce = int.from_bytes(os.urandom(8), "big")
    req = tsp.TimeStampReq({
        "version": 1,
        "message_imprint": {
            "hash_algorithm": {"algorithm": "sha256", "parameters": None},
            "hashed_message": imprint,
        },
        "req_policy": policy,
        "nonce": nonce,
        "cert_req": cert_req,
    })
    return TimestampRequest(der=req.dump(), imprint=imprint, nonce=nonce, policy=policy)


def issue_token(
    authority: TimestampAuthority,
    request: TimestampRequest,
    *,
    now: datetime | None = None,
) -> TimestampToken:
    algos, cms, core, tsp, ax509 = _asn1()
    now = now or datetime.now(timezone.utc)
    tst_info = tsp.TSTInfo({
        "version": 1,
        "policy": authority.policy,
        "message_imprint": {
            "hash_algorithm": {"algorithm": "sha256", "parameters": None},
            "hashed_message": request.imprint,
        },
        "serial_number": int.from_bytes(os.urandom(8), "big"),
        "gen_time": now,
        "nonce": request.nonce,
    })
    tst_der = tst_info.dump()
    digest = hashlib.sha256(tst_der).digest()
    signed_attrs = cms.CMSAttributes([
        cms.CMSAttribute({"type": "content_type", "values": ["tst_info"]}),
        cms.CMSAttribute({"type": "message_digest", "values": [digest]}),
    ])
    signature = authority.tsa_key.sign(_signed_attrs_tbs(signed_attrs), padding.PKCS1v15(), hashes.SHA256())
    tsa_asn1 = ax509.Certificate.load(authority.tsa_der)
    signer_info = cms.SignerInfo({
        "version": 1,
        "sid": cms.SignerIdentifier({
            "issuer_and_serial_number": cms.IssuerAndSerialNumber({
                "issuer": tsa_asn1.issuer,
                "serial_number": tsa_asn1.serial_number,
            })
        }),
        "digest_algorithm": {"algorithm": "sha256", "parameters": None},
        "signed_attrs": signed_attrs,
        "signature_algorithm": {"algorithm": "sha256_rsa", "parameters": None},
        "signature": signature,
    })
    signed_data = cms.SignedData({
        "version": 3,
        "digest_algorithms": [{"algorithm": "sha256", "parameters": None}],
        "encap_content_info": {
            "content_type": "tst_info",
            "content": core.ParsableOctetString(tst_der),
        },
        "certificates": [cms.CertificateChoices({"certificate": tsa_asn1})],
        "signer_infos": [signer_info],
    })
    token = cms.ContentInfo({"content_type": "signed_data", "content": signed_data})
    resp = tsp.TimeStampResp({
        "status": {"status": "granted"},
        "time_stamp_token": token,
    })
    return TimestampToken(der=resp.dump(), token_der=token.dump())


def verify_token(
    token: TimestampToken | bytes,
    *,
    data: bytes,
    nonce: int,
    trusted_ca: x509.Certificate,
    policy: str = TEST_TSA_POLICY,
) -> None:
    """Verify imprint, nonce, policy, TSA chain and CMS signature.

    Raises TimestampError with a distinct reason on each failure class.
    """
    algos, cms, core, tsp, ax509 = _asn1()
    raw = token.der if isinstance(token, TimestampToken) else token
    try:
        resp = tsp.TimeStampResp.load(raw)
    except Exception as exc:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp response is not valid ASN.1") from exc
    status = resp["status"]["status"].native
    if status not in {"granted", "granted_with_mods"}:
        raise TimestampError(ReasonCode.FAIL_CLOSED, f"timestamp status is {status}")
    info = resp["time_stamp_token"]
    if info is None or not info.contents:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp token is missing")
    signed = info["content"]
    if not isinstance(signed, cms.SignedData):
        # content may need parsing
        signed = cms.SignedData.load(info["content"].dump()) if hasattr(info["content"], "dump") else info["content"]
    encap = signed["encap_content_info"]
    content = encap["content"].parsed if hasattr(encap["content"], "parsed") else encap["content"]
    if not isinstance(content, tsp.TSTInfo):
        content = tsp.TSTInfo.load(bytes(encap["content"]))
    expected_imprint = imprint_sha256(data)
    got_imprint = bytes(content["message_imprint"]["hashed_message"])
    if got_imprint != expected_imprint:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp imprint does not match the data")
    if content["nonce"].native != nonce:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp nonce does not match the request")
    if content["policy"].dotted != policy and content["policy"].native != policy:
        # dotted vs native
        got_policy = getattr(content["policy"], "dotted", None) or str(content["policy"].native)
        if got_policy != policy:
            raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp policy does not match")
    certs = list(signed["certificates"] or [])
    if not certs:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp token carries no TSA certificate")
    tsa_asn1 = certs[0].chosen if hasattr(certs[0], "chosen") else certs[0]
    tsa_der = tsa_asn1.dump()
    tsa_cert = x509.load_der_x509_certificate(tsa_der)
    try:
        tsa_cert.verify_directly_issued_by(trusted_ca)
    except Exception as exc:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "TSA certificate is not chained to the trusted CA") from exc
    signer_infos = list(signed["signer_infos"])
    if len(signer_infos) != 1:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp token must have exactly one signer")
    signer = signer_infos[0]
    signed_attrs = signer["signed_attrs"]
    if signed_attrs is None:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp token has no signed attributes")
    # message digest over TSTInfo
    tst_der = bytes(encap["content"])
    digest = hashlib.sha256(tst_der).digest()
    attrs_native = {attr["type"].native: attr["values"] for attr in signed_attrs}
    md_values = attrs_native.get("message_digest")
    if not md_values or bytes(md_values[0]) != digest:
        raise TimestampError(ReasonCode.FAIL_CLOSED, "timestamp token signed digest does not match TSTInfo")
    try:
        tsa_cert.public_key().verify(
            bytes(signer["signature"]),
            _signed_attrs_tbs(signed_attrs),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except Exception as exc:
        raise TimestampError(ReasonCode.SIGNATURE_INVALID, "timestamp token signature is invalid") from exc
