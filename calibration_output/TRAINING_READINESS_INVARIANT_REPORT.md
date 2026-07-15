# Training Readiness Invariant Report V2.1.3

- Unique samples: 35
- training_ready=true: 13
- training_ready=true with relationship_count=0: 0
- training_ready=true in ambiguous_figurative category: 0

## training_ready=true with zero relationships

| text | decision | category | iso_quality |
|---|---|---|---:|

## Invariant violation

A record should not be training-ready when no relationships were extracted from an explicit analogy or causal claim.
Violations found: 0

## Recommended fix

Add a hard gate: `training_ready` requires `relationship_count > 0` for ANALOGY/CAUSAL/METAPHOR inputs, unless the input is explicitly non-relational.