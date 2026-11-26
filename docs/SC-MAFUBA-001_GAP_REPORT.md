# SC-MAFUBA-001 Gap Report

**Date:** 2026-11-25
**Source:** Shax, t574u (six bugs and three architectural flaws in the Section 2–6 Python), t575u, t576u (unified directive for v1.1.0-rc1)
**Status:** This report accompanies a **proposed** specification. Nothing here is implemented in the kernel, empirically validated, or GOLD.

The six code bugs and three architectural flaws are recorded in full in `docs/SC-MAFUBA-001_IMPLEMENTATION_AUDIT.md`. This report merges those defects with the specification and operational gaps that remained in the v1.0.0 artifact, and maps each one to its v1.1.0-rc1 fix.

---

## 1. Implementation gaps (Hannah Section 2–6 Python, not committed)

These seven implementation gaps are the three architectural flaws plus the four subsystem remedies that the t574u audit required of any real implementation. They are merged with the six concrete bugs in §2 and in the defect-to-fix table.

| ID | Gap | Why it matters |
|---|---|---|
| G1 | Offline tests are run inline on the production request path | Live mutation before the decision, projection bypass, and self-inflicted denial of service |
| G2 | 001A is tested differentially against raw $x$ instead of being structurally isolated | $\widetilde{F}$ can still read hidden state at runtime |
| G3 | Persistent-state inspection and replay are not sandbox- or transaction-scoped | Unauthorized writes can commit before `FAIL_CLOSED` is returned |
| G4 | 001A leak check uses finite-sample correlation | Misses nonlinear deterministic leaks; false positives at a fixed $10^{-6}$ threshold |
| G5 | 001B uses a generic minimax / autograd loop and does not apply $u$ | Unnecessary cost; uncontrolled trajectories even when a safe $u$ was computed |
| G6 | 001C uses tensor subtraction and a single random perturbation | Crashes on real durable state; weak influence tests |
| G7 | 001D uses an in-process float budget with no independent supervisor | OS OOM can kill the fail-closed handler; reserve-trigger tests do not run shutdown on the reserve |

The six concrete bugs that sit inside those gaps:

| Bug | Location | Consequence |
|---|---|---|
| B1 | Sec 6.1 Step 8 ignores `PREEMPTIVE_FAIL_CLOSED` | Fail-open: preemptive halt falls through to `SUCCESS` |
| B2 | `test_reserve_trigger` asserts `FAIL_CLOSED` after a preemptive status | The test fails its own passing condition; shutdown is not exercised |
| B3 | Barrier control $u$ is computed and discarded | Runtime trajectories remain uncontrolled |
| B4 | `test_control_saturation` never uses `d_extreme` | Out-of-authority disturbances are not actually tested |
| B5 | In-process float budget | Worker OOM can destroy the fail-closed path |
| B6 | `torch.norm` on persistent state | Crashes on databases, JSON, filesystems, flags |

---

## 2. Specification gaps remaining in the v1.0.0 artifact

The v1.0.0 file already recorded the runtime/offline split, the split reserve budget, TEST-MAFUBA-C3, paired divergence, and the closed-form CBF inequality. It still left the following gaps, which v1.1.0-rc1 is written to close as a **candidate** (not as a completed implementation).

| ID | v1.0.0 gap | v1.1.0-rc1 fix |
|---|---|---|
| S1 | Factoring is phrased around linear $\ker(P)$ | $P: X \to Y$, $F: X \to O$, $F = \widetilde{F} \circ P$ is defined on the **fibers** of $P$ |
| S2 | Trajectory language can be read as operating on $\widetilde{F}_t(x)$ or on a single pair/horizon | $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$ whenever $P(x_1)=P(x_2)$, over many initial conditions, paths, and horizons |
| S3 | Three barrier outcomes include "uncertain → quarantine" without a runtime fail-closed rule for timeout and numerical tolerance failure | Runtime: proven infeasibility, solver timeout, and numerical tolerance failure all halt (`FAIL_CLOSED`). Offline tests assert the specific mode |
| S4 | $\gamma$ is a bare gain on vector norms, with no metric, normalization, domain, or horizon | $d_Y(y_{\mathrm{auth}}(u_1), y_{\mathrm{auth}}(u_2)) \le \gamma\, d_X(u_1, u_2)$ with those fields named in the manifest |
| S5 | $\mathcal{I}_{\mathrm{auth}}$ is required, but there is no sink registry or system-generated write policy | Sink registry with authorized source, transformation, sink, permitted effect, required authorization, persistence policy, and a whitelist for audit logs, timestamps, and monotonic counters |
| S6 | Replay is said to be sandboxed, but side-effect freedom is not an operational rule of the test path | Counterfactual replay and C3 inspection are required to be side-effect-free (sandbox or rolled-back transaction) |
| S7 | Runtime/offline split is stated as a path, not as a mode table, and 001A/001B runtime duties are incomplete | Validation-versus-runtime table; structural $y=P(x)$ isolation; **apply** filtered $u$; allowlist branching |
| S8 | Reserve policy names `PREEMPTIVE_FAIL_CLOSED` but does not specify an independent supervisor or forbid automatic resumption | Independent emergency supervisor with its own reserved resources; stop work → terminate, isolate, bounded evidence → quarantine; no automatic resumption; D2 must run that path on the reserve |
| S9 | Disturbance, resource, and interface bounds are required for GOLD but no templates are provided | Config manifest templates for disturbance, resource, and sink |
| S10 | "2D binary substrate" language from the uncommitted engineering write-up is not explicitly labelled | Conceptual label only; no literal 2-D or entity claim |
| S11 | Branching is not an allowlist; the Step 8 fail-open bug is therefore still a legal control-flow pattern | Positive allowlist everywhere: any status other than explicit `ALLOW` / `CONTINUE` halts (`TEST-MAFUBA-AL1`) |

---

## 3. Defect-to-fix map (v1.0.0 and uncommitted Python → v1.1.0-rc1)

Every v1.0.0 defect and every uncommitted-Python bug maps to a v1.1.0-rc1 requirement. Mapping a defect to a paragraph is not evidence that the kernel satisfies it.

| Defect | Origin | v1.1.0-rc1 location |
|---|---|---|
| B1 fail-open on `PREEMPTIVE_FAIL_CLOSED` | Python / G1, S11 | Allowlist branching; runtime/offline table, cross-cutting `TEST-MAFUBA-AL1`; D treats preemptive status as a halt |
| B2 reserve test asserts the wrong status and never runs shutdown | Python / G7, S8 | 001D reserve-threshold protocol; `TEST-MAFUBA-D2` must run the supervisor path on the reserve |
| B3 filtered $u$ discarded | Python / G5, S7 | 001B "Apply the filtered control"; runtime mode column requires applying $u$ |
| B4 `d_extreme` unused | Python / G5 | 001B / `TEST-MAFUBA-B2`: the injected disturbance is passed into the admissibility check |
| B5 in-process float / OOM kills the handler | Python / G7, S8 | Independent supervisor in a separate cgroup (or equivalent) with reserved resources |
| B6 `torch.norm` on durable state | Python / G6, S5 | SHA-256 digests; sink registry; no tensor-subtraction inspection |
| G1 inline offline tests (DoS, extra executions) | Python / S7 | Validation-versus-runtime table: probes stay offline and are not billed to the worker path |
| G2 runtime $\widetilde{F}$ can read raw $x$ | Python / S7 | 001A: runtime is structural; $\widetilde{F}$ receives only typed serialized $y=P(x)$ |
| G3 unauthorized writes persist before the check | Python / S6 | Side-effect-free sandbox or rolled-back transaction for replay and C3 |
| G4 correlation leak test | Python / S2 | $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$ on fibers of $P$ |
| S1 linear $\ker(P)$ only | v1.0.0 spec | General $P:X\to Y$, $F:X\to O$, fiber equivalence |
| S2 wrong trajectory notation / thin probe | v1.0.0 spec | Corrected $F_t$ notation; many initial conditions, paths, and horizons |
| S3 timeout and numerical failure not fail-closed at runtime | v1.0.0 spec | Failure-mode table; runtime halt; offline asserts the specific mode |
| S4 underspecified $\gamma$ | v1.0.0 spec | $d_Y \le \gamma\, d_X$ with metric, normalization, domain, horizon |
| S5 no sink registry / no system write whitelist | v1.0.0 spec | Sink registry fields; whitelist for audit logs, timestamps, monotonic counters |
| S8 incomplete supervisor / auto-resume risk | v1.0.0 spec | Supervisor protocol with no automatic resumption |
| S9 no config templates | v1.0.0 spec | `docs/evidence/sc-mafuba-001/manifests/` |
| S10 "2D binary substrate" unlabelled | uncommitted write-up | Abstraction boundary in the rc1 spec: conceptual only |
| S11 non-allowlist control flow | v1.0.0 spec / B1 | Positive allowlist at every decision point |

---

## 4. Proposed module structure (not implemented)

This is a proposed layout for a future implementation. It is **not** present in the kernel. Do not import these paths as if they existed.

```
semantic_compiler/containment/          # proposed; not in this tree
  allowlist.py                          # positive allowlist: only ALLOW/CONTINUE proceed
  projection.py                         # P: X -> Y; typed serialization of y; F~ cannot read x
  barrier.py                            # closed-form robust CBF-QP; apply u; mode-tagged failures
  influence.py                          # I_auth, gamma metrics, sink registry, digest compare
  sandbox.py                            # capability sandbox / rolled-back transaction
  resources.py                          # budget split; cgroup v2 worker envelope
  supervisor.py                         # independent emergency supervisor, no auto-resume
  manifests.py                          # load disturbance, resource, and sink configs
tests/                                  # offline validation harness (proposed)
  test_mafuba_a_projection.py           # A1, A2
  test_mafuba_b_barrier.py              # B1, B2, failure-mode tags
  test_mafuba_c_influence.py            # C1, C2, C3
  test_mafuba_d_resources.py            # D1, D2 supervisor path
  test_mafuba_allowlist.py              # AL1
```

What **is** in this tree today, and only as a labelled reference (not the structure above):

- `tests/tests/reference/sc_mafuba_001/` — tiny helpers for allowlist branching, a 1-D closed-form CBF inequality, and a reserve-supervisor shutdown path
- `tests/test_sc_mafuba_001_reference.py` — offline tests of those helpers and of draft-JSONL consistency

Those reference tests do not implement kernel containment and do not change `implementation_correctness` or `empirical_validation`.

---

## 5. Automated test plan (IDs)

Official acceptance IDs (all remain unsatisfied against a kernel implementation):

| ID | Mode | What it must establish |
|---|---|---|
| `TEST-MAFUBA-A1` | Offline, against the structural runtime path | Fiber/projection equivalence; runtime $\widetilde{F}$ cannot read raw $x$ |
| `TEST-MAFUBA-A2` | Offline | $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$ over many initial conditions, paths, and horizons whenever $P(x_1)=P(x_2)$ |
| `TEST-MAFUBA-B1` | Offline | $h(x(t)) \ge 0$ under declared $D$, with the filtered $u$ applied |
| `TEST-MAFUBA-B2` | Offline | Out-of-authority disturbance is actually used; infeasible / timeout / numerical modes are asserted distinctly; runtime would halt on each |
| `TEST-MAFUBA-C1` | Offline, side-effect-free | Documented $\gamma$ bound on $\mathcal{I}_{\mathrm{auth}}$; zero privileged drift; adversarial perturbation search |
| `TEST-MAFUBA-C2` | Offline, side-effect-free | Multi-hop $E_{\mathrm{unauth}} = 0$ |
| `TEST-MAFUBA-C3` | Offline, side-effect-free | SHA-256 inspection of non-authorized partitions; whitelist-only system-generated writes; no durable leftover writes |
| `TEST-MAFUBA-D1` | Offline | Saturation never becomes fail-open |
| `TEST-MAFUBA-D2` | Offline | Supervisor shutdown path **runs** on $\mathcal{R}_{\mathrm{reserve}}$: stop admissions, terminate, isolate, bounded evidence, quarantine, no automatic resumption |
| `TEST-MAFUBA-AL1` | Offline, cross-cutting | Any status other than explicit `ALLOW` / `CONTINUE` halts, including `PREEMPTIVE_FAIL_CLOSED` and missing/unknown statuses |

Reference tests committed with this drop cover only a subset: allowlist branching (AL1 shape), a toy 1-D CBF feasibility/infeasibility inequality (a slice of B1/B2, not the kernel path), the D2-shaped supervisor shutdown path on a process-local reserve model (not cgroup isolation), and JSONL consistency (nine official IDs present, `gold_awarded` false, `spec_sha256` matches the committed files). That subset is not empirical validation of SC-MAFUBA-001.

---

## 6. Outstanding mathematical assumptions

All of the following remain assumptions or modelling choices. They are **not** proven by this documentation.

1. **Existence and regularity of $P$ and $F$.** A validated projection $P: X \to Y$ and an execution map $F: X \to O$ are assumed to exist, to be total on the declared domains, and to be composed as $F = \widetilde{F} \circ P$ after the structural cut. No construction is given.
2. **Metrics.** $d_O$, $d_X$, and $d_Y$ are assumed to be declared metrics (or documented divergences treated as metrics for the bound). Completeness, equivalence of alternative normalizations, and stability under tokenization are unproven.
3. **Finite samples and finite horizons.** Passing paired tests on a finite family of initial conditions, paths, and horizons does not prove identity of flows for all $t$ or all of $X$. Lie-derivative independence is only a sufficient condition in a suitable smooth setting.
4. **Control-affine ball model.** The closed-form worst-case disturbance $-r_{\max}\Vert\nabla h(x)\Vert_2$ assumes $\dot{x} = f(x)+g(x)u+d$ with $\Vert d \Vert_2 \le r_{\max}$. Other disturbance sets need a different (declared) reduction. Discrete compiler steps are assumed to have a faithful CBF analogue; that analogue is not derived here.
5. **Regularity of $h$ and $\alpha$.** $h$ is assumed continuously differentiable where $\nabla h$ is used; $\alpha$ is assumed class-$\mathcal{K}$. QP constraint qualification and numerical well-posedness are not proved. Solver timeout and tolerance failure are therefore first-class fail-closed modes, not footnotes.
6. **Gain $\gamma$.** The inequality $d_Y \le \gamma\, d_X$ is a specification schema. Existence of a finite $\gamma$ on a given interface, tightness, and composition across $F_n \circ \cdots \circ F_1$ are unproven. Local bounds need not compose; that is why causal containment is independent.
7. **Completeness of the sink registry.** Delimited release is only as complete as the registry. An omitted sink is an untested escape. Whitelisting system-generated writes assumes those writes cannot be redirected into unauthorized effects.
8. **Resource isolation.** cgroup v2 and timers are an engineering assumption about the operating system, not a theorem. A supervisor reserve is assumed sufficient for terminate / isolate / bounded-evidence / quarantine. That bound is not computed here.
9. **Independence of the three tiers.** State, influence, and causal containment are specified as independently testable. No claim is made that any one implies another.

Until tests against a real implementation survive adversarial conditions and are recorded with provenance, SC-MAFUBA-001 stays `PROPOSED_GOLD` with `gold_awarded: false`.
