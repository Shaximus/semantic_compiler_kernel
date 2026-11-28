"""Item 2: Ed25519 + ML-DSA-65 hybrid signatures (both must verify)."""

from __future__ import annotations

import pytest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography

pytestmark = pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)

if have_cryptography():
    from semantic_compiler.sov_trade.crypto import (
        ALG_ED25519,
        ALG_ML_DSA_65,
        ED25519_PUBLIC_LEN,
        ED25519_SIGNATURE_LEN,
        MLDSA65_PUBLIC_LEN,
        MLDSA65_SIGNATURE_LEN,
        SUITE_ED25519_MLDSA65,
        PublicKey,
        decode_hybrid_map,
        encode_hybrid_public,
        encode_hybrid_signature,
        generate_ed25519,
        generate_hybrid,
        generate_mldsa65,
        verify_all_signatures,
        verify_hybrid,
    )


@pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)
class TestHybridSignature:
    def test_hybrid_round_trip(self) -> None:
        pair = generate_hybrid()
        assert pair.algorithm == SUITE_ED25519_MLDSA65
        message = b"export licence 42"
        signature = pair.sign(message)
        assert pair.public_only().verify(message, signature)
        assert not pair.public_only().verify(b"other", signature)

    def test_ed25519_member_forged_fails(self) -> None:
        pair = generate_hybrid()
        message = b"payload"
        signature = pair.sign(message)
        members = decode_hybrid_map(signature, "sig")
        members[ALG_ED25519] = b"\x00" * ED25519_SIGNATURE_LEN
        forged = encode_hybrid_signature(members)
        assert not pair.public_only().verify(message, forged)

    def test_mldsa_member_forged_fails(self) -> None:
        pair = generate_hybrid()
        message = b"payload"
        signature = pair.sign(message)
        members = decode_hybrid_map(signature, "sig")
        flipped = bytearray(members[ALG_ML_DSA_65])
        flipped[0] ^= 0x01
        members[ALG_ML_DSA_65] = bytes(flipped)
        forged = encode_hybrid_signature(members)
        assert not pair.public_only().verify(message, forged)

    def test_downgrade_to_bare_ed25519_fails(self) -> None:
        pair = generate_hybrid()
        message = b"payload"
        # A lone Ed25519 signature (or the extracted member) is not a hybrid token.
        ed = generate_ed25519()
        bare = ed.sign(message)
        assert not pair.public_only().verify(message, bare)
        members = decode_hybrid_map(pair.sign(message), "sig")
        assert not pair.public_only().verify(message, members[ALG_ED25519])

    def test_algorithm_stripping_fails(self) -> None:
        pair = generate_hybrid()
        message = b"payload"
        members = decode_hybrid_map(pair.sign(message), "sig")
        # Drop ML-DSA, keep only Ed25519 in a hybrid-looking object.
        import json
        stripped = json.dumps(
            {
                "suite": SUITE_ED25519_MLDSA65,
                "v": 1,
                "members": [{"alg": ALG_ED25519, "sig": members[ALG_ED25519].hex()}],
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        assert not pair.public_only().verify(message, stripped)
        # Claiming a weaker suite also fails.
        weaker = json.dumps(
            {"suite": ALG_ED25519, "v": 1, "members": [{"alg": ALG_ED25519, "sig": members[ALG_ED25519].hex()}]},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        assert not pair.public_only().verify(message, weaker)

    def test_wrong_length_key_or_signature_fails(self) -> None:
        pair = generate_hybrid()
        message = b"payload"
        signature = pair.sign(message)
        members = decode_hybrid_map(signature, "sig")
        short = dict(members)
        short[ALG_ML_DSA_65] = members[ALG_ML_DSA_65][:-1]
        with pytest.raises(ValueError, match="length"):
            encode_hybrid_signature(short)
        long_ed = dict(members)
        long_ed[ALG_ED25519] = members[ALG_ED25519] + b"\x00"
        with pytest.raises(ValueError, match="length"):
            encode_hybrid_signature(long_ed)
        # Even if we sneak a wrong-length field past the encoder, verify is false.
        import json
        sneaky = json.dumps(
            {
                "suite": SUITE_ED25519_MLDSA65,
                "v": 1,
                "members": [
                    {"alg": ALG_ED25519, "sig": members[ALG_ED25519].hex()},
                    {"alg": ALG_ML_DSA_65, "sig": members[ALG_ML_DSA_65][:8].hex()},
                ],
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        assert not pair.public_only().verify(message, sneaky)

    def test_mixed_keys_fail(self) -> None:
        a = generate_hybrid()
        b = generate_hybrid()
        message = b"payload"
        # Sign with A, verify with B's public key.
        assert not b.public_only().verify(message, a.sign(message))
        # Swap the ML-DSA public of A for B's, keep A's Ed25519 public.
        pubs_a = decode_hybrid_map(a.public_key, "public")
        pubs_b = decode_hybrid_map(b.public_key, "public")
        mixed = encode_hybrid_public({
            ALG_ED25519: pubs_a[ALG_ED25519],
            ALG_ML_DSA_65: pubs_b[ALG_ML_DSA_65],
        })
        mixed_pub = PublicKey(algorithm=SUITE_ED25519_MLDSA65, public_key=mixed)
        assert not mixed_pub.verify(message, a.sign(message))
        # Using an Ed25519 public in the ML-DSA slot is rejected at encode time.
        with pytest.raises(ValueError, match="length"):
            encode_hybrid_public({
                ALG_ED25519: pubs_a[ALG_ED25519],
                ALG_ML_DSA_65: pubs_a[ALG_ED25519],
            })

    def test_verify_all_signatures_still_requires_every_member(self) -> None:
        ed = generate_ed25519()
        pq = generate_mldsa65()
        message = b"both"
        good = [
            (ed.public_only(), message, ed.sign(message)),
            (pq.public_only(), message, pq.sign(message)),
        ]
        assert verify_all_signatures(good)
        broken = list(good)
        broken[1] = (pq.public_only(), message, b"\x00" * MLDSA65_SIGNATURE_LEN)
        assert not verify_all_signatures(broken)
        assert not verify_all_signatures([])

    def test_sizes_match_fips_204_and_rfc_8032(self) -> None:
        assert ED25519_PUBLIC_LEN == 32
        assert ED25519_SIGNATURE_LEN == 64
        assert MLDSA65_PUBLIC_LEN == 1952
        assert MLDSA65_SIGNATURE_LEN == 3309
        pq = generate_mldsa65()
        assert len(pq.public_key) == 1952
        assert len(pq.sign(b"x")) == 3309
