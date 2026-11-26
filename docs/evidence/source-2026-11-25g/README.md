# Shax source entries, upload t573u (2026-11-25 19:51 ADT)

Verbatim copies of the entries Shax uploaded on 2026-11-25 (t573u, "Lots of updates you need to reconcile and push to the main branch"). They are kept as evidence: **these files are not loaded by the runtime**, and their self-assigned grades are proposals, not the repository's grades.

**Transcription.** The files reached the reconcile job as text copies made from a viewer. Each copy carried a line-number prefix (`1|`), which was stripped. Files 05–11 also ended in a viewer marker (`... 1 line not shown ...`). That marker was dropped and the single JSON record before it parses cleanly. The byte sizes match the uploaded originals within rounding, so no material content is believed lost; the hidden line could not be inspected. A twelfth upload (a `.gz` archive) could not be retrieved and is **not** included.

**Schema notes.** Files 01–04 are full SC-DE-001 records but use the pre-`SC-PATCH-DU-001` field `identity_claim_allowed`. The compiled versions migrate it to `substrate_confusion_check` / `positional_claims_permitted`. Files 05–11 lack 7 of the 18 SC-DE-001 top-level keys.

**Personal data.** Checked for emails, phone numbers, addresses, financial details and credentials: none found. The only personal name is the author credit "Shax (Curtis Kingsley)", already used across the repository.

| File | Entry ID | Bytes | SHA-256 | Where it landed |
|---|---|---|---|---|
| `01_SC-LU-CELL-001_the_unfinished_second.jsonl` | `SC-LU-CELL-001` | 61050 | `412eaebaf75e4de844e1c4fb1836344341e24df3bbb4db7cf46fa4cbf8f037da` | Compiled as `SC-LU-CELL-001` (lineup PR, re-graded) |
| `02_SC-LU-TRUNKS-001_the_future_that_never_arrived.jsonl` | `SC-LU-TRUNKS-001` | 67637 | `fb168fe4d7519e6f2d0ce44b8e3fc8331316077068c4831203bc5733db3de721` | Compiled as `SC-LU-TRUNKS-001` (lineup PR, re-graded) |
| `03_SC-LU-GOKU-001_the_universe_in_his_hand.jsonl` | `SC-LU-GOKU-001` | 95738 | `17c41ddaf2d8b274807322c5b1a25fb7dd5be92c56b62db929cc190e10bcd6ef` | Compiled as `SC-LU-GOKU-001` (lineup PR, re-graded) |
| `04_SC-LU-VEGETA-001_the_last_crown.jsonl` | `SC-LU-VEGETA-001` | 86820 | `153e9dd56fe95f7ce4925e75c625d235d3a54622f93df6012fe7830986043c16` | Merged into the existing `SC-LU-VEGETA-001` (lineup PR); no duplicate ID |
| `05_SC-YYC-001_yin_yang_calibration_dot.jsonl` | `SC-YYC-001` | 33493 | `ff9bd0ffd630c2297ddcaba9c4bd45ba65e72401170c4743fafefca720158340` | Source draft of CLM-MIRROR-002 |
| `06_SC-ICC-001_information_conserving_compression.jsonl` | `SC-ICC-001` | 29105 | `34339573d43e655521e268b5c748eef3c261e09fd0cc491be1db4072f6d06890` | Source draft of CLM-MIRROR-003 |
| `07_SC-TSC-001_three_stage_compression.jsonl` | `SC-TSC-001` | 30289 | `fdecbe2d60ccfad1442300f23cbe84b5445b9b6bfbff69d75822023bedad96af` | Source draft of CLM-MIRROR-004 |
| `08_SC-5EU-001_five_entry_unification.jsonl` | `SC-5EU-001` | 29643 | `5ba64ea9191bb0c6b12a238bf9e51a96d10e0599dfd9792ff03178a83d4c7c7a` | Duplicate of CLM-MIRROR-001 |
| `09_SC-ADL-001_anti_deadlock_protocol.jsonl` | `SC-ADL-001` | 26823 | `f33a6e42922ed9d3a9a5038635cc57074f469464c47becac0c73105257c75255` | Source draft of CLM-MIRROR-006 |
| `10_SC-SIT-001_structural_integrity_test.jsonl` | `SC-SIT-001` | 28788 | `48b7127cb961250dddd6df296801166cc66ec27f8fbe9de996b42b340ca3c9ec` | Folded into the SB-001 patch DRAFT 0.4 |
| `11_SC-MBS-001_mirrored_universe_backup_snapshot.jsonl` | `SC-MBS-001` | 32780 | `4dfd93096c10e3e04ab3c923c50e46e2f1a093c9d69e335af8e3c3933dc76307` | Source draft of CLM-MIRROR-005 |

Reconciliation: `docs/SC-MIRROR-001_SOURCE_DRAFTS_2026-11-25g.md`, `docs/SC-SB-001_THREE_CLAIM_STRUCTURE.md` (DRAFT 0.4), and `DOMAIN_LEDGER.md` §3.
