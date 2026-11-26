# Reference helpers (not kernel enforcement)

`tests/reference/sc_mafuba_001/` contains small, dependency-light helpers used
by `tests/test_sc_mafuba_001_reference.py`.

These modules are **reference code** for offline tests of a few specification
rules (allowlist branching, a toy 1-D robust CBF inequality, and a process-local
supervisor shutdown path). They are not `semantic_compiler` containment, not a
cgroup implementation, and not an award of GOLD or a change to
`implementation_correctness` / `empirical_validation`.

`tests/reference/scc_001/` contains the SCC-001 (Symbiotic Consent Classifier)
reference used by `tests/test_scc_001_reference.py`: a deterministic rule
engine, a transparent logistic advisory scorer, a side-effect-free
counterfactual replay and an aggregator, standard library only, plus 50
**synthetic** labelled agent-integration traces (`data/synthetic_traces.jsonl`).
It is not packaged, not imported by `core/` or `expansion/`, not an enforcement
gateway, and not evidence that SCC-001 works on real systems. See
`docs/SCC-001.md`.
