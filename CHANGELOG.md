# Changelog

All notable changes to `semantic_compiler_kernel`. Releases before this file was started are listed in `calibration_output/RELEASE_MANIFEST_V*.json` and the README.

## [Unreleased] — 2026-11-25 (branch `feat/integrate-2026-11-25-material`)

### Changed
- **SC-PATCH-DU-001, identity gate correction (authorized by Shax):** the `identity_claim_allowed: false` gate is replaced by `substrate_confusion_check: true` plus `positional_claims_permitted: true` on every cross-substrate mapping.
  - New `gates/substrate_confusion.py`: material claims are BLOCKED, positional claims are PERMITTED, and positional claims asserting exclusive or permanent authority are FLAGGED for review.
  - Applied to all compiled entries and catalog entries that carried the old field (manifest SHA-256 values refreshed), and to the runtime emitters in `expansion/consciousness/*`, `expansion/elevator.py` and `registry/buildcraft.py`.
  - Also updated: the invariant-translator skill, the `domain_expansion.yaml` template and `validate_catalog.py`.
  - **Behavior change:** `evaluate_invariant_prediction` no longer returns `identity_claim_allowed`. Real-to-real `ISOMORPHIC_INVARIANT` mappings previously returned `true`; every mapping now carries the two new fields, plus `fiction_to_real`.
  - `TurntableTranslation` fields are renamed to match.
  - **Score impact** (measured against `7e63996`; see the full-catalog score diff):
    - Compile path (`compile_semantic_packet` + `build_dataset_row`): no change across 956 inputs and 970 mappings in all 46 domains. Packet scores, `overclaim_control`, `final_isomorphism_quality` and decisions are identical.
    - Evaluator path (`evaluate_invariant_prediction` scored by `core/dataset._mapping_scores`): real-to-real `ISOMORPHIC_INVARIANT` `overclaim_control` goes from 0.5 to 1.0 in all 46 domains. Fiction-to-real, gate scores and `final_isomorphism_quality` are unchanged.
    - The new `gates/substrate_confusion.py` classifier is informational: nothing in scoring or decisions calls it yet.
  - Frozen dataset corpora and schemas, which use `identity_claim_allowed` as a dataset-row field, are untouched.

### Added
- `calibration_output/compiled_entries/SC-DU-001_THE_DUALITY.jsonl`: The Duality, GOLD 0.925, post-SC-PATCH-DU-001 revision. The pre-patch original is in `calibration_output/archive/`. The manifest now has 18 entries.
- `docs/SC-PATCH-DU-001_IDENTITY_GATE_CORRECTION.md`: the patch text plus an implementation record.
- `docs/SC-THEO-002_OMNI_STATE.md`: V3.8.0 entry patch (markdown, not yet compiled to JSONL).
- `docs/SC-BRM-001_BIOMEDICAL_MICROPLASTIC_DOSSIER.md`: text extraction of the 22-page feasibility dossier. Source PDF and hash are in `docs/evidence/sc-brm-001/`.
- `docs/MEDICAL_NANOPLASTIC_FILTRATION_MAGNETIC_TARGETING_DRAFT_0.1.md`: Medical Advancement Domain DRAFT 0.1 (molded plastic chassis, nanoparticle functional layer, UV activation, magnetic targeting), unedited, with an integration note cross-referencing SC-BRM-001. No entry ID; not compiled.
- `docs/MOBILE_ADDON_ROADMAP.md`: architecture assessment for shipping the kernel as a bolt-in add-on for AI mobile apps.
- `tests/test_substrate_confusion_gate.py`.
- Invariant catalog "Gate Corrections" note and DOMAIN_LEDGER rows for SC-DU-001, SC-THEO-002, SC-BRM-001 and SC-PATCH-DU-001.

### Security
- `docs/CURTIS_THEOLOGICAL_MAP_UNIFIED_V7.md` line 589: a credential-like value in the "Four messiahs password" row is redacted to `[REDACTED]`. The value is still in git history on `main` (commit `7e63996`); removing it from history requires a history rewrite and the owner's approval.
