"""Signed revocation and suspension status lists."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .canonical import canonical_json
from .crypto import PublicKey, sha256, verify_signature
from .custody import KeyStore, Officer
from .types import ReasonCode, Role


# PROVISIONAL_DEFAULT: status older than this many seconds is stale.
DEFAULT_STATUS_FRESHNESS = 15 * 60


@dataclass
class StatusEntry:
    subject: str
    state: str  # active, revoked, suspended
    as_of: int
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "state": self.state,
            "as_of": self.as_of,
            "reason": self.reason,
        }


@dataclass
class StatusList:
    domain: str
    version: int
    issued_at: int
    entries: list[StatusEntry]
    signature: str = ""
    key_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "version": self.version,
            "issued_at": self.issued_at,
            "entries": [e.to_dict() for e in self.entries],
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload()
        body["signature"] = self.signature
        body["key_id"] = self.key_id
        return body

    def digest(self) -> str:
        return sha256(canonical_json(self.payload()))

    def state_of(self, subject: str) -> StatusEntry | None:
        # Last write for the subject wins (list is append-ordered).
        found = None
        for entry in self.entries:
            if entry.subject == subject:
                found = entry
        return found


@dataclass
class StatusService:
    domain: str
    store: KeyStore
    version: int = 0
    entries: list[StatusEntry] = field(default_factory=list)
    reachable: bool = True
    lists: list[StatusList] = field(default_factory=list)

    def set_state(
        self,
        subject: str,
        state: str,
        first: Officer,
        second: Officer,
        signer_id: str,
        *,
        now: int,
        reason: str = "",
        signer: Officer | None = None,
    ) -> StatusList:
        self.store.require_dual_control(first, second, frozenset({Role.APPROVE}))
        self.entries.append(StatusEntry(subject=subject, state=state, as_of=now, reason=reason))
        return self.publish(signer_id, now=now, signer=signer)

    def publish(self, signer_id: str, *, now: int, signer: Officer | None = None) -> StatusList:
        self.version += 1
        sl = StatusList(
            domain=self.domain,
            version=self.version,
            issued_at=now,
            entries=list(self.entries),
            key_id=signer_id,
        )
        sig = self.store.sign(signer_id, canonical_json(sl.payload()), now=now, signer=signer)
        sl.signature = sig.hex()
        self.lists.append(sl)
        return sl

    def current(self) -> StatusList | None:
        if not self.reachable:
            return None
        return self.lists[-1] if self.lists else None

    def last_cached(self) -> StatusList | None:
        return self.lists[-1] if self.lists else None


def verify_status_list(status: StatusList, public: PublicKey) -> bool:
    return verify_signature(
        public, canonical_json(status.payload()), bytes.fromhex(status.signature)
    )


def evaluate_status(
    status: StatusList | None,
    subject: str,
    *,
    now: int,
    freshness: int = DEFAULT_STATUS_FRESHNESS,
    required: bool = True,
) -> ReasonCode:
    """Fail closed on unknown or stale status (R-06).

    PROVISIONAL_DEFAULT: no grace period for any document class. Section 12
    allows a bounded grace for lower-value classes; this build does not.
    """
    if status is None:
        return ReasonCode.STATUS_UNKNOWN if required else ReasonCode.OK
    if now - status.issued_at > freshness:
        return ReasonCode.STATUS_STALE
    entry = status.state_of(subject)
    if entry is None:
        # Unknown subject on a fresh list: treat as active (listed
        # implicitly). Callers that require an explicit entry can pass
        # required=True and check presence separately; default is active.
        return ReasonCode.OK
    if entry.state == "revoked":
        return ReasonCode.REVOKED
    if entry.state == "suspended":
        return ReasonCode.SUSPENDED
    return ReasonCode.OK
