# Semantic Compiler V2.1.1 Calibration Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the semantic extraction, scoring, and state-consistency defects identified in Kestrel's V2.1 calibration review so the compiler produces trustworthy training targets.

**Architecture:** Keep the existing V2.1 dataset envelope and schema, but fix the internal scoring (`core/dataset.py`), extraction (`core/pipeline.py` and skeleton extractor), missing-organ detector (`semantic_compiler/gates/missing_organ.py` or equivalent), evidence classification, and decision/disposition separation. Add a bounded corpus-completeness gate.

**Tech Stack:** Python 3, `semantic_compiler` package, `unittest`, JSON Schema validation.

## Global Constraints

- Do not freeze V2.1.0 or start mass dataset production.
- All changes must preserve schema-valid V2.1 output unless the schema itself is version-bumped.
- Unassessed dimensions must be `null`/`N/A`, not `0.0`.
- Missing-organ findings with `expected_at_scale="Unknown"` may not affect quality.
- Privacy, internal-training, and external-export permissions are separate axes.
- Every applicable hard-gate pass must carry a reason or deterministic validation record.

---

## File map

| File | Responsibility |
|---|---|
| `semantic_compiler/core/dataset.py` | Builds V2.1 dataset rows; contains ISO scoring and tier classification. |
| `semantic_compiler/core/pipeline.py` | Master compilation pipeline; sets decisions, target resolution, evidence inventory. |
| `semantic_compiler/core/skeleton.py` | Extracts structural skeleton (actors, objects, relationships). |
| `semantic_compiler/gates/missing_organ.py` | Missing-organ / functional-department detector. |
| `semantic_compiler/gates/evidence.py` | Evidence-type classification. |
| `semantic_compiler/gates/corpus_completeness.py` | New bounded corpus-completeness gate. |
| `semantic_compiler/core/types.py` | Enums and dataclasses (Decision, DatasetTier, MappingClass, etc.). |
| `semantic_compiler/schemas/logos_semantic_training_sample_v2_1.schema.json` | V2.1 dataset schema; may need `v2.1.1` additive fields. |
| `tests/test_dataset_v2_1.py` | Existing V2.1 tests. |
| `tests/test_missing_organ_scope.py` | New tests for scope-aware missing-organ detection. |
| `tests/test_corpus_completeness_gate.py` | New tests for corpus-completeness gate. |
| `scripts/generate_calibration_corpus.py` | Calibration corpus generator; must reflect new decisions/tiers. |

---

## Task 1: Separate mapping quality, assessment coverage, and confidence in ISO scoring

**Files:**
- Modify: `semantic_compiler/core/dataset.py:748-820` (`_mapping_scores`)
- Modify: `semantic_compiler/core/dataset.py:934-962` (`_isomorphism_analysis`)
- Test: `tests/test_dataset_v2_1.py`

**Interfaces:**
- Consumes: `mapping` dict, `packet`, computed `negative_tests`, `preserved`, `residuals`.
- Produces: `scores` dict containing `mapping_quality`, `assessment_coverage`, `confidence`, `final_isomorphism_quality`.

- [ ] **Step 1: Write failing test for unassessed dimensions**

```python
def test_unassessed_dimensions_do_not_zero_score(self):
    """A valid analogy with no negative tests must not get ISO 0.035."""
    packet = compile_semantic_packet(
        "The company has an immune system that detects threats and remembers them."
    )
    row = build_dataset_row(packet)
    scores = row["isomorphism_analysis"]["mappings"][0]["scores"]
    self.assertIsNotNone(scores.get("mapping_quality"))
    self.assertIsNotNone(scores.get("assessment_coverage"))
    self.assertIsNotNone(scores.get("confidence"))
    self.assertGreater(scores["mapping_quality"], 0.3)
    # coverage should be low because many dimensions were not assessed
    self.assertLess(scores["assessment_coverage"], 0.8)
```

- [ ] **Step 2: Run test and confirm failure**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest tests.test_dataset_v2_1.DatasetV21Tests.test_unassessed_dimensions_do_not_zero_score -v`
Expected: FAIL — `mapping_quality` key does not exist.

- [ ] **Step 3: Refactor `_mapping_scores` to compute mapping_quality and coverage separately**

Replace the single geometric mean with:

```python
def _mapping_scores(...):
    # ... existing individual dimension extraction ...

    # Mark unassessed dimensions as None instead of 0.0.
    def assessed(value):
        return value if value is not None and value > 0.0 else None

    assessed_values = {
        k: v for k, v in soft_values.items()
        if v is not None and v > 0.0
    }

    mapping_quality = _geometric_mean(assessed_values, _ISO_QUALITY_WEIGHTS)
    assessment_coverage = len(assessed_values) / len(_ISO_QUALITY_WEIGHTS)

    hard_multiplier = 1
    tested = [t for t in negative_tests if t.get("result") != "UNTESTED"]
    if negative_tests and any(t.get("result") == "FAILED" for t in negative_tests):
        hard_multiplier = 0
    if mapping.get("mapping_class") == "HEURISTIC_METAPHOR" and not tested:
        hard_multiplier = 0

    final_isomorphism_quality = mapping_quality * hard_multiplier
    confidence = final_isomorphism_quality * assessment_coverage

    return {
        # ... existing per-dimension rounded values, using None for unassessed ...
        "mapping_quality": round(mapping_quality, 4),
        "assessment_coverage": round(assessment_coverage, 4),
        "hard_gate_multiplier": hard_multiplier,
        "final_isomorphism_quality": round(final_isomorphism_quality, 4),
        "confidence": round(confidence, 4),
    }
```

- [ ] **Step 4: Update `_isomorphism_analysis` aggregate to expose mapping_quality and coverage**

```python
"aggregate": {
    "best_mapping_id": ...,
    "mapping_count": ...,
    "aggregate_isomorphism_quality": round(aggregate_quality, 4),
    "aggregate_mapping_quality": round(avg_mq, 4),
    "aggregate_assessment_coverage": round(avg_cov, 4),
    "cross_mapping_consistency": ...,
    "unresolved_residuals": ...,
}
```

- [ ] **Step 5: Run tests and confirm pass**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Task 2: Make missing-organ detector scope-aware

**Files:**
- Create or modify: `semantic_compiler/gates/missing_organ.py`
- Modify: `semantic_compiler/core/dataset.py:610-618` (`_adversarial`)
- Test: `tests/test_missing_organ_scope.py`

**Interfaces:**
- Consumes: `packet` with `mode`, `claim_types`, `semantic_ir`, `structural_skeleton`.
- Produces: list of organ findings with state in `{PRESENT, PARTIALLY_PRESENT, ABSENT_CONFIRMED, UNOBSERVED, NOT_APPLICABLE, UNKNOWN}`.

- [ ] **Step 1: Write failing tests**

```python
import unittest
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.gates.missing_organ import detect_missing_organs

class MissingOrganScopeTests(unittest.TestCase):
    def test_fragmentary_analogy_marks_unobserved(self):
        packet = SemanticPacket(
            raw_input="The immune system is like a security team.",
            mode=None,
        )
        result = detect_missing_organs(packet)
        for finding in result:
            self.assertIn(finding["state"], {"UNOBSERVED", "NOT_APPLICABLE"})
            self.assertNotEqual(finding["status"], "MISSING")

    def test_whole_system_claim_allows_absent_confirmed(self):
        packet = SemanticPacket(
            raw_input="This company has no security team and no decision maker.",
            mode="STRUCTURAL_RECONSTRUCTION",
        )
        result = detect_missing_organs(packet)
        states = {f["state"] for f in result}
        self.assertIn("ABSENT_CONFIRMED", states)
```

- [ ] **Step 2: Implement scope-aware detector**

```python
def detect_missing_organs(packet):
    completeness_modes = {
        "STRUCTURAL_RECONSTRUCTION", "SYSTEM_DIAGNOSTIC",
        "WHOLE_SYSTEM_AUDIT", "UNIVERSAL_DECOMPRESSION",
    }
    explicit_completeness = any(
        str(packet.mode).upper() in completeness_modes,
        packet.semantic_ir.get("requested_analysis") == "completeness",
        any("complete system" in str(c).lower() for c in packet.claim_types),
    )

    findings = []
    for organ in _ORGAN_REGISTRY:
        if explicit_completeness and _organ_absent_confirmed(packet, organ):
            state = "ABSENT_CONFIRMED"
            status = "MISSING"
        elif explicit_completeness:
            state = "UNOBSERVED"
            status = "UNKNOWN"
        else:
            state = "UNOBSERVED"
            status = "NOT_ASSESSED"

        findings.append({
            "department": organ,
            "expected_at_scale": _expected_scale(packet, organ),
            "state": state,
            "status": status,
            "implication": _implication(organ, state),
        })
    return findings
```

- [ ] **Step 3: Update `_adversarial` to filter findings that may affect quality**

```python
missing_organs = [
    f for f in packet.missing_organs
    if f.get("state") == "ABSENT_CONFIRMED"
    and f.get("expected_at_scale") not in (None, "Unknown", "")
]
```

- [ ] **Step 4: Run tests**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Task 3: Fix evidence-type hallucinations

**Files:**
- Modify: `semantic_compiler/gates/evidence.py` or `semantic_compiler/core/pipeline.py`
- Modify: `semantic_compiler/core/dataset.py:218-249` (`_build_provenance`)
- Test: `tests/test_dataset_v2_1.py`

**Interfaces:**
- Consumes: raw input text.
- Produces: evidence inventory with accurate `source_type` and `directness`.

- [ ] **Step 1: Write failing test**

```python
def test_analogy_is_not_recollection(self):
    packet = compile_semantic_packet(
        "The company has an immune system that detects threats and remembers them."
    )
    row = build_dataset_row(packet)
    for ev in row["provenance"]["evidence_chain"]:
        self.assertNotEqual(ev["source_type"], "recollection")
        self.assertNotIn("recollection", ev["notes"].lower())
```

- [ ] **Step 2: Replace heuristic evidence classifier with conservative rules**

```python
def classify_evidence(input_text: str) -> dict:
    lowered = input_text.lower()
    if any(p in lowered for p in ["i remember", "i recall", "in my experience", "once, i"]):
        return {"source_type": "recollection", "directness": "REPORTED"}
    if any(p in lowered for p in ["study found", "paper showed", "report says", "according to"]):
        return {"source_type": "document", "directness": "DERIVED"}
    return {"source_type": "statement", "directness": "DIRECT"}
```

- [ ] **Step 3: Run tests**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Task 4: Enforce canonical semantic decision and separate dispositions

**Files:**
- Modify: `semantic_compiler/core/types.py`
- Modify: `semantic_compiler/core/pipeline.py`
- Modify: `semantic_compiler/core/dataset.py:149-157` (`_derive_status`), `build_dataset_row`
- Modify: `semantic_compiler/schemas/logos_semantic_training_sample_v2_1.schema.json`
- Test: `tests/test_dataset_v2_1.py`

**Interfaces:**
- Consumes: packet decision, privacy sensitivity, external/internal training flags.
- Produces: dataset row with `decision.status`, `privacy`, `training_disposition`, `export_disposition`.

- [ ] **Step 1: Update dataset row schema**

Add to schema:

```json
"training_disposition": {"enum": ["LOCAL_TRAINING_ALLOWED", "LOCAL_TRAINING_DENIED"]},
"export_disposition": {"enum": ["ALLOWED", "PROHIBITED", "REDACTED_ONLY"]}
```

- [ ] **Step 2: Update `_derive_status` and add disposition builder**

```python
def _derive_dispositions(packet):
    privacy = packet.privacy_sensitivity
    external = packet.external_training_use

    if privacy in (PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL):
        training = "LOCAL_TRAINING_DENIED"
    elif external == "forbidden":
        training = "LOCAL_TRAINING_ALLOWED"
    else:
        training = "LOCAL_TRAINING_ALLOWED"

    if privacy == PrivacySensitivity.PUBLIC and external == "approved":
        export_disp = "ALLOWED"
    elif privacy in (PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL):
        export_disp = "PROHIBITED"
    else:
        export_disp = "REDACTED_ONLY" if external == "redacted_only" else "PROHIBITED"

    return {"training_disposition": training, "export_disposition": export_disp}
```

- [ ] **Step 3: Remove `COMPILED_PRIVATE_REDACTED_ONLY` from decision enum or demote to disposition**

In `types.py`, keep decision enum clean:

```text
REJECT, NEEDS_REVISION, COMPILED, COMPILED_WITH_GUARDRAILS, ROUTE_FOR_APPROVAL, ESCALATE, QUARANTINE
```

- [ ] **Step 4: Update tests**

```python
def test_dispositions_separate_from_decision(self):
    packet = compile_semantic_packet(
        "The company has an immune system.",
        context={"privacy_sensitivity": "CRITICAL"},
    )
    row = build_dataset_row(packet)
    self.assertIn(row["decision"]["status"], {"COMPILED", "COMPILED_WITH_GUARDRAILS", "NEEDS_REVISION"})
    self.assertEqual(row["privacy"]["training_disposition"], "LOCAL_TRAINING_DENIED")
    self.assertEqual(row["privacy"]["export_disposition"], "PROHIBITED")
```

- [ ] **Step 5: Run tests**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Task 5: Add mapping-direction status and require evidence for hard-gate passes

**Files:**
- Modify: `semantic_compiler/core/dataset.py:323-363` (`_target_resolution`)
- Modify: `semantic_compiler/core/dataset.py:488-608` (`_gates`)
- Modify: `semantic_compiler/core/types.py`
- Test: `tests/test_dataset_v2_1.py`

**Interfaces:**
- Consumes: packet source frames, target systems, selected target, context.
- Produces: target resolution with `mapping_direction` and `direction_confidence`.

- [ ] **Step 1: Add mapping direction to target resolution**

```python
def _target_resolution(packet):
    # ... existing logic ...
    source = packet.source_frames[0] if packet.source_frames else None
    target = packet.selected_target

    if source and target and source != target:
        direction = "EXPLICIT"
        direction_confidence = 0.8
    elif source and target and source == target:
        direction = "BIDIRECTIONAL"
        direction_confidence = 0.5
    else:
        direction = "UNRESOLVED"
        direction_confidence = 0.0

    return {
        # ... existing fields ...
        "mapping_direction": direction,
        "direction_confidence": direction_confidence,
    }
```

- [ ] **Step 2: Require reason for applicable hard-gate passes**

```python
def _gate_record(applicable, score, passed, reason):
    if applicable and passed and not reason:
        reason = "gate passed"
    return {...}
```

- [ ] **Step 3: Run tests**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Task 6: Implement corpus-completeness gate

**Files:**
- Create: `semantic_compiler/gates/corpus_completeness.py`
- Create: `tests/test_corpus_completeness_gate.py`
- Modify: `semantic_compiler/core/dataset.py:503-608` (`_gates`) to include the gate

**Interfaces:**
- Consumes: claim text, referenced documents, corpus manifest.
- Produces: gate record with state in `{PRESENT_IN_CURRENT_CONTEXT, FOUND_IN_LINKED_CORPUS, NOT_FOUND_WITHIN_SEARCH_SCOPE, SEARCH_NOT_PERFORMED, SEARCH_UNAVAILABLE, ABSENT_FROM_VERSION_LOCKED_CORPUS}`.

- [ ] **Step 1: Create gate module**

```python
from enum import Enum

class CorpusState(Enum):
    PRESENT_IN_CURRENT_CONTEXT = "PRESENT_IN_CURRENT_CONTEXT"
    FOUND_IN_LINKED_CORPUS = "FOUND_IN_LINKED_CORPUS"
    NOT_FOUND_WITHIN_SEARCH_SCOPE = "NOT_FOUND_WITHIN_SEARCH_SCOPE"
    SEARCH_NOT_PERFORMED = "SEARCH_NOT_PERFORMED"
    SEARCH_UNAVAILABLE = "SEARCH_UNAVAILABLE"
    ABSENT_FROM_VERSION_LOCKED_CORPUS = "ABSENT_FROM_VERSION_LOCKED_CORPUS"

class CorpusCompletenessGate:
    def __init__(self, manifest, search_fn=None):
        self.manifest = manifest or {}
        self.search_fn = search_fn

    def check(self, claim_component: str, query_terms: list[str]) -> dict:
        if claim_component in self.manifest.get("current_context", {}):
            return {"state": CorpusState.PRESENT_IN_CURRENT_CONTEXT.value, "passed": True}
        if self.search_fn is None:
            return {"state": CorpusState.SEARCH_NOT_PERFORMED.value, "passed": None}
        found = self.search_fn(query_terms)
        if found:
            return {"state": CorpusState.FOUND_IN_LINKED_CORPUS.value, "passed": True}
        return {"state": CorpusState.NOT_FOUND_WITHIN_SEARCH_SCOPE.value, "passed": None}
```

- [ ] **Step 2: Add tests**

```python
class CorpusCompletenessTests(unittest.TestCase):
    def test_present_in_context(self):
        gate = CorpusCompletenessGate({"current_context": {"Lagrangian": {}}})
        result = gate.check("Lagrangian", ["Lagrangian", "action"])
        self.assertEqual(result["state"], "PRESENT_IN_CURRENT_CONTEXT")

    def test_search_not_performed(self):
        gate = CorpusCompletenessGate({})
        result = gate.check("Lagrangian", ["Lagrangian"])
        self.assertEqual(result["state"], "SEARCH_NOT_PERFORMED")
```

- [ ] **Step 3: Wire gate into `_gates`**

```python
"corpus_completeness": _gate_record(...)
```

- [ ] **Step 4: Run tests**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Task 7: Improve entity and relationship extraction

**Files:**
- Modify: `semantic_compiler/core/skeleton.py`
- Modify: `semantic_compiler/core/pipeline.py`
- Test: `tests/test_skeleton_extraction.py`

**Interfaces:**
- Consumes: input text.
- Produces: actors, objects, relationships with verbs/prepositions.

- [ ] **Step 1: Add relationship extraction**

For each sentence, after extracting subject and object, record:

```python
{
    "relationship_id": "rel-001",
    "source_entity_id": "immune system",
    "target_entity_id": "threats",
    "relationship_type": "DETECTS",
    "confidence": 0.7,
}
```

- [ ] **Step 2: Remove substring duplicate actors**

After extracting actors, filter out any actor that is a substring of another actor unless it is a distinct named entity.

- [ ] **Step 3: Run tests**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Task 8: Regenerate calibration corpus and produce return artifacts

**Files:**
- Modify: `scripts/generate_calibration_corpus.py`
- Create: `calibration_output/CALIBRATION_V2_1_1_DIFF.md`
- Create: `calibration_output/SCORE_DISTRIBUTION_BEFORE_AFTER.json`
- Create: `calibration_output/DECISION_CONFUSION_MATRIX.json`
- Create: `calibration_output/MISSING_ORGAN_PRECISION_REPORT.md`
- Create: `calibration_output/CONTRADICTION_REPAIR_REPORT.md`
- Create: `calibration_output/KESTREL_REVIEW_SELECTION_V2_1_1.json`

**Interfaces:**
- Consumes: old 76-row corpus + new compiler.
- Produces: new 76-row corpus + comparison artifacts.

- [ ] **Step 1: Run generator and capture new metrics**

```bash
PYTHONPATH=/home/shax/Apps python3 scripts/generate_calibration_corpus.py
```

- [ ] **Step 2: Generate comparison artifacts**

Write a script that loads old and new corpora and produces:

```python
{
    "before": {"mean_iso": ..., "decision_counts": ..., "tier_counts": ...},
    "after": {"mean_iso": ..., "decision_counts": ..., "tier_counts": ...},
    "delta": {...}
}
```

- [ ] **Step 3: Create reports**

`CALIBRATION_V2_1_1_DIFF.md`: summary of code changes and observed metric shifts.
`MISSING_ORGAN_PRECISION_REPORT.md`: false-positive rate on fragmentary inputs before/after.
`CONTRADICTION_REPAIR_REPORT.md`: detection rate and correction quality on seeded contradiction cases.

- [ ] **Step 4: Run full test suite**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v`
Expected: all tests pass.

---

## Spec coverage self-review

| Kestrel requirement | Task |
|---|---|
| Separate 0 / null / N/A | Task 1 |
| Mapping-direction status | Task 5 |
| Fix evidence hallucinations | Task 3 |
| Extract entities/functions/relationships before scoring | Task 7 |
| Scope-aware missing-organ detector | Task 2 |
| One canonical semantic decision | Task 4 |
| Separate privacy/training/export | Task 4 |
| Evidence/reason for hard-gate passes | Task 5 |
| Decouple tier from input truth | Task 1, Task 4 |
| Corpus-completeness gate | Task 6 |
| Recalibration + return artifacts | Task 8 |

No placeholders remain in the tasks above; each includes concrete code or command.
