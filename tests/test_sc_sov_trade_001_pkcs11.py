"""Item 3: PKCS#11 signer against SoftHSM2 (non-extractable keys)."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

import pytest

from tests.sov_trade_deps import PKCS11_SKIP, have_pkcs11

pytestmark = pytest.mark.skipif(not have_pkcs11(), reason=PKCS11_SKIP)


@pytest.fixture(scope="module")
def token_env(tmp_path_factory):
    """Initialise one throwaway SoftHSM token for the module. PIN is not printed.

    SoftHSM's PKCS#11 module is loaded once per process and keeps the
    SOFTHSM2_CONF it first saw, so the token is module-scoped.
    """
    if not have_pkcs11():
        pytest.skip(PKCS11_SKIP)
    tmp_path = tmp_path_factory.mktemp("softhsm")
    conf = tmp_path / "softhsm2.conf"
    tokens = tmp_path / "tokens"
    tokens.mkdir()
    conf.write_text(
        f"directories.tokendir = {tokens}\nobjectstore.backend = file\nlog.level = ERROR\n",
        encoding="utf-8",
    )
    os.environ["SOFTHSM2_CONF"] = str(conf)
    pin = secrets.token_hex(16)
    so_pin = secrets.token_hex(16)
    import subprocess
    result = subprocess.run(
        [
            "softhsm2-util",
            "--init-token",
            "--free",
            "--label",
            "sov-test",
            "--pin",
            pin,
            "--so-pin",
            so_pin,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=os.environ,
    )
    assert result.returncode == 0, "softhsm2-util --init-token failed"
    pin_env = "SOV_TRADE_PKCS11_USER_PIN"
    os.environ[pin_env] = pin
    from semantic_compiler.sov_trade.pkcs11 import default_library_path

    yield {
        "library": default_library_path(),
        "label": "sov-test",
        "pin_env": pin_env,
    }
    os.environ.pop(pin_env, None)


@pytest.mark.skipif(not have_pkcs11(), reason=PKCS11_SKIP)
class TestPKCS11Signer:
    def test_sign_and_verify_in_token(self, token_env: dict[str, str]) -> None:
        from semantic_compiler.sov_trade.pkcs11 import PKCS11Config, PKCS11Signer

        signer = PKCS11Signer(
            PKCS11Config(
                library_path=token_env["library"],
                token_label=token_env["label"],
                user_pin_env=token_env["pin_env"],
            )
        )
        public = signer.generate_ed25519("signer-a")
        message = b"assertion-bytes"
        signature = signer.sign("signer-a", message)
        assert public.verify(message, signature)
        assert not public.verify(b"other", signature)
        # The same public key is readable back from the token.
        assert signer.public_key("signer-a").public_key == public.public_key

    def test_private_key_is_non_extractable_and_sensitive(self, token_env: dict[str, str]) -> None:
        from pkcs11.exceptions import AttributeSensitive, PKCS11Error
        from semantic_compiler.sov_trade.pkcs11 import PKCS11Config, PKCS11Signer
        from semantic_compiler.sov_trade.types import CustodyError

        signer = PKCS11Signer(
            PKCS11Config(
                library_path=token_env["library"],
                token_label=token_env["label"],
                user_pin_env=token_env["pin_env"],
            )
        )
        signer.generate_ed25519("locked")
        assert signer.private_key_exportable("locked") is False
        assert signer.private_key_sensitive("locked") is True
        # The token itself must refuse: a CustodyError here would mean the
        # token returned CKA_VALUE and only our wrapper caught it.
        with pytest.raises((AttributeSensitive, PKCS11Error)):
            signer.try_export_private_value("locked")
        assert not issubclass(CustodyError, PKCS11Error)

    def test_config_is_library_path_generic(self, token_env: dict[str, str]) -> None:
        from semantic_compiler.sov_trade.pkcs11 import PKCS11Config

        config = PKCS11Config(
            library_path=token_env["library"],
            token_label=token_env["label"],
            user_pin_env=token_env["pin_env"],
        )
        # A certified module is selected by path only; no SoftHSM type switch.
        assert config.library_path.endswith("libsofthsm2.so") or "pkcs11" in config.library_path.lower()
        # The config carries no PIN, only the name of the environment variable.
        assert not any("pin" == f for f in PKCS11Config.__dataclass_fields__)

    def test_sign_refuses_extractable_key(self, token_env: dict[str, str]) -> None:
        import pkcs11
        from pkcs11 import Attribute, KeyType, Mechanism
        from semantic_compiler.sov_trade.pkcs11 import PKCS11Config, PKCS11Signer
        from semantic_compiler.sov_trade.types import CustodyError

        lib = pkcs11.lib(token_env["library"])
        token = lib.get_token(token_label=token_env["label"])
        with token.open(user_pin=os.environ[token_env["pin_env"]], rw=True) as session:
            session.generate_keypair(
                KeyType.EC_EDWARDS,
                mechanism=Mechanism.EC_EDWARDS_KEY_PAIR_GEN,
                store=True,
                public_template={
                    Attribute.EC_PARAMS: bytes.fromhex("06032b6570"),
                    Attribute.TOKEN: True,
                    Attribute.LABEL: "leaky",
                },
                private_template={
                    Attribute.SIGN: True,
                    Attribute.TOKEN: True,
                    Attribute.SENSITIVE: False,
                    Attribute.EXTRACTABLE: True,
                    Attribute.LABEL: "leaky",
                },
            )
        signer = PKCS11Signer(
            PKCS11Config(
                library_path=token_env["library"],
                token_label=token_env["label"],
                user_pin_env=token_env["pin_env"],
            )
        )
        with pytest.raises(CustodyError):
            signer.sign("leaky", b"message")

    def test_sign_refuses_ambiguous_label(self, token_env: dict[str, str]) -> None:
        from semantic_compiler.sov_trade.pkcs11 import PKCS11Config, PKCS11Signer
        from semantic_compiler.sov_trade.types import CustodyError

        signer = PKCS11Signer(
            PKCS11Config(
                library_path=token_env["library"],
                token_label=token_env["label"],
                user_pin_env=token_env["pin_env"],
            )
        )
        signer.generate_ed25519("twin")
        signer.generate_ed25519("twin")
        with pytest.raises(CustodyError):
            signer.sign("twin", b"message")
