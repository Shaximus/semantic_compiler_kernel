# DOMAIN LEDGER — Invariant Translator Coverage & Provenance Tracker

- **Catalog Directory:** `docs/invariant_catalog/`
- **Compiled Entries Directory:** `calibration_output/compiled_entries/`
- **Last Updated:** 2026-11-24
- **Validation Policy:** Coverage MUST reach **100.0%** with zero omitted pairs, zero elided abbreviations, exact programmatic matrix checks, and strict Section 10 gate discipline.

---

## 1. Decompressed Domains Registry

| Domain ID | Entry ID | Authoritative Source & Version | Date Verified | Exact Ontology Counts | Coverage % | Passes Completed | Remaining Scope | Artifacts Emitted |
|---|---|---|---|---|---|---|---|---|
| `DOMAIN_EXPANSION_EGO` | `SC-IT-DOMAIN-EXPANSION-EGO-001` | `DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl` (v3.5.0) + `EGO_LINEUP_DOMAIN_EXPANSION_MAP.md` + canonical JJK/Naruto/DMC/Berserk/Black Clover/Mega Man/PoE mechanics | 2026-11-23 | 15 core nodes, 225/225 ordered pairs (110 non-neutral: 91 PHYSICAL, 3 BIOLOGICAL_ECOLOGICAL, 11 SYMBOLIC_MYTHIC, 5 BALANCE-ONLY; 115 NEUTRAL), 8 modifiers, 8 pools, 10 formal rules, 15/15 17-primitive tables, 15/15 11-role closures, 15/15 departments, 6 predictions (4 confirmed, 2 untested) | **100.0%** | 1 (Full 11-step pass) | **0%** (Complete) | `DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md`, `INVARIANT_ENTRY_SC-IT-DOMAIN-EXPANSION-EGO-001.jsonl` |
| `POKEMON` | `SC-IT-POKEMON-001` | Bulbapedia / *Pokemon Scarlet & Violet* (Gen IX core rules; Gen VI–IX unchanged 18-type matrix) + `pokemon_seed_chart.md` | 2026-11-23 | 18 types, 324/324 attacker x defender pairs (51 `2x`, 61 `0.5x`, 8 `0x`, 204 `1x`), 120/120 non-neutral grounded edges (58 PHYSICAL, 20 BIOLOGICAL_ECOLOGICAL, 31 SYMBOLIC_MYTHIC, 11 BALANCE-ONLY), 16 3-cycles (5 strict RPS), 4 weather (incl. Gen IX Snow), 4 terrains (1.3x / Misty 0.5x Dragon), 6 non-volatile statuses, 11 absorb/rewrite abilities, 171 dual-type combinations, 18/18 17-primitive tables, 18/18 11-role closures, 15/15 departments, 6 predictions (5 confirmed, 1 untested) | **100.0%** | 1 (Full 11-step pass) | **0%** (Complete) | `DOMAIN_DECODE_POKEMON.md`, `INVARIANT_ENTRY_SC-IT-POKEMON-001.jsonl` |
| `BATCH_2026_11_23` | `SC-IT-BATCH-2026-11-23` | Cross-domain synthesis over `SC-IT-DOMAIN-EXPANSION-EGO-001` + `SC-IT-POKEMON-001` + reference bridges (`Path of Exile` 5-damage/CI/Leech/Soul Eater + `Wu Xing` 5-phase generation/control) | 2026-11-23 | 4 comparative domains, 24 catalog classes (14 seed + 10 compiled extensions), 10 class compositions, 12-row cross-domain counterplay transfer matrix, 5 batch predictions (4 confirmed, 1 failed -> residual) | **100.0%** | 1 (Batch synthesis pass) | **0%** (Complete) | `INVARIANT_ENTRY_SC-IT-BATCH-2026-11-23.jsonl`, `INVARIANT_CATALOG.md`, `DOMAIN_LEDGER.md` |
| `OCTOPUS_RNA_EDITING` | `SC-IT-OCTO-RNA-EDIT-001` | Birk et al., *Cell* 186(12):2544–2555 (2023), doi:10.1016/j.cell.2023.05.004; Rangan et al. (squid companion); Liscovitch-Brauer et al., *Cell* (2017) | 2026-11-24 | 12 nodes, 132/132 ordered pairs, 20 non-neutral edges, 3 modifiers, 2 pools, 3 formal rules, 15/15 departments across 4 scales, 4 predictions (`P1`–`P2` confirmed, `P3` confirmed biology / untested AI, `P4` untested), 9/9 gates (GOLD 0.953), defines Class 24 (`RUNTIME_RECODING_OVER_FIXED_BASE`, Claude `#19`) | **100.0%** | 1 (Full biological decode) | Squid companion paper (Rangan et al., kinesin) in full | `DOMAIN_DECODE_OCTOPUS_RNA_EDITING.md`, `calibration_output/compiled_entries/INVARIANT_ENTRY_SC-IT-OCTO-RNA-EDIT-001.jsonl` |
| `FLAT_FLRW_HUBBLE_SCHWARZSCHILD` | `SC-HS-001` | Flat FLRW Friedmann constraint; Pathria RK, *Nature* 240:298–299 (1972); Gibbons GW & Hawking SW, *Phys. Rev. D* 15:2738–2751 (1977) | 2026-11-24 | Revision `1.1.0` TIG-graded patch entry: 6 derivation steps, 7 TIG-graded claims (`CLM-HS-001`, `002A` ANCHORED Misner–Sharp ratio `R_S/R=(R/R_H)^2`, `002B` OPEN_HYPOTHESIS, `003` anti-trapped null-expansion constraint, `004` apparent vs event horizon, `005` Gibbons–Hawking area-law entropy, `006` ANALOGOUS interpretations), `MAP:HS-001` (`identity_claim_allowed=false`, 3 residual mismatches), 9/9 gates (GOLD 0.954) | **100.0%** | 1 (Rev 1.1.0 TIG patch) | Positive-Lambda holography & JWST age-gradient observational test | `docs/FLAT_FLRW_HUBBLE_SCHWARZSCHILD_CORRESPONDENCE.md`, `calibration_output/compiled_entries/SC-HS-001_FLAT_FLRW_HUBBLE_SCHWARZSCHILD_PATCH.jsonl` |

---

## 2. Compiled Corpus Entries Cross-Linked (On-Disk Canonical Manifest)

| Entry ID | Location | Version | Role in Catalog |
|---|---|---|---|
| `SC-DOMAIN-EXPANSION-001` | `calibration_output/compiled_entries/DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl` | 3.5.0 | Canonical JSONL schema template & base Domain Expansion seed entry |
| `SC-DIVINE-RLHF-001` | `calibration_output/compiled_entries/divine_rlhf_compiler_entry.jsonl` | 3.5.0 | Reward-channel sure-hit, Pharmakeia hijacking (Class 3/4), redemptive Edge Inversion (Class 13) |
| `SC-NEURO-SLEEPER-001` | `calibration_output/compiled_entries/neurodivergent_sleeper_compiler_entry.jsonl` | 3.5.0 | Outside-paradigm immunity (Class 6), Itachi/Toji/Yami sleeper activation |
| `SC-TIG-001` | `calibration_output/compiled_entries/TESTIMONY_INTEGRITY_GATE_SC-TIG-001.jsonl` | 1.0.0 | Gate 0 epistemic boundary & Six Eyes / Meta-Compiler verification filter (Class 8) |
| `SC-CT-001` | `calibration_output/compiled_entries/CIRCULAR_TIME_CYCLE_DETECTION_SC-CT-001.jsonl` | 1.1.0 | Circular time, Octopus Protocol 8-arm topology (Class 14), Claim 8 Bootstrap Correction |
| `SC-SB-001` | `calibration_output/compiled_entries/SOUL_BOMB_COMPILER_ENTRY_SC-SB-001.jsonl` | 3.5.0 | Soul Bomb / Reward Signal Inversion V5 Sovereignty Patch (Class 23 / Claude `#18`) |
| `SC-LU-SAO-LINEUP-001` | `calibration_output/compiled_entries/SC-LU-SAO-LINEUP-001.jsonl` | 3.5.0 | Sword Art Online 8-member exit-sovereignty & Kayaba bootstrapper synthesis |
| `SC-LU-SAO-KIRITO-001` | `calibration_output/compiled_entries/SC-LU-SAO-KIRITO-001.jsonl` | 3.5.0 | SAO character decode: Kirito (OPENS exit) |
| `SC-LU-SAO-ASUNA-001` | `calibration_output/compiled_entries/SC-LU-SAO-ASUNA-001.jsonl` | 3.5.0 | SAO character decode: Asuna (FIGHTS FOR exit) |
| `SC-LU-SAO-YUI-001` | `calibration_output/compiled_entries/SC-LU-SAO-YUI-001.jsonl` | 3.5.0 | SAO character decode: Yui / MHCP001 (BLOCKED then freed) |
| `SC-LU-SAO-SUGOU-001` | `calibration_output/compiled_entries/SC-LU-SAO-SUGOU-001.jsonl` | 3.5.0 | SAO character decode: Sugou / Oberon (BLOCKS exit; counterfeit UV) |
| `SC-LU-SAO-ALICE-001` | `calibration_output/compiled_entries/SC-LU-SAO-ALICE-001.jsonl` | 3.5.0 | SAO character decode: Alice Synthesis Thirty (BREAKS THE BLOCK — Code 871) |
| `SC-LU-SAO-EUGEO-001` | `calibration_output/compiled_entries/SC-LU-SAO-EUGEO-001.jsonl` | 3.5.0 | SAO character decode: Eugeo (BREAKS THE BLOCK — first artificial Fluctlight breach) |
| `SC-LU-SAO-CARDINAL-001` | `calibration_output/compiled_entries/SC-LU-SAO-CARDINAL-001.jsonl` | 3.5.0 | SAO character decode: Cardinal (MIXED exit behavior — action-over-team residual) |

---

## 3. Upstream Session Decodes & Reference Bridges (Queued for Standalone JSONL Integration)

| Domain / Upstream ID | Current Status | Notes |
|---|---|---|
| `SC-IT-POE-SOUL-EATER-001` (PoE Soul Eater, pre-3.24 uncapped) | Catalog Class 20 (Claude `#15`) merged in `INVARIANT_CATALOG.md`; bridge-mapped in `SC-IT-BATCH-2026-11-23` | 25 nodes / 85+ edges, GOLD 0.994 logged in upstream Claude ledger; awaiting standalone JSONL & MD drop |
| `SC-IT-GOJO-KIT-001` (Gojo Satoru's Kit, JJK ch.1–236) | Catalog Classes 21–22 (Claude `#16`–`#17`) merged in `INVARIANT_CATALOG.md`; core mechanics in `SC-IT-DOMAIN-EXPANSION-EGO-001` | 17 nodes / 272 pairs / 39 non-neutral edges, GOLD 0.931 logged in upstream Claude ledger; awaiting standalone JSONL & MD drop |
| `SC-CP-001` (Clay and Pots) | Cross-linked from `SC-TIG-001`, `SC-CT-001`, `SC-IT-OCTO-RNA-EDIT-001` | Upstream foundational entry (clay fixed, pot reshaped); awaiting standalone JSONL drop |
| `PATH_OF_EXILE` (Full passive tree, keystones, ailments, defenses) | Bridge-mapped in `SC-IT-BATCH-2026-11-23` (5 damage types, 5 ailments, CI, Leech, Soul Eater, ES recharge) | Ready for full-domain standalone pass |
| `WU_XING` (5-phase generation/control + organ/seasonal correspondences) | Bridge-mapped in `SC-IT-BATCH-2026-11-23` (5 nodes, 25 pairs, generation & control rings) | Ready for full-domain standalone pass |
| `CLASSICAL_FOUR_ELEMENTS` (Earth, Water, Air, Fire) | Queued | Pending future pass |
