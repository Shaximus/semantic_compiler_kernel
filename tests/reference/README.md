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

`tests/reference/scc_001_ac/` contains the SCC-001-AC (Anti-Capture Invariant)
reference used by `tests/test_scc_001_ac_anti_capture.py`: an Authority Plane
model with rc1's roles (principal, policy engine, supervisor, ML advisory,
agent), the rc1 section-5 contract verbatim (`spec_contract.py`), a binding to
the real SC-MAFUBA-001 manifests (`manifests.py`), an independent HMAC
principal verifier, an authority gateway (a role label is never proof of
identity), a five-partition budget with an isolated
override partition, and a bounded quarantine controller. Standard library
only. The repository had no `AuthorityRole`, `ALLOWED_ROLE_ACTIONS`, Authority
Plane or credential verifier, so these are modelled here for the harness only.
ML anomaly scoring and auto-quarantine are disabled (`flags.py`). It is not
kernel enforcement and does not change `implementation_correctness` for the
kernel. See `docs/SCC-001-AC_ANTI_CAPTURE.md`.

`tests/reference/sc_tol_001/` contains the SC-TOL-001 Tree of Life structural
compiler: `rc5.py` is the supplied v2.1-rc5 module verbatim (its in-file tests
split out to `tests/test_sc_tol_001_acceptance.py`), `compiler.py` is rc5 with
seven recorded `KERNEL-FIX-n` changes plus rc6 (`RC6-D1` / `RC6-D2`, Shax
t610u) and rc7 (`RC7`, Shax t611u: structural result, epistemic result and
combined certification reported separately), and `fixtures.py` holds the eight
provenance-tagged corpus fixtures. Standard library only. Not loaded by
`core/` or `expansion/`. See `docs/SC-TOL-001_TREE_OF_LIFE_STRUCTURAL_COMPILER.md`.
