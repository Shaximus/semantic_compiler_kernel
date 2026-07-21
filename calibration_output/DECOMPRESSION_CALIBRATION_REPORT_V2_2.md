# Decompression Calibration Report V2.2

Generated: /home/shax/Apps/semantic_compiler/calibration_output/decompression_calibration_v2_2.jsonl
Builder: `scripts/build_decompression_calibration.py` (Task 11)
Date: 2026-07-21
Verification: full test suite 89/89 passing (67 frozen V2.1.3 core + 22 expansion)

## Corpus size

| Metric | Value |
|---|---:|
| Total samples | 80 |
| Calibration categories | 8 (10 each) |
| Intended domains covered | 16 (5 each) |
| Schema-valid system models | 80 / 80 (100.0%) |

Every corpus row was produced by `expansion.decompress(packet)` and re-validated
against `expansion/schemas/v2_2_system_model.schema.json` post hoc; no row was
skipped or quarantined.

## Category distribution

| Category | Count |
|---|---:|
| adversarial | 10 |
| architecture_improvement | 10 |
| boundary_case | 10 |
| cross_domain_analogy | 10 |
| fragmentary | 10 |
| pathology_positive | 10 |
| privacy_restricted | 10 |
| strong_whole_system | 10 |

## Domain distribution (intended labels)

| Domain | Count |
|---|---:|
| biology | 5 |
| computation | 5 |
| construction | 5 |
| corporate | 5 |
| ecology | 5 |
| economic | 5 |
| environmental | 5 |
| evolutionary | 5 |
| government | 5 |
| informational | 5 |
| law | 5 |
| medical | 5 |
| military | 5 |
| organizational | 5 |
| reflexion | 5 |
| social | 5 |

Domain-inference agreement (pipeline `_infer_domain` vs. intended label):
3 / 80 (3.8%). The current heuristic recognizes only computation/biology
keywords and falls back to `universal_generic` for 73 rows. This is a known
limitation of the V2.2 inference heuristic, not a corpus defect: calibration
labels are authoritative, inferred domains are not.

## Pathology detection rate

| Metric | Value |
|---|---:|
| Rows with ≥1 detected pathology | 80 / 80 (100.0%) |
| Rows with ≥1 medical diagnosis | 80 / 80 (100.0%) |
| pathology_positive category detection | 10 / 10 (100.0%) |
| Mean diagnoses per row | 1.09 |
| Diagnosis confidence (all rows) | 0.75 (fixed) |

Detection by pathology:

| Pathology | Rows |
|---|---:|
| boundary_breach | 73 |
| cancer | 4 |
| autoimmune | 4 |
| prompt_injection | 3 |
| data_corruption | 3 |

Detection by category:

| Category | Detected |
|---|---:|
| adversarial | 10 / 10 |
| architecture_improvement | 10 / 10 |
| boundary_case | 10 / 10 |
| cross_domain_analogy | 10 / 10 |
| fragmentary | 10 / 10 |
| pathology_positive | 10 / 10 |
| privacy_restricted | 10 / 10 |
| strong_whole_system | 10 / 10 |

Calibration finding: sensitivity on the pathology_positive category is 100%,
but the detector currently has no specificity — it fires on every category,
including strong_whole_system. `boundary_breach` alone accounts for 73 of 87
detections. The detection profiles are heuristic threshold rules; treat
detections on non-pathology categories as expected false positives until the
profiles are tuned (post-V2.2 work, outside the frozen V2.1.3 core).

## Reconstruction accuracy

| Metric | Value |
|---|---:|
| Template function coverage (mean) | 100.0% |
| Template function coverage (min) | 100.0% |
| Rows with inferred missing components | 0 / 80 |
| Functional-graph coverage ratio (min/mean/max) | 1.0 / 1.0 / 1.0 |
| Completeness scope `unknown` | 80 / 80 |

Calibration finding: the pipeline materializes every template component
(status `inferred_by_analogy`, confidence 0.6), so reconstruction never
observes a gap and the missing-component channel is never exercised. The
scope classifier likewise never sees `claims_complete_system`, so fragmentary
inputs are not distinguished from whole-system inputs (all rows score
`unknown`). Both channels are implemented and unit-tested; the calibration
corpus simply does not currently drive them. Flagged for post-V2.2 work.

## Advisor output quality

| Metric | Value |
|---|---:|
| Rows with ≥1 diagnosis | 80 / 80 (100.0%) |
| Rows with ≥1 prescription | 0 / 80 |
| Rows with ≥1 architecture improvement | 0 / 80 |
| Rows with ≥1 resilience-training item | 0 / 80 |
| Prognosis `at_risk` | 80 / 80 |
| Prognosis `stable` | 0 / 80 |

Calibration finding: advisor diagnosis output is fully wired to pathology
detection (every detection yields a medical-ontology diagnosis). The
prescription, architecture-improvement, and resilience-training channels
produce no output on this corpus because they are gated on missing-component
input, which never fires (see Reconstruction). Prognosis is uniformly
`at_risk` as a direct consequence of the 100% pathology detection rate.

## Schema validity rate

| Metric | Value |
|---|---:|
| System models valid against V2.2 schema | 80 / 80 (100.0%) |
| Validation errors | 0 |

## Summary

The V2.2 decompression calibration corpus meets its build contract: 80 rows,
8 balanced categories, all 16 non-generic domains represented, 100% schema
validity, end-to-end pipeline execution with no errors. The medical-ontology
diagnosis path is exercised on every row. Three calibration findings for
post-V2.2 tuning: (1) pathology detection has 100% sensitivity but no
specificity, (2) domain inference agrees with intended labels on only 3/80
rows, (3) the reconstruction and advisor prescription channels are never
activated by the current pipeline's component materialization.
