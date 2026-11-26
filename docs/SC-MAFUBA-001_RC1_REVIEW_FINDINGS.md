# SC-MAFUBA-001 v1.1.0-rc1 — Review Findings

**Date:** 2026-11-25
**Scope:** `docs/SC-MAFUBA-001_v1.1.0-rc1.md`, `docs/SC-MAFUBA-001_GAP_REPORT.md`, `docs/evidence/sc-mafuba-001/`, `tests/reference/sc_mafuba_001/`, `tests/test_sc_mafuba_001_reference.py`
**Status:** Review only. `SC-MAFUBA-001` remains `PROPOSED_GOLD`, `gold_awarded: false`. Spec files are untouched, so the SHA-256 pins in `sc_mafuba_001.jsonl` still hold. Spec amendments below are **proposals** for an rc2 and are not applied.

## 1. Coverage of the 11-item directive

All 11 items have a corresponding artifact at **specification / template level** (spec sections, gap report, module structure, test plan, registry with C3 + AL1, three manifests). v1.0.0 is preserved and hash-pinned. None of it is implemented in the kernel; the 14 offline tests exercise reference helpers only. TEST-MAFUBA-A1 through D2 do **not** exist as executable tests yet. This review checked presence and internal consistency and ran the code; it did not independently prove the mathematics.

## 2. Findings

Severity is for an eventual kernel implementation, not the reference toy.

| ID | Sev | Finding | Status |
|---|---|---|---|
| F1 | High | `toy_1d_robust_cbf` returned `CONTINUE` when `h(x) < 0` (already outside the safe set). v1.0.0 pseudocode had an explicit guard; rc1 dropped it and the spec is silent. A CBF condition gives forward invariance only from **inside** `Omega_safe`. | Ref code fixed. **Spec amendment proposed (A1).** |
| F2 | High | Non-finite input failed **open**: `x=NaN` → `CONTINUE`, `u_nom=NaN` → `CONTINUE` with `u=NaN`, `x=-inf` → `CONTINUE`. This is the `NUMERICAL_TOLERANCE_FAILURE` class the spec says must halt. | Fixed in ref code. |
| F3 | High | `ResourceBudget.admit(NaN)` returned `CONTINUE` and poisoned `r_used`; every later comparison is then `False`, so the reserve check never fires again (permanent fail-open). | Fixed in ref code. |
| F4 | Med | Allowlist accepted a `str` subclass overriding `__eq__`/`__hash__` as `ALLOW`, and raised `TypeError` on unhashable statuses. Statuses can arrive from deserialized data. | Fixed: exact `type(status) is str`, malformed → `MALFORMED_STATUS`. |
| F5 | Med | **Open spec question.** 001D permits `R_exec + R_enf + R_reserve <= R_budget` (equality allowed) but also says halt when `R_free <= R_reserve`. Work that lands exactly on the reserve is admitted and only the *next* admission halts. "Halt the moment free budget drops to the reserve" is not what happens. | Behaviour pinned by a test; **spec decision needed (A2).** |
| F6 | Med | D2 was unfalsifiable: `ShutdownRecord.reserve_used` was the literal `r_reserve`, so the test asserted a constant, and a reserve of `1e-4` still reported success. | Fixed: shutdown debits a modelled cost; short reserve yields `completed=False` / `RESERVE_INSUFFICIENT`; termination and admission-stop are never skipped. |
| F7 | Med | **Spec.** A2 uses `d_O(F_t(x1),F_t(x2)) <= eps`. A sub-`eps` difference is invisible to the test but extractable by a downstream threshold, which 001C itself names as multi-hop amplification. | **Proposed (A3).** |
| F8 | Low | **Spec.** Continuous-time `h_dot` is applied to discrete compiler steps. Assumption 4 admits the gap but derives no analogue. | **Proposed (A4).** |
| F9 | Low | `ResourceBudget` has one `r_used` counter; the spec's three-term inequality (execution, enforcement, reserve) is not represented, so enforcement cost is never billed separately. | Not fixed; belongs in the module design. |
| F10 | Low | `docs/SC-MAFUBA-001.md` index pointed at `tests/tests/reference/...`. | Fixed. |

## 3. Proposed rc2 spec amendments (not applied)

**A1 (001B).** Add a row to the failure-mode taxonomy: *Outside safe set* — `h(x) < 0` on entry → `FAIL_CLOSED`, reason `OUTSIDE_SAFE_SET`; no control is applied. Add: non-finite or ill-formed inputs to the barrier check are `NUMERICAL_TOLERANCE_FAILURE`.

**A2 (001D).** Choose one and state it:
- *(a) Admission-only:* the inequality may hold with equality; reaching `R_free == R_reserve` blocks new admissions and triggers the supervisor, but in-flight pre-admitted work may finish. This matches the current helper and the `<=` inequality.
- *(b) Strict:* require `R_exec + R_enf + R_reserve < R_budget` at admission, so landing on the reserve is never admitted.

Recommendation: (a), but make the supervisor trigger **edge-driven** (fires on the admission that reaches the reserve), not discovered on the next request.

**A3 (001A).** Declare `d_O` per observable class. For discrete outputs (routing, decisions, persisted writes) use the discrete metric with `eps = 0`. Allow `eps > 0` only for declared numeric observables, with an amplification bound from 001C. If timing is a claimed channel, `O` must include timing/resource observables.

**A4 (001B).** Add a discrete-time condition for compiler steps: `h(x_{k+1}) - h(x_k) >= -a * h(x_k)` for all `d_k` in `D`, with `0 < a <= 1`, as the normative form for step-based execution; keep the continuous form for the control-affine model.

Any edit to the rc1 spec changes its SHA-256 and requires re-pinning `provenance.spec_sha256` in the registry. Prefer a new `rc2` file over editing rc1 in place.

## 4. What this patch changes

`tests/reference/sc_mafuba_001/{allowlist,cbf,supervisor}.py`, `tests/test_sc_mafuba_001_reference.py` (7 new regression tests; one tautological D2 assertion replaced), `docs/SC-MAFUBA-001.md` (path typo), and this file. All new tests fail against the original helpers and pass against the patched ones.

## 5. Not verified here

The full CI suite (`pytest tests -q`, `unittest discover`) could not run in the review sandbox (no `jsonschema`/`pytest`, no network). Run it before merging. The 7 pre-existing MAFUBA tests and the 7 new ones pass under `unittest`.
