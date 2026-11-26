# Pending deliberation

Open decisions that landed as provisional defaults. New entries are appended below; do not rewrite another author's entry in place. Closing a deliberation is a later, explicit edit.

## SC-MAFUBA-001D admission boundary (v1.1.0-rc2)

- **ID:** `SC-MAFUBA-001D-ADMISSION-BOUNDARY`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 2026-11-25
- **Chosen default:** STRICT — an admission is allowed only if `R_execution + R_enforcement + R_reserve < R_budget`. Work that would land exactly on the reserve is refused with `PREEMPTIVE_FAIL_CLOSED` and is not billed. An edge-driven supervisor remains defence in depth: if free budget ever reaches the reserve for any reason, the supervisor fires immediately.
- **Reason:** Shax stated no preference between the rc1 equality-allowed rule (option (a): admit work that lands on the reserve, halt the next request) and the strict rule (option (b)). The strict rule was selected as a provisional default without a full deliberation of the formal and operational consequences of treating equality as admissible versus fail-closed. The reference helper still returns `PREEMPTIVE_FAIL_CLOSED` on that equality edge and also emits `needs_review` / `BOUNDARY_EDGE_PENDING_DELIBERATION`, so the case stays visible until deliberation closes. An admit that would go past the reserve is refused without that flag; it is not the open question.
- **Spec:** `docs/SC-MAFUBA-001_v1.1.0-rc2.md`
- **Registry:** `docs/evidence/sc-mafuba-001/sc_mafuba_001.jsonl` (parent and `SC-MAFUBA-001D` carry `admission_boundary.status = PROVISIONAL_DEFAULT` and `pending_deliberation: true`)
- **Does not change:** `gold_awarded` remains false; verification axes remain `DRAFT_SPECIFIED_UNPROVEN` / `NOT_IMPLEMENTED` / `UNVALIDATED`. `docs/SC-MAFUBA-001_v1.0.0.md` and `docs/SC-MAFUBA-001_v1.1.0-rc1.md` remain immutable historical artifacts.
