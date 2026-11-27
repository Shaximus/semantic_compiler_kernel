"""Append-only, hash-chained ledgers with Merkle checkpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .canonical import canonical_json
from .crypto import sha256
from .custody import KeyStore
from .types import ReasonCode, TradeError


def _leaf(data: bytes) -> str:
    return sha256(b"leaf|" + data)


def _node(left: str, right: str) -> str:
    return sha256(("node|" + left + "|" + right).encode("ascii"))


def merkle_root(leaves: list[str]) -> str:
    if not leaves:
        return sha256(b"empty")
    layer = list(leaves)
    while len(layer) > 1:
        nxt: list[str] = []
        for i in range(0, len(layer), 2):
            if i + 1 < len(layer):
                nxt.append(_node(layer[i], layer[i + 1]))
            else:
                nxt.append(_node(layer[i], layer[i]))
        layer = nxt
    return layer[0]


def merkle_proof(leaves: list[str], index: int) -> list[tuple[str, str]]:
    """Return sibling hashes as (side, hash) where side is 'L' or 'R'."""
    if index < 0 or index >= len(leaves):
        raise IndexError("leaf index out of range")
    layer = list(leaves)
    idx = index
    proof: list[tuple[str, str]] = []
    while len(layer) > 1:
        if idx % 2 == 0:
            sib = layer[idx + 1] if idx + 1 < len(layer) else layer[idx]
            proof.append(("R", sib))
        else:
            proof.append(("L", layer[idx - 1]))
        nxt: list[str] = []
        for i in range(0, len(layer), 2):
            if i + 1 < len(layer):
                nxt.append(_node(layer[i], layer[i + 1]))
            else:
                nxt.append(_node(layer[i], layer[i]))
        layer = nxt
        idx //= 2
    return proof


def verify_inclusion(leaf: str, index: int, proof: list[tuple[str, str]], root: str) -> bool:
    value = leaf
    for side, sib in proof:
        if side == "L":
            value = _node(sib, value)
        else:
            value = _node(value, sib)
    return value == root


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
        proof = merkle_proof(self.leaves(), seq)
        return {
            "seq": seq,
            "leaf": entry.leaf_hash(),
            "entry": entry.to_dict(),
            "proof": proof,
            "root": self.head(),
            "domain": self.domain,
        }

    def store_peer_checkpoint(self, checkpoint: Checkpoint) -> ReasonCode:
        """Detect a split view against already stored checkpoints (R-08)."""
        for prev in self.peer_checkpoints:
            if prev.domain != checkpoint.domain:
                continue
            if prev.seq == checkpoint.seq and prev.root != checkpoint.root:
                self.acceptance_halted = True
                self.halt_reason = "ledger_fork"
                return ReasonCode.LEDGER_FORK
            # A later checkpoint must be consistent with an earlier prefix
            # when the earlier seq is smaller and roots differ without extension
            # evidence: we flag equal-seq disagreement only, which is the
            # detectable split-view in this reference.
        self.peer_checkpoints.append(checkpoint)
        return ReasonCode.OK


def verify_inclusion_proof(proof: dict[str, Any], expected_root: str | None = None) -> bool:
    root = expected_root or proof["root"]
    return verify_inclusion(proof["leaf"], int(proof["seq"]), [(a, b) for a, b in proof["proof"]], root)
