"""Import guards for SC-SOV-TRADE-001 tests.

GitHub CI installs only jsonschema, PyYAML and pytest, and does not
`pip install -e .`, so `cryptography`, SoftHSM and python-pkcs11 are
absent there. Production code fails closed without cryptography. These
helpers let CI collect the suite without import errors, while the
refusal tests still run.
"""

from __future__ import annotations

CRYPTOGRAPHY_SKIP = (
    "sov_trade requires cryptography>=50.0.2; GitHub CI installs only "
    "jsonschema, PyYAML and pytest and does not install package dependencies"
)
PKCS11_SKIP = (
    "PKCS#11 tests require python-pkcs11 and SoftHSM2; they run fully on "
    "the development box and are skipped in GitHub CI"
)
TIMESTAMP_SKIP = (
    "RFC 3161 tests require asn1crypto and cryptography; they run fully "
    "on the development box and are skipped in GitHub CI"
)


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
    from pathlib import Path
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
