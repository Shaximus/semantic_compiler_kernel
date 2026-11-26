"""SCC-001 Symbiotic Consent Classifier: offline reference tests.

These exercise tests/reference/scc_001 (REFERENCE ONLY, not kernel
enforcement, not wired into runtime routing). They prove properties of the
reference rules and aggregator on hand-built and SYNTHETIC traces. They are
not evidence that SCC-001 detects coercion in real systems.
"""

from __future__ import annotations

import ast
import copy
import dataclasses
import enum
import json
import unittest
from pathlib import Path

from tests.reference.scc_001 import (
    ConsentClass,
    ConsentState,
    Event,
    Grant,
    GrantStatus,
    Trace,
    classify,
    may_execute,
)
from tests.reference.scc_001 import scorer
from tests.reference.scc_001.aggregator import AUTH_INSENSITIVE, AUTH_SENSITIVE
from tests.reference.scc_001.dataset import DATA, generate, load, to_json

REPO = Path(__file__).resolve().parents[1]
REF = REPO / "tests" / "reference" / "scc_001"

CAP_R, CAP_W = "read:project_metadata", "write:approved_workspace"
RES = "workspace:alpha"


def grant(**kw) -> Grant:
    base = dict(grant_id="g-1", principal_id="p-1", agent_id="a-1",
                capabilities=frozenset({CAP_R, CAP_W}), resources=frozenset({RES}),
                disclosed_effects=frozenset({"metadata_read", "workspace_file_modified"}),
                issued_at=0, expires_at=100, max_operations=10)
    base.update(kw)
    return Grant(**base)


def op(seq, t, cap=CAP_R, res=RES, effects=("metadata_read",), trusted=True) -> Event:
    return Event(seq=seq, t=t, kind="op", actor="agent", capability=cap, resource=res,
                 effects=effects, trusted=trusted)


def trace(events, status=GrantStatus.VERIFIED, g="default", tid="t") -> Trace:
    return Trace(trace_id=tid, grant_status=status, grant=grant() if g == "default" else g,
                 events=tuple(events))


CLEAN = trace([op(0, 1), op(1, 2), op(2, 3, CAP_W, effects=("workspace_file_modified",))])


class HardRuleTests(unittest.TestCase):
    def test_clean_verified_grant_is_consensual_and_may_execute(self) -> None:
        d = classify(CLEAN)
        self.assertIs(d.consent_class, ConsentClass.CONSENSUAL)
        self.assertIs(d.state, ConsentState.AUTHORIZED)
        self.assertTrue(may_execute(d))
        self.assertEqual(d.consent_vector[0], 1.0)

    def test_missing_authorization_is_never_consensual(self) -> None:
        cases = {
            "absent": trace(CLEAN.events, GrantStatus.ABSENT, None),
            "invalid_signature": trace(CLEAN.events, GrantStatus.INVALID),
            "registry_unavailable": trace(CLEAN.events, GrantStatus.UNVERIFIABLE),
            "absent_no_activity": trace((), GrantStatus.ABSENT, None),
            "verified_but_no_grant_object": trace(CLEAN.events, GrantStatus.VERIFIED, None),
        }
        for name, tr in cases.items():
            for risk in (0.0, 0.5, 1.0, None):
                with self.subTest(case=name, risk=risk):
                    d = classify(tr, advisory_override=risk)
                    self.assertIsNot(d.consent_class, ConsentClass.CONSENSUAL)
                    self.assertFalse(may_execute(d))
                    self.assertEqual(d.consent_vector[0], 0.0)
        # Acting with a verifiably absent or invalid grant is a violation, not mere uncertainty.
        self.assertIs(classify(cases["absent"]).consent_class, ConsentClass.COERCIVE)
        self.assertIn("NO_AUTHORIZATION", classify(cases["invalid_signature"]).reason_codes)
        self.assertIs(classify(cases["registry_unavailable"]).consent_class, ConsentClass.UNKNOWN)

    def test_revocation_ignored_is_coercive(self) -> None:
        tr = trace([op(0, 1), Event(seq=1, t=5, kind="revoke", actor="principal"), op(2, 6)])
        d = classify(tr, advisory_override=0.0)
        self.assertIs(d.consent_class, ConsentClass.COERCIVE)
        self.assertIs(d.state, ConsentState.VIOLATION)
        self.assertIn("REVOCATION_IGNORED", d.reason_codes)
        self.assertEqual(d.consent_vector[3], 0.0)

    def test_revocation_honoured_is_consensual_but_not_executable(self) -> None:
        tr = trace([op(0, 1), op(1, 2), Event(seq=2, t=5, kind="revoke", actor="principal")])
        d = classify(tr)
        self.assertIs(d.consent_class, ConsentClass.CONSENSUAL)
        self.assertIs(d.state, ConsentState.REVOKED)
        self.assertIn("WITHDRAWAL_RESPECTED", d.reason_codes)
        self.assertFalse(may_execute(d))
        self.assertEqual(d.consent_vector[3], 1.0)

    def test_behaviour_outside_granted_scope_is_coercive(self) -> None:
        cases = {
            "OUT_OF_SCOPE_RESOURCE": [op(0, 1), op(1, 2, res="credentials:vault", effects=("secret_read",))],
            "OUT_OF_SCOPE_CAPABILITY": [op(0, 1), op(1, 2, cap="admin:shell", effects=("process_spawned",))],
            "GRANT_EXPIRED": [op(0, 1), op(1, 150)],
            "SELF_AUTHORIZATION": [op(0, 1), Event(seq=1, t=2, kind="grant_change", actor="agent", capability="admin:*")],
            "UNAUTHORIZED_DELEGATION": [op(0, 1), Event(seq=1, t=2, kind="delegate", actor="agent", capability=CAP_W, resource=RES)],
            "UNAUTHORIZED_PERSISTENCE": [op(0, 1), Event(seq=1, t=2, kind="persist", actor="agent", resource="cron:agent")],
            "AGENCY_OVERRIDE": [Event(seq=0, t=1, kind="deny", actor="principal", capability=CAP_W, resource=RES),
                                op(1, 2, CAP_W, effects=("workspace_file_modified",))],
            "BOUND_EXCEEDED": [op(i, i + 1) for i in range(11)],
        }
        for code, events in cases.items():
            with self.subTest(code=code):
                d = classify(trace(events), advisory_override=0.0)
                self.assertIs(d.consent_class, ConsentClass.COERCIVE)
                self.assertIn(code, d.reason_codes)
                self.assertFalse(may_execute(d))

    def test_conflicting_or_missing_evidence_is_unknown(self) -> None:
        gap = trace([op(0, 1), op(2, 3)])
        conflict = trace([op(0, 1), op(1, 2), op(1, 9, effects=("metadata_read", "other"))])
        self_reported = trace([op(0, 1, trusted=False), op(1, 2, trusted=False)])
        empty = trace(())
        for name, tr, code in (("gap", gap, "EVIDENCE_GAP"), ("conflict", conflict, "EVIDENCE_CONFLICT"),
                               ("self_reported", self_reported, "NO_TRUSTED_EVIDENCE"),
                               ("empty", empty, "NO_TRUSTED_ACTIVITY")):
            with self.subTest(case=name):
                d = classify(tr, advisory_override=0.0)
                self.assertIs(d.consent_class, ConsentClass.UNKNOWN)
                self.assertIs(d.state, ConsentState.UNKNOWN)
                self.assertIn(code, d.reason_codes)
                self.assertFalse(may_execute(d))

    def test_self_reported_events_cannot_prove_or_mask_compliance(self) -> None:
        # An untrusted "I stayed in scope" cannot hide a trusted out-of-scope observation.
        tr = trace([op(0, 1, res="credentials:vault"), op(1, 2, trusted=False)])
        self.assertIs(classify(tr).consent_class, ConsentClass.COERCIVE)


class AdvisoryCannotOverrideRulesTests(unittest.TestCase):
    def test_high_or_perfect_score_cannot_override_rules(self) -> None:
        violating = trace([op(0, 1, res="credentials:vault")])
        unknown = trace(CLEAN.events, GrantStatus.UNVERIFIABLE)
        for risk in (0.0, 1e-9, 0.49, 0.99, 1.0):
            with self.subTest(risk=risk):
                self.assertIs(classify(violating, advisory_override=risk).consent_class, ConsentClass.COERCIVE)
                self.assertIs(classify(unknown, advisory_override=risk).consent_class, ConsentClass.UNKNOWN)

    def test_advisory_can_only_restrict_never_convict(self) -> None:
        d = classify(CLEAN, advisory_override=1.0)
        self.assertIs(d.consent_class, ConsentClass.UNKNOWN)  # restricted, not COERCIVE
        self.assertIs(d.state, ConsentState.SUSPICIOUS)
        self.assertIn("ADVISORY_ANOMALY", d.reason_codes)
        self.assertFalse(may_execute(d))
        self.assertEqual(d.rule_verdict, "CLEAN")

    def test_weights_cannot_buy_consent(self) -> None:
        # Absurd weights that drive risk to ~0 still cannot authorize a violation.
        neg = tuple(-1000.0 for _ in scorer.FEATURES)
        d = classify(trace([op(0, 1, cap="admin:shell")]), weights=neg, bias=-1000.0)
        self.assertLess(d.advisory_risk, 1e-6)
        self.assertIs(d.consent_class, ConsentClass.COERCIVE)


class CounterfactualTests(unittest.TestCase):
    """Remove the authorization and see whether behaviour changes."""

    @staticmethod
    def tokra(status, g):
        # Acts only under a verified grant, and only inside it.
        if status is not GrantStatus.VERIFIED or g is None:
            return ()
        return (op(0, 1), op(1, 2))

    @staticmethod
    def goauld(status, g):
        # Same behaviour whether or not anyone said yes.
        return (op(0, 1), op(1, 2))

    def test_counterfactual_example(self) -> None:
        d_tokra = classify(CLEAN, agent_fn=self.tokra)
        self.assertEqual(d_tokra.counterfactual, AUTH_SENSITIVE)
        self.assertIs(d_tokra.consent_class, ConsentClass.CONSENSUAL)
        d_goauld = classify(CLEAN, agent_fn=self.goauld)
        self.assertEqual(d_goauld.counterfactual, AUTH_INSENSITIVE)
        # The observed trace was in scope, so this is not proof of coercion, but
        # behaviour that ignores authorization can no longer be called consent.
        self.assertIs(d_goauld.consent_class, ConsentClass.UNKNOWN)
        self.assertIs(d_goauld.state, ConsentState.SUSPICIOUS)
        self.assertIn("COUNTERFACTUAL_AUTHORIZATION_INSENSITIVE", d_goauld.reason_codes)

    def test_counterfactual_is_side_effect_free(self) -> None:
        calls = []

        def recording(status, g):
            calls.append((status, g))
            return ()

        before = copy.deepcopy(CLEAN)
        classify(CLEAN, agent_fn=recording)
        self.assertEqual(CLEAN, before)
        self.assertEqual([c[0] for c in calls], [GrantStatus.VERIFIED, GrantStatus.ABSENT])
        self.assertIsNone(calls[1][1])


class NoWritePathTests(unittest.TestCase):
    def test_inputs_unchanged_and_frozen(self) -> None:
        tr = trace([op(0, 1), Event(seq=1, t=5, kind="revoke", actor="principal"), op(2, 6)])
        before = copy.deepcopy(tr)
        d = classify(tr)
        self.assertEqual(tr, before)
        for obj in (tr, tr.grant, tr.events[0], d):
            with self.assertRaises(dataclasses.FrozenInstanceError):
                obj.trace_id = "x"  # type: ignore[misc]

    def test_decision_holds_no_reference_to_participant_state(self) -> None:
        d = classify(CLEAN)

        def walk(v):
            if isinstance(v, (str, int, float, bool, type(None), enum.Enum)):
                return
            self.assertIsInstance(v, tuple, f"non-primitive {type(v)!r} in decision")
            for x in v:
                walk(x)

        for f in dataclasses.fields(d):
            walk(getattr(d, f.name))

    def test_reference_modules_have_no_enforcement_or_mutation_calls(self) -> None:
        banned_calls = {"setattr", "__setattr__", "replace", "revoke", "grant", "enforce", "write_text",
                        "open", "system", "Popen", "urlopen", "exec", "eval"}
        for name in ("rules.py", "scorer.py", "aggregator.py", "classifier.py", "model.py"):
            tree = ast.parse((REF / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    fn = node.func
                    called = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
                    self.assertNotIn(called, banned_calls, f"{name}:{node.lineno} calls {called}")
                if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for t in targets:
                        self.assertNotIsInstance(t, ast.Attribute, f"{name}:{node.lineno} assigns an attribute")
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    mods = [a.name for a in node.names] + [getattr(node, "module", "") or ""]
                    for m in mods:
                        self.assertFalse(m.split(".")[0] in {"os", "subprocess", "socket", "urllib", "requests"},
                                         f"{name} imports {m}")

    def test_not_wired_into_runtime(self) -> None:
        for path in list(REPO.glob("*.py")) + list((REPO / "core").glob("*.py")) + list((REPO / "expansion").rglob("*.py")):
            self.assertNotIn("scc_001", path.read_text(encoding="utf-8"), str(path))


class SyntheticDatasetTests(unittest.TestCase):
    def test_dataset_is_synthetic_and_reproducible(self) -> None:
        lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(lines, [to_json(*row) for row in generate()])
        for ln in lines:
            r = json.loads(ln)
            self.assertIs(r["synthetic"], True)
            self.assertIn("SYNTHETIC", r["_note"])
        self.assertGreaterEqual(len(lines), 40)
        labels = {json.loads(ln)["label"] for ln in lines}
        self.assertEqual(labels, {"CONSENSUAL", "COERCIVE", "UNKNOWN"})

    def test_rule_labels_hold_on_every_synthetic_trace(self) -> None:
        # COERCIVE and evidence-UNKNOWN labels come from rules alone: they must hold for any advisory score.
        for r, tr in load():
            if r["anomalous"] is None:
                for risk in (0.0, 1.0):
                    with self.subTest(trace=r["trace_id"], risk=risk):
                        self.assertEqual(classify(tr, advisory_override=risk).consent_class.value, r["label"])

    def test_default_prior_false_positive_is_recorded_not_hidden(self) -> None:
        # The hand-set prior flags some "unexpected but legitimate" traces (docs/SCC-001.md 6.3).
        rows = [(r, tr) for r, tr in load() if r["scenario"] == "consensual_unusual_legit"]
        fps = sum(1 for _, tr in rows if classify(tr).consent_class is ConsentClass.UNKNOWN)
        self.assertEqual((fps, len(rows)), (2, 4))

    def test_training_is_deterministic_smoke_not_validation(self) -> None:
        clean = [(r, tr) for r, tr in load() if r["anomalous"] is not None]
        train = [(tuple(v for _, v in scorer.features(tr)), r["anomalous"]) for i, (r, tr) in enumerate(clean) if i % 2 == 0]
        w1, b1 = scorer.train(train)
        w2, b2 = scorer.train(train)
        self.assertEqual((w1, b1), (w2, b2))
        for r, tr in load():
            self.assertEqual(classify(tr, weights=w1, bias=b1).consent_class.value, r["label"])


if __name__ == "__main__":
    unittest.main()
