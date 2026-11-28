# SC-SOV-TRADE-001 mutation table (t616u B3)

Each mutation is applied to a scratch copy of the tree (the checkout is never edited), the sov_trade tests run against it, and the copy is deleted. A control run with no mutation must pass first (M00). Script: `scripts/sov_trade/mutation_check.py` (patterns are exact source lines; a pattern that does not match exactly once is INVALID).

- **Current tests (this head):** 51/52 killed; equivalent survivors: ['M24']; other survivors/invalid: none. Control M00: CONTROL_OK.
- **Original tests from 64eb86f, run against the fixed source:** 25/52 killed. Every mutation that survived there is now killed by a test added in this pass, except M24 (equivalent, argued below).
- Column *orig tests* = result with the PR's original tests (64eb86f) on the fixed source; *now* = result with the current tests. *First failing tests* are the tests that caught it (up to 3).
- Mutations marked with a dagger in the notes target checks that did not exist before this pass (they were added as fixes), so the original tests could not have covered them.

| ID | property broken | file | orig tests | now | # failing | first failing tests (or equivalence argument) |
|---|---|---|---|---|---|---|
| M01 | hybrid: ML-DSA-65 half not verified | `sov_trade/crypto.py` | KILLED | **KILLED** | 3 | `t_hybrid.TestHybridSignature::test_mldsa_member_forged_fails`<br>`t_hybrid.TestHybridSignature::test_mixed_keys_fail`<br>`t_regressions::test_hybrid_rejects_bad_mldsa_half_with_good_ed25519_half` |
| M02 | hybrid: Ed25519 half not verified | `sov_trade/crypto.py` | KILLED | **KILLED** | 2 | `t_hybrid.TestHybridSignature::test_ed25519_member_forged_fails`<br>`t_regressions::test_hybrid_rejects_bad_mldsa_half_with_good_ed25519_half` |
| M03 | ML-DSA-65 verify always succeeds | `sov_trade/crypto.py` | KILLED | **KILLED** | 20 | `t_hybrid.TestHybridSignature::test_mldsa_member_forged_fails`<br>`t_hybrid.TestHybridSignature::test_mixed_keys_fail`<br>`t_hybrid.TestHybridSignature::test_verify_all_signatures_still_requires_every_member` (+17 more) |
| M04 | ML-DSA-65 signing context not bound at verify | `sov_trade/crypto.py` | KILLED | **KILLED** | 20 | `t_hybrid.TestHybridSignature::test_mldsa_member_forged_fails`<br>`t_hybrid.TestHybridSignature::test_mixed_keys_fail`<br>`t_hybrid.TestHybridSignature::test_verify_all_signatures_still_requires_every_member` (+17 more) |
| M05 | Ed25519 verify always succeeds | `sov_trade/crypto.py` | KILLED | **KILLED** | 15 | `t.TestR01Impersonation::test_forged_key_cannot_impersonate_a_nation`<br>`t.TestR03Tamper::test_bit_flip_every_field`<br>`t.TestR10Hybrid::test_hybrid_with_one_broken_signature_fails` (+12 more) |
| M06 | empty signature set accepted | `sov_trade/crypto.py` | KILLED | **KILLED** | 1 | `t_hybrid.TestHybridSignature::test_verify_all_signatures_still_requires_every_member` |
| M07 | RFC 3161: TSA nonce not checked | `sov_trade/timestamp.py` | KILLED | **KILLED** | 2 | `t_regressions.TestTimestampHardening::test_wrong_nonce_rejected`<br>`t_timestamp.TestRFC3161::test_wrong_nonce_fails` |
| M08 | RFC 3161: message imprint not checked | `sov_trade/timestamp.py` | KILLED | **KILLED** | 1 | `t_timestamp.TestRFC3161::test_wrong_imprint_fails` |
| M09 | RFC 3161: TSA chain to trusted CA not checked | `sov_trade/timestamp.py` | KILLED | **KILLED** | 1 | `t_timestamp.TestRFC3161::test_untrusted_tsa_cert_fails` |
| M10 | RFC 3161: CMS signature not verified | `sov_trade/timestamp.py` | KILLED | **KILLED** | 2 | `t_fuzz.TestParserFuzz::test_timestamp_bit_flips`<br>`t_timestamp.TestRFC3161::test_tampered_token_fails` |
| M11 | RFC 3161: policy not checked | `sov_trade/timestamp.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_timestamp_policy_mismatch_rejected` |
| M12 | RFC 3161: signed message-digest not checked | `sov_trade/timestamp.py` | SURVIVED | **KILLED** | 1 | `t_fuzz.TestParserFuzz::test_timestamp_bit_flips` |
| M13 | RFC 3161: timeStamping EKU not checked | `sov_trade/timestamp.py` | SURVIVED | **KILLED** | 1 | `t_regressions.TestTimestampHardening::test_tsa_without_timestamping_eku_rejected` |
| M14 | RFC 3161: ESS signing-certificate binding not checked | `sov_trade/timestamp.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_timestamp_ess_hash_must_match_tsa_certificate` |
| M15 | mTLS: server accepts any/expired client cert (no client verification) | `sov_trade/mtls.py` | KILLED | **KILLED** | 8 | `t_mtls.TestMutualTLS::test_valid_handshake`<br>`t_mtls.TestMutualTLS::test_expired_cert_rejected`<br>`t_mtls.TestMutualTLS::test_revoked_cert_rejected` (+5 more) |
| M16 | mTLS: client accepts any/expired server cert | `sov_trade/mtls.py` | KILLED | **KILLED** | 7 | `t_mtls.TestMutualTLS::test_valid_handshake`<br>`t_mtls.TestMutualTLS::test_wrong_ca_rejected`<br>`t_mtls.TestMutualTLSRejectionReasons::test_expired_server_cert_reason` (+4 more) |
| M17 | mTLS: client certificate optional | `sov_trade/mtls.py` | SURVIVED | **KILLED** | 2 | `t_mtls.TestMutualTLSRejectionReasons::test_client_without_certificate_is_rejected`<br>`t_mtls.TestMutualTLSRejectionReasons::test_contexts_pin_tls13_and_require_peer_certs` |
| M18 | mTLS: TLS 1.2 allowed on server | `sov_trade/mtls.py` | SURVIVED | **KILLED** | 2 | `t_mtls.TestMutualTLSRejectionReasons::test_tls12_client_is_rejected`<br>`t_mtls.TestMutualTLSRejectionReasons::test_contexts_pin_tls13_and_require_peer_certs` |
| M19 | mTLS: CRL not enforced | `sov_trade/mtls.py` | KILLED | **KILLED** | 2 | `t_mtls.TestMutualTLS::test_revoked_cert_rejected`<br>`t_mtls.TestMutualTLSRejectionReasons::test_revoked_client_reason` |
| M20 | mTLS: hostname not checked | `sov_trade/mtls.py` | SURVIVED | **KILLED** | 2 | `t_mtls.TestMutualTLSRejectionReasons::test_contexts_pin_tls13_and_require_peer_certs`<br>`t_mtls.TestMutualTLSRejectionReasons::test_hostname_mismatch_is_rejected` |
| M21 | ceremony: 2-of-5 shares meet the quorum | `sov_trade/ceremony.py` | KILLED | **KILLED** | 3 | `t_ceremony.TestRootCeremony::test_two_or_fewer_cannot`<br>`t_regressions::test_two_of_five_shares_fail_on_the_quorum_rule_itself`<br>`t_regressions::test_duplicate_share_does_not_count_twice` |
| M22 | ceremony: duplicate shares count toward quorum | `sov_trade/ceremony.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_duplicate_share_does_not_count_twice` |
| M23 | ceremony: published commitment not checked | `sov_trade/ceremony.py` | KILLED | **KILLED** | 1 | `t_ceremony.TestRootCeremony::test_tampered_share_is_detected` |
| M24 | ceremony: k-subset disagreement not checked | `sov_trade/ceremony.py` | SURVIVED | **SURVIVED_EQUIVALENT** | 0 | every k-subset is reconstructed recursively, and the recursive call already rejects any subset whose secret misses the published SHA-256 commitment; two subsets can only disagree with a SHA-256 collision |
| M25 | ceremony: reconstructed key not matched to publication | `sov_trade/ceremony.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_quorum_from_another_ceremony_cannot_sign` |
| M26 | delegation: value ceiling may grow | `sov_trade/authority.py` | SURVIVED | **KILLED** | 2 | `t_properties.TestChainProperties::test_subset_never_widens`<br>`t_regressions::test_value_ceiling_cannot_grow` |
| M27 | delegation: empty child set widens a constrained parent | `sov_trade/authority.py` | SURVIVED | **KILLED** | 3 | `t_properties.TestChainProperties::test_subset_never_widens`<br>`t_properties.TestChainProperties::test_subset_is_transitive`<br>`t_regressions::test_empty_child_scope_under_constrained_parent_is_widening` |
| M28 | delegation: doc class not enforced by covers() | `sov_trade/authority.py` | KILLED | **KILLED** | 1 | `t.TestR04Scope::test_signer_outside_doc_class_rejected` |
| M29 | delegation: issuance allows scope beyond parent | `sov_trade/authority.py` | KILLED | **KILLED** | 1 | `t_adversarial.TestAdversarialDelegationEscalation::test_delegate_cannot_widen_scope` |
| M30 | authority gate: verifier skips per-link narrowing | `sov_trade/protocol.py` | SURVIVED | **KILLED** | 1 | `t_properties.TestChainProperties::test_scope_check_ok_only_if_every_link_covers` |
| M31 | authority gate: verifier skips scope coverage | `sov_trade/protocol.py` | KILLED | **KILLED** | 4 | `t.TestR04Scope::test_signer_outside_doc_class_rejected`<br>`t.TestR04Scope::test_signer_outside_commodity_rejected`<br>`t.TestR04Scope::test_signer_above_value_ceiling_rejected` (+1 more) |
| M32 | replay check skipped | `sov_trade/protocol.py` | KILLED | **KILLED** | 2 | `t.TestR05FreshnessMatrix::test_replayed`<br>`t_adversarial.TestAdversarialReplay::test_same_assertion_same_transaction_replayed` |
| M33 | challenge nonce not checked | `sov_trade/protocol.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_wrong_challenge_nonce_rejected` |
| M34 | transaction binding not checked | `sov_trade/protocol.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_wrong_transaction_binding_rejected` |
| M35 | expired assertion accepted | `sov_trade/protocol.py` | KILLED | **KILLED** | 2 | `t.TestR05FreshnessMatrix::test_expired`<br>`t.TestR15Degraded::test_clock_drift_rejects` |
| M36 | status list signature not verified | `sov_trade/protocol.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_unsigned_or_forged_status_list_is_rejected` |
| M37 | revoked status ignored | `sov_trade/status.py` | KILLED | **KILLED** | 1 | `t.TestR05FreshnessMatrix::test_revoked` |
| M38 | receipt signatures not verified | `sov_trade/receipts.py` | KILLED | **KILLED** | 1 | `t_adversarial.TestAdversarialTamperedReceipt::test_tampered_receipt_fails_offline_verification` |
| M39 | transparency log: entry not bound to leaf | `sov_trade/ledger.py` | SURVIVED | **KILLED** | 1 | `t_ledger.TestInclusionBinding::test_entry_substitution_is_rejected` |
| M40 | transparency log: consistency proof failure ignored | `sov_trade/ledger.py` | SURVIVED | **KILLED** | 2 | `t_ledger.TestCheckpointConsistency::test_rewritten_history_halts_acceptance`<br>`t_ledger.TestCheckpointConsistency::test_garbage_proof_halts_acceptance` |
| M41 | transparency log: missing consistency proof accepted | `sov_trade/ledger.py` | SURVIVED | **KILLED** | 2 | `t_ledger.TestCheckpointConsistency::test_later_checkpoint_without_proof_is_not_stored`<br>`t_ledger.TestCheckpointConsistency::test_older_checkpoint_needs_proof_too` |
| M42 | transparency log: equal-size fork not detected | `sov_trade/ledger.py` | KILLED | **KILLED** | 1 | `t.TestR08SplitView::test_forked_checkpoint_is_flagged` |
| M43 | transparency log: inclusion verifier ignores tree shape (old duplicate-last tree) | `sov_trade/ledger.py` | SURVIVED | **KILLED** | 3 | `t_kat::test_rfc9162_inclusion_probe[inclusion/3/happy-path.json]`<br>`t_ledger.TestInclusionBinding::test_valid_proof_verifies`<br>`t_properties.TestLogProperties::test_inclusion_binds_leaf_and_index` |
| M44 | transparency log: consistency verifier skips second-root check | `sov_trade/ledger.py` | SURVIVED | **KILLED** | 12 | `t_kat::test_rfc9162_consistency_probe[consistency/1/modified-proof@0-bit-@4.json]`<br>`t_kat::test_rfc9162_consistency_probe[consistency/1/modified-proof@1-bit-@4.json]`<br>`t_kat::test_rfc9162_consistency_probe[consistency/1/modified-proof@2-bit-@4.json]` (+9 more) |
| M45 | JCS: keys sorted by code point, not UTF-16 | `sov_trade/canonical.py` | SURVIVED | **KILLED** | 3 | `t_kat::test_rfc8785_jcs[weird]`<br>`t_kat::test_rfc8785_utf16_sort_order_section_3_2_3`<br>`t_properties.TestCanonicalProperties::test_keys_sorted_by_utf16_code_units` |
| M46 | JCS: floats accepted | `sov_trade/canonical.py` | SURVIVED | **KILLED** | 3 | `t_kat::test_rfc8785_jcs[structures]`<br>`t_kat::test_rfc8785_jcs[values]`<br>`t_properties.TestCanonicalProperties::test_floats_refused` |
| M47 | JCS: unsafe integers accepted | `sov_trade/canonical.py` | SURVIVED | **KILLED** | 1 | `t_properties.TestCanonicalProperties::test_unsafe_integers_refused` |
| M48 | PKCS#11: key generated extractable and check removed | `sov_trade/pkcs11.py` | KILLED | **KILLED** | 3 | `t_pkcs11.TestPKCS11Signer::test_sign_and_verify_in_token`<br>`t_pkcs11.TestPKCS11Signer::test_private_key_is_non_extractable_and_sensitive`<br>`t_pkcs11.TestPKCS11Signer::test_sign_refuses_ambiguous_label` |
| M49 | PKCS#11: sign-time custody check removed | `sov_trade/pkcs11.py` | SURVIVED | **KILLED** | 1 | `t_pkcs11.TestPKCS11Signer::test_sign_refuses_extractable_key` |
| M50 | PKCS#11: ambiguous key label accepted | `sov_trade/pkcs11.py` | SURVIVED | **KILLED** | 1 | `t_pkcs11.TestPKCS11Signer::test_sign_refuses_ambiguous_label` |
| M51 | SAE signature check skipped | `sov_trade/assertion.py` | KILLED | **KILLED** | 5 | `t.TestR01Impersonation::test_forged_key_cannot_impersonate_a_nation`<br>`t.TestR03Tamper::test_bit_flip_every_field`<br>`t.TestR10Hybrid::test_hybrid_with_one_broken_signature_fails` (+2 more) |
| M52 | authority gate missing fails open | `sov_trade/authority.py` | SURVIVED | **KILLED** | 1 | `t_regressions::test_authority_gate_unavailable_fails_closed` |

Checks introduced in this pass (dagger): M13, M14, M27, M33, M36, M39, M40, M41, M43, M44, M45, M47, M49, M50, M52.

## Tests written for survivors
In `tests/test_sc_sov_trade_001_regressions.py`, `tests/test_sc_sov_trade_001_ledger.py`, `tests/test_sc_sov_trade_001_mtls.py` (`TestMutualTLSRejectionReasons`), `tests/test_sc_sov_trade_001_pkcs11.py`, `tests/test_sc_sov_trade_001_kat.py` and `tests/test_sc_sov_trade_001_properties.py`. The *now* column names the exact test for each.

## Weak spot
M12 (signed message-digest not checked) is caught only by the randomized bit-flip fuzz test (`test_timestamp_bit_flips`; 50 examples inside the mutation harness, 5000 in `make verify`). It was caught in this run, but there is no deterministic test that alters an unchecked TSTInfo field (for example the serial number) while keeping the signed attributes. Recommended follow-up.

## Equivalent mutation
M24 (`ceremony: k-subset disagreement not checked`): with more than k shares, every k-subset is reconstructed by a recursive `reconstruct_secret` call, which already rejects a subset whose secret does not hash to the published commitment. Two subsets can only disagree while both match the commitment with a SHA-256 collision. The check is kept as defence in depth; `test_tampered_extra_share_rejected` shows the behaviour. This is an argument, not a proof; a reviewer may disagree.
