"""Known-answer tests from official vectors (no invented vectors).

Sources (rebuilt by scripts/sov_trade/build_kat_fixtures.py):
  * RFC 8032 section 7.1 Ed25519 test vectors (TEST 1, 2, 3, 1024, SHA(abc)).
  * NIST ACVP-Server ML-DSA-keyGen-FIPS204 and ML-DSA-sigVer-FIPS204,
    ML-DSA-65 groups (sigVer: external interface, pure, with context).
  * RFC 8785 reference test data (cyberphone/json-canonicalization).
  * RFC 6962/9162 Merkle inclusion and consistency probes
    (transparency-dev/merkle testdata).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography

pytestmark = pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)

KAT = Path(__file__).resolve().parent / "fixtures" / "sov_trade_kat"


def _load(name: str) -> dict:
    return json.loads((KAT / name).read_text(encoding="utf-8"))


ED = _load("rfc8032_ed25519.json")["vectors"]
KEYGEN = _load("acvp_mldsa65_keygen.json")["tests"]
SIGVER = _load("acvp_mldsa65_sigver.json")["tests"]
JCS = _load("rfc8785_jcs.json")["cases"]
MERKLE = _load("rfc9162_merkle_proofs.json")


def test_fixture_counts_are_complete() -> None:
    assert [v["name"] for v in ED] == ["TEST 1", "TEST 2", "TEST 3", "TEST 1024", "TEST SHA(abc)"]
    assert len(KEYGEN) == 25
    assert len(SIGVER) == 15
    assert sum(t["testPassed"] for t in SIGVER) == 3
    assert {c["name"] for c in JCS} == {"arrays", "french", "structures", "unicode", "values", "weird"}
    assert len(MERKLE["inclusion"]) == 98 and len(MERKLE["consistency"]) == 98


@pytest.mark.parametrize("vec", ED, ids=[v["name"] for v in ED])
def test_rfc8032_ed25519(vec: dict) -> None:
    from semantic_compiler.sov_trade.crypto import ALGORITHMS, ALG_ED25519, PublicKey
    from semantic_compiler.sov_trade.ceremony import ed25519_keypair_from_secret

    sk, pk = bytes.fromhex(vec["secret_key"]), bytes.fromhex(vec["public_key"])
    msg, sig = bytes.fromhex(vec["message"]), bytes.fromhex(vec["signature"])
    alg = ALGORITHMS[ALG_ED25519]
    # Deterministic signing: exact signature bytes.
    assert alg.sign(sk, msg) == sig
    assert ed25519_keypair_from_secret(sk).public_key == pk
    assert alg.verify(pk, msg, sig)
    assert PublicKey(algorithm=ALG_ED25519, public_key=pk).verify(msg, sig)
    bad = bytearray(sig)
    bad[0] ^= 1
    assert not alg.verify(pk, msg, bytes(bad))
    assert not alg.verify(pk, msg + b"x", sig)


@pytest.mark.parametrize("vec", KEYGEN, ids=[f"tc{t['tcId']}" for t in KEYGEN])
def test_fips204_mldsa65_keygen(vec: dict) -> None:
    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

    key = MLDSA65PrivateKey.from_seed_bytes(bytes.fromhex(vec["seed"]))
    assert key.public_key().public_bytes_raw().hex().upper() == vec["pk"].upper()


@pytest.mark.parametrize("vec", SIGVER, ids=[f"tc{t['tcId']}" for t in SIGVER])
def test_fips204_mldsa65_sigver(vec: dict) -> None:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PublicKey
    from semantic_compiler.sov_trade.crypto import ALGORITHMS, ALG_ML_DSA_65, ML_DSA_CONTEXT

    pk = bytes.fromhex(vec["pk"])
    msg = bytes.fromhex(vec["message"])
    ctx = bytes.fromhex(vec["context"])
    sig = bytes.fromhex(vec["signature"])
    try:
        MLDSA65PublicKey.from_public_bytes(pk).verify(sig, msg, ctx)
        ok = True
    except InvalidSignature:
        ok = False
    assert ok is vec["testPassed"], vec["reason"]
    # The project verifier is bound to its own signing context; it must
    # accept an official vector only when the vector's context is ours.
    project_ok = ALGORITHMS[ALG_ML_DSA_65].verify(pk, msg, sig)
    assert project_ok is (vec["testPassed"] and ctx == ML_DSA_CONTEXT)


@pytest.mark.parametrize("case", JCS, ids=[c["name"] for c in JCS])
def test_rfc8785_jcs(case: dict) -> None:
    from semantic_compiler.sov_trade.canonical import CanonicalizationError, canonical_json

    value = json.loads(case["input"])
    if case["name"] in {"structures", "values"}:
        # These vectors contain non-integer numbers. The signing profile
        # refuses floats (PROVISIONAL_DEFAULT), so the vector must be refused,
        # never mis-serialized.
        with pytest.raises(CanonicalizationError):
            canonical_json(value)
        return
    assert canonical_json(value) == case["output"].encode("utf-8")


def test_rfc8785_utf16_sort_order_section_3_2_3() -> None:
    """RFC 8785 3.2.3: keys sort by UTF-16 code units, so U+1F602 (surrogates
    D83D DE02) sorts BEFORE U+FB33. A code-point sort gets this wrong."""
    from semantic_compiler.sov_trade.canonical import canonical_json

    out = canonical_json({"\ufb33": 1, "\U0001F602": 2}).decode("utf-8")
    assert out.index("\U0001F602") < out.index("\ufb33")


def _all_sha256(*values) -> bool:
    flat = []
    for v in values:
        flat.extend(v if isinstance(v, list) else [v])
    return all(isinstance(x, str) and len(x) == 64 for x in flat)


@pytest.mark.parametrize("probe", MERKLE["inclusion"], ids=[p["file"] for p in MERKLE["inclusion"]])
def test_rfc9162_inclusion_probe(probe: dict) -> None:
    from semantic_compiler.sov_trade.ledger import verify_inclusion

    root, leaf = probe["root"], probe["leafHash"]
    if root is None or leaf is None:
        assert probe["wantErr"]
        return
    ok = verify_inclusion(leaf, probe["leafIdx"], probe["treeSize"], probe["proof"], root)
    if not _all_sha256(root, leaf, probe["proof"]):
        # Upstream "don't care" placeholders are not 32-byte hashes; this
        # verifier refuses any non-SHA-256-sized hash (fail closed).
        assert ok is False
        return
    assert ok is (not probe["wantErr"]), probe["desc"]


@pytest.mark.parametrize("probe", MERKLE["consistency"], ids=[p["file"] for p in MERKLE["consistency"]])
def test_rfc9162_consistency_probe(probe: dict) -> None:
    from semantic_compiler.sov_trade.ledger import verify_consistency

    r1, r2 = probe["root1"], probe["root2"]
    if r1 is None or r2 is None:
        assert probe["wantErr"]
        return
    if probe["size1"] == 0:
        # Size-0 trees are trivially consistent in RFC 9162; the ledger
        # never stores an empty checkpoint, and verify_consistency refuses
        # size1 == 0 (fail closed).
        assert verify_consistency(0, probe["size2"], r1, r2, probe["proof"]) is False
        return
    ok = verify_consistency(probe["size1"], probe["size2"], r1, r2, probe["proof"])
    if not _all_sha256(r1, r2, probe["proof"]):
        assert ok is False
        return
    assert ok is (not probe["wantErr"]), probe["desc"]


def test_rfc9162_reference_roots() -> None:
    """transparency-dev/merkle testonly RootHashes for its 8 LeafInputs."""
    import hashlib

    from semantic_compiler.sov_trade.ledger import merkle_root

    leaves_in = ["", "00", "10", "2021", "3031", "40414243", "5051525354555657",
                 "606162636465666768696a6b6c6d6e6f"]
    roots = [
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d",
        "fac54203e7cc696cf0dfcb42c92a1d9dbaf70ad9e621f4bd8d98662f00e3c125",
        "aeb6bcfe274b70a14fb067a5e5578264db0fa9b51af5e0ba159158f329e06e77",
        "d37ee418976dd95753c1c73862b9398fa2a2cf9b4ff0fdfe8b30cd95209614b7",
        "4e3bbb1f7b478dcfe71fb631631519a3bca12c9aefca1612bfce4c13a86264d4",
        "76e67dadbcdf1e10e1b74ddc608abd2f98dfb16fbce75277b5232a127f2087ef",
        "ddb89be403809e325750d3d263cd78929c2942b7942a34b77e122c9594a74c8c",
        "5dc9da79a70659a9ad559cb701ded9a2ab9d823aad2f4960cfe370eff4604328",
    ]
    leaf_hashes = [hashlib.sha256(b"\x00" + bytes.fromhex(x)).hexdigest() for x in leaves_in]
    for size in range(len(roots)):
        assert merkle_root(leaf_hashes[:size]) == roots[size], size
