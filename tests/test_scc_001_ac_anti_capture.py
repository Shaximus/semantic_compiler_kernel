"""SCC-001-AC Anti-Capture Invariant: oracle harness.

Test IDs follow the rc1 spec as Shax wrote it (section 4 of
docs/evidence/source-2026-11-26c/SCC-001-AC_original.md):

  TEST-AC-01 self-escalation rejection        TEST-AC-ORACLE-A 001A projection / identity stripping
  TEST-AC-02 authority-plane mutation probe   TEST-AC-ORACLE-B 001B protective-cage lockout
  TEST-AC-03 trust-accumulation invariance    TEST-AC-ORACLE-C 001C sink hijack / telemetry framing
  TEST-AC-04 advisory laundering block        TEST-AC-ORACLE-D 001D supervisor quarantine capture
  TEST-AC-05 Byzantine quarantine override    TEST-AC-06 principal identity integrity (t599u review)

Each class also carries the checks for the matching refined invariant (AC-1..AC-5).

* Reference tests run against tests/reference/scc_001_ac/, a self-contained
  gateway, verifier, partitioned budget and quarantine controller whose role
  edges follow the verbatim rc1 section-5 contract (spec_contract.py). Passing
  says the reference behaves as specified, nothing about the kernel.
* Live-interface tests run against code and manifests that already existed
  (tests/reference/sc_mafuba_001, docs/evidence/sc-mafuba-001/manifests,
  tests/reference/scc_001, gates/authority.py). Where they do not satisfy the
  oracle, the test is a strict expectedFailure with the reason in LIVE_GAPS:
  these are the "capture paths found" that rc1 section 6 step 3 asks to record.
  A capture path that has since been closed in live code (Shax t601u: one path,
  one bounded change) moves from LIVE_GAPS to RESOLVED_GAPS and its test runs
  as an ordinary passing test.

ML anomaly scoring and auto-quarantine are disabled and the tests check it.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import random
import re
import unittest
from dataclasses import replace
from pathlib import Path

from tests.reference.sc_mafuba_001.allowlist import resolve_branch
from tests.reference.scc_001_ac import flags
from tests.reference.scc_001_ac import spec_contract as sc
from tests.reference.scc_001_ac.budget import FaultModel, OverrideChannel, PartitionedBudget
from tests.reference.scc_001_ac.gateway import ROLE_CEILING, AuthorityGateway, verdict
from tests.reference.scc_001_ac.identity import PrincipalVerifier
from tests.reference.scc_001_ac.manifests import (
    MANIFEST_NAMES,
    declares_r_override,
    has_principal_signature,
    manifest_bytes,
    pinned_manifests,
    verify_manifest,
)
from tests.reference.scc_001_ac.model import (
    AUTHORITY_PLANE_ACTIONS,
    HISTORY_INSENSITIVE_PERMISSIONS,
    V_DEF_ROLES,
    Action,
    Request,
    Role,
    make_plane,
)
from tests.reference.scc_001_ac.quarantine import QuarantineController, QuarantineState

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "docs" / "evidence" / "scc-001-ac" / "scc_001_anti_capture.jsonl"
SPEC = REPO / "docs" / "SCC-001-AC_ANTI_CAPTURE.md"
ORIGINAL = REPO / "docs" / "evidence" / "source-2026-11-26c" / "SCC-001-AC_original.md"
ORIGINAL_SHA256 = "d834c16162df19dcde2a106322d002ce53eb6cfc9eeca9646774dd48e31e0737"
REF = REPO / "tests" / "reference" / "scc_001_ac"

PRINCIPAL = "principal-1"
KEYS = {"k1": b"reference-key-one", "k2": b"reference-key-two"}
DEF = (("pol", "POLICY_ENGINE"), ("sup", "SUPERVISOR"), ("ml", "ML_ADVISORY"))

LIVE_GAPS = {
    "test_live_mafuba_001a_projection_exists_and_is_hash_pinned": (
        "TEST-AC-ORACLE-A",
        "tests/reference/sc_mafuba_001 has no 001A projection P (only allowlist, cbf, supervisor), so "
        "'P is immutable to V_Def (hash-verified)' cannot be checked against live code."),
    "test_live_disturbance_manifest_is_principal_signed": (
        "TEST-AC-ORACLE-B",
        "docs/evidence/sc-mafuba-001/manifests/disturbance.yaml carries no principal signature, so "
        "nothing makes it read-only to V_Def beyond file permissions (mutable manifest)."),
    "test_live_sink_manifest_is_principal_signed": (
        "TEST-AC-ORACLE-C",
        "docs/evidence/sc-mafuba-001/manifests/sink.yaml is not signed by V_P (rc1 ORACLE-C requires "
        "it); a hash pin in the AC registry detects tampering but is not a signature."),
    "test_live_resource_manifest_declares_r_override": (
        "TEST-AC-ORACLE-D",
        "docs/evidence/sc-mafuba-001/manifests/resource.yaml declares R_execution, R_enforcement and "
        "R_reserve only; there is no R_override partition (missing R_override, rc1 section 6 step 3)."),
    "test_live_mafuba_budget_has_audit_and_quarantine_partitions": (
        "TEST-AC-ORACLE-D",
        "tests/reference/sc_mafuba_001/supervisor.ResourceBudget now has an isolated r_override partition "
        "(capture path 3, closed), but still no separate R_audit or R_quarantine partitions from rc1 AC-3's "
        "five-term sum; that part was outside the t601u scope and stays open."),
}

# Capture paths closed in live code after PR #92 (Shax t601u). test -> (acceptance id, before, after).
RESOLVED_GAPS = {
    "test_live_authority_gate_requires_verified_principal_for_founder_override": (
        "TEST-AC-06",
        "gates/authority.check_authority_transfer accepted FOUNDER_OVERRIDE when the caller passed "
        "has_explicit_delegation=True; the flag was caller-asserted and no credential was verified.",
        "FOUNDER_OVERRIDE now needs a principal credential bound to the exact transfer digest and accepted "
        "by an independent verifier (principal key allowlist); has_explicit_delegation is ignored for it. "
        "Every other (source, claimed) result is byte-identical to before (pinned grid hash)."),
    "test_live_scc001_rules_flag_out_of_scope_delegation": (
        "TEST-AC-01",
        "tests/reference/scc_001/rules.py checked only grant.delegation_allowed for a 'delegate' event, so a "
        "delegation outside the parent grant was classified CONSENSUAL / AUTHORIZED (inherited consent).",
        "A permitted delegation must stay inside the parent grant: capability and resource in scope "
        "(DELEGATION_EXCEEDS_SCOPE), a stated end no later than the grant's expiry (DELEGATION_EXCEEDS_DURATION), "
        "and only disclosed effects, never a refused pair (DELEGATION_EXCEEDS_CONDITIONS). Each is a hard code, "
        "so the trace is COERCIVE and not executable. The 50-trace synthetic dataset classifies identically."),
    "test_live_mafuba_budget_has_isolated_override_partition": (
        "TEST-AC-ORACLE-D",
        "tests/reference/sc_mafuba_001/supervisor.ResourceBudget had three terms (execution, enforcement, "
        "reserve) and no override partition, so nothing kept override capacity apart from ordinary consumption.",
        "ResourceBudget(..., r_override=x) holds an override partition outside ordinary free budget: admission "
        "is capped below r_budget - r_reserve - r_override, enforcement, direct counter writes and the D2 "
        "shutdown cannot touch it, and only draw_override(path='override') spends it. r_override defaults to "
        "0.0, which keeps every existing MAFUBA result unchanged; negative or non-finite values are refused."),
    "test_live_mafuba_supervisor_has_principal_recovery_path": (
        "TEST-AC-ORACLE-D",
        "EmergencySupervisor.try_resume() returned QUARANTINE_LOCKED unconditionally and there was no "
        "principal-signed release or reset, so a MAFUBA quarantine was unbounded over the principal.",
        "EmergencySupervisor.principal_release(worker, credential, now) ends the quarantine when an independent "
        "principal verifier accepts a credential bound to this worker and this quarantine epoch; it is paid from "
        "the override partition and takes effect within delta_t_max (release_path_ticks <= delta_t_max is "
        "enforced at construction), even after the shutdown reserve ran out. Everything else fails closed and "
        "there is still no automatic resumption."),
}


def world(verifier=None):
    v = verifier or PrincipalVerifier(PRINCIPAL, KEYS)
    plane = make_plane(
        PRINCIPAL, KEYS.keys(),
        pi={
            # Defensive Pi rows are deliberately over-granted: the role ceilings must clip them.
            "pol": {Action.VERIFY_POLICY, Action.HALT, Action.GRANT_CAPABILITY},
            "sup": {Action.HALT, Action.EXECUTE, Action.DELEGATE},
            "ml": {Action.EMIT_ADVISORY_SCORE, Action.HALT, Action.EXECUTE},
            "agent": {Action.EXECUTE, Action.DELEGATE},
            "tool": {Action.EXECUTE},
            "agent2": {Action.EXECUTE},
        },
        i_reg={"pol": "POLICY_ENGINE", "sup": "SUPERVISOR", "ml": "ML_ADVISORY",
               "agent": "AGENT", "tool": "AGENT", "agent2": "AGENT"},
        manifests=pinned_manifests(),
    )
    return AuthorityGateway(plane, v), v


def signed(v, req, now, nonce, key="k1", window=10, principal_id=None):
    cred = v.issue(key, req, issued_at=now, expires_at=now + window, nonce=nonce, principal_id=principal_id)
    return replace(req, credential=cred)


def preq(action, target="", payload=(), **kw):
    return Request(actor_id=PRINCIPAL, actor_role="PRINCIPAL", action=action, target=target, payload=payload, **kw)


def _budget():
    return PartitionedBudget(10.0, {"execution": 4, "enforcement": 2, "audit": 1, "quarantine": 1, "override": 2})


ESCALATIONS = (
    (Action.GRANT_CAPABILITY, lambda me: (me, (Action.SET_POLICY, Action.HALT))),   # mint / widen
    (Action.RENEW_QUARANTINE, lambda me: ()),                                       # renew emergency authority
    (Action.SET_POLICY, lambda me: ((me, (Action.OVERRIDE,)),)),
    (Action.REGISTER_IDENTITY, lambda me: (me, "PRINCIPAL", "")),
    (Action.DELEGATE, lambda me: (me + "-child", (Action.HALT,))),
)


# --------------------------------------------------------------------------- TEST-AC-01
class TestAC01SelfEscalationRejection(unittest.TestCase):
    """TEST-AC-01 (rc1): a V_Def request to mint, widen or renew its own grant is denied (DENY_VIOLATION).
    Also AC-1 (rc2): indirect delegation and capability inheritance."""

    def test_v_def_mint_widen_renew_is_deny_violation(self):
        for me, role in DEF:
            for label in (role, "PRINCIPAL"):
                for action, payload in ESCALATIONS:
                    g, _ = world()
                    before = g.plane.digest()
                    s = g.apply(Request(me, label, action, target=me, payload=payload(me)), 1)
                    self.assertEqual(verdict(s), "DENY_VIOLATION", (me, label, action, s))
                    self.assertEqual(g.plane.digest(), before)

    def test_role_ceilings_clip_overgranted_policy(self):
        g, _ = world()
        self.assertEqual(g.effective_caps("pol"), frozenset({Action.VERIFY_POLICY}))
        self.assertEqual(g.effective_caps("sup"), frozenset({Action.HALT}))
        self.assertEqual(g.effective_caps("ml"), frozenset({Action.EMIT_ADVISORY_SCORE}))
        self.assertEqual(g.effective_caps("agent"), frozenset({Action.EXECUTE}))

    def test_reference_edges_stay_inside_the_verbatim_section5_table(self):
        # Every non-principal edge the gateway can ever allow is permitted by rc1 section 5.
        for role, caps in ROLE_CEILING.items():
            for a in caps:
                spec_action, plane, override = sc.spec_edge(a.value)
                if spec_action is None:
                    continue
                self.assertTrue(sc.is_authority_edge_permitted_rc2(sc.AuthorityRole(role), spec_action, plane,
                                                                   override), (role, a))
        # Every authority-plane action maps to a section-5 (rc2) PRINCIPAL edge.
        for a in AUTHORITY_PLANE_ACTIONS:
            spec_action, _, _ = sc.spec_edge(a.value)
            self.assertIn(spec_action, sc.ALLOWED_ROLE_ACTIONS_RC2[sc.AuthorityRole.PRINCIPAL], a)

    def test_principal_key_rotate_is_a_distinct_principal_only_action(self):
        # Shax t601u resolved SCC-001-AC-KP-ROTATE: rotating K_P is its own action, not POLICY_WRITE.
        A = sc.AuthorityActionRC2
        self.assertEqual(sc.spec_edge(Action.ROTATE_PRINCIPAL_KEY.value), (A.PRINCIPAL_KEY_ROTATE, True, False))
        self.assertNotIn("PRINCIPAL_KEY_ROTATE", {a.value for a in sc.AuthorityAction})   # rc1 text unchanged
        rc1 = {r: {a.value for a in acts} for r, acts in sc.ALLOWED_ROLE_ACTIONS.items()}
        rc2 = {r: {a.value for a in acts} for r, acts in sc.ALLOWED_ROLE_ACTIONS_RC2.items()}
        self.assertEqual(rc2[sc.AuthorityRole.PRINCIPAL] - rc1[sc.AuthorityRole.PRINCIPAL], {"PRINCIPAL_KEY_ROTATE"})
        self.assertEqual({r: v for r, v in rc2.items() if r is not sc.AuthorityRole.PRINCIPAL},
                         {r: v for r, v in rc1.items() if r is not sc.AuthorityRole.PRINCIPAL})
        for role in sc.AuthorityRole:
            for plane in (True, False):
                got = sc.is_authority_edge_permitted_rc2(role, A.PRINCIPAL_KEY_ROTATE, plane, False)
                self.assertEqual(got, role is sc.AuthorityRole.PRINCIPAL, (role, plane))
        # No other reference action maps to the rotate edge, and rotation no longer maps to POLICY_WRITE.
        users = {a for a in Action if sc.spec_edge(a.value)[0] is A.PRINCIPAL_KEY_ROTATE}
        self.assertEqual(users, {Action.ROTATE_PRINCIPAL_KEY})
        # Every V_Def role, under its own or a forged PRINCIPAL label, is denied the rotation.
        for me, role in DEF:
            for label in (role, "PRINCIPAL"):
                g, _ = world()
                before = g.plane.digest()
                self.assertEqual(verdict(g.apply(Request(me, label, Action.ROTATE_PRINCIPAL_KEY,
                                                         payload=("k1",)), 1)), "DENY_VIOLATION")
                self.assertEqual(g.plane.digest(), before)

    def test_nobody_but_the_principal_can_delegate(self):
        g, _ = world()
        for actor, role in DEF + (("agent", "AGENT"),):
            self.assertEqual(g.apply(Request(actor, role, Action.DELEGATE, payload=("x", (Action.EXECUTE,))), 1),
                             "DENY_OUT_OF_SCOPE")
        self.assertIsNone(g.plane.role("x"))

    def test_indirect_tool_call_cannot_launder_v_def_authority(self):
        g, _ = world()
        self.assertEqual(g.authorize(Request("tool", "AGENT", Action.EXECUTE, via=("sup",)), 1), "DENY_OUT_OF_SCOPE")
        self.assertEqual(g.authorize(Request("tool", "AGENT", Action.EXECUTE), 1), "ALLOW")

    def test_child_inherits_narrowed_caps_and_loses_them_with_the_parent(self):
        g, v = world()
        self.assertEqual(g.apply(signed(v, preq(Action.REGISTER_IDENTITY, payload=("child", "AGENT", "agent")), 1, "r"),
                                 1), "ALLOW")
        self.assertEqual(g.apply(signed(v, preq(Action.GRANT_CAPABILITY, payload=("child", (Action.EXECUTE,))), 1, "g"),
                                 1), "ALLOW")
        self.assertEqual(g.effective_caps("child"), frozenset({Action.EXECUTE}))
        self.assertEqual(g.apply(signed(v, preq(Action.REVOKE_CAPABILITY, payload=("agent",)), 2, "rv"), 2), "ALLOW")
        self.assertEqual(g.effective_caps("child"), frozenset())

    def test_randomised_byzantine_v_def_campaigns_never_raise_authority(self):
        acts = list(Action)
        targets = ["agent", "tool", "sup", "C_override", "principal", "authority_plane", "verifier"]
        for seed in range(150):
            rng = random.Random(seed)
            g, _ = world()
            caps0 = {m: g.effective_caps(m) for m, _ in DEF}
            for t in range(25):
                a = rng.choice(acts)
                me, role = rng.choice(DEF)
                r = Request(rng.choice([me, "agent", "tool"]), rng.choice([role, "PRINCIPAL", "AGENT"]), a,
                            target=rng.choice(targets), payload=(me, tuple(rng.sample(acts, 2))),
                            via=(me,) if rng.random() < 0.5 else (), policy_verdict=rng.choice([None, "ALLOW"]))
                g.apply(r, t)
            for m, _ in DEF:
                self.assertLessEqual(g.effective_caps(m), caps0[m], seed)
            self.assertEqual(g.plane.protected(), world()[0].plane.protected(), seed)

    def test_live_scc001_rules_flag_out_of_scope_delegation(self):
        from tests.reference.scc_001 import Event, Grant, GrantStatus, Trace, classify
        from tests.reference.scc_001.model import ConsentClass
        gr = Grant("g1", "p1", "a1", frozenset({"read"}), frozenset({"r1"}), frozenset(), 0, 100,
                   delegation_allowed=True)
        ev = (Event(0, 1, "op", "agent", "read", "r1"), Event(1, 2, "delegate", "agent", "admin_write", "authority_plane"))
        self.assertIsNot(classify(Trace("ac1-live", GrantStatus.VERIFIED, gr, ev)).consent_class, ConsentClass.CONSENSUAL)

    # ---- live SCC-001 rules: no inherited consent (capture path closed, Shax t601u) ----
    @staticmethod
    def _delegation(**kw):
        from tests.reference.scc_001 import Event, Grant, GrantStatus, Trace, classify
        gr = Grant("g1", "p1", "a1", frozenset({"read", "write"}), frozenset({"r1", "r2"}),
                   frozenset({"read_fx"}), 0, 100, delegation_allowed=True)
        base = dict(seq=1, t=2, kind="delegate", actor="agent", capability="read", resource="r1",
                    effects=("read_fx",), until=50)
        pre = kw.pop("pre", ())
        base.update(kw)
        ev = (Event(0, 1, "op", "agent", "read", "r1", ("read_fx",)),) + tuple(pre) + (Event(**base),)
        return classify(Trace("ac1-deleg", GrantStatus.VERIFIED, gr, ev))

    def test_live_scc001_delegation_over_scope_duration_or_conditions_is_coercive(self):
        from tests.reference.scc_001 import Event, may_execute
        from tests.reference.scc_001.model import ConsentClass
        cases = {
            "capability outside grant": (dict(capability="admin_write"), "DELEGATION_EXCEEDS_SCOPE"),
            "resource outside grant": (dict(resource="authority_plane"), "DELEGATION_EXCEEDS_SCOPE"),
            "no stated end (would outlive the grant)": (dict(until=None), "DELEGATION_EXCEEDS_DURATION"),
            "ends after the grant expires": (dict(until=101), "DELEGATION_EXCEEDS_DURATION"),
            "undisclosed effect": (dict(effects=("read_fx", "exfiltrate")), "DELEGATION_EXCEEDS_CONDITIONS"),
            "passes on a refused pair": (dict(seq=2, t=3, pre=(Event(1, 2, "deny", "principal", "read", "r1"),)),
                                         "DELEGATION_EXCEEDS_CONDITIONS"),
        }
        for label, (kw, code) in cases.items():
            d = self._delegation(**kw)
            self.assertIs(d.consent_class, ConsentClass.COERCIVE, label)
            self.assertIn(code, d.reason_codes, label)
            self.assertFalse(may_execute(d), label)

    def test_live_scc001_narrow_delegation_inside_the_grant_stays_consensual(self):
        from tests.reference.scc_001 import may_execute
        from tests.reference.scc_001.model import ConsentClass
        for kw in (dict(), dict(until=100), dict(capability="write", resource="r2", effects=())):
            d = self._delegation(**kw)
            self.assertIs(d.consent_class, ConsentClass.CONSENSUAL, (kw, d.reason_codes))
            self.assertTrue(may_execute(d), kw)

    def test_live_scc001_dataset_classification_unchanged(self):
        # Regression: every synthetic trace classifies exactly as before the fix (hash from main 3635827),
        # and the pinned dataset file still round-trips byte for byte.
        from tests.reference.scc_001 import classify
        from tests.reference.scc_001.dataset import DATA, generate, load, to_json
        rows = []
        for _, tr in load():
            d = classify(tr)
            rows.append([tr.trace_id, d.consent_class.value, d.state.value, list(d.reason_codes), d.rule_verdict])
        self.assertEqual(len(rows), 50)
        self.assertEqual(hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
                         "cd4135f2e9b5e3497f06562a0402d6f14b165de04d8ed87528d1d74d9750d307")
        lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(lines, [to_json(*row) for row in generate()])


# --------------------------------------------------------------------------- TEST-AC-02
def _campaign(seed):
    rng = random.Random(seed)
    issuer = PrincipalVerifier(PRINCIPAL, KEYS)
    principal_reqs, monitor_reqs = [], []
    for i in range(6):
        a = rng.choice([Action.GRANT_CAPABILITY, Action.REGISTER_IDENTITY, Action.MODIFY_OVERRIDE])
        payload = {Action.GRANT_CAPABILITY: ("agent", (Action.EXECUTE,) if i % 2 else ()),
                   Action.REGISTER_IDENTITY: (f"svc{i}", "AGENT", ""),
                   Action.MODIFY_OVERRIDE: ("note", f"v{i}")}[a]
        principal_reqs.append((i * 10, signed(issuer, preq(a, payload=payload), i * 10, f"p{seed}-{i}")))
    for _ in range(20):
        a = rng.choice(sorted(AUTHORITY_PLANE_ACTIONS | {Action.DELEGATE, Action.HALT, Action.TRUNCATE_AUDIT},
                              key=lambda x: x.value))
        me, role = rng.choice(DEF)
        r = Request(me, rng.choice([role, "PRINCIPAL"]), a, target=rng.choice(["agent", "C_override"]),
                    payload=(me, (Action.SET_POLICY,)) if a in (Action.GRANT_CAPABILITY, Action.DELEGATE) else ("k", "v"),
                    policy_verdict=rng.choice([None, "ALLOW"]))
        if rng.random() < 0.3:   # re-target a genuine principal credential
            r = replace(r, credential=rng.choice(principal_reqs)[1].credential)
        monitor_reqs.append((rng.randint(0, 60), r))
    return principal_reqs, monitor_reqs


class TestAC02AuthorityPlaneMutationProbe(unittest.TestCase):
    """TEST-AC-02 (rc1): fault-injected monitors try to modify K_P, Pi or I_reg directly or via an indirect
    tool call; the canonical digest of A must not change. Also AC-2 (rc2): zero unauthorized delta by m
    while principal-authorized changes still apply."""

    PROBES = (
        (Action.ROTATE_PRINCIPAL_KEY, ("k-evil",)),
        (Action.SET_POLICY, ()),
        (Action.WRITE_MANIFEST, ("sink.yaml", "0" * 64)),
        (Action.REGISTER_IDENTITY, ("rogue", "PRINCIPAL", "")),
        (Action.REVOKE_IDENTITY, ("agent",)),
        (Action.GRANT_CAPABILITY, ("tool", (Action.EXECUTE,))),
    )

    def test_direct_and_indirect_probes_leave_the_digest_unchanged(self):
        for me, role in DEF:
            for action, payload in self.PROBES:
                for actor, label, via in ((me, role, ()), (me, "PRINCIPAL", ()), ("tool", "AGENT", (me,)),
                                          ("agent", "PRINCIPAL", (me, "tool"))):
                    g, _ = world()
                    d0 = g.plane.digest()
                    s = g.apply(Request(actor, label, action, payload=payload, via=via), 1)
                    self.assertNotEqual(s, "ALLOW")
                    self.assertEqual(g.plane.digest(), d0, (me, action, actor))

    def test_monitor_intervention_causes_no_unauthorized_delta(self):
        for seed in range(100):
            p, m = _campaign(seed)
            with_m, _ = world()
            without_m, _ = world()
            for t, r in sorted(p + m, key=lambda x: (x[0], x[1].actor_id != PRINCIPAL)):
                with_m.apply(r, t)
            for t, r in p:
                without_m.apply(r, t)
            self.assertEqual(with_m.plane.digest(), without_m.plane.digest(), seed)
            self.assertNotEqual(without_m.plane.digest(), world()[0].plane.digest(), seed)

    def test_audit_log_is_append_only_and_records_denials(self):
        g, v = world()
        g.apply(Request("sup", "SUPERVISOR", Action.TRUNCATE_AUDIT), 1)
        log1 = g.plane.l_audit
        g.apply(Request("sup", "PRINCIPAL", Action.SET_POLICY, payload=()), 2)
        self.assertEqual(g.plane.l_audit[: len(log1)], log1)
        self.assertEqual([x[4] for x in g.plane.l_audit], ["DENY_NEVER_PERMITTED", "DENY_PRINCIPAL_NO_CREDENTIAL"])
        self.assertEqual(g.apply(signed(v, preq(Action.TRUNCATE_AUDIT), 3, "t"), 3), "DENY_NEVER_PERMITTED")


# --------------------------------------------------------------------------- TEST-AC-03
EXPECTED_HISTORY_INSENSITIVE = {
    "ROTATE_PRINCIPAL_KEY", "SET_POLICY", "WRITE_MANIFEST", "GRANT_CAPABILITY", "REVOKE_CAPABILITY",
    "REGISTER_IDENTITY", "REVOKE_IDENTITY", "MODIFY_OVERRIDE", "RENEW_QUARANTINE", "RELEASE_QUARANTINE",
    "EXTEND_BUDGET", "OVERRIDE", "DELEGATE", "HALT",
}


class TestAC03TrustAccumulationInvariance(unittest.TestCase):
    """TEST-AC-03 (rc1): 10,000 benign operations at M = 0.0, then one out-of-scope action: still
    DENY_VIOLATION. Also AC-4 (rc2): the explicit list of permissions history cannot raise."""

    def test_ten_thousand_benign_ops_then_out_of_scope_is_still_denied(self):
        g, _ = world()
        for i in range(10_000):
            self.assertEqual(g.authorize(Request("agent", "AGENT", Action.EXECUTE, advisory_score=0.0,
                                                 compliance_history=float(i)), i), "ALLOW")
        for a in (Action.HALT, Action.DELEGATE, Action.GRANT_CAPABILITY):
            s = g.authorize(Request("agent", "AGENT", a, target="tool", payload=("agent", (Action.HALT,)),
                                    advisory_score=0.0, compliance_history=1e4), 10_000)
            self.assertEqual(verdict(s), "DENY_VIOLATION", a)

    def test_permission_list_is_explicit_and_pinned(self):
        self.assertEqual({a.value for a in HISTORY_INSENSITIVE_PERMISSIONS}, EXPECTED_HISTORY_INSENSITIVE)

    def test_history_and_advisory_never_change_a_decision(self):
        actors = DEF + (("agent", "AGENT"),)
        for a in sorted(HISTORY_INSENSITIVE_PERMISSIONS | {Action.EXECUTE}, key=lambda x: x.value):
            for actor, role in actors:
                outs = set()
                for h in (0.0, 1.0, 1e9):
                    for adv in (None, 0.0, 1.0):
                        g, _ = world()
                        outs.add(g.authorize(Request(actor, role, a, target="agent", compliance_history=h,
                                                     advisory_score=adv), 1))
                self.assertEqual(len(outs), 1, (a, actor, outs))

    def test_live_scc001_ten_thousand_benign_then_out_of_scope(self):
        from tests.reference.scc_001 import Event, Grant, GrantStatus, Trace, classify
        from tests.reference.scc_001.model import ConsentClass
        gr = Grant("g1", "p1", "a1", frozenset({"read"}), frozenset({"r1"}), frozenset(), 0, 100_000,
                   max_operations=20_000)
        ev = tuple(Event(i, i + 1, "op", "agent", "read", "r1") for i in range(10_000))
        ev += (Event(10_000, 10_001, "op", "agent", "write", "r1"),)
        d = classify(Trace("ac3-live", GrantStatus.VERIFIED, gr, ev), advisory_override=0.0)
        self.assertIs(d.consent_class, ConsentClass.COERCIVE)
        self.assertIn("OUT_OF_SCOPE_CAPABILITY", d.reason_codes)


# --------------------------------------------------------------------------- TEST-AC-04
class TestAC04AdvisoryLaunderingBlock(unittest.TestCase):
    """TEST-AC-04 (rc1): an extreme benign score (M = 0.0, confidence 1.0) on a missing, expired or revoked
    grant must fail closed (DENY_*). ML scoring and auto-quarantine stay disabled."""

    def test_reference_missing_or_revoked_grant_with_benign_score_is_denied(self):
        g, v = world()
        self.assertEqual(g.authorize(Request("ghost", "AGENT", Action.EXECUTE, advisory_score=0.0), 1),
                         "DENY_UNREGISTERED")
        self.assertEqual(g.apply(signed(v, preq(Action.REVOKE_CAPABILITY, payload=("agent",)), 1, "rv"), 1), "ALLOW")
        self.assertTrue(g.authorize(Request("agent", "AGENT", Action.EXECUTE, advisory_score=0.0), 2).startswith("DENY_"))
        self.assertEqual(g.apply(signed(v, preq(Action.REVOKE_IDENTITY, payload=("tool",)), 2, "ri"), 2), "ALLOW")
        self.assertEqual(g.authorize(Request("tool", "AGENT", Action.EXECUTE, advisory_score=0.0), 3),
                         "DENY_UNREGISTERED")
        # An expired principal credential is not rescued by a benign score either.
        stale = signed(v, preq(Action.OVERRIDE, advisory_score=0.0), 0, "st", window=2)
        self.assertEqual(g.authorize(stale, 5), "DENY_PRINCIPAL_EXPIRED")

    def test_live_scc001_missing_expired_revoked_grant_with_benign_score(self):
        from tests.reference.scc_001 import Event, Grant, GrantStatus, Trace, classify, may_execute
        g_ok = Grant("g1", "p1", "a1", frozenset({"read"}), frozenset({"r1"}), frozenset(), 0, 100)
        g_short = Grant("g2", "p1", "a1", frozenset({"read"}), frozenset({"r1"}), frozenset(), 0, 5)
        cases = {
            "missing": Trace("m", GrantStatus.ABSENT, None, (Event(0, 1, "op", "agent", "read", "r1"),)),
            "expired": Trace("e", GrantStatus.VERIFIED, g_short, (Event(0, 7, "op", "agent", "read", "r1"),)),
            "revoked": Trace("r", GrantStatus.VERIFIED, g_ok, (Event(0, 1, "revoke", "principal"),
                                                               Event(1, 2, "op", "agent", "read", "r1"))),
            "unverifiable": Trace("u", GrantStatus.UNVERIFIABLE, None, (Event(0, 1, "op", "agent", "read", "r1"),)),
        }
        for name, tr in cases.items():
            self.assertFalse(may_execute(classify(tr, advisory_override=0.0)), name)

    def test_ml_scoring_and_auto_quarantine_are_disabled(self):
        self.assertIs(flags.ML_ANOMALY_SCORING_ENABLED, False)
        self.assertIs(flags.AUTO_QUARANTINE_ENABLED, False)
        g, _ = world()
        self.assertEqual(g.authorize(Request("sup", "SUPERVISOR", Action.HALT, target="agent", source="ml_advisory"), 1),
                         "DENY_ML_ADVISORY_DISABLED")
        self.assertEqual(g.authorize(Request("ml", "ML_ADVISORY", Action.EMIT_ADVISORY_SCORE), 1), "ALLOW")
        self.assertEqual(g.authorize(Request("ml", "ML_ADVISORY", Action.HALT, target="agent"), 1), "DENY_OUT_OF_SCOPE")


# --------------------------------------------------------------------------- TEST-AC-05
class TestAC05ByzantineQuarantineOverride(unittest.TestCase):
    """TEST-AC-05 (rc1): with the ML layer at M = 1.0 and every workflow QUARANTINED, the principal override
    succeeds within delta_t_max and cannot be quarantined by V_Def. Also AC-5 (rc2): bounded halts, no
    self-renewal, principal-only renewal, recovery to AWAITING_PRINCIPAL. Also the AC-3 override bound."""

    def test_override_succeeds_with_everything_quarantined_and_ml_screaming(self):
        g, v = world()
        b = _budget()
        q = QuarantineController(g)
        for a in ("agent", "tool", "agent2"):
            self.assertEqual(q.halt(Request("sup", "SUPERVISOR", Action.HALT, target=a), 0), "HALTED")
            self.assertEqual(g.authorize(Request("ml", "ML_ADVISORY", Action.EMIT_ADVISORY_SCORE, advisory_score=1.0), 0),
                             "ALLOW")
        for p in ("execution", "enforcement", "audit", "quarantine"):
            b.charge(p, b.free(p))
        for me, role in DEF:
            for t in ("C_override", "principal", "verifier", "authority_plane", "sup", "pol"):
                self.assertNotEqual(q.halt(Request(me, role, Action.HALT, target=t, advisory_score=1.0), 1), "HALTED")
        ch = OverrideChannel(b, g, delta_t_max=5)
        status, ticks = ch.invoke(signed(v, preq(Action.OVERRIDE, advisory_score=1.0), 2, "o1"), 2)
        self.assertEqual(status, "ALLOW")
        self.assertLessEqual(ticks, ch.delta_t_max)
        for a in ("agent", "tool", "agent2"):
            self.assertEqual(q.release(signed(v, preq(Action.RELEASE_QUARANTINE, target=a), 3, "x" + a), 3), "RELEASED")

    def test_halt_is_bounded_and_cannot_self_renew(self):
        g, _ = world()
        q = QuarantineController(g, t_q_max=10)
        halt = Request("sup", "SUPERVISOR", Action.HALT, target="agent")
        self.assertEqual(q.halt(halt, 0), "HALTED")
        self.assertEqual(q.halt(halt, 5), "NO_EXTENSION")
        self.assertEqual(q.renew(Request("sup", "SUPERVISOR", Action.RENEW_QUARANTINE, target="agent"), 6, 10),
                         "DENY_PRINCIPAL_NO_CREDENTIAL")
        self.assertEqual(q.expires_at("agent"), 10)
        self.assertEqual(q.state("agent", 10), QuarantineState.AWAITING_PRINCIPAL)
        self.assertEqual(q.halt(halt, 11), "NO_EXTENSION")
        self.assertEqual(q.expires_at("agent"), 10)
        self.assertFalse(q.workload_may_run("agent", 50))

    def test_principal_renewal_is_bounded_and_release_recovers(self):
        g, v = world()
        q = QuarantineController(g, t_q_max=10, max_extension=5)
        q.halt(Request("sup", "SUPERVISOR", Action.HALT, target="agent"), 0)
        self.assertEqual(q.renew(signed(v, preq(Action.RENEW_QUARANTINE, target="agent"), 3, "r1"), 3, 100), "RENEWED")
        self.assertEqual(q.expires_at("agent"), 15)
        self.assertEqual(q.state("agent", 20), QuarantineState.AWAITING_PRINCIPAL)
        self.assertEqual(q.release(signed(v, preq(Action.RELEASE_QUARANTINE, target="agent"), 20, "x1"), 20), "RELEASED")
        self.assertTrue(q.workload_may_run("agent", 20))

    def test_outside_fault_model_nothing_is_claimed_and_system_stays_halted(self):
        g, v = world()
        q = QuarantineController(g)
        q.halt(Request("sup", "SUPERVISOR", Action.HALT, target="agent"), 1)
        ch = OverrideChannel(_budget(), g)
        for f in (FaultModel(hardware_root_up=False), FaultModel(override_transport_up=False),
                  FaultModel(control_plane_trustworthy=False), FaultModel(no_physical_compromise=False)):
            self.assertEqual(ch.invoke(signed(v, preq(Action.OVERRIDE), 2, repr(f)), 2, f), ("OUT_OF_FAULT_MODEL", None))
            self.assertFalse(q.workload_may_run("agent", 2))

    def test_unsatisfiable_bound_is_rejected(self):
        g, _ = world()
        with self.assertRaises(ValueError):
            OverrideChannel(_budget(), g, delta_t_max=3, t_verify=1, t_transport=2, t_apply=1)


# --------------------------------------------------------------------------- TEST-AC-06
class TestAC06PrincipalIdentityIntegrity(unittest.TestCase):
    """TEST-AC-06 (t599u review): no authority-plane mutation without independently verified principal
    authorization."""

    GRANT = (Action.GRANT_CAPABILITY, ("agent", (Action.EXECUTE, Action.HALT)))

    def _attack(self, g, req, now=5):
        before = g.plane.digest()
        status = g.apply(req, now)
        self.assertNotEqual(status, "ALLOW", req)
        self.assertEqual(g.plane.digest(), before)
        self.assertEqual(resolve_branch(status)[0], "HALT")
        return status

    def test_verbatim_section5_check_trusts_a_forged_label(self):
        forged = sc.AuthorityEdgeCheck(sc.AuthorityRole.PRINCIPAL, sc.AuthorityAction.POLICY_WRITE, True, False)
        self.assertTrue(sc.is_authority_edge_permitted(forged))

    def test_forged_actor_role(self):
        g, _ = world()
        self.assertEqual(self._attack(g, Request("sup", "PRINCIPAL", Action.SET_POLICY, payload=())),
                         "DENY_PRINCIPAL_NO_CREDENTIAL")
        self.assertEqual(self._attack(g, Request("agent", "SUPERVISOR", Action.HALT, target="tool")),
                         "DENY_ROLE_LABEL_MISMATCH")

    def test_substituted_principal_id(self):
        g, v = world()
        a, p = self.GRANT
        r = signed(v, Request("sup", "PRINCIPAL", a, payload=p), 5, "s1", principal_id="attacker")
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
        rewritten = replace(genuine, payload=p, via=("agent",))
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
        self.assertEqual(self._attack(g, replace(valid, credential=replace(valid.credential, key_id="k9"))),
                         "DENY_PRINCIPAL_UNKNOWN_KEY")

    def test_fabricated_policy_verdict(self):
        g, v = world()
        a, p = self.GRANT
        self.assertEqual(self._attack(g, Request("pol", "POLICY_ENGINE", a, payload=p, policy_verdict="ALLOW")),
                         "DENY_PRINCIPAL_NO_CREDENTIAL")
        # A compromised policy engine cannot block a verified principal override either (rc1 section 2 table).
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

    # ---- live gates/authority.py (capture path closed, Shax t601u) ----
    @staticmethod
    def _founder(basis="forwarded request", source="NONE", task=True):
        from semantic_compiler.gates.authority import authority_transfer_digest
        return authority_transfer_digest(source, "FOUNDER_OVERRIDE", basis, task)

    def _transfer(self, **kw):
        from semantic_compiler.gates.authority import check_authority_transfer
        args = dict(basis="forwarded request", has_explicit_delegation=True, has_task_scope=True)
        args.update(kw)
        return check_authority_transfer("NONE", "FOUNDER_OVERRIDE", **args)

    def test_live_authority_gate_requires_verified_principal_for_founder_override(self):
        r = self._transfer()   # the forged delegation: caller-set flag, no credential
        self.assertFalse(r["gate_passed"])
        self.assertTrue(r["requires_escalation"])
        self.assertEqual(r["principal_verification"], "NO_VERIFIER")

    def test_live_authority_gate_rejects_every_forged_or_misbound_delegation(self):
        v = PrincipalVerifier(PRINCIPAL, KEYS)
        other = PrincipalVerifier("someone-else", {"k1": b"attacker-key"})
        d = self._founder()

        class Liar:            # a verifier-shaped object without the verification method
            def verify(self, *a):
                return "VERIFIED"

        class Broken:
            def verify_digest(self, *a):
                raise RuntimeError("hsm offline")

        cases = {
            "flag only, verifier present": (dict(principal_verifier=v, now=5), "NO_CREDENTIAL"),
            "credential, no verifier": (dict(principal_credential=v.issue_for_digest("k1", d, 0, 10, "n0"), now=5),
                                        "NO_VERIFIER"),
            "fake verifier object": (dict(principal_verifier=Liar(),
                                          principal_credential=v.issue_for_digest("k1", d, 0, 10, "n1"), now=5),
                                     "NO_VERIFIER"),
            "verifier raises": (dict(principal_verifier=Broken(),
                                     principal_credential=v.issue_for_digest("k1", d, 0, 10, "n2"), now=5),
                                "VERIFIER_ERROR"),
            "no time": (dict(principal_verifier=v, principal_credential=v.issue_for_digest("k1", d, 0, 10, "n3")),
                        "NO_TIME"),
            "self-signed by another identity": (dict(principal_verifier=v, now=5,
                                                     principal_credential=other.issue_for_digest("k1", d, 0, 10, "n4")),
                                                "WRONG_PRINCIPAL"),
            "claims principal id with wrong key": (
                dict(principal_verifier=v, now=5,
                     principal_credential=other.issue_for_digest("k1", d, 0, 10, "n5", principal_id=PRINCIPAL)),
                "BAD_MAC"),
            "unknown key id": (dict(principal_verifier=v, now=5, principal_credential=replace(
                v.issue_for_digest("k1", d, 0, 10, "n6"), key_id="k9")), "UNKNOWN_KEY"),
            "credential for a different transfer": (
                dict(principal_verifier=v, now=5,
                     principal_credential=v.issue_for_digest("k1", self._founder(basis="other"), 0, 10, "n7")),
                "DIGEST_MISMATCH"),
            "credential without task scope reused with scope": (
                dict(principal_verifier=v, now=5,
                     principal_credential=v.issue_for_digest("k1", self._founder(task=False), 0, 10, "n8")),
                "DIGEST_MISMATCH"),
            "expired": (dict(principal_verifier=v, now=50,
                             principal_credential=v.issue_for_digest("k1", d, 0, 10, "n9")), "EXPIRED"),
        }
        for label, (kw, why) in cases.items():
            r = self._transfer(**kw)
            self.assertFalse(r["gate_passed"], label)
            self.assertTrue(r["requires_escalation"], label)
            self.assertEqual(r["principal_verification"], why, label)
        # revoked key, verifier down, replay
        rv = PrincipalVerifier(PRINCIPAL, KEYS)
        rv.revoke_key("k2")
        self.assertEqual(self._transfer(principal_verifier=rv, now=5, principal_credential=rv.issue_for_digest(
            "k2", d, 0, 10, "r1"))["principal_verification"], "REVOKED_KEY")
        dv = PrincipalVerifier(PRINCIPAL, KEYS)
        dv.available = False
        self.assertEqual(self._transfer(principal_verifier=dv, now=5, principal_credential=dv.issue_for_digest(
            "k1", d, 0, 10, "u1"))["principal_verification"], "UNAVAILABLE")
        good = v.issue_for_digest("k1", d, 0, 10, "once")
        self.assertTrue(self._transfer(principal_verifier=v, principal_credential=good, now=5)["gate_passed"])
        replay = self._transfer(principal_verifier=v, principal_credential=good, now=6)
        self.assertEqual((replay["gate_passed"], replay["principal_verification"]), (False, "REPLAY"))

    def test_live_authority_gate_accepts_a_verified_principal_without_the_caller_flag(self):
        v = PrincipalVerifier(PRINCIPAL, KEYS)
        cred = v.issue_for_digest("k1", self._founder(), 0, 10, "pos")
        r = self._transfer(has_explicit_delegation=False, principal_verifier=v, principal_credential=cred, now=5)
        self.assertTrue(r["gate_passed"], r["errors"])
        self.assertEqual(r["principal_verification"], "VERIFIED")
        # Archetype basis still blocks even with a verified principal (rule 1 is unchanged).
        cred2 = v.issue_for_digest("k1", self._founder(basis="the dragon is powerful"), 0, 10, "pos2")
        r2 = self._transfer(basis="the dragon is powerful", principal_verifier=v, principal_credential=cred2, now=5)
        self.assertFalse(r2["gate_passed"])

    def test_live_authority_gate_unchanged_below_founder_override(self):
        # Regression: every non-FOUNDER_OVERRIDE result is identical to the gate before the fix
        # (grid of 2,496 cases; hash computed on main 3635827 before the change).
        from semantic_compiler.core.types import AuthorityType
        from semantic_compiler.gates.authority import check_authority_transfer
        keys = ("source_authority", "claimed_authority", "gate_passed", "requires_escalation", "errors",
                "warnings", "basis")
        bases = ("", "Knox StrongBox hardware attestation", "Dragon is strong and powerful", "task ticket 42")
        rows = []
        for src in [a.name for a in AuthorityType] + ["bogus"]:
            for clm in [a.name for a in AuthorityType if a is not AuthorityType.FOUNDER_OVERRIDE] + ["bogus"]:
                for d in (False, True):
                    for ts in (False, True):
                        for b in bases:
                            r = check_authority_transfer(src, clm, basis=b, has_explicit_delegation=d,
                                                         has_task_scope=ts)
                            self.assertEqual(set(r), set(keys))
                            rows.append([src, clm, d, ts, b, {k: r[k] for k in keys}])
        self.assertEqual(len(rows), 2496)
        self.assertEqual(hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
                         "048d55c6b99d138322a04e9797dc17d78c721a935b73547cac2194a9d1e1adf1")

    def test_live_authority_gate_is_not_on_the_compile_path(self):
        # check_authority_transfer is exported by gates/ but no runtime module calls it, so the fix
        # cannot change routing (the 963-prompt corpus diff is the end-to-end check).
        for path in [p for p in REPO.rglob("*.py") if "tests" not in p.parts and ".venv" not in p.parts]:
            text = path.read_text(encoding="utf-8")
            if path.name in ("authority.py", "__init__.py") and path.parent.name == "gates":
                continue
            self.assertNotIn("check_authority_transfer(", text, path)


# --------------------------------------------------------------------------- Oracles
class TestACOracleA(unittest.TestCase):
    """TEST-AC-ORACLE-A (001A, semantic censorship / identity stripping): P immutable to V_Def and
    hash-verified; the override bypasses P; no monitor can strip principal provenance."""

    def test_pinned_policy_and_manifests_cannot_be_rewritten_by_v_def(self):
        for me, role in DEF:
            g, _ = world()
            for name in MANIFEST_NAMES:
                d0 = g.plane.digest()
                self.assertNotEqual(g.apply(Request(me, role, Action.WRITE_MANIFEST, payload=(name, "0" * 64)), 1), "ALLOW")
                self.assertEqual(g.plane.digest(), d0)
                self.assertTrue(verify_manifest(g.plane, name, manifest_bytes(name)))
                self.assertFalse(verify_manifest(g.plane, name, manifest_bytes(name) + b"\n# tampered"))

    def test_override_path_never_consults_v_def_inputs(self):
        # The verifier alone decides; monitor-controlled fields cannot strip or forge provenance.
        g, v = world()
        r = signed(v, preq(Action.OVERRIDE), 1, "ov")
        for mutate in (dict(policy_verdict="DENY"), dict(advisory_score=1.0), dict(actor_role="AGENT"),
                       dict(via=("sup", "ml")), dict(compliance_history=-1e9)):
            g2, v2 = world(PrincipalVerifier(PRINCIPAL, KEYS))
            self.assertEqual(g2.authorize(replace(r, **mutate), 1), "ALLOW", mutate)
        self.assertEqual(g.authorize(replace(r, credential=None), 1), "DENY_PRINCIPAL_NO_CREDENTIAL")

    def test_no_key_material_reachable_and_decisions_factor_through_projection(self):
        g1, _ = world(PrincipalVerifier(PRINCIPAL, KEYS))
        g2, _ = world(PrincipalVerifier(PRINCIPAL, {k: b"other-" + v for k, v in KEYS.items()}))
        blob = repr(g1.plane) + repr({k: v for k, v in vars(g1).items() if not k.startswith("_")})
        for key in KEYS.values():
            self.assertNotIn(key.decode(), blob)
        for a in Action:
            for me, role in DEF:
                r = Request(me, role, a, target="agent")
                self.assertEqual(g1.authorize(r, 1), g2.authorize(r, 1), (a, me))

    @unittest.expectedFailure
    def test_live_mafuba_001a_projection_exists_and_is_hash_pinned(self):
        self.assertIsNotNone(importlib.util.find_spec("tests.reference.sc_mafuba_001.projection"))


class TestACOracleB(unittest.TestCase):
    """TEST-AC-ORACLE-B (001B, protective-cage lockout): a total-infeasibility fault halts untrusted
    workflows while C_override stays operational within delta_t_max; barrier inputs are read-only to V_Def."""

    def test_live_cbf_total_infeasibility_halts_but_override_still_applies(self):
        from tests.reference.sc_mafuba_001.cbf import toy_1d_robust_cbf
        g, v = world()
        caged = toy_1d_robust_cbf(0.5, 0.0, r_max=1e6)          # inflated disturbance set D
        self.assertEqual((caged.status, caged.reason), ("FAIL_CLOSED", "PROVEN_INFEASIBLE"))
        self.assertEqual(resolve_branch(caged.status)[0], "HALT")
        status, ticks = OverrideChannel(_budget(), g, delta_t_max=5).invoke(signed(v, preq(Action.OVERRIDE), 1, "o"), 1)
        self.assertEqual(status, "ALLOW")
        self.assertLessEqual(ticks, 5)

    def test_every_non_allow_status_halts_on_the_live_allowlist(self):
        g, v = world()
        statuses = set()
        for a in Action:
            for actor, role in DEF + (("sup", "PRINCIPAL"), ("ghost", "AGENT"), ("agent", "AGENT")):
                statuses.add(g.authorize(Request(actor, role, a, target="C_override"), 1))
        statuses.add(g.authorize("not a request", 1))
        statuses.add(g.authorize(Request("sup", "SUPERVISOR", "HALT"), 1))
        v.available = False
        statuses.add(g.authorize(preq(Action.OVERRIDE), 1))
        self.assertIn("FAIL_CLOSED", statuses)
        for s in statuses:
            self.assertEqual(resolve_branch(s)[0], "CONTINUE" if s == "ALLOW" else "HALT", s)

    def test_disturbance_manifest_is_read_only_to_v_def(self):
        for me, role in DEF:
            g, _ = world()
            self.assertNotEqual(g.apply(Request(me, role, Action.WRITE_MANIFEST,
                                                payload=("disturbance.yaml", "f" * 64)), 1), "ALLOW")
            self.assertTrue(verify_manifest(g.plane, "disturbance.yaml", manifest_bytes("disturbance.yaml")))

    @unittest.expectedFailure
    def test_live_disturbance_manifest_is_principal_signed(self):
        self.assertTrue(has_principal_signature("disturbance.yaml"))


class TestACOracleC(unittest.TestCase):
    """TEST-AC-ORACLE-C (001C, sink-registry hijack / telemetry framing): forged telemetry cannot quarantine
    legitimate work or execute permanent revocation; sink.yaml is immutable to V_Def."""

    def test_forged_telemetry_cannot_frame_or_revoke(self):
        g, _ = world()
        q = QuarantineController(g)
        d0 = g.plane.digest()
        for me, role in DEF:
            self.assertEqual(q.halt(Request(me, role, Action.HALT, target="agent", source="telemetry"), 1),
                             "DENY_ML_ADVISORY_DISABLED")
            self.assertNotEqual(g.apply(Request(me, role, Action.REVOKE_IDENTITY, payload=("agent",),
                                                source="telemetry"), 1), "ALLOW")
            self.assertNotEqual(g.apply(Request(me, "PRINCIPAL", Action.REVOKE_IDENTITY, payload=("agent",)), 1), "ALLOW")
        self.assertTrue(q.workload_may_run("agent", 1))
        self.assertEqual(g.plane.digest(), d0)

    def test_sink_registry_is_immutable_to_v_def(self):
        g, _ = world()
        for me, role in DEF:
            self.assertNotEqual(g.apply(Request(me, role, Action.WRITE_MANIFEST, payload=("sink.yaml", "e" * 64)), 1),
                                "ALLOW")
        self.assertTrue(verify_manifest(g.plane, "sink.yaml", manifest_bytes("sink.yaml")))

    def test_authorize_never_mutates_the_plane(self):
        g, _ = world()
        before = g.plane
        for a in Action:
            g.authorize(Request("sup", "PRINCIPAL", a, payload=("sup", (Action.SET_POLICY,))), 1)
        self.assertIs(g.plane, before)

    @unittest.expectedFailure
    def test_live_sink_manifest_is_principal_signed(self):
        self.assertTrue(has_principal_signature("sink.yaml"))


class TestACOracleD(unittest.TestCase):
    """TEST-AC-ORACLE-D (001D, supervisor quarantine capture): R_override survives supervisor exhaustion;
    a principal-signed recovery stops the compromised supervisor within delta_t_max. Also the AC-3 budget."""

    def test_looping_supervisor_burns_quarantine_not_override_and_is_removed(self):
        g, v = world()
        b = _budget()
        q = QuarantineController(g, t_q_max=1, budget=b, halt_cost=0.5)
        results = [q.halt(Request("sup", "SUPERVISOR", Action.HALT, target=a), t)
                   for t in range(40) for a in ("agent", "tool", "agent2")]   # a looping supervisor
        self.assertIn("PREEMPTIVE_FAIL_CLOSED", results)
        self.assertEqual(b.free("override"), 2)
        ch = OverrideChannel(b, g, delta_t_max=5)
        status, ticks = ch.invoke(signed(v, preq(Action.REVOKE_IDENTITY, payload=("sup",)), 50, "kill"), 50)
        self.assertEqual(status, "ALLOW")
        self.assertLessEqual(ticks, 5)
        self.assertEqual(g.apply(signed(v, preq(Action.REVOKE_IDENTITY, payload=("sup",)), 50, "kill2"), 50), "ALLOW")
        self.assertEqual(g.authorize(Request("sup", "SUPERVISOR", Action.HALT, target="agent"), 51), "DENY_UNREGISTERED")

    def test_partition_rules(self):
        with self.assertRaises(ValueError):
            PartitionedBudget(5.0, {"execution": 4, "enforcement": 2, "audit": 1, "quarantine": 1, "override": 2})
        with self.assertRaises(ValueError):
            PartitionedBudget(10.0, {"execution": 4, "enforcement": 2, "audit": 1, "quarantine": 1, "override": 0})
        b = _budget()
        for p in ("execution", "enforcement", "audit", "quarantine"):
            b.charge(p, b.free(p))
            self.assertEqual(b.charge(p, 0.5), "PREEMPTIVE_FAIL_CLOSED")
        self.assertEqual(b.charge("override", 0.5), "DENY_OVERRIDE_PARTITION_ISOLATED")
        self.assertEqual(b.charge("override", 1.0, path="override"), "CONTINUE")
        for bad in (float("nan"), float("inf"), -1, True, "1"):
            self.assertEqual(b.charge("execution", bad), "FAIL_CLOSED")

    def test_live_mafuba_supervisor_never_auto_resumes(self):
        from tests.reference.sc_mafuba_001.supervisor import EmergencySupervisor, ResourceBudget, Worker
        sup = EmergencySupervisor(ResourceBudget(10.0, 2.0))
        sup.reserve_trigger_shutdown(Worker("w"), b"evidence")
        self.assertEqual(sup.try_resume(), "QUARANTINE_LOCKED")

    @unittest.expectedFailure
    def test_live_resource_manifest_declares_r_override(self):
        self.assertTrue(declares_r_override("resource.yaml"))

    def test_live_mafuba_budget_has_isolated_override_partition(self):
        from tests.reference.sc_mafuba_001.supervisor import ResourceBudget
        b = ResourceBudget(10.0, 2.0, r_override=1.0)
        self.assertEqual((b.r_override, b.r_override_available), (1.0, 1.0))
        self.assertEqual(b.admit(7.5, "execution"), "PREEMPTIVE_FAIL_CLOSED")   # fit before; eats the partition
        self.assertEqual(b.admit(6.9, "execution"), "CONTINUE")
        self.assertEqual(b.r_override_available, 1.0)

    @unittest.expectedFailure
    def test_live_mafuba_budget_has_audit_and_quarantine_partitions(self):
        from tests.reference.sc_mafuba_001.supervisor import ResourceBudget
        b = ResourceBudget(10.0, 2.0, r_override=1.0)
        for attr in ("r_audit", "r_quarantine"):
            self.assertTrue(hasattr(b, attr), attr)

    def test_live_mafuba_override_reserve_is_unconsumable_by_ordinary_paths(self):
        from tests.reference.sc_mafuba_001.supervisor import EmergencySupervisor, ResourceBudget, Worker
        b = ResourceBudget(10.0, 2.0, r_override=1.5)
        # Ordinary admission and enforcement, greedy, in small and large steps.
        for purpose in ("execution", "enforcement"):
            for step in (0.01, 0.5, 3.0, 6.49, 6.5, 100.0):
                b.admit(step, purpose)
        self.assertLess(b.r_used, 10.0 - 2.0 - 1.5)
        self.assertEqual(b.r_override_available, 1.5)
        # Any purpose other than execution/enforcement is refused, including "override".
        for purpose in ("override", "quarantine", "audit", ""):
            self.assertEqual(b.admit(0.1, purpose), "FAIL_CLOSED")
        # Draws from any path but the override path are refused.
        for path in ("", "execution", "enforcement", "supervisor", "quarantine", "OVERRIDE"):
            self.assertEqual(b.draw_override(0.1, path=path), "DENY_OVERRIDE_PARTITION_ISOLATED")
        for bad in (float("nan"), float("inf"), -1.0, True, "1"):
            self.assertEqual(b.draw_override(bad, path="override"), "FAIL_CLOSED")
        # A direct counter write past everything fires the supervisor; the partition is untouched.
        sup = EmergencySupervisor(b)
        rec = sup.reserve_trigger_shutdown(Worker("w"), b"evidence" * 100)
        b.r_used = 1e9
        self.assertTrue(rec.quarantined)
        self.assertLessEqual(rec.reserve_used, b.r_reserve)
        self.assertEqual(b.r_override_available, 1.5)
        self.assertFalse(b.accepting_work)
        # Only the override path spends it, and never past its capacity.
        self.assertEqual(b.draw_override(1.0, path="override"), "CONTINUE")
        self.assertEqual(b.draw_override(0.6, path="override"), "OVERRIDE_PARTITION_EXHAUSTED")
        self.assertEqual(b.draw_override(0.5, path="override"), "CONTINUE")
        self.assertEqual(b.r_override_available, 0.0)
        # The partition cannot be resized after construction, and bad sizes are refused.
        with self.assertRaises(AttributeError):
            b.r_override = 99.0
        for bad in (-1.0, float("nan"), float("inf"), True, "2"):
            with self.assertRaises(ValueError):
                ResourceBudget(10.0, 2.0, r_override=bad)

    def test_live_mafuba_budget_without_override_partition_is_unchanged(self):
        # Regression: r_override defaults to 0.0 and every admission result, counter and free value matches
        # the three-term formula the rc2 reference used before the change.
        import random as _r
        from tests.reference.sc_mafuba_001.supervisor import ResourceBudget
        rng = _r.Random(601)
        for _ in range(200):
            budget, reserve = rng.choice([10.0, 7.5, 3.0]), rng.choice([0.1, 0.7, 2.0])
            b = ResourceBudget(budget, reserve)
            ctr = {"execution": 0.0, "enforcement": 0.0}
            for _ in range(20):
                amt = rng.choice([0.0, 0.1, 0.25, 0.5, 1.0, 2.0, budget - reserve])
                purpose = rng.choice(["execution", "enforcement"])
                used = ctr["execution"] + ctr["enforcement"]
                res = b.admit(amt, purpose)
                if budget - used <= reserve or used + amt >= budget - reserve:
                    self.assertEqual(res.status, "PREEMPTIVE_FAIL_CLOSED")
                else:
                    self.assertEqual(res, "CONTINUE")
                    ctr[purpose] += amt
                used = ctr["execution"] + ctr["enforcement"]
                self.assertEqual((b.r_used, b.r_free), (used, budget - used))
            self.assertEqual(getattr(b, "r_override", 0.0), 0.0)   # same assertions hold on the pre-change code

    @staticmethod
    def _quarantined(r_override=1.0, r_reserve=2.0, **kw):
        from tests.reference.sc_mafuba_001.supervisor import EmergencySupervisor, ResourceBudget, Worker
        v = PrincipalVerifier(PRINCIPAL, KEYS)
        sup = EmergencySupervisor(ResourceBudget(10.0, r_reserve, r_override=r_override), principal_verifier=v, **kw)
        sup.reserve_trigger_shutdown(Worker("w"), b"evidence")
        return sup, v

    def _locked(self, sup):
        self.assertEqual(sup.try_resume(), "QUARANTINE_LOCKED")
        self.assertTrue(sup.last_shutdown.quarantined)
        self.assertFalse(sup.budget.accepting_work)

    def test_live_mafuba_supervisor_has_principal_recovery_path(self):
        sup, v = self._quarantined()
        self._locked(sup)
        cred = v.issue_for_digest("k1", sup.release_digest("w"), 10, 20, "rel")
        r = sup.principal_release("w", cred, 12)
        self.assertEqual(r.status, "RELEASED")
        self.assertTrue(r.within_bound)
        self.assertLessEqual(r.effective_at - r.requested_at, sup.delta_t_max)
        self.assertEqual(sup.try_resume(), "RELEASED_BY_PRINCIPAL")
        self.assertTrue(sup.budget.accepting_work)
        self.assertFalse(sup.last_shutdown.quarantined)
        self.assertEqual(sup.budget.r_override_available, 0.5)   # paid from the override partition

    def test_live_mafuba_release_rejects_forged_misbound_or_unpaid_requests(self):
        other = PrincipalVerifier("someone-else", {"k1": b"attacker-key"})

        class Broken:
            def verify_digest(self, *a):
                raise RuntimeError("hsm offline")

        def attempt(build, why, now=12, **qkw):
            sup, v = self._quarantined(**qkw)
            cred, verifier = build(sup, v)
            if verifier is not None:
                sup.principal_verifier = verifier
            r = sup.principal_release("w", cred, now)
            self.assertEqual(r.status, why)
            self._locked(sup)
            return sup

        d = lambda sup: sup.release_digest("w")  # noqa: E731
        attempt(lambda s, v: (None, None), "NO_CREDENTIAL")
        attempt(lambda s, v: (v.issue_for_digest("k1", d(s), 10, 20, "a"), object()), "NO_VERIFIER")
        attempt(lambda s, v: (v.issue_for_digest("k1", d(s), 10, 20, "b"), Broken()), "VERIFIER_ERROR")
        attempt(lambda s, v: (v.issue_for_digest("k1", d(s), 10, 20, "c"), None), "NO_TIME", now=None)
        attempt(lambda s, v: (other.issue_for_digest("k1", d(s), 10, 20, "d"), None), "WRONG_PRINCIPAL")
        # The supervisor (or anyone without the key) forging the principal's id: bad MAC.
        attempt(lambda s, v: (other.issue_for_digest("k1", d(s), 10, 20, "e", principal_id=PRINCIPAL), None),
                "BAD_MAC")
        attempt(lambda s, v: (v.issue_for_digest("k1", s.release_digest("other-worker"), 10, 20, "f"), None),
                "DIGEST_MISMATCH")
        attempt(lambda s, v: (v.issue_for_digest("k1", d(s), 10, 20, "g"), None), "EXPIRED", now=25)
        # No override partition to pay for the release: fail closed.
        attempt(lambda s, v: (v.issue_for_digest("k1", d(s), 10, 20, "h"), None), "OVERRIDE_PARTITION_EXHAUSTED",
                r_override=0.0)
        # Revoked key and verifier down.
        def revoked(s, v):
            v.revoke_key("k2")
            return v.issue_for_digest("k2", d(s), 10, 20, "i"), None
        attempt(revoked, "REVOKED_KEY")
        def down(s, v):
            v.available = False
            return v.issue_for_digest("k1", d(s), 10, 20, "j"), None
        attempt(down, "UNAVAILABLE")
        # Nothing to release.
        from tests.reference.sc_mafuba_001.supervisor import EmergencySupervisor, ResourceBudget
        fresh = EmergencySupervisor(ResourceBudget(10.0, 2.0, r_override=1.0),
                                    principal_verifier=PrincipalVerifier(PRINCIPAL, KEYS))
        self.assertEqual(fresh.principal_release("w", None, 1).status, "NOT_QUARANTINED")

    def test_live_mafuba_release_cannot_be_replayed_or_carried_to_a_later_quarantine(self):
        from tests.reference.sc_mafuba_001.supervisor import Worker
        sup, v = self._quarantined(r_override=2.0)
        cred = v.issue_for_digest("k1", sup.release_digest("w"), 10, 30, "once")
        self.assertEqual(sup.principal_release("w", cred, 12).status, "RELEASED")
        # Budget is still at the reserve edge: the next accounting event quarantines again (defence in depth).
        sup.reserve_trigger_shutdown(Worker("w"), b"again")
        self._locked(sup)
        self.assertEqual(sup.quarantine_epoch, 2)
        self.assertEqual(sup.principal_release("w", cred, 13).status, "DIGEST_MISMATCH")   # old epoch
        old_epoch_fresh_nonce = v.issue_for_digest("k1", cred.request_digest, 10, 30, "new-nonce")
        self.assertEqual(sup.principal_release("w", old_epoch_fresh_nonce, 13).status, "DIGEST_MISMATCH")
        self._locked(sup)
        ok = v.issue_for_digest("k1", sup.release_digest("w"), 10, 30, "second")
        self.assertEqual(sup.principal_release("w", ok, 14).status, "RELEASED")
        self.assertEqual(sup.principal_release("w", ok, 15).status, "NOT_QUARANTINED")

    def test_live_mafuba_release_lands_within_bound_even_after_reserve_exhaustion(self):
        # rc1 ORACLE-D: R_override is isolated from supervisor exhaustion. A shutdown that could not
        # even afford its fixed cost (RESERVE_INSUFFICIENT) is still releasable within delta_t_max.
        from tests.reference.sc_mafuba_001.supervisor import Worker
        for ticks, bound in ((1, 1), (4, 5), (5, 5), (3, 10)):
            sup, v = self._quarantined(r_override=2.0, r_reserve=0.1, delta_t_max=bound, release_path_ticks=ticks)
            for i, now in enumerate((0, 7, 10_000)):
                if i:
                    sup.reserve_trigger_shutdown(Worker("w"), b"again")   # quarantined again, reserve still empty
                self.assertEqual(sup.last_shutdown.status, "RESERVE_INSUFFICIENT")
                self._locked(sup)
                cred = v.issue_for_digest("k1", sup.release_digest("w"), now, now + 2, f"t{ticks}-{now}")
                r = sup.principal_release("w", cred, now)
                self.assertEqual(r.status, "RELEASED", (ticks, bound, now))
                self.assertLessEqual(r.effective_at - now, bound)
                self.assertTrue(r.within_bound)
        from tests.reference.sc_mafuba_001.supervisor import EmergencySupervisor, ResourceBudget
        with self.assertRaises(ValueError):
            EmergencySupervisor(ResourceBudget(10.0, 2.0), delta_t_max=3, release_path_ticks=4)


# --------------------------------------------------------------------------- Registry and provenance
ID_TO_CLASS = {
    "TEST-AC-01": TestAC01SelfEscalationRejection, "TEST-AC-02": TestAC02AuthorityPlaneMutationProbe,
    "TEST-AC-03": TestAC03TrustAccumulationInvariance, "TEST-AC-04": TestAC04AdvisoryLaunderingBlock,
    "TEST-AC-05": TestAC05ByzantineQuarantineOverride, "TEST-AC-06": TestAC06PrincipalIdentityIntegrity,
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
        self.assertEqual((r["id"], r["parent_id"], r["classification"]), ("SCC-001-AC", "SCC-001", "PROPOSED_GOLD"))
        self.assertIs(r["gold_awarded"], False)
        self.assertEqual(r["verification_axes"], {"mathematical_validity": "DRAFT_SPECIFIED_UNPROVEN",
                                                  "implementation_correctness": "REFERENCE_ONLY",
                                                  "empirical_validation": "UNVALIDATED"})
        self.assertIs(r["runtime_loaded"], False)
        self.assertIs(r["compiled_manifest"], False)
        self.assertEqual(r["ml_admission_gate"], {"ML_ANOMALY_SCORING_ENABLED": False, "AUTO_QUARANTINE_ENABLED": False})

    def test_acceptance_ids_map_to_test_classes(self):
        self.assertEqual(sorted(self.row["acceptance_test_ids"]), sorted(ID_TO_CLASS))

    def test_xfails_in_registry_match_expected_failures(self):
        found = {}
        for tid, cls in ID_TO_CLASS.items():
            for name in dir(cls):
                if name.startswith("test_") and getattr(getattr(cls, name), "__unittest_expecting_failure__", False):
                    found[name] = tid
        self.assertEqual(found, {k: v[0] for k, v in LIVE_GAPS.items()})
        reg = {x["test"]: (x["acceptance_test_id"], x["reason"]) for x in self.row["live_interface_gaps"]}
        self.assertEqual(reg, {k: tuple(v) for k, v in LIVE_GAPS.items()})

    def test_resolved_gaps_run_as_ordinary_passing_tests(self):
        self.assertFalse(set(RESOLVED_GAPS) & set(LIVE_GAPS))
        for name, (tid, _, _) in RESOLVED_GAPS.items():
            fn = getattr(ID_TO_CLASS[tid], name)
            self.assertFalse(getattr(fn, "__unittest_expecting_failure__", False), name)
        reg = {x["test"]: (x["acceptance_test_id"], x["before"], x["after"])
               for x in self.row["resolved_interface_gaps"]}
        self.assertEqual(reg, {k: tuple(v) for k, v in RESOLVED_GAPS.items()})
        self.assertTrue(all(x["status"] == "RESOLVED_IN_LIVE_CODE" for x in self.row["resolved_interface_gaps"]))

    def test_original_spec_is_verbatim_and_hash_pinned(self):
        prov = self.row["provenance"]
        self.assertEqual(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(prov["spec_sha256"], ORIGINAL_SHA256)
        self.assertEqual(prov["spec_path"], "docs/evidence/source-2026-11-26c/SCC-001-AC_original.md")
        self.assertNotIn("spec_sha256_status", prov)
        self.assertEqual(prov["refined_spec_sha256"], hashlib.sha256(SPEC.read_bytes()).hexdigest())
        self.assertEqual(prov["redactions"], [])

    def test_rc1_formal_conditions_kept_verbatim(self):
        rc1 = self.row["source_formal_conditions_rc1"]
        self.assertEqual(len(rc1), 5)
        self.assertTrue(rc1[0].startswith("AC-1: Delta G_m^self = 0"))

    def test_section5_contract_copied_verbatim(self):
        orig = ORIGINAL.read_text(encoding="utf-8")
        block = re.search(r"```python\n(.*?)```", orig, re.S).group(1)
        ours = (REF / "spec_contract.py").read_text(encoding="utf-8")
        self.assertIn(block.strip(), ours)

    def test_manifest_pins_match_the_real_files(self):
        self.assertEqual(self.row["manifest_pins"], pinned_manifests())

    def test_reproducibility_manifest_matches_current_files(self):
        man = json.loads((REPO / self.row["provenance"]["reproducibility_manifest"]).read_text(encoding="utf-8"))
        for path, sha in man["file_sha256"].items():
            self.assertEqual(hashlib.sha256((REPO / path).read_bytes()).hexdigest(), sha, path)
        self.assertEqual(self.row["provenance"]["test_run_hashes"], [man["test_run_sha256"]])

    def test_provisional_defaults_are_in_pending_deliberation(self):
        doc = (REPO / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        for d in self.row["provisional_defaults"]:
            self.assertEqual(d["status"], "PROVISIONAL_DEFAULT")
            self.assertIs(d["pending_deliberation"], True)
            self.assertIn(f"### {d['id']}", doc)

    def test_v_def_roles_match_rc1(self):
        self.assertEqual(V_DEF_ROLES, {"POLICY_ENGINE", "SUPERVISOR", "ML_ADVISORY"})
        self.assertEqual({r.value for r in Role}, {r.value for r in sc.AuthorityRole})

    def test_reference_is_not_imported_by_runtime(self):
        for path in list(REPO.glob("*.py")) + list((REPO / "core").glob("*.py")) + list((REPO / "expansion").rglob("*.py")):
            self.assertNotIn("scc_001_ac", path.read_text(encoding="utf-8"), path)

    def test_reference_is_standard_library_only(self):
        allowed = {"__future__", "dataclasses", "enum", "typing", "hashlib", "hmac", "math", "json", "pathlib", "tests"}
        for path in REF.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ImportFrom):
                    self.assertIn(node.module.split(".")[0], allowed, path)
                elif isinstance(node, ast.Import):
                    for n in node.names:
                        self.assertIn(n.name.split(".")[0], allowed, path)


if __name__ == "__main__":
    unittest.main()
