"""Append-only, hash-chained ledgers with Merkle checkpoints."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Any

from .canonical import canonical_json
from .crypto import sha256
from .custody import KeyStore
from .types import ReasonCode


# ---------------------------------------------------------------------------
# RFC 9162 (Certificate Transparency v2) Merkle tree, section 2.1.
#
# Leaf hash  = SHA-256(0x00 || leaf_data)
# Node hash  = SHA-256(0x01 || left || right)
# MTH({})    = SHA-256("")
# The tree splits at the largest power of two smaller than n, so a tree
# of n leaves is never confused with a tree of n + 1 leaves (no
# last-node duplication). Inclusion proofs bind the leaf index and the
# tree size; consistency proofs show an older tree is a prefix of a
# newer one. Hashes are carried as lowercase hex strings.
# ---------------------------------------------------------------------------

_LEAF_PREFIX = b"\x00"
_NODE_PREFIX = b"\x01"


def _h(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _leaf(data: bytes) -> str:
    return _h(_LEAF_PREFIX + data).hex()


def _node_bytes(left: bytes, right: bytes) -> bytes:
    return _h(_NODE_PREFIX + left + right)


def _node(left: str, right: str) -> str:
    return _node_bytes(bytes.fromhex(left), bytes.fromhex(right)).hex()


def _split(n: int) -> int:
    """Largest power of two strictly smaller than n (n >= 2)."""
    k = 1
    while k << 1 < n:
        k <<= 1
    return k


def _mth(leaves: list[bytes]) -> bytes:
    n = len(leaves)
    if n == 0:
        return _h(b"")
    if n == 1:
        return leaves[0]
    k = _split(n)
    return _node_bytes(_mth(leaves[:k]), _mth(leaves[k:]))


def _from_hex_list(values: list[str]) -> list[bytes]:
    return [bytes.fromhex(v) for v in values]


def merkle_root(leaves: list[str]) -> str:
    """RFC 9162 Merkle Tree Hash over leaf hashes (hex)."""
    return _mth(_from_hex_list(leaves)).hex()


def _path(m: int, leaves: list[bytes]) -> list[bytes]:
    n = len(leaves)
    if n <= 1:
        return []
    k = _split(n)
    if m < k:
        return _path(m, leaves[:k]) + [_mth(leaves[k:])]
    return _path(m - k, leaves[k:]) + [_mth(leaves[:k])]


def merkle_proof(leaves: list[str], index: int) -> list[str]:
    """RFC 9162 section 2.1.3.1 inclusion path for leaf *index*."""
    if index < 0 or index >= len(leaves):
        raise IndexError("leaf index out of range")
    return [h.hex() for h in _path(index, _from_hex_list(leaves))]


def _is_hash_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        bytes.fromhex(value)
    except ValueError:
        return False
    return value == value.lower()


def verify_inclusion(leaf: str, index: int, tree_size: int, proof: list[str], root: str) -> bool:
    """RFC 9162 section 2.1.3.2 inclusion verification. Fails closed."""
    if not isinstance(index, int) or not isinstance(tree_size, int):
        return False
    if isinstance(index, bool) or isinstance(tree_size, bool):
        return False
    if index < 0 or tree_size <= 0 or index >= tree_size:
        return False
    if not _is_hash_hex(leaf) or not _is_hash_hex(root):
        return False
    if not isinstance(proof, list) or not all(_is_hash_hex(p) for p in proof):
        return False
    fn, sn = index, tree_size - 1
    r = bytes.fromhex(leaf)
    for p_hex in proof:
        p = bytes.fromhex(p_hex)
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            r = _node_bytes(p, r)
            if not fn & 1:
                while True:
                    fn >>= 1
                    sn >>= 1
                    if fn & 1 or fn == 0:
                        break
        else:
            r = _node_bytes(r, p)
        fn >>= 1
        sn >>= 1
    return sn == 0 and hmac.compare_digest(r, bytes.fromhex(root))


def _subproof(m: int, leaves: list[bytes], complete: bool) -> list[bytes]:
    n = len(leaves)
    if m == n:
        return [] if complete else [_mth(leaves)]
    k = _split(n)
    if m <= k:
        return _subproof(m, leaves[:k], complete) + [_mth(leaves[k:])]
    return _subproof(m - k, leaves[k:], False) + [_mth(leaves[:k])]


def consistency_proof(leaves: list[str], first_size: int) -> list[str]:
    """RFC 9162 section 2.1.4.1 proof that the first *first_size* leaves
    are a prefix of *leaves*."""
    n = len(leaves)
    if first_size <= 0 or first_size > n:
        raise ValueError("first_size out of range")
    if first_size == n:
        return []
    return [h.hex() for h in _subproof(first_size, _from_hex_list(leaves), True)]


def verify_consistency(
    first_size: int,
    second_size: int,
    first_root: str,
    second_root: str,
    proof: list[str],
) -> bool:
    """RFC 9162 section 2.1.4.2 consistency verification. Fails closed."""
    for v in (first_size, second_size):
        if not isinstance(v, int) or isinstance(v, bool):
            return False
    if first_size <= 0 or second_size < first_size:
        return False
    if not _is_hash_hex(first_root) or not _is_hash_hex(second_root):
        return False
    if not isinstance(proof, list) or not all(_is_hash_hex(p) for p in proof):
        return False
    if first_size == second_size:
        return proof == [] and hmac.compare_digest(first_root, second_root)
    path = _from_hex_list(proof)
    if first_size & (first_size - 1) == 0:
        # first_size is an exact power of two: its root is the first node.
        path = [bytes.fromhex(first_root)] + path
    if not path:
        return False
    fn, sn = first_size - 1, second_size - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1
    fr = sr = path[0]
    for c in path[1:]:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            fr = _node_bytes(c, fr)
            sr = _node_bytes(c, sr)
            if not fn & 1:
                while True:
                    fn >>= 1
                    sn >>= 1
                    if fn & 1 or fn == 0:
                        break
        else:
            sr = _node_bytes(sr, c)
        fn >>= 1
        sn >>= 1
    return (
        sn == 0
        and hmac.compare_digest(fr, bytes.fromhex(first_root))
        and hmac.compare_digest(sr, bytes.fromhex(second_root))
    )


@dataclass
class LedgerEntry:
    seq: int
    prev_hash: str
    body_hash: str
    body: dict[str, Any]
    issued_at: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "prev_hash": self.prev_hash,
            "body_hash": self.body_hash,
            "body": self.body,
            "issued_at": self.issued_at,
        }

    def leaf_hash(self) -> str:
        return _leaf(canonical_json(self.to_dict()))


@dataclass
class Checkpoint:
    domain: str
    seq: int
    root: str
    issued_at: int
    signature: str = ""
    key_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "seq": self.seq,
            "root": self.root,
            "issued_at": self.issued_at,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload()
        body["signature"] = self.signature
        body["key_id"] = self.key_id
        return body


@dataclass
class Ledger:
    domain: str
    store: KeyStore
    entries: list[LedgerEntry] = field(default_factory=list)
    checkpoints: list[Checkpoint] = field(default_factory=list)
    # Checkpoints received from the counterpart.
    peer_checkpoints: list[Checkpoint] = field(default_factory=list)
    acceptance_halted: bool = False
    halt_reason: str = ""

    def append(self, body: dict[str, Any], *, now: int) -> LedgerEntry:
        prev = "0" * 64 if not self.entries else self.entries[-1].leaf_hash()
        body_hash = sha256(canonical_json(body))
        entry = LedgerEntry(
            seq=len(self.entries),
            prev_hash=prev,
            body_hash=body_hash,
            body=body,
            issued_at=now,
        )
        self.entries.append(entry)
        return entry

    def leaves(self) -> list[str]:
        return [e.leaf_hash() for e in self.entries]

    def head(self) -> str:
        return merkle_root(self.leaves())

    def checkpoint(self, signer_id: str, *, now: int) -> Checkpoint:
        cp = Checkpoint(
            domain=self.domain,
            seq=len(self.entries),
            root=self.head(),
            issued_at=now,
            key_id=signer_id,
        )
        sig = self.store.sign(signer_id, canonical_json(cp.payload()), now=now)
        cp.signature = sig.hex()
        self.checkpoints.append(cp)
        return cp

    def inclusion_proof(self, seq: int) -> dict[str, Any]:
        entry = self.entries[seq]
        leaves = self.leaves()
        return {
            "seq": seq,
            "tree_size": len(leaves),
            "leaf": entry.leaf_hash(),
            "entry": entry.to_dict(),
            "proof": merkle_proof(leaves, seq),
            "root": merkle_root(leaves),
            "domain": self.domain,
        }

    def consistency_proof(self, first_size: int, second_size: int | None = None) -> list[str]:
        """RFC 9162 consistency proof between two sizes of this log."""
        leaves = self.leaves()
        if second_size is None:
            second_size = len(leaves)
        if second_size > len(leaves):
            raise ValueError("second_size exceeds the log size")
        return consistency_proof(leaves[:second_size], first_size)

    def store_peer_checkpoint(
        self,
        checkpoint: Checkpoint,
        *,
        consistency: list[str] | None = None,
    ) -> ReasonCode:
        """Detect a split view against already stored checkpoints (R-08).

        * Same domain and size with a different root: fork, acceptance halts.
        * A different size than the latest stored checkpoint for the domain
          needs an RFC 9162 consistency proof between the two sizes
          (smaller -> larger). A proof that fails is a fork and halts
          acceptance. No proof: the checkpoint is not stored and
          CONSISTENCY_PROOF_MISSING is returned (PROVISIONAL_DEFAULT, see
          docs/PENDING_DELIBERATION.md).
        """
        same_domain = [p for p in self.peer_checkpoints if p.domain == checkpoint.domain]
        for prev in same_domain:
            if prev.seq == checkpoint.seq and prev.root != checkpoint.root:
                self.acceptance_halted = True
                self.halt_reason = "ledger_fork"
                return ReasonCode.LEDGER_FORK
        others = [p for p in same_domain if p.seq != checkpoint.seq]
        if others:
            latest = max(others, key=lambda p: p.seq)
            if consistency is None:
                return ReasonCode.CONSISTENCY_PROOF_MISSING
            if latest.seq < checkpoint.seq:
                ok = latest.seq == 0 or verify_consistency(
                    latest.seq, checkpoint.seq, latest.root, checkpoint.root, consistency
                )
            else:
                ok = checkpoint.seq == 0 or verify_consistency(
                    checkpoint.seq, latest.seq, checkpoint.root, latest.root, consistency
                )
            if not ok:
                self.acceptance_halted = True
                self.halt_reason = "ledger_fork"
                return ReasonCode.LEDGER_FORK
        self.peer_checkpoints.append(checkpoint)
        return ReasonCode.OK


def verify_inclusion_proof(proof: dict[str, Any], expected_root: str | None = None) -> bool:
    """Verify an inclusion proof dict produced by Ledger.inclusion_proof.

    Fails closed: the tree size must be present, the leaf must be the
    RFC 9162 leaf hash of the carried entry (when an entry is carried),
    and the entry's seq must equal the proven index.
    """
    if not isinstance(proof, dict):
        return False
    try:
        leaf = proof["leaf"]
        seq = proof["seq"]
        tree_size = proof["tree_size"]
        path = list(proof["proof"])
        root = expected_root if expected_root is not None else proof["root"]
    except (KeyError, TypeError):
        return False
    if not _is_hash_hex(leaf):
        return False
    entry = proof.get("entry")
    if entry is not None:
        if not isinstance(entry, dict) or entry.get("seq") != seq:
            return False
        try:
            recomputed = _leaf(canonical_json(entry))
        except Exception:
            return False
        if not hmac.compare_digest(recomputed, leaf):
            return False
    return verify_inclusion(leaf, seq, tree_size, path, root)
