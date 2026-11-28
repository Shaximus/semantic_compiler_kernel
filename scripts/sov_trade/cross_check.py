#!/usr/bin/env python3
"""Independent cross-check of SC-SOV-TRADE-001 artefacts with OpenSSL.

Every check runs the `openssl` CLI (a tool that is not project code) on
artefacts produced by the project, plus the reverse direction where it
makes sense (OpenSSL produces, project verifies). All keys are TEST keys
generated per run in a temporary directory; private keys are never
written to the evidence output.

  1. Ed25519 signature: `openssl pkeyutl -verify -rawin` (+ tamper fails).
  2. Hybrid signature: Ed25519 half and ML-DSA-65 half, each verified by
     OpenSSL 3.5+ (ML-DSA with context-string SC-SOV-TRADE-001/v1); wrong
     context fails.
  3. RFC 3161: `openssl ts -verify` on a project token (+ tamper fails);
     reverse: `openssl ts -reply` token verified by the project client.
  4. mTLS: `openssl s_client` against the project's TLS 1.3 mTLS server:
     valid client accepted; expired client cert, no client cert and
     TLS 1.2 rejected.

usage: cross_check.py <out-dir>   (writes cross_check.json and cross_check.log)
"""

from __future__ import annotations

import json
import shlex
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

LOG: list[str] = []
RESULTS: list[dict] = []


def run(name: str, cmd: list[str], *, expect_ok: bool, must_contain: str | None = None,
        stdin: bytes | None = None, cwd: str | None = None, timeout: int = 20) -> dict:
    proc = subprocess.run(cmd, input=stdin, capture_output=True, cwd=cwd, timeout=timeout, check=False)
    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")
    ok = (proc.returncode == 0) == expect_ok
    if must_contain is not None:
        ok = ok and (must_contain in out or must_contain in err)
    rec = {"check": name, "cmd": " ".join(shlex.quote(c) for c in cmd), "rc": proc.returncode,
           "expect": "success" if expect_ok else "failure", "must_contain": must_contain,
           "stdout_tail": out.strip().splitlines()[-6:], "stderr_tail": err.strip().splitlines()[-6:],
           "result": "PASS" if ok else "FAIL"}
    RESULTS.append(rec)
    LOG.append(f"$ {rec['cmd']}\n[rc={proc.returncode}] expect {rec['expect']} -> {rec['result']}\n{out}{err}")
    return rec


def main() -> int:
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="sov-xcheck-"))
    LOG.append(f"# OpenSSL: {subprocess.run(['openssl', 'version'], capture_output=True, text=True).stdout.strip()}")
    LOG.append(f"# scratch dir (TEST keys only, deleted after run): {work}")

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PublicKey

    from semantic_compiler.sov_trade.crypto import (
        ALG_ED25519, ALG_ML_DSA_65, ML_DSA_CONTEXT, decode_hybrid_map,
        generate_ed25519, generate_hybrid, sign_hybrid,
    )

    spki = (serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    msg = b"SC-SOV-TRADE-001 cross-check message"
    (work / "msg.bin").write_bytes(msg)
    (work / "tampered.bin").write_bytes(msg + b"!")

    # 1. Ed25519
    ed = generate_ed25519()
    (work / "ed25519.pub.pem").write_bytes(Ed25519PublicKey.from_public_bytes(ed.public_key).public_bytes(*spki))
    (work / "ed25519.sig").write_bytes(ed.sign(msg))
    base = ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey"]
    run("ed25519: openssl verifies project signature",
        base + ["ed25519.pub.pem", "-rawin", "-in", "msg.bin", "-sigfile", "ed25519.sig"],
        expect_ok=True, must_contain="Signature Verified Successfully", cwd=str(work))
    run("ed25519: openssl rejects tampered message",
        base + ["ed25519.pub.pem", "-rawin", "-in", "tampered.bin", "-sigfile", "ed25519.sig"],
        expect_ok=False, cwd=str(work))

    # 2. Hybrid
    hyb = generate_hybrid()
    pubs = decode_hybrid_map(hyb.public_key, "public")
    sigs = decode_hybrid_map(sign_hybrid(hyb, msg), "sig")
    (work / "hyb-ed.pub.pem").write_bytes(Ed25519PublicKey.from_public_bytes(pubs[ALG_ED25519]).public_bytes(*spki))
    (work / "hyb-mldsa.pub.pem").write_bytes(MLDSA65PublicKey.from_public_bytes(pubs[ALG_ML_DSA_65]).public_bytes(*spki))
    (work / "hyb-ed.sig").write_bytes(sigs[ALG_ED25519])
    (work / "hyb-mldsa.sig").write_bytes(sigs[ALG_ML_DSA_65])
    ctx = ML_DSA_CONTEXT.decode("ascii")
    run("hybrid: openssl verifies Ed25519 half",
        base + ["hyb-ed.pub.pem", "-rawin", "-in", "msg.bin", "-sigfile", "hyb-ed.sig"],
        expect_ok=True, must_contain="Signature Verified Successfully", cwd=str(work))
    run("hybrid: openssl 3.5+ verifies ML-DSA-65 half (context-string)",
        base + ["hyb-mldsa.pub.pem", "-rawin", "-in", "msg.bin", "-sigfile", "hyb-mldsa.sig",
                "-pkeyopt", f"context-string:{ctx}"],
        expect_ok=True, must_contain="Signature Verified Successfully", cwd=str(work))
    run("hybrid: openssl rejects ML-DSA-65 half under a different context",
        base + ["hyb-mldsa.pub.pem", "-rawin", "-in", "msg.bin", "-sigfile", "hyb-mldsa.sig",
                "-pkeyopt", "context-string:wrong-context"],
        expect_ok=False, cwd=str(work))
    run("hybrid: openssl rejects ML-DSA-65 half on tampered message",
        base + ["hyb-mldsa.pub.pem", "-rawin", "-in", "tampered.bin", "-sigfile", "hyb-mldsa.sig",
                "-pkeyopt", f"context-string:{ctx}"],
        expect_ok=False, cwd=str(work))

    # 3. RFC 3161
    from semantic_compiler.sov_trade.timestamp import (
        TEST_TSA_POLICY, TimestampError, build_request, generate_test_tsa, issue_token, verify_token,
    )
    tsa = generate_test_tsa()
    data = b"SC-SOV-TRADE-001 timestamped assertion bytes"
    (work / "ts-data.bin").write_bytes(data)
    req = build_request(data)
    tok = issue_token(tsa, req)
    (work / "req.tsq").write_bytes(req.der)
    (work / "resp.tsr").write_bytes(tok.der)
    (work / "tsa-ca.pem").write_bytes(tsa.ca_cert.public_bytes(serialization.Encoding.PEM))
    (work / "tsa.pem").write_bytes(tsa.tsa_cert.public_bytes(serialization.Encoding.PEM))
    ts_base = ["openssl", "ts", "-verify", "-in", "resp.tsr", "-CAfile", "tsa-ca.pem", "-untrusted", "tsa.pem"]
    run("rfc3161: openssl ts -verify (queryfile) on project token",
        ts_base + ["-queryfile", "req.tsq"], expect_ok=True, must_contain="Verification: OK", cwd=str(work))
    run("rfc3161: openssl ts -verify (data) on project token",
        ts_base + ["-data", "ts-data.bin"], expect_ok=True, must_contain="Verification: OK", cwd=str(work))
    run("rfc3161: openssl ts -verify rejects tampered data",
        ts_base + ["-data", "tampered.bin"], expect_ok=False, cwd=str(work))
    # Reverse: OpenSSL TSA issues, project verifies. TEST TSA key written to scratch only.
    (work / "tsa.key").write_bytes(tsa.tsa_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    (work / "tsa.cnf").write_text(
        "[ tsa ]\ndefault_tsa = tsa_config1\n[ tsa_config1 ]\n"
        f"dir = {work}\nserial = {work}/tsaserial\nsigner_cert = {work}/tsa.pem\n"
        f"certs = {work}/tsa.pem\nsigner_key = {work}/tsa.key\nsigner_digest = sha256\n"
        f"default_policy = {TEST_TSA_POLICY}\ndigests = sha256\naccuracy = secs:1\n"
        "ordering = no\ntsa_name = no\ness_cert_id_chain = no\ness_cert_id_alg = sha256\n",
        encoding="utf-8")
    (work / "tsaserial").write_text("01\n", encoding="utf-8")
    req2 = build_request(data)
    (work / "req2.tsq").write_bytes(req2.der)
    rep = run("rfc3161: openssl ts -reply issues a token for a project request",
              ["openssl", "ts", "-reply", "-config", "tsa.cnf", "-queryfile", "req2.tsq", "-out", "resp2.tsr"],
              expect_ok=True, cwd=str(work))
    if rep["result"] == "PASS":
        try:
            verify_token((work / "resp2.tsr").read_bytes(), data=data, nonce=req2.nonce, trusted_ca=tsa.ca_cert)
            ok, detail = True, "verify_token accepted the OpenSSL-issued token"
        except TimestampError as exc:
            ok, detail = False, f"verify_token rejected: {exc}"
        RESULTS.append({"check": "rfc3161: project client verifies OpenSSL-issued token", "result": "PASS" if ok else "FAIL",
                        "detail": detail})
        LOG.append(f"# project verify_token on OpenSSL token: {detail}")
        try:
            verify_token((work / "resp2.tsr").read_bytes(), data=data + b"x", nonce=req2.nonce, trusted_ca=tsa.ca_cert)
            ok2 = False
        except TimestampError:
            ok2 = True
        RESULTS.append({"check": "rfc3161: project client rejects OpenSSL token for other data",
                        "result": "PASS" if ok2 else "FAIL"})

    # 4. mTLS via openssl s_client against the project server context
    from semantic_compiler.sov_trade.mtls import generate_ca, issue_cert, server_context

    now = datetime.now(timezone.utc)
    ca_a = generate_ca("Nation-A TEST CA", now=now)
    ca_b = generate_ca("Nation-B TEST CA", now=now)
    server = issue_cert(ca_b, "nation-b.example", now=now, server=True)
    good = issue_cert(ca_a, "nation-a.example", now=now)
    expired = issue_cert(ca_a, "nation-a.example", now=now, days=-1)
    for name, cert in (("good", good), ("expired", expired)):
        (work / f"{name}.crt").write_bytes(cert.cert_pem)
        (work / f"{name}.key").write_bytes(cert.key_pem)  # TEST key, scratch only
    (work / "ca-b.pem").write_bytes(ca_b.cert_pem)
    sctx = server_context(ca_a.cert_pem, server)

    def serve_once(sock: socket.socket) -> None:
        try:
            conn, _ = sock.accept()
            conn.settimeout(5)
            try:
                with sctx.wrap_socket(conn, server_side=True) as tls:
                    tls.sendall(b"hello from project mTLS server\n")
                    time.sleep(0.2)
                    tls.unwrap()  # clean TLS close_notify
            except Exception as exc:  # noqa: BLE001 - rejection is the expected signal
                LOG.append(f"# project server side: {type(exc).__name__}: {exc}")
        except Exception:  # noqa: BLE001
            pass

    def s_client(name: str, extra: list[str], *, expect_ok: bool, must_contain: str | None) -> None:
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        sock.settimeout(10)
        port = sock.getsockname()[1]
        t = threading.Thread(target=serve_once, args=(sock,), daemon=True)
        t.start()
        cmd = ["openssl", "s_client", "-connect", f"127.0.0.1:{port}", "-servername", "localhost",
               "-CAfile", "ca-b.pem", "-verify_return_error", "-verify_hostname", "localhost",
               "-ign_eof", *extra]
        run(name, cmd, expect_ok=expect_ok, must_contain=must_contain, stdin=b"", cwd=str(work))
        t.join(timeout=10)
        sock.close()

    s_client("mtls: s_client with valid TEST client cert is accepted (TLS 1.3)",
             ["-tls1_3", "-cert", "good.crt", "-key", "good.key"], expect_ok=True,
             must_contain="hello from project mTLS server")
    s_client("mtls: s_client with EXPIRED client cert is rejected",
             ["-tls1_3", "-cert", "expired.crt", "-key", "expired.key"], expect_ok=False,
             must_contain="certificate expired")
    s_client("mtls: s_client without a client cert is rejected",
             ["-tls1_3"], expect_ok=False, must_contain="certificate required")
    s_client("mtls: s_client forcing TLS 1.2 is rejected",
             ["-tls1_2", "-cert", "good.crt", "-key", "good.key"], expect_ok=False,
             must_contain="protocol version")

    # Clean up TEST keys.
    import shutil
    shutil.rmtree(work)
    failed = [r for r in RESULTS if r["result"] != "PASS"]
    summary = {"openssl": LOG[0][2:], "checks": RESULTS, "passed": len(RESULTS) - len(failed),
               "failed": len(failed), "note": "All keys were TEST keys generated per run and deleted."}
    (out_dir / "cross_check.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    (out_dir / "cross_check.log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    for r in RESULTS:
        print(f"{r['result']}  {r['check']}")
    print(f"{summary['passed']}/{len(RESULTS)} cross-checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
