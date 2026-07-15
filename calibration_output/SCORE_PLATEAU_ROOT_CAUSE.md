# Score Plateau Root-Cause Report V2.1.3

## Distribution summary

- Unique samples: 35
- Distinct ISO scores: 9
- Distinct coverage values: 2
- Most common ISO score: 0.0 (9 samples)
- Most common coverage: 0.8571 (30 samples)

## Top ISO score values

| iso_score | count |
|---:|---:|
| 0.0 | 9 |
| 0.6256 | 7 |
| 0.5319 | 5 |
| 0.0597 | 5 |
| 0.0548 | 3 |
| 0.0503 | 2 |
| 0.0001 | 2 |
| 0.5828 | 1 |
| 0.0428 | 1 |

## Top coverage values

| coverage | count |
|---:|---:|
| 0.8571 | 30 |
| 0.4286 | 5 |

## Likely root cause

The geometric mean of assessment dimensions collapses many samples to the same value because:
1. Most samples use the same set of populated dimensions (relationships, scale, contradictions).
2. The weighting does not strongly differentiate clear analogies from weak metaphors.
3. Several dimensions return default or near-default values for the majority of inputs.

## Recommended fix

Introduce a discriminative signal that depends on relationship quality and semantic error class, not only coverage count.