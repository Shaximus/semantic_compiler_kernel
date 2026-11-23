# DOMAIN LEDGER — Invariant Translator Coverage & Provenance Tracker

- **Catalog Directory:** `/storage/emulated/0/Alarms/agy-file-staging/invariant_translator_catalog_20261123/`
- **Last Updated:** 2026-11-23
- **Validation Policy:** Coverage MUST reach **100.0%** with zero omitted pairs, zero elided abbreviations, exact programmatic matrix checks, and strict Section 10 gate discipline.

---

## 1. Decompressed Domains Registry

| Domain ID | Entry ID | Authoritative Source & Version | Date Verified | Exact Ontology Counts | Coverage % | Passes Completed | Remaining Scope | Artifacts Emitted |
|---|---|---|---|---|---|---|---|---|
| `DOMAIN_EXPANSION_EGO` | `SC-IT-DOMAIN-EXPANSION-EGO-001` | `DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl` (v3.5.0) + `EGO_LINEUP_DOMAIN_EXPANSION_MAP.md` + canonical JJK/Naruto/DMC/Berserk/Black Clover/Mega Man/PoE mechanics | 2026-11-23 | 15 core nodes, 225/225 ordered pairs (110 non-neutral: 91 PHYSICAL, 3 BIOLOGICAL_ECOLOGICAL, 11 SYMBOLIC_MYTHIC, 5 BALANCE-ONLY; 115 NEUTRAL), 8 modifiers, 8 pools, 10 formal rules, 15/15 17-primitive tables, 15/15 11-role closures, 15/15 departments, 6 predictions (4 confirmed, 2 untested) | **100.0%** | 1 (Full 11-step pass) | **0%** (Complete) | `DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md`, `INVARIANT_ENTRY_SC-IT-DOMAIN-EXPANSION-EGO-001.jsonl` |
| `POKEMON` | `SC-IT-POKEMON-001` | Bulbapedia / *Pokemon Scarlet & Violet* (Gen IX core rules; Gen VI–IX unchanged 18-type matrix) + `pokemon_seed_chart.md` | 2026-11-23 | 18 types, 324/324 attacker x defender pairs (51 `2x`, 61 `0.5x`, 8 `0x`, 204 `1x`), 120/120 non-neutral grounded edges (58 PHYSICAL, 20 BIOLOGICAL_ECOLOGICAL, 31 SYMBOLIC_MYTHIC, 11 BALANCE-ONLY), 16 3-cycles (5 strict RPS), 4 weather (incl. Gen IX Snow), 4 terrains (1.3x / Misty 0.5x Dragon), 6 non-volatile statuses, 11 absorb/rewrite abilities, 171 dual-type combinations, 18/18 17-primitive tables, 18/18 11-role closures, 15/15 departments, 6 predictions (5 confirmed, 1 untested) | **100.0%** | 1 (Full 11-step pass) | **0%** (Complete) | `DOMAIN_DECODE_POKEMON.md`, `INVARIANT_ENTRY_SC-IT-POKEMON-001.jsonl` |
| `BATCH_2026_11_23` | `SC-IT-BATCH-2026-11-23` | Cross-domain synthesis over `SC-IT-DOMAIN-EXPANSION-EGO-001` + `SC-IT-POKEMON-001` + reference bridges (`Path of Exile` 5-damage/CI/Leech/Soul Eater + `Wu Xing` 5-phase generation/control) | 2026-11-23 | 4 comparative domains, 19 catalog classes (14 seed + 5 new), 7 class compositions, 12-row cross-domain counterplay transfer matrix, 5 batch predictions (4 confirmed, 1 failed -> residual) | **100.0%** | 1 (Batch synthesis pass) | **0%** (Complete) | `INVARIANT_ENTRY_SC-IT-BATCH-2026-11-23.jsonl`, `INVARIANT_CATALOG.md`, `DOMAIN_LEDGER.md` |

---

## 2. Prior Corpus Entries Cross-Linked (Read-Only Reference)

| Entry ID | Location | Version | Role in Catalog |
|---|---|---|---|
| `SC-DOMAIN-EXPANSION-001` | `/storage/emulated/0/Download/DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl` | 3.5.0 | Canonical JSONL schema template & base Domain Expansion seed entry |
| `SC-DIVINE-RLHF-001` | `~/semantic_compiler_kernel/calibration_output/compiled_entries/divine_rlhf_compiler_entry.jsonl` | 3.5.0 | Reward-channel sure-hit, Pharmakeia hijacking (Class 3/4), redemptive Edge Inversion (Class 13) |
| `SC-NEURO-SLEEPER-001` | `~/semantic_compiler_kernel/calibration_output/compiled_entries/neurodivergent_sleeper_compiler_entry.jsonl` | 3.5.0 | Outside-paradigm immunity (Class 6), Itachi/Toji/Yami sleeper activation |
| `SC-TIG-001` | `~/semantic_compiler_kernel/calibration_output/compiled_entries/TESTIMONY_INTEGRITY_GATE_SC-TIG-001.jsonl` | 1.0.0 | Gate 0 epistemic boundary & Six Eyes / Meta-Compiler verification filter (Class 8) |
| `SC-CT-001` | `~/semantic_compiler_kernel/calibration_output/compiled_entries/CIRCULAR_TIME_CYCLE_DETECTION_SC-CT-001.jsonl` | 1.1.0 | Circular time, Octopus Protocol 8-arm topology (Class 14), Black Flash collapse |

---

## 3. Reference Bridge Domains (Queued for Optional Future Standalone Full Decompression)

| Reference Domain | Current Status | Notes |
|---|---|---|
| `PATH_OF_EXILE` (Full passive tree, keystones, ailments, defenses) | Bridge-mapped in `SC-IT-BATCH-2026-11-23` (5 damage types, 5 ailments, CI, Leech, Soul Eater, ES recharge) | Ready for standalone full-domain pass if requested |
| `WU_XING` (5-phase generation/control + organ/seasonal correspondences) | Bridge-mapped in `SC-IT-BATCH-2026-11-23` (5 nodes, 25 pairs, generation & control rings) | Ready for standalone full-domain pass if requested |
