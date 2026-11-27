#!/usr/bin/env python3
"""HSM custody evidence for SC-SOV-TRADE-001 (SoftHSM2 TEST token only).

Generates an Ed25519 key in the PKCS#11 token through the project's
PKCS11Signer, then shows with an independent tool (OpenSC pkcs11-tool)
and with raw PKCS#11 attribute reads that:

  * CKA_EXTRACTABLE = false, CKA_SENSITIVE = true (and NEVER_EXTRACTABLE /
    ALWAYS_SENSITIVE = true);
  * reading the private key's CKA_VALUE fails (python-pkcs11), and
    wrapping it out with C_WrapKey (`pkcs11-tool --wrap`) is refused by
    the token with CKR_KEY_UNEXTRACTABLE;
  * a signature made in the token verifies with `cryptography`;
  * PKCS11Signer.sign uses only a key handle: its source never reads
    CKA_VALUE, never calls private_bytes, never handles key bytes.

Environment (the CI workflow and `make verify` set these):
  SOFTHSM2_CONF, SOV_TRADE_PKCS11_LIBRARY, SOV_TRADE_PKCS11_TOKEN_LABEL,
  SOV_TRADE_PKCS11_USER_PIN (a per-run TEST PIN; never printed).

Exit status is non-zero if any check fails.
"""

from __future__ import annotations

import ast
import inspect
import json
import os
import secrets
import subprocess
import sys
import tempfile
import textwrap


def main() -> int:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from pkcs11 import Attribute, ObjectClass
    from pkcs11.exceptions import AttributeSensitive, PKCS11Error

    from semantic_compiler.sov_trade import pkcs11 as sov_pkcs11
    from semantic_compiler.sov_trade.pkcs11 import PKCS11Config, PKCS11Signer

    library = os.environ["SOV_TRADE_PKCS11_LIBRARY"]
    token_label = os.environ["SOV_TRADE_PKCS11_TOKEN_LABEL"]
    pin_env = "SOV_TRADE_PKCS11_USER_PIN"
    if not os.environ.get(pin_env):
        print(f"{pin_env} is not set", file=sys.stderr)
        return 2

    results: dict[str, object] = {
        "token": "SoftHSM2 TEST token (not a certified HSM)",
        "library": library,
        "token_label": token_label,
        "softhsm2_conf": os.environ.get("SOFTHSM2_CONF"),
    }
    failures: list[str] = []

    signer = PKCS11Signer(PKCS11Config(library_path=library, token_label=token_label, user_pin_env=pin_env))
    label = "sov-evidence-" + secrets.token_hex(4)
    public = signer.generate_ed25519(label)
    message = b"SC-SOV-TRADE-001 HSM evidence message"
    signature = signer.sign(label, message)
    try:
        Ed25519PublicKey.from_public_bytes(public.public_key).verify(signature, message)
        results["token_signature_verifies_with_cryptography"] = True
    except Exception:  # pragma: no cover - evidence script
        results["token_signature_verifies_with_cryptography"] = False
        failures.append("token signature did not verify")
    results["key_label"] = label
    results["public_key_hex"] = public.public_key.hex()

    # Raw attribute reads through python-pkcs11.
    lib = __import__("pkcs11").lib(library)
    token = lib.get_token(token_label=token_label)
    with token.open(user_pin=os.environ[pin_env]) as session:
        objs = list(session.get_objects({Attribute.CLASS: ObjectClass.PRIVATE_KEY, Attribute.LABEL: label}))
        if len(objs) != 1:
            failures.append(f"expected one private key object, found {len(objs)}")
        priv = objs[0]
        attrs = {
            "CKA_EXTRACTABLE": bool(priv[Attribute.EXTRACTABLE]),
            "CKA_SENSITIVE": bool(priv[Attribute.SENSITIVE]),
            "CKA_NEVER_EXTRACTABLE": bool(priv[Attribute.NEVER_EXTRACTABLE]),
            "CKA_ALWAYS_SENSITIVE": bool(priv[Attribute.ALWAYS_SENSITIVE]),
            "CKA_PRIVATE": bool(priv[Attribute.PRIVATE]),
            "CKA_TOKEN": bool(priv[Attribute.TOKEN]),
        }
        results["python_pkcs11_attributes"] = attrs
        expected = {
            "CKA_EXTRACTABLE": False,
            "CKA_SENSITIVE": True,
            "CKA_NEVER_EXTRACTABLE": True,
            "CKA_ALWAYS_SENSITIVE": True,
        }
        for k, v in expected.items():
            if attrs[k] is not v:
                failures.append(f"{k} is {attrs[k]}, expected {v}")
        try:
            value = priv[Attribute.VALUE]
            del value
            results["cka_value_read"] = "SUCCEEDED (custody failure)"
            failures.append("CKA_VALUE of the private key was readable")
        except AttributeSensitive as exc:
            results["cka_value_read"] = f"refused: {type(exc).__name__} (CKR_ATTRIBUTE_SENSITIVE)"
        except PKCS11Error as exc:
            results["cka_value_read"] = f"refused: {type(exc).__name__}"

    # Independent tool: OpenSC pkcs11-tool. The PIN is passed as env:NAME so
    # it never appears on a command line or in this output.
    base = ["pkcs11-tool", "--module", library, "--token-label", token_label, "--login", "--pin", f"env:{pin_env}"]
    listing = subprocess.run(
        base + ["--list-objects", "--type", "privkey", "--label", label],
        capture_output=True, text=True, check=False,
    )
    results["pkcs11_tool_list_objects_cmd"] = " ".join(base[:-1] + ["env:" + pin_env, "--list-objects", "--type", "privkey", "--label", label])
    results["pkcs11_tool_list_objects_rc"] = listing.returncode
    results["pkcs11_tool_list_objects_stdout"] = listing.stdout
    access = [ln.strip() for ln in listing.stdout.splitlines() if ln.strip().startswith("Access:")]
    results["pkcs11_tool_access_line"] = access
    if listing.returncode != 0 or not access:
        failures.append("pkcs11-tool --list-objects did not list the key")
    else:
        line = access[0]
        for flag in ("sensitive", "never extractable"):
            if flag not in line:
                failures.append(f"pkcs11-tool Access line lacks '{flag}'")
        if ", extractable" in line or line.endswith(" extractable") and "never extractable" not in line:
            failures.append("pkcs11-tool reports the key as extractable")

    scratch = tempfile.mkdtemp(prefix="sov-hsm-evidence-")
    # Export attempt 1: pkcs11-tool --read-object. OpenSC refuses private
    # keys itself ("reading private keys not (yet) supported"), so this is
    # recorded but is NOT counted as token evidence.
    export_path = os.path.join(scratch, f"{label}.der")
    export = subprocess.run(
        base + ["--read-object", "--type", "privkey", "--label", label, "--output-file", export_path],
        capture_output=True, text=True, check=False,
    )
    exported = os.path.exists(export_path) and os.path.getsize(export_path) > 0
    results["export_attempt_read_object"] = {
        "rc": export.returncode,
        "stderr": export.stderr.strip(),
        "wrote_bytes": exported,
        "note": "OpenSC refuses --read-object for private keys at the tool level; not token evidence",
    }
    if exported:
        failures.append("pkcs11-tool --read-object wrote private key bytes")
    if os.path.exists(export_path):
        os.remove(export_path)

    # Export attempt 2 (token-level): wrap the private key out under a fresh
    # AES key with C_WrapKey. A non-extractable key must be refused by the
    # token with CKR_KEY_UNEXTRACTABLE.
    wrap_id = secrets.token_hex(4)
    keygen = subprocess.run(
        base + ["--keygen", "--key-type", "AES:32", "--label", "sov-evidence-wrap-" + wrap_id,
                "--id", wrap_id, "--usage-wrap"],
        capture_output=True, text=True, check=False,
    )
    wrapped_path = os.path.join(scratch, f"{label}.wrapped")
    wrap = subprocess.run(
        base + ["--wrap", "--mechanism", "AES-KEY-WRAP-PAD", "--id", wrap_id,
                "--application-id", label.encode("utf-8").hex(), "--output-file", wrapped_path],
        capture_output=True, text=True, check=False,
    )
    wrapped = os.path.exists(wrapped_path) and os.path.getsize(wrapped_path) > 0
    results["export_attempt_c_wrapkey"] = {
        "wrapping_key_keygen_rc": keygen.returncode,
        "cmd": " ".join(["pkcs11-tool", "--module", library, "--token-label", token_label, "--login",
                         "--pin", "env:" + pin_env, "--wrap", "--mechanism", "AES-KEY-WRAP-PAD",
                         "--id", wrap_id, "--application-id", label.encode("utf-8").hex(),
                         "--output-file", wrapped_path]),
        "rc": wrap.returncode,
        "stderr": wrap.stderr.strip(),
        "wrote_bytes": wrapped,
    }
    if keygen.returncode != 0:
        failures.append("could not create the AES wrapping key for the export attempt")
    if wrap.returncode == 0 or wrapped or "CKR_KEY_UNEXTRACTABLE" not in wrap.stderr:
        failures.append("C_WrapKey export of the private key was not refused with CKR_KEY_UNEXTRACTABLE")
    if os.path.exists(wrapped_path):
        os.remove(wrapped_path)

    # Signing path uses a key handle only.
    sign_src = textwrap.dedent(inspect.getsource(PKCS11Signer.sign))
    tree = ast.parse(sign_src)
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    forbidden = {"VALUE", "private_bytes", "private_bytes_raw", "from_private_bytes", "_secret"}
    hits = sorted(names & forbidden)
    calls_sign = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "sign"
        for n in ast.walk(tree)
    )
    module_src = inspect.getsource(sov_pkcs11)
    results["sign_path_forbidden_attributes"] = hits
    results["sign_path_calls_token_sign"] = calls_sign
    results["module_mentions_private_bytes"] = "private_bytes" in module_src
    if hits or not calls_sign or "private_bytes" in module_src:
        failures.append("PKCS11Signer.sign touches private key bytes or does not sign in-token")

    results["failures"] = failures
    results["result"] = "PASS" if not failures else "FAIL"
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
