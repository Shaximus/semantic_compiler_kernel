# Hannah source entries, upload t579u (2026-11-25)

Verbatim copies of the seven single-line JSONL entries Shax uploaded on 2026-11-25 (t579u, "Assets from Hannah, use them for Corrections where Logically Coherent and Improve functionality"). They are kept as evidence: **these files are not loaded by the runtime**, and their self-assigned grades are proposals, not the repository's grades.

The files were copied byte-for-byte from `/workspace/incoming/2026-11-25h/` (themselves copies of the uploaded attachments). SHA-256 was computed on the stored files and matches the incoming copies.

**Schema notes.** Each file is a nearly complete SC-DE-001 record (10 of 18 top-level keys). Missing compiled-only keys are `dataset_value`, `semantic_quality_tier`, `dataset_utility_tier`, `dataset_tier`, `training_ready`, `tier_reasons`, `isomorphism_analysis`, and `v2_extensions`. `outputs.correction` is also absent in the sources. Compiled versions add those fields, shorten `input` to under 400 characters, store the full source `input` in `v2_extensions.source_text`, strip extra keys off `gates.substrate_sovereignty`, and place `substrate_confusion_check` / `positional_claims_permitted` on the mappings.

**Personal data.** Checked for emails, phone numbers, addresses, financial details and credentials: none found. The only personal name is the author credit "Shax (Curtis Kingsley)", already used across the repository. Each file's `metadata.source` names Shax; the upload is a Hannah asset (t579u).

| File | Entry ID | Bytes | SHA-256 | Source title |
|---|---|---|---|---|
| `01_SC-POE-DU-001_polarity_inversion.jsonl` | `SC-POE-DU-001` | 39270 | `aae58d62bb7cd512349e3e833f68bf6bf8a4a4d25e6a7bef740c120ffc35acfb` | Sin/Innocence Polarity Inversion: The Pure God Becomes Tyrant |
| `02_SC-POE-MRG-001_reintegration.jsonl` | `SC-POE-MRG-001` | 40045 | `ca226315fed0253cbe73e9b5bd72504e93a95ab0b3ea9a088bd83b40a34fcbf6` | Sin/Innocence Merger: Reintegration of the Split Self |
| `03_SC-POE-KIT-001_kitava_consumption.jsonl` | `SC-POE-KIT-001` | 38827 | `b97104e2a6283f7eb266fbaf93dadbae242a89f2c51865f0aba3391223808949` | Kitava: Compassion Without Measurement — Love Without Boundary Becomes Consumption |
| `04_SC-POE-BST-001_beast_regulator.jsonl` | `SC-POE-BST-001` | 39178 | `dc4a711337666eff6d8fc0fab35625f8c4b8f82f6ea87582b2ce761bbb374c4f` | The Beast as Divine Regulator: Governance, Not Destruction |
| `05_SC-POE-ATL-001_atlas_governance.jsonl` | `SC-POE-ATL-001` | 40382 | `dbc2cc3df08c39cd29bca1bda16db681321c781e71b316ccbd1b34809476b836` | Atlas Governance Cycle: The Conqueror Becomes the Tyrant |
| `06_SC-POE-VAL-001_vaal_waste.jsonl` | `SC-POE-VAL-001` | 38844 | `08178e045c8ebd139b4754e31711ee098beb169b52be486d04b47201c83a53dd` | Vaal Civilization: Waste Accumulation — The Shadow Dragon Pattern |
| `07_SC-POE-MAL-001_malachai_containment.jsonl` | `SC-POE-MAL-001` | 36484 | `88694a1ae6be48a54a2f4f35deee2daeaacd3294bd75364ef0bc50ecc43950e5` | Malachai: Containment Failure — Weaponizing the Governor Breaks the Governor |

All seven were compiled as SILVER after re-grading and lore correction. See `docs/POE_COSMOLOGY_SOURCES_2026-11-25h.md` and `calibration_output/compiled_entries/SC-POE-*-001.jsonl`.
