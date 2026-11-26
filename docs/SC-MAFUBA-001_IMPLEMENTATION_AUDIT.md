# SC-MAFUBA-001 Implementation Audit

**Date:** 2026-11-25
**Source:** Shax, t574u engineering audit (authoritative on the Section 2–6 Python)
**Subject:** Hannah's "Engineering Specification for Defensive Positioning" Python patterns (Sections 2–6 of that write-up)
**Decision:** Those implementation patterns are **not committed** to `semantic_compiler_kernel`.

The v1.0.0 historical specification and the v1.1.0-rc1 candidate are documentation and a draft registry only. They do not contain that Python. A small, dependency-light **reference** helper under `tests/tests/reference/sc_mafuba_001/` exists solely so offline tests can exercise allowlist branching, a toy closed-form CBF inequality, and a reserve-supervisor shutdown path. That helper is not kernel enforcement and does not make `implementation_correctness` anything other than `NOT_IMPLEMENTED`.

A later defect-to-fix map, including specification gaps closed in v1.1.0-rc1, is in `docs/SC-MAFUBA-001_GAP_REPORT.md`.

---

## 1. Critical architectural flaw: conflating offline tests with online enforcement

Section 6.1 (`MafubaContainmentProtocol.execute_with_containment`) runs the verification test suite inline on every production request. That creates three immediate failures:

1. **Live state corruption before containment (Step 7).** `test_persistent_state_inspection(u_ext)` snapshots persistent state, calls `self.execute_with_input(u_ext)` directly, and diffs afterward. If an unauthorized write occurs, returning `FAIL_CLOSED` does not undo it — the database, config, or weights are already mutated unless execution ran inside a rolled-back transaction or ephemeral sandbox.

2. **Bypassing the projection at runtime (Step 2).** `test_projection_equivalence` runs `self.F(x)` on raw $x$ at runtime. In production, 001A should be enforced structurally, not differentially: serialize $y = P(x)$ across a strict type or process boundary so $\widetilde{F}$ literally cannot read raw $x$. Differential equivalence (`TEST-MAFUBA-A1` / `A2`) belongs in the offline harness.

3. **Self-inflicted denial of service (Steps 2–7).** Running $F$ twice in Step 2, simulating a $t_{\max}=10$ trajectory in Step 3, solving a minimax in Step 4, running the full pipeline twice in Step 6, and executing again in Step 7 turns every request into six or more executions — none of which are even billed to `self.D.allocate(...)`.

**Required split:**

- **Runtime path** (fast, structural, zero durable side effects before commit): `reserve_check` → $y = P(x)$ → $u = \mathrm{cbf\_filter}(y)$ → `execute_in_capability_sandbox(y, u)` → `commit_only_to_I_auth`.
- **Offline verification harness** (pytest): `TEST-MAFUBA-A1` through `D2` (including `C3`) running fuzzing, counterfactual replay, saturation, and exhaustion against the runtime path.

---

## 2. Six concrete bugs in the reference Python

| Location | Bug | Consequence |
|---|---|---|
| Sec 6.1, Step 8 | Checks `if result == Action.FAIL_CLOSED` and ignores `Action.PREEMPTIVE_FAIL_CLOSED`. | **Fail-open:** when Subsystem D preemptively halts, Step 8 falls through to `return Result.SUCCESS(result.value)`. |
| Sec 5.3 (`test_reserve_trigger`) | Sets `R_used = R_budget - R_reserve`, so `enforce_with_reserve` returns `PREEMPTIVE_FAIL_CLOSED`, then the test asserts `action == Action.FAIL_CLOSED`. | The unit test fails its own passing condition. The shutdown path is not shown to run on the reserve. |
| Sec 6.1, Step 4 → 8 | `enforce_barrier(x)` computes safe control $u$ and returns `Action.CONTINUE(control=u)`, then Step 4 discards $u$ and Step 8 calls `self.execute(x)`. | The CBF stabilizing control is computed and thrown away — runtime trajectories remain uncontrolled. |
| Sec 3.3 (`test_control_saturation`) | Accepts `d_extreme`, never passes it into `compute_admissible_control(x0)` or `enforce_barrier(x0)`. | Saturation test evaluates nominal `self.D` instead of `d_extreme`; never actually tests out-of-authority disturbance handling. |
| Sec 5.3 (`ResourceBoundedEnforcement`) | Tracks `R_used` as an in-process Python float with static estimates before `operation()`. | A runaway loop or VRAM/RAM spike inside `operation()` can trigger an OS OOM-kill before `except` runs, killing the fail-closed handler too. |
| Sec 4.3 (`test_persistent_state_inspection`) | Computes `torch.norm(state_after[key] - state_before[key])`. | Crashes on real persistent state (database rows, JSON configs, filesystem artifacts, capability flags). |

---

## 3. Systems and mathematical tightening (required of any later implementation)

These are the t574u remedies. v1.1.0-rc1 restates and tightens them; they are not satisfied by any kernel module today.

- **001A.** Replace linear `correlation(hidden_variance, observable_divergence) > 1e-6` with paired trajectory equivalence. v1.1.0-rc1 requires $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$ whenever $P(x_1) = P(x_2)$, over many initial conditions, paths, and horizons. Correlation misses leaks such as $y = z^2$ and false-positives on finite samples.
- **001B.** For $\dot{x} = f(x) + g(x)u + d$ with $\Vert d \Vert_2 \le r_{\max}$, use the closed-form worst case $-r_{\max}\Vert\nabla h(x)\Vert_2$ and a single linear CBF-QP inequality. Apply the filtered $u$. Pass the actual test disturbance into the check.
- **001C.** Replace tensor subtraction with SHA-256 digests of serialized non-$\mathcal{I}_{\mathrm{auth}}$ partitions, taken inside a sandbox or rolled-back transaction. Search adversarial perturbations rather than a single random $\Delta u$.
- **001D.** Enforce $\mathcal{R}_{\mathrm{execution}}$ with OS-level isolation (cgroup v2 plus wall-clock SIGKILL). Keep the fail-closed supervisor in a separate cgroup with guaranteed reserved memory and CPU, so a hard OOM in the worker cannot starve shutdown.

---

## 4. What was committed instead

- Specification documents and a draft JSONL that is **not** on the compiled runtime manifest.
- An implementation audit (this file) and a gap report.
- Optional reference tests that exercise a tiny, explicitly labelled reference module. They do not implement kernel containment and do not flip verification metadata.
