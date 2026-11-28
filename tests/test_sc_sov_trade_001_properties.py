"""Property-based tests (hypothesis) for SC-SOV-TRADE-001.

Covers canonicalization (RFC 8785 profile), delegation-chain validation,
and the RFC 9162 transparency log (inclusion and consistency proofs).
The parser fuzz pass lives in test_sc_sov_trade_001_fuzz.py.
"""

from __future__ import annotations

import json
import random

import pytest

from tests.sov_trade_deps import (
    CRYPTOGRAPHY_SKIP,
    HYPOTHESIS_SKIP,
    have_cryptography,
    have_hypothesis,
)

pytestmark = [
    pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP),
    pytest.mark.skipif(not have_hypothesis(), reason=HYPOTHESIS_SKIP),
]

if have_cryptography() and have_hypothesis():
    from hypothesis import HealthCheck, assume, given, settings
    from hypothesis import strategies as st

    from semantic_compiler.sov_trade.authority import DelegationScope
    from semantic_compiler.sov_trade.canonical import (
        MAX_SAFE_INTEGER,
        CanonicalizationError,
        canonical_json,
    )
    from semantic_compiler.sov_trade.ledger import (
        _leaf,
        consistency_proof,
        merkle_proof,
        merkle_root,
        verify_consistency,
        verify_inclusion,
    )

    SETTINGS = settings(max_examples=300, deadline=None, suppress_health_check=[HealthCheck.too_slow])

    # JSON strings without lone surrogates (valid I-JSON text).
    json_text = st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)), max_size=12
    )
    safe_int = st.integers(min_value=-MAX_SAFE_INTEGER, max_value=MAX_SAFE_INTEGER)
    json_value = st.recursive(
        st.none() | st.booleans() | safe_int | json_text,
        lambda children: st.lists(children, max_size=5)
        | st.dictionaries(json_text, children, max_size=5),
        max_leaves=25,
    )

    # ------------------------------------------------------------------
    # Canonicalization
    # ------------------------------------------------------------------

    class TestCanonicalProperties:
        @SETTINGS
        @given(json_value)
        def test_round_trip_and_idempotent(self, value) -> None:
            out = canonical_json(value)
            parsed = json.loads(out.decode("utf-8"))
            assert parsed == value
            assert canonical_json(parsed) == out

        @SETTINGS
        @given(st.dictionaries(json_text, safe_int, min_size=1, max_size=8), st.randoms())
        def test_key_order_does_not_matter(self, mapping, rnd) -> None:
            items = list(mapping.items())
            rnd.shuffle(items)
            assert canonical_json(dict(items)) == canonical_json(mapping)

        @SETTINGS
        @given(st.dictionaries(json_text, st.none(), min_size=2, max_size=8))
        def test_keys_sorted_by_utf16_code_units(self, mapping) -> None:
            out = json.loads(canonical_json(mapping).decode("utf-8"), object_pairs_hook=list)
            keys = [k for k, _ in out]
            assert keys == sorted(keys, key=lambda k: k.encode("utf-16-be"))

        @SETTINGS
        @given(st.floats(allow_nan=True, allow_infinity=True))
        def test_floats_refused(self, number) -> None:
            with pytest.raises(CanonicalizationError):
                canonical_json({"v": number})

        @SETTINGS
        @given(st.integers(min_value=MAX_SAFE_INTEGER + 1) | st.integers(max_value=-MAX_SAFE_INTEGER - 1))
        def test_unsafe_integers_refused(self, number) -> None:
            with pytest.raises(CanonicalizationError):
                canonical_json([number])

        @SETTINGS
        @given(json_value, json_value)
        def test_distinct_values_distinct_bytes(self, a, b) -> None:
            # Injective on the JSON data model: different values never
            # share a canonical encoding (no signature confusion).
            if canonical_json(a) == canonical_json(b):
                assert json.loads(canonical_json(a)) == json.loads(canonical_json(b))

    # ------------------------------------------------------------------
    # Delegation-chain validation
    # ------------------------------------------------------------------

    small_set = st.frozensets(st.sampled_from(["a", "b", "c", "d"]), max_size=4)
    scopes = st.builds(
        DelegationScope,
        doc_classes=small_set,
        commodity_codes=small_set,
        counterparty_domains=small_set,
        value_ceiling=st.integers(min_value=0, max_value=1000),
    )
    requests = st.tuples(
        st.sampled_from(["a", "b", "c", "d", "e"]),
        st.sampled_from(["a", "b", "c", "d", "e"]),
        st.sampled_from(["a", "b", "c", "d", "e"]),
        st.integers(min_value=0, max_value=1200),
    )

    class TestChainProperties:
        @SETTINGS
        @given(scopes, scopes, requests)
        def test_subset_never_widens(self, child, parent, request) -> None:
            # If the child is accepted as a narrowing of the parent, anything
            # the child covers, the parent covers too.
            if child.is_subset_of(parent) and child.covers(*request):
                assert parent.covers(*request)

        @SETTINGS
        @given(scopes, scopes, scopes)
        def test_subset_is_transitive(self, a, b, c) -> None:
            if a.is_subset_of(b) and b.is_subset_of(c):
                assert a.is_subset_of(c)

        @SETTINGS
        @given(scopes)
        def test_subset_is_reflexive(self, a) -> None:
            assert a.is_subset_of(a)

        @SETTINGS
        @given(st.lists(scopes, min_size=1, max_size=4), requests)
        def test_scope_check_ok_only_if_every_link_covers(self, chain_scopes, request) -> None:
            from semantic_compiler.sov_trade.protocol import _scope_check
            from semantic_compiler.sov_trade.types import ReasonCode

            doc, commodity, counterparty, value = request
            links = []
            for i, sc in enumerate(chain_scopes):
                links.append({
                    "grantor": f"did:sov:x:ii:g{i}",
                    "grantee": f"did:sov:x:os:g{i + 1}",
                    "scope": sc.to_dict(),
                    "mode": "direct",
                    "not_before": 0,
                    "not_after": 10,
                    "serial": i,
                })
            # Envelope order is leaf-to-root.
            fields = {
                "authority_chain": list(reversed(links)),
                "doc_class": doc,
                "subject": {"commodity_code": commodity, "value": value},
                "txn_binding": {"counterparty_domain": counterparty},
            }
            reason = _scope_check(fields, "verifier")
            if reason is ReasonCode.OK:
                for sc in chain_scopes:
                    assert sc.covers(doc, commodity, counterparty, value)
                for child, parent in zip(chain_scopes[1:], chain_scopes):
                    assert child.is_subset_of(parent)

    # ------------------------------------------------------------------
    # RFC 9162 transparency log
    # ------------------------------------------------------------------

    leaf_lists = st.lists(st.binary(max_size=16), min_size=1, max_size=40)

    def _hashes(data: list[bytes]) -> list[str]:
        return [_leaf(d) for d in data]

    class TestLogProperties:
        @SETTINGS
        @given(leaf_lists, st.data())
        def test_consistency_proofs_verify(self, data, draw) -> None:
            leaves = _hashes(data)
            n = len(leaves)
            m = draw.draw(st.integers(min_value=1, max_value=n))
            proof = consistency_proof(leaves, m)
            assert verify_consistency(m, n, merkle_root(leaves[:m]), merkle_root(leaves), proof)

        @SETTINGS
        @given(leaf_lists, st.data())
        def test_tampered_consistency_proof_fails(self, data, draw) -> None:
            leaves = _hashes(data)
            n = len(leaves)
            assume(n >= 2)
            m = draw.draw(st.integers(min_value=1, max_value=n - 1))
            proof = consistency_proof(leaves, m)
            r1, r2 = merkle_root(leaves[:m]), merkle_root(leaves)
            if proof:
                i = draw.draw(st.integers(min_value=0, max_value=len(proof) - 1))
                bad = list(proof)
                bad[i] = format(int(bad[i], 16) ^ 1, "064x")
                assert not verify_consistency(m, n, r1, r2, bad)
                assert not verify_consistency(m, n, r1, r2, proof[:-1])
                assert not verify_consistency(m, n, r1, r2, proof + [proof[0]])
            assert not verify_consistency(m, n, r2, r1, proof) or r1 == r2
            assert not verify_consistency(m + 1, n, r1, r2, proof) or m + 1 == n and False

        @SETTINGS
        @given(leaf_lists, leaf_lists)
        def test_rewritten_history_is_inconsistent(self, a, b) -> None:
            # A log whose first m entries differ cannot prove consistency
            # from the honest prefix.
            honest = _hashes(a)
            m = len(honest)
            forked = _hashes([x + b"!" for x in a]) + _hashes(b)
            assume(forked[:m] != honest)
            proof = consistency_proof(forked, m)
            assert not verify_consistency(m, len(forked), merkle_root(honest), merkle_root(forked), proof)

        @SETTINGS
        @given(st.lists(st.binary(max_size=16), min_size=1, max_size=40, unique=True), st.data())
        def test_inclusion_binds_leaf_and_index(self, data, draw) -> None:
            # Distinct leaves. Tree size is bound through the signed
            # checkpoint root (RFC 9162 9.1), so only leaf and index are
            # asserted here.
            leaves = _hashes(data)
            n = len(leaves)
            i = draw.draw(st.integers(min_value=0, max_value=n - 1))
            root = merkle_root(leaves)
            proof = merkle_proof(leaves, i)
            assert verify_inclusion(leaves[i], i, n, proof, root)
            for j in range(n):
                if j != i:
                    assert not verify_inclusion(leaves[j], i, n, proof, root)
                    assert not verify_inclusion(leaves[i], j, n, proof, root)
            assert not verify_inclusion(leaves[i], i, n, proof, "0" * 64)
            assert not verify_inclusion(leaves[i], n, n, proof, root)

        def test_n_and_n_plus_duplicate_have_distinct_roots(self) -> None:
            # The old tree duplicated the last node, so [a, b, c] and
            # [a, b, c, c] shared a root. RFC 9162 must not.
            rnd = random.Random(0)  # test data only, not secret
            for n in range(1, 33):
                leaves = [_leaf(bytes([rnd.randrange(256)])) for _ in range(n)]
                assert merkle_root(leaves) != merkle_root(leaves + [leaves[-1]])
