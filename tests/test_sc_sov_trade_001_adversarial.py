"""SC-SOV-TRADE-001 adversarial tests (wrapper)."""

from __future__ import annotations

import unittest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography

if have_cryptography():
    from tests.sov_trade_adversarial_cases import *  # noqa: F401,F403
else:
    class TestSkippedWithoutCryptography(unittest.TestCase):
        @unittest.skip(CRYPTOGRAPHY_SKIP)
        def test_placeholder(self) -> None:
            pass
