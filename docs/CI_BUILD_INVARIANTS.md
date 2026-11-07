# CI build invariants from the Buildcraft ontology

Added 2026-11-07 as domain template `expansion/templates/ci_build_invariants.yaml`.

This domain applies structural principles preserved by the Buildcraft compute ontology
(finite topology, resource reservation, compatibility gates, regulated refill of shared
pools, closed bypass channels, floor the lethal outcome) to continuous-integration
pipelines, local model inference, and defensive postures.

It does **not** claim literal identity with Path of Exile mechanics. It preserves
optimization structure (multiplicative stacking, diminishing returns, breakpoints,
reservation before execution) while remaining explicit about residuals: PoE builds are
static at craft time and deterministic; inference stacks reconfigure per request and
hardware scheduling is not.

## Source of the structure

- `registry/buildcraft.py` — BUILD_001 through BUILD_018, especially BUILD_001 (topology),
  BUILD_009 (compatibility), BUILD_010 (reservation), BUILD_008 (supports), BUILD_012
  (complete configuration).
- `STATIC_VS_DYNAMIC_GUARDRAIL` — the ontology-wide note that mappings preserve structure,
  not literal mechanics or dynamic scheduling.
- Patterns previously exercised in `poe_chaos_inoculation` (close the bypass, floor the
  lethal pool, regulated reservoir with deadband, budget spending against spikes) reapplied
  to CI and local inference.

## What the template is for

Use it as a checklist and vocabulary when diagnosing:

- local inference runs that OOM or throttle under concurrent load,
- CI pipelines that pass functional tests but leave attestation, privilege, or rollback open,
- support layers (quantization, speculative drafting, cache) that spend from a shared pool
  just before a spike,
- topology overcommitment when too many concurrent workloads are composed.

Do not cite `decompress()` output as a diagnosis; the engine copies template components.
Evidence must come from the actual pipeline, runtime, or host.

## Open

- No calibration samples or router keywords added in this commit; routing remains
  vocabulary-based if later extended.
- Medical-map labels are filing categories only.
