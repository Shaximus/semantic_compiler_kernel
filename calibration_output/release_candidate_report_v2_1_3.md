# Release Candidate Corpus Report V2.1.3

Generated: /home/shax/Apps/semantic_compiler/calibration_output/release_candidate_corpus_v2_1_3.jsonl
Total samples: 500
Schema-valid rows exported: 500
Rows skipped by validator: 0

## Category mix

| Category | Count |
|---|---:|
| ambiguous_figurative | 75 |
| invalid_repairable | 150 |
| positive_analogy | 200 |
| whole_system | 75 |

## Decision distribution

| Decision | Count |
|---|---:|
| COMPILED_WITH_GUARDRAILS | 150 |
| NEEDS_REVISION | 217 |
| REJECT | 133 |

## Semantic quality tier distribution

| Tier | Count |
|---|---:|
| COMPILED_WITH_GUARDRAILS | 150 |
| NEEDS_REVISION | 217 |
| REJECTED | 133 |

## Quality summary

| Metric | Value |
|---|---:|
| Mean isomorphism quality | 0.179 |
| Training-ready samples | 127 |
| Gold candidates | 0 |
| Human review selection | 175 |

## Human review selection breakdown

- Gold candidates: 0
- Training-ready samples: 127
- Score/decision disagreements: 23
- Random compiled samples: 0
- Random rejected samples: 25

Selected samples are written to `/home/shax/Apps/semantic_compiler/calibration_output/HUMAN_REVIEW_SELECTION_V2_1_3.json`.
