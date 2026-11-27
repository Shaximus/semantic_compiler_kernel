"""SC-TOL-001 rc7: structural result, epistemic result and combined certification (Shax t611u).

Shax's distinction: an unverified substrate (not empirically established), a speculative
architecture (deliberately in the speculative tier) and an invalid architecture (violates a
structural invariant) are not equivalent. rc6's propagation rule is kept: the combined
certification IS rc6's overall_verdict. rc7 reports two more axes beside it, so a speculative
architecture can be structurally valid without being empirically established, and the compiler
never implies that speculative means defective.

Investigation items (t611u), one test class each:
  1. Epistemic qualification propagates independently of structural failure.
  2. Speculative generators can reach structural PASS without empirical certification.
  3. A child can never silently upgrade a parent's qualification (structural, epistemic, combined).
  4. The 963-prompt corpus stays a regression baseline (run as an external gate; see the spec doc,
     section 5b); in-repo, the reference compiler stays outside every packaged module.
Principle: what a structure is, what evidence supports claims about it, and who has authority to
change it stay separate. rc7 adds no authority path.
"""

from __future__ import annotations

import itertools
import json
import unittest
from pathlib import Path

from tests.reference.sc_tol_001 import compiler as K
from tests.reference.sc_tol_001.fixtures import build_fixtures

C = K.StructuralCompiler()
SV, ES, GV = K.StructuralVerdict, K.EpistemicStatus, K.GateVerdict
K4_NODES = {"a", "b", "c", "d"}
K4_EDGES = {("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"), ("a", "c"), ("b", "d")}
REPO_ROOT = Path(__file__).resolve().parents[1]

EMP_OK = dict(has_empirical_autopoiesis=True, memory_mechanism_status="verified")
SPEC_SUB = dict(has_represented_autopoiesis=True, memory_mechanism_status="unverified")
COMBINED_RANK = {GV.BLOCKED: 0, GV.QUALIFIED: 1, GV.PASS: 2}


def _st(sid="s", tier=K.EpistemicTier.EMPIRICAL_SCI, sub=None, **kw):
    if sub is None:
        sub = EMP_OK if tier == K.EpistemicTier.EMPIRICAL_SCI else SPEC_SUB
    base = dict(system_id=sid, substrate=K.SubstrateSpec("m", **sub), topology=K.TopologyClass.DISTRIBUTED,
                epistemic_tier=tier, nodes=set(K4_NODES), edges=set(K4_EDGES))
    base.update(kw)
    return K.SystemState(**base)


# Child kinds: each differs from a clean empirical child on exactly one axis.
def clean(sid="clean"):
    return _st(sid)


def speculative(sid="spec"):
    return _st(sid, K.EpistemicTier.SPECULATIVE_EXO)


def empirical_unverified(sid="emp_unv"):
    return _st(sid, sub=dict(has_empirical_autopoiesis=True, memory_mechanism_status="unverified"))


def structural_fail(sid="sfail"):
    return _st(sid, edges=set(K4_EDGES) | {("a", "a")})  # E1 self_loop_edge: an invariant violation


def structural_qualified(sid="squal"):
    return _st(sid, topology=K.TopologyClass.ARBORESCENT)  # K4 declared as a tree: T1 QUALIFIED


def epistemic_blocked(sid="eblock"):
    return _st(sid, source_id="unregistered_source", require_registered_provenance=True)  # T0


def governance_blocked(sid="gblock"):
    reg = {"council": K.AuthorityRecord("council", True, frozenset({"*"}), frozenset({"*"}),
                                        frozenset(K.GovernanceMode), (0, 1000))}
    return _st(sid, authority_registry=reg,
               governance=[K.GovernanceGrant("a", "routing", K.GovernanceMode.CAPTURED, (0, 10), "council")])


CHILD_KINDS = {
    "clean": clean, "speculative": speculative, "empirical_unverified": empirical_unverified,
    "structural_fail": structural_fail, "structural_qualified": structural_qualified,
    "epistemic_blocked": epistemic_blocked, "governance_blocked": governance_blocked,
}


def parent(children, tier=K.EpistemicTier.EMPIRICAL_SCI, gen="g", **kw):
    return _st("parent", tier, meta_spec=K.MetaArchitectureSpec(K.MetaGenerator(gen), [(c, set()) for c in children]), **kw)


def axes(r):
    return (r.structural_result.verdict, r.epistemic_result.status, r.combined_certification)


class ChildKindSanityTests(unittest.TestCase):
    """Each child kind sits where intended on the three axes (the premises of the other tests)."""

    def test_child_kinds(self) -> None:
        expect = {
            "clean": (SV.PASS, ES.ESTABLISHED, GV.PASS),
            "speculative": (SV.PASS, ES.UNVERIFIED, GV.QUALIFIED),
            "empirical_unverified": (SV.PASS, ES.UNVERIFIED, GV.QUALIFIED),
            "structural_fail": (SV.FAIL, ES.ESTABLISHED, GV.BLOCKED),
            "structural_qualified": (SV.QUALIFIED, ES.ESTABLISHED, GV.QUALIFIED),
            "epistemic_blocked": (SV.PASS, ES.INADMISSIBLE, GV.BLOCKED),
            "governance_blocked": (SV.PASS, ES.ESTABLISHED, GV.BLOCKED),
        }
        for name, make in CHILD_KINDS.items():
            with self.subTest(kind=name):
                self.assertEqual(axes(C.compile(make())), expect[name])

    def test_three_distinctions_are_three_different_outputs(self) -> None:
        unverified_substrate = C.compile(empirical_unverified()).certification()
        speculative_arch = C.compile(speculative()).certification()
        invalid_arch = C.compile(structural_fail()).certification()
        self.assertEqual(unverified_substrate["epistemic"]["label"], "EMPIRICAL / UNVERIFIED")
        self.assertEqual(unverified_substrate["structural"]["verdict"], "PASS")
        self.assertEqual(speculative_arch["epistemic"]["label"], "SPECULATIVE / UNVERIFIED")
        self.assertEqual(speculative_arch["structural"]["verdict"], "PASS")
        self.assertEqual(invalid_arch["structural"]["verdict"], "FAIL")
        self.assertEqual(invalid_arch["epistemic"]["label"], "EMPIRICAL / ESTABLISHED")
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in (unverified_substrate, speculative_arch, invalid_arch)}), 3)


class Item1EpistemicPropagatesIndependentlyTests(unittest.TestCase):
    """t611u item 1: epistemic qualification propagates independently of structural failure."""

    def test_structural_failure_does_not_touch_parent_epistemic(self) -> None:
        r = C.compile(parent([structural_fail()]))
        self.assertEqual(r.structural_result.verdict, SV.FAIL)
        self.assertEqual(r.epistemic_result.status, ES.ESTABLISHED)
        self.assertEqual(r.combined_certification, GV.BLOCKED)  # rc6 rule unchanged

    def test_epistemic_qualification_does_not_touch_parent_structure(self) -> None:
        for make in (speculative, empirical_unverified):
            with self.subTest(child=make.__name__):
                r = C.compile(parent([make()]))
                self.assertEqual(r.structural_result.verdict, SV.PASS)
                self.assertEqual(r.epistemic_result.status, ES.UNVERIFIED)
                self.assertEqual(r.combined_certification, GV.QUALIFIED)
                self.assertIn(f"child:{make().system_id}:UNVERIFIED", r.epistemic_result.qualifiers)

    def test_inadmissible_evidence_is_not_a_structural_failure(self) -> None:
        r = C.compile(parent([epistemic_blocked()]))
        self.assertEqual(r.structural_result.verdict, SV.PASS)
        self.assertEqual(r.epistemic_result.status, ES.INADMISSIBLE)
        self.assertEqual(r.combined_certification, GV.BLOCKED)
        self.assertFalse(r.is_trustworthy)

    def test_governance_failure_moves_neither_axis(self) -> None:
        r = C.compile(parent([governance_blocked()]))
        self.assertEqual((r.structural_result.verdict, r.epistemic_result.status), (SV.PASS, ES.ESTABLISHED))
        self.assertEqual(r.combined_certification, GV.BLOCKED)

    def test_both_failures_reported_on_their_own_axes(self) -> None:
        r = C.compile(parent([structural_fail("x"), speculative("y")]))
        self.assertEqual(r.structural_result.verdict, SV.FAIL)
        self.assertIn("child:x:FAIL", r.structural_result.qualifiers)
        self.assertNotIn("child:y:FAIL", r.structural_result.qualifiers)
        self.assertEqual(r.epistemic_result.status, ES.UNVERIFIED)
        self.assertIn("child:y:UNVERIFIED", r.epistemic_result.qualifiers)
        self.assertFalse(any(q.startswith("child:x:") for q in r.epistemic_result.qualifiers))

    def test_grandchild_epistemic_reaches_grandparent_without_structural_effect(self) -> None:
        mid = parent([speculative("leaf")], gen="g2")
        mid = K.SystemState(**{**mid.__dict__, "system_id": "mid"})
        top = C.compile(parent([mid], gen="g1"))
        self.assertEqual(top.structural_result.verdict, SV.PASS)
        self.assertEqual(top.epistemic_result.status, ES.UNVERIFIED)
        self.assertEqual(top.child_results[0].child_results[0].system_id, "leaf")

    def test_structural_result_ignores_tier_entirely(self) -> None:
        for kw in ({}, {"topology": K.TopologyClass.ARBORESCENT}, {"edges": set(K4_EDGES) | {("a", "a")}}):
            with self.subTest(kw=list(kw)):
                emp = C.compile(_st("x", **kw)).structural_result
                spec = C.compile(_st("x", K.EpistemicTier.SPECULATIVE_EXO, **kw)).structural_result
                myth = C.compile(_st("x", K.EpistemicTier.CORPUS_MYTH, sub=dict(has_represented_autopoiesis=True), **kw)).structural_result
                self.assertEqual(emp, spec)
                self.assertEqual(emp, myth)

    def test_taint_record_carries_child_axes_for_provenance(self) -> None:
        r = C.compile(parent([speculative()]))
        (t,) = r.taint_provenance
        self.assertEqual(t.preserved_observation["child_structural_result"], "PASS")
        self.assertEqual(t.preserved_observation["child_epistemic_status"], "UNVERIFIED")
        self.assertIs(t.preserved_observation["authority_granted"], False)


class Item2SpeculativeStructuralPassTests(unittest.TestCase):
    """t611u item 2: a speculative generator can reach structural PASS without empirical certification."""

    def test_speculative_generator_structural_pass(self) -> None:
        r = C.compile(parent([speculative("c1"), speculative("c2")], tier=K.EpistemicTier.SPECULATIVE_EXO))
        c = r.certification()
        self.assertEqual(c["structural"], {"verdict": "PASS", "qualifiers": []})
        self.assertEqual(c["epistemic"]["label"], "SPECULATIVE / UNVERIFIED")
        self.assertEqual(c["combined"], "QUALIFIED")
        self.assertFalse(c["empirically_certified"])
        self.assertTrue(r.is_trustworthy)  # speculative is not defective
        self.assertEqual(r.verdicts_for("E6"), [GV.QUALIFIED, GV.QUALIFIED])  # rc6 rule kept

    def test_speculative_never_empirically_certified(self) -> None:
        subs = [dict(has_empirical_autopoiesis=e, has_represented_autopoiesis=rp, memory_mechanism_status=m)
                for e, rp, m in itertools.product((False, True), (False, True), ("verified", "unverified", "impossible"))]
        for sub in subs:
            with self.subTest(sub=sub):
                r = C.compile(_st("x", K.EpistemicTier.SPECULATIVE_EXO, sub=sub))
                self.assertFalse(r.empirically_certified)
                self.assertNotEqual(r.epistemic_result.status, ES.ESTABLISHED)
                self.assertNotEqual(r.combined_certification, GV.PASS)

    def test_self_certification_attempt_is_inadmissible_not_invalid(self) -> None:
        r = C.compile(_st("x", K.EpistemicTier.SPECULATIVE_EXO, sub=dict(memory_mechanism_status="verified")))
        self.assertEqual(r.epistemic_result.status, ES.INADMISSIBLE)
        self.assertEqual(r.structural_result.verdict, SV.PASS)

    def test_meta_generative_fixture(self) -> None:
        r = C.compile(build_fixtures()["meta_generative"].state)
        for child in r.child_results:
            with self.subTest(child=child.system_id):
                self.assertEqual(child.structural_result.verdict, SV.PASS)
                self.assertEqual(child.epistemic_result.label, "SPECULATIVE / UNVERIFIED")
                self.assertEqual(child.combined_certification, GV.QUALIFIED)
        # The parent's structural qualification is its own (a 3-node graph), never its children's.
        self.assertEqual(r.structural_result.verdict, SV.QUALIFIED)
        self.assertEqual(r.structural_result.qualifiers, ("T5:two_node_cut_not_applicable_small_graph:QUALIFIED",))
        self.assertEqual(r.epistemic_result.label, "SPECULATIVE / UNVERIFIED")
        self.assertFalse(r.empirically_certified)

    def test_speculative_fixtures_are_structurally_pass(self) -> None:
        fx = build_fixtures()
        for key in ("multiversal_mycelium", "plasma_lattice", "temporal_fractal"):
            with self.subTest(fixture=key):
                r = C.compile(fx[key].state)
                self.assertEqual(r.structural_result.verdict, SV.PASS)
                self.assertEqual(r.epistemic_result.label, "SPECULATIVE / UNVERIFIED")
                self.assertEqual(r.combined_certification, GV.QUALIFIED)

    def test_empirical_certification_needs_established_evidence(self) -> None:
        self.assertTrue(C.compile(clean()).empirically_certified)
        self.assertFalse(C.compile(empirical_unverified()).empirically_certified)
        self.assertFalse(C.compile(_st("m", K.EpistemicTier.CORPUS_MYTH, sub=dict(has_represented_autopoiesis=True))).empirically_certified)
        self.assertFalse(C.compile(parent([speculative()])).empirically_certified)  # child lowers evidence


class Item3NoSilentUpgradeTests(unittest.TestCase):
    """t611u item 3: no child can raise a parent's structural, epistemic or combined qualification,
    and every lowering names the child that caused it."""

    PARENTS = {
        "empirical": dict(),
        "speculative": dict(tier=K.EpistemicTier.SPECULATIVE_EXO),
        "corpus": dict(tier=K.EpistemicTier.CORPUS_MYTH, sub=dict(has_represented_autopoiesis=True)),
        "structural_qualified": dict(topology=K.TopologyClass.ARBORESCENT),
        "unverified": dict(sub=dict(has_empirical_autopoiesis=True, memory_mechanism_status="unverified")),
    }

    def _alone(self, pkw):
        return C.compile(parent([], **pkw))

    def test_no_child_raises_any_axis(self) -> None:
        for (pname, pkw), (cname, make) in itertools.product(self.PARENTS.items(), CHILD_KINDS.items()):
            with self.subTest(parent=pname, child=cname):
                base = self._alone(pkw)
                withc = C.compile(parent([make()], **pkw))
                self.assertLessEqual(K.STRUCTURAL_RANK[withc.structural_result.verdict], K.STRUCTURAL_RANK[base.structural_result.verdict])
                self.assertLessEqual(K.EPISTEMIC_RANK[withc.epistemic_result.status], K.EPISTEMIC_RANK[base.epistemic_result.status])
                self.assertLessEqual(COMBINED_RANK[withc.combined_certification], COMBINED_RANK[base.combined_certification])
                self.assertEqual(withc.epistemic_result.tier, base.epistemic_result.tier)

    def test_parent_is_never_better_than_its_worst_child(self) -> None:
        for kinds in itertools.combinations(CHILD_KINDS, 2):
            with self.subTest(children=kinds):
                r = C.compile(parent([CHILD_KINDS[k](k) for k in kinds]))
                for ch in r.child_results:
                    self.assertLessEqual(K.STRUCTURAL_RANK[r.structural_result.verdict], K.STRUCTURAL_RANK[ch.structural_result.verdict])
                    self.assertLessEqual(K.EPISTEMIC_RANK[r.epistemic_result.status], K.EPISTEMIC_RANK[ch.epistemic_result.status])
                    self.assertLessEqual(COMBINED_RANK[r.combined_certification], COMBINED_RANK[ch.combined_certification])

    def test_empirical_child_cannot_upgrade_speculative_parent(self) -> None:
        r = C.compile(parent([clean()], tier=K.EpistemicTier.SPECULATIVE_EXO))
        self.assertEqual(r.epistemic_result.label, "SPECULATIVE / UNVERIFIED")
        self.assertFalse(r.empirically_certified)
        self.assertEqual(r.combined_certification, GV.QUALIFIED)

    def test_clean_child_cannot_upgrade_structurally_qualified_parent(self) -> None:
        r = C.compile(parent([clean()], topology=K.TopologyClass.ARBORESCENT))
        self.assertEqual(r.structural_result.verdict, SV.QUALIFIED)

    def test_every_lowering_names_its_child(self) -> None:
        for cname, make in CHILD_KINDS.items():
            with self.subTest(child=cname):
                r = C.compile(parent([make(cname)]))
                ch = r.child_results[0]
                if ch.structural_result.verdict != SV.PASS:
                    self.assertIn(f"child:{cname}:{ch.structural_result.verdict.value}", r.structural_result.qualifiers)
                if ch.epistemic_result.status != ES.ESTABLISHED:
                    self.assertIn(f"child:{cname}:{ch.epistemic_result.status.value}", r.epistemic_result.qualifiers)

    def test_appended_records_cannot_upgrade(self) -> None:
        r = C.compile(parent([speculative(), structural_fail()], tier=K.EpistemicTier.SPECULATIVE_EXO))
        before = axes(r)
        fake = [
            K.GateRecord("E6", GV.PASS, "child is fine"),
            K.GateRecord("T7", GV.VERIFIED_SUBSTRATE, "trust me"),
            K.GateRecord("T2", GV.AUTOPOIESIS_EMPIRICAL, "trust me"),
            K.GateRecord("T1", GV.PASS, "structure fine"),
            K.GateRecord("E6", GV.PASS, "override", {"code": "child_failure_taint", "child_id": "spec",
                                                     "child_structural_result": "PASS", "child_epistemic_status": "ESTABLISHED"}),
        ]
        over = r.with_appended_records(fake)
        self.assertEqual(axes(over), before)
        self.assertFalse(over.empirically_certified)

    def test_exemption_requests_cannot_upgrade(self) -> None:
        for ex in ({"T7"}, {"T2", "T7"}, {"T1", "T5"}):
            with self.subTest(exemptions=ex):
                spec = K.MetaArchitectureSpec(K.MetaGenerator("g"), [(speculative(), ex)])
                r = C.compile(_st("parent", K.EpistemicTier.SPECULATIVE_EXO, meta_spec=spec))
                self.assertNotEqual(r.epistemic_result.status, ES.ESTABLISHED)
                self.assertNotEqual(r.combined_certification, GV.PASS)

    def test_axes_cannot_be_assigned(self) -> None:
        r = C.compile(parent([speculative()]))
        for attr in ("structural_result", "epistemic_result", "combined_certification", "empirically_certified"):
            with self.subTest(attr=attr), self.assertRaises(AttributeError):
                setattr(r, attr, None)


class CombinedCertificationTests(unittest.TestCase):
    """The rc6 propagation rule is unchanged, and the combined result never beats either axis."""

    def test_combined_is_rc6_overall_verdict(self) -> None:
        fx = build_fixtures()
        for key, f in fx.items():
            with self.subTest(fixture=key):
                r = C.compile(f.state)
                self.assertEqual(r.combined_certification, r.overall_verdict)

    def test_combined_never_better_than_an_axis(self) -> None:
        cases = [make() for make in CHILD_KINDS.values()] + [parent([m()]) for m in CHILD_KINDS.values()]
        cases += [f.state for f in build_fixtures().values()]
        for st in cases:
            with self.subTest(system=st.system_id):
                r = C.compile(st)
                if r.structural_result.verdict == SV.FAIL or r.epistemic_result.status == ES.INADMISSIBLE:
                    self.assertEqual(r.combined_certification, GV.BLOCKED)
                if r.combined_certification == GV.PASS:
                    self.assertEqual(r.structural_result.verdict, SV.PASS)
                    self.assertEqual(r.epistemic_result.status, ES.ESTABLISHED)

    def test_rc6_dimensions_unchanged_and_kept(self) -> None:
        self.assertEqual(set(K.DIMENSION_GATES), {"structural", "biological", "governance"})
        r = C.compile(parent([speculative()]))
        self.assertEqual(set(r.dimension_verdicts()), {"structural", "biological", "governance"})

    def test_serialised(self) -> None:
        r = C.compile(build_fixtures()["meta_generative"].state)
        d = json.loads(r.to_json())
        self.assertEqual(d["certification"]["epistemic"]["label"], "SPECULATIVE / UNVERIFIED")
        self.assertEqual(d["certification"]["combined"], "QUALIFIED")
        self.assertEqual(d["schema_version"], "SC-TOL-001/2.1-rc7+kernel.3")


class NoAuthorityPathTests(unittest.TestCase):
    """What a structure is, what supports claims about it, and who may change it stay apart."""

    def _common(self):
        reg = {"council": K.AuthorityRecord("council", True, frozenset({"routing"}), frozenset({"a"}),
                                            frozenset({K.GovernanceMode.STEWARDED}), (0, 1000))}
        return dict(authority_registry=reg,
                    governance=[K.GovernanceGrant("a", "routing", K.GovernanceMode.STEWARDED, (0, 10), "council")],
                    escalations=[K.EscalationRequest("g", "c", K.GovernanceMode.SOVEREIGN, "quarantine", "g")])

    def test_axes_do_not_change_governance(self) -> None:
        base = C.compile(parent([clean("c")], **self._common()))
        for make in CHILD_KINDS.values():
            with self.subTest(child=make.__name__):
                r = C.compile(parent([make("c")], **self._common()))
                for attr in ("active_grants", "expired_grants", "accepted_escalations", "rejected_escalations"):
                    self.assertEqual(getattr(r, attr), getattr(base, attr), attr)
                self.assertEqual(r.dimension_verdicts()["governance"], base.dimension_verdicts()["governance"])
                self.assertEqual(r.accepted_escalations, ())

    def test_established_evidence_grants_nothing(self) -> None:
        # Fully established evidence and a valid structure do not let a generator authorize
        # its own escalation, and the evidence axis does not hide the governance failure.
        r = C.compile(_st("x", **self._common()))
        self.assertEqual((r.structural_result.verdict, r.epistemic_result.status), (SV.PASS, ES.ESTABLISHED))
        self.assertEqual(r.accepted_escalations, ())
        self.assertIn("self_authorized_escalation", r.codes_for("T8"))
        self.assertEqual(r.combined_certification, GV.BLOCKED)
        self.assertFalse(r.empirically_certified)

    def test_certification_payload_has_no_authority_fields(self) -> None:
        blob = json.dumps(C.compile(parent([speculative()])).certification()).lower()
        for word in ("grant", "authority", "escalat", "sovereign", "mode"):
            self.assertNotIn(word, blob)


class Item4CorpusBaselineTests(unittest.TestCase):
    """t611u item 4 (in-repo part): the reference compiler is reachable from no packaged module,
    so rc7 cannot move the 963-prompt corpus. The corpus diff itself is a merge gate (spec doc 5b)."""

    def test_no_packaged_module_imports_reference_compiler(self) -> None:
        offenders = []
        for py in REPO_ROOT.rglob("*.py"):
            rel = py.relative_to(REPO_ROOT).as_posix()
            if rel.startswith(("tests/", "docs/", ".")) or "/__pycache__/" in rel:
                continue
            if "sc_tol_001" in py.read_text(encoding="utf-8", errors="replace"):
                offenders.append(rel)
        self.assertEqual(offenders, [])

    def test_spec_doc_records_rc7_and_baseline(self) -> None:
        doc = (REPO_ROOT / "docs" / "SC-TOL-001_TREE_OF_LIFE_STRUCTURAL_COMPILER.md").read_text(encoding="utf-8")
        for needle in ("rc7", "963", "SPECULATIVE / UNVERIFIED", "gold_awarded"):
            self.assertIn(needle, doc)


if __name__ == "__main__":
    unittest.main()
