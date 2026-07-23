# Semantic Compiler Kernel

A semantic compilation and isomorphism-analysis pipeline that converts raw natural language into structured, schema-validated training data for language-model fine-tuning.

## Status

**Current release:** `V2.1.3` (canonical freeze) + `V2.2` medical-ontology decompression expansion

- 147/147 tests passing (67 frozen core + 80 expansion) via `python -m pytest tests`;
  `python -m unittest discover` also runs clean (77 unittest-style tests; the
  remaining expansion tests are pytest-style function tests)
- Core schema version: `2.1.0` (frozen; `core/`, `extraction/`, `gates/`, `registry/` untouched)
- Expansion decompression version: `2.2.0-rc1`
- Packaged with `pyproject.toml` (setuptools): `pip install -e .` from a fresh
  clone makes `semantic_compiler` importable everywhere — no `PYTHONPATH` hacks
- Corpus orchestration + cross-document invariant registry in `expansion.corpus`
- Buildcraft compute ontology available in `registry/` and `translation/`
- Manifest: `calibration_output/RELEASE_MANIFEST_V2_1_3.json`

## What it does

1. **Extraction** — skeleton (actors/objects), relationships, claims, evidence, frames
2. **Semantic IR** — normalized intermediate representation
3. **Gates** — security, boundaries, causality, measurement, corpus completeness, contradiction repair, missing-organ scope
4. **Scoring** — mapping quality, assessment coverage, isomorphism quality
5. **Dataset export** — schema-validated JSONL for SFT/DPO/contrastive training

## V2.2 expansion — medical-ontology decompression

The `expansion/` layer adds system decompression on top of the frozen V2.1.3
core: given a `SemanticPacket`, `expansion.decompress()` reconstructs the
whole system the input describes, diagnoses its failure modes in
medical-ontology terms, and advises on treatment.

- **16 domain templates** (`expansion/templates/`, via `expansion.registry`) —
  biology, computation, construction, corporate, ecology, economic,
  environmental, evolutionary, government, informational, law, medical,
  military, organizational, reflexion, social
- **Pathology taxonomy** (`expansion.pathology`) — structural pathologies
  (boundary_breach, cancer, autoimmune, prompt_injection, data_corruption,
  ...) mapped to medical diagnoses with evidence and confidence
- **Isomorphism overlay** (`expansion.isomorphism`) — universal functional
  graph with coverage ratios
- **Reconstruction** (`expansion.reconstruction`) — missing-component
  inference by cross-domain analogy plus scope-aware completeness assessment
- **Architecture advisor** (`expansion.advisor`) — diagnosis, prescriptions,
  architecture improvements, resilience training, prognosis
- **V2.2 system-model schema** (`expansion/schemas/v2_2_system_model.schema.json`)
  — every decompressed model is validated before return

Calibration: `calibration_output/decompression_calibration_v2_2.jsonl`
(80 rows, 8 categories × 10, 16 domains × 5, 100% schema-valid) with the full
analysis in `calibration_output/DECOMPRESSION_CALIBRATION_REPORT_V2_2.md`.

## V2.2 expansion — corpus mapping and mission readiness

Additional expansion modules supporting multi-document corpus mapping into a
cross-document **invariant registry** (all deterministic, no LLM calls):

- **Corpus orchestration** (`expansion.corpus`) — `compile_corpus()` accepts
  document paths, `(doc_id, text, metadata)` tuples, or dicts; chunks long
  documents paragraph/section-aware with exact source offsets; compiles each
  chunk with document metadata in the context dict; aggregates a corpus-level
  report whose `invariant_registry` records recurring structural fingerprints
  with supporting documents+locations, confirmations, scoped disconfirmations,
  evidence tier, verdict, timestamps, and a derivation event log.
- **Evidence tiers** (`expansion.evidence_tiers`) — five mission-facing tiers
  (PRIMARY_RECORD, PUBLISHED_RESEARCH, SELF_ASSESSED_ESTIMATE,
  AI_GENERATED_ASSESSMENT, MARKED_SPECULATION) mapped from the frozen
  `EvidenceSourceType` / `EVIDENCE_PRIORITY` machinery.
- **Counter-mapping** (`expansion.counter_mapping`) — attach real
  disconfirmations (counterexamples, source/target-only features) to mappings
  so they flow through the frozen pipeline into dataset-row `negative_tests[]`;
  "searched but not found" is recorded with an auditable scope, never as
  confirmed absence.
- **Derivation order** (`expansion.derivation_order`) — per-claim/per-invariant
  event log tracking whether derivation preceded exposure to a parallel
  account (`True`/`False`/`None`, never guessed).
- **Verdict translation** (`expansion.verdicts`) — maps the frozen verdict
  machinery onto HOLDS / STRAINS / UNRESOLVED (documented mapping table).
- **Invariant-registry schema** (`expansion/schemas/v2_2_invariant_registry.schema.json`,
  Draft 2020-12) — validates the corpus report and registry entries; the
  domain-template and V2.2 system-model validators now use real `jsonschema`
  validation as well.
- **Advisor content** (`expansion.advisor`) — prescriptions and resilience
  training are now populated rule-based from the pathology taxonomy and
  template failure modes (vaccination-style indicator drills, graduated load
  drills for reconstructed components).

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
# Install (editable) from a fresh clone
pip install -e .

# Run the full suite (core + expansion)
python -m pytest tests -q

# unittest discovery also runs clean (unittest-style subset)
python -m unittest discover

# Generate calibration corpus
python scripts/generate_calibration_corpus.py

# Generate freeze artifacts
python scripts/generate_v2_1_3_freeze_artifacts.py

# Build the V2.2 decompression calibration corpus
python scripts/build_decompression_calibration.py

# Compile a multi-document corpus into an invariant registry
python -c "
from semantic_compiler.expansion.corpus import compile_corpus
report = compile_corpus(['doc1.md', ('doc2', 'raw text', {'evidence_tier': 'PRIMARY_RECORD'})])
print(report['invariant_registry'])
"
```

## Layout

- `core/` — pipeline, types, scoring, audit, dataset export
- `extraction/` — skeleton, relationships, frames, claims, evidence
- `gates/` — semantic gates and repair logic
- `registry/` — terms, cosmological constants, department mappings, buildcraft ontology
- `translation/` — fractal / cross-domain translation and buildcraft shorthand resolution
- `modes/` — operating modes (coherence, reality orientation, defense pathology)
- `expansion/` — V2.2 medical-ontology decompression (templates, pathology, reconstruction, advisor, schema) plus corpus orchestration, evidence tiers, counter-mapping, derivation-order tracking, and verdict translation
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
| V2.2 decompression corpus | `calibration_output/decompression_calibration_v2_2.jsonl` |
| V2.2 calibration report | `calibration_output/DECOMPRESSION_CALIBRATION_REPORT_V2_2.md` |
