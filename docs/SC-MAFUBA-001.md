# SC-MAFUBA-001 — Dimensional Containment and Information-Flow Integrity

**Current candidate:** `v1.1.0-rc1` (`docs/SC-MAFUBA-001_v1.1.0-rc1.md`)
**Historical artifact:** `v1.0.0` (`docs/SC-MAFUBA-001_v1.0.0.md`) — immutable; do not edit in place
**Classification:** Proposed GOLD invariant (`gold_awarded: false`)
**Status:** Pending implementation and validation. Not compiled, not runtime-loaded, no GOLD award.
**Date:** 2026-11-25
**Source:** Shax, t574u (locked v1.0.0 specification and engineering audit), t575u, t576u (unified 11-item directive for v1.1.0-rc1)
**Target:** `semantic_compiler_kernel`

This directory entry is an index only. The specification text lives in the versioned files.

| Document | Role |
|---|---|
| `docs/SC-MAFUBA-001_v1.0.0.md` | Frozen v1.0.0 historical artifact (SHA-256 recorded in the draft JSONL) |
| `docs/SC-MAFUBA-001_v1.1.0-rc1.md` | Current proposed candidate; not GOLD, not implemented, unvalidated |
| `docs/SC-MAFUBA-001_IMPLEMENTATION_AUDIT.md` | Why Hannah's Section 2–6 Python reference code is not committed |
| `docs/SC-MAFUBA-001_GAP_REPORT.md` | Defect-to-fix map, proposed module structure, test plan, outstanding assumptions |
| `docs/evidence/sc-mafuba-001/sc_mafuba_001.jsonl` | Draft registry (parent + 001A–001D). Not on the compiled runtime path |
| `docs/evidence/sc-mafuba-001/manifests/` | Disturbance, resource, and sink config templates |
| `tests/reference/sc_mafuba_001/` | Dependency-light reference helpers for offline tests. Not kernel enforcement |

Do not treat beauty of the derivation as evidence. Do not mark this GOLD until the linked tests exist, run under adversarial conditions, and are recorded with provenance.
