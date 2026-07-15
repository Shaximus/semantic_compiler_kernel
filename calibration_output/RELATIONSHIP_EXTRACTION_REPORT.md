# Relationship Extraction Report V2.1.2

## Overview
Dependency-free SVO and analogy-edge extraction now populates
`semantic_ir.relationships` for every compiled packet.

## Calibration corpus relationship metrics
- Samples with ≥1 relationship: 19 / 76
- Mean relationships per sample: 0.43
- Max relationships in a sample: 3

## Relationship type distribution

| Type | Count |
|---|---:|
| ANALOGOUS_TO | 10 |
| ROUTES_TO | 8 |
| ENABLES | 6 |
| OBSERVES | 5 |
| CONTROLS | 2 |
| CONSTRAINS | 1 |
| CONTAINS | 1 |

## Example extractions

| Input | Extracted relationships |
|---|---|
| A firewall is like a cell membrane... | firewall ANALOGOUS_TO cell membrane |
| The judicial system filters disputes like a kidney filters blood. | kidney CONSTRAINS blood; judicial system ANALOGOUS_TO kidney |
| A supply chain delivers materials like a circulatory system delivers oxygen. | supply chain ROUTES_TO materials; circulatory system ROUTES_TO oxygen; supply chain ANALOGOUS_TO circulatory system |
| The nervous system routes signals like a telecommunications network. | nervous system ROUTES_TO signals; nervous system ANALOGOUS_TO telecommunications network |

## Known residual
- Relative clauses and conjunctions inside verb phrases are not yet fully split into multiple edges.
- Object pronouns ('them', 'it') are skipped because they are not noun phrases.
