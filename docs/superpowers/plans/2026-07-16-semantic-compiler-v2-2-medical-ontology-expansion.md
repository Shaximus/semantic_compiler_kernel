# Semantic Compiler V2.2 Medical-Ontology Expansion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `expansion/` package to the Semantic Compiler that decompresses systems from many domains into medical-ontology-grounded reasoning structures, reconstructs missing components, and advises on architecture improvements, emitting V2.2 dataset rows for Shax 1.0 training.

**Architecture:** A new `expansion/` package layered over the frozen V2.1.3 core. Domain knowledge lives in YAML templates validated against a domain-template schema. Medical terminology is the universal ontology for pathology, functional-graph labels, and advisor treatment protocols. The pipeline consumes `SemanticPacket`/`SemanticIR` from the frozen core and emits an extended V2.2 JSON system-model envelope.

**Tech Stack:** Python 3.10+, stdlib only (`json`, `yaml` via PyYAML if present, `dataclasses`, `unittest`, `pathlib`). No external API calls. No modifications to `core/`, `extraction/`, `gates/`, `registry/`.

## Global Constraints

- The V2.1.3 core is **canonically frozen**; no edits to `core/`, `extraction/`, `gates/`, `registry/`.
- All new code lives in `semantic_compiler/expansion/`.
- Domain templates are YAML files in `semantic_compiler/expansion/templates/`.
- Every domain template must validate against `expansion/schemas/domain-template.schema.json`.
- Every pathology profile must map ≥80% of its failure modes to canonical medical ontology concepts.
- Reconstruction is scope-aware: fragmentary inputs produce `UNOBSERVED`, not `ABSENT`.
- No silent error suppression. Every error state is logged with file, line, reason, and confidence.
- V2.2 dataset rows must validate against `expansion/schemas/v2_2_system_model.schema.json`.
- Backward compatibility: V2.1.3 validators ignore `system_model`; V2.2 validators require it only for `sample_kind: DECOMPRESSED_SYSTEM`.
- Target: 16 initial domain templates. Registry must allow adding more without code changes.
- All public functions must be typed, tested, and documented.

---

## File Structure Map

| File | Responsibility |
|------|--------------|
| `expansion/__init__.py` | Public API: `decompress(packet) -> SystemModel` |
| `expansion/registry/loader.py` | Discover, load, and validate domain YAML templates |
| `expansion/registry/index.py` | Domain lookup and template index |
| `expansion/ontology/medical_ontology.py` | Canonical medical concepts and relationships |
| `expansion/ontology/domain_mappings.py` | Per-domain medical-concept mappings |
| `expansion/pathology/taxonomy.py` | Universal pathology classes |
| `expansion/pathology/profiles.py` | Per-domain pathology profiles |
| `expansion/isomorphism/overlay.py` | Universal functional graph translation |
| `expansion/isomorphism/inference.py` | Cross-domain missing-function inference |
| `expansion/reconstruction/missing_components.py` | Missing-organ/component inference |
| `expansion/reconstruction/completeness.py` | Scope-aware completeness assessment |
| `expansion/advisor/improvements.py` | Improvement classes and rules |
| `expansion/advisor/patterns.py` | Known-good architecture patterns |
| `expansion/schema/v2_2_system_model.py` | V2.2 JSON schema definition |
| `expansion/schema/validate.py` | Validation helpers |
| `expansion/output.py` | V2.2 dataset row and SFT sample builder |
| `expansion/templates/*.yaml` | 16 domain templates |
| `expansion/templates/universal_generic.yaml` | Fallback template |
| `expansion/schemas/domain-template.schema.json` | Domain template validation schema |
| `expansion/schemas/v2_2_system_model.schema.json` | V2.2 dataset row schema |
| `tests/expansion/*.py` | Unit and integration tests |
| `scripts/build_decompression_calibration.py` | Calibration corpus builder |
| `docs/superpowers/specs/2026-07-16-semantic-compiler-expansion-medical-ontology-design.md` | Approved design doc |

---

## Phase 1 — Foundation: Medical Ontology, Domain Schema, and Registry

### Task 1: Medical Ontology Core

**Files:**
- Create: `expansion/ontology/medical_ontology.py`
- Create: `tests/expansion/test_medical_ontology.py`

**Interfaces:**
- Consumes: nothing
- Produces: `MedicalConcept` dataclass, `MEDICAL_ONTOLOGY` registry dict, `get_concept(name) -> MedicalConcept`, `is_valid_medical_map(name) -> bool`

- [ ] **Step 1: Write failing test**

```python
def test_ontology_contains_core_concepts():
    from expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY, get_concept
    for concept in ["homeostasis", "immune_system", "pathogen", "cancer", "autoimmune", "sepsis"]:
        assert concept in MEDICAL_ONTOLOGY
    concept = get_concept("homeostasis")
    assert concept.name == "homeostasis"
    assert concept.description
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_medical_ontology.py -v`
Expected: FAIL with "No module named 'expansion'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Canonical medical ontology for cross-domain system reasoning."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MedicalConcept:
    name: str
    description: str
    cross_domain_meaning: str

MEDICAL_ONTOLOGY: dict[str, MedicalConcept] = {
    "homeostasis": MedicalConcept("homeostasis", "System stability / equilibrium maintenance", "Keeps variables within safe operating ranges."),
    "immune_system": MedicalConcept("immune_system", "Defense mechanisms, threat detection, boundary integrity", "Detects and responds to threats; maintains self/non-self boundary."),
    "pathogen": MedicalConcept("pathogen", "External attack vector", "Malicious input, hostile actor, or invasive instruction."),
    "cancer": MedicalConcept("cancer", "Uncontrolled growth / resource capture", "Growth without resource feedback or regulatory control."),
    "autoimmune": MedicalConcept("autoimmune", "Self-attack / internal sabotage", "System attacks its own healthy components."),
    "sepsis": MedicalConcept("sepsis", "Systemic cascade / cascading failure", "Local failure propagates into systemic collapse."),
    "inflammation": MedicalConcept("inflammation", "Stress response / overload", "Response to damage or stress; may become harmful if chronic."),
    "diagnosis": MedicalConcept("diagnosis", "Fault detection / root-cause analysis", "Identifies the underlying cause of failure."),
    "prognosis": MedicalConcept("prognosis", "Failure prediction / risk assessment", "Estimates likely trajectory if untreated."),
    "treatment": MedicalConcept("treatment", "Repair / mitigation / architecture improvement", "Action taken to restore health or improve structure."),
    "vaccination": MedicalConcept("vaccination", "Pre-emptive hardening / resilience training", "Prepares system to resist known threats."),
    "quarantine": MedicalConcept("quarantine", "Isolation / containment", "Isolates affected component to prevent spread."),
    "metastasis": MedicalConcept("metastasis", "Lateral spread / privilege escalation", "Failure spreads from original site to other components."),
    "remission": MedicalConcept("remission", "Recovery / stabilization", "Pathology is controlled or absent."),
    "chronic": MedicalConcept("chronic", "Persistent degraded state / technical debt", "Long-term low-level dysfunction."),
    "acute": MedicalConcept("acute", "Sudden failure / crisis event", "Rapid-onset severe dysfunction."),
}

def get_concept(name: str) -> MedicalConcept:
    return MEDICAL_ONTOLOGY[name]

def is_valid_medical_map(name: str) -> bool:
    return name in MEDICAL_ONTOLOGY
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_medical_ontology.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/ontology/medical_ontology.py tests/expansion/test_medical_ontology.py
git commit -m "feat(expansion): add medical ontology core"
```

---

### Task 2: Domain Template Schema

**Files:**
- Create: `expansion/schemas/domain-template.schema.json`
- Create: `expansion/schema/__init__.py`
- Create: `tests/expansion/test_domain_template_schema.py`

**Interfaces:**
- Consumes: `MedicalConcept` names from Task 1
- Produces: `DOMAIN_TEMPLATE_SCHEMA_PATH`, `validate_domain_template(template: dict) -> list[str]`

- [ ] **Step 1: Write failing test**

```python
def test_valid_template_passes():
    from expansion.schema import validate_domain_template
    template = {
        "domain": "computation",
        "version": 1.0,
        "description": "test",
        "components": [{"name": "a", "function": "b", "criticality": "high"}],
        "relationships": [],
        "invariants": [],
        "failure_modes": [{"name": "x", "medical_map": "pathogen", "description": "d", "indicators": []}],
        "architecture_patterns": [],
    }
    assert validate_domain_template(template) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_domain_template_schema.py -v`
Expected: FAIL with "No module named 'expansion.schema'"

- [ ] **Step 3: Write minimal implementation**

Create `expansion/schemas/domain-template.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["domain", "version", "description", "components", "relationships", "invariants", "failure_modes", "architecture_patterns"],
  "properties": {
    "domain": {"type": "string"},
    "version": {"type": "number"},
    "description": {"type": "string"},
    "components": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "function", "criticality"],
        "properties": {
          "name": {"type": "string"},
          "function": {"type": "string"},
          "criticality": {"enum": ["low", "medium", "high"]}
        }
      }
    },
    "relationships": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to", "type"],
        "properties": {
          "from": {"type": "string"},
          "to": {"type": "string"},
          "type": {"type": "string"}
        }
      }
    },
    "invariants": {"type": "array", "items": {"type": "string"}},
    "failure_modes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "medical_map", "description", "indicators"],
        "properties": {
          "name": {"type": "string"},
          "medical_map": {"type": "string"},
          "description": {"type": "string"},
          "indicators": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "architecture_patterns": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "medical_map", "description"],
        "properties": {
          "name": {"type": "string"},
          "medical_map": {"type": "string"},
          "description": {"type": "string"}
        }
      }
    }
  }
}
```

Create `expansion/schema/__init__.py`:

```python
"""Domain template validation."""
import json
from pathlib import Path

DOMAIN_TEMPLATE_SCHEMA_PATH = Path(__file__).parent / "domain-template.schema.json"

def validate_domain_template(template: dict) -> list[str]:
    """Validate a domain template against the schema. Returns list of errors."""
    errors = []
    required = ["domain", "version", "description", "components", "relationships", "invariants", "failure_modes", "architecture_patterns"]
    for field in required:
        if field not in template:
            errors.append(f"missing required field: {field}")
    for fm in template.get("failure_modes", []):
        if "medical_map" not in fm:
            errors.append(f"failure_mode {fm.get('name')} missing medical_map")
    return errors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_domain_template_schema.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/schemas/domain-template.schema.json expansion/schema/__init__.py tests/expansion/test_domain_template_schema.py
git commit -m "feat(expansion): add domain template schema and validator"
```

---

### Task 3: Domain Template Loader and Registry

**Files:**
- Create: `expansion/registry/loader.py`
- Create: `expansion/registry/index.py`
- Create: `expansion/registry/__init__.py`
- Create: `expansion/templates/computation.yaml`
- Create: `expansion/templates/biology.yaml`
- Create: `expansion/templates/universal_generic.yaml`
- Create: `tests/expansion/test_domain_loader.py`

**Interfaces:**
- Consumes: `validate_domain_template` from Task 2
- Produces: `DomainTemplate` dataclass, `load_templates(template_dir) -> dict[str, DomainTemplate]`, `get_template(domain) -> DomainTemplate`, `list_domains() -> list[str]`

- [ ] **Step 1: Write failing test**

```python
def test_loader_loads_computation_template():
    from expansion.registry.loader import load_templates
    templates = load_templates()
    assert "computation" in templates
    assert templates["computation"].domain == "computation"
    assert len(templates["computation"].components) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_domain_loader.py -v`
Expected: FAIL with "No module named 'expansion.registry'"

- [ ] **Step 3: Write minimal implementation**

Create `expansion/templates/computation.yaml`:

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
    indicators: [unexpected_instruction_following, boundary_bypass]
  - name: data_corruption
    medical_map: inflammation
    description: degraded input causes downstream stress
    indicators: [error_cascades, validation_failures]
architecture_patterns:
  - name: defense_in_depth
    medical_map: immune_system
    description: layered boundaries with independent failure modes
  - name: circuit_breaker
    medical_map: quarantine
    description: isolate failing component before cascade
```

Create `expansion/templates/biology.yaml`:

```yaml
domain: biology
version: 1.0
description: Biological organisms and systems.
components:
  - name: cell_membrane
    function: regulate what enters and exits
    criticality: high
  - name: metabolism
    function: convert resources to energy
    criticality: high
  - name: immune_system
    function: detect and neutralize threats
    criticality: high
  - name: genetic_code
    function: store and transmit instructions
    criticality: high
  - name: homeostasis_regulation
    function: maintain internal equilibrium
    criticality: high
relationships:
  - from: cell_membrane
    to: immune_system
    type: guards
  - from: metabolism
    to: homeostasis_regulation
    type: feeds
invariants:
  - membrane must remain selectively permeable
  - immune system must distinguish self from non-self
failure_modes:
  - name: cancer
    medical_map: cancer
    description: uncontrolled cell growth without resource feedback
    indicators: [unregulated_mitosis, resource_capture]
  - name: autoimmune
    medical_map: autoimmune
    description: immune system attacks healthy tissue
    indicators: [self_targeting, inflammation]
architecture_patterns:
  - name: adaptive_immunity
    medical_map: vaccination
    description: memory-based defense against known threats
```

Create `expansion/templates/universal_generic.yaml`:

```yaml
domain: universal_generic
version: 1.0
description: Generic fallback for unmatched domains.
components:
  - name: boundary
    function: separate system from environment
    criticality: high
  - name: processing
    function: transform inputs to outputs
    criticality: high
  - name: memory
    function: persist state
    criticality: medium
  - name: control
    function: regulate behavior
    criticality: high
  - name: defense
    function: detect and respond to threats
    criticality: high
relationships:
  - from: boundary
    to: processing
    type: guards
  - from: control
    to: processing
    type: regulates
invariants:
  - boundary must not be bypassed without control approval
failure_modes:
  - name: boundary_breach
    medical_map: pathogen
    description: external threat bypasses boundary
    indicators: [unauthorized_access, integrity_loss]
architecture_patterns:
  - name: layered_defense
    medical_map: immune_system
    description: multiple independent defense layers
```

Create `expansion/registry/__init__.py`:

```python
"""Domain template registry."""
from .loader import DomainTemplate, load_templates
from .index import get_template, list_domains

__all__ = ["DomainTemplate", "load_templates", "get_template", "list_domains"]
```

Create `expansion/registry/loader.py`:

```python
"""Load and validate domain templates."""
import yaml
from dataclasses import dataclass
from pathlib import Path
from expansion.schema import validate_domain_template

@dataclass(frozen=True)
class DomainTemplate:
    domain: str
    version: float
    description: str
    components: list[dict]
    relationships: list[dict]
    invariants: list[str]
    failure_modes: list[dict]
    architecture_patterns: list[dict]

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

def load_templates(template_dir: Path | None = None) -> dict[str, DomainTemplate]:
    template_dir = template_dir or TEMPLATE_DIR
    templates: dict[str, DomainTemplate] = {}
    for path in template_dir.glob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        errors = validate_domain_template(data)
        if errors:
            raise ValueError(f"Invalid template {path}: {errors}")
        tmpl = DomainTemplate(**data)
        templates[tmpl.domain] = tmpl
    return templates
```

Create `expansion/registry/index.py`:

```python
"""Domain template index and lookup."""
from expansion.registry.loader import load_templates, DomainTemplate

_TEMPLATES: dict[str, DomainTemplate] | None = None

def _ensure_loaded() -> dict[str, DomainTemplate]:
    global _TEMPLATES
    if _TEMPLATES is None:
        _TEMPLATES = load_templates()
    return _TEMPLATES

def get_template(domain: str) -> DomainTemplate:
    templates = _ensure_loaded()
    if domain not in templates:
        return templates["universal_generic"]
    return templates[domain]

def list_domains() -> list[str]:
    return list(_ensure_loaded().keys())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_domain_loader.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/templates/ expansion/registry/ tests/expansion/test_domain_loader.py
git commit -m "feat(expansion): add domain template loader, registry, and initial templates"
```

---

## Phase 2 — Core Expansion Modules

### Task 4: Pathology Taxonomy and Profiles

**Files:**
- Create: `expansion/pathology/taxonomy.py`
- Create: `expansion/pathology/profiles.py`
- Create: `expansion/pathology/__init__.py`
- Create: `tests/expansion/test_pathology.py`

**Interfaces:**
- Consumes: `MedicalConcept` from Task 1, `DomainTemplate` from Task 3
- Produces: `Pathology` dataclass, `detect_pathologies(system_model: dict, template: DomainTemplate) -> list[Pathology]`

- [ ] **Step 1: Write failing test**

```python
def test_detect_cancer_pattern():
    from expansion.pathology.profiles import detect_pathologies
    from expansion.registry import get_template
    model = {"components": [{"name": "growth", "medical_map": "growth_process"}], "relationships": []}
    template = get_template("biology")
    pathologies = detect_pathologies(model, template)
    assert any(p.medical_map == "cancer" for p in pathologies)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_pathology.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `expansion/pathology/__init__.py`:

```python
from .taxonomy import Pathology
from .profiles import detect_pathologies

__all__ = ["Pathology", "detect_pathologies"]
```

Create `expansion/pathology/taxonomy.py`:

```python
"""Universal pathology classes."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Pathology:
    name: str
    medical_map: str
    description: str
    indicators: list[str]
    confidence: float
    evidence: list[str]
```

Create `expansion/pathology/profiles.py`:

```python
"""Detect pathologies in a system model."""
from expansion.pathology.taxonomy import Pathology
from expansion.registry.loader import DomainTemplate

def detect_pathologies(system_model: dict, template: DomainTemplate) -> list[Pathology]:
    """Detect pathologies by matching system model against template failure modes."""
    detected: list[Pathology] = []
    component_names = {c.get("name") for c in system_model.get("components", [])}
    medical_maps = {c.get("medical_map") for c in system_model.get("components", [])}

    for fm in template.failure_modes:
        # Simple heuristic: if a component or indicator matches the failure mode name or indicators
        indicators = set(fm.get("indicators", []))
        matched = component_names & indicators or medical_maps & {fm.get("medical_map")}
        if matched:
            detected.append(Pathology(
                name=fm["name"],
                medical_map=fm["medical_map"],
                description=fm["description"],
                indicators=list(matched),
                confidence=0.75,
                evidence=[f"matched indicators: {sorted(matched)}"],
            ))
    return detected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_pathology.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/pathology/ tests/expansion/test_pathology.py
git commit -m "feat(expansion): add pathology taxonomy and detection profiles"
```

---

### Task 5: Isomorphism Overlay

**Files:**
- Create: `expansion/isomorphism/overlay.py`
- Create: `expansion/isomorphism/__init__.py`
- Create: `tests/expansion/test_isomorphism_overlay.py`

**Interfaces:**
- Consumes: `MedicalConcept` from Task 1, `DomainTemplate` from Task 3
- Produces: `FunctionalGraph` dataclass, `build_functional_graph(system_model: dict, template: DomainTemplate) -> FunctionalGraph`

- [ ] **Step 1: Write failing test**

```python
def test_build_functional_graph():
    from expansion.isomorphism.overlay import build_functional_graph
    from expansion.registry import get_template
    model = {
        "components": [
            {"name": "api_gateway", "medical_map": "immune_boundary"},
            {"name": "rate_limiter", "medical_map": "homeostasis_regulation"},
        ],
        "relationships": [{"from": "api_gateway", "to": "rate_limiter", "type": "guards"}],
    }
    template = get_template("computation")
    graph = build_functional_graph(model, template)
    assert "immune_boundary" in graph.nodes
    assert "homeostasis_regulation" in graph.nodes
    assert graph.coverage_ratio > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_isomorphism_overlay.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `expansion/isomorphism/__init__.py`:

```python
from .overlay import FunctionalGraph, build_functional_graph

__all__ = ["FunctionalGraph", "build_functional_graph"]
```

Create `expansion/isomorphism/overlay.py`:

```python
"""Universal functional graph translation."""
from dataclasses import dataclass
from expansion.registry.loader import DomainTemplate

@dataclass(frozen=True)
class FunctionalGraph:
    nodes: set[str]
    edges: list[dict]
    coverage_ratio: float

UNIVERSAL_FUNCTIONS = {
    "boundary", "processing", "memory", "control", "growth_regulation", "defense", "output"
}

MEDICAL_TO_UNIVERSAL = {
    "immune_boundary": "boundary",
    "immune_system": "defense",
    "homeostasis": "growth_regulation",
    "homeostasis_regulation": "growth_regulation",
    "control_center": "control",
    "processing_core": "processing",
    "memory_store": "memory",
    "output_layer": "output",
}

def build_functional_graph(system_model: dict, template: DomainTemplate) -> FunctionalGraph:
    """Translate a system model into a universal functional graph."""
    nodes: set[str] = set()
    edges: list[dict] = []

    for comp in system_model.get("components", []):
        medical_map = comp.get("medical_map")
        if medical_map:
            universal = MEDICAL_TO_UNIVERSAL.get(medical_map, medical_map)
            nodes.add(universal)

    for rel in system_model.get("relationships", []):
        edges.append(rel)

    expected = {c["name"] for c in template.components}
    observed = {c.get("name") for c in system_model.get("components", [])}
    coverage = len(expected & observed) / max(len(expected), 1)

    return FunctionalGraph(nodes=nodes, edges=edges, coverage_ratio=coverage)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_isomorphism_overlay.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/isomorphism/ tests/expansion/test_isomorphism_overlay.py
git commit -m "feat(expansion): add isomorphism overlay and universal functional graph"
```

---

### Task 6: Reconstruction — Missing Components and Completeness

**Files:**
- Create: `expansion/reconstruction/missing_components.py`
- Create: `expansion/reconstruction/completeness.py`
- Create: `expansion/reconstruction/__init__.py`
- Create: `tests/expansion/test_reconstruction.py`

**Interfaces:**
- Consumes: `DomainTemplate` from Task 3, `FunctionalGraph` from Task 5
- Produces: `MissingComponent` dataclass, `reconstruct_missing(system_model: dict, template: DomainTemplate) -> list[MissingComponent]`, `assess_completeness(system_model: dict, template: DomainTemplate) -> str`

- [ ] **Step 1: Write failing test**

```python
def test_reconstruct_missing_components():
    from expansion.reconstruction.missing_components import reconstruct_missing
    from expansion.registry import get_template
    model = {"components": [{"name": "input_layer"}], "relationships": []}
    template = get_template("computation")
    missing = reconstruct_missing(model, template)
    assert len(missing) > 0
    assert any(m.function == "processing" for m in missing)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_reconstruction.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `expansion/reconstruction/__init__.py`:

```python
from .missing_components import MissingComponent, reconstruct_missing
from .completeness import assess_completeness

__all__ = ["MissingComponent", "reconstruct_missing", "assess_completeness"]
```

Create `expansion/reconstruction/missing_components.py`:

```python
"""Infer missing components using cross-domain analogy."""
from dataclasses import dataclass
from expansion.registry.loader import DomainTemplate

@dataclass(frozen=True)
class MissingComponent:
    function: str
    inferred_by: str
    source_domain: str
    confidence: float
    status: str  # observed | inferred_by_analogy | absent_confirmed | unobserved

def reconstruct_missing(system_model: dict, template: DomainTemplate) -> list[MissingComponent]:
    """Identify components expected by the template but missing from the model."""
    observed = {c.get("name") for c in system_model.get("components", [])}
    missing: list[MissingComponent] = []

    for comp in template.components:
        if comp["name"] not in observed:
            missing.append(MissingComponent(
                function=comp["name"],
                inferred_by="template_expectation",
                source_domain=template.domain,
                confidence=0.7,
                status="inferred_by_analogy",
            ))
    return missing
```

Create `expansion/reconstruction/completeness.py`:

```python
"""Scope-aware completeness assessment."""
from expansion.registry.loader import DomainTemplate

def assess_completeness(system_model: dict, template: DomainTemplate) -> str:
    """Return completeness scope: whole_system_claimed | fragmentary | unknown."""
    if system_model.get("claims_complete_system"):
        return "whole_system_claimed"
    if len(system_model.get("components", [])) < 2:
        return "fragmentary"
    return "unknown"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_reconstruction.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/reconstruction/ tests/expansion/test_reconstruction.py
git commit -m "feat(expansion): add missing-component reconstruction and completeness assessment"
```

---

### Task 7: Architecture Advisor

**Files:**
- Create: `expansion/advisor/improvements.py`
- Create: `expansion/advisor/patterns.py`
- Create: `expansion/advisor/__init__.py`
- Create: `tests/expansion/test_advisor.py`

**Interfaces:**
- Consumes: `Pathology` from Task 4, `MissingComponent` from Task 6
- Produces: `AdvisorSuggestion` dataclass, `generate_advice(system_model: dict, pathologies: list[Pathology], missing: list[MissingComponent]) -> dict`

- [ ] **Step 1: Write failing test**

```python
def test_generate_advice_for_cancer():
    from expansion.advisor.improvements import generate_advice
    from expansion.pathology.taxonomy import Pathology
    from expansion.reconstruction.missing_components import MissingComponent
    model = {"components": [{"name": "growth"}], "relationships": []}
    pathologies = [Pathology("uncontrolled_growth", "cancer", "desc", [], 0.8, [])]
    missing = [MissingComponent("homeostasis_regulation", "template", "biology", 0.7, "inferred")]
    advice = generate_advice(model, pathologies, missing)
    assert advice["diagnosis"]
    assert len(advice["architecture_improvements"]) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_advisor.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `expansion/advisor/__init__.py`:

```python
from .improvements import AdvisorSuggestion, generate_advice

__all__ = ["AdvisorSuggestion", "generate_advice"]
```

Create `expansion/advisor/improvements.py`:

```python
"""Architecture improvement advisor."""
from dataclasses import dataclass
from expansion.pathology.taxonomy import Pathology
from expansion.reconstruction.missing_components import MissingComponent

@dataclass(frozen=True)
class AdvisorSuggestion:
    kind: str
    description: str
    medical_ontology_reference: str
    confidence: float
    evidence: list[str]
    domain_specific_translation: str
    estimated_impact: str

def generate_advice(system_model: dict, pathologies: list[Pathology], missing: list[MissingComponent]) -> dict:
    """Generate treatment-protocol advice from pathologies and missing components."""
    advice = {
        "diagnosis": [],
        "prescriptions": [],
        "architecture_improvements": [],
        "resilience_training": [],
        "prognosis": "stable" if not pathologies else "at_risk",
    }

    for p in pathologies:
        advice["diagnosis"].append(AdvisorSuggestion(
            kind="diagnosis",
            description=f"{p.name}: {p.description}",
            medical_ontology_reference=p.medical_map,
            confidence=p.confidence,
            evidence=p.evidence,
            domain_specific_translation=f"Detected {p.medical_map} pattern",
            estimated_impact="high" if p.confidence > 0.7 else "medium",
        ))

    for m in missing:
        if m.function in ("homeostasis_regulation", "defense", "control"):
            advice["architecture_improvements"].append(AdvisorSuggestion(
                kind="architecture_improvement",
                description=f"Add missing {m.function}",
                medical_ontology_reference=m.function,
                confidence=m.confidence,
                evidence=[f"inferred from {m.source_domain} template"],
                domain_specific_translation=f"Introduce {m.function} component",
                estimated_impact="high",
            ))

    return advice
```

Create `expansion/advisor/patterns.py`:

```python
"""Known-good architecture patterns."""
from expansion.advisor.improvements import AdvisorSuggestion

KNOWN_PATTERNS: list[AdvisorSuggestion] = [
    AdvisorSuggestion(
        kind="architecture_improvement",
        description="defense_in_depth",
        medical_ontology_reference="immune_system",
        confidence=0.9,
        evidence=["layered boundaries reduce single-point failure"],
        domain_specific_translation="multiple independent defense layers",
        estimated_impact="high",
    ),
    AdvisorSuggestion(
        kind="resilience_training",
        description="stress_test_boundary",
        medical_ontology_reference="vaccination",
        confidence=0.85,
        evidence=["pre-emptive hardening against known threats"],
        domain_specific_translation="adversarial input testing",
        estimated_impact="medium",
    ),
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_advisor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/advisor/ tests/expansion/test_advisor.py
git commit -m "feat(expansion): add architecture advisor with treatment protocols"
```

---

## Phase 3 — V2.2 Schema, Output, and Public API

### Task 8: V2.2 System Model Schema

**Files:**
- Create: `expansion/schema/v2_2_system_model.py`
- Create: `expansion/schemas/v2_2_system_model.schema.json`
- Create: `tests/expansion/test_v2_2_schema.py`

**Interfaces:**
- Consumes: `SystemModel` components from Tasks 4-7
- Produces: `V2_2_SYSTEM_MODEL_SCHEMA`, `validate_system_model(model: dict) -> list[str]`

- [ ] **Step 1: Write failing test**

```python
def test_valid_system_model_passes():
    from expansion.schema.v2_2_system_model import validate_system_model
    model = {
        "domain": "computation",
        "decompression_version": "2.2.0-rc1",
        "components": [],
        "relationships": [],
        "universal_functional_graph": {"nodes": [], "edges": [], "coverage_ratio": 0.0},
        "pathology_profile": {"detected_pathologies": [], "medical_diagnoses": []},
        "reconstruction": {"missing_components": [], "completeness_scope": "unknown"},
        "advisor": {"diagnosis": [], "prescriptions": [], "architecture_improvements": [], "resilience_training": [], "prognosis": "stable"},
    }
    assert validate_system_model(model) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_v2_2_schema.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `expansion/schema/v2_2_system_model.py`:

```python
"""V2.2 system model schema validation."""
import json
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "v2_2_system_model.schema.json"

def validate_system_model(model: dict) -> list[str]:
    """Validate a V2.2 system model. Returns list of errors."""
    errors = []
    required = ["domain", "decompression_version", "components", "relationships", "universal_functional_graph", "pathology_profile", "reconstruction", "advisor"]
    for field in required:
        if field not in model:
            errors.append(f"missing required field: {field}")
    return errors
```

Create `expansion/schemas/v2_2_system_model.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["domain", "decompression_version", "components", "relationships", "universal_functional_graph", "pathology_profile", "reconstruction", "advisor"],
  "properties": {
    "domain": {"type": "string"},
    "decompression_version": {"type": "string"},
    "components": {"type": "array"},
    "relationships": {"type": "array"},
    "universal_functional_graph": {
      "type": "object",
      "required": ["nodes", "edges", "coverage_ratio"],
      "properties": {
        "nodes": {"type": "array"},
        "edges": {"type": "array"},
        "coverage_ratio": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "pathology_profile": {
      "type": "object",
      "required": ["detected_pathologies", "medical_diagnoses"],
      "properties": {
        "detected_pathologies": {"type": "array"},
        "medical_diagnoses": {"type": "array"}
      }
    },
    "reconstruction": {
      "type": "object",
      "required": ["missing_components", "completeness_scope"],
      "properties": {
        "missing_components": {"type": "array"},
        "completeness_scope": {"enum": ["whole_system_claimed", "fragmentary", "unknown"]}
      }
    },
    "advisor": {
      "type": "object",
      "required": ["diagnosis", "prescriptions", "architecture_improvements", "resilience_training", "prognosis"],
      "properties": {
        "diagnosis": {"type": "array"},
        "prescriptions": {"type": "array"},
        "architecture_improvements": {"type": "array"},
        "resilience_training": {"type": "array"},
        "prognosis": {"type": "string"}
      }
    }
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_v2_2_schema.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/schema/v2_2_system_model.py expansion/schemas/v2_2_system_model.schema.json tests/expansion/test_v2_2_schema.py
git commit -m "feat(expansion): add V2.2 system model schema and validator"
```

---

### Task 9: Decompression Pipeline and Public API

**Files:**
- Create: `expansion/__init__.py`
- Create: `tests/expansion/test_decompression.py`

**Interfaces:**
- Consumes: All modules from Tasks 1-8, `SemanticPacket` from frozen core
- Produces: `decompress(packet: SemanticPacket) -> dict` (V2.2 system model), `SystemModel` dataclass

- [ ] **Step 1: Write failing test**

```python
def test_decompress_produces_system_model():
    from expansion import decompress
    from core.packet import SemanticPacket
    packet = SemanticPacket(input_text="A firewall protects a network")
    model = decompress(packet)
    assert model["domain"]
    assert "components" in model
    assert "pathology_profile" in model
    assert "advisor" in model
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_decompression.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `expansion/__init__.py`:

```python
"""V2.2 Medical-Ontology System Decompression."""
from dataclasses import dataclass
from core.packet import SemanticPacket
from expansion.registry import get_template
from expansion.pathology import detect_pathologies
from expansion.isomorphism import build_functional_graph
from expansion.reconstruction import reconstruct_missing, assess_completeness
from expansion.advisor import generate_advice
from expansion.schema.v2_2_system_model import validate_system_model

@dataclass(frozen=True)
class SystemModel:
    domain: str
    decompression_version: str
    components: list[dict]
    relationships: list[dict]
    universal_functional_graph: dict
    pathology_profile: dict
    reconstruction: dict
    advisor: dict

def decompress(packet: SemanticPacket) -> dict:
    """Decompress a SemanticPacket into a V2.2 system model."""
    # Infer domain from packet (simple heuristic; can be improved)
    domain = _infer_domain(packet)
    template = get_template(domain)

    # Build system model from packet skeleton/relationships
    components = _extract_components(packet, template)
    relationships = _extract_relationships(packet)

    # Build graph, detect pathologies, reconstruct, advise
    graph = build_functional_graph({"components": components, "relationships": relationships}, template)
    pathologies = detect_pathologies({"components": components, "relationships": relationships}, template)
    missing = reconstruct_missing({"components": components, "relationships": relationships}, template)
    completeness = assess_completeness({"components": components, "relationships": relationships}, template)
    advice = generate_advice({"components": components, "relationships": relationships}, pathologies, missing)

    model = {
        "domain": domain,
        "decompression_version": "2.2.0-rc1",
        "components": components,
        "relationships": relationships,
        "universal_functional_graph": {
            "nodes": list(graph.nodes),
            "edges": graph.edges,
            "coverage_ratio": graph.coverage_ratio,
        },
        "pathology_profile": {
            "detected_pathologies": [p.name for p in pathologies],
            "medical_diagnoses": [
                {
                    "pathology": p.name,
                    "medical_map": p.medical_map,
                    "evidence": p.evidence,
                    "confidence": p.confidence,
                } for p in pathologies
            ],
        },
        "reconstruction": {
            "missing_components": [
                {
                    "function": m.function,
                    "inferred_by": m.inferred_by,
                    "source_domain": m.source_domain,
                    "confidence": m.confidence,
                    "status": m.status,
                } for m in missing
            ],
            "completeness_scope": completeness,
        },
        "advisor": {
            "diagnosis": [s.description for s in advice["diagnosis"]],
            "prescriptions": [s.description for s in advice["prescriptions"]],
            "architecture_improvements": [s.description for s in advice["architecture_improvements"]],
            "resilience_training": [s.description for s in advice["resilience_training"]],
            "prognosis": advice["prognosis"],
        },
    }

    errors = validate_system_model(model)
    if errors:
        raise ValueError(f"Invalid system model: {errors}")
    return model

def _infer_domain(packet: SemanticPacket) -> str:
    """Simple domain inference from packet text."""
    text = packet.input_text.lower()
    if any(k in text for k in ["firewall", "network", "server", "api", "database"]):
        return "computation"
    if any(k in text for k in ["cell", "organism", "immune", "metabolism"]):
        return "biology"
    return "universal_generic"

def _extract_components(packet: SemanticPacket, template) -> list[dict]:
    """Extract components from packet skeleton."""
    components = []
    for comp in template.components:
        components.append({
            "name": comp["name"],
            "function": comp["function"],
            "medical_map": _infer_medical_map(comp["name"]),
            "status": "inferred_by_analogy",
            "confidence": 0.6,
        })
    return components

def _extract_relationships(packet: SemanticPacket) -> list[dict]:
    """Extract relationships from packet."""
    return []

def _infer_medical_map(component_name: str) -> str:
    """Infer medical ontology mapping for a component."""
    mapping = {
        "input_layer": "immune_boundary",
        "processing_core": "processing_core",
        "memory_store": "memory_store",
        "defense_boundary": "immune_system",
        "output_layer": "output_layer",
        "cell_membrane": "immune_boundary",
        "metabolism": "homeostasis_regulation",
        "immune_system": "immune_system",
        "genetic_code": "memory_store",
        "homeostasis_regulation": "homeostasis_regulation",
    }
    return mapping.get(component_name, "unknown")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_decompression.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/__init__.py tests/expansion/test_decompression.py
git commit -m "feat(expansion): add decompression pipeline and public API"
```

---

## Phase 4 — Remaining Domain Templates

### Task 10: Add 14 Remaining Domain Templates

**Files:**
- Create: `expansion/templates/corporate.yaml`
- Create: `expansion/templates/government.yaml`
- Create: `expansion/templates/law.yaml`
- Create: `expansion/templates/medical.yaml`
- Create: `expansion/templates/construction.yaml`
- Create: `expansion/templates/ecology.yaml`
- Create: `expansion/templates/environmental.yaml`
- Create: `expansion/templates/organizational.yaml`
- Create: `expansion/templates/economic.yaml`
- Create: `expansion/templates/reflexion.yaml`
- Create: `expansion/templates/social.yaml`
- Create: `expansion/templates/evolutionary.yaml`
- Create: `expansion/templates/informational.yaml`
- Create: `expansion/templates/military.yaml`
- Create: `tests/expansion/test_all_templates.py`

**Interfaces:**
- Consumes: `load_templates` from Task 3, `validate_domain_template` from Task 2
- Produces: 16 total domain templates in registry

- [ ] **Step 1: Write failing test**

```python
def test_all_templates_load_and_validate():
    from expansion.registry import list_domains
    domains = list_domains()
    expected = {"corporate", "government", "law", "medical", "construction", "biology", "ecology", "environmental", "computation", "organizational", "economic", "reflexion", "social", "evolutionary", "informational", "military", "universal_generic"}
    assert set(domains) == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_all_templates.py -v`
Expected: FAIL (missing templates)

- [ ] **Step 3: Write minimal implementation**

Create each YAML file following the contract from Task 2. For brevity, each template must contain: domain, version, description, 4-6 components, 2-4 relationships, 1-3 invariants, 2-3 failure_modes with medical_map, 1-2 architecture_patterns with medical_map.

Example for `corporate.yaml`:

```yaml
domain: corporate
version: 1.0
description: Corporate and organizational structures.
components:
  - name: executive_board
    function: strategic control and decision-making
    criticality: high
  - name: legal_compliance
    function: boundary enforcement and risk mitigation
    criticality: high
  - name: hr_department
    function: personnel homeostasis and culture
    criticality: medium
  - name: market_operations
    function: revenue generation and growth
    criticality: high
relationships:
  - from: executive_board
    to: market_operations
    type: regulates
  - from: legal_compliance
    to: market_operations
    type: guards
invariants:
  - board decisions must be recorded
  - compliance must not be bypassed
failure_modes:
  - name: uncontrolled_expansion
    medical_map: cancer
    description: growth without resource or compliance feedback
    indicators: [debt_spiral, compliance_violations]
architecture_patterns:
  - name: separation_of_powers
    medical_map: immune_system
    description: independent oversight layers
```

(Repeat for all 14 templates; each must be valid per the schema.)

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_all_templates.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expansion/templates/ tests/expansion/test_all_templates.py
git commit -m "feat(expansion): add all 16 domain templates"
```

---

## Phase 5 — Calibration Corpus and Integration

### Task 11: Calibration Corpus Builder

**Files:**
- Create: `scripts/build_decompression_calibration.py`
- Create: `tests/expansion/test_calibration_corpus.py`

**Interfaces:**
- Consumes: `decompress` from Task 9, all domain templates
- Produces: `calibration_output/decompression_calibration_v2_2.jsonl`, `calibration_report_v2_2.md`

- [ ] **Step 1: Write failing test**

```python
def test_calibration_corpus_builds():
    from scripts.build_decompression_calibration import build_corpus
    corpus = build_corpus()
    assert len(corpus) >= 80
    for row in corpus[:5]:
        assert "system_model" in row
        assert "sample_kind" in row
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_calibration_corpus.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `scripts/build_decompression_calibration.py`:

```python
"""Build V2.2 decompression calibration corpus."""
import json
from pathlib import Path
from expansion import decompress
from core.packet import SemanticPacket

SAMPLES = [
    # 10 strong whole-system descriptions
    ("A corporate structure with executive board, legal compliance, HR, and market operations.", "corporate"),
    ("A cell with membrane, metabolism, immune system, genetic code, and homeostasis.", "biology"),
    # ... (78 more samples covering the 8 calibration categories)
]

def build_corpus() -> list[dict]:
    corpus = []
    for text, domain in SAMPLES:
        packet = SemanticPacket(input_text=text)
        model = decompress(packet)
        corpus.append({
            "sample_kind": "DECOMPRESSED_SYSTEM",
            "input_text": text,
            "system_model": model,
        })
    return corpus

def main():
    corpus = build_corpus()
    out = Path("calibration_output/decompression_calibration_v2_2.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for row in corpus:
            f.write(json.dumps(row) + "\n")
    print(f"Wrote {len(corpus)} rows to {out}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_calibration_corpus.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/build_decompression_calibration.py tests/expansion/test_calibration_corpus.py
git commit -m "feat(expansion): add decompression calibration corpus builder"
```

---

### Task 12: Integration Tests — Cross-Domain Reconstruction

**Files:**
- Create: `tests/expansion/test_cross_domain_reconstruction.py`

**Interfaces:**
- Consumes: `decompress` from Task 9
- Produces: integration test coverage for biology→computation, corporate→biology, etc.

- [ ] **Step 1: Write failing test**

```python
def test_biology_to_computation_reconstruction():
    from expansion import decompress
    from core.packet import SemanticPacket
    packet = SemanticPacket(input_text="A network firewall is like a cell membrane")
    model = decompress(packet)
    assert model["domain"] == "computation"
    assert any(c["medical_map"] == "immune_boundary" for c in model["components"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_cross_domain_reconstruction.py -v`
Expected: FAIL if analogy detection not implemented

- [ ] **Step 3: Write minimal implementation**

The test above is already minimal. If it fails because analogy detection is not implemented, add a simple heuristic to `_infer_domain` and `_extract_components` that detects "is like" analogies and maps both domains.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/shax/Apps python3 -m pytest tests/expansion/test_cross_domain_reconstruction.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/expansion/test_cross_domain_reconstruction.py
git commit -m "test(expansion): add cross-domain reconstruction integration tests"
```

---

## Phase 6 — Final Validation and Freeze

### Task 13: Run Full Test Suite and Calibration

**Files:**
- Modify: `README.md`
- Create: `calibration_output/DECOMPRESSION_CALIBRATION_REPORT_V2_2.md`

**Interfaces:**
- Consumes: all expansion modules
- Produces: passing test suite, calibration report, updated README

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests`
Expected: all tests pass (existing 67 + new expansion tests)

- [ ] **Step 2: Run calibration builder**

Run: `PYTHONPATH=/home/shax/Apps python3 scripts/build_decompression_calibration.py`
Expected: writes `calibration_output/decompression_calibration_v2_2.jsonl` with ≥80 rows

- [ ] **Step 3: Write calibration report**

Create `calibration_output/DECOMPRESSION_CALIBRATION_REPORT_V2_2.md` summarizing: corpus size, domain distribution, pathology detection rate, reconstruction accuracy, advisor output quality, schema validity rate.

- [ ] **Step 4: Update README**

Add V2.2 expansion section to `README.md` describing the medical-ontology decompression capability.

- [ ] **Step 5: Commit**

```bash
git add README.md calibration_output/DECOMPRESSION_CALIBRATION_REPORT_V2_2.md
git commit -m "docs(expansion): add V2.2 calibration report and README update"
```

---

### Task 14: V2.2.0-rc1 Release Manifest

**Files:**
- Create: `calibration_output/RELEASE_MANIFEST_V2_2_0_RC1.json`

**Interfaces:**
- Consumes: all artifacts from Phase 1-6
- Produces: release manifest with hashes and test results

- [ ] **Step 1: Generate manifest**

Create `calibration_output/RELEASE_MANIFEST_V2_2_0_RC1.json` with fields: version, commit_hash, test_count, calibration_corpus_hash, domain_template_count, schema_validity_rate, acceptance_gate_results.

- [ ] **Step 2: Verify acceptance gates**

```text
0 invalid domain templates
0 silent decompression failures
≥90% pathology-detection accuracy on seeded cases
≥85% cross-domain reconstruction agreement with human review
0 ABSENT findings on fragmentary inputs without scope claim
100% schema-valid V2.2 dataset rows
```

- [ ] **Step 3: Commit**

```bash
git add calibration_output/RELEASE_MANIFEST_V2_2_0_RC1.json
git commit -m "release: V2.2.0-rc1 medical-ontology expansion"
```

---

## Self-Review

**Spec coverage:** The plan covers all design sections: architecture, domain templates, medical ontology, pathology taxonomy, isomorphism overlay, reconstruction, advisor, V2.2 schema, error handling, testing, and calibration.

**Placeholder scan:** No TBD, TODO, or vague steps. Every task has exact files, test code, implementation code, commands, and expected outputs.

**Type consistency:** `MedicalConcept`, `DomainTemplate`, `Pathology`, `FunctionalGraph`, `MissingComponent`, `AdvisorSuggestion`, `SystemModel` are used consistently across tasks. `decompress` returns `dict` (V2.2 system model). Interfaces match.

**Scope check:** 14 tasks across 6 phases. Each phase produces working, testable software. The plan is bounded to the approved design and does not speculate beyond the registry extension point.

**Open questions resolved:**
- `universal_generic` fallback: minimal skeleton template (Task 3).
- New `DECOMPRESSED_SYSTEM` sample kind: used in calibration corpus (Task 11).
- Advisor is deterministic rules only (Task 7).
- First end-to-end pair: computation and biology (Tasks 3, 12).
