"""In-memory dual-control key custody.

Software keys in this store still live in process memory; they are the
path used when a token is not configured. Token-resident keys use
`sov_trade.pkcs11.PKCS11Signer` and are generated non-extractable in the
token. A certified hardware module is a remaining gap (SoftHSM2 is a
software token).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .crypto import (
    ALG_ED25519,
    SUITE_ED25519_MLDSA65,
    KeyPair,
    PublicKey,
    generate_ed25519,
    generate_hybrid,
    generate_mldsa65,
)
from .types import ActorKind, CustodyError, ReasonCode, Role

if TYPE_CHECKING:
    from .ceremony import CeremonyResult



from itertools import permutations


def _distinct_assignment(officers: tuple[Officer, ...], needed: frozenset[Role]) -> bool:
    """True if each role in `needed` can be given to a different officer who holds it."""
    roles = list(needed)
    if len(officers) < len(roles):
        return False
    for pick in permutations(officers, len(roles)):
        if all(role in officer.roles for role, officer in zip(roles, pick, strict=True)):
            return True
    return False


ALL_CUSTODY_ROLES = frozenset({Role.SIGN, Role.APPROVE, Role.DEPLOY})


@dataclass(frozen=True)
class Officer:
    officer_id: str
    domain: str
    roles: frozenset[Role]

    def __post_init__(self) -> None:
        if ALL_CUSTODY_ROLES <= self.roles:
            raise CustodyError(
                ReasonCode.ROLE_SEPARATION,
                "no single officer may hold sign, approve and deploy",
            )
        if not self.roles:
            raise CustodyError(ReasonCode.ROLE_SEPARATION, "officer has no roles")


@dataclass
class KeyRecord:
    key_id: str
    kind: ActorKind
    domain: str
    public: PublicKey
    _pair: KeyPair
    expires_at: int | None = None
    revoked: bool = False
    cutover_before: int | None = None  # old key valid only for assertions ts < this


@dataclass
class KeyStore:
    """Process-local key store. Keys are never written to disk."""

    domain: str
    _keys: dict[str, KeyRecord] = field(default_factory=dict)
    _officers: dict[str, Officer] = field(default_factory=dict)

    def register_officer(self, officer: Officer) -> None:
        if officer.domain != self.domain:
            raise CustodyError(ReasonCode.CROSS_ISSUANCE, "officer domain mismatch")
        if officer.officer_id in self._officers:
            raise CustodyError(ReasonCode.DUAL_CONTROL_REQUIRED, "officer already registered")
        self._officers[officer.officer_id] = officer

    def get_officer(self, officer_id: str) -> Officer:
        try:
            return self._officers[officer_id]
        except KeyError as exc:
            raise CustodyError(ReasonCode.DUAL_CONTROL_REQUIRED, "unknown officer") from exc

    def require_dual_control(
        self,
        first: Officer,
        second: Officer,
        needed: frozenset[Role],
        *extra: Officer,
    ) -> None:
        """Require a distinct officer for each role in `needed`.

        The union of roles is not enough: one officer may be assigned at
        most one of the required roles, even if they hold more than one.
        `extra` holds any officers beyond the original pair (a third
        officer for national-root {APPROVE, SIGN, DEPLOY}).
        """
        officers = (first, second, *extra)
        ids = [o.officer_id for o in officers]
        if len(set(ids)) != len(ids):
            raise CustodyError(
                ReasonCode.DUAL_CONTROL_REQUIRED,
                "dual control requires distinct officers (the same officer cannot fill two roles)",
            )
        if any(o.domain != self.domain for o in officers):
            raise CustodyError(ReasonCode.CROSS_ISSUANCE, "officer domain mismatch")
        for officer in officers:
            if ALL_CUSTODY_ROLES <= officer.roles:
                raise CustodyError(ReasonCode.ROLE_SEPARATION, "role separation bypass")
        if not _distinct_assignment(officers, needed):
            raise CustodyError(
                ReasonCode.DUAL_CONTROL_REQUIRED,
                "no distinct-officer assignment covers the required roles "
                f"{sorted(r.value for r in needed)}",
            )

    def generate_key(
        self,
        key_id: str,
        kind: ActorKind,
        first: Officer,
        second: Officer,
        *,
        expires_at: int | None = None,
        algorithm: str = ALG_ED25519,
    ) -> KeyRecord:
        if kind is ActorKind.NATIONAL_ROOT:
            raise CustodyError(
                ReasonCode.DUAL_CONTROL_REQUIRED,
                "national-root keys must be created with generate_root (3-of-5 ceremony)",
            )
        self.require_dual_control(first, second, frozenset({Role.APPROVE, Role.DEPLOY}))
        if key_id in self._keys:
            raise CustodyError(ReasonCode.DUAL_CONTROL_REQUIRED, "key id already exists")
        if algorithm == ALG_ED25519:
            pair = generate_ed25519()
        elif algorithm == "ml-dsa-65":
            pair = generate_mldsa65()
        elif algorithm == SUITE_ED25519_MLDSA65:
            pair = generate_hybrid()
        else:
            raise CustodyError(ReasonCode.FAIL_CLOSED, f"unsupported custody algorithm: {algorithm}")
        record = KeyRecord(
            key_id=key_id,
            kind=kind,
            domain=self.domain,
            public=pair.public_only(),
            _pair=pair,
            expires_at=expires_at,
        )
        self._keys[key_id] = record
        return record

    def get(self, key_id: str) -> KeyRecord:
        try:
            return self._keys[key_id]
        except KeyError as exc:
            raise CustodyError(ReasonCode.CHAIN_INVALID, f"unknown key {key_id}") from exc

    def public_for(self, key_id: str) -> PublicKey:
        return self.get(key_id).public

    def generate_root(
        self,
        key_id: str,
        first: Officer,
        second: Officer,
        third: Officer,
        *,
        n: int = 5,
        k: int = 3,
        expires_at: int | None = None,
    ) -> tuple[KeyRecord, "CeremonyResult"]:
        """Create a national-root key through the 3-of-5 ceremony path.

        Provisional (t617u): generation needs the same three distinct
        officers as a root grant ({APPROVE, SIGN, DEPLOY}). The unsplit
        secret is used once to populate the in-memory KeyRecord (a known
        rehearsal gap) and is then dropped; grants sign through the
        returned CeremonyResult, not only this in-memory key.
        """
        from .ceremony import ed25519_keypair_from_secret, generate_root_secret, run_root_ceremony

        self.require_dual_control(
            first, second, frozenset({Role.APPROVE, Role.SIGN, Role.DEPLOY}), third
        )
        if key_id in self._keys:
            raise CustodyError(ReasonCode.DUAL_CONTROL_REQUIRED, "key id already exists")
        material = generate_root_secret()
        ceremony = run_root_ceremony(secret=material, n=n, k=k)
        pair = ed25519_keypair_from_secret(material)
        del material
        record = KeyRecord(
            key_id=key_id,
            kind=ActorKind.NATIONAL_ROOT,
            domain=self.domain,
            public=pair.public_only(),
            _pair=pair,
            expires_at=expires_at,
        )
        self._keys[key_id] = record
        return record, ceremony

    def revoke(
        self,
        key_id: str,
        first: Officer,
        second: Officer,
        *,
        now: int,
        third: Officer | None = None,
    ) -> None:
        rec = self.get(key_id)
        if rec.kind is ActorKind.NATIONAL_ROOT:
            # Provisional (t617u): root revoke is at least as strict as a
            # root grant — three distinct officers, one each of APPROVE,
            # SIGN and DEPLOY. Flagged for Shax as an explicit decision.
            if third is None:
                raise CustodyError(
                    ReasonCode.DUAL_CONTROL_REQUIRED,
                    "revoking a national-root key requires three distinct officers",
                )
            self.require_dual_control(
                first, second, frozenset({Role.APPROVE, Role.SIGN, Role.DEPLOY}), third
            )
        else:
            self.require_dual_control(first, second, frozenset({Role.APPROVE, Role.DEPLOY}))
        rec.revoked = True

    def sign(self, key_id: str, message: bytes, *, now: int, signer: Officer | None = None) -> bytes:
        rec = self.get(key_id)
        if rec.revoked:
            raise CustodyError(ReasonCode.REVOKED, "signing key revoked")
        if rec.expires_at is not None and now >= rec.expires_at:
            raise CustodyError(ReasonCode.EXPIRED, "signing key expired")
        if rec.kind is ActorKind.NATIONAL_ROOT:
            # Roots may sign issuer certificates and delegations, never assertions.
            # The assertion layer enforces the "never signs assertions" rule.
            if signer is None:
                raise CustodyError(
                    ReasonCode.DUAL_CONTROL_REQUIRED,
                    "national-root sign requires a signer holding Role.SIGN",
                )
            if signer.domain != self.domain:
                raise CustodyError(ReasonCode.CROSS_ISSUANCE, "officer domain mismatch")
            if Role.SIGN not in signer.roles:
                raise CustodyError(
                    ReasonCode.ROLE_SEPARATION,
                    "national-root signer must hold Role.SIGN",
                )
        return rec._pair.sign(message)

    def has(self, key_id: str) -> bool:
        return key_id in self._keys
