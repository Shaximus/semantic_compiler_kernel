# Dataset Tier Separation Diff V2.1.2

## Change
`quality` block now separates:
- `semantic_quality_tier` — what the compiler decided about the input.
- `dataset_utility_tier` — what the sample is worth as training material.
- `training_ready` — whether local SFT is permitted.
- `dataset_tier` — preserved as backward-compatible alias to utility tier.

## Calibration corpus distribution

| semantic_quality_tier | dataset_utility_tier | count |
|---|---|---:|
| COMPILED_WITH_GUARDRAILS | SILVER | 23 |
| NEEDS_REVISION | BRONZE | 31 |
| NEEDS_REVISION | SILVER | 22 |

- Training-ready samples: 23 / 76
- SENSITIVE/CRITICAL samples are automatically `training_ready: false`.
