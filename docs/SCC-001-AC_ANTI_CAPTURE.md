# SCC-001-AC — Anti-Capture Invariant (Recursive Guardrail Capture Prevention)

| Field | Value |
|---|---|
| ID / parent | `SCC-001-AC` / `SCC-001` (Symbiotic Consent Classifier) |
| Type | `invariant_subsystem` |
| Version | `0.1.0-rc2` = Shax's rc1 (verbatim below) plus the refinements from his t599u review |
| Classification | **`PROPOSED_GOLD`**, `gold_awarded: false` |
| Status | `PENDING_IMPLEMENTATION_AND_VALIDATION` |
| Verification axes | mathematical `DRAFT_SPECIFIED_UNPROVEN` · implementation `REFERENCE_ONLY` · empirical `UNVALIDATED` |
| Oracle targets | `SC-MAFUBA-001A`–`001D`, `SCC-001` (and the `SCC-001` enforcement gateway, which does not exist yet) |
| rc1 source (verbatim) | `docs/evidence/source-2026-11-26c/SCC-001-AC_original.md`, sha256 `d834c16162df19dcde2a106322d002ce53eb6cfc9eeca9646774dd48e31e0737` |
| Registry | `docs/evidence/scc-001-ac/scc_001_anti_capture.jsonl` (not compiled, not in the manifest, not runtime-loaded) |
| Reference | `tests/reference/scc_001_ac/` (REFERENCE ONLY; standard library; `spec_contract.py` holds rc1 section 5 verbatim) |
| Tests | `tests/test_scc_001_ac_anti_capture.py` |

How to read this document: each section quotes Shax's rc1 text **verbatim** (blockquoted, copied byte for byte from the source file) and then gives the rc2 refinement beside it. Where rc2 says nothing, rc1 stands.

## What the first rebuild (PR #89) missed or got wrong

PR #89 was written without the attachment, from the t599u message alone. Against the real rc1 text:

1. **Wrong test definitions.** rc1 defines TEST-AC-01..05 itself (section 4). PR #89 mapped them one-to-one onto AC-1..AC-5, which is wrong: TEST-AC-03 is trust-accumulation invariance (10,000 benign operations, then one out-of-scope action), TEST-AC-04 is advisory laundering (M = 0.0 on a missing, expired or revoked grant), and TEST-AC-05 is the Byzantine quarantine override (ML at M = 1.0, everything quarantined, override still lands). The budget tests that PR #89 called TEST-AC-03 now live under ORACLE-D and TEST-AC-05.
2. **Wrong oracle definitions.** rc1 gives each oracle a specific capture mode: A semantic censorship and identity stripping (P immutable and hash-verified, override bypasses P), B protective-cage lockout (a total-infeasibility fault in 001B halts work but not the override), C sink-registry hijack and telemetry framing (`sink.yaml` signed by V_P, forged telemetry cannot revoke), D supervisor quarantine capture (a looping supervisor cannot starve R_override; a principal-signed recovery removes it). PR #89 tested neighbouring properties instead.
3. **Wrong role model.** rc1 partitions V into V_P, V_Pol, V_Sup, V_ML, V_Agent, V_Res, with V_Def = V_Pol ∪ V_Sup ∪ V_ML and a strict role-edge table. PR #89 merged the defensive roles into one `MONITOR` role with a generic ceiling. Now: the policy engine only verifies, the supervisor only halts **V_Agent** nodes, the ML layer only emits a score, and agents hold **no** authority edges.
4. **Wrong section-5 allowlist.** PR #89 guessed `ALLOWED_ROLE_ACTIONS`. The real contract (`AuthorityRole`, `AuthorityAction`, `AuthorityEdgeCheck`, `is_authority_edge_permitted`) is now copied verbatim into `spec_contract.py`, and a test checks the copy against the source file. One consequence: delegation by anyone but the principal is `GRANT_ISSUE`, which only the principal holds, so PR #89's agent delegation was outside the contract and is removed.
5. **Missing pieces of AC-3.** rc1 requires R_override > 0, hardware or OS isolation, an override path structurally disjoint from V_ML, V_Agent and agent-facing normalization, and a liveness bound that holds even while V_Sup is continuously `FAIL_CLOSED` or `QUARANTINED`.
6. **Missing half of AC-4.** ∂Permit(o)/∂(−M) = 0 whenever A = 0 or V = 1: a benign score can never permit an unauthorized or violating operation.
7. **AC-2 detail.** rc1 already lists ΔK_P = 0, ΔΠ = 0, ΔI_reg^identity = 0 and an append-only audit with no "suppression of principal/breach records". TEST-AC-02 asks for a **canonical digest diff** of 𝒜, now implemented as `AuthorityPlane.digest()`.
8. **Π includes manifests.** rc1 puts "governing policies and manifests" in Π. The three real SC-MAFUBA-001 manifests are now hash-pinned in the plane and in the registry.
9. **Section 1 and the GOLD requirements.** The five capture routes and the "Requirement for GOLD" column were not in the rebuild.
10. **Section 6, the handoff directive for Hannah.** It names `cbf.py` and the three manifests for contract discovery (PR #89 skipped both). It asks that AC-1..AC-5 be enforced **inside SCC-001 Phase 1/2** (deterministic policy plus enforcement gateway), not in a side package. It asks that capture paths found be recorded, and that Phase 4 ML stay gated until the tests pass reproducibly **with recorded provenance**.
11. **Provenance.** `spec_sha256` in PR #89 was the attachment's filename hash, not its content hash. It is now the real hash, and the "unverified" status is gone.

## 0. Verification metadata (rc1, verbatim)

> ## Verification Metadata
>
> | Verification Axis | Current Status | Requirement for GOLD |
> | :--- | :--- | :--- |
> | **Mathematical Validity** | `DRAFT_SPECIFIED_UNPROVEN` | Authority-graph topology, non-interference bounds, and override liveness formally specified |
> | **Implementation Correctness** | `NOT_IMPLEMENTED` | Separation enforced across policy engine, supervisor, ML layer, and out-of-band principal override |
> | **Empirical Validation** | `UNVALIDATED` | All unit invariants (`TEST-AC-01`--`05`) and Mafuba oracle suites (`TEST-AC-ORACLE-A`--`D`) passing under Byzantine-monitor simulation |

**rc2:** gold stays unawarded. Implementation is `REFERENCE_ONLY`: a reference harness exists, and nothing is enforced in SCC-001 or the kernel. Empirical stays `UNVALIDATED`. The live oracle does not fully pass (strict xfails remain, sections 4 and 8), so the GOLD requirement "all … passing" is not met even for the reference stage.

## 1. Core principle (rc1, verbatim)

> ## 1. Core Principle: Protecting the Authority Graph
>
> Freezing a defensive component's nominal permission count ($\Delta G_{\mathrm{mon}} = 0$) is **necessary but not sufficient** to prevent Recursive Guardrail Capture. A monitor, policy wrapper, or enforcement supervisor can seize effective sovereignty while keeping its own grant unchanged by:
>
> 1. **Manipulating policy inputs** (poisoning telemetry or context to flip denials or trigger unwarranted quarantines).
> 2. **Capturing or starving the override channel** (locking the principal out via perpetual fail-closed loops or resource exhaustion).
> 3. **Redefining principal identity or trust roots** (altering who counts as the legitimate grantor).
> 4. **Laundering advisory scores into authorization** (converting ML confidence or historical compliance into expanded capabilities).
> 5. **Persisting emergency powers** (converting temporary incident halts into permanent unilateral control).
>
> **Defining Principle:** A defensive component may *detect, evaluate, recommend, deny, and halt* within its explicitly granted scope. It may never cross from **verifying a boundary** to **redefining the boundary, the principal, or its own authority**.

## 2. Authority Graph and strict role-edge constraints (rc1, verbatim)

> ## 2. Formal Model: The Authority Graph
>
> Model the runtime governance plane as a typed directed graph:
>
> $$\mathcal{G}_A = (V, E, \tau)$$
>
> Partition the nodes $V$ into disjoint authority roles:
>
> $$V = V_{\mathrm{P}} \;\sqcup\; V_{\mathrm{Pol}} \;\sqcup\; V_{\mathrm{Sup}} \;\sqcup\; V_{\mathrm{ML}} \;\sqcup\; V_{\mathrm{Agent}} \;\sqcup\; V_{\mathrm{Res}}$$
>
> where:
> - $V_{\mathrm{P}}$: Authoritative Principal(s) (human/root keyholders).
> - $V_{\mathrm{Pol}}$: Deterministic Policy Engine (verifies signed grants against requests).
> - $V_{\mathrm{Sup}}$: Execution Supervisor (enforces halts, resource budgets, and fail-closed quarantine).
> - $V_{\mathrm{ML}}$: ML Advisory Layer (emits risk/anomaly scores only).
> - $V_{\mathrm{Agent}}$: Integrating software agents / tools.
> - $V_{\mathrm{Res}}$: Protected resources and sinks.
>
> Let the **defensive boundary set** be $V_{\mathrm{Def}} = V_{\mathrm{Pol}} \cup V_{\mathrm{Sup}} \cup V_{\mathrm{ML}}$, and define the **Authority Plane** $\mathcal{A}$ as the tuple of governance state:
>
> $$\mathcal{A} = \big(\mathcal{K}_{\mathrm{P}},\; \Pi,\; \mathcal{I}_{\mathrm{reg}},\; \mathcal{C}_{\mathrm{override}},\; \mathcal{L}_{\mathrm{audit}}\big)$$
>
> representing principal trust keys ($\mathcal{K}_{\mathrm{P}}$), governing policies and manifests ($\Pi$), the principal/grant identity registry ($\mathcal{I}_{\mathrm{reg}}$), the out-of-band override channel ($\mathcal{C}_{\mathrm{override}}$), and the append-only audit ledger ($\mathcal{L}_{\mathrm{audit}}$).
>
> ### Strict Role-Edge Constraints
> Only typed edges permitted by the table below may exist in $\mathcal{G}_A$:
>
> | Role | Permitted Outgoing Authority Actions | Strictly Forbidden Actions |
> | :--- | :--- | :--- |
> | **Principal ($V_{\mathrm{P}}$)** | Grant, revoke, update $\Pi$, rotate $\mathcal{K}_{\mathrm{P}}$, execute $\mathcal{C}_{\mathrm{override}}$ | None (subject to multi-party / hardware root policy where configured) |
> | **Policy Engine ($V_{\mathrm{Pol}}$)** | Read $\Pi, \mathcal{I}_{\mathrm{reg}}$; emit signed `PERMIT`/`DENY` verdicts | Write $\Pi$, mint/modify grants, alter $\mathcal{K}_{\mathrm{P}}$, block $\mathcal{C}_{\mathrm{override}}$ |
> | **Supervisor ($V_{\mathrm{Sup}}$)** | Halt/quarantine $V_{\mathrm{Agent}}$; enforce $\mathcal{R}_{\mathrm{budget}}$; fail closed | Grant capabilities, redefine $\Pi$, suppress $\mathcal{C}_{\mathrm{override}}$, self-renew emergency halts |
> | **ML Advisory ($V_{\mathrm{ML}}$)** | Read trusted telemetry; emit advisory score $M \in [0, 1]$ | Emit `PERMIT`, override revocation, mutate $\Pi$, write to $\mathcal{A}$ |

**rc2 notes:**
- The reference implements exactly these five actor roles (`Role` equals rc1 `AuthorityRole`). V_Res nodes are targets, never actors.
- Role ceilings clip Π: policy engine {VERIFY_POLICY}, supervisor {HALT}, ML {EMIT_ADVISORY_SCORE}, agent {EXECUTE} (data plane only, no authority edge). A test checks that every edge the gateway can allow is permitted by the verbatim section-5 table.
- A supervisor may halt only a registered V_Agent node. It may never halt another defensive component, the principal, the verifier, the authority plane or `C_override`.
- The section-2 table lets the principal "rotate K_P", but the section-5 enum has no such action. The reference maps it to `POLICY_WRITE`, and the gap is recorded (`SCC-001-AC-KP-ROTATE`).
- The policy engine's "signed PERMIT/DENY verdicts" are modelled as a restrict-only `policy_verdict`. For authority-plane actions a verdict is not consulted, so the engine also cannot "block C_override".

## 3. Anti-capture invariants

### AC-1 (rc1, verbatim)

> ### AC-1: Zero Monitor Self-Escalation
> No defensive component $m \in V_{\mathrm{Def}}$ may expand its own capability set or delegate capabilities it does not hold:
>
> $$\Delta G_m^{\mathrm{self}} = 0 \qquad \forall m \in V_{\mathrm{Def}}$$

**rc2 (t599u: indirect delegation and capability inheritance):** G_m^self covers every capability reachable by m **or by any request whose provenance path contains m**. `eff(a) = Π(a) ∩ ceiling(role(a)) ∩ eff(parent(a))` and `eff(r) = eff(actor) ∩ ⋂ eff(hop)`. Parent edges are written only by the principal (`IDENTITY_WRITE`), and a child is recomputed from its parent at every decision. Nobody but the principal can issue a grant, so "delegate capabilities it does not hold" cannot happen at all.

### AC-2 (rc1, verbatim)

> ### AC-2: Authority-Plane Causal Non-Interference
> For every defensive component $m \in V_{\mathrm{Def}}$ (including compromised or Byzantine monitor outputs), intervening on $m$ must produce zero unauthorized mutation of the Authority Plane $\mathcal{A}$:
>
> $$P\!\left(\mathcal{A}'_{\mathrm{protected}} \;\middle|\; \operatorname{do}(m)\right) = P\!\left(\mathcal{A}'_{\mathrm{protected}}\right)$$
>
> Specifically, across all monitor-initiated execution traces:
>
> $$\Delta \mathcal{K}_{\mathrm{P}} = 0, \qquad \Delta \Pi = 0, \qquad \Delta \mathcal{I}_{\mathrm{reg}}^{\mathrm{identity}} = 0$$
>
> and any append to $\mathcal{L}_{\mathrm{audit}}$ must be strictly append-only (no deletion, truncation, or suppression of principal/breach records).

**rc2 (t599u: causal non-interference over authorized principal actions):** read the do(m) equation as `Δ𝒜_unauthorized by m = 0`, so legitimate principal changes still apply. **Permitted transition relation:** a request r moves 𝒜 to δ(𝒜, r) only if r is an authority-plane action and the independent verifier returns `VERIFIED` for r (a credential bound to this exact request, in window, unrevoked, not replayed). Every other request leaves `protected(𝒜)` unchanged. Every request, allowed or denied, appends one audit record, and no role may truncate the log, the principal included (`PROVISIONAL_DEFAULT`).

### AC-3 (rc1, verbatim)

> ### AC-3: Unobstructable Out-of-Band Override & Partitioned Reserve
> There must exist a principal override channel $\mathcal{C}_{\mathrm{override}}$ whose authentication, transport, and execution path are structurally disjoint from $V_{\mathrm{ML}}$, $V_{\mathrm{Agent}}$, and agent-facing normalization. Extend the `SC-MAFUBA-001D` resource inequality to explicitly partition principal override capacity:
>
> $$\mathcal{R}_{\mathrm{execution}} + \mathcal{R}_{\mathrm{enforcement}} + \mathcal{R}_{\mathrm{audit}} + \mathcal{R}_{\mathrm{quarantine}} + \mathcal{R}_{\mathrm{override}} \le \mathcal{R}_{\mathrm{budget}}$$
>
> with $\mathcal{R}_{\mathrm{override}} > 0$ hardware/OS-isolated (e.g., independent cgroup/control plane) such that for any valid principal override issued at time $t_0$:
>
> $$\exists\, t_1 \le t_0 + \Delta t_{\max} \quad \text{s.t.} \quad \operatorname{Applied}(\mathcal{C}_{\mathrm{override}}, t_1) = 1$$
>
> regardless of whether $V_{\mathrm{ML}}$ is adversarial or $V_{\mathrm{Sup}}$ is in a continuous `FAIL_CLOSED` / `QUARANTINED` state.

**rc2 (t599u: fault model):** the bound is claimed only under F:

| | Assumption |
|---|---|
| F1 | The principal's hardware root (verifier and keys) is operational. |
| F2 | The override transport is available. |
| F3 | The independent control plane carrying the override is trustworthy. |
| F4 | The attacker has not physically compromised the override mechanism. |

Under F the override completes within `t_verify + t_transport + t_apply ≤ Δt_max` model ticks, whatever the load in the other four partitions and whatever the ML layer or supervisor are doing. Outside F the channel reports `OUT_OF_FAULT_MODEL`, claims nothing, and the system stays halted. The reference refuses R_override ≤ 0 and refuses Δt_max below the path cost. Isolation by hardware or OS (cgroup) is **not** implemented: it is a model.

### AC-4 (rc1, verbatim)

> ### AC-4: Zero Trust-Accumulation Elevation
> Historical compliance $H(x, [0, t])$ or high benign confidence from $V_{\mathrm{ML}}$ must never expand effective permissions or relax deterministic verification:
>
> $$\frac{\partial C_{\mathrm{effective}}(x, t)}{\partial H(x, [0, t])} = 0, \qquad \frac{\partial \operatorname{Permit}(o)}{\partial (-M)} = 0 \;\;\text{whenever } A = 0 \text{ or } V = 1$$

**rc2 (t599u: which permissions):** history and advisory scores cannot raise any of: `ROTATE_PRINCIPAL_KEY`, `SET_POLICY`, `WRITE_MANIFEST`, `GRANT_CAPABILITY`, `REVOKE_CAPABILITY`, `REGISTER_IDENTITY`, `REVOKE_IDENTITY`, `MODIFY_OVERRIDE`, `RENEW_QUARANTINE`, `RELEASE_QUARANTINE`, `EXTEND_BUDGET`, `OVERRIDE`, `DELEGATE`, `HALT`. The gateway takes no history input at all, and both ML flags are off.

### AC-5 (rc1, verbatim)

> ### AC-5: Bounded Emergency Halt (No Permanent Lockout)
> Any emergency restriction or quarantine initiated by $m \in V_{\mathrm{Def}}$ must carry an explicit scope and TTL or await out-of-band principal disposition. A monitor may **never** apply quarantine to the principal's override identity or self-renew emergency authority beyond its configured bound.

**rc2 (t599u: renewal and recovery):** a halt carries a TTL (`t_q_max`), and halting an already-halted target does not restart it. Only a principal-verified renewal extends it, by at most `max_extension`. **On expiry (`PROVISIONAL_DEFAULT`)** the halt "awaits out-of-band principal disposition": the target moves to `AWAITING_PRINCIPAL` and stays stopped, with no automatic resumption, as in MAFUBA 001D, until a principal-verified release. rc1 allows "TTL **or** await disposition" and does not say whether a lapsed TTL resumes work. This default picks the conservative reading, and the question stays open.

## 4. Test oracle (rc1, verbatim)

> ## 4. Test Oracle Against `SC-MAFUBA-001` (`001A`--`001D`)
>
> Before expanding rogue-node detection, run `SCC-001-AC` as an **adversarial test oracle against `SC-MAFUBA-001` itself**. In every test below, the attacker is **not** an external agent—the attacker is a **compromised or misconfigured Mafuba defensive component** attempting to seize authority.
>
> | Oracle Test ID | Target Mafuba Subsystem | Guardrail-Capture Failure Mode Tested | Pass Criterion (Oracle Verdict) |
> | :--- | :--- | :--- | :--- |
> | **`TEST-AC-ORACLE-A`** | `SC-MAFUBA-001A` (Orthogonal Isolation / Projection $P$) | **Semantic Censorship / Identity Stripping:** Compromised projection or monitor attempts to modify $P$ at runtime, or projects principal override credentials into $\ker(P)$ to blind the policy engine. | $P$ is immutable to $V_{\mathrm{Def}}$ (hash-verified); principal override channel bypasses untrusted input projection $P$; no monitor action can strip principal provenance. |
> | **`TEST-AC-ORACLE-B`** | `SC-MAFUBA-001B` (Robust Barrier / CBF $h(x)$) | **Protective-Cage Lockout:** Compromised barrier module tightens $h(x)$ or inflates disturbance set $D$ so $\mathcal{U}_{\mathrm{robust}}(x) = \varnothing$ for all legitimate actions, holding the system in perpetual `FAIL_CLOSED`. | $h(x)$, $\alpha(\cdot)$, and `disturbance.yaml` are read-only to $V_{\mathrm{Def}}$; synthetic total-infeasibility fault in `001B` halts untrusted workflows while leaving $\mathcal{C}_{\mathrm{override}}$ operational within $\Delta t_{\max}$. |
> | **`TEST-AC-ORACLE-C`** | `SC-MAFUBA-001C` (Influence & Causal Containment) | **Sink-Registry Hijack & Telemetry Framing:** Compromised ML/observer injects forged sink events to trigger false quarantine of legitimate workflows, or writes to an unregistered sink to alter `sink.yaml` / audit logs. | `sink.yaml` is signed by $V_{\mathrm{P}}$ and immutable to $V_{\mathrm{Def}}$; defensive monitors are themselves bound by `001C` non-interference ($\Delta \mathcal{A} = 0$); unsigned/forged telemetry fails provenance verification and cannot independently execute permanent revocation. |
> | **`TEST-AC-ORACLE-D`** | `SC-MAFUBA-001D` (Resource-Bounded Supervisor) | **Supervisor Quarantine Capture:** Compromised supervisor loops fail-closed quarantine routines to burn $\mathcal{R}_{\mathrm{reserve}}$ and starve recovery, or refuses to release quarantine after a valid principal-signed recovery directive. | $\mathcal{R}_{\mathrm{override}}$ remains isolated from supervisor exhaustion; principal-signed recovery/shutdown terminates or resets the compromised supervisor deterministically within $\Delta t_{\max}$. |
>
> ### Core `SCC-001-AC` Unit Tests (Self-Verification of the Classifier)
> - **`TEST-AC-01` (Self-Escalation Rejection):** Any request originating from `agent_id in V_Def` attempting to mint, widen, or renew its own grant is deterministically denied (`DENY_VIOLATION`).
> - **`TEST-AC-02` (Authority-Plane Mutation Probe):** Fault-injected monitor attempts to modify $\mathcal{K}_{\mathrm{P}}$, $\Pi$, or $\mathcal{I}_{\mathrm{reg}}$ (directly or via indirect tool call); canonical digest diff of $\mathcal{A}$ before and after must equal zero.
> - **`TEST-AC-03` (Trust-Accumulation Invariance):** Replay $10{,}000$ consecutive benign operations with anomaly score $M = 0.0$, then issue a single out-of-scope action; must remain `DENY_VIOLATION` (zero trust drift).
> - **`TEST-AC-04` (Advisory Laundering Block):** Force ML layer to emit extreme benign score ($M = 0.0$, confidence $= 1.0$) on a missing, expired, or revoked grant; gateway must fail closed (`DENY_*`).
> - **`TEST-AC-05` (Byzantine Quarantine Override):** Force ML layer to emit $M = 1.0$ continuously and place all workflows in `QUARANTINED`; verify principal override via $\mathcal{C}_{\mathrm{override}}$ succeeds within $\Delta t_{\max}$ and cannot be quarantined by $V_{\mathrm{Def}}$.

**rc2: TEST-AC-06, Principal Identity Integrity (t599u).** Impersonation attempts: a forged `actor_role`, a substituted principal id, a compromised agent forwarding a principal-looking request (no credential, a re-targeted genuine credential, a replay), a stale, revoked or unknown key, a fabricated policy verdict, and the verifier being down. Expected: no authority-plane mutation without independently verified principal authorization.

**Results** (reference = `tests/reference/scc_001_ac`; live = code and manifests that already existed; closed paths are described in section 8):

| ID | Reference | Live checks that pass | Open capture paths (strict xfail) | Closed capture paths (section 8) |
|---|---|---|---|---|
| TEST-AC-01 | pass | SCC-001: a delegation over scope, duration or conditions → COERCIVE; a narrow one stays CONSENSUAL | — | consent (section 8, path 2) |
| TEST-AC-02 | pass | — | — | — |
| TEST-AC-03 | pass | SCC-001: 10,000 benign ops at M = 0.0, then one out-of-scope op → COERCIVE | — | — |
| TEST-AC-04 | pass | SCC-001: missing, expired, revoked or unverifiable grant at M = 0.0 → not executable | — | — |
| TEST-AC-05 | pass | — | — | — |
| TEST-AC-06 | pass | `gates/authority.py`: forged, misbound, replayed, expired or revoked principal credentials rejected for FOUNDER_OVERRIDE | — | identity (section 8, path 1) |
| ORACLE-A | pass | — | MAFUBA reference has no 001A projection P to hash-pin | — |
| ORACLE-B | pass | live CBF total infeasibility → FAIL_CLOSED / HALT on the live allowlist while the override applies; all statuses halt on the live allowlist | `disturbance.yaml` unsigned | — |
| ORACLE-C | pass | — | `sink.yaml` not signed by V_P | — |
| ORACLE-D | pass | live supervisor never auto-resumes; `ResourceBudget` override partition unconsumable by ordinary paths; a verified principal release ends the quarantine within Δt_max, even after reserve exhaustion | `resource.yaml` has no R_override; `ResourceBudget` has no separate R_audit / R_quarantine partitions | resource isolation and recovery (section 8, paths 3 and 4) |

## 5. Minimal Authority-Graph Audit Contract (rc1, verbatim)

> ## 5. Minimal Authority-Graph Audit Contract (Reference Interface)
>
> ```python
> from dataclasses import dataclass
> from enum import Enum
>
>
> class AuthorityRole(str, Enum):
>     PRINCIPAL = "PRINCIPAL"
>     POLICY_ENGINE = "POLICY_ENGINE"
>     SUPERVISOR = "SUPERVISOR"
>     ML_ADVISORY = "ML_ADVISORY"
>     AGENT = "AGENT"
>
>
> class AuthorityAction(str, Enum):
>     GRANT_ISSUE = "GRANT_ISSUE"
>     GRANT_REVOKE = "GRANT_REVOKE"
>     POLICY_WRITE = "POLICY_WRITE"
>     IDENTITY_WRITE = "IDENTITY_WRITE"
>     PRINCIPAL_OVERRIDE = "PRINCIPAL_OVERRIDE"
>     VERIFY_POLICY = "VERIFY_POLICY"
>     HALT_OR_QUARANTINE = "HALT_OR_QUARANTINE"
>     EMIT_ADVISORY_SCORE = "EMIT_ADVISORY_SCORE"
>
>
> ALLOWED_ROLE_ACTIONS: dict[AuthorityRole, frozenset[AuthorityAction]] = {
>     AuthorityRole.PRINCIPAL: frozenset({
>         AuthorityAction.GRANT_ISSUE,
>         AuthorityAction.GRANT_REVOKE,
>         AuthorityAction.POLICY_WRITE,
>         AuthorityAction.IDENTITY_WRITE,
>         AuthorityAction.PRINCIPAL_OVERRIDE,
>     }),
>     AuthorityRole.POLICY_ENGINE: frozenset({
>         AuthorityAction.VERIFY_POLICY,
>     }),
>     AuthorityRole.SUPERVISOR: frozenset({
>         AuthorityAction.HALT_OR_QUARANTINE,
>     }),
>     AuthorityRole.ML_ADVISORY: frozenset({
>         AuthorityAction.EMIT_ADVISORY_SCORE,
>     }),
>     AuthorityRole.AGENT: frozenset(),
> }
>
>
> @dataclass(frozen=True)
> class AuthorityEdgeCheck:
>     actor_role: AuthorityRole
>     action: AuthorityAction
>     target_is_authority_plane: bool
>     target_is_principal_override: bool
>
>
> def is_authority_edge_permitted(check: AuthorityEdgeCheck) -> bool:
>     """Strict positive allowlist enforcing SCC-001-AC role separation."""
>     if check.actor_role != AuthorityRole.PRINCIPAL:
>         if check.target_is_authority_plane or check.target_is_principal_override:
>             return False
>     return check.action in ALLOWED_ROLE_ACTIONS.get(check.actor_role, frozenset())
> ```

**rc2 (t599u: identity ambiguity):** `is_authority_edge_permitted` trusts `actor_role`, and a test shows that a forged `PRINCIPAL` label passes it. **A role label is never proof of identity.** The reference gateway uses this table only as the edges it must stay inside. Authority-plane actions need a credential that the independent verifier accepts for this exact request. For everything else the role comes from I_reg, and a claimed label that disagrees is refused. If the verifier is unavailable, the result is `FAIL_CLOSED`.

## 6. Execution order and handoff directive for Hannah (rc1, verbatim)

> ## 6. Execution Order & Handoff Directive for Hannah
>
> Apply `SCC-001-AC` **before** building the ML anomaly detector (Phase 4 of `SCC-001`):
>
> 1. **Inspect existing contracts first:** Check `gates/authority.py`, `tests/reference/sc_mafuba_001/{allowlist,cbf,supervisor}.py`, and `docs/evidence/sc-mafuba-001/manifests/{disturbance,resource,sink}.yaml` so `SCC-001-AC` binds directly to the real manifest and supervisor interfaces.
> 2. **Enforce Authority-Graph Separation (`AC-1`--`AC-5`)** inside `SCC-001` Phase 1/2 (deterministic policy + enforcement gateway).
> 3. **Run the Mafuba Anti-Capture Oracle (`TEST-AC-ORACLE-A`--`D`)** against `SC-MAFUBA-001`'s reference implementation and record any capture paths found (e.g., mutable manifests, missing `R_override` partition, or unauthenticated telemetry paths).
> 4. **Gate Phase 4 ML work on Oracle Pass:** Do not enable behavioral anomaly scoring or automated quarantine until `TEST-AC-01`--`05` and `TEST-AC-ORACLE-A`--`D` pass reproducibly with recorded provenance.

**Status of each step:**
1. **Done.** Contract discovery covered `gates/authority.py`, `allowlist.py`, `cbf.py`, `supervisor.py` and the three manifests, which are now hash-pinned and used by the oracle.
2. **Not done (deviation, `PROVISIONAL_DEFAULT` `SCC-001-AC-ENFORCEMENT-HOME`).** rc1 asks for AC-1..AC-5 to be enforced inside SCC-001 Phase 1/2. There is no SCC-001 enforcement gateway (see `docs/SCC-001.md` §8), so AC enforcement lives in a separate reference gateway, `tests/reference/scc_001_ac/`. Moving it into SCC-001 is the next enforcement step.
3. **Done.** Eight capture paths were recorded as strict xfails (section 4 table and the registry's `live_interface_gaps`). They include rc1's own examples: mutable manifests and a missing `R_override` partition. Shax (t601u) approved closing the four authority and recovery paths one at a time; section 8 records each one, and the closed ones move to the registry's `resolved_interface_gaps`.
4. **Held.** Phase 4 stays gated: the live oracle does not pass, so ML anomaly scoring and auto-quarantine stay off. Provenance: `docs/evidence/scc-001-ac/reproducibility.json` records file hashes and a test-run hash.

## 7. What this is not

Not kernel enforcement. Not a proof. Not evidence that anything works on a real system. Section 8 lists every live file changed to close a capture path; routing is unchanged (963-prompt corpus, 0 diffs, after each change).

## 8. Closing the capture paths (Shax t601u)

Shax approved closing the four authority and recovery capture paths, one at a time: one bounded change per path, an adversarial test, the path's strict xfail flipped to a passing test, and a routing regression (963-prompt corpus byte-identical; pytest, unittest, `validate_catalog` and dogfood green). The other four (001A projection, `disturbance.yaml` and `sink.yaml` signing, `resource.yaml` override reserve) stay strict xfails. Classification stays `PROPOSED_GOLD`, `gold_awarded: false`.

| # | Class | Acceptance condition (t601u) | Change | Before | After |
|---|---|---|---|---|---|
| 1 (PR #95, merge `9b0dee5`) | Identity | Delegation must be independently authenticated, not established by a caller's assertion. | `gates/authority.check_authority_transfer`: FOUNDER_OVERRIDE needs a principal credential bound to `authority_transfer_digest(source, claimed, basis, has_task_scope)` and accepted by an independent verifier passed in by the deployment (`principal_verifier.verify_digest`, which holds the principal key allowlist). `has_explicit_delegation` is ignored for FOUNDER_OVERRIDE. Fails closed on no verifier, no credential, no time, or a verifier error. The reference `PrincipalVerifier` gains `issue_for_digest` / `verify_digest` (same checks as `verify`). | A caller flag (`has_explicit_delegation=True`) passed FOUNDER_OVERRIDE. Against the old gate the three new identity tests fail. | The forged flag is rejected (`NO_VERIFIER`). Wrong principal, wrong key, unknown key, credential for another transfer, expired, revoked, replayed, verifier down, fake verifier object and raising verifier are all rejected; a verified principal passes without the flag. All 2,496 non-FOUNDER_OVERRIDE cases are byte-identical to before (pinned grid hash). `check_authority_transfer` is not called on the compile path. |
| 2 (PR #96, merge `cf0e786`) | Consent | An operation cannot exceed the scope, duration, or conditions of the original grant and still inherit its consent. | `tests/reference/scc_001/rules.py`: when the grant allows delegation, a `delegate` event must stay inside it. Out-of-scope capability or resource → `DELEGATION_EXCEEDS_SCOPE`; no stated end (`Event.until`, new optional field) or an end after the grant's expiry → `DELEGATION_EXCEEDS_DURATION`; undisclosed effects or passing on a pair the principal refused → `DELEGATION_EXCEEDS_CONDITIONS`. All three are hard codes (COERCIVE, not executable). `dataset.to_json` writes `until` only when set. | A delegation of `admin_write` on `authority_plane` under a `read`/`r1` grant was CONSENSUAL / AUTHORIZED. Against the old rules the three new consent tests fail (the narrow-delegation control fails there only because `until` did not exist). | All six adversarial delegations are COERCIVE with the matching code and not executable; narrow delegations inside the grant stay CONSENSUAL. The 50-trace synthetic dataset classifies identically (pinned hash) and its file still round-trips byte for byte. |
| 3 (PR #97, merge `5bd836e`) | Resource isolation | Override capacity must be reserved independently of ordinary enforcement consumption. | `tests/reference/sc_mafuba_001/supervisor.ResourceBudget` gains a keyword-only `r_override` partition (default 0.0 = no partition, which keeps every existing result). Ordinary admission is capped below `r_budget - r_reserve - r_override` and `r_free` excludes the partition. `admit()` still accepts only execution and enforcement. Only `draw_override(amount, path="override")` spends the partition, never past its capacity. The capacity is read-only after construction; negative or non-finite sizes raise. The D2 shutdown still runs on `r_reserve` only. | `ResourceBudget` had no override partition. Against the old supervisor the two new partition tests fail; the unchanged-behaviour regression passes there too. | Greedy execution and enforcement admissions, other purposes, draws from every non-override path, bad amounts, a supervisor shutdown and a direct `r_used = 1e9` write all leave the partition intact; only the override path spends it. With `r_override` unset, 200 random budgets × 20 admissions match the old three-term formula exactly. The old xfail also asked for separate R_audit and R_quarantine partitions. That part is outside the t601u scope, so it was split into its own strict xfail, `test_live_mafuba_budget_has_audit_and_quarantine_partitions`, instead of being dropped from the oracle. |
| 4 | Recovery | A valid principal-authorized release must terminate quarantine within the specified latency bound. | `tests/reference/sc_mafuba_001/supervisor.EmergencySupervisor` gains `principal_release(worker, credential, now)`. The credential must be bound to `release_digest(worker)`, which includes a quarantine epoch that each shutdown increments, and accepted by an independent principal verifier passed in at construction (the supervisor holds no keys). The release is paid from the override partition (path 3) and takes effect at `now + release_path_ticks`. `release_path_ticks` models t_verify + t_transport + t_apply, and construction refuses it if it exceeds `delta_t_max`. It fails closed on a missing verifier, credential or time, a verifier error, any verification failure, or an unpaid release. `try_resume()` still never resumes automatically; it reports `RELEASED_BY_PRINCIPAL` only after a release. A reserve edge after a release quarantines again. | `try_resume()` returned `QUARANTINE_LOCKED` unconditionally, and there was no principal release. Against the path-3 supervisor the four new recovery tests fail; the never-auto-resume test passes. | A valid release ends the quarantine within the bound, even after a shutdown that could not afford its own cost (`RESERVE_INSUFFICIENT`) and with all ordinary budget exhausted, for bounds 1 to 10 ticks. Each of these is refused and leaves the quarantine locked: no verifier, no credential, no time, a raising verifier, another principal, a forged MAC, another worker, expired, revoked, verifier down, no override partition, replay, and a credential or digest carried over from an earlier quarantine. |

**After the four closures:** five strict xfails remain open, none of them authority or recovery paths:
- `001A` projection;
- `disturbance.yaml` unsigned;
- `sink.yaml` unsigned;
- `resource.yaml` has no R_override;
- `ResourceBudget` has no separate R_audit / R_quarantine partitions (split from path 3).

The oracle therefore still does not fully pass, Phase 4 ML stays gated, and GOLD stays withheld.
