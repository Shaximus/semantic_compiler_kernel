#!/usr/bin/env python3
"""Hand-written mutation check for SC-SOV-TRADE-001 security properties.

For each mutation: copy the repository to a scratch directory, apply ONE
textual change that breaks a security property, run the sov_trade test
modules, record which tests fail, then discard the copy (the working tree
is never modified, so "revert" is automatic and exact).

A mutation that no test catches is SURVIVED and the script exits 1.

usage: mutation_check.py [--python PY] [--out results.json] [--only ID ...]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(os.environ.get("SOV_MUTATION_REPO") or Path(__file__).resolve().parents[2])

# (id, property, file, old, new)
MUTATIONS: list[tuple[str, str, str, str, str]] = [
    ("M01", "hybrid: ML-DSA-65 half not verified", "sov_trade/crypto.py",
     "    for name in HYBRID_REQUIRED_MEMBERS:\n        if not ALGORITHMS[name].verify(pubs[name], message, sigs[name]):",
     "    for name in (ALG_ED25519,):\n        if not ALGORITHMS[name].verify(pubs[name], message, sigs[name]):"),
    ("M02", "hybrid: Ed25519 half not verified", "sov_trade/crypto.py",
     "    for name in HYBRID_REQUIRED_MEMBERS:\n        if not ALGORITHMS[name].verify(pubs[name], message, sigs[name]):",
     "    for name in (ALG_ML_DSA_65,):\n        if not ALGORITHMS[name].verify(pubs[name], message, sigs[name]):"),
    ("M03", "ML-DSA-65 verify always succeeds", "sov_trade/crypto.py",
     "            MLDSA65PublicKey.from_public_bytes(public).verify(\n                signature, message, ML_DSA_CONTEXT\n            )",
     "            MLDSA65PublicKey.from_public_bytes(public)"),
    ("M04", "ML-DSA-65 signing context not bound at verify", "sov_trade/crypto.py",
     "            MLDSA65PublicKey.from_public_bytes(public).verify(\n                signature, message, ML_DSA_CONTEXT\n            )",
     "            MLDSA65PublicKey.from_public_bytes(public).verify(\n                signature, message\n            ) if False else None"),
    ("M05", "Ed25519 verify always succeeds", "sov_trade/crypto.py",
     "            Ed25519PublicKey.from_public_bytes(public).verify(signature, message)",
     "            Ed25519PublicKey.from_public_bytes(public)"),
    ("M06", "empty signature set accepted", "sov_trade/crypto.py",
     "    if not items:\n        return False",
     "    if not items:\n        return True"),
    ("M07", "RFC 3161: TSA nonce not checked", "sov_trade/timestamp.py",
     '    if content["nonce"].native != nonce:',
     '    if False and content["nonce"].native != nonce:'),
    ("M08", "RFC 3161: message imprint not checked", "sov_trade/timestamp.py",
     "    if got_imprint != expected_imprint:",
     "    if False and got_imprint != expected_imprint:"),
    ("M09", "RFC 3161: TSA chain to trusted CA not checked", "sov_trade/timestamp.py",
     "        tsa_cert.verify_directly_issued_by(trusted_ca)",
     "        pass"),
    ("M10", "RFC 3161: CMS signature not verified", "sov_trade/timestamp.py",
     "        tsa_public.verify(\n            bytes(signer[\"signature\"]),",
     "        (lambda *a, **k: None)(\n            bytes(signer[\"signature\"]),"),
    ("M11", "RFC 3161: policy not checked", "sov_trade/timestamp.py",
     '    if content["policy"].dotted != policy:',
     '    if False and content["policy"].dotted != policy:'),
    ("M12", "RFC 3161: signed message-digest not checked", "sov_trade/timestamp.py",
     "    if not md_values or len(md_values) != 1 or bytes(md_values[0]) != digest:",
     "    if False:"),
    ("M13", "RFC 3161: timeStamping EKU not checked", "sov_trade/timestamp.py",
     "    if not eku.critical or list(eku.value) != [ExtendedKeyUsageOID.TIME_STAMPING]:",
     "    if False:"),
    ("M14", "RFC 3161: ESS signing-certificate binding not checked", "sov_trade/timestamp.py",
     "    _check_ess_binding(attrs_native, tsa_der)",
     "    pass"),
    ("M15", "mTLS: server accepts any/expired client cert (no client verification)", "sov_trade/mtls.py",
     "    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\n    ctx.minimum_version = ssl.TLSVersion.TLSv1_3\n    ctx.verify_mode = ssl.CERT_REQUIRED",
     "    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\n    ctx.minimum_version = ssl.TLSVersion.TLSv1_3\n    ctx.verify_mode = ssl.CERT_NONE"),
    ("M16", "mTLS: client accepts any/expired server cert", "sov_trade/mtls.py",
     "    ctx.check_hostname = check_hostname\n    ctx.verify_mode = ssl.CERT_REQUIRED",
     "    ctx.check_hostname = False\n    ctx.verify_mode = ssl.CERT_NONE"),
    ("M17", "mTLS: client certificate optional", "sov_trade/mtls.py",
     "    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\n    ctx.minimum_version = ssl.TLSVersion.TLSv1_3\n    ctx.verify_mode = ssl.CERT_REQUIRED",
     "    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\n    ctx.minimum_version = ssl.TLSVersion.TLSv1_3\n    ctx.verify_mode = ssl.CERT_OPTIONAL"),
    ("M18", "mTLS: TLS 1.2 allowed on server", "sov_trade/mtls.py",
     "    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\n    ctx.minimum_version = ssl.TLSVersion.TLSv1_3",
     "    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\n    ctx.minimum_version = ssl.TLSVersion.TLSv1_2"),
    ("M19", "mTLS: CRL not enforced", "sov_trade/mtls.py",
     "    ctx.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF",
     "    pass"),
    ("M20", "mTLS: hostname not checked", "sov_trade/mtls.py",
     "    ctx.check_hostname = check_hostname",
     "    ctx.check_hostname = False"),
    ("M21", "ceremony: 2-of-5 shares meet the quorum", "sov_trade/ceremony.py",
     "    if len(unique) < k:",
     "    if len(unique) < k - 1:"),
    ("M22", "ceremony: duplicate shares count toward quorum", "sov_trade/ceremony.py",
     "    if len(unique) < k:",
     "    if len(shares) < k:"),
    ("M23", "ceremony: published commitment not checked", "sov_trade/ceremony.py",
     "    if not hmac.compare_digest(commit_secret(material), commitment):",
     "    if False:"),
    ("M24", "ceremony: k-subset disagreement not checked", "sov_trade/ceremony.py",
     "            if trial != material:",
     "            if False:"),
    ("M25", "ceremony: reconstructed key not matched to publication", "sov_trade/ceremony.py",
     "        if pair.public_key != self.public.public_key:",
     "        if False:"),
    ("M26", "delegation: value ceiling may grow", "sov_trade/authority.py",
     "        if self.value_ceiling > parent.value_ceiling:\n            return False\n        return True",
     "        return True"),
    ("M27", "delegation: empty child set widens a constrained parent", "sov_trade/authority.py",
     "            if theirs and (not mine or not mine <= theirs):",
     "            if theirs and mine and not mine <= theirs:"),
    ("M28", "delegation: doc class not enforced by covers()", "sov_trade/authority.py",
     "        if self.doc_classes and doc_class not in self.doc_classes:\n            return False",
     "        pass"),
    ("M29", "delegation: issuance allows scope beyond parent", "sov_trade/authority.py",
     "            if not scope.is_subset_of(parent.scope):",
     "            if False:"),
    ("M30", "authority gate: verifier skips per-link narrowing", "sov_trade/protocol.py",
     "        if parent_scope is not None and not rec.scope.is_subset_of(parent_scope):",
     "        if False:"),
    ("M31", "authority gate: verifier skips scope coverage", "sov_trade/protocol.py",
     "        if not rec.scope.covers(doc_class, commodity, counterparty, value):",
     "        if False:"),
    ("M32", "replay check skipped", "sov_trade/protocol.py",
     "        if replay_key in self._replay:",
     "        if False:"),
    ("M33", "challenge nonce not checked", "sov_trade/protocol.py",
     '    if not isinstance(got, str) or not hmac.compare_digest(got.encode("utf-8"), challenge.nonce.encode("utf-8")):',
     "    if False:"),
    ("M34", "transaction binding not checked", "sov_trade/protocol.py",
     '    if txn.get("txn_id") != challenge.txn_id:',
     "    if False:"),
    ("M35", "expired assertion accepted", "sov_trade/protocol.py",
     "    if now - skew >= not_after:\n        return ReasonCode.EXPIRED",
     "    if False:\n        return ReasonCode.EXPIRED"),
    ("M36", "status list signature not verified", "sov_trade/protocol.py",
     "        if not status_sig_ok:\n            status_reason = ReasonCode.SIGNATURE_INVALID",
     "        if False:\n            status_reason = ReasonCode.SIGNATURE_INVALID"),
    ("M37", "revoked status ignored", "sov_trade/status.py",
     '    if entry.state == "revoked":\n        return ReasonCode.REVOKED',
     '    if False:\n        return ReasonCode.REVOKED'),
    ("M38", "receipt signatures not verified", "sov_trade/receipts.py",
     "        if not verify_signature(pub, payload, raw):",
     "        if False:"),
    ("M39", "transparency log: entry not bound to leaf", "sov_trade/ledger.py",
     "        if not hmac.compare_digest(recomputed, leaf):\n            return False",
     "        pass"),
    ("M40", "transparency log: consistency proof failure ignored", "sov_trade/ledger.py",
     "            if not ok:\n                self.acceptance_halted = True",
     "            if False:\n                self.acceptance_halted = True"),
    ("M41", "transparency log: missing consistency proof accepted", "sov_trade/ledger.py",
     "            if consistency is None:\n                return ReasonCode.CONSISTENCY_PROOF_MISSING",
     "            if consistency is None:\n                consistency = []"),
    ("M42", "transparency log: equal-size fork not detected", "sov_trade/ledger.py",
     "            if prev.seq == checkpoint.seq and prev.root != checkpoint.root:",
     "            if False:"),
    ("M43", "transparency log: inclusion verifier ignores tree shape (old duplicate-last tree)", "sov_trade/ledger.py",
     "        if fn & 1 or fn == sn:\n            r = _node_bytes(p, r)",
     "        if fn & 1:\n            r = _node_bytes(p, r)"),
    ("M44", "transparency log: consistency verifier skips second-root check", "sov_trade/ledger.py",
     "        and hmac.compare_digest(sr, bytes.fromhex(second_root))\n    )",
     "    )"),
    ("M45", "JCS: keys sorted by code point, not UTF-16", "sov_trade/canonical.py",
     '        return key.encode("utf-16-be")',
     '        return key.encode("utf-32-be")'),
    ("M46", "JCS: floats accepted", "sov_trade/canonical.py",
     '        raise CanonicalizationError(\n            "floating-point numbers are not accepted in signed objects"\n        )',
     "        return repr(value)"),
    ("M47", "JCS: unsafe integers accepted", "sov_trade/canonical.py",
     "        if abs(value) > MAX_SAFE_INTEGER:",
     "        if False:"),
    ("M48", "PKCS#11: key generated extractable and check removed", "sov_trade/pkcs11.py",
     "                    Attribute.SENSITIVE: True,\n                    Attribute.EXTRACTABLE: False,",
     "                    Attribute.SENSITIVE: False,\n                    Attribute.EXTRACTABLE: True,"),
    ("M49", "PKCS#11: sign-time custody check removed", "sov_trade/pkcs11.py",
     "            if bool(priv[Attribute.EXTRACTABLE]) is not False or bool(priv[Attribute.SENSITIVE]) is not True:",
     "            if False:"),
    ("M50", "PKCS#11: ambiguous key label accepted", "sov_trade/pkcs11.py",
     "    if len(objs) > 1:\n        # Ambiguous label",
     "    if False:\n        # Ambiguous label"),
    ("M51", "SAE signature check skipped", "sov_trade/assertion.py",
     "    if not verify_all_signatures(triples):",
     "    if False:"),
    ("M52", "authority gate missing fails open", "sov_trade/authority.py",
     '        return {"gate_passed": False, "errors": ["authority gate unavailable (fail closed)"]}',
     '        return {"gate_passed": True, "errors": [], "skipped": True}'),
]

# Mutations argued to be equivalent (no observable behaviour change without
# breaking SHA-256). They are still run and reported; a survivor here is
# reported as SURVIVED_EQUIVALENT and does not fail the run. A KILLED result
# would mean the argument is wrong.
EQUIVALENT = {
    "M24": "every k-subset is reconstructed recursively, and the recursive call already "
           "rejects any subset whose secret misses the published SHA-256 commitment; "
           "two subsets can only disagree with a SHA-256 collision",
}

TESTS = sorted(str(p.relative_to(REPO)) for p in (REPO / "tests").glob("test_sc_sov_trade_001*.py"))


def run_one(py: str, mid: str, prop: str, rel: str | None, old: str, new: str,
            control_failures: frozenset[str] = frozenset()) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix=f"sov-mut-{mid}-"))
    root = tmp / "semantic_compiler"
    shutil.copytree(REPO, root, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".hypothesis", "verify-out"))
    if rel is not None:
        target = root / rel
        text = target.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            shutil.rmtree(tmp)
            return {"id": mid, "property": prop, "file": rel, "status": "INVALID",
                    "detail": f"pattern found {count} times"}
        target.write_text(text.replace(old, new), encoding="utf-8")
    junit = tmp / "junit.xml"
    env = dict(os.environ, PYTHONPATH=str(tmp), SOV_TRADE_FUZZ_EXAMPLES="50", PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    proc = subprocess.run(
        [py, "-m", "pytest", *TESTS, "-q", "-p", "no:cacheprovider", f"--junitxml={junit}",
         "-o", "junit_family=xunit2"],
        cwd=root, env=env, capture_output=True, text=True, check=False,
    )
    failed: list[str] = []
    if junit.exists():
        for case in ET.parse(junit).getroot().iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                failed.append(f"{case.get('classname')}::{case.get('name')}")
    shutil.rmtree(tmp)
    caught = [f for f in failed if f not in control_failures]
    if rel is None:
        status = "CONTROL_OK" if not failed and proc.returncode == 0 else "CONTROL_FAILED"
    else:
        status = "KILLED" if caught else "SURVIVED"
    return {"id": mid, "property": prop, "file": rel, "status": status, "pytest_rc": proc.returncode,
            "failing_tests": caught, "n_failing": len(caught), "seconds": round(time.time() - t0, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--out", default=None)
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    results = []
    # Control: the unmutated tree must pass, otherwise every mutation would
    # look "killed" by pre-existing failures.
    control = run_one(args.python, "M00", "control (no mutation)", None, "", "")
    print(f"M00 {control['status']:8} {control.get('n_failing', '-'):>4} control (no mutation)", flush=True)
    results.append(control)
    if control["status"] != "CONTROL_OK":
        print("control run failed; mutation results would be meaningless")
        if args.out:
            Path(args.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
        return 2
    for mid, prop, rel, old, new in MUTATIONS:
        if args.only and mid not in args.only:
            continue
        r = run_one(args.python, mid, prop, rel, old, new)
        if r["status"] == "SURVIVED" and mid in EQUIVALENT:
            r["status"] = "SURVIVED_EQUIVALENT"
            r["equivalence_argument"] = EQUIVALENT[mid]
        results.append(r)
        print(f"{r['id']} {r['status']:8} {r.get('n_failing', '-'):>4} {prop}", flush=True)
    if args.out:
        Path(args.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    muts = [r for r in results if r["id"] != "M00"]
    eq = [r for r in muts if r["status"] == "SURVIVED_EQUIVALENT"]
    bad = [r for r in muts if r["status"] not in ("KILLED", "SURVIVED_EQUIVALENT")]
    killed = len(muts) - len(bad) - len(eq)
    print(f"\n{killed}/{len(muts)} killed; equivalent survivors: {[r['id'] for r in eq]}; "
          f"survived/invalid: {[r['id'] for r in bad]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
