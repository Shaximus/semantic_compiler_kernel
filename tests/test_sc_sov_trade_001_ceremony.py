"""Item 6: 3-of-5 Shamir root ceremony rehearsal."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography

pytestmark = pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)

if have_cryptography():
    from semantic_compiler.sov_trade.ceremony import (
        CeremonyError,
        Share,
        commit_secret,
        reconstruct_secret,
        run_root_ceremony,
        split_secret,
    )
    from semantic_compiler.sov_trade.crypto import PublicKey


@pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)
class TestRootCeremony:
    def test_three_or_more_can_reconstruct_and_sign(self) -> None:
        ceremony = run_root_ceremony(n=5, k=3)
        message = b"root signs an issuer certificate"
        for count in (3, 4, 5):
            signature = ceremony.sign_with_quorum(message, ceremony.shares[:count])
            assert ceremony.public.verify(message, signature)

    def test_two_or_fewer_cannot(self) -> None:
        ceremony = run_root_ceremony(n=5, k=3)
        with pytest.raises(CeremonyError, match="quorum not met"):
            ceremony.sign_with_quorum(b"msg", ceremony.shares[:2])
        with pytest.raises(CeremonyError, match="quorum not met"):
            reconstruct_secret(ceremony.shares[:1], k=3)
        with pytest.raises(CeremonyError, match="quorum not met"):
            reconstruct_secret([], k=3)

    def test_tampered_share_is_detected(self) -> None:
        ceremony = run_root_ceremony(n=5, k=3)
        good = list(ceremony.shares[:3])
        bad_data = bytearray(good[0].data)
        bad_data[0] ^= 0x5A
        tampered = Share(index=good[0].index, data=bytes(bad_data), commitment=good[0].commitment)
        with pytest.raises(CeremonyError, match="tampered|commitment"):
            reconstruct_secret([tampered, good[1], good[2]], k=3)
        # Four shares including one tampered: subset disagreement.
        with pytest.raises(CeremonyError, match="tampered|disagree"):
            reconstruct_secret([tampered, *ceremony.shares[1:4]], k=3)

    def test_known_secret_round_trip(self) -> None:
        secret = bytes(range(32))
        shares = split_secret(secret, n=5, k=3)
        assert commit_secret(secret) == shares[0].commitment
        assert reconstruct_secret(shares[0:3], k=3) == secret
        assert reconstruct_secret(shares[2:5], k=3) == secret

    def test_runbook_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "docs" / "runbooks" / "SC-SOV-TRADE-001_ROOT_CEREMONY.md"
        text = path.read_text(encoding="utf-8")
        assert "3-of-5" in text or "3 of 5" in text
        assert "Shamir" in text
        assert "SoftHSM" in text or "HSM" in text
        assert "not a witnessed national" in text.lower() or "rehearsal" in text.lower()
