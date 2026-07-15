# Calibration V2.1.1 Diff Report

**Generated:** 2026-07-14T15:37:52.313551Z

## Code changes

1. `core/dataset.py:_mapping_scores` — separated mapping_quality, assessment_coverage, confidence; unassessed dimensions are null.
2. `core/dataset.py:_isomorphism_analysis` — added aggregate mapping_quality and assessment_coverage.
3. `translation/fractal.py:identify_missing_departments` — scope-aware; UNOBSERVED for fragments.
4. `core/pipeline.py:infer_missing_functions` — determines completeness scope from mode.
5. `extraction/evidence.py:extract_evidence_inventory` — first-person recollection detection only.
6. `core/decisions.py:decide_packet` — removed CRITICAL privacy as semantic decision driver.
7. `core/dataset.py:_build_privacy` — added training_disposition and export_disposition.
8. `core/dataset.py:_target_resolution` — added mapping_direction and direction_confidence.
9. `core/dataset.py:_gate_record` — applicable passes always include a reason.
10. `gates/corpus_completeness.py` — new bounded corpus-completeness gate.

## Metric shifts

| Metric | Before | After |
|---|---|---|
| Mean isomorphism quality | 0.015 | 0.747 |
| Mean mapping quality | — | 0.747 |
| Mean assessment coverage | — | 0.384 |
| Mean structural fit | 0.375 | 0.178 |

### Decision distribution

| Decision | Before | After |
|---|---|---|
| COMPILED_PRIVATE_REDACTED_ONLY | 1 | 0 |
| COMPILED_WITH_GUARDRAILS | 8 | 8 |
| NEEDS_REVISION | 67 | 68 |

### Tier distribution

| Tier | Before | After |
|---|---|---|
| BRONZE | 40 | 40 |
| SILVER | 36 | 36 |

## Remaining blockers

1. Skeleton extraction still misses actors/objects in simple analogies.
2. Decision engine rejects high-quality samples due to low structural_fit.
3. Contradiction-repair does not emit explicit `repair` objects.
4. Relationship extraction is empty for inputs with explicit verbs.

## Tests

- Full test suite: 48 tests pass.
- New tests added for missing-organ scope and corpus-completeness gate.

## Recommendation

Do not freeze V2.1.0. Proceed with skeleton/relationship extraction improvements and a second calibration pass.
