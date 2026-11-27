"""Ledger inclusion binding and checkpoint consistency (R-08), RFC 9162."""

from __future__ import annotations

import copy

import pytest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography

pytestmark = pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)

if have_cryptography():
    from semantic_compiler.sov_trade.custody import KeyStore
    from semantic_compiler.sov_trade.ledger import (
        Checkpoint,
        Ledger,
        merkle_root,
        verify_inclusion_proof,
    )
    from semantic_compiler.sov_trade.types import ReasonCode


def _ledger(n: int, tag: str = "") -> Ledger:
    led = Ledger(domain="nation-a", store=KeyStore("nation-a"))
    for i in range(n):
        led.append({"type": "note", "i": i, "tag": tag}, now=1000 + i)
    return led


def _cp(led: Ledger, size: int) -> Checkpoint:
    return Checkpoint(domain=led.domain, seq=size, root=merkle_root(led.leaves()[:size]), issued_at=0)


class TestInclusionBinding:
    def test_valid_proof_verifies(self) -> None:
        led = _ledger(7)
        for seq in range(7):
            assert verify_inclusion_proof(led.inclusion_proof(seq))

    def test_entry_substitution_is_rejected(self) -> None:
        led = _ledger(5)
        proof = led.inclusion_proof(2)
        proof["entry"] = copy.deepcopy(proof["entry"])
        proof["entry"]["body"]["i"] = 99
        assert not verify_inclusion_proof(proof)

    def test_index_swap_is_rejected(self) -> None:
        led = _ledger(5)
        proof = led.inclusion_proof(2)
        proof["seq"] = 3
        assert not verify_inclusion_proof(proof)

    def test_missing_tree_size_fails_closed(self) -> None:
        led = _ledger(5)
        proof = led.inclusion_proof(1)
        del proof["tree_size"]
        assert not verify_inclusion_proof(proof)

    def test_wrong_expected_root_is_rejected(self) -> None:
        led = _ledger(5)
        assert not verify_inclusion_proof(led.inclusion_proof(1), expected_root="0" * 64)


class TestCheckpointConsistency:
    def test_growing_log_with_proof_is_accepted(self) -> None:
        a = _ledger(9)
        b = _ledger(0)
        assert b.store_peer_checkpoint(_cp(a, 4)) is ReasonCode.OK
        proof = a.consistency_proof(4, 9)
        assert b.store_peer_checkpoint(_cp(a, 9), consistency=proof) is ReasonCode.OK
        assert not b.acceptance_halted

    def test_later_checkpoint_without_proof_is_not_stored(self) -> None:
        a = _ledger(9)
        b = _ledger(0)
        b.store_peer_checkpoint(_cp(a, 4))
        assert b.store_peer_checkpoint(_cp(a, 9)) is ReasonCode.CONSISTENCY_PROOF_MISSING
        assert len(b.peer_checkpoints) == 1
        assert not b.acceptance_halted

    def test_rewritten_history_halts_acceptance(self) -> None:
        honest = _ledger(4)
        forked = _ledger(9, tag="rewritten")
        b = _ledger(0)
        b.store_peer_checkpoint(_cp(honest, 4))
        proof = forked.consistency_proof(4, 9)
        assert b.store_peer_checkpoint(_cp(forked, 9), consistency=proof) is ReasonCode.LEDGER_FORK
        assert b.acceptance_halted

    def test_garbage_proof_halts_acceptance(self) -> None:
        a = _ledger(9)
        b = _ledger(0)
        b.store_peer_checkpoint(_cp(a, 4))
        assert b.store_peer_checkpoint(_cp(a, 9), consistency=["00" * 32]) is ReasonCode.LEDGER_FORK
        assert b.acceptance_halted

    def test_older_checkpoint_needs_proof_too(self) -> None:
        a = _ledger(9)
        b = _ledger(0)
        b.store_peer_checkpoint(_cp(a, 9))
        assert b.store_peer_checkpoint(_cp(a, 4)) is ReasonCode.CONSISTENCY_PROOF_MISSING
        assert b.store_peer_checkpoint(_cp(a, 4), consistency=a.consistency_proof(4, 9)) is ReasonCode.OK
