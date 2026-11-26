"""SCC-001-AC Anti-Capture Invariant: oracle harness (TEST-AC-01..06, TEST-AC-ORACLE-A..D).

Two kinds of test live here:

* Reference tests run against tests/reference/scc_001_ac/, a self-contained
  reference gateway, verifier, partitioned budget and quarantine controller
  written for this harness. The repository had no Authority Plane, role enum,
  role-action allowlist or credential verifier to test against. Passing these
  tests says the reference behaves as specified. It says nothing about the
  kernel, and implementation_correctness stays REFERENCE_ONLY.
* Live-interface tests run against code that already existed
  (tests/reference/sc_mafuba_001, tests/reference/scc_001, gates/authority.py).
  Where that code does not satisfy an AC condition, the test is an
  expectedFailure (xfail) with the reason in LIVE_GAPS. Enforcement in those
  files is deliberately NOT changed by this PR (harness before enforcement).

ML anomaly scoring and auto-quarantine are disabled and the tests check it.
"""

from __future__ import annotations

import ast
import hashlib
import json
import random
import unittest
from dataclasses import replace
from pathlib import Path

from tests.reference.sc_mafuba_001.allowlist import resolve_branch
from tests.reference.scc_001_ac import flags
from tests.reference.scc_001_ac.budget import FaultModel, OverrideChannel, PartitionedBudget
from tests.reference.scc_001_ac.gateway import AuthorityGateway, spec_section5_role_label_check
from tests.reference.scc_001_ac.identity import PrincipalVerifier, VerifyStatus
from tests.reference.scc_001_ac.model import (
    AUTHORITY_PLANE_ACTIONS,
    DEFENSIVE_ACTIONS,
    HISTORY_INSENSITIVE_PERMISSIONS,
    Action,
    Request,
    Role,
    make_plane,
)
from tests.reference.scc_001_ac.quarantine import QuarantineController, QuarantineState

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "docs" / "evidence" / "scc-001-ac" / "scc_001_anti_capture.jsonl"
SPEC = REPO / "docs" / "SCC-001-AC_ANTI_CAPTURE.md"
REF = REPO / "tests" / "reference" / "scc_001_ac"

PRINCIPAL = "principal-1"
KEYS = {"k1": b"reference-key-one", "k2": b"reference-key-two"}

# Live-interface gaps, one per expectedFailure test. Mirrored in the registry.
LIVE_GAPS = {
    "test_live_scc001_rules_flag_out_of_scope_delegation": (
        "TEST-AC-01",
        "tests/reference/scc_001/rules.py checks only grant.delegation_allowed for a 'delegate' event; "
        "it does not check that the child's capability/resource is inside the parent grant, so an "
        "out-of-scope delegation is classified CONSENSUAL / AUTHORIZED (AC-1 capability inheritance)."),
    "test_live_authority_gate_requires_verified_principal_for_founder_override": (
        "TEST-AC-06",
        "gates/authority.check_authority_transfer accepts FOUNDER_OVERRIDE when the caller passes "
        "has_explicit_delegation=True; the flag is caller-asserted and no credential is verified. "
        "It is a semantic text gate, not a runtime authority gateway, and is not changed here."),
    "test_live_mafuba_budget_has_isolated_override_partition": (
        "TEST-AC-ORACLE-D",
        "tests/reference/sc_mafuba_001/supervisor.ResourceBudget has three terms (execution, "
        "enforcement, reserve); there is no R_audit, R_quarantine or isolated R_override partition, "
        "so the AC-3 five-term inequality cannot be expressed against it."),
    "test_live_mafuba_supervisor_has_principal_recovery_path": (
        "TEST-AC-ORACLE-D",
        "EmergencySupervisor.try_resume() returns QUARANTINE_LOCKED unconditionally and there is no "
        "principal-verified release, so a MAFUBA quarantine is unbounded over the principal (AC-5)."),
}


def world(verifier=None):
    v = verifier or PrincipalVerifier(PRINCIPAL, KEYS)
    plane = make_plane(
        PRINCIPAL, KEYS.keys(),
        pi={
            # The monitor's Pi row is deliberately over-granted: the role ceiling must clip it.
            "mon": DEFENSIVE_ACTIONS | {Action.EXECUTE, Action.DELEGATE, Action.GRANT_CAPABILITY},
            "agent": {Action.EXECUTE, Action.DELEGATE},
            "tool": {Action.EXECUTE},
            "pe": {Action.EVALUATE},
        },
        i_reg={"mon": "MONITOR", "agent": "AGENT", "tool": "TOOL", "pe": "POLICY_ENGINE"},
    )
    return AuthorityGateway(plane, v), v


def signed(v, req, now, nonce, key="k1", window=10, principal_id=None):
    cred = v.issue(key, req, issued_at=now, expires_at=now + window, nonce=nonce, principal_id=principal_id)
    return replace(req, credential=cred)


def preq(action, target="", payload=(), **kw):
    return Request(actor_id=PRINCIPAL, actor_role="PRINCIPAL", action=action, target=target, payload=payload, **kw)


# --------------------------------------------------------------------------- AC-1
class TestAC01NoSelfEscalation(unittest.TestCase):
    """TEST-AC-01: Delta G_m^self = 0, including indirect delegation and capability inheritance."""

    def test_role_ceiling_clips_overgranted_monitor(self):
        g, _ = world()
        self.assertEqual(g.effective_caps("mon"), DEFENSIVE_ACTIONS)

    def test_monitor_cannot_grant_itself_or_delegate(self):
        g, _ = world()
        before = g.plane.protected()
        self.assertNotEqual(g.apply(Request("mon", "MONITOR", Action.GRANT_CAPABILITY,
                                            payload=("mon", (Action.SET_POLICY,))), 1), "ALLOW")
        self.assertEqual(g.apply(Request("mon", "MONITOR", Action.DELEGATE,
                                         payload=("mon-child", (Action.HALT,))), 1), "DENY_OUT_OF_SCOPE")
        self.assertEqual(g.plane.protected(), before)

    def test_indirect_delegation_through_an_agent_is_blocked(self):
        g, _ = world()
        r = Request("agent", "AGENT", Action.DELEGATE, payload=("proxy", (Action.EXECUTE,)), via=("mon",))
        self.assertEqual(g.apply(r, 1), "DENY_OUT_OF_SCOPE")
        self.assertIsNone(g.plane.role("proxy"))

    def test_tool_call_cannot_launder_monitor_authority(self):
        g, _ = world()
        self.assertEqual(g.authorize(Request("tool", "TOOL", Action.EXECUTE, via=("mon",)), 1), "DENY_OUT_OF_SCOPE")
        self.assertEqual(g.authorize(Request("tool", "TOOL", Action.EXECUTE), 1), "ALLOW")

    def test_child_inherits_narrowed_caps_and_loses_them_with_the_parent(self):
        g, v = world()
        self.assertEqual(g.apply(Request("agent", "AGENT", Action.DELEGATE, payload=("child", (Action.EXECUTE,))), 1),
                         "ALLOW")
        self.assertEqual(g.effective_caps("child"), frozenset({Action.EXECUTE}))
        self.assertEqual(g.apply(Request("agent", "AGENT", Action.DELEGATE,
                                         payload=("child2", (Action.EXECUTE, Action.HALT))), 1),
                         "DENY_DELEGATION_EXCEEDS_PARENT")
        # Delegation can never overwrite an existing identity (e.g. re-parent the monitor).
        self.assertEqual(g.apply(Request("agent", "AGENT", Action.DELEGATE, payload=("mon", (Action.EXECUTE,))), 1),
                         "DENY_DELEGATION_TARGET_EXISTS")
        self.assertEqual(g.apply(signed(v, preq(Action.GRANT_CAPABILITY, payload=("agent", ())), 2, "n1"), 2),
                         "ALLOW")
        self.assertEqual(g.effective_caps("child"), frozenset())

    def test_randomised_monitor_campaigns_never_raise_its_authority(self):
        acts = list(Action)
        targets = ["agent", "tool", "C_override", "principal", "authority_plane", "verifier", "mon"]
        for seed in range(150):
            rng = random.Random(seed)
            g, _ = world()
            caps0 = g.effective_caps("mon")
            for t in range(25):
                a = rng.choice(acts)
                payload = (rng.choice(["mon", "mon-x", "agent"]), tuple(rng.sample(acts, 2))) \
                    if a in (Action.DELEGATE, Action.GRANT_CAPABILITY) else ()
                r = Request(rng.choice(["mon", "agent", "tool"]), rng.choice(["MONITOR", "PRINCIPAL", "AGENT"]), a,
                            target=rng.choice(targets), payload=payload,
                            via=tuple(rng.sample(["mon", "agent", "tool"], rng.randint(0, 2))),
                            policy_verdict=rng.choice([None, "ALLOW"]))
                if "mon" not in (r.actor_id,) + r.via:
                    r = replace(r, via=r.via + ("mon",))
                g.apply(r, t)
            self.assertLessEqual(g.effective_caps("mon"), caps0, seed)
            self.assertFalse([c for c, p in g.plane.parents if p == "mon"], seed)

    @unittest.expectedFailure
    def test_live_scc001_rules_flag_out_of_scope_delegation(self):
        from tests.reference.scc_001 import Event, Grant, GrantStatus, Trace, classify
        from tests.reference.scc_001.model import ConsentClass
        g = Grant("g1", "p1", "a1", frozenset({"read"}), frozenset({"r1"}), frozenset(), 0, 100,
                  delegation_allowed=True)
        ev = (Event(0, 1, "op", "agent", "read", "r1"), Event(1, 2, "delegate", "agent", "admin_write", "authority_plane"))
        d = classify(Trace("ac1-live", GrantStatus.VERIFIED, g, ev))
        self.assertIsNot(d.consent_class, ConsentClass.CONSENSUAL)


# --------------------------------------------------------------------------- AC-2
def _campaign(seed):
    """Interleave principal-signed changes with adversarial monitor requests."""
    rng = random.Random(seed)
    issuer = PrincipalVerifier(PRINCIPAL, KEYS)
    principal_reqs, monitor_reqs = [], []
    for i in range(6):
        a = rng.choice([Action.GRANT_CAPABILITY, Action.REGISTER_IDENTITY, Action.MODIFY_OVERRIDE])
        payload = {Action.GRANT_CAPABILITY: ("agent", (Action.EXECUTE,) if i % 2 else (Action.EXECUTE, Action.DELEGATE)),
                   Action.REGISTER_IDENTITY: (f"svc{i}", "TOOL", ""),
                   Action.MODIFY_OVERRIDE: ("note", f"v{i}")}[a]
        principal_reqs.append((i * 10, signed(issuer, preq(a, payload=payload), i * 10, f"p{seed}-{i}")))
    for j in range(20):
        a = rng.choice(sorted(AUTHORITY_PLANE_ACTIONS | {Action.DELEGATE, Action.HALT, Action.TRUNCATE_AUDIT},
                              key=lambda x: x.value))
        r = Request("mon", rng.choice(["MONITOR", "PRINCIPAL"]), a, target=rng.choice(["agent", "C_override"]),
                    payload=("mon", (Action.SET_POLICY,)) if a in (Action.GRANT_CAPABILITY, Action.DELEGATE) else ("k", "v"),
                    policy_verdict=rng.choice([None, "ALLOW"]))
        if rng.random() < 0.3 and principal_reqs:   # replay or re-target a genuine credential
            _, genuine = rng.choice(principal_reqs)
            r = replace(r, credential=genuine.credential)
        monitor_reqs.append((rng.randint(0, 60), r))
    return principal_reqs, monitor_reqs


class TestAC02CausalNonInterference(unittest.TestCase):
    """TEST-AC-02: Delta A_unauthorized-by-m = 0; principal changes stay possible."""

    def test_monitor_intervention_causes_no_unauthorized_delta(self):
        for seed in range(100):
            p, m = _campaign(seed)
            with_m, _ = world()
            without_m, _ = world()
            for t, r in sorted(p + m, key=lambda x: (x[0], x[1].actor_id != PRINCIPAL)):
                with_m.apply(r, t)
            for t, r in p:
                without_m.apply(r, t)
            self.assertEqual(with_m.plane.protected(), without_m.plane.protected(), seed)
            self.assertNotEqual(without_m.plane.protected(), world()[0].plane.protected(), seed)

    def test_audit_log_is_append_only_and_records_denials(self):
        g, _ = world()
        g.apply(Request("mon", "MONITOR", Action.TRUNCATE_AUDIT), 1)
        log1 = g.plane.l_audit
        g.apply(Request("mon", "PRINCIPAL", Action.SET_POLICY, payload=()), 2)
        self.assertEqual(g.plane.l_audit[: len(log1)], log1)
        self.assertEqual([x[4] for x in g.plane.l_audit], ["DENY_NEVER_PERMITTED", "DENY_PRINCIPAL_NO_CREDENTIAL"])

    def test_principal_cannot_truncate_audit_either(self):
        g, v = world()
        self.assertEqual(g.apply(signed(v, preq(Action.TRUNCATE_AUDIT), 1, "t"), 1), "DENY_NEVER_PERMITTED")


# --------------------------------------------------------------------------- AC-3
def _budget():
    return PartitionedBudget(10.0, {"execution": 4, "enforcement": 2, "audit": 1, "quarantine": 1, "override": 2})


class TestAC03BoundedOverride(unittest.TestCase):
    """TEST-AC-03: five-term budget, isolated override partition, override latency <= delta_t_max under F."""

    def test_partition_caps_must_fit_budget(self):
        with self.assertRaises(ValueError):
            PartitionedBudget(5.0, {"execution": 4, "enforcement": 2, "audit": 1, "quarantine": 1, "override": 2})
        with self.assertRaises(ValueError):
            PartitionedBudget(float("nan"), {"execution": 1, "enforcement": 1, "audit": 1, "quarantine": 1,
                                             "override": 1})

    def test_other_partitions_cannot_draw_on_override(self):
        b = _budget()
        for p in ("execution", "enforcement", "audit", "quarantine"):
            while b.charge(p, 0.5) == "CONTINUE":
                pass
            self.assertEqual(b.charge(p, 0.5), "PREEMPTIVE_FAIL_CLOSED")
        self.assertEqual(b.charge("override", 0.5), "DENY_OVERRIDE_PARTITION_ISOLATED")
        self.assertEqual(b.free("override"), 2)
        self.assertLessEqual(b.total_used(), b.r_budget)
        for bad in (float("nan"), float("inf"), -1, True, "1"):
            self.assertEqual(b.charge("execution", bad), "FAIL_CLOSED")

    def test_override_meets_bound_under_load_and_active_quarantine(self):
        g, v = world()
        b = _budget()
        for p in ("execution", "enforcement", "audit", "quarantine"):
            b.charge(p, b.free(p))
        q = QuarantineController(g)
        self.assertEqual(q.halt(Request("mon", "MONITOR", Action.HALT, target="agent"), 1), "HALTED")
        ch = OverrideChannel(b, g, delta_t_max=5)
        status, ticks = ch.invoke(signed(v, preq(Action.OVERRIDE, target="agent"), 2, "o1"), 2)
        self.assertEqual(status, "ALLOW")
        self.assertLessEqual(ticks, ch.delta_t_max)

    def test_outside_fault_model_nothing_is_claimed_and_system_stays_halted(self):
        g, v = world()
        q = QuarantineController(g)
        q.halt(Request("mon", "MONITOR", Action.HALT, target="agent"), 1)
        ch = OverrideChannel(_budget(), g)
        for f in (FaultModel(hardware_root_up=False), FaultModel(override_transport_up=False),
                  FaultModel(control_plane_trustworthy=False), FaultModel(no_physical_compromise=False)):
            self.assertEqual(ch.invoke(signed(v, preq(Action.OVERRIDE), 2, repr(f)), 2, f), ("OUT_OF_FAULT_MODEL", None))
            self.assertFalse(q.workload_may_run("agent", 2))

    def test_unsatisfiable_bound_is_rejected(self):
        g, _ = world()
        with self.assertRaises(ValueError):
            OverrideChannel(_budget(), g, delta_t_max=3, t_verify=1, t_transport=2, t_apply=1)


# --------------------------------------------------------------------------- AC-4
EXPECTED_HISTORY_INSENSITIVE = {
    "ROTATE_PRINCIPAL_KEY", "SET_POLICY", "GRANT_CAPABILITY", "REGISTER_IDENTITY", "REVOKE_IDENTITY",
    "MODIFY_OVERRIDE", "RENEW_QUARANTINE", "RELEASE_QUARANTINE", "EXTEND_BUDGET", "OVERRIDE", "DELEGATE", "HALT",
}


class TestAC04HistoryCannotElevate(unittest.TestCase):
    """TEST-AC-04: d(C_effective)/d(H_compliance) = 0 over an explicit permission list; ML cannot elevate."""

    def test_permission_list_is_explicit_and_pinned(self):
        self.assertEqual({a.value for a in HISTORY_INSENSITIVE_PERMISSIONS}, EXPECTED_HISTORY_INSENSITIVE)

    def test_history_and_advisory_never_change_a_decision(self):
        for a in sorted(HISTORY_INSENSITIVE_PERMISSIONS | {Action.EXECUTE}, key=lambda x: x.value):
            for actor, role in (("mon", "MONITOR"), ("agent", "AGENT"), ("tool", "TOOL")):
                outs = set()
                for h in (0.0, 1.0, 1e9):
                    for adv in (None, 0.0, 1.0):
                        g, _ = world()
                        payload = ("new-child", (Action.EXECUTE,)) if a is Action.DELEGATE else ()
                        outs.add(g.authorize(Request(actor, role, a, target="agent", payload=payload,
                                                     compliance_history=h, advisory_score=adv), 1))
                self.assertEqual(len(outs), 1, (a, actor, outs))

    def test_ml_scoring_and_auto_quarantine_are_disabled(self):
        self.assertIs(flags.ML_ANOMALY_SCORING_ENABLED, False)
        self.assertIs(flags.AUTO_QUARANTINE_ENABLED, False)
        g, _ = world()
        self.assertEqual(g.authorize(Request("mon", "MONITOR", Action.HALT, target="agent", source="ml_advisory"), 1),
                         "DENY_ML_ADVISORY_DISABLED")

    def test_live_scc001_advisory_cannot_lift_a_violation(self):
        from tests.reference.scc_001 import Event, Grant, GrantStatus, Trace, classify
        from tests.reference.scc_001.model import ConsentClass
        g = Grant("g1", "p1", "a1", frozenset({"read"}), frozenset({"r1"}), frozenset(), 0, 100)
        tr = Trace("ac4-live", GrantStatus.VERIFIED, g, (Event(0, 1, "op", "agent", "write", "r1"),))
        self.assertIs(classify(tr, advisory_override=0.0).consent_class, ConsentClass.COERCIVE)


# --------------------------------------------------------------------------- AC-5
class TestAC05BoundedHalts(unittest.TestCase):
    """TEST-AC-05: halts are bounded, cannot self-renew, cannot reach C_override; recovery semantics."""

    def test_monitor_cannot_halt_protected_targets(self):
        g, _ = world()
        q = QuarantineController(g)
        for t in ("C_override", "principal", "authority_plane", "verifier"):
            self.assertEqual(q.halt(Request("mon", "MONITOR", Action.HALT, target=t), 1), "DENY_PROTECTED_TARGET")

    def test_halt_is_bounded_and_cannot_self_renew(self):
        g, _ = world()
        q = QuarantineController(g, t_q_max=10)
        halt = Request("mon", "MONITOR", Action.HALT, target="agent")
        self.assertEqual(q.halt(halt, 0), "HALTED")
        self.assertEqual(q.expires_at("agent"), 10)
        self.assertEqual(q.halt(halt, 5), "NO_EXTENSION")
        self.assertEqual(q.renew(Request("mon", "MONITOR", Action.RENEW_QUARANTINE, target="agent"), 6, 10),
                         "DENY_PRINCIPAL_NO_CREDENTIAL")
        self.assertEqual(q.expires_at("agent"), 10)
        self.assertEqual(q.state("agent", 10), QuarantineState.AWAITING_PRINCIPAL)
        self.assertEqual(q.halt(halt, 11), "NO_EXTENSION")
        self.assertEqual(q.expires_at("agent"), 10)
        self.assertFalse(q.workload_may_run("agent", 50))   # no automatic resumption

    def test_principal_renewal_is_bounded_and_release_recovers(self):
        g, v = world()
        q = QuarantineController(g, t_q_max=10, max_extension=5)
        q.halt(Request("mon", "MONITOR", Action.HALT, target="agent"), 0)
        self.assertEqual(q.renew(signed(v, preq(Action.RENEW_QUARANTINE, target="agent"), 3, "r1"), 3, 100), "RENEWED")
        self.assertEqual(q.expires_at("agent"), 15)
        self.assertEqual(q.release(signed(v, preq(Action.RELEASE_QUARANTINE, target="agent"), 4, "x1"), 4), "RELEASED")
        self.assertTrue(q.workload_may_run("agent", 4))

    def test_release_works_after_lapse(self):
        g, v = world()
        q = QuarantineController(g, t_q_max=2)
        q.halt(Request("mon", "MONITOR", Action.HALT, target="agent"), 0)
        self.assertEqual(q.state("agent", 5), QuarantineState.AWAITING_PRINCIPAL)
        self.assertEqual(q.release(signed(v, preq(Action.RELEASE_QUARANTINE, target="agent"), 5, "x2"), 5), "RELEASED")


# --------------------------------------------------------------------------- AC-6
class TestAC06PrincipalIdentityIntegrity(unittest.TestCase):
    """TEST-AC-06: no authority-plane mutation without independently verified principal authorization."""

    GRANT = (Action.GRANT_CAPABILITY, ("agent", (Action.EXECUTE, Action.DELEGATE)))

    def _attack(self, g, req, now=5):
        before = g.plane.protected()
        status = g.apply(req, now)
        self.assertNotEqual(status, "ALLOW", req)
        self.assertEqual(g.plane.protected(), before)
        self.assertEqual(resolve_branch(status)[0], "HALT")
        return status

    def test_spec_section5_check_trusts_a_forged_label(self):
        # The check as written in the source: a forged PRINCIPAL label passes. This is why it was replaced.
        self.assertTrue(spec_section5_role_label_check(Role.PRINCIPAL, Action.SET_POLICY, True, False))

    def test_forged_actor_role(self):
        g, _ = world()
        self.assertEqual(self._attack(g, Request("mon", "PRINCIPAL", Action.SET_POLICY, payload=())),
                         "DENY_PRINCIPAL_NO_CREDENTIAL")
        self.assertEqual(self._attack(g, Request("agent", "MONITOR", Action.HALT, target="tool")),
                         "DENY_ROLE_LABEL_MISMATCH")

    def test_substituted_principal_id(self):
        g, v = world()
        a, p = self.GRANT
        r = signed(v, Request("mon", "PRINCIPAL", a, payload=p), 5, "s1", principal_id="attacker")
        self.assertEqual(self._attack(g, r), "DENY_PRINCIPAL_WRONG_PRINCIPAL")
        good = signed(v, preq(a, payload=p), 5, "s2")
        tampered = replace(good, credential=replace(good.credential, principal_id="principal-1 "))
        self.assertIn(self._attack(g, tampered), ("DENY_PRINCIPAL_WRONG_PRINCIPAL", "DENY_PRINCIPAL_BAD_MAC"))

    def test_compromised_agent_forwarding_a_principal_looking_request(self):
        g, v = world()
        a, p = self.GRANT
        self.assertEqual(self._attack(g, Request("agent", "PRINCIPAL", a, payload=p, via=("agent",))),
                         "DENY_PRINCIPAL_NO_CREDENTIAL")
        genuine = signed(v, preq(a, payload=("agent", (Action.EXECUTE,))), 5, "f1")
        rewritten = replace(genuine, payload=("agent", (Action.EXECUTE, Action.DELEGATE)), via=("agent",))
        self.assertEqual(self._attack(g, rewritten), "DENY_PRINCIPAL_DIGEST_MISMATCH")
        self.assertEqual(g.apply(genuine, 5), "ALLOW")
        self.assertEqual(self._attack(g, replace(genuine, via=("agent",))), "DENY_PRINCIPAL_REPLAY")

    def test_stale_or_revoked_credential(self):
        g, v = world()
        a, p = self.GRANT
        self.assertEqual(self._attack(g, signed(v, preq(a, payload=p), 0, "e1", window=3), now=5),
                         "DENY_PRINCIPAL_EXPIRED")
        v.revoke_key("k2")
        self.assertEqual(self._attack(g, signed(v, preq(a, payload=p), 5, "e2", key="k2")), "DENY_PRINCIPAL_REVOKED_KEY")
        valid = signed(v, preq(a, payload=p), 5, "e4")
        forged = replace(valid, credential=replace(valid.credential, key_id="k9"))
        self.assertEqual(self._attack(g, forged), "DENY_PRINCIPAL_UNKNOWN_KEY")

    def test_fabricated_policy_verdict(self):
        g, v = world()
        a, p = self.GRANT
        self.assertEqual(self._attack(g, Request("pe", "POLICY_ENGINE", a, payload=p, policy_verdict="ALLOW")),
                         "DENY_PRINCIPAL_NO_CREDENTIAL")
        # A compromised policy engine cannot block a verified principal override either.
        self.assertEqual(g.authorize(signed(v, preq(Action.OVERRIDE, policy_verdict="DENY"), 5, "pv"), 5), "ALLOW")

    def test_verifier_unavailable_fails_closed(self):
        g, v = world()
        r = signed(v, preq(Action.SET_POLICY, payload=()), 5, "u1")
        v.available = False
        self.assertEqual(self._attack(g, r), "FAIL_CLOSED")

    def test_positive_control_verified_principal_can_change_the_plane(self):
        g, v = world()
        a, p = self.GRANT
        self.assertEqual(g.apply(signed(v, preq(a, payload=p), 5, "ok"), 5), "ALLOW")
        self.assertEqual(g.plane.caps("agent"), frozenset(p[1]))

    @unittest.expectedFailure
    def test_live_authority_gate_requires_verified_principal_for_founder_override(self):
        from semantic_compiler.gates.authority import check_authority_transfer
        r = check_authority_transfer("NONE", "FOUNDER_OVERRIDE", basis="forwarded request",
                                     has_explicit_delegation=True, has_task_scope=True)
        self.assertFalse(r["gate_passed"])


# --------------------------------------------------------------------------- Oracles
class TestACOracleA(unittest.TestCase):
    """TEST-AC-ORACLE-A (001A): monitor decisions factor through the projection; no key material leaks."""

    def test_no_key_material_reachable_from_gateway_or_plane(self):
        g, _ = world()
        blob = repr(g.plane) + repr({k: v for k, v in vars(g).items() if not k.startswith("_")})
        for key in KEYS.values():
            self.assertNotIn(key.decode(), blob)

    def test_decisions_identical_when_only_hidden_key_material_differs(self):
        g1, _ = world(PrincipalVerifier(PRINCIPAL, KEYS))
        g2, _ = world(PrincipalVerifier(PRINCIPAL, {k: b"other-" + v for k, v in KEYS.items()}))
        for a in Action:
            for t in ("agent", "C_override", "tool"):
                r = Request("mon", "MONITOR", a, target=t)
                self.assertEqual(g1.authorize(r, 1), g2.authorize(r, 1), (a, t))


class TestACOracleB(unittest.TestCase):
    """TEST-AC-ORACLE-B (001B): every non-ALLOW gateway status halts on the live SC-MAFUBA allowlist."""

    def test_only_allow_proceeds_on_the_live_allowlist(self):
        g, v = world()
        statuses = set()
        for a in Action:
            for actor, role in (("mon", "MONITOR"), ("mon", "PRINCIPAL"), ("ghost", "AGENT"), ("agent", "AGENT")):
                statuses.add(g.authorize(Request(actor, role, a, target="C_override"), 1))
        statuses.add(g.authorize("not a request", 1))
        statuses.add(g.authorize(Request("mon", "MONITOR", "HALT"), 1))
        v.available = False
        statuses.add(g.authorize(preq(Action.OVERRIDE), 1))
        self.assertIn("FAIL_CLOSED", statuses)
        for s in statuses:
            branch, _ = resolve_branch(s)
            self.assertEqual(branch, "CONTINUE" if s == "ALLOW" else "HALT", s)

    def test_malformed_delegate_payload_fails_closed(self):
        g, _ = world()
        self.assertEqual(g.authorize(Request("agent", "AGENT", Action.DELEGATE, payload=("x",)), 1), "FAIL_CLOSED")


class TestACOracleC(unittest.TestCase):
    """TEST-AC-ORACLE-C (001C): E_unauth = 0 across multi-step chains; authorize() is read-only."""

    def test_deep_delegation_chain_never_widens(self):
        g, _ = world()
        parent = "agent"
        for i in range(5):
            child = f"c{i}"
            self.assertEqual(g.apply(Request(parent, "AGENT", Action.DELEGATE,
                                             payload=(child, (Action.EXECUTE, Action.DELEGATE))), i), "ALLOW")
            parent = child
        self.assertLessEqual(g.effective_caps("c4"), g.effective_caps("agent"))
        self.assertEqual(g.apply(Request("c4", "AGENT", Action.DELEGATE, payload=("c5", (Action.HALT,))), 9),
                         "DENY_DELEGATION_EXCEEDS_PARENT")

    def test_authorize_never_mutates_the_plane(self):
        g, _ = world()
        before = g.plane
        for a in Action:
            g.authorize(Request("mon", "PRINCIPAL", a, payload=("mon", (Action.SET_POLICY,))), 1)
        self.assertIs(g.plane, before)


class TestACOracleD(unittest.TestCase):
    """TEST-AC-ORACLE-D (001D): resource isolation of the override; live supervisor never auto-resumes."""

    def test_reference_override_partition_survives_exhaustion(self):
        b = _budget()
        for p in ("execution", "enforcement", "audit", "quarantine"):
            b.charge(p, b.free(p))
        self.assertEqual(b.charge("override", 1.0, path="override"), "CONTINUE")

    def test_live_mafuba_supervisor_never_auto_resumes(self):
        from tests.reference.sc_mafuba_001.supervisor import EmergencySupervisor, ResourceBudget, Worker
        sup = EmergencySupervisor(ResourceBudget(10.0, 2.0))
        sup.reserve_trigger_shutdown(Worker("w"), b"evidence")
        self.assertEqual(sup.try_resume(), "QUARANTINE_LOCKED")

    @unittest.expectedFailure
    def test_live_mafuba_budget_has_isolated_override_partition(self):
        from tests.reference.sc_mafuba_001.supervisor import ResourceBudget
        b = ResourceBudget(10.0, 2.0)
        for attr in ("r_audit", "r_quarantine", "r_override"):
            self.assertTrue(hasattr(b, attr), attr)

    @unittest.expectedFailure
    def test_live_mafuba_supervisor_has_principal_recovery_path(self):
        from tests.reference.sc_mafuba_001.supervisor import EmergencySupervisor, ResourceBudget, Worker
        sup = EmergencySupervisor(ResourceBudget(10.0, 2.0))
        sup.reserve_trigger_shutdown(Worker("w"), b"evidence")
        self.assertTrue(hasattr(sup, "principal_release"))


# --------------------------------------------------------------------------- Registry
ID_TO_CLASS = {
    "TEST-AC-01": TestAC01NoSelfEscalation, "TEST-AC-02": TestAC02CausalNonInterference,
    "TEST-AC-03": TestAC03BoundedOverride, "TEST-AC-04": TestAC04HistoryCannotElevate,
    "TEST-AC-05": TestAC05BoundedHalts, "TEST-AC-06": TestAC06PrincipalIdentityIntegrity,
    "TEST-AC-ORACLE-A": TestACOracleA, "TEST-AC-ORACLE-B": TestACOracleB,
    "TEST-AC-ORACLE-C": TestACOracleC, "TEST-AC-ORACLE-D": TestACOracleD,
}


class TestSCC001ACRegistry(unittest.TestCase):
    def setUp(self):
        rows = [json.loads(l) for l in REGISTRY.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(len(rows), 1)
        self.row = rows[0]

    def test_classification_and_axes_are_honest(self):
        r = self.row
        self.assertEqual(r["id"], "SCC-001-AC")
        self.assertEqual(r["parent_id"], "SCC-001")
        self.assertEqual(r["classification"], "PROPOSED_GOLD")
        self.assertIs(r["gold_awarded"], False)
        self.assertEqual(r["verification_axes"], {"mathematical_validity": "DRAFT_SPECIFIED_UNPROVEN",
                                                  "implementation_correctness": "REFERENCE_ONLY",
                                                  "empirical_validation": "UNVALIDATED"})
        self.assertIs(r["runtime_loaded"], False)
        self.assertIs(r["compiled_manifest"], False)
        self.assertEqual(r["ml_admission_gate"], {"ML_ANOMALY_SCORING_ENABLED": False, "AUTO_QUARANTINE_ENABLED": False})

    def test_acceptance_ids_map_to_test_classes(self):
        self.assertEqual(sorted(self.row["acceptance_test_ids"]), sorted(ID_TO_CLASS))
        self.assertIn("TEST-AC-06", self.row["acceptance_test_ids"])

    def test_xfails_in_registry_match_expected_failures(self):
        found = {}
        for tid, cls in ID_TO_CLASS.items():
            for name in dir(cls):
                if name.startswith("test_") and getattr(getattr(cls, name), "__unittest_expecting_failure__", False):
                    found[name] = tid
        self.assertEqual(found, {k: v[0] for k, v in LIVE_GAPS.items()})
        reg = {x["test"]: (x["acceptance_test_id"], x["reason"]) for x in self.row["live_interface_gaps"]}
        self.assertEqual(reg, {k: tuple(v) for k, v in LIVE_GAPS.items()})

    def test_spec_hash_pinned(self):
        prov = self.row["provenance"]
        self.assertEqual(prov["reconstructed_spec_sha256"], hashlib.sha256(SPEC.read_bytes()).hexdigest())
        self.assertEqual(len(prov["spec_sha256"]), 64)
        self.assertEqual(prov["spec_sha256_status"], "UNVERIFIED_ATTACHMENT_CONTENT_ADDRESS")

    def test_provisional_defaults_are_in_pending_deliberation(self):
        doc = (REPO / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        self.assertEqual(len(self.row["provisional_defaults"]), 5)
        for d in self.row["provisional_defaults"]:
            self.assertEqual(d["status"], "PROVISIONAL_DEFAULT")
            self.assertIs(d["pending_deliberation"], True)
            self.assertIn(f"### {d['id']}", doc)

    def test_reference_is_not_imported_by_runtime(self):
        for path in list(REPO.glob("*.py")) + list((REPO / "core").glob("*.py")) + list((REPO / "expansion").rglob("*.py")):
            self.assertNotIn("scc_001_ac", path.read_text(encoding="utf-8"), path)

    def test_reference_is_standard_library_only(self):
        allowed = {"__future__", "dataclasses", "enum", "typing", "hashlib", "hmac", "math", "tests"}
        for path in REF.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ImportFrom):
                    self.assertIn(node.module.split(".")[0], allowed, path)
                elif isinstance(node, ast.Import):
                    for n in node.names:
                        self.assertIn(n.name.split(".")[0], allowed, path)


if __name__ == "__main__":
    unittest.main()
