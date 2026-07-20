# Semantic Compiler Kernel

A semantic compilation and isomorphism-analysis pipeline that converts raw natural language into structured, schema-validated training data for language-model fine-tuning.

## Status

**Current release:** `V2.1.3` (canonical freeze)

- 67/67 canonical release tests passing
- Schema version: `2.1.0`
- Manifest: `calibration_output/RELEASE_MANIFEST_V2_1_3.json`

## What it does

1. **Extraction** — skeleton (actors/objects), relationships, claims, evidence, frames
2. **Semantic IR** — normalized intermediate representation
3. **Gates** — security, boundaries, causality, measurement, corpus completeness, contradiction repair, missing-organ scope
4. **Scoring** — mapping quality, assessment coverage, isomorphism quality
5. **Dataset export** — schema-validated JSONL for SFT/DPO/contrastive training

## Buildcraft compute ontology

The optional `BUILDCRAFT_COMPUTE_ONTOLOGY` formalizes Path of Exile buildcraft shorthand as guarded structural mappings:

- motherboard/chassis topology → character equipment paper doll
- PCIe accelerator slot → weapon slot
- CPU socket/host position → body-armour slot
- GPU/accelerator → equipped weapon
- CPU package → equipped body armour
- hardware integration capacity → item sockets and links
- LLM/application → active skill gem
- drafter/MTP/cache/framework → support gem
- CUDA/PyTorch/drivers/ABI → compatibility requirements
- occupied VRAM → mana reservation
- deployed architecture → complete build

The registry preserves slot → item → socket/link → component → reservation relationships while rejecting literal material identity. Repositories and packages are classified by deployed function rather than artifact format alone.

Example:

```python
from semantic_compiler.translation import resolve_buildcraft_mappings

mappings = resolve_buildcraft_mappings(
    "PCIe slots are weapon slots; the GPU is the weapon; "
    "the LLM and support gems consume VRAM."
)
```

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
- `registry/` — terms, cosmological constants, department mappings, buildcraft ontology
- `translation/` — fractal / cross-domain translation and buildcraft shorthand resolution
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
