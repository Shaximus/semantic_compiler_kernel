#!/usr/bin/env python3
"""Rebuild tests/fixtures/sov_trade_kat/ from the official upstream sources.

Nothing in the fixtures is hand-written. Each file records its source URL
and upstream revision. Run from a directory that holds the downloads:

  rfc8032.txt   https://www.rfc-editor.org/rfc/rfc8032.txt
  ML-DSA-keyGen-FIPS204/internalProjection.json
  ML-DSA-sigVer-FIPS204/internalProjection.json
                https://github.com/usnistgov/ACVP-Server gen-val/json-files
  jcs_in_<name>.json, jcs_out_<name>.json
                https://github.com/cyberphone/json-canonicalization testdata
  tdev-merkle/  git clone https://github.com/transparency-dev/merkle

usage: build_kat_fixtures.py <download-dir> <out-dir> <acvp-rev> <jcs-rev> <merkle-rev>
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path


def rfc8032(src: Path) -> list[dict]:
    text = src.read_text(encoding="utf-8")
    section = text[text.index("7.1.  Test Vectors for Ed25519\n"):text.index("7.2.  Test Vectors for Ed25519ctx\n")]
    # Drop page headers and footers.
    lines = [
        ln for ln in section.splitlines()
        if not ln.startswith("RFC 8032") and not ln.startswith("Josefsson")
    ]
    section = "\n".join(lines)
    out = []
    for block in section.split("-----TEST ")[1:]:
        name = block.splitlines()[0].strip()
        def field(label: str, nxt: str) -> str:
            m = re.search(label + r"[^\n]*:\n(.*?)\n\s*" + nxt, block, re.S)
            assert m, (name, label)
            return re.sub(r"[^0-9a-f]", "", m.group(1))
        out.append({
            "name": f"TEST {name}",
            "secret_key": field("SECRET KEY", "PUBLIC KEY"),
            "public_key": field("PUBLIC KEY", "MESSAGE"),
            "message": field(r"MESSAGE \(length \d+ bytes?\)", "SIGNATURE"),
        })
        sig = re.search(r"SIGNATURE:\n(.*?)(?:\n\s*\n|\Z)", block, re.S)
        out[-1]["signature"] = re.sub(r"[^0-9a-f]", "", sig.group(1))
        assert len(out[-1]["signature"]) == 128, name
        assert len(out[-1]["public_key"]) == 64 and len(out[-1]["secret_key"]) == 64
    return out


def main() -> None:
    dl, out, acvp_rev, jcs_rev, merkle_rev = sys.argv[1:6]
    dl, out = Path(dl), Path(out)
    out.mkdir(parents=True, exist_ok=True)

    vectors = rfc8032(dl / "rfc8032.txt")
    (out / "rfc8032_ed25519.json").write_text(json.dumps({
        "source": "RFC 8032 section 7.1, https://www.rfc-editor.org/rfc/rfc8032.txt",
        "vectors": vectors,
    }, indent=1) + "\n", encoding="utf-8")

    keygen = json.loads((dl / "ML-DSA-keyGen-FIPS204/internalProjection.json").read_text())
    groups = [g for g in keygen["testGroups"] if g["parameterSet"] == "ML-DSA-65"]
    (out / "acvp_mldsa65_keygen.json").write_text(json.dumps({
        "source": "NIST ACVP-Server gen-val/json-files/ML-DSA-keyGen-FIPS204/internalProjection.json",
        "upstream_revision": acvp_rev,
        "parameterSet": "ML-DSA-65",
        "tests": [{"tcId": t["tcId"], "seed": t["seed"], "pk": t["pk"]} for g in groups for t in g["tests"]],
    }, indent=1) + "\n", encoding="utf-8")

    sigver = json.loads((dl / "ML-DSA-sigVer-FIPS204/internalProjection.json").read_text())
    groups = [
        g for g in sigver["testGroups"]
        if g["parameterSet"] == "ML-DSA-65" and g.get("signatureInterface") == "external"
        and g.get("preHash") == "pure"
    ]
    (out / "acvp_mldsa65_sigver.json").write_text(json.dumps({
        "source": "NIST ACVP-Server gen-val/json-files/ML-DSA-sigVer-FIPS204/internalProjection.json",
        "upstream_revision": acvp_rev,
        "parameterSet": "ML-DSA-65",
        "signatureInterface": "external",
        "preHash": "pure",
        "tests": [
            {k: t[k] for k in ("tcId", "testPassed", "pk", "message", "context", "signature", "reason")}
            for g in groups for t in g["tests"]
        ],
    }, indent=1) + "\n", encoding="utf-8")

    jcs = []
    for name in ("arrays", "french", "structures", "unicode", "values", "weird"):
        jcs.append({
            "name": name,
            "input": (dl / f"jcs_in_{name}.json").read_text(encoding="utf-8"),
            "output": (dl / f"jcs_out_{name}.json").read_bytes().decode("utf-8"),
        })
    (out / "rfc8785_jcs.json").write_text(json.dumps({
        "source": "cyberphone/json-canonicalization testdata (RFC 8785 reference test data)",
        "upstream_revision": jcs_rev,
        "cases": jcs,
    }, ensure_ascii=True, indent=1) + "\n", encoding="utf-8")

    def b64hex(v):
        if v is None:
            return None
        if isinstance(v, list):
            return [base64.b64decode(x).hex() for x in v]
        return base64.b64decode(v).hex()

    root = dl / "tdev-merkle" / "testdata"
    inc, con = [], []
    for path in sorted((root / "inclusion").rglob("*.json")):
        d = json.loads(path.read_text())
        inc.append({
            "file": str(path.relative_to(root)), "leafIdx": d["leafIdx"], "treeSize": d["treeSize"],
            "root": b64hex(d.get("root")), "leafHash": b64hex(d.get("leafHash")),
            "proof": b64hex(d.get("proof")) or [], "wantErr": d["wantErr"], "desc": d["desc"],
        })
    for path in sorted((root / "consistency").rglob("*.json")):
        d = json.loads(path.read_text())
        con.append({
            "file": str(path.relative_to(root)), "size1": d["size1"], "size2": d["size2"],
            "root1": b64hex(d.get("root1")), "root2": b64hex(d.get("root2")),
            "proof": b64hex(d.get("proof")) or [], "wantErr": d["wantErr"], "desc": d["desc"],
        })
    (out / "rfc9162_merkle_proofs.json").write_text(json.dumps({
        "source": "transparency-dev/merkle testdata/inclusion and testdata/consistency (RFC 6962/9162 hashing)",
        "upstream_revision": merkle_rev,
        "inclusion": inc,
        "consistency": con,
    }, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
