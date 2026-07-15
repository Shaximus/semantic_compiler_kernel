# DPO Acceptance Metrics Report V2.1.3

## Summary

- Valid DPO pairs: 4
- Mean delta: 0.016
- Median delta: 0.000
- Min delta: 0.000
- Max delta: 0.065

## Acceptance gate

- median valid DPO delta ≥ 0.15: FAIL

## Per-pair detail

| pair_id | positive_iso | negative_iso | delta | positive_tier | negative_tier | positive_decision | negative_decision |
|---|---|---:|---:|---:|---|---|---|---|
| firewall_membrane | 0.529 | 0.529 | +0.000 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |
| immune_security | 0.529 | 0.529 | +0.000 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |
| memory_gc | 0.477 | 0.412 | +0.065 | SILVER | SILVER | NEEDS_REVISION | REJECT |
| supply_circulation | 0.529 | 0.529 | +0.000 | SILVER | SILVER | COMPILED_WITH_GUARDRAILS | REJECT |