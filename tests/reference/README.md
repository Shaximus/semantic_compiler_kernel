# Reference helpers (not kernel enforcement)

`tests/reference/sc_mafuba_001/` contains small, dependency-light helpers used
by `tests/test_sc_mafuba_001_reference.py`.

These modules are **reference code** for offline tests of a few specification
rules (allowlist branching, a toy 1-D robust CBF inequality, and a process-local
supervisor shutdown path). They are not `semantic_compiler` containment, not a
cgroup implementation, and not an award of GOLD or a change to
`implementation_correctness` / `empirical_validation`.
