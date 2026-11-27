# Shax source, t610u (2026-11-27): SC-TOL-001 rc6 decisions

| File | What it is | Bytes | SHA-256 |
|---|---|---|---|
| `t610u_message_body.txt` | Shax's t610u message, verbatim as relayed to the compiler. One header line was added. The Markdown escapes (`\\text`, `1\.`) are kept exactly as received. It decides the two items SC-TOL-001 left open. | 4046 | `7281f8a6adffd8d2687e348bf00cf24c4a19b6f918ac7e2dad8a6af2290976a2` |

**Attribution.** The decisions are Shax's. The message does not say whether he wrote the wording himself or adapted it from an assistant conversation, so the wording is not attributed further.

**What it decides.**
- **D1, ACCEPT.** A failing child taints the parent's current compilation only. The taint is scoped, keeps the child's provenance, and grants no authority.
- **D2, RECLASSIFY.** T2 gains `LIVING_OBSERVED`, `SELF_MAINTENANCE_UNVERIFIED`, `AUTOPOIESIS_EMPIRICAL` and `INERT_TAXONOMY`. Neither of the first two satisfies T2.
- **Principle.** Structural validity, biological status and governance authority are separate dimensions.
- Implemented as rc6 in `tests/reference/sc_tol_001/compiler.py`. See `docs/SC-TOL-001_TREE_OF_LIFE_STRUCTURAL_COMPILER.md` section 5a.

**This file is evidence.** The runtime does not load it.

**Personal data.** Before commit, the file was scanned for personal names and family names, birthdays, emails, phone numbers, addresses, URLs, and credentials. None were found, and **no redaction was made**.
