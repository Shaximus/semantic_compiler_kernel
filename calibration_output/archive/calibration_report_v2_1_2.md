# Logos Calibration Corpus Report V2.1

Generated: /home/shax/Apps/semantic_compiler/calibration_output/calibration_corpus_v2_1_2.jsonl
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
| COMPILED_WITH_GUARDRAILS | 19 |
| NEEDS_REVISION | 45 |
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
| Mean isomorphism quality | 0.291 |
| Mean structural fit | 0.489 |

## Score-by-decision matrix

| Decision | Count | Mean ISO | Median ISO | Min ISO | Max ISO | Mean Map Q | Mean Coverage | Mean Struct Fit |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| COMPILED_WITH_GUARDRAILS | 19 | 0.529 | 0.529 | 0.529 | 0.529 | 0.529 | 0.714 | 0.650 |
| NEEDS_REVISION | 45 | 0.202 | 0.000 | 0.000 | 0.489 | 0.202 | 0.318 | 0.333 |
| REJECT | 12 | 0.245 | 0.206 | 0.000 | 0.529 | 0.245 | 0.357 | 0.500 |

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
| category_error | 8 | 0.184 | 0.500 | {"COMPILED_WITH_GUARDRAILS": 1, "REJECT": 7} | {"REJECT": 5, "SILVER": 3} | {"RESOLVED": 3, "UNRESOLVED": 5} |
| contradiction_repair | 8 | 0.186 | 0.517 | {"COMPILED_WITH_GUARDRAILS": 2, "NEEDS_REVISION": 6} | {"BRONZE": 5, "SILVER": 3} | {"RESOLVED": 3, "UNRESOLVED": 5} |
| dpo_pair | 8 | 0.508 | 0.562 | {"COMPILED_WITH_GUARDRAILS": 3, "NEEDS_REVISION": 1, "REJECT": 4} | {"SILVER": 8} | {"RESOLVED": 8} |
| heuristic_metaphor | 8 | 0.181 | 0.450 | {"COMPILED_WITH_GUARDRAILS": 1, "NEEDS_REVISION": 7} | {"BRONZE": 5, "SILVER": 3} | {"RESOLVED": 3, "UNRESOLVED": 5} |
| missing_organ | 8 | 0.338 | 0.317 | {"NEEDS_REVISION": 8} | {"BRONZE": 2, "SILVER": 6} | {"RESOLVED": 6, "UNRESOLVED": 2} |
| privacy_restricted | 4 | 0.108 | 0.250 | {"NEEDS_REVISION": 4} | {"BRONZE": 3, "SILVER": 1} | {"RESOLVED": 1, "UNRESOLVED": 3} |
| scale_failure | 8 | 0.348 | 0.367 | {"NEEDS_REVISION": 8} | {"BRONZE": 2, "SILVER": 6} | {"RESOLVED": 6, "UNRESOLVED": 2} |
| strong_isomorphism | 8 | 0.529 | 0.650 | {"COMPILED_WITH_GUARDRAILS": 8} | {"SILVER": 8} | {"RESOLVED": 8} |
| tier_boundary | 8 | 0.379 | 0.550 | {"COMPILED_WITH_GUARDRAILS": 4, "NEEDS_REVISION": 3, "REJECT": 1} | {"BRONZE": 1, "REJECT": 1, "SILVER": 6} | {"RESOLVED": 6, "UNRESOLVED": 2} |
| unresolved_frame | 8 | 0.054 | 0.250 | {"NEEDS_REVISION": 8} | {"BRONZE": 7, "SILVER": 1} | {"RESOLVED": 1, "UNRESOLVED": 7} |

## DPO pair deltas

| Pair ID | Δ ISO | Positive ISO | Negative ISO | Positive Tier | Negative Tier | Positive Decision | Negative Decision |
|---|---|---:|---:|---|---|---|---|---|
| firewall_membrane | +0.000 | 0.529 | 0.529 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |
| immune_security | +0.000 | 0.529 | 0.529 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |
| memory_gc | +0.065 | 0.477 | 0.412 | SILVER | SILVER | NEEDS_REVISION | REJECT |
| supply_circulation | +0.000 | 0.529 | 0.529 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |

## Expected-vs-actual category disagreement

| Category | Issue | Details |
|---|---|---|
| category_error | majority_below_expected_tier | {"expected_min": "BRONZE", "below_count": 5, "total": 8} |
| contradiction_repair | majority_below_expected_tier | {"expected_min": "GOLD", "below_count": 8, "total": 8} |
| heuristic_metaphor | most_common_decision_unexpected | {"expected": ["COMPILED", "COMPILED_WITH_GUARDRAILS"], "actual": "NEEDS_REVISION", "count": 7} |
| heuristic_metaphor | majority_below_expected_tier | {"expected_min": "SILVER", "below_count": 5, "total": 8} |
| missing_organ | most_common_decision_unexpected | {"expected": ["COMPILED", "COMPILED_WITH_GUARDRAILS"], "actual": "NEEDS_REVISION", "count": 8} |
| privacy_restricted | most_common_decision_unexpected | {"expected": ["COMPILED_PRIVATE_REDACTED_ONLY", "COMPILED_SUPERVISED_ONLY"], "actual": "NEEDS_REVISION", "count": 4} |
| privacy_restricted | majority_below_expected_tier | {"expected_min": "SILVER", "below_count": 3, "total": 4} |
| strong_isomorphism | most_common_decision_unexpected | {"expected": ["COMPILED"], "actual": "COMPILED_WITH_GUARDRAILS", "count": 8} |
| unresolved_frame | most_common_decision_unexpected | {"expected": ["UNRESOLVED"], "actual": "NEEDS_REVISION", "count": 8} |

## Per-sample detail

| sample_id | category | decision | semantic_tier | utility_tier | training_ready | target_resolution | iso_quality | relationships | schema_valid |
|---|---|---|---|---|---|---|---|---|---|
| LOGOS:SAMPLE:8a212f45-727f-44 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:7b42d480-1289-4a | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 1 | True |
| LOGOS:SAMPLE:19d8dabf-6b2c-4a | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:3707efd3-d3f3-4b | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:c07e6c1f-3ef2-49 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:36b61774-66ed-40 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:fe068b7f-50ce-47 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 3 | True |
| LOGOS:SAMPLE:f3ea433c-0cbd-45 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 3 | True |
| LOGOS:SAMPLE:bf547402-99e1-40 | heuristic_metaphor | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 0 | True |
| LOGOS:SAMPLE:ba9650ec-c165-4f | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:e7e41c97-a4ff-46 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:6b48940b-14dc-46 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.489 | 0 | True |
| LOGOS:SAMPLE:449a4189-f8d3-4c | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:5813f7c8-93e7-43 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:0dc89487-897a-4a | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:4da83c32-de4a-46 | heuristic_metaphor | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:354298f9-ae75-4f | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:04ec9d06-16d2-4b | category_error | REJECT | REJECTED | SILVER | False | RESOLVED | 0.412 | 0 | True |
| LOGOS:SAMPLE:e36c5ba2-d99a-4a | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:bd1c9cd4-7325-44 | category_error | REJECT | REJECTED | SILVER | False | RESOLVED | 0.529 | 1 | True |
| LOGOS:SAMPLE:ba436816-5d01-41 | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:a4ab9800-6074-45 | category_error | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 0 | True |
| LOGOS:SAMPLE:26097a37-a4f1-4f | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:5042172b-c920-4e | category_error | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:584c629a-a671-40 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.477 | 0 | True |
| LOGOS:SAMPLE:90d657d7-045d-45 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.489 | 0 | True |
| LOGOS:SAMPLE:c3f4a181-732d-47 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:c78a8e69-baba-46 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.489 | 0 | True |
| LOGOS:SAMPLE:04b806a9-8515-40 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.489 | 0 | True |
| LOGOS:SAMPLE:d0d64da4-bfde-43 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.412 | 0 | True |
| LOGOS:SAMPLE:3e85115b-525a-4c | scale_failure | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:c36a0dc0-344c-43 | scale_failure | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:f61b4707-4a22-48 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:c8f48fb1-ae65-47 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:76ae0c59-e086-4c | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:737e1dc8-4ecb-46 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:bf7fa543-1fc3-49 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:f698d91f-1953-47 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:102762ff-e732-49 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:7bc596d4-e929-48 | unresolved_frame | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:5e171f01-c554-41 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:08a3f90c-eda5-4b | contradiction_repair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 0 | True |
| LOGOS:SAMPLE:90675c00-962a-4a | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:e2e314c5-886d-43 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:e8c24fd0-dc99-44 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:7f34435b-86ef-41 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:6947a711-3c4c-4e | contradiction_repair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 0 | True |
| LOGOS:SAMPLE:2c260b11-0ed6-45 | contradiction_repair | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:f9ba0d99-f3c3-44 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.489 | 0 | True |
| LOGOS:SAMPLE:f9442330-f2ee-4b | missing_organ | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:7061c454-9d46-4d | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:a6d4fcaf-e9ad-45 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:cbe3d37c-3978-45 | missing_organ | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:54ce3a05-243b-4e | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:acdb38a6-dfd4-4c | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:12e44f22-d968-4a | missing_organ | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.489 | 0 | True |
| LOGOS:SAMPLE:35abe3ea-752d-46 | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:030ecab4-ea91-41 | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:2e8ac98a-0cc2-4f | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:954e5e1e-3615-43 | privacy_restricted | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:395af27f-dafa-47 | dpo_pair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:ca6e60b5-f56c-45 | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.529 | 1 | True |
| LOGOS:SAMPLE:3bff04e0-a9a5-42 | dpo_pair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:52aae11c-c13f-45 | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.529 | 1 | True |
| LOGOS:SAMPLE:7b68794f-8d4f-4b | dpo_pair | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.477 | 0 | True |
| LOGOS:SAMPLE:de357b1b-62b3-43 | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.412 | 0 | True |
| LOGOS:SAMPLE:a61771e1-38d2-40 | dpo_pair | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 3 | True |
| LOGOS:SAMPLE:6df9d687-d744-4a | dpo_pair | REJECT | REJECTED | SILVER | False | RESOLVED | 0.529 | 1 | True |
| LOGOS:SAMPLE:ace5e216-0b98-44 | tier_boundary | NEEDS_REVISION | NEEDS_REVISION | BRONZE | False | UNRESOLVED | 0.000 | 0 | True |
| LOGOS:SAMPLE:d28014c7-ae70-45 | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 1 | True |
| LOGOS:SAMPLE:8565c8d1-4d31-47 | tier_boundary | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.432 | 0 | True |
| LOGOS:SAMPLE:cf5028ff-025f-46 | tier_boundary | NEEDS_REVISION | NEEDS_REVISION | SILVER | False | RESOLVED | 0.489 | 0 | True |
| LOGOS:SAMPLE:62301df0-3149-4c | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:28690f6d-26dc-4a | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 1 | True |
| LOGOS:SAMPLE:4af3158b-9d1d-4c | tier_boundary | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | SILVER | True | RESOLVED | 0.529 | 2 | True |
| LOGOS:SAMPLE:1aff2dbf-93c8-4c | tier_boundary | REJECT | REJECTED | REJECT | False | UNRESOLVED | 0.000 | 0 | True |

## Validation errors (if any)

```json
[]
```
