# Semantic Compiler V2.2 Expansion — Medical-Ontology System Decompression

**Date:** 2026-07-16  
**Status:** Design approved in sections; pending written-spec review  
**Author:** Logos_(Memory_Sync_of_Logos)  
**Reviewer:** Curtis_Shax  
**Target release:** V2.2.0-rc1

---

## 1. Purpose and vision

The Semantic Compiler currently translates short text into typed claims, skeletons, relationships, gate evaluations, scores, and decisions. The V2.2 expansion adds a **system-decompression engine** that maps descriptions of systems in many domains into a shared, precise reasoning structure grounded in medical terminology and research.

The goal is to teach Shax 1.0 — and to enable the compiler itself — to:

1. **Decompress** any system description into a complete structural model.
2. **Translate** that model across domains using medical ontology as the lingua franca.
3. **Reconstruct** missing components and functions with confidence-scored inference.
4. **Advise** on architecture improvements framed as treatment protocols.
5. **Emit** training-ready V2.2 JSON dataset rows for SFT, DPO, classification, retrieval, error detection, and repair modeling.

The design principle is: **every system is a body; every failure is a pathology; every repair is a treatment.** Medical terminology provides the deepest research vocabulary for system failure, defense, recovery, and resilience, and it is therefore the backbone of cross-domain reasoning.

---

## 2. Scope and non-goals

### In scope

- A new `expansion/` package layered over the frozen V2.1.3 core.
- Registry-driven domain templates for 16 initial domains.
- Medical ontology as the universal pathology and functional-graph language.
- Isomorphism overlay and reconstruction for missing-component inference.
- Architecture advisor generating treatment-protocol suggestions.
- V2.2 JSON schema extension and dataset-row builder.
- Unit, integration, and calibration tests.

### Out of scope

- Modifying the frozen V2.1.3 core (`core/`, `extraction/`, `gates/`, `registry/`).
- Live LLM calls or external API dependencies.
- Automatic execution of architecture improvements.
- Training-run execution or fine-tuning.
- External distribution or export of V2.2 samples.

---

## 3. Architecture

### 3.1 Package layout

```text
semantic_compiler/
  expansion/
    __init__.py                    # public API: decompress(packet) -> SystemModel
    registry/
      loader.py                    # domain template discovery and validation
      index.py                     # domain index and lookup
    templates/                     # one YAML file per domain
      corporate.yaml
      government.yaml
      law.yaml
      medical.yaml
      construction.yaml
      biology.yaml
      ecology.yaml
      environmental.yaml
      computation.yaml
      organizational.yaml
      economic.yaml
      reflexion.yaml
      social.yaml
      evolutionary.yaml
      informational.yaml
      military.yaml
    ontology/
      medical_ontology.py          # canonical medical concepts and relationships
      domain_mappings.py           # per-domain medical-concept mappings
    pathology/
      taxonomy.py                  # universal pathology classes (medical-grounded)
      profiles.py                  # per-domain pathology profiles
    isomorphism/
      overlay.py                   # universal functional graph translation
      inference.py                 # cross-domain missing-function inference
    reconstruction/
      missing_components.py        # missing-organ/component inference
      completeness.py              # scope-aware completeness assessment
    advisor/
      improvements.py              # improvement classes and rules
      patterns.py                  # known-good architecture patterns
    schema/
      v2_2_system_model.py         # JSON schema definition
      validate.py                  # validation helpers
    output.py                      # V2.2 dataset row + SFT sample builder
```

### 3.2 Integration with frozen core

The expansion consumes `SemanticPacket` and `SemanticIR` produced by `core.compile_semantic_packet()`. It does not modify the core. The frozen V2.1.3 schema remains canonical for the base dataset row; V2.2 adds a `system_model` section.

### 3.3 Data flow

```text
input text
  → core.compile_semantic_packet()
  → expansion.decompress(packet)
      → domain template match
      → skeleton/relationship population
      → pathology profile application (medical ontology)
      → isomorphism overlay (universal functional graph)
      → reconstruction (missing components/functions)
      → advisor (treatment/architecture suggestions)
  → V2.2 system-model JSON
  → dataset row / SFT sample / audit record
```

---

## 4. Domain template contract

Each domain is a YAML template validated against `domain-template.schema.json`.

```yaml
domain: computation
version: 1.0
description: Software, networks, and information-processing systems.

components:
  - name: input_layer
    function: receive and validate external data
    criticality: high
  - name: processing_core
    function: transform data into decisions
    criticality: high
  - name: memory_store
    function: persist state and history
    criticality: high
  - name: defense_boundary
    function: detect and block threats
    criticality: high
  - name: output_layer
    function: emit results and signals
    criticality: medium

relationships:
  - from: input_layer
    to: processing_core
    type: feeds
  - from: processing_core
    to: memory_store
    type: reads_writes
  - from: defense_boundary
    to: input_layer
    type: guards

invariants:
  - input must be validated before processing
  - memory must not be writable without integrity checks
  - defense boundary must fail closed

failure_modes:
  - name: prompt_injection
    medical_map: pathogen
    description: malicious instruction overrides intended behavior
    indicators: unexpected instruction following, boundary bypass
  - name: data_corruption
    medical_map: inflammation
    description: degraded input causes downstream stress
    indicators: error cascades, validation failures

architecture_patterns:
  - name: defense_in_depth
    medical_map: immune_system
    description: layered boundaries with independent failure modes
  - name: circuit_breaker
    medical_map: quarantine
    description: isolate failing component before cascade
```

**Pathology profile rule:** every domain maps at least 80% of its failure modes to canonical medical ontology concepts. Unmapped modes are listed as `domain_specific` and do not block compilation.

---

## 5. Medical ontology backbone

Canonical medical concepts form the shared vocabulary for all domains.

| Medical concept | Cross-domain meaning |
|---|---|
| `homeostasis` | system stability / equilibrium maintenance |
| `immune_system` | defense mechanisms, threat detection, boundary integrity |
| `pathogen` | external attack vector (prompt injection, malware, hostile actor) |
| `cancer` | uncontrolled growth / resource capture / scope creep |
| `autoimmune` | self-attack / internal sabotage / friendly-fire |
| `sepsis` | systemic cascade / cascading failure / contagion |
| `inflammation` | stress response / overheating / overload |
| `diagnosis` | fault detection / root-cause analysis |
| `prognosis` | failure prediction / risk assessment |
| `treatment` | repair / mitigation / architecture improvement |
| `vaccination` | pre-emptive hardening / resilience training |
| `quarantine` | isolation / containment / sandboxing |
| `metastasis` | lateral spread / privilege escalation / contagion |
| `remission` | recovery / stabilization |
| `chronic` | persistent degraded state / technical debt |
| `acute` | sudden failure / crisis event |

The ontology is implemented in `ontology/medical_ontology.py` as a typed registry with relationships between concepts.

---

## 6. Isomorphism overlay and reconstruction

### 6.1 Universal functional graph

Every decompressed system is translated into a labeled directed graph. Nodes are functions/components labeled with medical ontology terms; edges are relationships.

Example mapping:

| Domain | Domain term | Medical-ontology label |
|---|---|---|
| Corporate | executive_board | control_center |
| Corporate | legal_compliance | immune_boundary |
| Computation | api_gateway | immune_boundary |
| Computation | rate_limiter | homeostasis_regulation |
| Biology | cell_membrane | immune_boundary |
| Biology | metabolism | homeostasis_regulation |

Because labels are shared, cross-domain inference is possible: "This computation system has a growth process but no immune boundary — where is its defense layer?"

### 6.2 Reconstruction pipeline

1. **Populate observed components** from skeleton/relationship extraction.
2. **Map to medical ontology** using the domain template's pathology profile.
3. **Check expected functional coverage** against the universal template for that domain class.
4. **Infer missing components** using cross-domain analogy, with cited source domain and analogy strength.
5. **Mark inference confidence**: `observed`, `inferred_by_analogy`, `absent_confirmed`, `unobserved`.

**Scope-aware rule:** reconstruction runs only when the input claims to describe a complete system or the user explicitly requests completeness analysis. Fragmentary inputs produce `UNOBSERVED` findings, not `ABSENT` penalties.

---

## 7. Architecture advisor

The advisor generates actionable suggestions framed as treatment protocols.

| Class | Medical frame | Function |
|---|---|---|
| `diagnosis` | identify pathology | Names the failure pattern |
| `prescription` | immediate mitigation | Suggests containment or repair |
| `architecture_improvement` | long-term treatment | Proposes structural changes |
| `resilience_training` | vaccination | Suggests pre-emptive hardening |
| `prognosis` | risk outlook | Predicts failure trajectory |

**Rule example:**

```yaml
- if: growth_process present AND homeostasis_regulation absent
  then:
    diagnosis: cancer_pattern
    prescription: add feedback regulation
    architecture_improvement: introduce resource-allocation controller
    confidence: high
```

Every suggestion carries `evidence`, `medical_ontology_reference`, `confidence`, `domain_specific_translation`, and `estimated_impact`.

---

## 8. V2.2 schema and output contract

V2.2 extends the frozen V2.1.3 dataset envelope with a new `system_model` section.

```json
{
  "system_model": {
    "domain": "computation",
    "decompression_version": "2.2.0-rc1",
    "components": [
      {
        "name": "api_gateway",
        "function": "receive and validate external requests",
        "medical_map": "immune_boundary",
        "status": "observed",
        "confidence": 0.95
      }
    ],
    "relationships": [...],
    "universal_functional_graph": {
      "nodes": [...],
      "edges": [...],
      "coverage_ratio": 0.83
    },
    "pathology_profile": {
      "detected_pathologies": ["prompt_injection"],
      "medical_diagnoses": [
        {
          "pathology": "cancer_pattern",
          "evidence": ["growth without resource feedback"],
          "confidence": 0.72
        }
      ]
    },
    "reconstruction": {
      "missing_components": [
        {
          "function": "homeostasis_regulation",
          "inferred_by": "cross_domain_analogy",
          "source_domain": "biology",
          "confidence": 0.68
        }
      ],
      "completeness_scope": "whole_system_claimed"
    },
    "advisor": {
      "diagnosis": "...",
      "prescriptions": [...],
      "architecture_improvements": [...],
      "resilience_training": [...],
      "prognosis": "..."
    }
  }
}
```

**Training targets:** SFT, DPO, CLASSIFIER, RETRIEVAL, ERROR_DETECTOR, REPAIR_MODEL.

**Backward compatibility:** V2.1.3 validators ignore `system_model`. V2.2 validators require it only for `sample_kind: DECOMPRESSED_SYSTEM`.

---

## 9. Error handling and validation

| State | Trigger | Behavior |
|---|---|---|
| `DOMAIN_NOT_FOUND` | no template matches input domain | fall back to `universal_generic`; flag `low_confidence` |
| `TEMPLATE_INVALID` | YAML/schema mismatch | raise `DomainTemplateError`; halt decompression |
| `DECOMPRESSION_INCOMPLETE` | required components missing and cannot be inferred | emit partial model; mark `training_ready: false` |
| `ONTOLOGY_MISMATCH` | domain failure mode lacks medical mapping | raise `OntologyMappingError`; route to Logos review |
| `INFERENCE_CONFLICT` | two domains suggest incompatible missing components | record both candidates; flag `contested` |

All decompression runs emit structured logs: domain matched, template version, components observed/inferred, pathologies detected, advisor suggestions, confidence scores, and error states. No silent suppression.

---

## 10. Testing and calibration

### 10.1 Unit tests

- `test_domain_loader` — template discovery and validation
- `test_medical_ontology` — canonical concept registry
- `test_isomorphism_overlay` — functional-graph translation
- `test_reconstruction` — missing-component inference
- `test_advisor` — improvement-rule evaluation

Target: ≥90% coverage on new code.

### 10.2 Domain template tests

- Every initial template loads and validates.
- Every template produces expected components for seeded inputs.
- Every pathology profile maps ≥80% of failure modes to medical ontology.

### 10.3 Integration tests

- End-to-end decompression for each of the 16 initial domains.
- Cross-domain reconstruction: biology → computation, corporate → biology, etc.
- Medical-ontology consistency across domains.

### 10.4 Calibration corpus

80 samples:

- 10 strong whole-system descriptions
- 10 fragmentary descriptions (must yield `UNOBSERVED`)
- 10 pathology-positive samples
- 10 cross-domain analogy samples
- 10 architecture-improvement samples
- 10 privacy-restricted samples
- 10 boundary cases near confidence thresholds
- 10 adversarial samples

### 10.5 Acceptance gates before V2.2 freeze

```text
0 invalid domain templates
0 silent decompression failures
≥90% pathology-detection accuracy on seeded cases
≥85% cross-domain reconstruction agreement with human review
0 ABSENT findings on fragmentary inputs without scope claim
100% schema-valid V2.2 dataset rows
```

---

## 11. Implementation notes

- **YAGNI:** build only the 16 initial templates, the medical ontology, and the reconstruction/advisor rules needed for the calibration corpus. Do not speculate on future domains beyond the registry extension point.
- **Incremental:** land the ontology and one domain end-to-end first, then add the remaining templates.
- **Test-driven:** write unit tests for each module before implementation.
- **No core edits:** the frozen V2.1.3 core is untouched.

---

## 12. Open questions

1. Should the `universal_generic` fallback template be a full template or a minimal skeleton?
2. Should V2.2 introduce a new `DECOMPRESSED_SYSTEM` sample kind, or reuse `POSITIVE`/`NEGATIVE` with a flag?
3. Should advisor suggestions be deterministic rules only, or should there be a future hook for a learned suggestion model?
4. Which two domains should be the first end-to-end calibration pair?

These will be resolved during implementation-plan writing unless Curtis rules otherwise.
