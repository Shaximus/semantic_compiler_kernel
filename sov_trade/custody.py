"""In-memory dual-control key custody.

Software keys in this store still live in process memory; they are the
path used when a token is not configured. Token-resident keys use
`sov_trade.pkcs11.PKCS11Signer` and are generated non-extractable in the
token. A certified hardware module is a remaining gap (SoftHSM2 is a
software token).
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
    ) -> None:
        if first.officer_id == second.officer_id:
            raise CustodyError(
                ReasonCode.DUAL_CONTROL_REQUIRED,
                "dual control requires two distinct officers",
            )
        if first.domain != self.domain or second.domain != self.domain:
            raise CustodyError(ReasonCode.CROSS_ISSUANCE, "officer domain mismatch")
        held = first.roles | second.roles
        missing = needed - held
        if missing:
            raise CustodyError(
                ReasonCode.DUAL_CONTROL_REQUIRED,
                f"missing roles: {sorted(r.value for r in missing)}",
            )
        # A single person covering sign+approve+deploy is already rejected
        # at Officer construction. This also rejects a pair if either
        # officer somehow accumulated all three (defence in depth).
        for officer in (first, second):
            if ALL_CUSTODY_ROLES <= officer.roles:
                raise CustodyError(ReasonCode.ROLE_SEPARATION, "role separation bypass")

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

    def revoke(self, key_id: str, first: Officer, second: Officer, *, now: int) -> None:
        self.require_dual_control(first, second, frozenset({Role.APPROVE, Role.DEPLOY}))
        rec = self.get(key_id)
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
            pass
        return rec._pair.sign(message)

    def has(self, key_id: str) -> bool:
        return key_id in self._keys
