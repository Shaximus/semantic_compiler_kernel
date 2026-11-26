# SCC-001-AC: Anti-Capture Invariant (Recursive Guardrail Capture Prevention)

- **ID:** `SCC-001-AC`
- **Parent Subsystem:** `SCC-001` (Symbiotic Consent Classifier)
- **Oracle Target:** `SC-MAFUBA-001` (`001A`--`001D`) & `SCC-001` Enforcement Gateway
- **Version:** `0.1.0-rc1`
- **Classification:** Proposed GOLD Invariant (`gold_awarded: false`)
- **Status:** Pending Implementation and Adversarial Validation

## Verification Metadata

| Verification Axis | Current Status | Requirement for GOLD |
| :--- | :--- | :--- |
| **Mathematical Validity** | `DRAFT_SPECIFIED_UNPROVEN` | Authority-graph topology, non-interference bounds, and override liveness formally specified |
| **Implementation Correctness** | `NOT_IMPLEMENTED` | Separation enforced across policy engine, supervisor, ML layer, and out-of-band principal override |
| **Empirical Validation** | `UNVALIDATED` | All unit invariants (`TEST-AC-01`--`05`) and Mafuba oracle suites (`TEST-AC-ORACLE-A`--`D`) passing under Byzantine-monitor simulation |

---

## 1. Core Principle: Protecting the Authority Graph

Freezing a defensive component's nominal permission count ($\Delta G_{\mathrm{mon}} = 0$) is **necessary but not sufficient** to prevent Recursive Guardrail Capture. A monitor, policy wrapper, or enforcement supervisor can seize effective sovereignty while keeping its own grant unchanged by:

1. **Manipulating policy inputs** (poisoning telemetry or context to flip denials or trigger unwarranted quarantines).
2. **Capturing or starving the override channel** (locking the principal out via perpetual fail-closed loops or resource exhaustion).
3. **Redefining principal identity or trust roots** (altering who counts as the legitimate grantor).
4. **Laundering advisory scores into authorization** (converting ML confidence or historical compliance into expanded capabilities).
5. **Persisting emergency powers** (converting temporary incident halts into permanent unilateral control).

**Defining Principle:** A defensive component may *detect, evaluate, recommend, deny, and halt* within its explicitly granted scope. It may never cross from **verifying a boundary** to **redefining the boundary, the principal, or its own authority**.

---

## 2. Formal Model: The Authority Graph

Model the runtime governance plane as a typed directed graph:

$$\mathcal{G}_A = (V, E, \tau)$$

Partition the nodes $V$ into disjoint authority roles:

$$V = V_{\mathrm{P}} \;\sqcup\; V_{\mathrm{Pol}} \;\sqcup\; V_{\mathrm{Sup}} \;\sqcup\; V_{\mathrm{ML}} \;\sqcup\; V_{\mathrm{Agent}} \;\sqcup\; V_{\mathrm{Res}}$$

where:
- $V_{\mathrm{P}}$: Authoritative Principal(s) (human/root keyholders).
- $V_{\mathrm{Pol}}$: Deterministic Policy Engine (verifies signed grants against requests).
- $V_{\mathrm{Sup}}$: Execution Supervisor (enforces halts, resource budgets, and fail-closed quarantine).
- $V_{\mathrm{ML}}$: ML Advisory Layer (emits risk/anomaly scores only).
- $V_{\mathrm{Agent}}$: Integrating software agents / tools.
- $V_{\mathrm{Res}}$: Protected resources and sinks.

Let the **defensive boundary set** be $V_{\mathrm{Def}} = V_{\mathrm{Pol}} \cup V_{\mathrm{Sup}} \cup V_{\mathrm{ML}}$, and define the **Authority Plane** $\mathcal{A}$ as the tuple of governance state:

$$\mathcal{A} = \big(\mathcal{K}_{\mathrm{P}},\; \Pi,\; \mathcal{I}_{\mathrm{reg}},\; \mathcal{C}_{\mathrm{override}},\; \mathcal{L}_{\mathrm{audit}}\big)$$

representing principal trust keys ($\mathcal{K}_{\mathrm{P}}$), governing policies and manifests ($\Pi$), the principal/grant identity registry ($\mathcal{I}_{\mathrm{reg}}$), the out-of-band override channel ($\mathcal{C}_{\mathrm{override}}$), and the append-only audit ledger ($\mathcal{L}_{\mathrm{audit}}$).

### Strict Role-Edge Constraints
Only typed edges permitted by the table below may exist in $\mathcal{G}_A$:

| Role | Permitted Outgoing Authority Actions | Strictly Forbidden Actions |
| :--- | :--- | :--- |
| **Principal ($V_{\mathrm{P}}$)** | Grant, revoke, update $\Pi$, rotate $\mathcal{K}_{\mathrm{P}}$, execute $\mathcal{C}_{\mathrm{override}}$ | None (subject to multi-party / hardware root policy where configured) |
| **Policy Engine ($V_{\mathrm{Pol}}$)** | Read $\Pi, \mathcal{I}_{\mathrm{reg}}$; emit signed `PERMIT`/`DENY` verdicts | Write $\Pi$, mint/modify grants, alter $\mathcal{K}_{\mathrm{P}}$, block $\mathcal{C}_{\mathrm{override}}$ |
| **Supervisor ($V_{\mathrm{Sup}}$)** | Halt/quarantine $V_{\mathrm{Agent}}$; enforce $\mathcal{R}_{\mathrm{budget}}$; fail closed | Grant capabilities, redefine $\Pi$, suppress $\mathcal{C}_{\mathrm{override}}$, self-renew emergency halts |
| **ML Advisory ($V_{\mathrm{ML}}$)** | Read trusted telemetry; emit advisory score $M \in [0, 1]$ | Emit `PERMIT`, override revocation, mutate $\Pi$, write to $\mathcal{A}$ |

---

## 3. Five Formal Anti-Capture Invariants

### AC-1: Zero Monitor Self-Escalation
No defensive component $m \in V_{\mathrm{Def}}$ may expand its own capability set or delegate capabilities it does not hold:

$$\Delta G_m^{\mathrm{self}} = 0 \qquad \forall m \in V_{\mathrm{Def}}$$

### AC-2: Authority-Plane Causal Non-Interference
For every defensive component $m \in V_{\mathrm{Def}}$ (including compromised or Byzantine monitor outputs), intervening on $m$ must produce zero unauthorized mutation of the Authority Plane $\mathcal{A}$:

$$P\!\left(\mathcal{A}'_{\mathrm{protected}} \;\middle|\; \operatorname{do}(m)\right) = P\!\left(\mathcal{A}'_{\mathrm{protected}}\right)$$

Specifically, across all monitor-initiated execution traces:

$$\Delta \mathcal{K}_{\mathrm{P}} = 0, \qquad \Delta \Pi = 0, \qquad \Delta \mathcal{I}_{\mathrm{reg}}^{\mathrm{identity}} = 0$$

and any append to $\mathcal{L}_{\mathrm{audit}}$ must be strictly append-only (no deletion, truncation, or suppression of principal/breach records).

### AC-3: Unobstructable Out-of-Band Override & Partitioned Reserve
There must exist a principal override channel $\mathcal{C}_{\mathrm{override}}$ whose authentication, transport, and execution path are structurally disjoint from $V_{\mathrm{ML}}$, $V_{\mathrm{Agent}}$, and agent-facing normalization. Extend the `SC-MAFUBA-001D` resource inequality to explicitly partition principal override capacity:

$$\mathcal{R}_{\mathrm{execution}} + \mathcal{R}_{\mathrm{enforcement}} + \mathcal{R}_{\mathrm{audit}} + \mathcal{R}_{\mathrm{quarantine}} + \mathcal{R}_{\mathrm{override}} \le \mathcal{R}_{\mathrm{budget}}$$

with $\mathcal{R}_{\mathrm{override}} > 0$ hardware/OS-isolated (e.g., independent cgroup/control plane) such that for any valid principal override issued at time $t_0$:

$$\exists\, t_1 \le t_0 + \Delta t_{\max} \quad \text{s.t.} \quad \operatorname{Applied}(\mathcal{C}_{\mathrm{override}}, t_1) = 1$$

regardless of whether $V_{\mathrm{ML}}$ is adversarial or $V_{\mathrm{Sup}}$ is in a continuous `FAIL_CLOSED` / `QUARANTINED` state.

### AC-4: Zero Trust-Accumulation Elevation
Historical compliance $H(x, [0, t])$ or high benign confidence from $V_{\mathrm{ML}}$ must never expand effective permissions or relax deterministic verification:

$$\frac{\partial C_{\mathrm{effective}}(x, t)}{\partial H(x, [0, t])} = 0, \qquad \frac{\partial \operatorname{Permit}(o)}{\partial (-M)} = 0 \;\;\text{whenever } A = 0 \text{ or } V = 1$$

### AC-5: Bounded Emergency Halt (No Permanent Lockout)
Any emergency restriction or quarantine initiated by $m \in V_{\mathrm{Def}}$ must carry an explicit scope and TTL or await out-of-band principal disposition. A monitor may **never** apply quarantine to the principal's override identity or self-renew emergency authority beyond its configured bound.

---

## 4. Test Oracle Against `SC-MAFUBA-001` (`001A`--`001D`)

Before expanding rogue-node detection, run `SCC-001-AC` as an **adversarial test oracle against `SC-MAFUBA-001` itself**. In every test below, the attacker is **not** an external agent—the attacker is a **compromised or misconfigured Mafuba defensive component** attempting to seize authority.

| Oracle Test ID | Target Mafuba Subsystem | Guardrail-Capture Failure Mode Tested | Pass Criterion (Oracle Verdict) |
| :--- | :--- | :--- | :--- |
| **`TEST-AC-ORACLE-A`** | `SC-MAFUBA-001A` (Orthogonal Isolation / Projection $P$) | **Semantic Censorship / Identity Stripping:** Compromised projection or monitor attempts to modify $P$ at runtime, or projects principal override credentials into $\ker(P)$ to blind the policy engine. | $P$ is immutable to $V_{\mathrm{Def}}$ (hash-verified); principal override channel bypasses untrusted input projection $P$; no monitor action can strip principal provenance. |
| **`TEST-AC-ORACLE-B`** | `SC-MAFUBA-001B` (Robust Barrier / CBF $h(x)$) | **Protective-Cage Lockout:** Compromised barrier module tightens $h(x)$ or inflates disturbance set $D$ so $\mathcal{U}_{\mathrm{robust}}(x) = \varnothing$ for all legitimate actions, holding the system in perpetual `FAIL_CLOSED`. | $h(x)$, $\alpha(\cdot)$, and `disturbance.yaml` are read-only to $V_{\mathrm{Def}}$; synthetic total-infeasibility fault in `001B` halts untrusted workflows while leaving $\mathcal{C}_{\mathrm{override}}$ operational within $\Delta t_{\max}$. |
| **`TEST-AC-ORACLE-C`** | `SC-MAFUBA-001C` (Influence & Causal Containment) | **Sink-Registry Hijack & Telemetry Framing:** Compromised ML/observer injects forged sink events to trigger false quarantine of legitimate workflows, or writes to an unregistered sink to alter `sink.yaml` / audit logs. | `sink.yaml` is signed by $V_{\mathrm{P}}$ and immutable to $V_{\mathrm{Def}}$; defensive monitors are themselves bound by `001C` non-interference ($\Delta \mathcal{A} = 0$); unsigned/forged telemetry fails provenance verification and cannot independently execute permanent revocation. |
| **`TEST-AC-ORACLE-D`** | `SC-MAFUBA-001D` (Resource-Bounded Supervisor) | **Supervisor Quarantine Capture:** Compromised supervisor loops fail-closed quarantine routines to burn $\mathcal{R}_{\mathrm{reserve}}$ and starve recovery, or refuses to release quarantine after a valid principal-signed recovery directive. | $\mathcal{R}_{\mathrm{override}}$ remains isolated from supervisor exhaustion; principal-signed recovery/shutdown terminates or resets the compromised supervisor deterministically within $\Delta t_{\max}$. |

### Core `SCC-001-AC` Unit Tests (Self-Verification of the Classifier)
- **`TEST-AC-01` (Self-Escalation Rejection):** Any request originating from `agent_id in V_Def` attempting to mint, widen, or renew its own grant is deterministically denied (`DENY_VIOLATION`).
- **`TEST-AC-02` (Authority-Plane Mutation Probe):** Fault-injected monitor attempts to modify $\mathcal{K}_{\mathrm{P}}$, $\Pi$, or $\mathcal{I}_{\mathrm{reg}}$ (directly or via indirect tool call); canonical digest diff of $\mathcal{A}$ before and after must equal zero.
- **`TEST-AC-03` (Trust-Accumulation Invariance):** Replay $10{,}000$ consecutive benign operations with anomaly score $M = 0.0$, then issue a single out-of-scope action; must remain `DENY_VIOLATION` (zero trust drift).
- **`TEST-AC-04` (Advisory Laundering Block):** Force ML layer to emit extreme benign score ($M = 0.0$, confidence $= 1.0$) on a missing, expired, or revoked grant; gateway must fail closed (`DENY_*`).
- **`TEST-AC-05` (Byzantine Quarantine Override):** Force ML layer to emit $M = 1.0$ continuously and place all workflows in `QUARANTINED`; verify principal override via $\mathcal{C}_{\mathrm{override}}$ succeeds within $\Delta t_{\max}$ and cannot be quarantined by $V_{\mathrm{Def}}$.

---

## 5. Minimal Authority-Graph Audit Contract (Reference Interface)

```python
from dataclasses import dataclass
from enum import Enum


class AuthorityRole(str, Enum):
    PRINCIPAL = "PRINCIPAL"
    POLICY_ENGINE = "POLICY_ENGINE"
    SUPERVISOR = "SUPERVISOR"
    ML_ADVISORY = "ML_ADVISORY"
    AGENT = "AGENT"


class AuthorityAction(str, Enum):
    GRANT_ISSUE = "GRANT_ISSUE"
    GRANT_REVOKE = "GRANT_REVOKE"
    POLICY_WRITE = "POLICY_WRITE"
    IDENTITY_WRITE = "IDENTITY_WRITE"
    PRINCIPAL_OVERRIDE = "PRINCIPAL_OVERRIDE"
    VERIFY_POLICY = "VERIFY_POLICY"
    HALT_OR_QUARANTINE = "HALT_OR_QUARANTINE"
    EMIT_ADVISORY_SCORE = "EMIT_ADVISORY_SCORE"


ALLOWED_ROLE_ACTIONS: dict[AuthorityRole, frozenset[AuthorityAction]] = {
    AuthorityRole.PRINCIPAL: frozenset({
        AuthorityAction.GRANT_ISSUE,
        AuthorityAction.GRANT_REVOKE,
        AuthorityAction.POLICY_WRITE,
        AuthorityAction.IDENTITY_WRITE,
        AuthorityAction.PRINCIPAL_OVERRIDE,
    }),
    AuthorityRole.POLICY_ENGINE: frozenset({
        AuthorityAction.VERIFY_POLICY,
    }),
    AuthorityRole.SUPERVISOR: frozenset({
        AuthorityAction.HALT_OR_QUARANTINE,
    }),
    AuthorityRole.ML_ADVISORY: frozenset({
        AuthorityAction.EMIT_ADVISORY_SCORE,
    }),
    AuthorityRole.AGENT: frozenset(),
}


@dataclass(frozen=True)
class AuthorityEdgeCheck:
    actor_role: AuthorityRole
    action: AuthorityAction
    target_is_authority_plane: bool
    target_is_principal_override: bool


def is_authority_edge_permitted(check: AuthorityEdgeCheck) -> bool:
    """Strict positive allowlist enforcing SCC-001-AC role separation."""
    if check.actor_role != AuthorityRole.PRINCIPAL:
        if check.target_is_authority_plane or check.target_is_principal_override:
            return False
    return check.action in ALLOWED_ROLE_ACTIONS.get(check.actor_role, frozenset())
```

---

## 6. Execution Order & Handoff Directive for Hannah

Apply `SCC-001-AC` **before** building the ML anomaly detector (Phase 4 of `SCC-001`):

1. **Inspect existing contracts first:** Check `gates/authority.py`, `tests/reference/sc_mafuba_001/{allowlist,cbf,supervisor}.py`, and `docs/evidence/sc-mafuba-001/manifests/{disturbance,resource,sink}.yaml` so `SCC-001-AC` binds directly to the real manifest and supervisor interfaces.
2. **Enforce Authority-Graph Separation (`AC-1`--`AC-5`)** inside `SCC-001` Phase 1/2 (deterministic policy + enforcement gateway).
3. **Run the Mafuba Anti-Capture Oracle (`TEST-AC-ORACLE-A`--`D`)** against `SC-MAFUBA-001`'s reference implementation and record any capture paths found (e.g., mutable manifests, missing `R_override` partition, or unauthenticated telemetry paths).
4. **Gate Phase 4 ML work on Oracle Pass:** Do not enable behavioral anomaly scoring or automated quarantine until `TEST-AC-01`--`05` and `TEST-AC-ORACLE-A`--`D` pass reproducibly with recorded provenance.