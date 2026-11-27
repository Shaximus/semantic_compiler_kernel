"""Generic PKCS#11 signer interface for SC-SOV-TRADE-001.

Keys are generated in the token with CKA_EXTRACTABLE=false and
CKA_SENSITIVE=true. Signing happens inside the token. This module never
returns private key bytes and never logs a PIN.

The interface is configuration-driven (library path, token label, PIN
source). A certified hardware HSM can be swapped in by pointing the
config at its PKCS#11 module; no code change is required.

SoftHSM2 is the software token used in tests. It is not a certified
HSM; tokens live in a test-generated temporary directory.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .crypto import ALG_ED25519, ED25519_PUBLIC_LEN, ED25519_SIGNATURE_LEN, PublicKey
from .types import CustodyError, ReasonCode

_PKCS11_IMPORT_ERROR = (
    "sov_trade.pkcs11 requires the 'python-pkcs11' package "
    "(tested with python-pkcs11==0.10.1). Install it with: "
    "pip install 'python-pkcs11==0.10.1'."
)

# RFC 8410 / PKCS#11 CKA_EC_PARAMS for Ed25519 (OID 1.3.101.112).
_ED25519_EC_PARAMS = bytes.fromhex("06032b6570")

_DEFAULT_LIBRARY_CANDIDATES = (
    "/usr/lib/softhsm/libsofthsm2.so",
    "/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so",
    "/usr/lib64/softhsm/libsofthsm2.so",
)


def _pkcs11():
    try:
        import pkcs11
        from pkcs11 import Attribute, KeyType, Mechanism, ObjectClass
    except ImportError as exc:
        raise ImportError(_PKCS11_IMPORT_ERROR) from exc
    return pkcs11, Attribute, KeyType, Mechanism, ObjectClass


def default_library_path() -> str:
    env = os.environ.get("SOV_TRADE_PKCS11_LIBRARY")
    if env:
        return env
    for candidate in _DEFAULT_LIBRARY_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    raise FileNotFoundError(
        "No PKCS#11 library found. Set SOV_TRADE_PKCS11_LIBRARY to the "
        "module path (for example /usr/lib/softhsm/libsofthsm2.so, or a "
        "certified HSM vendor module)."
    )


@dataclass(frozen=True)
class PKCS11Config:
    """How to reach a token. PINs are supplied at runtime, never stored here on disk."""

    library_path: str
    token_label: str
    # PIN is taken from the environment variable named here, not from the object.
    user_pin_env: str = "SOV_TRADE_PKCS11_USER_PIN"
    slot: int | None = None

    def user_pin(self) -> str:
        pin = os.environ.get(self.user_pin_env)
        if not pin:
            raise CustodyError(
                ReasonCode.DUAL_CONTROL_REQUIRED,
                f"PKCS#11 user PIN is not set in the environment ({self.user_pin_env})",
            )
        return pin


class PKCS11Signer:
    """Sign with a non-extractable token key. Private material never leaves the token."""

    def __init__(self, config: PKCS11Config) -> None:
        self.config = config
        pkcs11, *_ = _pkcs11()
        self._lib = pkcs11.lib(config.library_path)

    def _token(self) -> Any:
        return self._lib.get_token(token_label=self.config.token_label)

    def generate_ed25519(self, label: str) -> PublicKey:
        """Generate a non-extractable, sensitive Ed25519 key in the token."""
        _, Attribute, KeyType, Mechanism, _ObjectClass = _pkcs11()
        pin = self.config.user_pin()
        with self._token().open(user_pin=pin, rw=True) as session:
            _pub, priv = session.generate_keypair(
                KeyType.EC_EDWARDS,
                mechanism=Mechanism.EC_EDWARDS_KEY_PAIR_GEN,
                store=True,
                public_template={
                    Attribute.EC_PARAMS: _ED25519_EC_PARAMS,
                    Attribute.VERIFY: True,
                    Attribute.TOKEN: True,
                    Attribute.LABEL: label,
                },
                private_template={
                    Attribute.SIGN: True,
                    Attribute.TOKEN: True,
                    Attribute.PRIVATE: True,
                    Attribute.SENSITIVE: True,
                    Attribute.EXTRACTABLE: False,
                    Attribute.LABEL: label,
                },
            )
            if bool(priv[Attribute.EXTRACTABLE]) is not False:
                raise CustodyError(
                    ReasonCode.FAIL_CLOSED,
                    "generated token key is extractable; refusing to use it",
                )
            if bool(priv[Attribute.SENSITIVE]) is not True:
                raise CustodyError(
                    ReasonCode.FAIL_CLOSED,
                    "generated token key is not marked sensitive; refusing to use it",
                )
            public_bytes = _ed25519_public_from_object(_pub, Attribute)
        return PublicKey(algorithm=ALG_ED25519, public_key=public_bytes)

    def sign(self, label: str, message: bytes) -> bytes:
        _, Attribute, _KeyType, Mechanism, ObjectClass = _pkcs11()
        pin = self.config.user_pin()
        with self._token().open(user_pin=pin, rw=False) as session:
            priv = _find_private(session, label, Attribute, ObjectClass)
            signature = priv.sign(message, mechanism=Mechanism.EDDSA)
        if len(signature) != ED25519_SIGNATURE_LEN:
            raise CustodyError(
                ReasonCode.SIGNATURE_INVALID,
                f"token signature length {len(signature)} is not Ed25519",
            )
        return signature

    def public_key(self, label: str) -> PublicKey:
        _, Attribute, _KeyType, _Mechanism, ObjectClass = _pkcs11()
        pin = self.config.user_pin()
        with self._token().open(user_pin=pin, rw=False) as session:
            pub = _find_public(session, label, Attribute, ObjectClass)
            public_bytes = _ed25519_public_from_object(pub, Attribute)
        return PublicKey(algorithm=ALG_ED25519, public_key=public_bytes)

    def private_key_exportable(self, label: str) -> bool:
        _, Attribute, _KeyType, _Mechanism, ObjectClass = _pkcs11()
        pin = self.config.user_pin()
        with self._token().open(user_pin=pin, rw=False) as session:
            priv = _find_private(session, label, Attribute, ObjectClass)
            return bool(priv[Attribute.EXTRACTABLE])

    def private_key_sensitive(self, label: str) -> bool:
        _, Attribute, _KeyType, _Mechanism, ObjectClass = _pkcs11()
        pin = self.config.user_pin()
        with self._token().open(user_pin=pin, rw=False) as session:
            priv = _find_private(session, label, Attribute, ObjectClass)
            return bool(priv[Attribute.SENSITIVE])

    def try_export_private_value(self, label: str) -> None:
        """Attempt to read CKA_VALUE of the private key.

        A correctly configured token must raise; this method re-raises that
        error and never returns key bytes. A successful read is a failure
        of the custody rule and becomes CustodyError.
        """
        _, Attribute, _KeyType, _Mechanism, ObjectClass = _pkcs11()
        pin = self.config.user_pin()
        with self._token().open(user_pin=pin, rw=False) as session:
            priv = _find_private(session, label, Attribute, ObjectClass)
            try:
                value = priv[Attribute.VALUE]
            except Exception:
                raise
            # If we got here the token leaked key material through the API.
            # Drop the value immediately and fail closed without returning it.
            del value
            raise CustodyError(
                ReasonCode.FAIL_CLOSED,
                "token allowed CKA_VALUE to be read for a sensitive key",
            )


def _find_private(session: Any, label: str, Attribute: Any, ObjectClass: Any) -> Any:
    objs = list(
        session.get_objects({Attribute.CLASS: ObjectClass.PRIVATE_KEY, Attribute.LABEL: label})
    )
    if not objs:
        raise CustodyError(ReasonCode.CHAIN_INVALID, f"no private key labelled {label!r}")
    return objs[0]


def _find_public(session: Any, label: str, Attribute: Any, ObjectClass: Any) -> Any:
    objs = list(
        session.get_objects({Attribute.CLASS: ObjectClass.PUBLIC_KEY, Attribute.LABEL: label})
    )
    if not objs:
        raise CustodyError(ReasonCode.CHAIN_INVALID, f"no public key labelled {label!r}")
    return objs[0]


def _ed25519_public_from_object(pub: Any, Attribute: Any) -> bytes:
    # SoftHSM stores the raw 32-byte point in CKA_EC_POINT, sometimes as
    # an OCTET STRING (0x04 0x20 || point). Accept both.
    point = bytes(pub[Attribute.EC_POINT])
    if len(point) == ED25519_PUBLIC_LEN:
        return point
    if len(point) == ED25519_PUBLIC_LEN + 2 and point[0] == 0x04 and point[1] == ED25519_PUBLIC_LEN:
        return point[2:]
    raise CustodyError(
        ReasonCode.FAIL_CLOSED,
        f"unexpected Ed25519 CKA_EC_POINT length {len(point)}",
    )
