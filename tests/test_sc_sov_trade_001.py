"""SC-SOV-TRADE-001 acceptance tests (wrapper).

The cases live in `sov_trade_cases.py` so this module can be imported
by unittest discover when cryptography is not installed (GitHub CI).
"""

from __future__ import annotations

import unittest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography, require_functional

if have_cryptography():
    from tests.sov_trade_cases import *  # noqa: F401,F403
elif require_functional():
    class TestFunctionalDependencyMissing(unittest.TestCase):
        def test_cryptography_is_installed(self) -> None:
            self.fail("SOV_TRADE_REQUIRE_FUNCTIONAL=1 but " + CRYPTOGRAPHY_SKIP)
else:
    class TestSkippedWithoutCryptography(unittest.TestCase):
        @unittest.skip(CRYPTOGRAPHY_SKIP)
        def test_placeholder(self) -> None:
            pass
