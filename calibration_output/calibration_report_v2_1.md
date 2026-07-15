# Logos Calibration Corpus Report V2.1

Generated: /home/shax/Apps/semantic_compiler/calibration_output/calibration_corpus_v2_1.jsonl
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
| COMPILED_WITH_GUARDRAILS | 8 |
| NEEDS_REVISION | 68 |

## Tier distribution

| Tier | Count |
|---|---:|
| BRONZE | 40 |
| SILVER | 36 |

## Target frame resolution

| Status | Count |
|---|---:|
| RESOLVED | 36 |
| UNRESOLVED | 40 |

## Quality metrics

| Metric | Value |
|---|---:|
| Schema validity rate | 100.0% |
| Hard gate failure frequency | 2 / 76 (2.6%) |
| Forced target frequency | 0 / 76 (0.0%) |
| Unresolved frame frequency | 40 / 76 (52.6%) |
| Mean isomorphism quality | 0.747 |
| Mean structural fit | 0.375 |

## Category-level calibration

| Category | Count | Mean ISO | Mean Struct Fit | Decisions | Tiers | Target Resolution |
|---|---|---:|---:|---|---|---|
| category_error | 8 | 0.860 | 0.200 | {"NEEDS_REVISION": 8} | {"BRONZE": 6, "SILVER": 2} | {"RESOLVED": 2, "UNRESOLVED": 6} |
| contradiction_repair | 8 | 0.873 | 0.450 | {"COMPILED_WITH_GUARDRAILS": 1, "NEEDS_REVISION": 7} | {"BRONZE": 6, "SILVER": 2} | {"RESOLVED": 2, "UNRESOLVED": 6} |
| dpo_pair | 8 | 0.381 | 0.263 | {"NEEDS_REVISION": 8} | {"SILVER": 8} | {"RESOLVED": 8} |
| heuristic_metaphor | 8 | 0.803 | 0.367 | {"COMPILED_WITH_GUARDRAILS": 1, "NEEDS_REVISION": 7} | {"BRONZE": 5, "SILVER": 3} | {"RESOLVED": 3, "UNRESOLVED": 5} |
| missing_organ | 8 | 0.670 | 0.330 | {"NEEDS_REVISION": 8} | {"BRONZE": 3, "SILVER": 5} | {"RESOLVED": 5, "UNRESOLVED": 3} |
| privacy_restricted | 4 | 0.864 | 0.250 | {"NEEDS_REVISION": 4} | {"BRONZE": 3, "SILVER": 1} | {"RESOLVED": 1, "UNRESOLVED": 3} |
| scale_failure | 8 | 0.755 | 0.450 | {"NEEDS_REVISION": 8} | {"BRONZE": 4, "SILVER": 4} | {"RESOLVED": 4, "UNRESOLVED": 4} |
| strong_isomorphism | 8 | 0.552 | 0.386 | {"COMPILED_WITH_GUARDRAILS": 2, "NEEDS_REVISION": 6} | {"BRONZE": 1, "SILVER": 7} | {"RESOLVED": 7, "UNRESOLVED": 1} |
| tier_boundary | 8 | 0.774 | 0.650 | {"COMPILED_WITH_GUARDRAILS": 4, "NEEDS_REVISION": 4} | {"BRONZE": 4, "SILVER": 4} | {"RESOLVED": 4, "UNRESOLVED": 4} |
| unresolved_frame | 8 | 1.000 | 0.000 | {"NEEDS_REVISION": 8} | {"BRONZE": 8} | {"UNRESOLVED": 8} |

## DPO pair deltas

| Pair ID | Δ ISO | Positive ISO | Negative ISO | Positive Tier | Negative Tier | Positive Decision | Negative Decision |
|---|---|---:|---:|---|---|---|---|---|
| firewall_membrane | +0.051 | 0.490 | 0.439 | SILVER | SILVER | NEEDS_REVISION | NEEDS_REVISION |
| immune_security | +0.000 | 0.499 | 0.499 | SILVER | SILVER | NEEDS_REVISION | NEEDS_REVISION |
| memory_gc | +0.492 | 0.555 | 0.063 | SILVER | SILVER | NEEDS_REVISION | NEEDS_REVISION |
| supply_circulation | +0.376 | 0.439 | 0.063 | SILVER | SILVER | NEEDS_REVISION | NEEDS_REVISION |

## Expected-vs-actual category disagreement

| Category | Issue | Details |
|---|---|---|
| contradiction_repair | majority_below_expected_tier | {"expected_min": "GOLD", "below_count": 8, "total": 8} |
| heuristic_metaphor | most_common_decision_unexpected | {"expected": ["COMPILED", "COMPILED_WITH_GUARDRAILS"], "actual": "NEEDS_REVISION", "count": 7} |
| heuristic_metaphor | majority_below_expected_tier | {"expected_min": "SILVER", "below_count": 5, "total": 8} |
| missing_organ | most_common_decision_unexpected | {"expected": ["COMPILED", "COMPILED_WITH_GUARDRAILS"], "actual": "NEEDS_REVISION", "count": 8} |
| privacy_restricted | most_common_decision_unexpected | {"expected": ["COMPILED_PRIVATE_REDACTED_ONLY", "COMPILED_SUPERVISED_ONLY"], "actual": "NEEDS_REVISION", "count": 4} |
| privacy_restricted | majority_below_expected_tier | {"expected_min": "SILVER", "below_count": 3, "total": 4} |
| strong_isomorphism | most_common_decision_unexpected | {"expected": ["COMPILED"], "actual": "NEEDS_REVISION", "count": 6} |
| unresolved_frame | most_common_decision_unexpected | {"expected": ["UNRESOLVED"], "actual": "NEEDS_REVISION", "count": 8} |

## Per-sample detail

| sample_id | category | decision | tier | target_resolution | iso_quality | schema_valid |
|---|---|---|---|---|---|---|
| LOGOS:SAMPLE:46b32a7f-3d0f-4e | strong_isomorphism | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.530 | True |
| LOGOS:SAMPLE:90ab80fa-2096-45 | strong_isomorphism | NEEDS_REVISION | SILVER | RESOLVED | 0.497 | True |
| LOGOS:SAMPLE:d0690841-1155-43 | strong_isomorphism | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.530 | True |
| LOGOS:SAMPLE:ecf47666-8fb5-43 | strong_isomorphism | NEEDS_REVISION | SILVER | RESOLVED | 0.490 | True |
| LOGOS:SAMPLE:245c6374-bbee-4d | strong_isomorphism | NEEDS_REVISION | SILVER | RESOLVED | 0.439 | True |
| LOGOS:SAMPLE:2c9ca4bd-da9f-40 | strong_isomorphism | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:095992df-df26-4c | strong_isomorphism | NEEDS_REVISION | SILVER | RESOLVED | 0.439 | True |
| LOGOS:SAMPLE:4fba9b4e-a4b7-47 | strong_isomorphism | NEEDS_REVISION | SILVER | RESOLVED | 0.490 | True |
| LOGOS:SAMPLE:2435e016-6e4f-46 | heuristic_metaphor | NEEDS_REVISION | SILVER | RESOLVED | 0.439 | True |
| LOGOS:SAMPLE:36343f97-695a-4f | heuristic_metaphor | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:1f2c97cd-5ecb-44 | heuristic_metaphor | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:c324260d-0cbb-43 | heuristic_metaphor | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.530 | True |
| LOGOS:SAMPLE:848224b3-d077-40 | heuristic_metaphor | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:db6a2634-f7d7-48 | heuristic_metaphor | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:e24ec559-78cf-4b | heuristic_metaphor | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:01b63271-cd4e-49 | heuristic_metaphor | NEEDS_REVISION | SILVER | RESOLVED | 0.455 | True |
| LOGOS:SAMPLE:62902316-6374-40 | category_error | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:65eb62dd-abbc-4c | category_error | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:c2231266-bb5e-44 | category_error | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:86b5048f-da12-42 | category_error | NEEDS_REVISION | SILVER | RESOLVED | 0.439 | True |
| LOGOS:SAMPLE:7abe5e5e-9aba-4f | category_error | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:30979cb1-76e3-48 | category_error | NEEDS_REVISION | SILVER | RESOLVED | 0.439 | True |
| LOGOS:SAMPLE:e8d54b83-2e84-4b | category_error | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:0a474180-44f5-45 | category_error | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:39d60fb9-f25d-43 | scale_failure | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:026f33a5-ec1b-45 | scale_failure | NEEDS_REVISION | SILVER | RESOLVED | 0.499 | True |
| LOGOS:SAMPLE:d3826c6f-9efd-45 | scale_failure | NEEDS_REVISION | SILVER | RESOLVED | 0.540 | True |
| LOGOS:SAMPLE:0e30287f-efb2-42 | scale_failure | NEEDS_REVISION | SILVER | RESOLVED | 0.499 | True |
| LOGOS:SAMPLE:6b5ecb38-82dc-48 | scale_failure | NEEDS_REVISION | SILVER | RESOLVED | 0.499 | True |
| LOGOS:SAMPLE:de873759-8355-43 | scale_failure | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:0ec0d64c-dedb-4d | scale_failure | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:89d90a4c-e600-41 | scale_failure | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:c248686e-6a64-40 | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:08cd2a3f-bfe0-49 | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:3291340a-9b2c-45 | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:47e229da-6a63-4b | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:f0bf219e-9e3b-43 | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:644bba8f-a680-4b | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:68c75c4a-1190-40 | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:7f9fad23-a683-42 | unresolved_frame | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:967def1e-eac3-45 | contradiction_repair | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:fde243f9-1e3a-46 | contradiction_repair | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:ac4c8c07-83b4-43 | contradiction_repair | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:5d8ceabe-8d52-47 | contradiction_repair | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:a425629c-2376-4d | contradiction_repair | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:6716a92a-067a-49 | contradiction_repair | NEEDS_REVISION | SILVER | RESOLVED | 0.455 | True |
| LOGOS:SAMPLE:1e746602-6571-46 | contradiction_repair | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.530 | True |
| LOGOS:SAMPLE:5abd9255-ebd6-4b | contradiction_repair | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:a4093c91-e172-44 | missing_organ | NEEDS_REVISION | SILVER | RESOLVED | 0.499 | True |
| LOGOS:SAMPLE:5f7a15dc-0483-4c | missing_organ | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:a1432eee-cc33-47 | missing_organ | NEEDS_REVISION | SILVER | RESOLVED | 0.455 | True |
| LOGOS:SAMPLE:fa63ce9c-f9a2-43 | missing_organ | NEEDS_REVISION | SILVER | RESOLVED | 0.455 | True |
| LOGOS:SAMPLE:67c88112-d77d-48 | missing_organ | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:c97bbb5f-2b8d-40 | missing_organ | NEEDS_REVISION | SILVER | RESOLVED | 0.455 | True |
| LOGOS:SAMPLE:c43cdca7-7828-45 | missing_organ | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:0ebfc577-5e30-46 | missing_organ | NEEDS_REVISION | SILVER | RESOLVED | 0.499 | True |
| LOGOS:SAMPLE:933f3f30-27b9-4b | privacy_restricted | NEEDS_REVISION | SILVER | RESOLVED | 0.455 | True |
| LOGOS:SAMPLE:4e4da4d6-dc43-46 | privacy_restricted | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:c33c5304-5dd8-48 | privacy_restricted | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:5de6a40f-183e-49 | privacy_restricted | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:ab3ac192-6be3-49 | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.490 | True |
| LOGOS:SAMPLE:f1750e83-5c04-44 | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.439 | True |
| LOGOS:SAMPLE:7e3a5244-e781-42 | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.499 | True |
| LOGOS:SAMPLE:4af28ba1-1ead-4a | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.499 | True |
| LOGOS:SAMPLE:8d83a772-79a1-46 | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.555 | True |
| LOGOS:SAMPLE:8872271a-c456-4c | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.063 | True |
| LOGOS:SAMPLE:a87a118a-3244-46 | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.439 | True |
| LOGOS:SAMPLE:173a5de4-9d90-4e | dpo_pair | NEEDS_REVISION | SILVER | RESOLVED | 0.063 | True |
| LOGOS:SAMPLE:2a2b9e2a-c418-4e | tier_boundary | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:7f27c393-8279-43 | tier_boundary | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.530 | True |
| LOGOS:SAMPLE:e674dd54-7d62-41 | tier_boundary | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:675c4275-e02a-4a | tier_boundary | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |
| LOGOS:SAMPLE:e05f3621-6a07-42 | tier_boundary | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.600 | True |
| LOGOS:SAMPLE:b606b0d4-a536-42 | tier_boundary | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.530 | True |
| LOGOS:SAMPLE:a44b4a84-2739-46 | tier_boundary | COMPILED_WITH_GUARDRAILS | SILVER | RESOLVED | 0.530 | True |
| LOGOS:SAMPLE:0f1afd8f-1f50-4a | tier_boundary | NEEDS_REVISION | BRONZE | UNRESOLVED | 1.000 | True |

## Validation errors (if any)

```json
[]
```
