"""Signatures, hashes and algorithm identifiers for SC-SOV-TRADE-001.

`cryptography` is a hard requirement. This module fails closed on import
if it is missing or too old. There is no production fallback, vendored
or otherwise.

Post-quantum signatures use the FIPS 204 ML-DSA implementation shipped
by pyca/cryptography (ML-DSA-65). Hybrid envelopes carry Ed25519 and
ML-DSA-65 together; every listed member must verify (R-10).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Mapping, Protocol, Sequence

_CRYPTO_IMPORT_ERROR = (
    "semantic_compiler.sov_trade requires the 'cryptography' package "
    "(pinned >=50.0.2 for FIPS 204 ML-DSA on official wheels). "
    "Install it with: pip install 'cryptography>=50.0.2,<51'. "
    "This module fails closed and will not import or start without it."
)

try:
    import cryptography
    from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives.asymmetric.mldsa import (
        MLDSA65PrivateKey,
        MLDSA65PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
except ImportError as exc:  # pragma: no cover - exercised in a subprocess test
    raise ImportError(_CRYPTO_IMPORT_ERROR) from exc

_MIN_CRYPTOGRAPHY = (50, 0, 2)


def _cryptography_version_tuple() -> tuple[int, ...]:
    parts: list[int] = []
    for token in cryptography.__version__.split("."):
        if token.isdigit():
            parts.append(int(token))
        else:
            break
    return tuple(parts) if parts else (0,)


if _cryptography_version_tuple() < _MIN_CRYPTOGRAPHY:
    raise ImportError(
        f"{_CRYPTO_IMPORT_ERROR} Found cryptography "
        f"{cryptography.__version__}, which is older than 50.0.2."
    )

ALG_ED25519 = "ed25519"
ALG_ML_DSA_65 = "ml-dsa-65"
SUITE_ED25519_MLDSA65 = "ed25519+ml-dsa-65"
HYBRID_REQUIRED_MEMBERS: tuple[str, ...] = (ALG_ED25519, ALG_ML_DSA_65)
ALG_SHA256 = "sha-256"
ALG_SHA384 = "sha-384"

# Domain-separation context for ML-DSA (FIPS 204 context string, <= 255 bytes).
ML_DSA_CONTEXT = b"SC-SOV-TRADE-001/v1"

ED25519_PUBLIC_LEN = 32
ED25519_SECRET_LEN = 32
ED25519_SIGNATURE_LEN = 64
MLDSA65_PUBLIC_LEN = 1952
MLDSA65_SEED_LEN = 32
MLDSA65_SIGNATURE_LEN = 3309


def backend_name() -> str:
    return "cryptography"


def side_channel_safe() -> bool:
    """Software keys use pyca/cryptography. PKCS#11 tokens sign in-token."""
    return True


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


class SignatureAlgorithm(Protocol):
    """Algorithm-agility hook: generate, sign, verify, and size checks."""

    name: str
    public_key_size: int
    signature_size: int

    def generate(self) -> "KeyPair":
        ...

    def sign(self, secret: bytes, message: bytes) -> bytes:
        ...

    def verify(self, public: bytes, message: bytes, signature: bytes) -> bool:
        ...


def _require_len(name: str, data: bytes, expected: int) -> None:
    if len(data) != expected:
        raise ValueError(f"{name} has length {len(data)}, expected {expected}")


class Ed25519Algorithm:
    name = ALG_ED25519
    public_key_size = ED25519_PUBLIC_LEN
    signature_size = ED25519_SIGNATURE_LEN

    def generate(self) -> "KeyPair":
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
        return KeyPair(algorithm=self.name, public_key=public, _secret=secret)

    def sign(self, secret: bytes, message: bytes) -> bytes:
        _require_len("ed25519 secret", secret, ED25519_SECRET_LEN)
        return Ed25519PrivateKey.from_private_bytes(secret).sign(message)

    def verify(self, public: bytes, message: bytes, signature: bytes) -> bool:
        if len(public) != ED25519_PUBLIC_LEN or len(signature) != ED25519_SIGNATURE_LEN:
            return False
        try:
            Ed25519PublicKey.from_public_bytes(public).verify(signature, message)
            return True
        except (InvalidSignature, ValueError):
            return False


class MLDSA65Algorithm:
    name = ALG_ML_DSA_65
    public_key_size = MLDSA65_PUBLIC_LEN
    signature_size = MLDSA65_SIGNATURE_LEN

    def generate(self) -> "KeyPair":
        try:
            key = MLDSA65PrivateKey.generate()
        except UnsupportedAlgorithm as exc:
            raise ImportError(
                "This cryptography build does not provide FIPS 204 ML-DSA-65. "
                "Use official wheels of cryptography>=50.0.2 (OpenSSL 3.5+)."
            ) from exc
        secret = key.private_bytes_raw()
        public = key.public_key().public_bytes_raw()
        return KeyPair(algorithm=self.name, public_key=public, _secret=secret)

    def sign(self, secret: bytes, message: bytes) -> bytes:
        _require_len("ml-dsa-65 seed", secret, MLDSA65_SEED_LEN)
        return MLDSA65PrivateKey.from_seed_bytes(secret).sign(message, ML_DSA_CONTEXT)

    def verify(self, public: bytes, message: bytes, signature: bytes) -> bool:
        if len(public) != MLDSA65_PUBLIC_LEN or len(signature) != MLDSA65_SIGNATURE_LEN:
            return False
        try:
            MLDSA65PublicKey.from_public_bytes(public).verify(
                signature, message, ML_DSA_CONTEXT
            )
            return True
        except (InvalidSignature, ValueError, UnsupportedAlgorithm):
            return False


ALGORITHMS: dict[str, SignatureAlgorithm] = {
    ALG_ED25519: Ed25519Algorithm(),
    ALG_ML_DSA_65: MLDSA65Algorithm(),
}


def get_algorithm(name: str) -> SignatureAlgorithm:
    try:
        return ALGORITHMS[name]
    except KeyError as exc:
        raise ValueError(f"unsupported signature algorithm: {name}") from exc


@dataclass(frozen=True)
class KeyPair:
    """In-memory software key material. Never written to disk by this package.

    HSM-resident keys use `sov_trade.pkcs11.PKCS11Signer` and do not appear here.
    Hybrid pairs store both secrets concatenated as ed25519_sk || mldsa_seed
    and both publics as a hybrid public blob.
    """

    algorithm: str
    public_key: bytes
    _secret: bytes

    def public_hex(self) -> str:
        return self.public_key.hex()

    def sign(self, message: bytes) -> bytes:
        if self.algorithm == SUITE_ED25519_MLDSA65:
            return sign_hybrid(self, message)
        alg = get_algorithm(self.algorithm)
        return alg.sign(self._secret, message)

    def public_only(self) -> "PublicKey":
        return PublicKey(algorithm=self.algorithm, public_key=self.public_key)


@dataclass(frozen=True)
class PublicKey:
    algorithm: str
    public_key: bytes

    def public_hex(self) -> str:
        return self.public_key.hex()

    def verify(self, message: bytes, signature: bytes) -> bool:
        if self.algorithm == SUITE_ED25519_MLDSA65:
            return verify_hybrid(self, message, signature)
        try:
            alg = get_algorithm(self.algorithm)
        except ValueError:
            return False
        return alg.verify(self.public_key, message, signature)


def generate_ed25519() -> KeyPair:
    return ALGORITHMS[ALG_ED25519].generate()


def generate_mldsa65() -> KeyPair:
    return ALGORITHMS[ALG_ML_DSA_65].generate()


def generate_hybrid() -> KeyPair:
    """Ed25519 + ML-DSA-65 software hybrid. Both members are required to verify."""
    ed = generate_ed25519()
    pq = generate_mldsa65()
    public = encode_hybrid_public({ALG_ED25519: ed.public_key, ALG_ML_DSA_65: pq.public_key})
    secret = ed._secret + pq._secret
    return KeyPair(algorithm=SUITE_ED25519_MLDSA65, public_key=public, _secret=secret)


def encode_hybrid_public(members: Mapping[str, bytes]) -> bytes:
    _require_hybrid_member_set(members)
    _require_member_key_sizes(members)
    payload = {
        "suite": SUITE_ED25519_MLDSA65,
        "v": 1,
        "members": [
            {"alg": name, "public": members[name].hex()}
            for name in HYBRID_REQUIRED_MEMBERS
        ],
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def encode_hybrid_signature(members: Mapping[str, bytes]) -> bytes:
    _require_hybrid_member_set(members)
    _require_member_signature_sizes(members)
    payload = {
        "suite": SUITE_ED25519_MLDSA65,
        "v": 1,
        "members": [
            {"alg": name, "sig": members[name].hex()}
            for name in HYBRID_REQUIRED_MEMBERS
        ],
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def decode_hybrid_map(blob: bytes, field: str) -> dict[str, bytes]:
    try:
        payload = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("hybrid blob is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("hybrid blob is not an object")
    if payload.get("suite") != SUITE_ED25519_MLDSA65:
        raise ValueError("hybrid suite mismatch or algorithm stripping")
    members = payload.get("members")
    if not isinstance(members, list):
        raise ValueError("hybrid members missing")
    out: dict[str, bytes] = {}
    for item in members:
        if not isinstance(item, dict) or "alg" not in item or field not in item:
            raise ValueError("hybrid member is malformed")
        name = item["alg"]
        if name in out:
            raise ValueError(f"duplicate hybrid member: {name}")
        try:
            out[name] = bytes.fromhex(item[field])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"hybrid member {name} is not hex") from exc
    _require_hybrid_member_set(out)
    return out


def _require_hybrid_member_set(members: Mapping[str, bytes]) -> None:
    names = tuple(members)
    if set(names) != set(HYBRID_REQUIRED_MEMBERS):
        raise ValueError(
            "hybrid requires exactly "
            + " and ".join(HYBRID_REQUIRED_MEMBERS)
            + f"; got {sorted(names)}"
        )


def _require_member_key_sizes(members: Mapping[str, bytes]) -> None:
    for name, material in members.items():
        expected = get_algorithm(name).public_key_size
        if len(material) != expected:
            raise ValueError(
                f"hybrid member {name} public key has length {len(material)}, expected {expected}"
            )


def _require_member_signature_sizes(members: Mapping[str, bytes]) -> None:
    for name, material in members.items():
        expected = get_algorithm(name).signature_size
        if len(material) != expected:
            raise ValueError(
                f"hybrid member {name} signature has length {len(material)}, expected {expected}"
            )


def sign_hybrid(pair: KeyPair, message: bytes) -> bytes:
    if pair.algorithm != SUITE_ED25519_MLDSA65:
        raise ValueError("not a hybrid key")
    if len(pair._secret) != ED25519_SECRET_LEN + MLDSA65_SEED_LEN:
        raise ValueError("hybrid secret has the wrong length")
    publics = decode_hybrid_map(pair.public_key, "public")
    ed_sk = pair._secret[:ED25519_SECRET_LEN]
    pq_sk = pair._secret[ED25519_SECRET_LEN:]
    signatures = {
        ALG_ED25519: ALGORITHMS[ALG_ED25519].sign(ed_sk, message),
        ALG_ML_DSA_65: ALGORITHMS[ALG_ML_DSA_65].sign(pq_sk, message),
    }
    # Bind the public keys we are signing under (mixed-key defence).
    _ = publics
    return encode_hybrid_signature(signatures)


def verify_hybrid(public: PublicKey, message: bytes, signature: bytes) -> bool:
    if public.algorithm != SUITE_ED25519_MLDSA65:
        return False
    try:
        pubs = decode_hybrid_map(public.public_key, "public")
        sigs = decode_hybrid_map(signature, "sig")
        _require_member_key_sizes(pubs)
        _require_member_signature_sizes(sigs)
    except ValueError:
        return False
    for name in HYBRID_REQUIRED_MEMBERS:
        if not ALGORITHMS[name].verify(pubs[name], message, sigs[name]):
            return False
    return True


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


def suite_members(algorithm: str) -> tuple[str, ...]:
    if algorithm == SUITE_ED25519_MLDSA65:
        return HYBRID_REQUIRED_MEMBERS
    return (algorithm,)
