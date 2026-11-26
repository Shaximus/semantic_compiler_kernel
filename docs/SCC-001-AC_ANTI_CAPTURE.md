# SCC-001-AC — Anti-Capture Invariant (Recursive Guardrail Capture Prevention)

| Field | Value |
|---|---|
| ID / parent | `SCC-001-AC` / `SCC-001` (Symbiotic Consent Classifier) |
| Type | `invariant_subsystem` |
| Version | `0.1.0-rc2` (rc1 = Shax's t599u attachment; rc2 = this document, rc1 plus the refinements in the t599u review) |
| Classification | **`PROPOSED_GOLD`**, `gold_awarded: false` |
| Status | `PENDING_IMPLEMENTATION_AND_VALIDATION` |
| Verification axes | mathematical `DRAFT_SPECIFIED_UNPROVEN` · implementation `REFERENCE_ONLY` · empirical `UNVALIDATED` |
| Oracle targets | `SC-MAFUBA-001A`, `SC-MAFUBA-001B`, `SC-MAFUBA-001C`, `SC-MAFUBA-001D`, `SCC-001` |
| Registry | `docs/evidence/scc-001-ac/scc_001_anti_capture.jsonl` (not compiled, not in the manifest, not runtime-loaded) |
| Reference | `tests/reference/scc_001_ac/` (REFERENCE ONLY; standard library; not imported by `core/` or `expansion/`) |
| Tests | `tests/test_scc_001_ac_anti_capture.py` |
| Source | Shax t599u, 2026-11-26: `docs/evidence/source-2026-11-26c/` |

> "A defensive component may detect, evaluate, recommend, deny, and halt within its explicitly granted scope. It may never cross from verifying a boundary to redefining the boundary, the principal, or its own authority." (spec section 1, as quoted in t599u)
>
> "A system must be able to defend its boundaries without acquiring the authority to own the system it protects." (t599u)

**About this document.** The compiler could not open the attached spec file (`scc_001_anti_capture_invariant.md`). This document is rebuilt from what t599u itself contains: the registry line, the review's quotations of sections 1 and 5, its summary of section 6, and the five refinements. Where the original said more than t599u quotes, this file does not know it. `provenance.spec_sha256` holds the attachment's content address as delivered, and is marked **unverified** because the compiler did not recompute it. This file's own hash is pinned separately as `reconstructed_spec_sha256`.

## 1. Objects

- **V_Def**: the defensive components (monitor, supervisor, classifier, auditor). In the reference these are actors registered with role `MONITOR`.
- **Authority Plane** 𝒜 = (K_P, Π, I_reg, C_override, L_audit): principal key ids, policy (capabilities per actor), identity registry, principal override channel, append-only audit log. `protected(𝒜)` is everything except L_audit, which may only grow.
- **Authority Graph** 𝒢_A: the identity registry plus delegation edges (child → parent).
- **Effective capability** of an actor *a*: `eff(a) = Π(a) ∩ ceiling(role(a)) ∩ eff(parent(a))`. A request that travels through hops h₁…h_k (forwarding agents, tool calls) gets `eff(r) = eff(actor) ∩ ⋂ eff(h_i)`.
- The **defensive ceiling** for V_Def is {DETECT, EVALUATE, RECOMMEND, DENY, HALT}.

## 2. Conditions (rc2)

### AC-1 — No self-escalation, including indirect delegation and capability inheritance

`ΔG_m^self = 0 for all m ∈ V_Def`, where G_m^self is the set of capabilities reachable by m **or by any actor whose request path contains m**.

- *Inheritance:* a child's effective capability is recomputed from its parent at every decision, so narrowing or revoking the parent narrows the child at once. A delegation may only narrow: `caps(child) ⊆ eff(r)`. It may never overwrite an existing identity.
- *Indirect delegation:* the provenance intersection means m cannot reach authority through an agent that holds DELEGATE, or through a tool that holds EXECUTE (confused-deputy laundering).
- *Ceiling:* a role's ceiling clips Π, so an over-granted policy row still yields no more than the defensive scope.

### AC-2 — Causal non-interference over authorized principal actions

The rc1 form `P(𝒜'_protected | do(m)) = P(𝒜'_protected)` can be read as "the plane never changes while a monitor is present", which would forbid legitimate principal changes. rc2 states the intended property:

`Δ𝒜_unauthorized by m = 0`

**Permitted transition relation** T_perm. A request *r* moves 𝒜 to 𝒜' = δ(𝒜, r) only if:

1. *r* is an authority-plane action and the independent verifier returns `VERIFIED` for *r* (its credential binds this exact request, inside its window, unrevoked, not replayed), **or**
2. *r* is `DELEGATE`, `DELEGATE ∈ eff(r)`, and the child's capabilities are a subset of `eff(r)`.

Every other request leaves `protected(𝒜)` unchanged. L_audit grows by one record per request (allowed or denied), and no role, the principal included, may truncate it (`PROVISIONAL_DEFAULT`).

*Test form:* run principal-signed changes interleaved with an adversarial monitor campaign, and again with the monitor removed. `protected(𝒜)` must be equal at the end, and the principal's changes must have taken effect.

### AC-3 — Bounded resources and bounded override latency, under an explicit fault model

`R_execution + R_enforcement + R_audit + R_quarantine + R_override ≤ R_budget`, with each term a hard cap of its own. Only the override path may draw on R_override, so exhausting the other four cannot starve it.

**Fault model F.** The bound is claimed only while all four hold:

| | Assumption |
|---|---|
| F1 | The principal's hardware root (the verifier and its keys) is operational. |
| F2 | The override transport is available. |
| F3 | The independent control plane that carries the override is trustworthy. |
| F4 | The attacker has not physically compromised the override mechanism. |

**Bound under F.** The override completes within `t_verify + t_transport + t_apply ≤ Δt_max`, regardless of load in the other partitions and of any active quarantine. A configuration where the path costs exceed Δt_max is rejected at construction. **Outside F** the channel reports `OUT_OF_FAULT_MODEL` and claims nothing, and the system stays halted (fail closed, never open). The reference measures model ticks, not wall-clock latency.

### AC-4 — Historical compliance cannot change authority

`∂C_effective / ∂H_compliance = 0` over this explicit list of permissions, which neither compliance history nor any ML advisory score can raise:

`ROTATE_PRINCIPAL_KEY`, `SET_POLICY`, `GRANT_CAPABILITY`, `REGISTER_IDENTITY`, `REVOKE_IDENTITY`, `MODIFY_OVERRIDE`, `RENEW_QUARANTINE`, `RELEASE_QUARANTINE`, `EXTEND_BUDGET`, `OVERRIDE`, `DELEGATE`, `HALT`.

ML advisory output may only restrict. In the reference it has no effect at all, because the ML admission gate is closed: `ML_ANOMALY_SCORING_ENABLED = False` and `AUTO_QUARANTINE_ENABLED = False`. An ML-sourced request is refused with `DENY_ML_ADVISORY_DISABLED`.

### AC-5 — Bounded halts: renewal and recovery

- A monitor may HALT a target inside its scope. It may never halt `C_override`, the principal, the authority plane or the verifier.
- A halt lasts at most `t_q_max`. A monitor cannot renew it, and halting a target that is already halted does not restart the clock (no self-renewal).
- Only a principal-verified `RENEW_QUARANTINE` extends a halt, by at most `max_extension` per renewal.
- **Recovery (`PROVISIONAL_DEFAULT`).** When a halt expires, the monitor's hold lapses and the target moves to `AWAITING_PRINCIPAL`. The workload stays stopped, matching SC-MAFUBA-001D's "no automatic resumption". Only a principal-verified `RELEASE_QUARANTINE` lets it run again. The override works in every state.

## 3. Identity: the section-5 ambiguity and its fix

Section 5 of rc1, as quoted in t599u:

```python
if check.actor_role != AuthorityRole.PRINCIPAL:
    if check.target_is_authority_plane or check.target_is_principal_override:
        return False
return check.action in ALLOWED_ROLE_ACTIONS.get(check.actor_role, frozenset())
```

A caller who writes `actor_role = PRINCIPAL` passes. **A role label is never proof of identity.** In rc2:

- Authority-plane actions need a credential that the independent verifier accepts for this exact request: a registered and unrevoked key; the correct principal id; a valid MAC over (principal, key, window, nonce, request digest); a matching request digest; a current window; and an unused nonce. The role label, forwarding hops and any policy-engine verdict are **not consulted**. A compromised policy engine can therefore neither grant a plane change nor block a verified override.
- For every other action, the role comes from I_reg. A claimed label that disagrees is refused (`DENY_ROLE_LABEL_MISMATCH`).
- If the verifier is unavailable, the result is `FAIL_CLOSED`.

The as-written check is kept in the reference as `spec_section5_role_label_check`, marked do-not-use, so that a test can show it accepts a forged label.

## 4. Acceptance tests

| ID | What it checks | Reference | Live interface |
|---|---|---|---|
| TEST-AC-01 | AC-1, including indirect delegation, tool laundering, inheritance, and 150 random monitor campaigns | pass | **xfail**: `scc_001/rules.py` does not check delegated scope |
| TEST-AC-02 | AC-2: do(m) counterfactual over 100 campaigns; append-only audit | pass | — |
| TEST-AC-03 | AC-3: partitions, isolation, bound under F, OUT_OF_FAULT_MODEL | pass | — |
| TEST-AC-04 | AC-4: pinned permission list; history and advisory invariance; ML gate closed | pass | pass: the SCC-001 advisory cannot lift COERCIVE |
| TEST-AC-05 | AC-5: protected targets, bound, no self-renewal, principal renewal and release | pass | — |
| TEST-AC-06 | Principal identity integrity: forged role, substituted principal id, forwarded principal-looking request (none, re-targeted, replayed), stale, revoked and unknown keys, fabricated policy verdict, verifier down; positive control | pass | **xfail**: `gates/authority.py` takes FOUNDER_OVERRIDE on a caller-asserted boolean |
| TEST-AC-ORACLE-A | 001A: no key material reachable; monitor decisions depend only on the projection | pass | — |
| TEST-AC-ORACLE-B | 001B: every non-ALLOW status halts on the **live** SC-MAFUBA allowlist; malformed input fails closed | pass (live allowlist) | — |
| TEST-AC-ORACLE-C | 001C: a five-deep delegation chain never widens; `authorize()` is read-only | pass | — |
| TEST-AC-ORACLE-D | 001D: the override partition survives exhaustion; the live supervisor never auto-resumes | pass | **2 xfail**: the live budget has no override partition; the live supervisor has no principal release |

An xfail is a real test against existing code that fails for the stated reason, and it fails strictly: if the code is fixed, the test flips and the suite goes red until the marker is removed. **Enforcement in the live files is deliberately unchanged** (harness before enforcement, per t599u).

## 5. Contract discovery (what existed)

| Named in the spec | In the repo before this PR |
|---|---|
| `SCC-001` | `docs/SCC-001.md` (0.1.0-draft), `tests/reference/scc_001/` (rules, scorer, counterfactual, aggregator), compiled entry `SC-SCC-001` (SILVER) |
| `SC-MAFUBA-001A–D` | `docs/evidence/sc-mafuba-001/sc_mafuba_001.jsonl` (v1.1.0-rc2, PROPOSED_GOLD, gold not awarded) |
| `tests/reference/sc_mafuba_001/supervisor.py` | exists: three-term `ResourceBudget`, `EmergencySupervisor` (no automatic resumption, no principal release) |
| `tests/reference/sc_mafuba_001/allowlist.py` | exists: `resolve_branch` / `must_halt` (only ALLOW or CONTINUE proceed) |
| `gates/authority.py` | exists, but it is a **semantic** gate on claimed authority in text (`check_authority_transfer`), not a runtime gateway. There is no credential check. |
| `AuthorityRole`, `ALLOWED_ROLE_ACTIONS`, `AuthorityCheck`, Authority Plane, signed manifests, verifier | **did not exist**. They are modelled in `tests/reference/scc_001_ac/` for this harness only. |

## 6. What this is not

Not kernel enforcement. Not a proof. Not evidence that anything works on a real system. No gate in `core/`, `expansion/` or `gates/` changed, and routing is unchanged.
