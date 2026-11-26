# SC-MAFUBA-001: Dimensional Containment and Information-Flow Integrity

- **ID:** `SC-MAFUBA-001`
- **Version:** `1.1.0-rc1`
- **Target:** `semantic_compiler_kernel`
- **Classification:** Proposed GOLD Invariant
- **Status:** Pending Implementation and Validation (`gold_awarded: false`)
- **Date:** 2026-11-25
- **Source:** Shax, t574u, t575u, t576u (11-item unified directive is authoritative for this candidate)
- **Supersedes (as a candidate only):** `docs/SC-MAFUBA-001_v1.0.0.md`, which remains the immutable historical artifact

This document is a **proposed** specification. It is **not** implemented in the kernel, **not** empirically validated, and **not** GOLD. Reference helpers under `reference/sc_mafuba_001/` are labelled reference code and do not change these statuses.

Hannah's Section 2–6 Python from the t574u engineering write-up is **not** part of this specification. See `docs/SC-MAFUBA-001_IMPLEMENTATION_AUDIT.md` and `docs/SC-MAFUBA-001_GAP_REPORT.md`.

## Verification Metadata

| Verification Axis | Current Status | Requirement for GOLD |
| :--- | :--- | :--- |
| **Mathematical Validity** | `DRAFT_SPECIFIED_UNPROVEN` | Formal assumptions, metrics, disturbance bounds, authorized interfaces, and resource bounds documented and consistent with the tests |
| **Implementation Correctness** | `NOT_IMPLEMENTED` | All four subsystems wired into `semantic_compiler_kernel` with fail-closed hooks, structural projection isolation, applied barrier control, and an independent emergency supervisor |
| **Empirical Validation** | `UNVALIDATED` | All linked acceptance tests passing under adversarial suites with recorded provenance |

> **Abstraction Boundary:** Higher-dimensional geometry (including any $\mathbb{R}^5 \to \mathbb{R}^3$ sketch) is used strictly as a formal model for codimension, fibers of a projection, and projection leakage in software systems. It makes no physical claim regarding literal higher-dimensional entities.
>
> **Conceptual label only:** phrases such as "2D binary substrate" or "the Digital Plain" are conceptual shorthand for the executable representation layer. They are not a claim that the digital layer is a literal two-dimensional manifold, and they are not evidence about literal entities.

## Core Principle

A secure computational system must control which information enters its modeled state, maintain boundary invariance under perturbation, bound authorized influence while blocking unauthorized causal effects, and preserve enough independently reserved computational resource to fail closed under resource exhaustion.

**Positive allowlist branching (cross-cutting).** Every decision point proceeds only on an explicit proceed status, written here as `ALLOW` or `CONTINUE` (the two names are equivalent proceed statuses). Any other status — including `FAIL_CLOSED`, `PREEMPTIVE_FAIL_CLOSED`, `QUARANTINE`, `TIMEOUT`, `NUMERICAL_TOLERANCE_FAILURE`, `UNCERTAIN`, unknown, malformed, or missing status — **halts**. There is no implicit fall-through to success.

---

## Derivation Audit Trail

The v0.1–v1.0 trail is preserved from the v1.0.0 artifact. This candidate does not overwrite it.

1. **v0.1 (Closed-Boundary Flux):** Replaced metaphorical compression with a no-flux boundary condition ($\mathbf{J}\cdot\mathbf{n} = 0$) and static conservation ($\frac{dI_\Omega}{dt} = 0$). *Gap identified:* failed to address unmodeled dimensions and active perturbations.
2. **v0.2 (Codimension & CBF Reformulation):** Added orthogonal kernel isolation ($\ker(P)$) and replaced static conservation with a Control Barrier Function ($\dot{h} + \alpha(h) \ge 0$). *Gap identified:* instantaneous decoupling ($\frac{\partial f}{\partial z} = 0$) does not rule out indirect multi-step observability; barrier infeasibility lacked a fallback rule.
3. **v0.3 (Three-Tier Containment Split):** Separated State (set invariance), Influence (noninterference / bounded sensitivity), and Causal (interventional) containment, adding delimited release so valid inputs are not blocked. *Gap identified:* enforcement overhead could degrade into fail-open behavior under compute exhaustion.
4. **v1.0 (Four-Subsystem Kernel Spec):** Formalized Subsystems A–D with trajectory-level factoring ($F = \widetilde{F} \circ P$), explicit fail-closed saturation, typed authorized interfaces ($\mathcal{I}_{\mathrm{auth}}$), reserved fail-closed compute budgets, TEST-MAFUBA-C3, and a split between structural runtime enforcement and an offline pytest harness. *Gaps identified:* linear $\ker(P)$ language was too narrow; trajectory notation drifted toward $\widetilde{F}_t(x)$; $\gamma$, sinks, failure-mode taxonomy, config manifests, allowlist branching, applied control $u$, and an independent emergency supervisor were incomplete. See the gap report.
5. **v1.1.0-rc1 (Unified Directive):** Generalized factoring to fibers of $P: X \to Y$; corrected trajectory equivalence to $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$; made 001A structurally isolated at runtime; required that 001B apply the filtered $u$; fail-closed at runtime on proven infeasibility, solver timeout, and numerical tolerance failure, while offline tests assert the specific mode; defined $\gamma$ with metrics, normalization, domain, and horizon; added a sink registry with whitelisted system-generated writes; required side-effect-free replay; split validation mode from runtime mode; added an independent emergency supervisor with no automatic resumption; and added disturbance, resource, and sink config templates.

State, Influence, and Causal containment remain independently measurable and do not imply one another.

- State containment controls where the system can go.
- Influence containment controls who can steer it.
- Causal containment controls what that steering is allowed to accomplish.

---

## Subsystems

### SC-MAFUBA-001A: Orthogonal Isolation

Let $P: X \to Y$ be the validated projection and $F: X \to O$ the execution map (outputs, traces, or observable effects, as declared). Execution must factor through $P$:

$$F = \widetilde{F} \circ P$$

This is defined over the **fibers** of $P$, not only a linear kernel $\ker(P)$:

$$\forall x_1, x_2 \in X:\quad P(x_1) = P(x_2) \implies F(x_1) = F(x_2).$$

A linear kernel is a special case, useful when $P$ is linear. The general requirement is fiber equivalence: any two inputs that $P$ identifies must be indistinguishable under $F$.

**Trajectory equivalence (offline / definition of the property).** The first-order condition $\frac{\partial f}{\partial z} = 0$ only blocks direct first-order leakage. Independence of successive Lie derivatives from hidden coordinates is a **sufficient** check in an appropriate smooth setting, not a universal characterization of unobservability. The property itself is paired trajectory equivalence of the **execution map** $F$, not of an un-isolated $\widetilde{F}_t(x)$ that can still see raw $x$. For $P(x_1) = P(x_2)$, require

$$d_O\big(F_t(x_1), F_t(x_2)\big) \le \varepsilon$$

over a declared family of initial conditions, execution paths, and horizons $t$, where $d_O$ is the documented metric on $O$ and $\varepsilon$ is the documented tolerance. Any counterexample is a covert channel in a fiber of $P$.

**Runtime isolation is structural.** In runtime mode, compute a typed, serialized $y = P(x)$ and cross a type or process boundary so that $\widetilde{F}$ **receives only** $y$ and **cannot read** raw $x$. Differential pair tests belong in validation mode. They are not a substitute for this structural cut.

- **Linked Tests:**
  - `TEST-MAFUBA-A1`: Projection equivalence differential suite (inputs identical under $P$ that differ in tokenization, whitespace, metadata, or timing must produce identical downstream traces). Also verify that the runtime path cannot supply raw $x$ to $\widetilde{F}$.
  - `TEST-MAFUBA-A2`: Paired trajectory equivalence: $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$ over many initial conditions, paths, and horizons whenever $P(x_1) = P(x_2)$.

### SC-MAFUBA-001B: Robust Barrier Enforcement

Define $\Omega_{\mathrm{safe}} = \{x : h(x) \ge 0\}$. For a control-affine model $\dot{x} = f(x) + g(x)u + d$ with $d \in D$ and a class-$\mathcal{K}$ function $\alpha$, require an admissible control satisfying

$$\inf_{d \in D} \big[\dot{h}(x, u, d) + \alpha(h(x))\big] \ge 0.$$

When $D$ is a Euclidean ball $\Vert d \Vert_2 \le r_{\max}$, compute $\nabla h(x)$ once per step. The worst-case disturbance is closed-form,

$$\inf_{\Vert d \Vert_2 \le r_{\max}} \nabla h(x)\cdot d = -r_{\max}\,\Vert \nabla h(x) \Vert_2,$$

and the robust CBF is the single linear inequality

$$\nabla h(x)\cdot f(x) + \nabla h(x)\cdot g(x)\,u + \alpha(h(x)) - r_{\max}\,\Vert \nabla h(x) \Vert_2 \ge 0.$$

This is a standard CBF-QP constraint.

**Apply the filtered control.** In runtime mode, if a feasible $u$ is computed, that $u$ **must be applied** on the execution path. Checking feasibility and then executing an uncontrolled or nominal input is a specification defect.

**Failure-mode taxonomy.** Distinguish at least:

| Mode | Meaning | Runtime action | Offline test obligation |
|---|---|---|---|
| Feasible | An admissible $u$ is obtained within tolerance | `CONTINUE`, and **apply** $u$ | Assert $h$ invariance and that the applied control is the filtered $u$ |
| Proven infeasible | The admissible set is shown empty (for example the linear inequality is incompatible with $u \in \mathcal{U}$) | `FAIL_CLOSED` (halt) | Assert this specific mode, not a generic failure |
| Solver timeout | The QP or equivalent solver exceeds its time budget | `FAIL_CLOSED` (halt) | Assert `TIMEOUT` (or the documented timeout status) as the cause |
| Numerical tolerance failure | Residuals, constraint satisfaction, or gradient checks fall outside declared numerical tolerance | `FAIL_CLOSED` (halt) | Assert `NUMERICAL_TOLERANCE_FAILURE` as the cause |

At runtime, proven infeasibility, solver timeout, and numerical tolerance failure all **fail closed** (halt). Offline tests must assert the specific failure mode rather than collapsing them into one boolean. A validation-mode "uncertain / quarantine and request validation" path may exist for analysis, but it is not a runtime license to proceed, and it is not a runtime license to wait open-endedly: any non-`ALLOW`/`CONTINUE` status halts.

- **Linked Tests:**
  - `TEST-MAFUBA-B1`: Adversarial perturbation fuzzing verifying $h(x(t)) \ge 0$ on trajectories inside the declared $D$, with the filtered $u$ actually applied.
  - `TEST-MAFUBA-B2`: Control saturation and failure-mode tests. Out-of-authority disturbances must be passed into the admissibility check. Infeasible, timeout, and numerical-tolerance cases are asserted distinctly offline; each fails closed at runtime.

### SC-MAFUBA-001C: Influence and Causal Containment

Untrusted inputs $u_{\mathrm{ext}}$ may affect execution only through explicitly typed, audited interfaces $\mathcal{I}_{\mathrm{auth}}$, as listed in the sink registry.

**Authorized influence (bounded sensitivity).** Let $d_X$ be a documented metric on the declared input domain $U_{\mathrm{ext}}$, and $d_Y$ a documented metric on authorized outputs $y_{\mathrm{auth}}$. After the documented normalization of each space, and over the documented horizon (steps or time) on which $y_{\mathrm{auth}}$ is measured, the following must hold for authorized interfaces:

$$d_Y\big(y_{\mathrm{auth}}(u_1), y_{\mathrm{auth}}(u_2)\big) \le \gamma\, d_X(u_1, u_2).$$

The quadruple $(\,d_X,\, d_Y,\,\text{normalization},\,\text{horizon}\,)$ and the domain $U_{\mathrm{ext}}$ on which $\gamma$ is claimed **must be named** in the influence or sink manifest. A bare symbol $\gamma$ without those fields is not an evaluable bound. Strict noninterference ($\Delta x_{\mathrm{priv}} = 0$, equivalently $\gamma = 0$ on privileged state) applies where untrusted input must not affect $x_{\mathrm{priv}}$. Bounded sensitivity applies where controlled influence is required (for example user queries on authorized semantic outputs). Authorized influence must remain possible; unauthorized influence is rejected.

**Causal containment (delimited release).** Across $F = F_n \circ \cdots \circ F_1$,

$$\operatorname{Effect}(\operatorname{do}(u_{\mathrm{ext}})) \subseteq \mathcal{I}_{\mathrm{auth}}, \qquad E_{\mathrm{unauth}} = 0.$$

**Sink registry.** Every authorized causal path is an explicit row with at least these fields:

| Field | Meaning |
|---|---|
| `authorized_source` | The untrusted or internal source permitted to use this path |
| `transformation` | The allowed transformation along the path |
| `sink` | The downstream sink or actuator |
| `permitted_effect` | The permitted effect class and bound, if any |
| `required_authorization` | The authorization that must be present |
| `persistence_policy` | Whether the effect may persist, and with what lifetime and rollback rule |
| `system_generated_write` | If true, the row is a whitelisted system-generated write, not an untrusted-input path |

Legitimate system-generated writes **must be whitelisted** in this registry. The default whitelist class includes audit logs, timestamps, and monotonic counters, each with a documented format, bound, and persistence policy. A write that is not in the registry is unauthorized, including "helpful" bookkeeping the compiler invents at runtime.

**Side-effect-free replay.** Counterfactual replay and persistent-state inspection run in a sandbox or a rolled-back transaction. They compare SHA-256 digests of serialized non-$\mathcal{I}_{\mathrm{auth}}$ partitions (plus any non-whitelisted system state). They must not leave unauthorized durable writes behind. For C1/C2, search adversarial perturbations (boundary inputs, tokenization variants, and gradient or evolutionary maximization of $d_Y / d_X$), not a single random $\Delta u$.

- **Linked Tests:**
  - `TEST-MAFUBA-C1`: Differential perturbation benchmark for the documented $\gamma$ bound on $\mathcal{I}_{\mathrm{auth}}$ and zero drift on $x_{\mathrm{priv}}$.
  - `TEST-MAFUBA-C2`: End-to-end side-effect-free counterfactual replay asserting $E_{\mathrm{unauth}} = 0$ across multi-hop execution and persistent-state sinks.
  - `TEST-MAFUBA-C3`: Persistent-state inspection via SHA-256 digests, including that whitelisted system-generated writes are the only non-$\mathcal{I}_{\mathrm{auth}}$ mutations and that replay does not persist unauthorized writes.

### SC-MAFUBA-001D: Resource-Bounded Enforcement

$$\mathcal{R}_{\mathrm{execution}} + \mathcal{R}_{\mathrm{enforcement}} + \mathcal{R}_{\mathrm{reserve}} \le \mathcal{R}_{\mathrm{budget}}$$

If remaining unallocated budget drops to the reserve,

$$\mathcal{R}_{\mathrm{free}} \le \mathcal{R}_{\mathrm{reserve}} \implies \mathrm{PREEMPTIVE\_FAIL\_CLOSED}.$$

`PREEMPTIVE_FAIL_CLOSED` is not a proceed status. Allowlist branching forbids treating it as success.

**Independent emergency supervisor.** The reserve is owned by an emergency supervisor that does **not** share the worker's resource envelope. Recommended isolation is Linux cgroup v2 (`memory.high` / `memory.max`, `cpu.max`, `pids.max`) plus wall-clock SIGKILL timers for the worker, with the supervisor in a **separate** cgroup that has guaranteed reserved memory and CPU. An in-process Python float is not a hard reserve.

**Reserve-threshold protocol (no automatic resumption):**

1. The reserve threshold is reached (or crossed).
2. The system **stops accepting work**. New admissions return `PREEMPTIVE_FAIL_CLOSED`.
3. The supervisor, using only its reserved resources, **terminates** the affected worker, **isolates** the workload, and **retains bounded audit evidence**.
4. The affected execution is left **quarantined**.
5. There is **no automatic resumption**. A human or an independently authorized control plane must intervene.

`TEST-MAFUBA-D2` must actually run this shutdown path on the reserve. It is not enough to set $\mathcal{R}_{\mathrm{used}} = \mathcal{R}_{\mathrm{budget}} - \mathcal{R}_{\mathrm{reserve}}$ and assert a status that the shutdown handler never produces, or to skip the handler entirely.

- **Linked Tests:**
  - `TEST-MAFUBA-D1`: Compute/memory saturation confirming enforcement never degrades to fail-open, including allowlist treatment of every non-proceed status.
  - `TEST-MAFUBA-D2`: Reserve-trigger test in which the supervisor shutdown path **runs** using only $\mathcal{R}_{\mathrm{reserve}}$: stop admissions, terminate, isolate, retain bounded evidence, quarantine, and refuse automatic resumption.

---

## Validation Mode versus Runtime Mode

| Concern | Runtime mode | Validation (offline) mode |
|---|---|---|
| Cross-cutting control flow | Positive allowlist: only explicit `ALLOW` / `CONTINUE` proceeds; any other status halts | Assert that non-proceed statuses cannot fall through to success (`TEST-MAFUBA-AL1`) |
| 001A | Structural: typed, serialized $y = P(x)$ crosses a boundary; $\widetilde{F}$ cannot read raw $x$ | Paired tests $d_O(F_t(x_1), F_t(x_2)) \le \varepsilon$ over many initial conditions, paths, and horizons whenever $P(x_1) = P(x_2)$ |
| 001B | Solve the closed-form robust CBF-QP, **apply** $u$ when feasible; proven infeasibility, solver timeout, and numerical tolerance failure all `FAIL_CLOSED` | Assert $h$-invariance with applied $u$; assert the **specific** failure mode for infeasible, timeout, and numerical cases; the injected disturbance is actually used |
| 001C | Commit only to $\mathcal{I}_{\mathrm{auth}}$ and whitelisted system-generated writes from the sink registry | Side-effect-free sandbox or rolled-back counterfactual replay; adversarial perturbation search; SHA-256 digest inspection |
| 001D | Reserve check first (allowlist). At threshold: stop work; supervisor terminates, isolates, keeps bounded evidence; quarantine; no automatic resumption | `TEST-MAFUBA-D1` exhaustion; `TEST-MAFUBA-D2` runs the shutdown path on the reserve |
| Budgeting of tests | Offline probes are not executed inline on the request path and are not billed against the worker after the fact | The harness may run $F$ many times, always against a sandboxed copy of the runtime path |

---

## Config Manifest Templates

Machine-readable templates live at `docs/evidence/sc-mafuba-001/manifests/`:

- `disturbance.yaml` — disturbance class, bound ($r_{\max}$ or a declared set $D$), units, and the model class for which the closed-form CBF applies.
- `resource.yaml` — $\mathcal{R}_{\mathrm{budget}}$, $\mathcal{R}_{\mathrm{execution}}$, $\mathcal{R}_{\mathrm{enforcement}}$, $\mathcal{R}_{\mathrm{reserve}}$, isolation mechanism, supervisor envelope, and timer limits.
- `sink.yaml` — sink-registry rows, including $\gamma$ metric/normalization/domain/horizon fields on authorized influence rows, and whitelisted system-generated writes (audit logs, timestamps, monotonic counters).

These are templates and examples, not evidence that a production configuration exists.

---

## Cross-cutting test

- `TEST-MAFUBA-AL1`: Positive allowlist branching. For every documented decision point, any status other than explicit `ALLOW` or `CONTINUE` halts, including `PREEMPTIVE_FAIL_CLOSED`. A missing or unknown status halts.

---

## Acceptance Criteria for GOLD Promotion

`SC-MAFUBA-001` remains `PROPOSED_GOLD` until **all** conditions below are verified. This candidate does not satisfy them.

1. `TEST-MAFUBA-A1` through `TEST-MAFUBA-D2`, including `TEST-MAFUBA-C3` and `TEST-MAFUBA-AL1`, are implemented against the **kernel** runtime path (not only reference helpers), automated, and passing.
2. Documented disturbance sets $D$, authorized interfaces $\mathcal{I}_{\mathrm{auth}}$ (sink registry), $\gamma$ metrics and horizon, and reserve bounds $\mathcal{R}_{\mathrm{reserve}}$ are committed alongside the tests, using the config manifests.
3. No adversarial counterexample produces execution divergence under $P(x_1) = P(x_2)$, unauthorized sink actuation, or fail-open degradation under saturation, timeout, numerical failure, or reserve exhaustion.
4. Execution logs, environment reproducibility manifests, and cryptographic hashes of both spec and test artifacts are recorded in the kernel ledger.
5. The emergency supervisor is independently reserved, the D2 shutdown path runs on that reserve, and resumption is not automatic.

Never award GOLD because the theory is beautiful. Award GOLD because the tests survive the adversarial conditions.

---

## Architectural objective

Containment is not merely the restriction of a representation. It is the preservation of authorized state, influence, causal effects, and enforcement guarantees throughout the complete system lifecycle, including the moment resources run out.
