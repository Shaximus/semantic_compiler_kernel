# Semantic Compiler Kernel

A semantic compilation and isomorphism-analysis pipeline that converts raw natural language into structured, schema-validated training data for language-model fine-tuning.

## Status

**Current release:** `V2.1.3` (canonical freeze)

- 67/67 tests passing
- Schema version: `2.1.0`
- Manifest: `calibration_output/RELEASE_MANIFEST_V2_1_3.json`

## What it does

1. **Extraction** — skeleton (actors/objects), relationships, claims, evidence, frames
2. **Semantic IR** — normalized intermediate representation
3. **Gates** — security, boundaries, causality, measurement, corpus completeness, contradiction repair, missing-organ scope
4. **Scoring** — mapping quality, assessment coverage, isomorphism quality
5. **Dataset export** — schema-validated JSONL for SFT/DPO/contrastive training

## Quick start

```bash
# Run tests
PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v

# Generate calibration corpus
PYTHONPATH=/home/shax/Apps python3 scripts/generate_calibration_corpus.py

# Generate freeze artifacts
PYTHONPATH=/home/shax/Apps python3 scripts/generate_v2_1_3_freeze_artifacts.py
```

## Layout

- `core/` — pipeline, types, scoring, audit, dataset export
- `extraction/` — skeleton, relationships, frames, claims, evidence
- `gates/` — semantic gates and repair logic
- `registry/` — terms, cosmological constants, department mappings
- `translation/` — fractal / cross-domain translation
- `modes/` — operating modes (coherence, reality orientation, defense pathology)
- `schemas/` — JSON Schema for V2.1 dataset rows
- `scripts/` — corpus generation, quarantine, freeze artifacts
- `calibration_output/` — generated corpora, reports, release artifacts
- `tests/` — unit tests

## Release artifacts

| Artifact | Path |
|---|---|
| Release manifest | `calibration_output/RELEASE_MANIFEST_V2_1_3.json` |
| Known limitations | `calibration_output/KNOWN_LIMITATIONS_V2_1_3.md` |
| SFT pilot train | `calibration_output/SFT_PILOT_DATASET_V1.jsonl` |
| SFT pilot eval | `calibration_output/SFT_PILOT_EVALUATION_SET_V1.jsonl` |
| DPO registry | `calibration_output/DPO_DIAGNOSTIC_REGISTRY.json` |
