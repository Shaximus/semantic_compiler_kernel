"""Signatures, hashes and algorithm identifiers for SC-SOV-TRADE-001.

Baseline signature algorithm is Ed25519 (spec section 10). The
`cryptography` package is used when importable. Otherwise the vendored
CC0 reference in `_ed25519.py` is used so CI, which does not install
extra dependencies, can still run the suite.

ML-DSA (FIPS 204) is not implemented: no vetted library is in the
install set, and this package will not invent a post-quantum primitive.
Hybrid verification is implemented as "every listed signature must
verify"; a broken member fails the envelope (R-10).
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Iterable

from . import _ed25519 as _ref

ALG_ED25519 = "ed25519"
ALG_SHA256 = "sha-256"
ALG_SHA384 = "sha-384"

_CRYPTOGRAPHY_OK = False
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.exceptions import InvalidSignature

    _CRYPTOGRAPHY_OK = True
except Exception:  # pragma: no cover - absence is the CI path
    Ed25519PrivateKey = None  # type: ignore[assignment]
    Ed25519PublicKey = None  # type: ignore[assignment]
    InvalidSignature = Exception  # type: ignore[assignment]


def backend_name() -> str:
    return "cryptography" if _CRYPTOGRAPHY_OK else "vendored_ed25519_ref"


def side_channel_safe() -> bool:
    """The vendored fallback is not constant-time; see `_ed25519.py`."""
    return _CRYPTOGRAPHY_OK


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha384(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()


def content_hash(data: bytes, algorithm: str = ALG_SHA256) -> str:
    if algorithm == ALG_SHA256:
        return sha256(data)
    if algorithm == ALG_SHA384:
        return sha384(data)
    raise ValueError(f"unsupported hash algorithm: {algorithm}")


@dataclass(frozen=True)
class KeyPair:
    """In-memory key material. Never written to disk by this package."""

    algorithm: str
    public_key: bytes
    _secret: bytes

    def public_hex(self) -> str:
        return self.public_key.hex()

    def sign(self, message: bytes) -> bytes:
        if self.algorithm != ALG_ED25519:
            raise ValueError(f"unsupported signature algorithm: {self.algorithm}")
        if _CRYPTOGRAPHY_OK:
            key = Ed25519PrivateKey.from_private_bytes(self._secret)
            return key.sign(message)
        pk = _ref.publickey_unsafe(self._secret)
        return _ref.signature_unsafe(message, self._secret, pk)

    def public_only(self) -> "PublicKey":
        return PublicKey(algorithm=self.algorithm, public_key=self.public_key)


@dataclass(frozen=True)
class PublicKey:
    algorithm: str
    public_key: bytes

    def public_hex(self) -> str:
        return self.public_key.hex()

    def verify(self, message: bytes, signature: bytes) -> bool:
        if self.algorithm != ALG_ED25519:
            return False
        try:
            if _CRYPTOGRAPHY_OK:
                Ed25519PublicKey.from_public_bytes(self.public_key).verify(
                    signature, message
                )
                return True
            _ref.checkvalid(signature, message, self.public_key)
            return True
        except Exception:
            return False


def generate_ed25519() -> KeyPair:
    if _CRYPTOGRAPHY_OK:
        from cryptography.hazmat.primitives import serialization
        key = Ed25519PrivateKey.generate()
        secret = key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public = key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return KeyPair(algorithm=ALG_ED25519, public_key=public, _secret=secret)
    secret = secrets.token_bytes(32)
    public = _ref.publickey_unsafe(secret)
    return KeyPair(algorithm=ALG_ED25519, public_key=public, _secret=secret)


def verify_signature(public: PublicKey, message: bytes, signature: bytes) -> bool:
    return public.verify(message, signature)


def verify_all_signatures(
    members: Iterable[tuple[PublicKey, bytes, bytes]],
) -> bool:
    """Hybrid rule: every (public, message, signature) triple must verify.

    An empty member list is a failure (fail closed).
    """
    items = list(members)
    if not items:
        return False
    return all(pub.verify(msg, sig) for pub, msg, sig in items)
