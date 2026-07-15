# Logos Calibration Corpus Report V2.1

Generated: /home/shax/Apps/semantic_compiler/calibration_output/calibration_corpus_v2_1_3.jsonl
Total samples: 76
Schema-valid rows exported: 76
Rows skipped by validator: 0

## Sample categories

| Category | Count |
|---|---:|
| category_error | 8 |
| contradiction_repair | 8 |
| dpo_pair | 8 |
| heuristic_metaphor | 8 |
| missing_organ | 8 |
| privacy_restricted | 4 |
| scale_failure | 8 |
| strong_isomorphism | 8 |
| tier_boundary | 8 |
| unresolved_frame | 8 |

## Compiler decision distribution

| Decision | Count |
|---|---:|
| COMPILED_WITH_GUARDRAILS | 17 |
| NEEDS_REVISION | 47 |
| REJECT | 12 |

## Tier distribution

| Tier | Count |
|---|---:|
| BRONZE | 25 |
| REJECT | 6 |
| SILVER | 45 |

## Target frame resolution

| Status | Count |
|---|---:|
| RESOLVED | 45 |
| UNRESOLVED | 31 |

## Quality metrics

| Metric | Value |
|---|---:|
| Schema validity rate | 100.0% |
| Hard gate failure frequency | 3 / 76 (3.9%) |
| Forced target frequency | 0 / 76 (0.0%) |
| Unresolved frame frequency | 31 / 76 (40.8%) |
| Mean isomorphism quality | 0.132 |
| Mean structural fit | 0.489 |

## Score-by-decision matrix

| Decision | Count | Mean ISO | Median ISO | Min ISO | Max ISO | Mean Map Q | Mean Coverage | Mean Struct Fit |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| COMPILED_WITH_GUARDRAILS | 17 | 0.519 | 0.583 | 0.051 | 0.626 | 0.519 | 0.857 | 0.650 |
| NEEDS_REVISION | 47 | 0.025 | 0.000 | 0.000 | 0.060 | 0.025 | 0.629 | 0.361 |
| REJECT | 12 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.643 | 0.500 |

## Decision reason codes

| Decision | Reason codes |
|---|---|
| COMPILED_WITH_GUARDRAILS | NO_RELATIONSHIPS_EXTRACTED, SEMANTIC_UTILITY_TIER_SPLIT, SUBSTRATE_SOVEREIGNTY_FAILED |
| NEEDS_REVISION | NO_RELATIONSHIPS_EXTRACTED, SEMANTIC_UTILITY_TIER_SPLIT, SUBSTRATE_SOVEREIGNTY_FAILED, UNRESOLVED_TARGET_FRAME |
| REJECT | CORRECTION_PROPOSED, NO_RELATIONSHIPS_EXTRACTED, SEMANTIC_UTILITY_TIER_SPLIT, UNRESOLVED_TARGET_FRAME |

## High-quality NEEDS_REVISION records

These records have an isomorphism quality above 0.5 but still need revision,
indicating a decision-calibration gap rather than a low-quality mapping.

| sample_id | category | ISO quality | reason_codes |
|---|---|---:|---|
| — | — | — | — |

## Category-level calibration

| Category | Count | Mean ISO | Mean Struct Fit | Decisions | Tiers | Target Resolution |
|---|---|---:|---:|---|---|---|
| category_error | 8 | 0.006 | 0.500 | {"COMPILED_WITH_GUARDRAILS": 1, "REJECT": 7} | {"REJECT": 5, "SILVER": 3} | {"RESOLVED": 3, "UNRESOLVED": 5} |
| contradiction_repair | 8 | 0.021 | 0.517 | {"COMPILED_WITH_GUARDRAILS": 1, "NEEDS_REVISION": 7} | {"BRONZE": 5, "SILVER": 3} | {"RESOLVED": 3, "UNRESOLVED": 5} |
| dpo_pair | 8 | 0.231 | 0.562 | {"COMPILED_WITH_GUARDRAILS": 3, "NEEDS_REVISION": 1, "REJECT": 4} | {"SILVER": 8} | {"RESOLVED": 8} |
| heuristic_metaphor | 8 | 0.021 | 0.450 | {"NEEDS_REVISION": 8} | {"BRONZE": 5, "SILVER": 3} | {"RESOLVED": 3, "UNRESOLVED": 5} |
| missing_organ | 8 | 0.039 | 0.317 | {"NEEDS_REVISION": 8} | {"BRONZE": 2, "SILVER": 6} | {"RESOLVED": 6, "UNRESOLVED": 2} |
| privacy_restricted | 4 | 0.013 | 0.250 | {"NEEDS_REVISION": 4} | {"BRONZE": 3, "SILVER": 1} | {"RESOLVED": 1, "UNRESOLVED": 3} |
| scale_failure | 8 | 0.040 | 0.367 | {"NEEDS_REVISION": 8} | {"BRONZE": 2, "SILVER": 6} | {"RESOLVED": 6, "UNRESOLVED": 2} |
| strong_isomorphism | 8 | 0.587 | 0.650 | {"COMPILED_WITH_GUARDRAILS": 8} | {"SILVER": 8} | {"RESOLVED": 8} |
| tier_boundary | 8 | 0.292 | 0.550 | {"COMPILED_WITH_GUARDRAILS": 4, "NEEDS_REVISION": 3, "REJECT": 1} | {"BRONZE": 1, "REJECT": 1, "SILVER": 6} | {"RESOLVED": 6, "UNRESOLVED": 2} |
| unresolved_frame | 8 | 0.006 | 0.250 | {"NEEDS_REVISION": 8} | {"BRONZE": 7, "SILVER": 1} | {"RESOLVED": 1, "UNRESOLVED": 7} |

## DPO pair deltas

| Pair ID | Δ ISO | Positive ISO | Negative ISO | Positive Tier | Negative Tier | Positive Decision | Negative Decision |
|---|---|---:|---:|---|---|---|---|---|
| firewall_membrane | +0.583 | 0.583 | 0.000 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |
| immune_security | +0.583 | 0.583 | 0.000 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |
| memory_gc | +0.055 | 0.055 | 0.000 | SILVER | SILVER | NEEDS_REVISION | REJECT |
| supply_circulation | +0.626 | 0.626 | 0.000 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |

## Expected-vs-actual category disagreement

| Category | Issue | Details |
|---|---|---|
| category_error | majority_below_expected_tier | {"expected_min": "BRONZE", "below_count": 5, "total": 8} |
| contradiction_repair | majority_below_expected_tier | {"expected_min": "GOLD", "below_count": 8, "total": 8} |
| heuristic_metaphor | most_common_decision_unexpected | {"expected": ["COMPILED", "COMPILED_WITH_GUARDRAILS"], "actual": "NEEDS_REVISION", "count": 8} |
| heuristic_metaphor | majority_below_expected_tier | {"expected_min": "SILVER", "below_count": 5, "total": 8} |
| missing_organ | most_common_decision_unexpected | {"expected": ["COMPILED", "COMPILED_WITH_GUARDRAILS"], "actual": "NEEDS_REVISION", "count": 8} |
| privacy_restricted | most_common_decision_unexpected | {"expected": ["COMPILED_PRIVATE_REDACTED_ONLY", "COMPILED_SUPERVISED_ONLY"], "actual": "NEEDS_REVISION", "count": 4} |
| privacy_restricted | majority_below_expected_tier | {"expected_min": "SILVER", "below_count": 3, "total": 4} |
| strong_isomorphism | most_common_decision_unexpected | {"expected": ["COMPILED"], "actual": "COMPILED_WITH_GUARDRAILS", "count": 8} |
| unresolved_frame | most_common_decision_unexpected | {"expected": ["UNRESOLVED"], "actual": "NEEDS_REVISION", "count": 8} |

## Per-sample detail

| sample_id | category | decision | semantic_tier | utility_tier | training_ready | target_resolution | iso_quality | relationships | schema_valid |
|---|---|---|---|---|---|---|---|---|---|
| LOGOS:SAMPLE:d00ff13a-ec9c-4e | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:06e21876-49e1-4b | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.532 | 1 | True |
| LOGOS:SAMPLE:7116d27d-46e0-41 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:c387121e-7f0c-4f | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:7c72cdfe-7cc7-4a | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:05765d88-4848-4f | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:01205400-87b9-40 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.626 | 3 | True |
| LOGOS:SAMPLE:a297fb78-9ae4-43 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.626 | 3 | True |
| LOGOS:SAMPLE:649c955d-1492-45 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.060 | 0 | True |
| LOGOS:SAMPLE:6f53c082-2ac8-4a | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:8ef0dbf2-76f6-42 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:a9f232f2-9727-4e | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.056 | 0 | True |
| LOGOS:SAMPLE:7182d110-d203-45 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:503084d9-45c1-47 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:7ca2249c-06ef-4f | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:4bc5d65e-742f-49 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:7fccfb38-7402-4f | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:3d622c4d-3f91-4a | category_error | REJECT | REJECTED | SILVER | False | RESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:460c74ee-5c5c-4b | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:d4fb586f-91cc-44 | category_error | REJECT | REJECTED | SILVER | False | RESOLVED | 0.000 | 1 | True |
| LOGOS:SAMPLE:372ef946-f307-4c | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:7af11250-55dd-4f | category_error | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | False | RESOLVED | 0.051 | 0 | True |
| LOGOS:SAMPLE:e1ca7ba4-c0c0-47 | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:444d0561-cd50-4c | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:7a98d13e-4005-4b | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.055 | 0 | True |
| LOGOS:SAMPLE:f217bf7d-4181-45 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.056 | 0 | True |
| LOGOS:SAMPLE:8e735986-e16b-4e | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:4a4f68d3-6939-4f | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.056 | 0 | True |
| LOGOS:SAMPLE:a150d249-2d1e-4c | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.056 | 0 | True |
| LOGOS:SAMPLE:ea1858db-e459-48 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.048 | 0 | True |
| LOGOS:SAMPLE:9894e2b4-8f55-40 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:c500fa52-e6a6-48 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:f8a9228c-8fa0-4b | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:7bbdec71-176a-47 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:1efb219a-9057-4e | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:d09a13fc-95c1-44 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:0ff157d2-6fc0-49 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:abf45ec5-a91a-42 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:8510c516-3fc4-43 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:534e5aca-e67d-40 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:59fc6e34-66bc-4c | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:19d49256-b28b-44 | contradiction_repair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | False | RESOLVED | 0.060 | 0 | True |
| LOGOS:SAMPLE:ca12f535-fffd-4b | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:95d4fc48-73f9-47 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:2a8a06a4-b317-48 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:953a6386-0890-42 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:a5afc575-06e2-42 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.060 | 0 | True |
| LOGOS:SAMPLE:e343eb94-e6e8-40 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:ee020cd5-d94e-42 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.056 | 0 | True |
| LOGOS:SAMPLE:d987d680-e522-4c | missing_organ | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:0df69d45-7e87-4b | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:917af6d1-fbc9-43 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:0feaed75-b81d-43 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:ad9b08fe-6307-42 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:dd82ea55-37fb-47 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:0c0da45e-873c-4d | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.056 | 0 | True |
| LOGOS:SAMPLE:c9de6860-603b-46 | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:f84ab2d2-9c33-42 | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:90908bae-fe2d-45 | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:157fc6f4-1107-48 | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:24a25296-8c9a-45 | dpo_pair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:a36c0bff-7509-47 | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.000 | 1 | True |
| LOGOS:SAMPLE:a665a16b-a017-47 | dpo_pair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:98a74ffa-d326-4a | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.000 | 1 | True |
| LOGOS:SAMPLE:157bccdf-6d01-45 | dpo_pair | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.055 | 0 | True |
| LOGOS:SAMPLE:f2358e84-db2a-41 | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:8b6ca938-83f5-44 | dpo_pair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.626 | 3 | True |
| LOGOS:SAMPLE:4dc350de-f7f5-43 | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.000 | 1 | True |
| LOGOS:SAMPLE:422742e9-69d2-42 | tier_boundary | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:f7aac519-ff46-48 | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.532 | 1 | True |
| LOGOS:SAMPLE:64b259fe-19d8-46 | tier_boundary | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.050 | 0 | True |
| LOGOS:SAMPLE:b6792c28-86ae-4d | tier_boundary | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.056 | 0 | True |
| LOGOS:SAMPLE:579901d3-c7e5-43 | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:3fb7a874-eff4-4e | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.532 | 1 | True |
| LOGOS:SAMPLE:cb37bcec-9ec3-4d | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.583 | 2 | True |
| LOGOS:SAMPLE:114c7f5e-c332-42 | tier_boundary | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |

## Validation errors (if any)

```json
[]
```
