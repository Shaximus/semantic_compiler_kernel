# SC-SOV-TRADE-001 verification evidence (Shax t616u / t617u), 27 Nov 2026

**Tested commit:** `21ce5030ddfc3f3bf91760ebab14ea5bd5ddda8a` (PR #107, branch `feat/sc-sov-trade-001-crypto-gaps`). This evidence directory was added in a later docs-only commit; it changes no code.
**Where it ran:** the Grok Bot Linux box (Debian 13 trixie), from a fresh `git clone` and a fresh venv built from the hash-locked requirements. **It did not run on Shax's PC**: the registered machine was a phone and the PC was not reachable. **Command:** `make verify` (`scripts/sov_trade/verify.sh`), with `SOV_TRADE_CORPUS_HARNESS` pointing at the box-only 963-prompt corpus harness.
**Grade:** unchanged, SILVER 0.793, `gold_awarded` false. **R-16:** `NOT_MET`. Version 4.1.0. Nothing merged, tagged or released.
**t617u:** national-root grants require three distinct officers (APPROVE, SIGN, DEPLOY), a signer holding Role.SIGN, and a 3-of-5 ceremony quorum. `generate_root` and root revoke use the same three-officer rule (provisional, flagged for Shax). Non-grant root signatures still use the in-memory key (remaining gap). Mutations M53–M56 were added; M12 now has a deterministic TSTInfo-binding test.
**Keys:** every key, certificate, token and PIN used here is a TEST item generated per run (SoftHSM2 test token, test CAs, test TSA). None is committed; PINs are random per run and never written to logs.

## Environment (step 1)
```
date_local: 2026-11-27 23:18:21 AST
host_kind: unspecified
uname: Linux grok-bot-vm-420080851 6.12.113+ #1 SMP PREEMPT_DYNAMIC Tue Nov 24 16:59:13 UTC 2026 x86_64 GNU/Linux
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
VERSION_ID="13"
repo: /workspace/cos-wt/fresh-t617u-2/semantic_compiler
git_head: 21ce5030ddfc3f3bf91760ebab14ea5bd5ddda8a
git_dirty_files: 0
python: Python 3.13.5 (main, Aug 10 2026, 12:06:59) [GCC 14.2.0] 
openssl_cli: OpenSSL 3.5.9 29 Sep 2026 (Library: OpenSSL 3.5.9 29 Sep 2026)
cryptography: 50.0.2 | linked: OpenSSL 4.0.3 29 Sep 2026
softhsm2: 2.6.1
pkcs11_module: /usr/lib/softhsm/libsofthsm2.so
pkcs11_tool: pkcs11-tool: unrecognized option '--version'
opensc	0.26.1-2
dpkg: opensc	0.26.1-2
dpkg: openssl	3.5.9-1~deb13u1
dpkg: softhsm2	2.6.1-3
SOV_TRADE_REQUIRE_FUNCTIONAL: 1
SOV_TRADE_FUZZ_EXAMPLES: 5000
```
Full `pip freeze`: `logs/environment.txt`.

## Results by step
| step | exit code | time |
|---|---|---|
| venv | 0 | 10s |
| softhsm_init | 0 | 0s |
| pytest_full | 0 | 99s |
| pytest_sov_trade | 0 | 85s |
| sov_trade_zero_skips | 0 | 0s |
| unittest | 0 | 7s |
| validate_catalog | 0 | 0s |
| fuzz | 0 | 75s |
| hsm_evidence | 0 | 1s |
| cross_check | 0 | 0s |
| mutation | 0 | 777s |
| ruff_errors | 0 | 0s |
| ruff_full | INFO(rc=1) | - |
| mypy | 0 | 1s |
| bandit | 0 | 1s |
| bandit_scripts | INFO(rc=1) | - |
| pip_audit_ci | 0 | 1s |
| pip_audit_static | 0 | 1s |
| static_audit | 0 | 1s |
| dogfood_base | 0 | 2s |
| dogfood_head | 0 | 0s |
| dogfood_diff | 0 | 0s |
| corpus_base | 0 | 7s |
| corpus_head | 0 | 6s |
| corpus_diff | 0 | 0s |

Exit code 0 = pass. `INFO(rc=…)` = report only, not a gate. `ruff_errors` (E9,F) is a gate; after t617u it is clean (the unused `needed` F841 is gone).

## Test counts (step 2)
- Full suite, `pytest tests -rsx -v` with `SOV_TRADE_REQUIRE_FUNCTIONAL=1`: **1580 passed, 6 xfailed, 1385 subtests passed in 97.65s (0:01:37)**
- sov_trade only (`-k sov_trade -rsx -v`): **417 passed, 1169 deselected in 84.28s (0:01:24)**
- **sov_trade skips: 0.** Other skips in the full suite: 0.
- `unittest discover -v`: Ran 831 tests in 6.246s; OK (expected failures=6)
- `validate_catalog.py`: exit 0; 278 [PASS] checks, 0 [FAIL]

### The 6 xfails (all outside sov_trade, all strict expected failures)
1. `tests/test_domain_router.py::AcceptanceTests::test_frieza_paraphrase_without_names`: known router limit: with no Dragon Ball names, "energy" + "chaos" route to poe_chaos_inoculation.
2. `tests/test_scc_001_ac_anti_capture.py::TestACOracleA::test_live_mafuba_001a_projection_exists_and_is_hash_pinned`: TEST-AC-ORACLE-A: tests/reference/sc_mafuba_001 has no 001A projection P, so hash-pinned immutability cannot be checked against live code.
3. `tests/test_scc_001_ac_anti_capture.py::TestACOracleB::test_live_disturbance_manifest_is_principal_signed`: TEST-AC-ORACLE-B: the disturbance manifest carries no principal signature (mutable manifest).
4. `tests/test_scc_001_ac_anti_capture.py::TestACOracleC::test_live_sink_manifest_is_principal_signed`: TEST-AC-ORACLE-C: the sink manifest is hash-pinned but not signed by V_P.
5. `tests/test_scc_001_ac_anti_capture.py::TestACOracleD::test_live_mafuba_budget_has_audit_and_quarantine_partitions`: TEST-AC-ORACLE-D: ResourceBudget has r_override but no separate R_audit / R_quarantine partitions.
6. `tests/test_scc_001_ac_anti_capture.py::TestACOracleD::test_live_resource_manifest_declares_r_override`: TEST-AC-ORACLE-D: resource.yaml declares no R_override partition.

xfails seen in this run: 6 (match the list).

## Mutation check (step 3)
See `MUTATION_TABLE.md` (also `mutation.json`, `mutation_baseline_original_tests.json`). 55/56 killed; equivalent survivors: ['M24']; survived/invalid: []

## Known-answer tests (step 4), official sources only
- **RFC 8032** section 7.1 Ed25519 test vectors 1, 2, 3, 1024-byte, SHA(abc): exact public key and signature bytes (rfc-editor.org).
- **NIST ACVP ML-DSA-65** (FIPS 204), usnistgov/ACVP-Server @ `975de31eb83d87039ec88934fdc47d8c312b892d`: 25 keyGen cases (seed -> exact pk/sk), 15 sigVer cases (3 pass, 12 expected failures, each matched; the project verifier only accepts the vector's context when it equals `SC-SOV-TRADE-001/v1`, which is checked separately).
- **RFC 8785** JCS, cyberphone/json-canonicalization @ `32a48195b9b20fe67b1795e39e4509f14d860b45`: arrays, french, unicode, weird must match byte-for-byte; structures and values contain floats and must be refused (provisional default).
- **RFC 9162** Merkle trees, transparency-dev/merkle @ `ff0af9a8d5457640371453f71e7acefd5cfda811`: reference roots for sizes 0-8, 98 inclusion and 98 consistency probes. Two upstream "additional" equal-size probes use non-32-byte placeholder hashes and diverge on purpose (strict 32-byte rule).
- Fixtures: `tests/fixtures/sov_trade_kat/`, built by `scripts/sov_trade/build_kat_fixtures.py`.

## Independent cross-checks (step 5), OpenSSL CLI, not project code
Commands and outputs: `cross_check/cross_check.log` and `cross_check/cross_check.json`.
- PASS  ed25519: openssl verifies project signature
- PASS  ed25519: openssl rejects tampered message
- PASS  hybrid: openssl verifies Ed25519 half
- PASS  hybrid: openssl 3.5+ verifies ML-DSA-65 half (context-string)
- PASS  hybrid: openssl rejects ML-DSA-65 half under a different context
- PASS  hybrid: openssl rejects ML-DSA-65 half on tampered message
- PASS  rfc3161: openssl ts -verify (queryfile) on project token
- PASS  rfc3161: openssl ts -verify (data) on project token
- PASS  rfc3161: openssl ts -verify rejects tampered data
- PASS  rfc3161: openssl ts -reply issues a token for a project request
- PASS  rfc3161: project client verifies OpenSSL-issued token
- PASS  rfc3161: project client rejects OpenSSL token for other data
- PASS  mtls: s_client with valid TEST client cert is accepted (TLS 1.3)
- PASS  mtls: s_client with EXPIRED client cert is rejected
- PASS  mtls: s_client without a client cert is rejected
- PASS  mtls: s_client forcing TLS 1.2 is rejected
- 16/16 cross-checks passed

## HSM evidence (step 6), SoftHSM2 TEST token
From `logs/hsm_evidence.log` (also produced in every CI functional job):
- python-pkcs11 attributes: `{"CKA_ALWAYS_SENSITIVE": true, "CKA_EXTRACTABLE": false, "CKA_NEVER_EXTRACTABLE": true, "CKA_PRIVATE": true, "CKA_SENSITIVE": true, "CKA_TOKEN": true}`
- pkcs11-tool: `Access:     sensitive, always sensitive, never extractable, local`
- CKA_VALUE read: refused: AttributeSensitive (CKR_ATTRIBUTE_SENSITIVE)
- Export attempt (C_WrapKey via pkcs11-tool): rc=1, `error: PKCS11 function C_WrapKey failed: rv = CKR_KEY_UNEXTRACTABLE (0x6a)
Aborting.`, bytes written: False
- `pkcs11-tool --read-object` on the private key: refused by the tool itself (sorry, reading private keys not (yet) supported); recorded, but it is not token evidence.
- Signing path: `PKCS11Signer.sign` calls the token's sign on a key handle (`sign_path_calls_token_sign`=True), and an AST check finds no private-value attribute use in the signer (`sign_path_forbidden_attributes`=[]); the token signature verifies with `cryptography` (True). `sign()` also refuses extractable or non-sensitive keys and ambiguous labels (tests).
- Result: **PASS**. SoftHSM2 is a software token, not a certified HSM.

## Property and fuzz tests (step 7)
- hypothesis properties (`tests/test_sc_sov_trade_001_properties.py`): canonicalization round-trip, idempotence, key-order independence, UTF-16 order, floats and unsafe integers refused; delegation subset never widens, transitivity, reflexivity, `_scope_check` ok only if every link covers; log consistency verifies, tampered proofs fail, rewritten history is inconsistent, inclusion binds leaf and index.
- Fuzz pass (`tests/test_sc_sov_trade_001_fuzz.py`, 5000 examples per target): 10 passed in 73.90s (0:01:13). Targets: hybrid signature decoder, hybrid verify mutations, canonicalizer, RFC 3161 parser (random bytes and bit flips), inclusion-proof dict, inclusion/consistency arguments, delegation chains.
- An exhaustive single-bit sweep of one token (12,272 flips) leaves exactly one accepted flip: PKIStatus granted -> grantedWithMods, which is unsigned and accepted by design.

## Static checks (step 8)
- mypy (`-p semantic_compiler.sov_trade`): Success: no issues found in 20 source files
- bandit `sov_trade/`: No issues identified. (Low 0, Medium 0, High 0); scripts (report only): Low B404/B603/B101 subprocess/assert findings and B405/B314 for parsing the harness's own JUnit XML.
- pip-audit (CI lock): No known vulnerabilities found; (static lock): No known vulnerabilities found
- ruff E9,F: All checks passed! The t616u F841 (`needed` unused in `authority.issue`) is gone: t617u uses the required set {APPROVE, SIGN, DEPLOY} and the dead variable was removed. The broader ruff report (`logs/ruff_full.log`) is style (UP, B905, BLE001 on intentional fail-closed catches, E501) and is not a gate.
- `scripts/sov_trade/static_audit.py`: "result": "PASS". Checks: no `random` module anywhere in sov_trade; signature, MAC, commitment and challenge comparisons use `hmac.compare_digest` or the library verify call (listed in the log); secret scan of every tracked and untracked file for private keys, tokens and PINs.

## Reproducibility (step 9)
`make verify` rebuilds the venv from the locks, initialises a SoftHSM2 test token and reruns everything above. `scripts/sov_trade/Dockerfile` (Debian trixie) wraps the same script; **the Dockerfile was not built here** (no Docker on the box).

## Regression gates
- Full pytest and unittest: above. `validate_catalog`: above.
- Dogfood (27 prompts, `scripts/sov_trade/regression/dogfood_27.py`), merge-base `02d577c485dba6ec9e8162d76b3d8f9336c511fc` vs tested head: 27 items, 0 diffs
- 963-prompt corpus (box-only harness, not in the repo): 963 items, 0 diffs

## CI (step A)
| job | result | link |
|---|---|---|
| functional (python 3.10) | success | https://github.com/Shaximus/semantic_compiler_kernel/actions/runs/46102154929/job/140846784683 |
| functional (python 3.11) | success | https://github.com/Shaximus/semantic_compiler_kernel/actions/runs/46102154929/job/140846784550 |
| functional (python 3.12) | success | https://github.com/Shaximus/semantic_compiler_kernel/actions/runs/46102154929/job/140846784584 |
| functional (python 3.13) | success | https://github.com/Shaximus/semantic_compiler_kernel/actions/runs/46102154929/job/140846784619 |
| functional (python 3.14) | success | https://github.com/Shaximus/semantic_compiler_kernel/actions/runs/46102154929/job/140846784749 |
| refuses import without cryptography | success | https://github.com/Shaximus/semantic_compiler_kernel/actions/runs/46102154929/job/140846784400 |
| test | success | https://github.com/Shaximus/semantic_compiler_kernel/actions/runs/46102154929/job/140847284495 |

CI runs SoftHSM2/OpenSC/pinned cryptography on Python 3.10-3.14 with `SOV_TRADE_REQUIRE_FUNCTIONAL=1`, asserts zero sov_trade skips, prints the HSM evidence, and a separate job proves the package refuses to import without `cryptography`. Python 3.10 has 5 non-sov skips (`tests/test_packaging_config.py`, tomllib needs 3.11+). CI does not run the OpenSSL cross-checks (ubuntu-latest's OpenSSL lacks ML-DSA) or the mutation check; `make verify` does.

## What ran, what skipped, what was NOT tested
- **Ran:** everything in the steps table, on the box.
- **Skipped:** no sov_trade test. Full suite skips: 0.
- **Not tested / not done:** the run on Shax's PC; a certified hardware HSM (SoftHSM2 only); a real national TSA, PKI or root ceremony; hybrid post-quantum TLS (mTLS is classical TLS 1.3); peer checkpoint signatures in `store_peer_checkpoint` (not verified by the code); constant-time behaviour of the Shamir GF(256) arithmetic and in-memory secret reconstruction (rehearsal only); the Dockerfile build; legal review; outside review (R-16 stays NOT_MET); FIPS/CMVP validation.

## Hashes
`SHA256SUMS` lists sha256 for every file in this directory.
