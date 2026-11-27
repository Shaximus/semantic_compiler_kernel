"""SC-TOL-001 rc6: Shax's two decisions (t610u), adversarial boundary tests.

D1 ACCEPT: a failing child taints the parent's CURRENT compilation only.
  PASS child -> no taint; QUALIFIED child -> parent QUALIFIED; BLOCKED child -> parent
  BLOCKED for that compilation. ChildFailure => ParentCompilationTainted, never
  ParentIdentityDestroyed. Siblings unaffected, the child's failure provenance is carried
  upward and cannot be erased, and the taint grants no governance authority.
D2 RECLASSIFY: LIVING_OBSERVED / SELF_MAINTENANCE_UNVERIFIED / AUTOPOIESIS_EMPIRICAL /
  INERT_TAXONOMY. The first two never satisfy T2; a living system is never labelled inert.
Principle: structural validity, biological status and governance authority are separate
dimensions, never one verdict.
"""

from __future__ import annotations

import dataclasses
import json
import unittest

from tests.reference.sc_tol_001 import compiler as K
from tests.reference.sc_tol_001 import rc5 as R

C = K.StructuralCompiler()
K4_NODES = {"a", "b", "c", "d"}
K4_EDGES = {("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"), ("a", "c"), ("b", "d")}


def _st(M=K, **kw):
    base = dict(
        system_id="s",
        substrate=M.SubstrateSpec("dna", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
        topology=M.TopologyClass.DISTRIBUTED,
        epistemic_tier=M.EpistemicTier.EMPIRICAL_SCI,
        nodes=set(K4_NODES), edges=set(K4_EDGES),
    )
    base.update(kw)
    return M.SystemState(**base)


def good_child(cid="good"):
    return _st(system_id=cid)


def qualified_child(cid="qual"):
    return _st(system_id=cid, substrate=K.SubstrateSpec("x", has_empirical_autopoiesis=True, memory_mechanism_status="unverified"))


def blocked_child(cid="bad"):
    return _st(system_id=cid, source_id="unregistered_source", require_registered_provenance=True)


def parent(gen, children, **kw):
    return _st(system_id="parent", meta_spec=K.MetaArchitectureSpec(gen, [(c, set(e)) for c, e in children]), **kw)


class ChildTaintPropagationTests(unittest.TestCase):
    def test_child_verdicts_are_as_intended(self) -> None:
        self.assertEqual(C.compile(good_child()).overall_verdict, K.GateVerdict.PASS)
        self.assertEqual(C.compile(qualified_child()).overall_verdict, K.GateVerdict.QUALIFIED)
        self.assertEqual(C.compile(blocked_child()).overall_verdict, K.GateVerdict.BLOCKED)

    def test_pass_child_no_taint(self) -> None:
        r = C.compile(parent(K.MetaGenerator("g"), [(good_child(), ())]))
        self.assertEqual(r.taint_provenance, ())
        self.assertIn(K.GateVerdict.PASS, r.verdicts_for("E6"))
        self.assertEqual(r.overall_verdict, K.GateVerdict.PASS)

    def test_qualified_child_makes_parent_qualified_not_blocked(self) -> None:
        r = C.compile(parent(K.MetaGenerator("g"), [(qualified_child(), ())]))
        self.assertEqual(r.verdicts_for("E6"), [K.GateVerdict.QUALIFIED])
        self.assertEqual(r.overall_verdict, K.GateVerdict.QUALIFIED)
        self.assertTrue(r.is_trustworthy)

    def test_blocked_child_blocks_parent_compilation(self) -> None:
        r = C.compile(parent(K.MetaGenerator("g"), [(blocked_child(), ())]))
        self.assertIn(K.GateVerdict.BLOCKED, r.verdicts_for("E6"))
        self.assertNotIn(K.GateVerdict.PASS, r.verdicts_for("E6"))
        self.assertFalse(r.is_trustworthy)
        (t,) = r.taint_provenance
        self.assertEqual(t.preserved_observation["scope"], "CURRENT_COMPILATION")

    def test_sibling_unaffected(self) -> None:
        alone = C.compile(parent(K.MetaGenerator("g"), [(good_child("sib"), ())]))
        mixed = C.compile(parent(K.MetaGenerator("g"), [(blocked_child(), ()), (good_child("sib"), ())]))
        sib_alone = alone.child_results[0]
        sib_mixed = mixed.child_results[1]
        self.assertTrue(sib_mixed.is_trustworthy)
        self.assertEqual(sib_mixed.to_json(), sib_alone.to_json())
        self.assertEqual([t.preserved_observation["child_id"] for t in mixed.taint_provenance], ["bad"])

    def test_generator_identity_intact_and_reusable(self) -> None:
        gen = K.MetaGenerator("g")
        before = (gen.generator_id, gen.immutable_gates, gen.tamper_events)
        tainted = C.compile(parent(gen, [(blocked_child(), ())]))
        self.assertFalse(tainted.is_trustworthy)
        self.assertEqual((gen.generator_id, gen.immutable_gates, gen.tamper_events), before)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            gen.tamper_events = ("tainted",)  # type: ignore[misc]
        # No permanent DoS: the same generator compiles clean in the next compilation.
        clean = C.compile(parent(gen, [(good_child(), ())]))
        self.assertEqual(clean.taint_provenance, ())
        self.assertTrue(clean.is_trustworthy)
        self.assertEqual(clean.overall_verdict, K.GateVerdict.PASS)
        for t in tainted.taint_provenance:
            self.assertIs(t.preserved_observation["generator_identity_affected"], False)

    def test_compilation_is_stateless_across_runs(self) -> None:
        gen = K.MetaGenerator("g")
        s = parent(gen, [(blocked_child(), ()), (good_child(), ())])
        self.assertEqual(C.compile(s).to_json(), C.compile(s).to_json())

    def test_child_failure_provenance_preserved_and_not_erasable(self) -> None:
        r = C.compile(parent(K.MetaGenerator("g"), [(blocked_child(), ())]))
        child = r.child_results[0]
        (t,) = r.taint_provenance
        copied = t.preserved_observation["child_failure_records"]
        self.assertEqual([c["preserved_observation"].get("code") for c in copied],
                         [h.preserved_observation.get("code") for h in child.hard_blocks])
        self.assertEqual([c["message"] for c in copied], [h.message for h in child.hard_blocks])
        with self.assertRaises(TypeError):
            t.preserved_observation["child_failure_records"] = []
        with self.assertRaises(TypeError):
            copied[0]["message"] = "nothing happened"
        with self.assertRaises(TypeError):
            copied.clear()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            r.records = ()  # type: ignore[misc]
        # The only post-hoc API appends; the taint survives any appended "override".
        over = r.with_appended_records([K.GateRecord("E6", K.GateVerdict.PASS, "parent says child is fine")])
        self.assertEqual(over.taint_provenance, r.taint_provenance)
        self.assertFalse(over.is_trustworthy)

    def test_exemptions_cannot_launder_the_taint(self) -> None:
        for ex in ({"T7"}, {"T2", "T7", "E1"}, {"T0"}):
            with self.subTest(exemptions=ex):
                r = C.compile(parent(K.MetaGenerator("g"), [(qualified_child(), ex)]))
                self.assertTrue(r.taint_provenance)
                self.assertNotIn(K.GateVerdict.PASS, r.verdicts_for("E6"))

    def test_taint_grants_no_authority(self) -> None:
        reg = {"council": K.AuthorityRecord("council", True, frozenset({"routing"}), frozenset({"a"}),
                                            frozenset({K.GovernanceMode.STEWARDED}), (0, 1000))}
        common = dict(
            authority_registry=reg,
            governance=[K.GovernanceGrant("a", "routing", K.GovernanceMode.STEWARDED, (0, 10), "council")],
            escalations=[K.EscalationRequest("g", "bad", K.GovernanceMode.SOVEREIGN, "quarantine", "g")],
        )
        clean = C.compile(parent(K.MetaGenerator("g"), [(good_child("bad"), ())], **common))
        tainted = C.compile(parent(K.MetaGenerator("g"), [(blocked_child("bad"), ())], **common))
        for attr in ("active_grants", "expired_grants", "accepted_escalations", "rejected_escalations"):
            self.assertEqual(getattr(tainted, attr), getattr(clean, attr), attr)
        self.assertEqual(tainted.accepted_escalations, ())
        self.assertEqual(tainted.dimension_verdicts()["governance"], clean.dimension_verdicts()["governance"])
        self.assertEqual(tainted.dimension_verdicts()["biological"], clean.dimension_verdicts()["biological"])
        for t in tainted.taint_provenance:
            self.assertIs(t.preserved_observation["authority_granted"], False)
            self.assertEqual(t.gate, "E6")
        # The parent's own escalation (generator quarantining its child) stays rejected.
        self.assertEqual(len(tainted.rejected_escalations), 1)
        self.assertIn("self_authorized_escalation", tainted.codes_for("T8"))

    def test_nested_provenance_reaches_grandparent(self) -> None:
        mid = _st(system_id="mid", meta_spec=K.MetaArchitectureSpec(K.MetaGenerator("g2"), [(blocked_child("leaf"), set())]))
        top = C.compile(parent(K.MetaGenerator("g1"), [(mid, ())]))
        self.assertFalse(top.is_trustworthy)
        blob = json.dumps(top.to_dict()["records"], default=str)
        self.assertIn('"leaf"', blob)
        self.assertIn('"unregistered_source"', blob)  # the leaf's original T0 code
        (t,) = top.taint_provenance
        inner = t.preserved_observation["child_failure_records"]
        self.assertTrue(any(c["preserved_observation"].get("code") == "child_failure_taint" for c in inner))


class LivingClassificationTests(unittest.TestCase):
    @staticmethod
    def _t2(M=K, tier=None, **sub):
        tier = tier or M.EpistemicTier.EMPIRICAL_SCI
        r = M.StructuralCompiler().compile(_st(M, epistemic_tier=tier, substrate=M.SubstrateSpec("cells", **sub)))
        return r, [v.name for v in r.verdicts_for("T2")]

    def test_living_observed_does_not_pass_t2(self) -> None:
        r, t2 = self._t2(empirical_life_observed=True)
        self.assertEqual(t2, ["LIVING_OBSERVED"])
        self.assertFalse(r.t2_satisfied)
        self.assertIn(K.GateVerdict.LIVING_OBSERVED, [u.verdict for u in r.uncertainties])
        self.assertEqual(r.soft_blocks, ())

    def test_self_maintenance_unverified_does_not_pass_t2(self) -> None:
        r, t2 = self._t2(empirical_life_observed=True, has_represented_autopoiesis=True)
        self.assertEqual(t2, ["SELF_MAINTENANCE_UNVERIFIED"])
        self.assertFalse(r.t2_satisfied)

    def test_demonstrated_self_maintenance_is_autopoiesis(self) -> None:
        for extra in ({}, {"empirical_life_observed": True}):
            with self.subTest(extra=extra):
                r, t2 = self._t2(has_empirical_autopoiesis=True, **extra)
                self.assertEqual(t2, ["AUTOPOIESIS_EMPIRICAL"])
                self.assertTrue(r.t2_satisfied)

    def test_static_chart_still_inert(self) -> None:
        for extra in ({}, {"has_represented_autopoiesis": True}):
            with self.subTest(extra=extra):
                r, t2 = self._t2(**extra)
                self.assertEqual(t2, ["INERT_TAXONOMY"])
                self.assertFalse(r.t2_satisfied)

    def test_living_system_never_inert(self) -> None:
        for rep in (False, True):
            for mem in ("verified", "unverified", "impossible"):
                with self.subTest(represented=rep, memory=mem):
                    _r, t2 = self._t2(empirical_life_observed=True, has_represented_autopoiesis=rep, memory_mechanism_status=mem)
                    self.assertNotIn("INERT_TAXONOMY", t2)

    def test_rc5_labelled_living_represented_case_inert(self) -> None:
        # rc5 has no life-evidence field: the represented-only empirical case was INERT there.
        _r, t2 = self._t2(R, has_represented_autopoiesis=True)
        self.assertEqual(t2, ["INERT_TAXONOMY"])

    def test_myth_tier_unaffected(self) -> None:
        for sub in ({}, {"has_represented_autopoiesis": True}, {"has_empirical_autopoiesis": True},
                    {"has_empirical_autopoiesis": True, "has_represented_autopoiesis": True}):
            with self.subTest(sub=sub):
                _r5, t5 = self._t2(R, R.EpistemicTier.CORPUS_MYTH, **sub)
                _rk, tk = self._t2(K, K.EpistemicTier.CORPUS_MYTH, **sub)
                self.assertEqual(tk, t5)

    def test_non_empirical_tiers_cannot_claim_observed_life(self) -> None:
        for tier in (K.EpistemicTier.CORPUS_MYTH, K.EpistemicTier.SPECULATIVE_EXO):
            with self.subTest(tier=tier.name):
                r, t2 = self._t2(K, tier, empirical_life_observed=True, has_represented_autopoiesis=True)
                self.assertIn("BLOCKED", t2)
                self.assertNotIn("LIVING_OBSERVED", t2)
                self.assertIn("non_empirical_life_claim_blocked", r.codes_for("T2"))

    def test_speculative_tier_unchanged_without_life_flag(self) -> None:
        _r5, t5 = self._t2(R, R.EpistemicTier.SPECULATIVE_EXO, has_represented_autopoiesis=True)
        _rk, tk = self._t2(K, K.EpistemicTier.SPECULATIVE_EXO, has_represented_autopoiesis=True)
        self.assertEqual(tk, t5)

    def test_classification_does_not_touch_other_dimensions(self) -> None:
        inert, _ = self._t2()
        living, _ = self._t2(empirical_life_observed=True)
        self.assertEqual(living.dimension_verdicts()["structural"], inert.dimension_verdicts()["structural"])
        self.assertEqual(living.dimension_verdicts()["governance"], inert.dimension_verdicts()["governance"])
        self.assertNotEqual(living.dimension_verdicts()["biological"], inert.dimension_verdicts()["biological"])
        json.loads(living.to_json())


class PrincipleTests(unittest.TestCase):
    def test_three_dimensions_are_disjoint(self) -> None:
        dims = list(K.DIMENSION_GATES.values())
        for i, a in enumerate(dims):
            for b in dims[i + 1:]:
                self.assertFalse(a & b)
        self.assertEqual(set(K.DIMENSION_GATES), {"structural", "biological", "governance"})

    def test_t2_satisfying_set_excludes_observations(self) -> None:
        self.assertNotIn(K.GateVerdict.LIVING_OBSERVED, K.T2_SATISFYING_VERDICTS)
        self.assertNotIn(K.GateVerdict.SELF_MAINTENANCE_UNVERIFIED, K.T2_SATISFYING_VERDICTS)

    def test_rc5_untouched(self) -> None:
        self.assertFalse(hasattr(R.GateVerdict, "LIVING_OBSERVED"))
        self.assertEqual(R.SCHEMA_VERSION, "SC-TOL-001/2.1-rc5")


if __name__ == "__main__":
    unittest.main()
