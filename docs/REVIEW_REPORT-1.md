# Semantic Compiler Kernel V3.0.0 — review report (continued)

**Authoritative full text:** project folder `REVIEW_REPORT-1.md` (28 250 bytes).

## Deep-system domains (patch 06)

Three templates added with sourced invariants; `docs/DEEP_SYSTEM_INVARIANTS.md` lists sources, a cross-source table, and what was not established:

- `mobile_security.yaml` — Verified Boot, sandbox, SELinux, FBE DE/CE, KeyMint levels, attestation, optional pKVM/MTE, patch channels
- `networking.yaml` — end-to-end principle, RPKI/ROA, DNSSEC validation outcomes
- `trust_chain.yaml` — chain-of-trust modeling

Precision pass applied to `mobile_security` (see `docs/ANDROID_SECURITY_DOMAIN_REVIEW.md`): Knox-specific claims removed from generic AOSP model; KeyMint security level required; DE vs CE split; Gatekeeper timeout (not universal exponential backoff); optional mitigations marked optional.

## Packaging

Wheel previously omitted `expansion.gem_decode` / `expansion.gem_forge` and looked for `templates/**/*.json` while templates are `*.yaml`. Fixed package data globs; post-fix wheel contains all templates and runs medical decompress.

## Advisor remediation

Advisor remediation coverage expanded from 3 of 16 ontology concepts to full set (including cancer, autoimmune, sepsis, metastasis, physiotherapy) with domain-specific wording.

## Kestrel integration (patch 07)

Kestrel `lab-3cycle` branch integrated via `compat.py`:
1. Decision-dependent outputs built before the decision — still real on calibration corpora; wrapper aligns executive translation.
2. Sensitive text in SFT labelled redacted — SHA-256 marker applied.
3. Package version — already 3.0.0 upstream; test re-pointed.

## Companion method and new domains (same session)

- `docs/ARK_ANDROID_DIAGNOSIS_METHOD_20261106.md` + `expansion/templates/android_connectivity.yaml`
- `expansion/templates/bluetooth.yaml`
