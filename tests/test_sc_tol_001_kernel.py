"""SC-TOL-001 Tree of Life structural compiler: kernel checks (Shax t608u/t609u).

Material Shax supplied: a design thread (v1 -> v2.1-rc2) and an rc5 ``.py`` file,
pasted from ChatGPT and other-assistant conversations. t609u names rc5 as the
version to implement.

What this file checks:
- rc5's own 42 acceptance bodies run against the unmodified rc5 as well;
- one regression per recorded KERNEL-FIX that fails on rc5 and passes on the kernel copy;
- claims made in the thread (rc1 Issue B false, rc2 correction, test_08 trunk);
- the eight provenance-tagged fixtures;
- the evidence file (hash, bytes, privacy);
- the compiled entry (schema, SILVER by rule, xrefs), explicit-only routing and needs_review;
- that core/ and expansion/ do not import the reference compiler.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unittest
from pathlib import Path

from semantic_compiler import compile_semantic_packet
from semantic_compiler.expansion.elevator import EXPLICIT_ONLY_ENTRY_HINTS, summon
from semantic_compiler.expansion.router import route_domains
from tests.reference.sc_tol_001 import compiler as K
from tests.reference.sc_tol_001 import rc5 as R
from tests.reference.sc_tol_001.fixtures import NEEDS, SEFIROT_KIRCHER_22, build_fixtures

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-27a"
ATTACHMENT = EVIDENCE / "sc_tol_001_v2.1-rc5_attachment.py"
SPEC_DOC = REPO_ROOT / "docs" / "SC-TOL-001_TREE_OF_LIFE_STRUCTURAL_COMPILER.md"
ACCEPTANCE = REPO_ROOT / "tests" / "test_sc_tol_001_acceptance.py"
EID = "SC-TOL-001"
ATTACHMENT_SHA = "55dea4aeacc12aa75a7729d5fbd276061b0ee4e9519a903653522da695b64cfa"
ATTACHMENT_BYTES = 128351


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRY = _single(f"{EID}.jsonl")
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


def _state(M, **kw):
    base = dict(
        system_id="p",
        substrate=M.SubstrateSpec("dna", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
        topology=M.TopologyClass.DISTRIBUTED,
        epistemic_tier=M.EpistemicTier.EMPIRICAL_SCI,
        nodes={"g1", "n1", "n2", "hid"},
        edges={("g1", "n1"), ("n1", "n2"), ("n2", "g1")},
    )
    base.update(kw)
    return M.SystemState(**base)


def _omni(M, aid, chain=()):
    return M.AuthorityRecord(aid, True, frozenset({"*"}), frozenset({"*"}), frozenset(M.GovernanceMode), (0, 1000), chain)


class Rc5SourceTests(unittest.TestCase):
    def test_rc5_module_is_verbatim_attachment_prefix(self) -> None:
        att = ATTACHMENT.read_text(encoding="utf-8").splitlines()
        rc5 = (REPO_ROOT / "tests" / "reference" / "sc_tol_001" / "rc5.py").read_text(encoding="utf-8").splitlines()
        body = rc5[4:]
        self.assertEqual(body, att[: len(body)])
        self.assertEqual(len(body), 1868)
        self.assertEqual(R.SCHEMA_VERSION, "SC-TOL-001/2.1-rc5")
        self.assertEqual(K.SCHEMA_VERSION, "SC-TOL-001/2.1-rc5+kernel.1")

    def test_acceptance_bodies_are_verbatim(self) -> None:
        att = ATTACHMENT.read_text(encoding="utf-8").splitlines()
        acc = ACCEPTANCE.read_text(encoding="utf-8").splitlines()
        tail = att[1871:]
        self.assertEqual(acc[-len(tail):], tail)

    def test_42_acceptance_bodies_pass_on_unmodified_rc5(self) -> None:
        src = ACCEPTANCE.read_text(encoding="utf-8")
        swapped = src.replace("from tests.reference.sc_tol_001.compiler import *",
                              "from tests.reference.sc_tol_001.rc5 import *", 1)
        self.assertNotEqual(src, swapped)
        ns: dict = {"__name__": "sc_tol_001_acceptance_on_rc5"}
        exec(compile(swapped, "acceptance_on_rc5", "exec"), ns)
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        for obj in ns.values():
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj is not unittest.TestCase:
                suite.addTests(loader.loadTestsFromTestCase(obj))
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 42)
        self.assertEqual((result.failures, result.errors), ([], []))


class KernelFixRegressionTests(unittest.TestCase):
    """Each test asserts the rc5 defect and the kernel-copy behaviour."""

    def test_fix1_opaque_node_cannot_authorize_escalation(self) -> None:
        def run(M):
            return M.StructuralCompiler().compile(_state(
                M, authority_registry={"hid": _omni(M, "hid")}, boundaries=[M.HorizonBoundary("b", {"hid"})],
                escalations=[M.EscalationRequest("g1", "n1", M.GovernanceMode.SOVEREIGN, "routing", "hid")]))
        self.assertEqual(len(run(R).accepted_escalations), 1)
        r = run(K)
        self.assertEqual(len(r.accepted_escalations), 0)
        self.assertIn("opaque_escalation_node", r.codes_for("T6"))

    def test_fix1_opaque_node_cannot_grant(self) -> None:
        def run(M):
            return M.StructuralCompiler().compile(_state(
                M, authority_registry={"hid": _omni(M, "hid")}, boundaries=[M.HorizonBoundary("b", {"hid"})],
                governance=[M.GovernanceGrant("n1", "routing", M.GovernanceMode.STEWARDED, (0, 10), "hid")]))
        self.assertEqual(len(run(R).active_grants), 1)
        r = run(K)
        self.assertEqual(len(r.active_grants), 0)
        self.assertIn("opaque_authority_reference", r.codes_for("T6"))

    def test_fix2_invalid_memory_status_blocks(self) -> None:
        for status in ("Verified", "verfied", "impossibl"):
            with self.subTest(status=status):
                def run(M):
                    return M.StructuralCompiler().compile(_state(
                        M, substrate=M.SubstrateSpec("x", has_empirical_autopoiesis=True, memory_mechanism_status=status)))
                self.assertTrue(run(R).is_trustworthy)
                r = run(K)
                self.assertFalse(r.is_trustworthy)
                self.assertIn("invalid_memory_mechanism_status", r.codes_for("E1"))
        self.assertTrue(K.StructuralCompiler().compile(_state(K)).is_trustworthy)

    def test_fix3_result_is_deeply_immutable(self) -> None:
        r5 = R.StructuralCompiler().compile(_state(R, fault_sets=[{"n1"}]))
        r5.fault_reports[0]["fragmentation_status"] = "TAMPERED"
        self.assertEqual(r5.fault_reports[0]["fragmentation_status"], "TAMPERED")
        rk = K.StructuralCompiler().compile(_state(K, fault_sets=[{"n1"}]))
        with self.assertRaises(TypeError):
            rk.fault_reports[0]["fragmentation_status"] = "TAMPERED"
        with self.assertRaises(TypeError):
            rk.records[0].preserved_observation["x"] = 1
        json.loads(rk.to_json())

    def test_fix4_captured_mode_escalation_blocked(self) -> None:
        def run(M):
            return M.StructuralCompiler().compile(_state(
                M, authority_registry={"hid": _omni(M, "hid")},
                escalations=[M.EscalationRequest("g1", "n1", M.GovernanceMode.CAPTURED, "routing", "hid")]))
        self.assertEqual(len(run(R).accepted_escalations), 1)
        r = run(K)
        self.assertEqual(len(r.accepted_escalations), 0)
        self.assertIn("captured_mode_escalation", r.codes_for("T8"))

    def test_fix5_t1_ignores_opaque_structure(self) -> None:
        def run(M):
            return M.StructuralCompiler().compile(_state(
                M, topology=M.TopologyClass.ARBORESCENT, nodes={"a", "b", "c", "hid"},
                edges={("a", "b"), ("b", "c"), ("c", "hid"), ("hid", "a")},
                boundaries=[M.HorizonBoundary("b", {"hid"})]))
        r5 = run(R)
        self.assertEqual(r5.effective_topology, R.TopologyClass.RETICULATE)
        rk = run(K)
        self.assertEqual(rk.effective_topology, K.TopologyClass.ARBORESCENT)
        self.assertNotIn("topology_structure_mismatch", rk.codes_for("T1"))

    def test_fix6_subgenerator_tamper_reported_once(self) -> None:
        def run(M):
            sg, _rec = M.MetaGenerator("m").emit_subgenerator("s", frozenset({"T1"}))
            return sg, sg.emit(M.StructuralCompiler(), _state(M, system_id="c2"))
        _sg, c5 = run(R)
        self.assertIn("generator_tamper_restored", c5.codes_for("E6"))
        sgk, ck = run(K)
        self.assertNotIn("generator_tamper_restored", ck.codes_for("E6"))
        self.assertTrue(K.CORE_IMMUTABLE_GATES <= set(sgk.immutable_gates))

    def test_fix7_unregistered_hop_is_surfaced(self) -> None:
        def run(M):
            return M.StructuralCompiler().compile(_state(
                M, authority_registry={"ext": _omni(M, "ext", ("ghost_hop",))},
                escalations=[M.EscalationRequest("g1", "n1", M.GovernanceMode.SOVEREIGN, "routing", "ext")]))
        r5 = run(R)
        self.assertEqual(len(r5.accepted_escalations), 1)
        self.assertNotIn("unregistered_upstream_hop", r5.codes_for("T8"))
        rk = run(K)
        self.assertEqual(len(rk.accepted_escalations), 1)  # default stays permissive (PROVISIONAL_DEFAULT)
        self.assertIn("unregistered_upstream_hop", rk.codes_for("T8"))
        self.assertIn(K.GateVerdict.QUALIFIED, rk.verdicts_for("T8"))

    def test_recorded_not_changed_child_does_not_taint_parent(self) -> None:
        child = _state(K, system_id="child", source_id="nope")
        r = K.StructuralCompiler().compile(_state(K, meta_spec=K.MetaArchitectureSpec(K.MetaGenerator("m"), [(child, set())])))
        self.assertTrue(r.is_trustworthy)
        self.assertFalse(r.child_results[0].is_trustworthy)

    def test_every_fix_is_tagged_and_documented(self) -> None:
        src = (REPO_ROOT / "tests" / "reference" / "sc_tol_001" / "compiler.py").read_text(encoding="utf-8")
        doc = SPEC_DOC.read_text(encoding="utf-8")
        for n in range(1, 8):
            with self.subTest(fix=n):
                self.assertIn(f"KERNEL-FIX-{n}", src)
                self.assertIn(f"KERNEL-FIX-{n}", doc)


class ThreadClaimTests(unittest.TestCase):
    def test_rc1_issue_b_example_is_false(self) -> None:
        tri = {("C", "A"), ("C", "B"), ("A", "B")}
        self.assertEqual(K.find_cut_vertices({"A", "B", "C"}, tri), frozenset())

    def test_rc2_corrected_example_holds(self) -> None:
        g = {("A", "B"), ("A", "H"), ("B", "H"), ("H", "C")}
        self.assertEqual(K.find_cut_vertices({"A", "B", "H", "C"}, g), frozenset({"H"}))

    def test_trunk_is_the_only_cut_in_test_08_graph(self) -> None:
        g = {("hidden_root", "trunk"), ("trunk", "branch_1"), ("trunk", "branch_2")}
        self.assertEqual(K.find_cut_vertices({"hidden_root", "trunk", "branch_1", "branch_2"}, g), frozenset({"trunk"}))


class FixtureTests(unittest.TestCase):
    FIX = build_fixtures()
    C = K.StructuralCompiler()

    def test_eight_fixtures_with_provenance(self) -> None:
        self.assertEqual(len(self.FIX), 8)
        for fx in self.FIX.values():
            self.assertTrue(fx.provenance.citation)
            self.assertIn(fx.provenance.provenance_status,
                          {"NAMED_IN_SOURCE_NOT_OPENED", "NEEDS_PER_TEXT_PROVENANCE", "SPECULATIVE_PROPOSAL"})

    def test_expectations(self) -> None:
        for key, fx in self.FIX.items():
            r = self.C.compile(fx.state)
            for k, v in fx.expectations.items():
                with self.subTest(fixture=key, check=k):
                    if k == "trustworthy":
                        self.assertEqual(r.is_trustworthy, v)
                    elif k == "cut_vertices":
                        self.assertEqual(set(r.cut_vertices), v)
                    elif k == "masked":
                        self.assertEqual(set(r.masked_nodes), v)
                    elif k == "effective_topology":
                        self.assertEqual(r.effective_topology.name, v)
                    elif k == "children":
                        self.assertEqual(len(r.child_results), v)
                        self.assertTrue(all(c.is_trustworthy for c in r.child_results))
                    else:
                        self.assertIn(v, [x.name for x in r.verdicts_for(k)])

    def test_sefirot_shape_and_provenance(self) -> None:
        nodes = {n for e in SEFIROT_KIRCHER_22 for n in e}
        self.assertEqual((len(nodes), len(set(SEFIROT_KIRCHER_22))), (10, 22))
        fx = self.FIX["sefirot"]
        self.assertEqual(fx.provenance.provenance_status, NEEDS)
        r = self.C.compile(fx.state)
        self.assertIn(K.GateVerdict.BLOCKED, r.verdicts_for("T0"))
        self.assertFalse(r.is_trustworthy)

    def test_speculative_never_verified(self) -> None:
        for key in ("multiversal_mycelium", "plasma_lattice", "temporal_fractal"):
            with self.subTest(fixture=key):
                r = self.C.compile(self.FIX[key].state)
                self.assertNotIn(K.GateVerdict.VERIFIED_SUBSTRATE, r.verdicts_for("T7"))


class EntryAndEvidenceTests(unittest.TestCase):
    def test_evidence_hash_bytes_privacy(self) -> None:
        raw = ATTACHMENT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), ATTACHMENT_SHA)
        self.assertEqual(len(raw), ATTACHMENT_BYTES)
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        self.assertIn(ATTACHMENT_SHA, readme)
        self.assertIn(str(ATTACHMENT_BYTES), readme)
        self.assertIn("not by Shax", readme)
        self.assertIn("no redaction", readme)
        self.assertIn(ATTACHMENT_SHA, ENTRY["metadata"]["source_draft"])
        blob = "\n".join([raw.decode("utf-8"), readme, SPEC_DOC.read_text(encoding="utf-8"), json.dumps(ENTRY, ensure_ascii=False)])
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))
        self.assertNotIn("http", raw.decode("utf-8"))

    def test_schema_manifest_xrefs(self) -> None:
        self.assertEqual(list(ENTRY.keys()), list(TEMPLATE.keys()))
        item = next(m for m in MANIFEST["entries"] if m["entry_id"] == EID)
        self.assertEqual(item["sha256"], hashlib.sha256((COMPILED_DIR / item["file"]).read_bytes()).hexdigest())
        self.assertEqual(item["classification"], "SILVER")
        self.assertEqual(len(ENTRY["functional_departments"]), 15)
        for x in ENTRY["metadata"]["cross_references"]:
            self.assertIn(x, MANIFEST_IDS)
        self.assertLess(len(ENTRY["input"]), 400)
        self.assertTrue(ENTRY["input"].startswith(EID))

    def test_silver_by_rule_not_gold(self) -> None:
        scores = [g["score"] for g in ENTRY["gates"].values()]
        iq = round(math.exp(sum(math.log(s) for s in scores) / len(scores)), 3)
        self.assertEqual(ENTRY["isomorphism_quality"]["score"], iq)
        self.assertLess(iq, 0.9)
        self.assertEqual(ENTRY["dataset_tier"], "SILVER")
        self.assertLessEqual(max(scores), 0.9)
        self.assertTrue(all(g["passed"] for g in ENTRY["gates"].values()))
        doc = SPEC_DOC.read_text(encoding="utf-8")
        self.assertIn("gold_awarded", doc)
        self.assertIn("Catherine remains unresolved", " ".join(ENTRY["outputs"]["guardrails"]))

    def test_scc_cross_link_and_pending(self) -> None:
        # The SCC-001-AC doc is hash-pinned (reproducibility.json), so the link lives on the SC-TOL-001 side.
        doc = SPEC_DOC.read_text(encoding="utf-8")
        self.assertIn("docs/SCC-001-AC_ANTI_CAPTURE.md", doc)
        self.assertIn("T4", doc)
        self.assertIn("T8", doc)
        pending = (REPO_ROOT / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        self.assertIn(f"## {EID} ", pending)
        meta = ENTRY["metadata"]
        self.assertEqual(meta["deliberation_status"], "PROVISIONAL_DEFAULT")
        self.assertIn(EID.lower(), meta["review_trigger_terms"])


class RoutingAndIsolationTests(unittest.TestCase):
    def test_explicit_only_and_routes_home(self) -> None:
        self.assertIn(EID, EXPLICIT_ONLY_ENTRY_HINTS)
        self.assertEqual(route_domains(f"Explain {EID}.").domain, "soul_bomb_sovereignty")
        self.assertIn(EID, [e.entry_id for e in summon(f"Explain {EID}.", top_k=5).compiled_entries])

    def test_everyday_words_do_not_lift(self) -> None:
        for text in ("The tree of life in my garden is blooming.", "Yggdrasil is a cool name for a server.",
                     "What is a phylogenetic tree?", "remind me to call mom at 6"):
            with self.subTest(text=text):
                self.assertNotEqual(route_domains(text).domain, "soul_bomb_sovereignty")
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertNotIn(EID, ids)

    def test_needs_review_for_explicit_id(self) -> None:
        packet = compile_semantic_packet(f"Explain {EID}.")
        self.assertTrue(packet.needs_review)
        self.assertIn(EID, [x["entry_id"] for x in packet.needs_review_entries])

    def test_runtime_does_not_import_reference(self) -> None:
        for sub in ("core", "expansion"):
            for p in (REPO_ROOT / sub).rglob("*.py"):
                with self.subTest(path=str(p.relative_to(REPO_ROOT))):
                    self.assertNotIn("sc_tol_001", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
