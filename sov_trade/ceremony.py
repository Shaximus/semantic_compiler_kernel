"""Software rehearsal of a 3-of-5 Shamir root-key ceremony.

This is a scripted quorum procedure for tests and dry runs. It is not a
witnessed national root ceremony and it does not replace a certified
HSM or legal ceremony controls. See
`docs/runbooks/SC-SOV-TRADE-001_ROOT_CEREMONY.md`.

Secret sharing uses GF(256) with the AES (Rijndael) polynomial, one
independent polynomial per secret byte, threshold 3 of 5 by default.
A published SHA-256 commitment of the secret (and the matching root
public key) detects a tampered share: reconstruction either disagrees
across subsets or fails to match the commitment.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from typing import Sequence

from .crypto import ALG_ED25519, KeyPair, PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from .types import ReasonCode, TradeError

DEFAULT_THRESHOLD = 3
DEFAULT_SHARES = 5
_GF_POLY = 0x11B  # x^8 + x^4 + x^3 + x + 1, same as AES


class CeremonyError(TradeError):
    """Root ceremony or share reconstruction failed."""


def _gf_add(a: int, b: int) -> int:
    return a ^ b


def _gf_mul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = ((a << 1) & 0xFF)
        if hi:
            a ^= 0x1B
        b >>= 1
    return p


def _gf_pow(a: int, e: int) -> int:
    result = 1
    base = a
    while e:
        if e & 1:
            result = _gf_mul(result, base)
        base = _gf_mul(base, base)
        e >>= 1
    return result


def _gf_inv(a: int) -> int:
    if a == 0:
        raise CeremonyError(ReasonCode.FAIL_CLOSED, "division by zero in GF(256)")
    # a^(255-1) = a^254 = inverse in a field of 256 elements
    return _gf_pow(a, 254)


def _eval_poly(coeffs: list[int], x: int) -> int:
    acc = 0
    power = 1
    for c in coeffs:
        acc = _gf_add(acc, _gf_mul(c, power))
        power = _gf_mul(power, x)
    return acc


def _lagrange_at_zero(xs: list[int], ys: list[int]) -> int:
    acc = 0
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        num = 1
        den = 1
        for j, xj in enumerate(xs):
            if i == j:
                continue
            num = _gf_mul(num, xj)  # (0 - xj) = xj in characteristic 2
            den = _gf_mul(den, xi ^ xj)
        acc = _gf_add(acc, _gf_mul(yi, _gf_mul(num, _gf_inv(den))))
    return acc


@dataclass(frozen=True)
class Share:
    index: int  # x-coordinate, 1..n
    data: bytes
    # Commitment is SHA-256 of the secret. It is not secret; it is published
    # at the ceremony so a reconstructed value can be checked.
    commitment: str

    def to_record(self) -> dict[str, str | int]:
        return {"index": self.index, "data": self.data.hex(), "commitment": self.commitment}


def commit_secret(secret: bytes) -> str:
    return hashlib.sha256(secret).hexdigest()


def split_secret(
    secret: bytes,
    *,
    n: int = DEFAULT_SHARES,
    k: int = DEFAULT_THRESHOLD,
    rng: secrets.SystemRandom | None = None,
) -> list[Share]:
    if k < 2 or n < k:
        raise CeremonyError(ReasonCode.FAIL_CLOSED, "need 2 <= k <= n")
    if not secret:
        raise CeremonyError(ReasonCode.FAIL_CLOSED, "refusing to split an empty secret")
    rng = rng or secrets.SystemRandom()
    commitment = commit_secret(secret)
    shares_data = [bytearray(len(secret)) for _ in range(n)]
    for pos, byte in enumerate(secret):
        coeffs = [byte] + [rng.randrange(256) for _ in range(k - 1)]
        # Ensure at least one higher coefficient is non-zero so the
        # polynomial actually has degree k-1 with overwhelming probability;
        # if all random coeffs are zero, force the last one.
        if all(c == 0 for c in coeffs[1:]):
            coeffs[-1] = 1
        for i in range(n):
            x = i + 1
            shares_data[i][pos] = _eval_poly(coeffs, x)
    return [
        Share(index=i + 1, data=bytes(shares_data[i]), commitment=commitment)
        for i in range(n)
    ]


def reconstruct_secret(shares: Sequence[Share], *, k: int = DEFAULT_THRESHOLD) -> bytes:
    unique: dict[int, Share] = {}
    for share in shares:
        if share.index <= 0 or share.index > 255:
            raise CeremonyError(ReasonCode.FAIL_CLOSED, "share index out of range")
        if share.index in unique and unique[share.index].data != share.data:
            raise CeremonyError(ReasonCode.FAIL_CLOSED, "conflicting shares for the same index")
        unique[share.index] = share
    if len(unique) < k:
        raise CeremonyError(
            ReasonCode.FAIL_CLOSED,
            f"quorum not met: {len(unique)} of {k} shares",
        )
    chosen = list(unique.values())[:k]
    lengths = {len(s.data) for s in chosen}
    if len(lengths) != 1:
        raise CeremonyError(ReasonCode.FAIL_CLOSED, "share lengths disagree")
    commitments = {s.commitment for s in chosen}
    if len(commitments) != 1:
        raise CeremonyError(ReasonCode.FAIL_CLOSED, "share commitments disagree")
    commitment = next(iter(commitments))
    length = next(iter(lengths))
    xs = [s.index for s in chosen]
    secret = bytearray(length)
    for pos in range(length):
        ys = [s.data[pos] for s in chosen]
        secret[pos] = _lagrange_at_zero(xs, ys)
    material = bytes(secret)
    if not hmac.compare_digest(commit_secret(material), commitment):
        raise CeremonyError(
            ReasonCode.FAIL_CLOSED,
            "reconstructed secret does not match the published commitment (tampered share)",
        )
    # If more than k shares were supplied, every k-subset must agree.
    extras = list(unique.values())
    if len(extras) > k:
        from itertools import combinations
        for combo in combinations(extras, k):
            trial = reconstruct_secret(combo, k=k)
            if trial != material:
                raise CeremonyError(
                    ReasonCode.FAIL_CLOSED,
                    "share subsets disagree; at least one share is tampered",
                )
    return material


# Forward reference hack avoided by alias after definition


def ed25519_keypair_from_secret(secret: bytes) -> KeyPair:
    if len(secret) != 32:
        raise CeremonyError(ReasonCode.FAIL_CLOSED, "root secret must be 32 bytes for Ed25519")
    key = Ed25519PrivateKey.from_private_bytes(secret)
    public = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return KeyPair(algorithm=ALG_ED25519, public_key=public, _secret=secret)


def generate_root_secret() -> bytes:
    return Ed25519PrivateKey.generate().private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )


@dataclass(frozen=True)
class CeremonyResult:
    public: PublicKey
    commitment: str
    shares: tuple[Share, ...]
    threshold: int
    share_count: int

    def sign_with_quorum(self, message: bytes, shares: Sequence[Share]) -> bytes:
        secret = reconstruct_secret(shares, k=self.threshold)
        pair = ed25519_keypair_from_secret(secret)
        if pair.public_key != self.public.public_key:
            raise CeremonyError(
                ReasonCode.FAIL_CLOSED,
                "reconstructed root public key does not match the ceremony publication",
            )
        return pair.sign(message)


def run_root_ceremony(
    *,
    n: int = DEFAULT_SHARES,
    k: int = DEFAULT_THRESHOLD,
    secret: bytes | None = None,
) -> CeremonyResult:
    """Scripted 3-of-5 (by default) split of root signing material."""
    material = secret if secret is not None else generate_root_secret()
    pair = ed25519_keypair_from_secret(material)
    shares = split_secret(material, n=n, k=k)
    # The software rehearsal drops the unsplit secret here. Custodians keep
    # only their shares. Tests hold shares in memory; they must not be committed.
    del material
    return CeremonyResult(
        public=pair.public_only(),
        commitment=shares[0].commitment,
        shares=tuple(shares),
        threshold=k,
        share_count=n,
    )
