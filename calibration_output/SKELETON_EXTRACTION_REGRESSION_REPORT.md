# Skeleton Extraction Regression Report V2.1.2

## Changes
- Internal phrase-breaker checks prevent prepositions/analogy markers from starting subject phrases.
- Gerund/participle verb forms (running, filtering, delivering, etc.) break object phrases.
- Multi-word domain nouns such as "supply chain" are accepted when the full phrase is known.
- Substring duplicates (e.g. "system" alongside "immune system") are pruned.

## Seeded spot-check results

| Input | Actors | Objects | Notes |
|---|---|---|---|
| A firewall is like a cell membrane... | firewall | cell membrane | Clean |
| The judicial system filters disputes like a kidney filters blood. | judicial system, kidney | blood | "like a kidney" no longer extracted as actor |
| The brain's memory consolidates during sleep like a database running garbage collection. | brain memory, database | garbage collection | Phrase no longer crosses "running" |
| A supply chain delivers materials like a circulatory system delivers oxygen. | supply chain, circulatory system | materials, oxygen | "supply chain" preserved |
| The nervous system routes signals like a telecommunications network. | nervous system | signals, telecommunications network | Clean |
| The company has an immune system that detects threats and remembers them. | company | immune system, threats | Clean |

## Calibration corpus skeleton metrics
- Mean actors per sample: 0.75
- Mean objects per sample: 0.54
- Samples with ≥1 actor: 40 / 76
- Samples with ≥1 object: 28 / 76

## Known residual
- 'brain memory' is awkward; the head noun logic preserves the final noun of the subject phrase.
- Relative clauses ('that detects threats') are not yet expanded into additional actor relationships.
