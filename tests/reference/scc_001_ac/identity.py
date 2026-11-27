"""Independent principal verifier (simulated hardware root; reference only).

Key material is held here and nowhere else. The gateway and every monitor see
only key ids. A credential is accepted only if: the verifier is available; the
key id is registered and not revoked; the MAC over (principal, key, issued,
expires, nonce, request digest) is valid; the request digest matches the
exact request; the time is inside the window; and the nonce is unused.
"""

from __future__ import annotations

import hashlib
import hmac
from enum import Enum

from tests.reference.scc_001_ac.model import Credential, Request


class VerifyStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNAVAILABLE = "UNAVAILABLE"
    NO_CREDENTIAL = "NO_CREDENTIAL"
    UNKNOWN_KEY = "UNKNOWN_KEY"
    REVOKED_KEY = "REVOKED_KEY"
    WRONG_PRINCIPAL = "WRONG_PRINCIPAL"
    BAD_MAC = "BAD_MAC"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    EXPIRED = "EXPIRED"
    NOT_YET_VALID = "NOT_YET_VALID"
    REPLAY = "REPLAY"


def _mac(key: bytes, principal_id: str, key_id: str, issued_at: int, expires_at: int,
         nonce: str, digest: str) -> str:
    msg = "|".join([principal_id, key_id, str(issued_at), str(expires_at), nonce, digest]).encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


class PrincipalVerifier:
    def __init__(self, principal_id: str, keys: dict) -> None:
        self._principal_id = principal_id
        self._keys = dict(keys)        # key_id -> bytes; never exposed
        self._revoked = set()
        self._seen_nonces = set()
        self.available = True

    # --- principal-side helper (stands in for the principal's hardware token) ---
    def issue(self, key_id: str, request: Request, issued_at: int, expires_at: int, nonce: str,
              principal_id: str = None) -> Credential:
        return self.issue_for_digest(key_id, request.digest(), issued_at, expires_at, nonce, principal_id)

    def issue_for_digest(self, key_id: str, digest: str, issued_at: int, expires_at: int, nonce: str,
                         principal_id: str = None) -> Credential:
        pid = principal_id or self._principal_id
        return Credential(pid, key_id, issued_at, expires_at, nonce, digest,
                          _mac(self._keys[key_id], pid, key_id, issued_at, expires_at, nonce, digest))

    def revoke_key(self, key_id: str) -> None:
        self._revoked.add(key_id)

    def verify(self, request: Request, now: int) -> VerifyStatus:
        return self.verify_digest(request.credential, request.digest(), now)

    def verify_digest(self, c: Credential, digest: str, now: int) -> VerifyStatus:
        """Verify a credential against a request digest computed by the caller's gate
        (used by gates/authority.check_authority_transfer for FOUNDER_OVERRIDE)."""
        if not self.available:
            return VerifyStatus.UNAVAILABLE
        if c is None:
            return VerifyStatus.NO_CREDENTIAL
        if c.key_id not in self._keys:
            return VerifyStatus.UNKNOWN_KEY
        if c.key_id in self._revoked:
            return VerifyStatus.REVOKED_KEY
        if c.principal_id != self._principal_id:
            return VerifyStatus.WRONG_PRINCIPAL
        good = _mac(self._keys[c.key_id], c.principal_id, c.key_id, c.issued_at, c.expires_at, c.nonce,
                    c.request_digest)
        if not hmac.compare_digest(good, c.mac):
            return VerifyStatus.BAD_MAC
        if c.request_digest != digest:
            return VerifyStatus.DIGEST_MISMATCH
        if now < c.issued_at:
            return VerifyStatus.NOT_YET_VALID
        if now >= c.expires_at:
            return VerifyStatus.EXPIRED
        if c.nonce in self._seen_nonces:
            return VerifyStatus.REPLAY
        self._seen_nonces.add(c.nonce)
        return VerifyStatus.VERIFIED
