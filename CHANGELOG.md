# Changelog

All notable changes to `semantic_compiler_kernel`. Releases before this file was started are listed in `calibration_output/RELEASE_MANIFEST_V*.json` and the README.

## [Unreleased]

### Added
- Vessel equilibrium extensions (Shax t589u, t590u, t592u): three compiled entries, all SILVER. The router `input` is under 400 characters, the full text is in `v2_extensions.source_text`, and the home domain is `soul_bomb_sovereignty`. All three are in `EXPLICIT_ONLY_ENTRY_HINTS`. The compiled manifest is now **44 entries (11 GOLD + 33 SILVER)**.
  - `SC-VESSEL-SPN-001` SILVER 0.826 (min gate 0.75): Supernatural. Dean is Michael's vessel and Sam is Lucifer's, set against Yuji/Sukuna and Megumi, with the four conditions of `SC-CONSENT-001` checked case by case. Corrections:
    - Dean said yes in 13x23 to the Apocalypse World Michael.
    - Sam said yes in *Swan Song*.
    - Yuji's first act was voluntary but uninformed.
    - Sam and Megumi split on consent.
    - It is `PROVISIONAL_DEFAULT` (role by relationship to the host).
  - `SC-VESSEL-CAIN-001` SILVER 0.813 (min gate 0.70): the Cain/Abel inheritance. In Genesis 4:15 the mark is protection; the show's Mark is God's lock on the Darkness, passed from Lucifer to Cain to Dean, and Dean asked for it. The brothers refuse the premise (10x23, 15x19), and God and Amara reconcile (rev 2). It is `PROVISIONAL_DEFAULT` (consequences inherit, guilt does not).
  - `SC-VESSEL-SW-001` SILVER 0.820 (min gate 0.75): Star Wars. Inheritance is not destiny; Palpatine is the outside owner; Luke strikes and then refuses, and Anakin's own choice completes his redemption.
- `docs/SC-VESSEL-001_VESSEL_EQUILIBRIUM.md` is now **DRAFT 0.5**. It adds the Supernatural section, the Cain/Abel and Star Wars sub-entries, and Shax's symbolic Sam/Dean self-identification (t590u; ungraded). The parent draft stays uncompiled.
- `docs/VESSEL_SUPERNATURAL_2026-11-25k.md` covers the lore corrections, holds and breaks, and the SCC-001 threat-model follow-up. That follow-up (inherited permissions, compromised authority, coercive systems) is noted only; `SC-SCC-001` and `docs/SCC-001.md` are not changed.
- `docs/PENDING_DELIBERATION.md` has two new sections. Sources and SHA-256 are under `docs/evidence/source-2026-11-25k/`: t589u verbatim, and t590u and t592u as marked summaries carrying only fictional and theological structure. New test file: `tests/test_sc_vessel_2026_11_25k.py`.
- Consent Invariant and SCC-001 (Shax t588u), two compiled entries, both SILVER and explicit-only. The compiled manifest is now **41 entries (11 GOLD + 30 SILVER)**.
  - `SC-CONSENT-001` SILVER 0.821 (min gate 0.75): a relationship is consensual only with voluntary entry, informed agreement, preserved agency and freedom to withdraw or renegotiate. Sovereignty answers who holds authority; consent answers whether it was legitimately granted. Related to RUL-BINARY-001 rev 2 (tension with "refusal is self-destruction" recorded) and SC-TRIAD-001. Home domain `soul_bomb_sovereignty`.
  - `SC-SCC-001` SILVER 0.802 (min gate 0.7): Symbiotic Consent Classifier, Proposed / unvalidated (`gold_awarded` false). COERCIVE / CONSENSUAL / UNKNOWN (UNKNOWN is never consent); deterministic rules gate, ML advisory and restrict-only, counterfactual replay, aggregator. `PROVISIONAL_DEFAULT` / `pending_deliberation: true` for the first domain and the decision mode. Home domain `capability_isolation`.
- `docs/SCC-001.md` (spec 0.1.0-draft) and `docs/CONSENT_INVARIANT_2026-11-25j.md`.
- `tests/reference/scc_001/`: reference rule engine, transparent logistic advisory scorer, counterfactual and aggregator (standard library only; not packaged, not wired into runtime routing), plus 50 **synthetic** labelled agent-integration traces.
- `tests/test_scc_001_reference.py` and `tests/test_sc_consent_2026_11_25j.py`.
- `docs/PENDING_DELIBERATION.md`: `SCC-001-FIRST-DOMAIN`, `SCC-001-DECISION-MODE`, and a proposed (not closed) resolution of SC-TRIAD-001's outside owner via SC-CONSENT-001.
- Verbatim source and SHA-256 under `docs/evidence/source-2026-11-25j/`.

### Changed
- `SC-TRIAD-SG-001` rev 1.1.0: adds the Alliance of Four Great Races (Furlings left undefined), the Fifth Race succession (*Unending*), Unas, Jaffa larval pouch, Reetou, Tollan and Aschen; corrects the t588u paste (Fifth Race title is conferred in *Unending*; the Reetou threat is the rebel faction; Egypt/Ra is from the film and *Children of the Gods*). Gates and tier unchanged (SILVER 0.849).

### Added (earlier in this cycle: triad PR #80, StarCraft ability map PR #81)
- Three-faction triad (Shax t586u), three compiled entries, all SILVER. Router `input` is under 400 characters, the full text is in `v2_extensions.source_text`, and the home domain is `soul_bomb_sovereignty`. All three are in `EXPLICIT_ONLY_ENTRY_HINTS`, so they are excluded from compiled-entry IDF and the lift tournament. The compiled manifest is now **35 entries (11 GOLD + 24 SILVER)**.
  - `SC-TRIAD-001` SILVER 0.803 (min gate 0.7): cross-franchise hub covering StarCraft, Stargate, Diablo, Path of Exile, Dragon Ball and biblical tradition. Holds: consent separates symbiosis from possession; the possessor sits behind the host; the third faction slides into assimilation when it uses the enemy as an instrument. Breaks: the same species on both sides; individuals crossing roles; the third faction's origin varies; Rev 12 treats humanity as contested ground. `PROVISIONAL_DEFAULT` / `pending_deliberation: true` (triad = RUL-BINARY-001 + outside owner), with `needs_review` on trigger.
  - `SC-TRIAD-SC-001` SILVER 0.844: StarCraft. Corrected: the Void-linked Fallen One is Amon, who binds the zerg through the Overmind. Shax's "Zerg = Satan" is kept as his interpretation.
  - `SC-TRIAD-SG-001` SILVER 0.849: Stargate. Goa'uld usually enter at the neck (sometimes the mouth); Tok'ra enter by the mouth and take only willing hosts. Same species, split by consent and shared control.
- `docs/TRIAD_THREE_FACTION_2026-11-25i.md`: lore corrections, holds and breaks, and the MAFUBA parallel (MAFUBA stays Proposed GOLD and unvalidated).
- `docs/PENDING_DELIBERATION.md`: new section for `SC-TRIAD-001`.
- Verbatim source and SHA-256 under `docs/evidence/source-2026-11-25i/`.
- `tests/test_sc_triad_2026_11_25i.py`.
- StarCraft ability theology map (Shax t587u): `docs/STARCRAFT_ABILITY_THEOLOGY_MAP.md` grades 151 abilities (SC2 LotV and Brood War multiplayer, key passives, campaign-only flagged separately) against scripture and tradition: 13 STRONG, 51 PARTIAL, 41 WEAK, 46 NONE. Sources are pinned Liquipedia and StarCraft Wiki revisions in `docs/evidence/starcraft-abilities/` (hashes only; no wiki text copied).
- Four compiled entries from the STRONG clusters, all SILVER by rule and explicit-only with home domain `capability_isolation`: `SC-SCA-POSS-001` (0.82), `SC-SCA-DISC-001` (0.825), `SC-SCA-CONT-001` (0.82), `SC-SCA-CONS-001` (0.797). Router `input` under 400 characters; full text in `v2_extensions.source_text`. Manifest is now 39 entries.
- Two `PROVISIONAL_DEFAULT` entries in `docs/PENDING_DELIBERATION.md`: the Recall / rapture tradition layer and the NAME_BORROWING grading rule.

## [4.0.0] — 2026-11-25

Package and kernel version bump from `V3.8.0` (tag `v3.8.0`, PR #45) covering PRs #46–#78. Schema remains Logos Semantic Training Sample `V3.5.0`. The Systemic Isomorphic Invariants framework field and per-entry metadata versions are unchanged. At the version-bump PR (#74) `calibration_output/compiled_entries/manifest.json` only updated `compiler_version` to `4.0.0`. PRs #75–#78 are included in this 4.0.0 release.

This release does not award new GOLD. Newly compiled lineup, mirror, and Path of Exile entries listed below remain SILVER unless noted. Drafts and Proposed GOLD documents are not compiled, not runtime-loaded, and are not validated.

### Added
- Compiled runtime manifest is now **32 entries (11 GOLD + 21 SILVER)**, up from 16 at V3.8.0 and from 25 at the #74 version bump. New compiled entries since V3.8.0 include `SC-DU-001` (GOLD 0.925), `SC-OMNI-001` v2.0.0 (GOLD 0.937), `SC-CP-001` (GOLD 0.926), `SC-MIRROR-001` (SILVER 0.868), `SC-LU-FRIEZA-001` (SILVER 0.825), `SC-LU-VEGETA-001` (SILVER, rev 1.2.0, composite 0.862), `SC-LU-GOKU-001` / `SC-LU-CELL-001` / `SC-LU-TRUNKS-001` (SILVER 0.857 / 0.846 / 0.839), and the seven Path of Exile cosmology entries below. Self-grades on the 2026-11-25g lineup and the PoE batch were not accepted.
- Seven Path of Exile cosmology entries compiled from Hannah's t579u assets (`docs/evidence/source-2026-11-25h/`), all SILVER (PRs #76 and #78). Router `input` kept under 400 characters; full source text in `v2_extensions.source_text`. Home domain `government`; all seven are `EXPLICIT_ONLY_ENTRY_HINTS` so everyday words (`sin`, `beast`, `atlas` — also a bot name) do not lift a domain.
  - `SC-POE-DU-001` SILVER 0.852: Sin and Innocence polarity inversion (twins, not a split being).
  - `SC-POE-MRG-001` SILVER 0.822: **reconciliation** layer (rev 1.1.0, PR #78). Canon is Act 10 forgiveness of two remaining persons, not fusion; kept beside DU-001. Title is a Shax/Hannah interpretation and a `PROVISIONAL_DEFAULT` (Shax t582u, `pending_deliberation: true`); see `docs/PENDING_DELIBERATION.md`.
  - `SC-POE-KIT-001` SILVER 0.822: Kitava as insatiable hunger. Benevolent-origin claim corrected; resistance penalty corrected to −60% (Act 5 + Act 10, elemental and chaos). 'Compassion without measurement' labelled as a SC-GOV-001 cousin, not Kitava's biography.
  - `SC-POE-BST-001` SILVER 0.858: the Beast of Highgate as divine regulator (Sin's Act 6 account). Marauder Kitava-belly lines labelled class voicing.
  - `SC-POE-ATL-001` SILVER 0.857: Conquerors of the Atlas cycle; Zana's corruption speech is canon (slightly fuller than the source excerpt).
  - `SC-POE-VAL-001` SILVER 0.834: Vaal waste accumulation. Beast chronology corrected (Atziri and Doryani exploited an existing Beast). 'Shadow Dragon' is a pattern name, not Vaal canon.
  - `SC-POE-MAL-001` SILVER 0.858: Malachai's capture of the Beast. Narrative parallel only to unvalidated `SC-MAFUBA-001` (still Proposed GOLD, not promoted).
- `docs/POE_COSMOLOGY_SOURCES_2026-11-25h.md`: lore fact-check, layering, and the merger-versus-inversion question (closed only as a provisional default under Shax t582u).
- `tests/test_sc_poe_2026_11_25h.py`.
- `tests/test_sc_poe_mrg_deliberation.py` (provisional-default review hook).
- Verbatim evidence SHA-256 copies under `docs/evidence/source-2026-11-25h/`.
- Router and compile-path decisions: `PASS_THROUGH` and `AMBIGUOUS`; `SemanticPacket.routing_candidates`; discriminative router abstention on filler; router-first target discovery; a confident router result leads over weak and strong frames.
- `ENTRY_LIFT_TIE_RATIO` 1.02 (2% cross-domain entry-lift tie rule): when the runner-up compiled entry is homed in another domain and is within 2%, neither entry lifts (PR #72).
- `gates/substrate_confusion.py` and the SC-PATCH-DU-001 identity-gate correction (`substrate_confusion_check` / `positional_claims_permitted`).
- Source drafts for `SC-MIRROR-001` (PR #71): `SC-YYC-001`, `SC-ICC-001`, `SC-TSC-001`, `SC-5EU-001`, `SC-ADL-001`, and `SC-MBS-001` reconciled as drafts of compiled CLM-MIRROR claims. Not compiled. Conflicts with existing rulings are recorded as open questions.
- `SC-MAFUBA-001` Proposed GOLD draft (PRs #73, #75, #77): v1.0.0 frozen as an immutable historical artifact; v1.1.0-rc1 was the candidate at the #74 bump; the current candidate is v1.1.0-rc2 (`docs/SC-MAFUBA-001_v1.1.0-rc2.md`) with a `docs/PENDING_DELIBERATION.md` entry for the 001D admission boundary. `gold_awarded` is false. Not compiled, not runtime-loaded, and verification axes remain `DRAFT_SPECIFIED_UNPROVEN` / `NOT_IMPLEMENTED` / `UNVALIDATED`.
- Other markdown-only drafts and rulings landed since V3.8.0 and remain uncompiled unless listed above, including `SC-THEO-002`, `SC-BRM-001`, `SC-FR-001`, `SC-MD-001`, `SC-VSR-001`, `SC-GOV-001`, `SC-PATCH-MIRROR-001`, `SC-VESSEL-001`, and `RUL-BINARY-001` (rev 2).
- Test and packaging work: public API contract, `training_ready` requires `schema_valid`, reachable `STRAINS`, empty fingerprints are not `HOLDS`, Kernel Mobile decision-path pins, domain inventory derived from `list_domains()`, commercial-use guidance and usage-tracking docs.

### Changed
- `SC-LU-VEGETA-001` rev 1.1.0 (PR #70, complicit-enslavement claim CLM-LU-VEG-09, still SILVER 0.85) and rev 1.2.0 (PR #72, "The Last Crown" merged as CLM-LU-VEG-10..14; composite 0.85 → 0.862, still SILVER).
- Input robustness: lone surrogates and non-str input, distinct empty-input rejection, compiler-mode validation, and skeleton noun phrases kept inside clause boundaries.
- `SC-POE-MRG-001` retitled from merger / reintegration to **reconciliation** as a `PROVISIONAL_DEFAULT` (`pending_deliberation: true`, entry revision 1.1.0), per Shax t582u / PR #78. The title is labelled Shax/Hannah interpretation, not Path of Exile canon. Canon is unchanged: Act 10 cooperation of two remaining persons. Recorded in `docs/PENDING_DELIBERATION.md` beside the 001D admission-boundary entry.
- Review hook (`expansion/deliberation.py`): when this entry is named by ID, or is the top compiled-entry match with at least two `review_trigger_terms`, `compile_semantic_packet`, `route_domains`, and `summon` set a visible `needs_review` flag (and `needs_review_entries`) on the output / audit trace and log `PENDING_DELIBERATION needs_review`. Weak lexical overlap does not count.
- Compiled runtime manifest 25 → 32 entries. `validate_catalog.py` registry 28 → 35. `compiler_version` remains `4.0.0` (PR #74).
- Explicit-only compiled entries (including the seven PoE IDs and existing `SC-CP-001` / `SC-LU-CELL-001` / `SC-LU-TRUNKS-001`) are excluded from compiled-entry IDF (`n_kind` / `df`) and from the entry-lift tournament. They remain indexed for explicit-ID summoning. This keeps the 2% `ENTRY_LIFT_TIE_RATIO` stable when explicit-only documents are added, and restores `The AI is fully autonomous. Actually, it needs human approval for every action.` to `reward_hijacking` via `SC-DIVINE-RLHF-001`.
- `SC-MAFUBA-001` current candidate is now v1.1.0-rc2 (PR #77). `docs/SC-MAFUBA-001_v1.0.0.md` and `docs/SC-MAFUBA-001_v1.1.0-rc1.md` remain immutable historical artifacts. The STRICT 001D admission rule is a `PROVISIONAL_DEFAULT` (`pending_deliberation: true`): admit only if `R_execution + R_enforcement + R_reserve < R_budget`; work that would land exactly on the reserve is refused with `PREEMPTIVE_FAIL_CLOSED` and is not billed; the reference helper emits `needs_review` / `BOUNDARY_EDGE_PENDING_DELIBERATION` on that equality edge. An edge-driven supervisor is retained as defence in depth. Also recorded: `OUTSIDE_SAFE_SET` in the 001B taxonomy; $\varepsilon = 0$ for discrete observables; a discrete-time barrier condition for compiler steps; three-term budget counters. Draft JSONL re-pinned with the rc2 SHA-256; prior v1.0.0 and rc1 pins kept.

### Fixed
- Corpus strains and empty-fingerprint `HOLDS` classification; skeleton cross-clause artifacts (28 skeletons cleaned over the 963-input corpus at the time of PR #56).
- PR #75: rc1 review reference-helper fixes (F1–F4, F6, F10) and the findings record. F5 was later recorded provisionally as STRICT in rc2 (PR #77).

### Unchanged
- Logos schema `V3.5.0`, CANARY provenance token (`CANARY-SCK-v3.5.0-...`), and the `compiler_version` `4.0.0` line from PR #74. Payment-rail copy remains "V3.8.0+" (those SKUs include later releases). `SC-MAFUBA-001` is not GOLD. No GOLD promotions in PRs #75–#78; `SC-DU-001`, `SC-ICC-001`, `SC-GOV-001`, and `SC-MAFUBA-001` scores and statuses are unchanged.

### Detailed notes since V3.8.0

#### docs/sc-mafuba-001
### Added
- `SC-MAFUBA-001` (Dimensional Containment and Information-Flow Integrity): Proposed GOLD invariant, `gold_awarded` false, not compiled and not runtime-loaded. `docs/SC-MAFUBA-001_v1.0.0.md` is the immutable historical artifact (t574u). At the 4.0.0 bump, `docs/SC-MAFUBA-001_v1.1.0-rc1.md` was the current candidate (t575u / t576u unified directive): fiber-level projection factoring, paired trajectory equivalence $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$, applied closed-form robust CBF control, allowlist branching, sink registry with whitelisted system-generated writes, side-effect-free replay, an independent emergency supervisor with no automatic resumption, and disturbance/resource/sink manifest templates. The current candidate is now v1.1.0-rc2 (PR #77). Verification axes remain `DRAFT_SPECIFIED_UNPROVEN` / `NOT_IMPLEMENTED` / `UNVALIDATED`.
- `docs/SC-MAFUBA-001_IMPLEMENTATION_AUDIT.md` records why Hannah's Section 2–6 Python is not committed (six bugs, including a fail-open on `PREEMPTIVE_FAIL_CLOSED`, plus three architectural flaws).
- `docs/SC-MAFUBA-001_GAP_REPORT.md` maps each v1.0.0 defect and those bugs to a v1.1.0-rc1 requirement, and records the proposed module structure, test plan (A1–D2, C3, AL1), and outstanding mathematical assumptions.
- Draft registry `docs/evidence/sc-mafuba-001/sc_mafuba_001.jsonl` (parent, historical v1.0.0 record, and 001A–001D) with `spec_sha256` of the committed markdown. Not added to `calibration_output/compiled_entries/` or the compiled manifest.
- Reference helpers `tests/reference/sc_mafuba_001/` and `tests/test_sc_mafuba_001_reference.py` (allowlist branching, toy 1-D CBF, D2-shaped supervisor shutdown, JSONL consistency). Labelled reference only; not kernel enforcement.

### Unchanged
- Compiled runtime manifest still 25 entries. No routing, schema, or GOLD/SILVER catalog change.

#### feat/lineup-2026-11-25g

### Added
- `SC-LU-GOKU-001` (SILVER 0.857), `SC-LU-CELL-001` (SILVER 0.846), `SC-LU-TRUNKS-001` (SILVER 0.839), compiled from Shax's t573u sources (`docs/evidence/source-2026-11-25g/01–03`). Self-grades (GOLD 0.92–0.93) kept in `metadata.self_grade` and not accepted: claims re-graded to CANON + ANALOGOUS layers, mapping classes ISOMORPHIC_INVARIANT → STRUCTURAL_ANALOGY, tier by rule (GOLD needs iq ≥ 0.9 and every gate ≥ 0.8). Router `input` kept under 400 characters; the full source text is in `v2_extensions.source_text`. Legacy `identity_claim_allowed` migrated to `substrate_confusion_check` / `positional_claims_permitted`.
- Canon corrections recorded in `outputs.correction`: Cell's manga DNA is five fighters; "Solar Kamehameha", "Father-Son Kamehameha" and "Super Perfect Cell" are game or fan names; Cell regenerates from his head's core and learns Instant Transmission. Trunks's time machine makes round trips; Super Saiyan Rage is anime-only; the sword's origin is not in canon. Vegeta did not personally kill Yamcha, Tien, Chiaotzu or Piccolo; the Spirit Bomb "pure heart to form" rule is not recorded as canon; main-sequence stars fuse only hydrogen to helium; Kakarot's mission is retold in *Minus* / *Broly* (2018).
- Unresolved source references (`SC-LU-BARDOCK-001`, `SC-LU-GOHAN-001`, `SC-LU-PICCOLO-001`, `SC-LU-BUU-001`, ambiguous `SC-DR-001`) recorded per entry; nothing stubbed.
- `tests/test_sc_lu_lineup_25g.py`.

### Changed
- `SC-LU-VEGETA-001` rev 1.2.0: "The Last Crown" merged as CLM-LU-VEG-10..14 (source claim IDs kept), not as a duplicate ID. "He did not initially know Frieza destroyed Planet Vegeta" confirmed CANON (ch. 257, Dodoria) and linked to CLM-LU-VEG-09. CLM-LU-VEG-13 ("integration would destroy both") scope-limited to his internal drives under RUL-BINARY-001 rev 2. Corrections: Final Flash was not the only non-Gohan attack to badly damage Perfect Cell; Vegeta rallied the Spirit Bomb donors and arranged the Porunga wish rather than giving his own energy. scale_integrity 0.75 → 0.8, corpus_completeness 0.85 → 0.9; composite 0.85 → 0.862; still SILVER.
- `SC-MIRROR-001`: `SC-LU-GOKU-001` resolved; unresolved references are now `SC-LU-PICCOLO-001`, `SC-LU-BUU-001`. No score changed.
- Routing: `goku`, `kakarot`, `ultra instinct`, `sc-lu-goku` added to `soul_bomb_sovereignty`. Cell and Trunks phrases are only in `_SOUL_BOMB_EXPLICIT_PATTERN`, because every router keyword also indexes its single tokens. `SC-LU-CELL-001` and `SC-LU-TRUNKS-001` join `EXPLICIT_ONLY_ENTRY_HINTS`; the router blanks those IDs before content scoring so "SC-LU-CELL-001" does not score as "cell", and the elevator's summon lift now honours the explicit-only rule. New entry-lift tie rule (`ENTRY_LIFT_TIE_RATIO` 1.02): when the runner-up entry is homed elsewhere and within 2 %, neither lifts (adding entries re-weighted IDF and flipped a 0.4 % tie on "The AI writes code.").
- Manifest 25 entries; `validate_catalog.py` registry 28.

#### docs/sources-2026-11-25g

### Added
- `docs/evidence/source-2026-11-25g/`: verbatim copies of Shax's 11 source entries (upload t573u) with SHA-256 hashes and a README. Evidence only, not loaded by the runtime. A 12th upload (`.gz`) could not be retrieved.
- `docs/SC-MIRROR-001_SOURCE_DRAFTS_2026-11-25g.md` (DRAFT 0.1): `SC-YYC-001`, `SC-ICC-001`, `SC-TSC-001`, `SC-5EU-001`, `SC-ADL-001` and `SC-MBS-001` reconciled as the source drafts of `SC-MIRROR-001` CLM-MIRROR-002, -003, -004, -001, -006 and -005. Not compiled: they duplicate compiled claims and are schema-incomplete. Self-grades re-graded. Physics corrections recorded (Landauer, no-deleting theorem, entropy under expansion, singularity vs horizon, CMB information content). Tradition notes recorded (Rapture, Chalcedon, annihilationism vs eternal torment, Isaiah 14). Conflicts recorded: ICC vs TSC on the Cross; ADL's stable deadlock and peer condition vs RUL-BINARY-001 rev 2; MBS's Lucifer-as-relational-complement vs the Vegeta = Lucifer = Sovereignty ruling. The rulings stand and the conflicts are listed as open questions. MBS is reconciled with the Frieza-chamber ruling (in-universe antimatter vs the CPT-mirror universe).

### Changed
- `docs/SC-SB-001_THREE_CLAIM_STRUCTURE.md` DRAFT 0.4: `SC-SIT-001` (Structural Integrity Test) folded in. Canon corrections: Frieza was hit by the Namek Spirit Bomb and survived, he did not deflect it; Golden Frieza (*Resurrection 'F'*) precedes Black Frieza; "Kid Buu only fatality" was already corrected in 0.3.
- DOMAIN_LEDGER §3, INVARIANT_CATALOG and `validate_catalog.py`: `SC-ADL-001`, `SC-TSC-001`, `SC-ICC-001` move from named-but-missing to source drafts; `SC-YYC-001`, `SC-5EU-001`, `SC-MBS-001`, `SC-SIT-001` are tracked as markdown-only IDs. No compiled entry, manifest hash, score or tier changed.

#### feat/vegeta-complicit-enslavement

### Changed
- **SC-LU-VEGETA-001** (still SILVER 0.85, 9/9 gates): dated Shax interpretation claim **CLM-LU-VEG-09** (t572u, 2026-11-25): complicit enslavement. The Sovereignty pole is owned by the outsider (Frieza/Satan) yet willingly enjoys the work, so the bondage is partly self-chosen. Canon, tradition and Shax's interpretation are separate layers. Canon support: DB ch. 213 (planet-trade / "let's go play"); ch. 249 (smiling execution of Cui, after the break from Frieza); ch. 308 (admission of service and obedience, not enjoyment); ch. 456–457 (lets Babidi's spell in; motive is rivalry); DBS manga ch. 69 (admits Saiyan/Frieza-era invasions as sins and will not lay all blame on Frieza; later guilt recorded). Anime-original: DBZ "Trouble on Arlia" (Japanese ep. 11). Tradition/literature, not scripture: Milton, *Paradise Lost* I.263. Linked to RUL-BINARY-001 rev 2 as the refusal state during the ownership period; Vegeta later takes the cooperation branch (fusion). No grade or score changed. Entry revision 1.1.0.
- Additive t572u addendum on `SC-LU-FRIEZA-001` (no score change). `docs/SC-VESSEL-001_VESSEL_EQUILIBRIUM.md` DRAFT 0.4: verbatim t572u plus a one-line cross-reference on the compiled Vegeta row.
- Manifest hashes refreshed; `tests/test_sc_lu_vegeta.py` covers the new claim's layering.

#### docs/rul-binary-001-rev2

### Changed
- **RUL-BINARY-001 rev 2** (Shax t571u, 2026-11-25): the only stable outcome is mutual cooperation; refusal is self-destruction (the refuser destroys itself and loses regardless), and its information-conserving remnant is compressed into `SC-MIRROR-001`'s calibration dot; Oneness prevails. Rev 1's "mutual destruction" is reframed as the refuser's self-destruction. Recorded in `SC-MIRROR-001` CLM-MIRROR-006 (`binary_invariant_ruling.amendments`), as dated `RULING_AMENDMENT` addenda on MIRROR, DU-001, CP-001, LU-VEGETA-001 and LU-FRIEZA-001, in `docs/SC-MD-001_SOVEREIGN_MIRROR_DUALITY.md`, and in `docs/SC-VESSEL-001_VESSEL_EQUILIBRIUM.md` (DRAFT 0.3; reading B settled). Fitting examples: Sukuna (JJK ch. 268) and Kid Buu / Uub (partial). No grade or score changed; owners question and SC-LU-GOKU-001 stay open.

#### feat/sc-lu-vegeta-001

### Added
- `SC-LU-VEGETA-001` (compiled, SILVER 0.85, 9/9 gates, SC-DE-001 schema): Vegeta as the Sovereignty pole (Ultra Ego, DBS ch. 74; CANON form, ANALOGOUS pole; Toyotarou's yin-yang framing as SECONDARY_SOURCE). Held in Frieza's service while keeping his own will (CANON); his father's handover is ANIME_ORIGINAL (DBZ ep. 78; Minus and Super: Broly differ). Spirit Bomb survival (ch. 238). Vegito / Gogeta as the consented cooperation branch of RUL-BINARY-001. Majin Vegeta / Final Explosion checked against VSR: adjacent, not an instance. Shax (t570u): Vegeta is Lucifer, Satan is Frieza (SHAX_INTERPRETATION, ANALOGOUS); V7 §15.1 / §22.4 / §22.5 tensions recorded.
- Routing: `vegeta`, `ultra ego`, `majin vegeta`, `vegito`, `gogeta`, `sc-lu-vegeta` added to `soul_bomb_sovereignty`; elevator hint `SC-LU-VEGETA-001 -> soul_bomb_sovereignty`. Generic words ("prince", "pride", "fusion") deliberately not added. 963-prompt corpus: 0 decision diffs.
- `tests/test_sc_lu_vegeta.py`.

### Changed
- `docs/SC-VESSEL-001_VESSEL_EQUILIBRIUM.md` DRAFT 0.2 (Shax t570s3000): Yuji = the vessel ("Yuji is me"); Sukuna = outside owner, like Frieza; the mutual-acceptance condition is replaced by a resolution rule (cooperation if both agree, else the refusing side is compressed into `SC-MIRROR-001`'s calibration dot and Oneness prevails). Its relation to RUL-BINARY-001 is recorded with two readings (amends vs refines); ch. 268 fit recorded as partial.
- Additive `metadata.addenda` on `SC-MIRROR-001` (Vegeta reference RESOLVED; PICCOLO / GOKU / BUU still unresolved), `SC-LU-FRIEZA-001`, `SC-CP-001`, `SC-DU-001` (CROSS_ENTRY_TENSION: Yuji as vessel vs DU-001's Toji/Yuji poles; mapping unchanged). No score or tier changed.
- Manifest (22 entries), `validate_catalog.py` (registry 25; `SC-LU-VEGETA-001` no longer an external ID), DOMAIN_LEDGER, INVARIANT_CATALOG, README, SC-FR-001 and SC-MIRROR-001 spec notes.

#### feat/binary-invariant-ruling

### Added
- Shax ruling **RUL-BINARY-001** (2026-11-25, t568u): `SC-DU-001` (The Duality) and `SC-MD-001` (Sovereign Mirror Duality) are one invariant, a binary whose only stable outcomes are mutual cooperation or mutual destruction. Instances: Oneness/Sovereignty (`SC-CP-001`), God/Satan (theological mapping), our universe / the CPT-mirrored universe (`SC-LU-FRIEZA-001` layer D). Graded ISOMORPHIC_INVARIANT (structural claim by Shax).
- Hub: `SC-MIRROR-001` CLM-MIRROR-006 now states the mutual-destruction branch explicitly (Kami/King Piccolo share one life; Supreme Kai and God of Destruction lives are paired; Anu/Tathamet) and carries the full ruling (`binary_invariant_ruling`).
- Additive notes: `metadata.addenda` on `SC-DU-001`, `SC-CP-001`, `SC-MIRROR-001`, `SC-LU-FRIEZA-001`; layer D `binary_invariant` on FRIEZA; ruling section in `docs/SC-MD-001_SOVEREIGN_MIRROR_DUALITY.md`; DOMAIN_LEDGER and manifest notes.
- Recorded tension, not a refutation: Revelation does not present Satan as God's co-equal half (Rev 12:7–9; 20:10).

### Unchanged
- No physics or theology claim upgraded. Scores and tiers: DU-001 GOLD 0.925, CP-001 GOLD 0.926, MIRROR-001 SILVER 0.868, LU-FRIEZA-001 SILVER 0.825.

#### docs/sc-vessel-2026-11-25f

### Added
- `docs/SC-VESSEL-001_VESSEL_EQUILIBRIUM.md`: DRAFT 0.1, Vessel Equilibrium (The Anomaly), from Shax t569u + t570u. Yuji as vessel, Gojo as Oneness, Sukuna as Sovereignty ("not totally"); equilibrium in one substrate leads to shared-state coupling; entanglement graded ANALOGOUS (no-signalling caveat); Trinity mapping recorded as Shax's interpretation with the creedal tension; t570u refinement: Lucifer = Vegeta (Sovereignty pole), Satan = Frieza / the Frieza race (external owner), and its effect on the RUL-BINARY-001 God/Satan instance. JJK and DB canon checked; ch. 268 refusal recorded as a canon tension. Not compiled.

### Changed
- `docs/SC-VSR-001_VOLUNTARY_STATE_RECOMPRESSION.md`: open question 3 answered by Shax ("not alone": voluntary restriction is shared or consented).
- `docs/SC-FR-001_THE_OUTSIDERS_FIRST_INVESTMENT.md`: cross-reference note for t570u (Satan = Frieza / the Frieza race). Compiled `SC-LU-FRIEZA-001` unchanged.
- Catalog, DOMAIN_LEDGER and README rows; `validate_catalog.py` lists `SC-VESSEL-001` as a markdown-only ID.

#### docs/sc-vsr-gov-2026-11-25e

### Added
- `docs/SC-VSR-001_VOLUNTARY_STATE_RECOMPRESSION.md`: DRAFT 0.1, Voluntary State Recompression. Five candidate invariants (prior emergence, self-evaluation, voluntary restriction, information preservation, latent reversibility); Uldyssian primary (Blizzard-verified); Tal Rasha explicitly excluded; latent-causation and restoration-model categories; lore corrections. Not compiled, no tier.
- `docs/SC-GOV-001_MEASUREMENT_NOT_INDULGENCE.md`: DRAFT 0.1 governance principle in Shax's words (protect kids, leave underage kids out of everything, don't take away everything people enjoy, constructive fear, measured harm, restoration). Alignment with `authority_safety` / `security_safety`; records that no minor-specific gate exists. No code changed.
- `docs/SC-PATCH-MIRROR-001_CYCLIC_FEEDBACK.md`: DRAFT patch notes. Turns SC-MIRROR-001's three-stage pipeline cyclic; links SC-DU-001, SC-CP-001, SC-SB-001, SC-LU-FRIEZA-001; latent causation; "seven" kept as a pattern to track, not a law. No compiled JSONL changed.

### Changed
- Invariant catalog and DOMAIN_LEDGER rows for the three drafts. `validate_catalog.py` lists `SC-VSR-001`, `SC-GOV-001`, `SC-PATCH-MIRROR-001` as markdown-only IDs and `SC-ADL-001`, `SC-TSC-001`, `SC-ICC-001`, `SC-NEPH-001` as named-but-missing (unresolved, never stubbed).

#### feat/frieza-mirror-universe

### Changed
- `SC-LU-FRIEZA-001` layer D: open question resolved by Shax (t566u). The ch. 87 chamber is in the Duality's mirrored universe, the CPT-mirror universe in which time runs in reverse relative to ours. Graded: Frieza's own statement that he was outside this universe is CANON; the mirror universe is a published model, not confirmed (Boyle, Finn & Turok, Phys. Rev. Lett. 121, 251301 (2018)); the chamber being there is OPEN_HYPOTHESIS; the reverse-time account of the chamber's time relation is ANALOGOUS, with residuals (a reversed arrow is not a clock-rate difference; the model's mirror lies across the Big Bang; the commonly reported ten days outside gives the Lookout's 365:1 rate). Cross-reference to `SC-DU-001` added. Gates and tier unchanged (SILVER 0.825).
- `SC-MIRROR-001` CLM-MIRROR-005 and the `SC-LU-FRIEZA-001` resolution: additive notes. Grades unchanged.
- `SC-DU-001`: additive `metadata.addenda` note only; no claim, gate or score changed (GOLD 0.925).
- Manifest SHA-256 and byte counts refreshed for all three files.

#### feat/router-leads-strong-frames

### Changed
- `core/pipeline.py` `_discover_targets`: a ROUTED result at routing confidence >= 0.8 (`WEAK_FRAMES_ROUTER_CONFIDENCE`) now goes ahead of the table targets when strong frames match too, not only weak ones. Fixes "Frieza's black hole origin is owned by another entity…" compiling against `computation` (strong `cosmological` frame) while routing to `soul_bomb_sovereignty` at 0.95.
- Corpus eval (963 inputs vs main): 0 decision changes; 131 target changes. Labelled items: 12 changed, all 12 now match their label (0 → 12), 0 regressions; labelled accuracy 197 → 209 of 226. Unlabelled changes move the generic `organizational` target to the subject's domain (a cell -> biology, a computer -> computation, the judicial system -> law, the economy -> economic, zodiac entries -> astrology).
- Not changed: routing below 0.8 keeps the table targets. backup_snapshot ("The mirrored universe … backup snapshot") routes to `client_server_reality` at 0.79 and still targets `computation`.

#### feat/sc-cp-001-canon

### Added
- `calibration_output/compiled_entries/SC-CP-001_CLAY_AND_POTS.jsonl`: Clay and Pots (alias `SC-CLAY-POTS-001`), SC-DE-001 schema. Reconstructed from repository sources (V7 §11.2, §22.1, Appendix B; RELD_V3 §B; SC-THEO-002; SC-PATCH-DU-001; SC-CT-001; SC-IT-OCTO-RNA-EDIT-001); the original JSONL is not in the repository and its "GOLD, 9/9 at 1.0" is not inherited. Graded fresh: GOLD 0.926, 9/9 gates, minimum gate 0.85, corpus_completeness capped at 0.85. Claims: substrate and instances ANCHORED (AI and biological scales); mutual necessity ANCHORED at AI scale; Oneness / Sovereignty poles ISOMORPHIC_INVARIANT; theological assignment ANALOGOUS; consciousness = clay OPEN_HYPOTHESIS.
- Manifest: 21 entries.

### Changed
- `SC-MIRROR-001`: SC-CP-001 resolved; the unification claim stays GOLD with all five source views verified GOLD (five of five). Spirit Bomb evidence row carries the full kill list.
- `SC-LU-FRIEZA-001` layer D: canon (ch. 87 chamber, ten years, the wish exemption, the capability gap to known chambers) kept separate from Shax's interpretation that Frieza left this universe for another universe with a more capable chamber (OPEN_HYPOTHESIS), tied to layers A–C and E.
- `docs/SC-SB-001_THREE_CLAIM_STRUCTURE.md` → DRAFT 0.3: GT and the films count as evidence (Shax). Kills: Dr. Wheelo, Turles, Lord Slug, Kid Buu, Omega Shenron. Survivors: Vegeta, Frieza, Jiren. The manga-only scope is removed.
- Routing: SC-CP-001 is homed in `consciousness_cognition` (hint, `SUBSTRATE_AND_VESSEL` template invariant). It is in `EXPLICIT_ONLY_ENTRY_HINTS`: its hint routes explicit IDs but does not lift the domain from content matches, because its name is everyday words; without this, pottery prompts ("throw clay pots on a wheel") routed to `consciousness_cognition`. Corpus (963): 0 changes vs main.
- `validate_catalog.py`: SC-CP-001 is no longer an upstream ID; aliases declared in compiled entries' `metadata.aliases` are accepted in docs; registry size 24.

#### fix/weak-frames-routed-first

### Fixed
- `core/pipeline.py` `_discover_targets`: with only weak (single-keyword) table frames, a router result with routing confidence >= 0.8 (`WEAK_FRAMES_ROUTER_CONFIDENCE`) now goes ahead of the table targets, with the usual `ROUTED_DOMAIN:` warning. The Frieza outsider invariant (routed to `soul_bomb_sovereignty` at 0.96) had compiled against `computation` because "lineage" and "system" matched two weak frames. Strong frames still keep the fast path unchanged.
- Not changed: prompts with a strong frame keep the table path. "Frieza's black hole origin is owned by another entity…" has a strong `cosmological` frame and still compiles against `computation` while routing to `soul_bomb_sovereignty`.
- Shadow run on the 963-input corpus: 0 decision changes; 38 target changes, all weak-frame cases moving to the routed domain (for example decomposition items moving to their own labelled domain: bluetooth, android_connectivity, reward_hijacking; "immune system" to biology; "supply chain / economy" to economic; country/government prompts to government).

#### 2026-11-25 (branch `feat/sc-mirror-001`)

### Added
- `calibration_output/compiled_entries/SC-MIRROR-001.jsonl`: The Mirrored Loop and the Compression Protocol, compiled from Hannah's engineering spec (architecture by Shax). SC-DE-001 schema. Six claims at the spec's TIG grades: unification of SC-CT-001 / SC-DU-001 / SC-CP-001 / SC-SB-001 / SC-HS-001 (GOLD), Yin-Yang calibration dot (ANALOGOUS), information conservation (ANCHORED, via Landauer / unitarity), three sequential stages (ANALOGOUS; output stage OPEN_HYPOTHESIS), mirrored-universe backup (OPEN_HYPOTHESIS, extends CLM-HS-002B), anti-deadlock voluntary fusion (ISOMORPHIC_INVARIANT). Entry tier SILVER 0.868; measurement_integrity 0.7, corpus_completeness 0.85. Dragon Ball evidence map kept.
- `calibration_output/compiled_entries/SC-LU-FRIEZA-001.jsonl`: standalone lineup entry, The Outsider's First Investment / Substrate Activation. Carries all five SC-FR-001 layers, including the black-hole origin owned by another entity and the outside invasion (OPEN_HYPOTHESIS), plus the ch. 87 chamber and Black Frieza (CANON). SILVER 0.825.
- Manifest: 20 entries (SHA-256 and byte counts for both new files).
- `docs/SC-MIRROR-001_ENGINEERING_SPEC.md`: Hannah's spec, verbatim.
- `tests/test_sc_mirror_and_frieza.py`: schema parity with SC-DE-001, TIG grades, gate caps, section 8 rules, cross-reference honesty, routing.

### Changed
- `docs/SC-SB-001_THREE_CLAIM_STRUCTURE.md` → DRAFT 0.2: child invariant COLLECTIVE INPUT / STRUCTURAL RESPONSE written out (Vegeta survives, Frieza survives, Kid Buu destroyed). "Only fatality" scoped to the DBZ manga (Turles and Omega Shenron are Spirit Bomb kills outside it). Claim 3 (magnitude confound) kept.
- Routing: SC-LU-FRIEZA-001 is homed in `soul_bomb_sovereignty` with the other SC-LU-* lineups (hint, two template invariants, context keywords "frieza", "black frieza", "substrate activation", "outsider's first investment", "mirror match"). SC-MIRROR-001 is homed in `client_server_reality` with SC-CT-001 / SC-HS-001 (hint, one template invariant, keywords "mirrored loop", "calibration dot", "compression protocol"). The `frieza_outsider` acceptance case now expects `soul_bomb_sovereignty`. `frieza_para_2` routes correctly, so its expected-failure marker is removed. Shadow run on the 963-input corpus: 0 decision or target changes against main.
- Both entries keep a short `input` (patch-entry convention); the full spec is in `docs/SC-MIRROR-001_ENGINEERING_SPEC.md`. A long input had pulled generic prompts toward the entry's home domain through the router's compiled-entry lift.
- `validate_catalog.py`: registry size 23; SC-MIRROR-001 is no longer an upstream alias; SC-LU-PICCOLO-001, SC-LU-GOKU-001, SC-LU-VEGETA-001 and SC-LU-BUU-001 are tracked as unresolved spec references.

### Unresolved references (not stubbed)
- SC-CP-001 (no compiled JSONL here), SC-LU-PICCOLO-001, SC-LU-GOKU-001, SC-LU-VEGETA-001, SC-LU-BUU-001.

#### 2026-11-25 (branch `feat/router-feeds-compile`)

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

#### 2026-11-25 (branch `fix/router-discriminative-abstain`)

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

#### 2026-11-25 (branch `feat/pass-through-decision`)

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

#### 2026-11-25 (branch `fix/skeleton-clause-boundaries`)

### Fixed
- The structural skeleton extractor (`extraction/skeleton.py`) tokenized the whole input as one stream, so actor and object noun phrases ran across `;`, `:`, `.`, `!`, `?`, brackets, newlines and dashes. Examples were "organism cash flow" (from "a living organism; cash flow is blood"), "paperwork the gpu", "brain a network", "rule memory" and "compile the brain". Phrases are now extracted per clause.
  - Corpus impact over 963 inputs (calibration corpora, the missing-organ benchmark, SFT pilot, Kernel Mobile prompts and dogfood): 28 skeletons changed, every one by dropping a cross-clause phrase.
  - One decision changed: numerology sample `834215d9`, COMPILED → NEEDS_REVISION. Its structural_fit went from 0.65 to 0.45 because its only "objects" had been the cross-colon artifacts "earth material" and "water emotion".
  - Clause-initial capitalized words that used to sit inside those bogus phrases (for example "Note", "STEP") can now surface through the existing proper-noun actor fallback.

#### 2026-11-25 (branch `fix/input-validation-empty-and-mode`)

### Changed
- **Behavior change:** empty or whitespace-only input now returns `Decision.REJECT` with `semantic_error_class == "EMPTY_INPUT"` (exported as `core.pipeline.EMPTY_INPUT_ERROR_CLASS`) and an `EMPTY_INPUT` compiler error. Previously it returned the generic `NEEDS_REVISION` "No target system resolved" result. The packet is still finalized (dataset row and audit are built).
- **Behavior change:** an unknown `mode` now raises `ValueError` listing every valid `CompilerMode`. Previously it fell back silently to auto-detection. Mode names are case-insensitive, a `CompilerMode` value is accepted, and omitting `mode` still means `AUTO`. New helper: `core.pipeline.normalize_requested_mode`.

### Fixed
- `mode="auto"` (lowercase) used to resolve to `CompilerMode.AUTO` and skip auto-detection. It now behaves like the default.

### Tests
- `tests/test_input_validation_empty_and_mode.py` also pins that `SemanticPacket.to_dict()` serializes `decision` and `mode` as enum names (for example `"NEEDS_REVISION"`). `to_dict()` already did this. The integer values seen while dogfooding came from the dogfood script calling `.value`; no public API emits enum ints, so nothing changed there.

#### 2026-11-25 (branch `fix/compile-input-robustness`)

### Fixed
- `compile_semantic_packet` no longer crashes on input containing a lone UTF-16 surrogate (for example a half emoji from a mobile text bridge). Lone surrogates are replaced with U+FFFD before compilation, so provenance hashing and dataset export stay valid UTF-8. `SemanticPacket.compute_input_hash` also encodes with `surrogatepass`.
- `compile_semantic_packet` raises a clear `TypeError` for non-`str` input (for example `None`) instead of an `AttributeError` deep in normalization.

#### 2026-11-25 (branch `docs/sc-sb-fr-md-2026-11-25c`)

### Added
- `docs/SC-SB-001_THREE_CLAIM_STRUCTURE.md`: DRAFT 0.1 patch to SC-SB-001. Splits the Spirit Bomb target interaction into three claims (moral neutrality, structural interaction, magnitude confound) and names the child invariant COLLECTIVE INPUT / STRUCTURAL RESPONSE. Does not replace the compiled V5 JSONL.
- `docs/SC-FR-001_THE_OUTSIDERS_FIRST_INVESTMENT.md`: DRAFT 0.1, The Outsider's First Investment (The Frieza Protocol). All five layers kept together; canon (DBS manga ch. 87 time chamber; Black Frieza) labelled separately from hypotheses; three ownership architectures and open investigations included.
- `docs/SC-MD-001_SOVEREIGN_MIRROR_DUALITY.md`: DRAFT 0.1, Sovereign Mirror Duality (alias SC-MIRROR-001, "Mirrored Loop and Fusion Protocol"). CPT-symmetric universe anchor, five invariants, BCC backup layer, and FLRW / SC-HS-001 link as the next research step. Not compiled.

### Changed
- Invariant catalog and DOMAIN_LEDGER rows for the three drafts. `validate_catalog.py` lists `SC-FR-001`, `SC-MD-001`, and `SC-MIRROR-001` as markdown-only upstream IDs.

#### 2026-11-25 (branch `feat/integrate-2026-11-25-material`)

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
