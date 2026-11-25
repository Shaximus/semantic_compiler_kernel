# Changelog

All notable changes to `semantic_compiler_kernel`. Releases before this file was started are listed in `calibration_output/RELEASE_MANIFEST_V*.json` and the README.

## [Unreleased] — 2026-11-25 (branch `feat/router-feeds-compile`)

### Changed
- `compile_semantic_packet` discovers targets router-first:
  - **Fast path.** A strong 8-frame table frame, or two distinct table frames, keeps the table targets.
  - **Otherwise the router decides:**
    - `ROUTED` puts the routed domain first and adds a `ROUTED_DOMAIN:` warning.
    - `AMBIGUOUS` returns `Decision.AMBIGUOUS` with `status="ambiguous"`, `route_to=["HOST_CLARIFY"]`, `routing_candidates` and a clarifying question.
    - `ABSTAIN` drops a lone weak ("?") frame, so the input passes through. An explicit `mode` keeps it.
  - `routing_candidates` is filled for every compiled input.
  - `STRUCTURAL_FIT_MIN` stays at 0.55.
- Corpus (963 inputs), before → after:

  | Decision | Before | After |
  |---|---|---|
  | COMPILED | 316 | 343 |
  | NEEDS_REVISION | 232 | 325 |
  | PASS_THROUGH | 264 | 137 |
  | AMBIGUOUS | 0 | 7 |
  | REJECT | 148 | 148 |

  - 105 of the 107 new NEEDS_REVISION results on the labeled calibration set have the correct domain, with low fit.
  - All 51 out-of-domain prompts still pass through.
- Kernel Mobile pinned prompts: 04 (Android security) is now COMPILED as `mobile_security`. 05 (clinic redesign) is now NEEDS_REVISION as `medical`, with fit 0.0.

### Added
- `tests/test_routing_acceptance.py`: the spec acceptance list.

## [Unreleased] — 2026-11-25 (branch `fix/router-discriminative-abstain`)

### Added
- `expansion/router.py`: a discriminative domain router (`route_domains()`, `DomainRouter`, `RoutingResult`). It returns `ROUTED`, `AMBIGUOUS` or `ABSTAIN` with ranked candidates, a routing confidence, and the top-1 vs top-2 margin.
  - Filler and stop words are suppressed. The relational words `not, without, before, after, only, never, no, unless, except` are never stripped: they stay in the phrase stream but don't count as standalone evidence.
  - Weighting is IDF-style: a token counts only if at most 25% of domains use it. Phrase matches get a boost, and the subject clause outweighs the source clause of an analogy.
  - A domain needs a phrase match, two distinct evidence units, or one very specific term to qualify. If the top two are within a 0.15 margin, the result is `AMBIGUOUS`. If confidence is below 0.35, the router abstains.
  - Curated keyword anchors and the PoE-specific Buildcraft triggers (for `ci_build_invariants`) boost a domain that already has evidence. A literal compiled-entry ID (`SC-…-NNN`) routes to its home domain.
- `BayDelivery.routing` carries the router verdict.
- Fixtures under `tests/fixtures/routing_eval/`, plus `tests/test_domain_router.py`.

### Fixed
- `summon()` no longer picks a domain on filler. When the router abstains, `matched_domains` is empty and `primary_domain` is `universal_generic`. Dogfood examples: "phone battery" previously went to `poe_chaos_inoculation` and "landlord email" to `speculative_decoding`. The README example still routes to `ci_build_invariants`, its intended Buildcraft-derived domain, but now on the phrase "support gems" rather than "support" + "vram".
- Measured results: 31/31 out-of-domain fixture prompts abstain (previously 1/31). On the 225-sample labeled calibration corpus, summon's primary is correct for 212 (previously 213; 4 now abstain). Router precision is 0.977 and recall 0.942. Decompress routing changed for none of the 1,181 corpus inputs.
- `soul_bomb_sovereignty` decompress keywords gain "spirit bomb", "genki dama", "kid buu" and "collective input" (SC-SB-001 patch vocabulary).

## [Unreleased] — 2026-11-25 (branch `feat/pass-through-decision`)

### Added
- `Decision.PASS_THROUGH`: input with no resolved target system and no semantic error is no longer `NEEDS_REVISION`.
  - It gets `status="pass_through"`, `route_to=["HOST_AI"]`, no `semantic_error_class`, no `compiler_errors`, and the `PASS_THROUGH_REASON` warning.
  - `SemanticPacket.forward_text` holds the caller's original input byte-for-byte (before lone-surrogate sanitization) so a mobile host can forward it unchanged.
  - The dataset `sample_kind` is `UNRESOLVED`.
- `Decision.AMBIGUOUS`: reserved for close top-2 domain routing. It is emitted once the router feed lands.
- Both members are appended to the enum, so existing integer values are unchanged. The three `logos_semantic_training_sample` schemas accept both in `routing.status`.
- README section "Decisions for host apps."

### Changed
- **Behavior change:** the Kernel Mobile bench prompts 01, 04 and 05 and "Purple sleeps horizontally under Tuesday." now return `PASS_THROUGH` instead of `NEEDS_REVISION`; their tests are updated. Empty input stays `REJECT`, and low-fit input with a target stays `NEEDS_REVISION`.

## [Unreleased] — 2026-11-25 (branch `fix/skeleton-clause-boundaries`)

### Fixed
- The structural skeleton extractor (`extraction/skeleton.py`) tokenized the whole input as one stream, so actor and object noun phrases ran across `;`, `:`, `.`, `!`, `?`, brackets, newlines and dashes. Examples were "organism cash flow" (from "a living organism; cash flow is blood"), "paperwork the gpu", "brain a network", "rule memory" and "compile the brain". Phrases are now extracted per clause.
  - Corpus impact over 963 inputs (calibration corpora, the missing-organ benchmark, SFT pilot, Kernel Mobile prompts and dogfood): 28 skeletons changed, every one by dropping a cross-clause phrase.
  - One decision changed: numerology sample `834215d9`, COMPILED → NEEDS_REVISION. Its structural_fit went from 0.65 to 0.45 because its only "objects" had been the cross-colon artifacts "earth material" and "water emotion".
  - Clause-initial capitalized words that used to sit inside those bogus phrases (for example "Note", "STEP") can now surface through the existing proper-noun actor fallback.

## [Unreleased] — 2026-11-25 (branch `fix/input-validation-empty-and-mode`)

### Changed
- **Behavior change:** empty or whitespace-only input now returns `Decision.REJECT` with `semantic_error_class == "EMPTY_INPUT"` (exported as `core.pipeline.EMPTY_INPUT_ERROR_CLASS`) and an `EMPTY_INPUT` compiler error. Previously it returned the generic `NEEDS_REVISION` "No target system resolved" result. The packet is still finalized (dataset row and audit are built).
- **Behavior change:** an unknown `mode` now raises `ValueError` listing every valid `CompilerMode`. Previously it fell back silently to auto-detection. Mode names are case-insensitive, a `CompilerMode` value is accepted, and omitting `mode` still means `AUTO`. New helper: `core.pipeline.normalize_requested_mode`.

### Fixed
- `mode="auto"` (lowercase) used to resolve to `CompilerMode.AUTO` and skip auto-detection. It now behaves like the default.

### Tests
- `tests/test_input_validation_empty_and_mode.py` also pins that `SemanticPacket.to_dict()` serializes `decision` and `mode` as enum names (for example `"NEEDS_REVISION"`). `to_dict()` already did this. The integer values seen while dogfooding came from the dogfood script calling `.value`; no public API emits enum ints, so nothing changed there.

## [Unreleased] — 2026-11-25 (branch `fix/compile-input-robustness`)

### Fixed
- `compile_semantic_packet` no longer crashes on input containing a lone UTF-16 surrogate (for example a half emoji from a mobile text bridge). Lone surrogates are replaced with U+FFFD before compilation, so provenance hashing and dataset export stay valid UTF-8. `SemanticPacket.compute_input_hash` also encodes with `surrogatepass`.
- `compile_semantic_packet` raises a clear `TypeError` for non-`str` input (for example `None`) instead of an `AttributeError` deep in normalization.

## [Unreleased] — 2026-11-25 (branch `docs/sc-sb-fr-md-2026-11-25c`)

### Added
- `docs/SC-SB-001_THREE_CLAIM_STRUCTURE.md`: DRAFT 0.1 patch to SC-SB-001. Splits the Spirit Bomb target interaction into three claims (moral neutrality, structural interaction, magnitude confound) and names the child invariant COLLECTIVE INPUT / STRUCTURAL RESPONSE. Does not replace the compiled V5 JSONL.
- `docs/SC-FR-001_THE_OUTSIDERS_FIRST_INVESTMENT.md`: DRAFT 0.1, The Outsider's First Investment (The Frieza Protocol). All five layers kept together; canon (DBS manga ch. 87 time chamber; Black Frieza) labelled separately from hypotheses; three ownership architectures and open investigations included.
- `docs/SC-MD-001_SOVEREIGN_MIRROR_DUALITY.md`: DRAFT 0.1, Sovereign Mirror Duality (alias SC-MIRROR-001, "Mirrored Loop and Fusion Protocol"). CPT-symmetric universe anchor, five invariants, BCC backup layer, and FLRW / SC-HS-001 link as the next research step. Not compiled.

### Changed
- Invariant catalog and DOMAIN_LEDGER rows for the three drafts. `validate_catalog.py` lists `SC-FR-001`, `SC-MD-001`, and `SC-MIRROR-001` as markdown-only upstream IDs.

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
