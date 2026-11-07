# Semantic Compiler Kernel V3.0.0 — review, repair and upgrade

Date: 2026-11-06. Reviewed: `github.com/Shaximus/semantic_compiler_kernel` (HEAD as cloned this session), in a local clone only.
**Nothing was committed or pushed.** The original is intact in git; every change is in the working tree and in the patch files delivered with this report.

## Result in numbers

| | Before (pristine HEAD) | After |
|---|---|---|
| `pytest tests` | 223 passed (README claimed 211) | 366 passed + 4 expected failures (305 after patches 01-05, +31 patch 06, +14 passing and +4 expected-failure markers in patch 07, +16 patch 08, +12 patch 09) |
| `unittest discover` | 82 tests | 151 tests (4 expected failures) |
| Missing-organ benchmark, absent-confirmed recall | 0.805 (66 TP / 16 FN) | 1.000 (82 TP / 0 FN) |
| Missing-organ benchmark, absent-confirmed precision | 0.985 (1 FP) | 0.921 (7 FP) — see B.2 |
| Calibration corpus (76 rows): decisions / dataset tiers / `training_ready` | 17 / 47 / 12 · 45 / 25 / 6 · 15 true | identical |
| Departments marked PRESENT per corpus row (avg) | 3.5 | 0.4 |
| Installed wheel: `import semantic_compiler.expansion` | `ModuleNotFoundError` | works, medical decompress runs |

The patch set applies cleanly to pristine HEAD (`git apply --check`) and reproduces 378 passing plus 4 expected failures (the rows above were measured at 305, through patch 05). Patches 01–04 alone give 279 passing; 01–04 plus 06 to 09 (no waiver needed) give 352, plus the 4 expected failures. Applying 01 to 09 in order, or `00-ALL-IN-ONE.patch` alone, to pristine HEAD gives a tree byte-identical to the working tree.

## Patch files (apply in this order; 05 needs your waiver; 06, 08 and 09 are the domain expansions, F, H and I; 07 is the Kestrel integration, G)

| File | Touches | Notes |
|---|---|---|
| `01-buildcraft-resolver.patch` | `translation/structural_resolver.py`, `translation/buildcraft.py`, 2 test files | |
| `02-isomorphism-organ-detector.patch` | `translation/fractal.py`, new `tests/test_department_presence.py` | |
| `03-medical-ontology-and-decompression.patch` | `expansion/{__init__,advisor,ontology,pathology}`, new test | |
| `04-packaging-and-readme.patch` | `pyproject.toml`, `README.md`, new packaging test | README test count updated to 305 / 133 |
| `05-frozen-dirs-need-waiver.patch` | `core/pipeline.py` (one line), `registry/cosmological_constants.py`, 2 new test files | README says `core/` and `registry/` are frozen. Your call. |
| `06-deep-system-domains.patch` | 3 new templates in `expansion/templates/`, `expansion/__init__.py` routing and optional component `medical_map`, schema, `docs/DEEP_SYSTEM_INVARIANTS.md`, calibration builder, 3 test files, README | Builds on 01–04; independent of 05. README counts 336 / 133 |
| `07-kestrel-integration.patch` | `compat.py`, `__init__.py` (one import), `tests/test_kestrel_lab_regressions.py`, `.github/workflows/ci.yml`, `docs/kestrel/`, README | Builds on 01–04 and 06; independent of 05 (section G) |
| `08-poe-chaos-inoculation.patch` | new template `expansion/templates/poe_chaos_inoculation.yaml`, `docs/POE_CHAOS_INOCULATION_INVARIANTS.md`, one routing group in `expansion/__init__.py`, calibration builder (+5 samples), 3 test files, README | Builds on 06; independent of 05 (section H). README counts 366 / 151 |
| `09-poe-ci-spec-and-reference-model.patch` | `poe_chaos_inoculation.yaml` (one failure mode, one pattern, refill wording), the PoE doc (spec and derived properties), new `tests/expansion/test_poe_ci_reference_model.py`, 1 test file, README | Builds on 08; independent of 05 (section I). README count 378 |
| `00-ALL-IN-ONE.patch` | 01–09 | |

## A. Buildcraft ontology (patch 01)

Each defect was reproduced on the shipped code first; each fix has a regression test (`BuildcraftResolverRegressionTests`, plus five tests in `test_structural_resolver.py`).

1. **Slot/item collision.** The alias index let a short alias overwrite the longer one containing it. "The CPU socket is the body armour slot" resolved BUILD_005 (CPU *is* armour) and "accelerator slot is the weapon slot" resolved BUILD_004 (GPU *is* weapon). Now longest-phrase-wins (maximal munch); ties over the same span keep both concepts. Both sentences resolve only the slot mappings, including through the fallback layer.
2. **BUILD_001 was keyed on the same concept as BUILD_012**, so "This is a complete build" also resolved the paper-doll topology mapping. It now has its own `topology` concept.
3. **Substring triggers in the recall layer.** "abi" fired on capability/probability, "repo" on report, "gem" on management. Triggers are now whole-word with plural/inflection tolerance (so "GPUs", "repos", "drivers" still match).
4. **Negation was ignored.** "A GPU is not a weapon" resolved BUILD_004. Negated relations are now emitted as `not_<relation>`, never count as support, and a fallback-only match carries the reason `relation_negated_in_source`.
5. **Relation kinds were loose.** "The LLM uses an active skill" counted as equivalence evidence. Relation kinds must now match exactly.
6. **Clause boundaries.** Sentence-final tokens kept their "." so "reservation." never matched, and `;` produced relations between unrelated clauses. Relations are now extracted per clause.
7. **BUILD_010 could not resolve structurally.** Relation coverage was averaged across alternative patterns, so one match never reached the threshold. "Any pattern" now suffices.

## B. Society / biology / AI / cosmology comparisons (patch 02)

**B.1 The presence detector leaked.** `_map_present_to_departments` substring-matched every word of the raw text against every table string. "It is in the of to and from with at on by." marked **all 15** departments PRESENT, and "A cell has a nucleus." marked six. On the shipped labeled benchmark this cost 16 of 82 absences. Rewritten: whole-token matching, function words and the system's own name ("cell" in a cell sentence) never count, negation windows ("no security team", "without a firewall") are honored, table phrases at the active scale count for every department that lists them, and a one-word match that several departments list resolves to the first-listed department (documented, tested).

**B.2 Benchmark, honestly.** 43 of the 49 rows now score precision 1.0 / recall 1.0. All 7 false absences are in the 6 `implied_organ_*` rows, which the old detector "passed" only because of the leak:
- 5 are rows where the label is `UNOBSERVED` for an organ the text never names (e.g. "A complete human body includes a brain, eyes, ..." → REPRODUCTION, DELETION). These labels appear to encode a rule the detector does not implement: *a "complete X" claim makes omitted organs UNOBSERVED rather than ABSENT_CONFIRMED*. I did not invent that semantic.
- 2 are labeled PRESENT through a word the table lists under two departments: "attention" (PROCESSOR and TELECOMMUNICATIONS at LLM scale) and "membrane" (DISPLAY and SECURITY at cell scale).

The baseline's 0.985 precision was low-recall luck: it rarely said "absent", so it rarely said it wrongly.

**B.3 Pipeline impact.** Across the 76 calibration inputs no decision, tier or `training_ready` value changed. The corpus never produces `ABSENT_CONFIRMED`, so it does not exercise this path; `core/dataset.py` does demote any `ABSENT_CONFIRMED` row, which is the path that matters for whole-system inputs.

**B.4 `map_fractal_similarity` returns nothing for most real frames.** Its keyword table matches none of the names the frame detector emits ("computation", "organizational", "reflexion"), so 0 of 76 corpus rows get fractal mappings. I added `scale_for_frame()` and a shared `FRAME_TO_SCALE`, but left the default behavior unchanged: when I turned it on, the mappings carry lower-case scales ("human", "society") that the frozen dataset schema 2.1.0 enum rejects, and 5 existing tests failed (4 dataset-schema tests and one counter-mapping test). It is opt-in via `map_fractal_similarity(packet, resolve_frames=True)`. Enabling it by default needs a schema-aware translation step first.

**B.5 Table observations (not changed).**
- `SUBCONSCIOUS` at society scale is "Government (the hidden control layer)", which duplicates `PROCESSOR` ("Government executive branch").
- Two parallel scale tables exist: `registry/universal_departments.py` (12 `ScaleType` names) and `translation/fractal.py` (7 string scales). I did not reconcile them.
- `core.pipeline._infer_system_scale` keeps its own copy of the frame table. It is currently identical to `FRAME_TO_SCALE`; a test guards against drift so `core/` could stay untouched.

## C. Cosmology constants (patch 05, `registry/cosmological_constants.py`)

The module had **zero tests and zero callers** anywhere in the repo. I added `check_constant_consistency()`, which recomputes every number that can be recomputed from the others plus CODATA values. 11 of 16 checks pass; the foundational identities hold (r_s = c/H0, H0 = 70 km/s/Mpc, Λ_geom + Λ_info = Λ_obs, C_geom = 1 − e^(−3κ̃), I_max ≈ 3.02e122 bits).

**Five checks fail. I recorded them in `KNOWN_DISCREPANCIES` and did not change your numbers.** A failed check is not a claim that the paper is wrong; the paper may define a quantity differently from the registry's comments.

| ID | Registry says | Recomputed from the registry's own definitions |
|---|---|---|
| `amplification_exponent_product` | C·Ξ·I[r] = 0.91 × 70 × 1.143 → "exp(69)" | = 72.81. `exp(72.81)` takes T_H to **94.7 K**, not 2.725 K. The exponent that reproduces the CMB is ln(T_CMB/T_H) = 69.26, which needs I[r] = 1.087 or Ξ = 66.6. The stored 69 works; the three factors do not multiply to it. |
| `kappa_tilde_definition` | κ̃ = κ·R_H² = 0.5, κ = H0²/c², R_H = c/H0 | That product is identically 1 (0.999 with the rounded radius). Every C_geom number built on κ̃ = 0.5 depends on this. |
| `lambda_faces_match_observed` | Λ = 3H0²/c² = 3/L², stored Λ_obs = 1.105e-52 | 1.72e-52, which is 1.56× the stored value. The three Trinity faces agree with each other; none equals the stored total. 1.105e-52 matches the Planck-fit Λ and needs a ~0.64 density factor the equations as written lack. |
| `hawking_temperature` | T = 2.269e-30 K | ħH0/(2πk_B) = 2.76e-30 K. 2.269e-30 corresponds to √Ω_Λ·H0, not H0. |
| `kappa_physical` | κ = H0²/c² ≈ 0.050 Gpc⁻² | 0.0546 Gpc⁻² |

A test pins the contract: the failing checks must equal `KNOWN_DISCREPANCIES` exactly, so a new unexplained inconsistency fails CI and a resolved one flags its stale entry.

Code fixes in the same module, each tested:
- `verify_lambda_trinity` had `trinity_intact: True` hard-coded and its `converged` test is true by construction. It now evaluates the three equations and reports the open discrepancy.
- `compute_information_amplification` returned a 94.7 K "CMB prediction" next to a docstring saying 2.725 K. It now reports both exponents and `consistent_with_cmb`. Overflow returns `inf`, not the string `"overflow"`.
- `compute_bh_core_radius` used `ln x − ln ln x` for the Lambert W (off by 0.05 at 10^38) and returned the argument itself when ln x ≤ 1 (0.91 where W(0.91) ≈ 0.54). It now uses `lambert_w0` (Halley, checked against known values to 1e-12 and by round-trip to 1e300). Docstring "≈ 84" corrected to 82.99.
- `compute_psi_equilibrium_gauge` reported EQUILIBRIUM for Ψ = −5 or for opposite-sign components that cancel. Status now uses the sum of component magnitudes.
- `get_cosmological_isomorphism("")` and `("a")` silently returned the first entry (`information_saturation`). Concepts under 4 characters no longer substring-match.
- Input validation added (zero or negative mass, NaN, non-positive `i_available`).
- Added `CONSTANT_PROVENANCE` labeling each value OBSERVED / DERIVED / MODEL_PARAMETER / PREDICTION. The module docstring said "measured values with verified derivations", which holds for the OBSERVED rows only. I reworded that one sentence; revert it if you prefer your original framing.

I did **not** assess the physics, and I could not independently derive Ξ(C), I[r] or the redshift-drift prediction (ż = −1.23e-10 yr⁻¹).

## D. Medical ontology and decompression (patch 03)

**Verified good:** all 14 `medical_map` values used by the 19 domain templates are canonical ontology concepts.

**Fixed**
- **Domain inference used substring matching.** "rapid onset sepsis" contained "api" and routed to `computation`; "observer" contained "server"; "excellent" contained "cell" and routed to `biology`. Whole-word matching now; the original computation → biology precedence is kept (two existing tests pin the domain results). A `medical` branch was added, so `medical.yaml` is reachable at all. Before this, `decompress` could only ever pick 3 of the 19 templates, never `medical`.
- **Pathology false positives.** A benign model of five generic components (`the_team`, `of`, `system`, `data`, `service`) produced **25 false pathologies** across the 19 templates, each at confidence 0.75, because common words matched failure-mode descriptions. Function words and generic structural words are now ignored. Result on that model: 0. Every failure mode is still detectable from its own first indicator (tested for all 19 templates). Confidence now reflects evidence: 0.75 for an indicator or `medical_map` match (unchanged), 0.6 for word overlap alone, and the evidence list says which. One detection appears that did not before (`law` → `judicial_overreach`, from the word "legislature's" which was previously swallowed by a trailing apostrophe).
- **Advisor remediation covered 3 of 16 ontology concepts**, so cancer, autoimmune, sepsis and metastasis (all used by shipped templates) got the generic text "remove the matched indicators and re-test". All 17 concepts (the 16 plus `physiotherapy`, below) now have specific remediation. **The wording of the 14 new lines is mine; please review it, it is domain advice in your voice.** Existing entries are untouched.
- **Vocabulary mismatch.** `_infer_medical_map` emits `immune_boundary`, `homeostasis_regulation`, `processing_core`, `memory_store`, `output_layer` — five values that are not ontology concepts (and `unknown` for 87 of 97 template components; 85 after this patch). An existing test pins `immune_boundary`, so the emitted values are unchanged. The ontology now has `ONTOLOGY_ALIASES` (two legacy spellings → canonical), `FUNCTIONAL_ROLE_TAGS` (the three role tags, classified honestly as not medical), `resolve_concept()`/`classify_medical_map()`, and tolerant `get_concept()`. Components named after a concept now map to it ("diagnosis", "treatment" in the medical template).
- The advisor referenced `physiotherapy`, which was not in the ontology. Added it. Its "missing critical component" rule matched only exact names (`"defense"`), never the template's `defense_boundary`; it now matches by token, and its `medical_ontology_reference` is a real concept instead of a component name.

**Not fixed: the main limitation.** `decompress()` does not read the input. `_extract_components` copies every component from the domain template, `_extract_relationships` returns `[]`, so two different inputs in one domain produce identical models, and `reconstruct_missing()` compares the template to itself and can never report anything missing. Cross-domain "missing organ" reconstruction therefore does not happen in `decompress` today. A test pins this as a known limitation so a future fix is noticed. Fixing it is a design change (extract observed components from the skeleton, then diff against the template), not a touch-up, and it conflicts with two existing tests that expect template-derived `medical_map` values. Say the word if you want it.

## E. Core and packaging (patches 04 and 05)

- **`resolve_mode` AUTO never detected anything.** It read `c.get("type")` but claims are stored under `claim_type`, so all 76 corpus rows resolved to `UNIVERSAL_DECOMPRESSION`. One-line fix in `core/pipeline.py` (patch 05). 3 corpus rows change mode (1 → COSMOLOGICAL_MAPPING, 2 → PUBLIC_TRANSLATION); no decision, tier or `training_ready` changed. This is behavior in a directory the README calls frozen.
- **The wheel was broken.** `pyproject.toml` omitted the packages `expansion.gem_decode` and `expansion.gem_forge` (imported unconditionally by `expansion/__init__`), its data glob looked for `templates/**/*.json` while the templates are `*.yaml`, and `gem_forge/data/*.json` was not packaged. I built wheels from a scratch copy: the original wheel contains 0 of 19 templates and `import semantic_compiler.expansion` raises `ModuleNotFoundError`; the fixed wheel contains all 19 templates, installs, and runs a medical decompress. A test checks the config against the directory tree.

## F. Deep-system domains: mobile security, networking, chain of trust (2026-11-06, patch 06)

You asked for a domain section covering the invariant system in deep-system Android/Knox/"Eris"/networking work, plus any other patterns I identified. Three templates were added; all invariants are sourced, and `docs/DEEP_SYSTEM_INVARIANTS.md` lists the sources, a cross-source table and what was not established.

| Domain | Components | Invariants | Failure modes | Patterns | Sources |
|---|---|---|---|---|---|
| `mobile_security` | 10 | 16 | 7 | 7 | Android Verified Boot and security docs, Samsung Knox white paper, Kanonov and Wool (arXiv:1605.08567) |
| `networking` | 10 | 16 | 7 | 6 | UCSB CS176C four invariants, RFC 1958, RFC 6480 (RPKI), RFC 4033 (DNSSEC) |
| `trust_chain` | 9 | 12 | 7 | 6 | all of the above |

**The pattern I identified (`trust_chain`).** Android Verified Boot, Knox secure boot, DNSSEC and the RPKI were designed independently and share one structure: an anchor the verified system cannot rewrite; each link verified by the one before; freshness (rollback indexes and fuses, nonce-bound attestation, signature expiry); an enforced consequence for failure; narrow single-purpose authority (an RPKI end-entity key signs exactly one object); a monotonic compromise record (Knox warranty bit); untrusted channels made safe by signatures and manifests; make-before-break replacement; and an explicit statement of what the chain does not cover (DNSSEC gives no confidentiality or availability, the RPKI gives authorization not identity, Android notes a kernel bug yielding root can bypass its protections). Knox's failure policy is tiered: a failed signature step terminates boot, while a bootable but unapproved configuration is recorded permanently and the keys it gates stop working. The cross-source table is in the doc; `-` means "not stated in what I read".

**"Eris": not identified.** Several searches combining it with Android, Knox, TrustZone and networking found nothing, and the Knox case-study paper explicitly does not mention it. No content is attributed to it. Tell me what it is (or attach its documentation) and I will extend the templates.

**Engine changes (all in the non-frozen `expansion/`, plus tests, docs and the calibration builder)**
- `_DOMAIN_KEYWORDS`: three new groups ahead of `computation` that match only specific vocabulary (`android`, `knox`, `bootloader`, `dns`, `dnssec`, `rpki`, `chain of trust`, `trust anchor`, ...). Whole-word matching, so `dnsmasq` and `tcpdump` do not route. A test recomputes the pre-change routing for every older calibration sample and requires an exact match.
- Components may declare an optional `medical_map` (schema updated; used only if canonical). Older templates have none and are unchanged.
- The new templates keep component concepts disjoint from failure-mode concepts. `detect_pathologies` treats a shared concept as direct evidence (0.75); without the separation one failure mode scored 0.75 on every input purely because a component carried the same concept. Caught on the first run; a test now enforces it.
- Tests that pinned the old domain set were updated: `test_all_templates` (19 to 22 domains) and `test_calibration_corpus` (90 to 105 samples, 18 to 21 domains; 15 new samples, 5 per domain across 5 categories). Totals: **336 pytest, 133 unittest, all pass.**

**Limits to know about**
- Failure modes and patterns are my mappings onto the medical ontology, not quotes. Invariants are page-level sourced. Nothing here has been reviewed by a platform-security engineer or a network operator.
- The Knox white paper was read for about the first 100,000 of 159,658 characters. RPKI and DNSSEC coverage is the architecture and introduction RFCs only. RFC 1958's robustness principle is included because the RFC states it; later IETF criticism of it was not read.
- The main limitation from section D applies to the new domains unchanged: `decompress()` copies the template whatever the input says, so routing is the only input-dependent step. The new templates add domains the router can reach, not input-specific analysis.
- `android` also routes the robot sense of the word ("androids marching") to `mobile_security`. I judged that rare enough in this corpus to accept; say if you want it dropped from the keyword list.
- `calibration_output/decompression_calibration_v2_2.jsonl` (80 rows) is a shipped record and was not regenerated; the builder now produces 105 rows. It was already out of date against the builder (90 rows) before this change.
- If you keep patch 05, the README line calling `core/` and `registry/` "untouched" is no longer true; it is the upstream wording and I left it.

## G. Kestrel Lab branch integrated (2026-11-06, patch 07)

You attached the Kestrel workspace archive. It is the `kestrel/lab-3cycle` branch (commit `053f518`, 2026-07-15, base `main@4110edc`, V2.1.3). Against V3.0.0 it contributes four new files and one edited one; everything else in the archive is V3.0.0 being newer. Its report said runtime verification was pending, so none of it had ever been run. I ran it.

| Kestrel cycle | On V3.0.0 | What I did |
|---|---|---|
| 1. Decision-dependent outputs built before the decision | **Still real.** 76/76 calibration inputs carry a stale routing decision; 45/76 have `PENDING` in a translation. In the shipped corpora: **45/76** rows (`calibration_corpus_v2_1_3.jsonl`) and **377/500** rows (`release_candidate_corpus_v2_1_3.jsonl`) have an executive translation saying `Decision: PENDING`. | Integrated `compat.py` as the package entry point |
| 2. Sensitive text echoed into the SFT prompt labelled "redacted" | **Still real.** 4 rows in each of the shipped `calibration_corpus_v2_1.jsonl` and `_v2_1_3.jsonl` (for example a first-person disclosure about a therapist). | Integrated: SHA-256 marker in the SFT export and in the copy inside the dataset row |
| 3. Package version behind the release | **Already fixed upstream** (`__version__`, `pyproject.toml` and the V3.0.0 manifest all say 3.0.0). Kestrel's test pinned 2.1.3. | Test re-pointed at `pyproject.toml` and the latest manifest. The follow-up Kestrel documented is still open: `SemanticPacket.version` is `2.0.0` and is written into every audit record and row as `compiler_version` |

**What the wrapper changes, measured.** On all 76 calibration inputs, decision, scores, dataset tier and `training_ready` are identical to the core's. Compared with the rows the corpus scripts build today, exactly two fields differ: `outputs.executive_translation` in 45 rows and `training_payloads.sft.messages` in 4 rows. Packets that exit before Stage 4 never built these outputs and get nothing added.

**Beyond Kestrel's three cycles (found while testing)**
- The core builds the dataset row *before* the SFT export and before status becomes `compiled`, so the row `compile_semantic_packet` returns always has an empty SFT payload and status `DRAFT`. The corpus scripts hide this by calling `build_dataset_row(packet)` again. The wrapper does the same, so `packet.dataset_row` now matches what the scripts produce.
- For a SENSITIVE packet the row declares `privacy.redactions_required: ["raw_input"]`, but **nothing in the repository applies it**: the raw text stays in `input.normalized_input` and two claim-content fields. The row is flagged not training-ready and export-prohibited. Recorded as a known-gap test; whether a downstream step redacts is your call.
- The corpus scripts and `expansion.corpus` import the core function directly, so they bypass the wrapper. Re-running them would reproduce both defects. I left them alone. Pointing them at `compat` is a three-line change that alters regenerated output (the two fields above).

**Also brought over:** the Kestrel report (verbatim, with a status addendum) at `docs/kestrel/`, and the CI workflow as `.github/workflows/ci.yml`, retargeted from the old branch to `main` and extended to run pytest. It does nothing until committed and pushed, and it has not run on a GitHub runner. I simulated its steps from a clean copy (pass) and syntax-checked every file under Python 3.12; the suite itself ran on 3.13 because 3.12 here has no jsonschema or pytest.

**Verification.** 350 tests pass plus 4 expected-failure markers (the known gaps above; each flips to a reported unexpected success when the gap is fixed); 151 under unittest. Mutation check: with the entry point pointed back at the core, 12 of the new tests fail. A wheel built offline contains `compat.py` and installs and runs.

**Not done:** shipped corpora and the V3.0.0 manifest were not regenerated or edited. The wrapper is the compatibility route because `core/` is frozen; Kestrel's own recommendation was to reorder the stages inside `core/pipeline.py`, which needs the same waiver as patch 05.

## H. Path of Exile Chaos Inoculation: the 1 HP shield invariant (2026-11-06, patch 08)

You asked for another domain expansion for the PoE skill CI, the 1 HP "insane shield" mechanical invariant. I read that as the Chaos Inoculation keystone (maximum life becomes 1, immune to chaos damage) with energy shield as the only buffer, and wrote it as a sourced domain template in the same style as section F. Say if you meant something else (a particular build, or a PoE 2 only model) and I will redo it.

| Domain | Components | Invariants | Failure modes | Patterns | Sources |
|---|---|---|---|---|---|
| `poe_chaos_inoculation` | 9 | 15 | 7 | 6 | poedb Chaos Inoculation (PoE 1), fandom Eldritch Battery and an old Energy shield revision (PoE 1), Mobalytics PoE 2 energy shield guide (Jan 4, 2025) and 0.5.0 patch notes (2026-06-08), Sportskeeda PoE 2 CI explainer (undated), a pathofexile.com forum thread (Jan 2025) |

**The invariant.** CI is one indivisible trade: the lethal pool (life) is floored to the constant 1, so anything that reaches it is fatal, and the only protection is the energy shield buffer. The one damage type that ignores the buffer in PoE 1 (chaos) is made harmless by the immunity that comes with the keystone. Around that core the template records: buffer-first damage routing with bypass exceptions; recharge as delay, rate and interruption; recovery that must be converted into the buffer because a 1-point pool cannot use it (leech, regeneration, flasks); stun and ailment thresholds that still read the pre-override life in PoE 1; and the list of mechanics that need a life pool and stop working (low-life effects, life-cost skills, Arrogance Support, Midnight Bargain, Eldritch Battery).

**Version handling.** Every invariant says whether it was sourced for PoE 1, PoE 2 or both, and a test requires it. The bypass channel genuinely differs: in PoE 1 chaos ignores the buffer, in the January 2025 PoE 2 guide chaos removes twice as much buffer and poison and bleeding skip it. Recharge delay, rate and the chaos factor are **not** pinned: the sources disagree across patches (PoE 1 halved the recharge rate in 3.5.0; PoE 2 0.5.0 lowered many recharge modifiers) and one page is a 2014 revision, so the template asserts the delay-rate-interrupt structure and a test forbids percentages and seconds in invariants. This follows the repo's guardrail that PoE mappings preserve structure, not literal mechanics.

**Routing.** One new keyword group, `chaos inoculation`, `energy shield`, `eldritch battery`, `ghost reaver`, ahead of `computation`. Bare `path of exile` is deliberately not a keyword, because Buildcraft and gem-decode use PoE shorthand to describe computation builds; a test pins the `gem_decode` PoE build spec to its old routing, and the existing test that recomputes routing for every older calibration sample still passes.

**Tests and numbers.** 5 new calibration samples (one per category), `test_all_templates` (22 to 23 domains), `test_calibration_corpus` (105 to 110 samples, 21 to 22 domains), and the deep-system template test file now covers four domains with a per-template sources doc, an "every defined source is cited" check, version-qualifier and no-numbers checks, and routing cases both ways (including `energy shielding` not routing). **366 pytest (+16) and 151 unittest, all pass**, plus the same 4 expected failures. Mutation check: five deliberate breaks (a bare `path of exile` keyword, an undefined source tag, a pinned recharge number, a component and failure mode sharing a concept, a dropped version qualifier) each fail at least one test.

**Limits to know about**
- **The wikis could not be read.** poewiki.net and poe2wiki.net refuse automated clients; poedb's energy shield page, poe2db and the fandom CI page are not reachable from here. The fandom energy shield page I could reach is a 2014 revision (a 6 second delay), so it supplies structure only.
- **PoE 2 claims rest on a January 2025 early-access guide** and the 0.5.0 notes, which I read for two changes only (recharge modifiers, the stun and ailment threshold fix). I did not re-verify the January claims against 0.5.x. The 0.5.0 threshold note does not say which way the fix cuts, so the template states only that it was fixed. The Eternal Youth nerf is player-reported and is not in the template.
- **"Chaos bypasses the buffer, therefore CI" is my inference.** The sources state both facts; none says that is why the keystone exists. Failure modes and patterns are my mappings, as in section F.
- **Not reviewed by a player or tested in game.** Every claim is what a page states.
- **`decompress()` does not read the input.** Pathology detection compares the template with itself, so the five PoE samples all surface the same six failure modes at 0.6; the seventh (`self_inflicted_life_drain`) shares no word with any component and is not surfaced. This is the existing behavior from section D. I did not reword the template to change it.
- `energy shield` also appears in other games and in fiction, and a text using it that way will route here. `calibration_output/decompression_calibration_v2_2.jsonl` was not regenerated (see decision 16); the builder now produces 110 rows.

## I. Chaos Inoculation: specification and reference model (2026-11-06, patch 09)

You asked for my own decompression of the CI invariant and then for it to be built. Everything in this section is my reasoning on top of the sourced rules in H, kept out of the template's `invariants` list and marked as derived in the doc.

**Template changes.** Now 9 components, 15 invariants (unchanged), 8 failure modes, 7 patterns.
- New failure mode `spike_after_chip`: the composite of `recharge_starvation` and `oversized_hit_overflow`. Chip damage keeps the buffer below its maximum, then a hit the full buffer would absorb overflows.
- New pattern `audit_predicates_on_fixed_value`: fixing life at 1 makes every condition on it a constant (low life never, full life always).
- Refill restated in terms of quiet time: what matters is the gaps between hits against the delay, not the rate. Converted recovery is described as removing the quiet-time requirement.

**Specification.** The doc now has a short state-machine spec: life constant 1, buffer, quiet time, routing by damage type. It gives two safety properties (no open bypass; no event larger than the *current* buffer) and one refill property. The central observation is that survival changes type from a margin over time to a condition on every event.

**Reference model.** `tests/expansion/test_poe_ci_reference_model.py` encodes the sourced rules for PoE 1 and the January 2025 PoE 2 guide as a toy state machine with illustrative integers (not game values). It checks every sequence of up to three events (13,824 sequences per case) and tests specific cases:
- CI dies only by overflow, in both versions.
- One life without the immunity dies to one chaos point at full buffer.
- **PoE 2: bleeding is never the first cause of death under CI**, because it needs a hit that damages life and at life 1 that hit is already lethal. The model shows this is not vacuous: bleeding does kill a character with real life, and it kills CI if that one rule is removed. That rule is the one to re-verify against 0.5.x.
- The same three hits kill with no gaps and are survived with quiet gaps; a thousand-fold faster recharge does not help; converted recovery alone survives them.

Mutation check: removing the immunity check, the bleeding rule, the quiet-time gate or converted recovery from the model each fails at least one test.

**Not changed: the ontology.** The keystone still maps to `vaccination`, now flagged in the doc as approximate. CI is closer to removing the target (a receptor knockout) than to a learned response, and the 17 concepts have nothing for that. Adding an 18th concept is decision 21.

**Limits.** The model is a test, not part of `decompress`. A property holds for the game only as far as its encoded rules match the cited version. PoE 1 bleeding, thresholds and flasks are not modeled. `decompress` still surfaces the same seven of eight failure modes for every PoE input (section H).

**Verification.** 378 pytest (+12) and 151 unittest pass, plus the same 4 expected failures. Patches 01 to 09 in order, and the all-in-one patch, reproduce the working tree byte for byte. Without 05: 352 pass.

## Needs your decision

1. **Frozen-directory waiver** for patch 05 (`core/pipeline.py` one line; `registry/cosmological_constants.py`, which nothing imports).
2. **The five constant discrepancies in section C.** Which are paper rounding, which are definitions, which are errors? Updating `KNOWN_DISCREPANCIES` is the only change required once you decide.
3. **Do "complete X" claims make unnamed organs `UNOBSERVED`?** Your benchmark labels suggest yes. If so, the 5 `implied_organ_*` misses go away with a small rule.
4. **Table duplicates:** `SUBCONSCIOUS` vs `PROCESSOR` at society scale; "attention" listed under two LLM departments; the two parallel scale tables.
5. **BUILD_010 `minimum_score` 0.45 → 0.40.** Needed so the "LLM consumes VRAM" pattern is reachable; the alternative is changing the score weights.
6. **`canonical_chain` in `summarize_buildcraft_ontology`** is the same 11 lines for every input, whatever resolved. Keep as an outline, or filter it to what resolved?
7. **Fallback layer still fires on bare words** such as "GPU" (it is the recall layer). It is now word-bounded, slot-aware and negation-aware, but I left its design alone.
8. **`get_cosmological_isomorphism` labels every hit `STRUCTURAL_IDENTITY`**, while the buildcraft layer uses `STRUCTURAL_ANALOGY` and sets `identity_claim_allowed: False`.
9. **Enabling `resolve_frames` by default** needs a schema-aware translation (B.4).
10. **Advisor wording** for the 14 new remediation lines (D).
11. A dead routing rule in `core/decisions.py`: it reads `organ.get("type")`, but missing-organ records have `department`, so the "communication/security/ownership" routes never fire. Fixing it naively would route PRESENT organs too. Not changed.
12. **"Eris":** what does it refer to? (F)
13. **Domain review of the three new templates**: do the invariants and the failure-mode mappings match how you want them stated? (F)
14. **Routing breadth:** I did not send the generic words `network` or `firewall` to `networking`, because that would move existing inputs. Do you want them to?
15. **Kestrel fix location:** keep the wrapper (no waiver), or move the reordering into `core/pipeline.py` as Kestrel recommended (waiver, same as 05)? (G)
16. **Release data:** the shipped corpora contain the stale translations (45/76 and 377/500 rows) and 4 leaked sensitive prompts. Regenerate them, and point the corpus scripts at `compat`? Release artifacts, so not touched. (G)
17. **`redactions_required` is declared but never applied** to the dataset row. Intended, or should a step apply it? (G)
18. **`SemanticPacket.version` = `2.0.0`** in every audit record and row. Run the metadata migration Kestrel deferred? (G)
19. **PoE domain review and target version:** should the template model PoE 1, PoE 2 or both, and does someone who plays a CI build agree with the invariants, the version qualifiers and the failure-mode mappings? (H)
20. **PoE routing breadth:** `energy shield` alone routes to the new domain. Keep that, or require a second PoE term (`chaos inoculation`, `recharge`, `leech`) so other games and fiction do not land there? (H)
21. **An 18th ontology concept** for immunity by removing the target (receptor knockout), so CI need not map to `vaccination`? It changes the ontology every template uses. (I)

## What I did not verify

- Anything on your machine: I ran everything in a Linux container from a fresh clone. Network installs were unavailable, so tests ran with a path shim (and one wheel was built and installed offline); `tests/expansion/test_skill_decompression.py` imports bare `expansion.*` and needs the repo root on the path.
- The physics itself (section C), PoE-side data accuracy in `gem_forge`/`gem_decode`, the PoE mechanics in section H beyond what the cited pages state, and the 90-sample `expansion` calibration corpus beyond running its existing tests.
- The 49-row benchmark is the one you shipped. Using its labels to tune the detector risks overfitting, so the new tests also pin the specific leaks (function words, system name, negation) independently of it.
