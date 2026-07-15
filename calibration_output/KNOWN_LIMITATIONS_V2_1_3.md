# Known Limitations — Semantic Compiler V2.1.3

## Approved scope

- Canonical compiler freeze.
- Controlled corpus production.
- Deduplicated, human-reviewed SFT pilot dataset.

## Not approved for this release

- Production DPO training: the `memory_gc` pair remains diagnostic-only.
- Missing-organ hard-gate enforcement: findings remain advisory.
- Autonomous Gold/Diamond promotion: all positive mappings are currently
  `COMPILED_WITH_GUARDRAILS` pending explicit invariants, negative tests,
  residual analysis, and full gate clearance.

## Quarantined records

Three residual disputed cases (and their duplicates) are quarantined in both
`calibration_corpus_v2_1_3.jsonl` and `release_candidate_corpus_v2_1_3.jsonl`:

- `LOGOS:SAMPLE:dc51ef2d-301d-43` — incomplete computer system
- `LOGOS:SAMPLE:0dc86964-7ec3-45` — incomplete society system
- `LOGOS:SAMPLE:c1f4f30c-10c5-4e` — complete cell listing

They are marked:
- `decision.status` = `NEEDS_REVISION`
- `quality.training_ready` = `false`
- `quality.dataset_utility_tier` = `DIAGNOSTIC`
- `review.consensus.status` = `QUARANTINED_PENDING_ADJUDICATION`

They are excluded from SFT positives, DPO chosen records, Gold candidates, and
release acceptance statistics.

## Score/modeling notes

- Strong-isomorphism analogies are intentionally retained as
  `COMPILED_WITH_GUARDRAILS` in V2.1.3.
- The `memory_gc` DPO pair has a weak delta because the positive sample is
  still `NEEDS_REVISION`; it is retained as a diagnostic regression sample.
- The score plateau is broken: distinct ISO scores now range across strong
  analogies (~0.58–0.63), underspecified cases (~0.00–0.06), and rejected
  cases (0.00).

## Next release targets

- Promote strong isomorphisms to plain `COMPILED` after explicit invariant,
  negative-test, residual, and gate requirements are formalized.
- Expand missing-organ benchmark and enable hard-gate enforcement.
- Repair the `memory_gc` extraction path and re-enable production DPO export.
