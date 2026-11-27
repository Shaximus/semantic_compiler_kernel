"""Import guards for SC-SOV-TRADE-001 tests.

Local development may lack `cryptography`, `asn1crypto`, python-pkcs11,
SoftHSM2 or `hypothesis`; there the functional tests skip with a reason.

When SOV_TRADE_REQUIRE_FUNCTIONAL=1 (GitHub CI sets it), a missing
dependency is a FAILURE, not a skip: tests/conftest.py turns every skip
in a test_sc_sov_trade_001* module into a failure, and the unittest
wrappers fail instead of skipping. The separate `no-cryptography` CI
job leaves the variable unset and runs only the refusal tests.
"""

from __future__ import annotations

import os

REQUIRE_FUNCTIONAL_ENV = "SOV_TRADE_REQUIRE_FUNCTIONAL"

CRYPTOGRAPHY_SKIP = (
    "sov_trade requires cryptography>=50.0.2,<51 (not installed here); "
    "install the package dependencies to run these tests"
)
PKCS11_SKIP = (
    "PKCS#11 tests require python-pkcs11 and SoftHSM2 (libsofthsm2.so, "
    "softhsm2-util); install the sov-trade extra and softhsm2"
)
TIMESTAMP_SKIP = (
    "RFC 3161 tests require asn1crypto and cryptography; install the "
    "sov-trade extra"
)
HYPOTHESIS_SKIP = (
    "property tests require hypothesis; install the sov-trade-test extra"
)


def require_functional() -> bool:
    """True when missing dependencies must fail instead of skip."""
    return os.environ.get(REQUIRE_FUNCTIONAL_ENV, "") == "1"


def have_cryptography() -> bool:
    try:
        import cryptography
        parts = []
        for token in cryptography.__version__.split("."):
            if token.isdigit():
                parts.append(int(token))
            else:
                break
        return tuple(parts) >= (50, 0, 2)
    except ImportError:
        return False


def have_pkcs11() -> bool:
    if not have_cryptography():
        return False
    try:
        import pkcs11  # noqa: F401
    except ImportError:
        return False
    import shutil
    from pathlib import Path
    if shutil.which("softhsm2-util") is None:
        return False
    env = os.environ.get("SOV_TRADE_PKCS11_LIBRARY")
    if env:
        return Path(env).is_file()
    for candidate in (
        "/usr/lib/softhsm/libsofthsm2.so",
        "/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so",
        "/usr/lib64/softhsm/libsofthsm2.so",
    ):
        if Path(candidate).is_file():
            return True
    return False


def have_asn1crypto() -> bool:
    if not have_cryptography():
        return False
    try:
        import asn1crypto  # noqa: F401
        return True
    except ImportError:
        return False


def have_hypothesis() -> bool:
    try:
        import hypothesis  # noqa: F401
        return True
    except ImportError:
        return False
