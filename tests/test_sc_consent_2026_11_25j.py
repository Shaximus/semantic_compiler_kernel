"""2026-11-25j Consent Invariant, SCC-001 entry and SC-TRIAD-SG-001 rev 1.1.0 (Shax t588u).

Honest grading (tier by rule, no gate above 0.9), separate layers, short router
inputs with full text in the body, explicit-only routing, SC-SCC-001's
provisional defaults raising needs_review, MAFUBA left unvalidated, and the
Stargate corrections recorded.
"""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

from semantic_compiler import compile_semantic_packet
from semantic_compiler.expansion.elevator import EXPLICIT_ONLY_ENTRY_HINTS, summon
from semantic_compiler.expansion.router import route_domains

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-25j"
NEW_IDS = ("SC-CONSENT-001", "SC-SCC-001")
EXPECTED = {"SC-CONSENT-001": 0.821, "SC-SCC-001": 0.802}
HOMES = {"SC-CONSENT-001": "soul_bomb_sovereignty", "SC-SCC-001": "capability_isolation"}


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
SG = _single("SC-TRIAD-SG-001.jsonl")
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}
PENDING_DOC = (REPO_ROOT / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")


class ConsentEntrySchemaAndGradeTests(unittest.TestCase):
    def test_schema_parity_and_manifest(self) -> None:
        for eid, e in {**ENTRIES, "SC-TRIAD-SG-001": SG}.items():
            with self.subTest(eid=eid):
                self.assertEqual(list(e.keys()), list(TEMPLATE.keys()))
                item = next(m for m in MANIFEST["entries"] if m["entry_id"] == eid)
                raw = (COMPILED_DIR / item["file"]).read_bytes()
                self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(item["bytes"], len(raw))
                self.assertEqual(item["classification"], e["dataset_tier"])
                self.assertEqual(len(e["functional_departments"]), 15)
                for x in e["metadata"]["cross_references"]:
                    self.assertIn(x, MANIFEST_IDS)

    def test_short_router_input_and_full_text_in_body(self) -> None:
        spec_text = (EVIDENCE / "t588u_scc_engineering_spec.txt").read_text(encoding="utf-8")
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertLess(len(e["input"]), 400)
                self.assertTrue(e["input"].startswith(eid))
                body = e["v2_extensions"]["source_text"]
                self.assertIn(spec_text, body)
        self.assertIn((REPO_ROOT / "docs" / "SCC-001.md").read_text(encoding="utf-8"),
                      ENTRIES["SC-SCC-001"]["v2_extensions"]["source_text"])

    def test_tier_by_rule_no_gold_for_beauty(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                scores = [g["score"] for g in e["gates"].values()]
                iq = round(math.exp(sum(math.log(s) for s in scores) / len(scores)), 3)
                self.assertEqual(e["isomorphism_quality"]["score"], iq)
                self.assertEqual(iq, EXPECTED[eid])
                self.assertEqual(e["dataset_tier"], "SILVER")
                self.assertLessEqual(max(scores), 0.9)
                self.assertTrue(all(g["passed"] for g in e["gates"].values()))

    def test_layers_kept_separate(self) -> None:
        grades = set()
        for e in list(ENTRIES.values()) + [SG]:
            for c in e["analysis"]["claims"]:
                self.assertTrue(c["layers"])
                grades |= {layer["grade"] for layer in c["layers"]}
            self.assertTrue(any("literal" in g.lower() for g in e["outputs"]["guardrails"]))
        self.assertTrue({"CANON", "TRADITION", "SHAX_INTERPRETATION", "COMPILER", "SYNTHETIC_ONLY"} <= grades)


class ConsentInvariantContentTests(unittest.TestCase):
    def test_four_conditions_and_axes(self) -> None:
        text = ENTRIES["SC-CONSENT-001"]["analysis"]["claims"][0]["text"].lower()
        for cond in ("voluntary entry", "informed agreement", "preserved agency", "withdraw or renegotiate"):
            self.assertIn(cond, text)
        axes = ENTRIES["SC-CONSENT-001"]["analysis"]["claims"][1]["text"]
        self.assertIn("who holds authority", axes)
        self.assertIn("legitimately granted", axes)

    def test_triad_resolution_is_proposed_not_closed(self) -> None:
        claim = next(c for c in ENTRIES["SC-CONSENT-001"]["analysis"]["claims"] if c["tig_grade"] == "PROPOSED_RESOLUTION")
        self.assertIn("SC-TRIAD-001", claim["text"])
        self.assertIn("SC-TRIAD-001 — proposed resolution via SC-CONSENT-001 (not closed)", PENDING_DOC)
        hub = _single("SC-TRIAD-001.jsonl")
        self.assertIs(hub["metadata"]["pending_deliberation"], True)
        self.assertEqual(hub["metadata"]["deliberation_status"], "PROVISIONAL_DEFAULT")
        self.assertNotIn("pending_deliberation", ENTRIES["SC-CONSENT-001"]["metadata"])

    def test_rev2_tension_recorded(self) -> None:
        body = ENTRIES["SC-CONSENT-001"]["v2_extensions"]["source_text"]
        self.assertIn("refusal is self-destruction", body)
        self.assertIn("refusal is self-destruction", PENDING_DOC)


class SccEntryTests(unittest.TestCase):
    def test_proposed_unvalidated_like_mafuba(self) -> None:
        m = ENTRIES["SC-SCC-001"]["metadata"]
        self.assertIs(m["gold_awarded"], False)
        self.assertEqual(m["validation_status"], "PROPOSED_UNVALIDATED")
        self.assertEqual(m["verification_axes"]["empirical"], "UNVALIDATED")
        for e in ENTRIES.values():
            self.assertIn("SC-MAFUBA-001", e["metadata"]["unresolved_cross_references"])
            self.assertNotIn("SC-MAFUBA-001", MANIFEST_IDS)
            self.assertEqual(e["metadata"]["cross_reference_resolution"]["SC-MAFUBA-001"]["status"], "PROPOSED_GOLD_UNVALIDATED")

    def test_two_provisional_defaults_listed(self) -> None:
        m = ENTRIES["SC-SCC-001"]["metadata"]
        self.assertIs(m["pending_deliberation"], True)
        self.assertEqual(m["deliberation_status"], "PROVISIONAL_DEFAULT")
        ids = {d["id"] for d in ENTRIES["SC-SCC-001"]["v2_extensions"]["deliberation"]["defaults"]}
        self.assertEqual(ids, {"SCC-001-FIRST-DOMAIN", "SCC-001-DECISION-MODE"})
        spec = (REPO_ROOT / "docs" / "SCC-001.md").read_text(encoding="utf-8")
        for i in ids:
            self.assertIn(i, PENDING_DOC)
            self.assertIn(i, spec)
        self.assertIn("PROVISIONAL_DEFAULT", spec)


class StargateRevisionTests(unittest.TestCase):
    def test_revision_bumped_and_grade_unchanged(self) -> None:
        self.assertEqual(SG["metadata"]["entry_revision"], "1.1.0")
        self.assertEqual(SG["isomorphism_quality"]["score"], 0.849)
        self.assertNotIn("pending_deliberation", SG["metadata"])

    def test_alliance_succession_and_threat_forms(self) -> None:
        text = " ".join(c["text"] for c in SG["analysis"]["claims"])
        for s in ("Ancients, Asgard, Nox and Furlings", "The Torment of Tantalus", "The Fifth Race", "Unending",
                  "succession, not victory", "Unas", "abdominal pouch", "Reetou", "Tollan", "Aschen"):
            self.assertIn(s, text)

    def test_furlings_left_undefined(self) -> None:
        furl = next(c for c in SG["analysis"]["claims"] if c["text"].startswith("The Furlings"))
        self.assertIn("No theology is assigned", furl["text"])
        self.assertEqual({layer["grade"] for layer in furl["layers"]}, {"CANON"})

    def test_paste_corrections_recorded(self) -> None:
        corr = SG["outputs"]["correction"]
        for s in ("back of the neck", "Fifth Race", "Unending", "Reetou rebel", "Children of the Gods", "200", "Paradise Lost"):
            self.assertIn(s, corr)

    def test_evidence_hashes_in_readme(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        for name in ("t588u_scc_engineering_spec.txt", "t588u_inline_message_excerpt.md"):
            sha = hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest()
            self.assertIn(sha, readme)
            for e in ENTRIES.values():
                self.assertIn(sha, e["metadata"]["source_draft"])


class ConsentRoutingTests(unittest.TestCase):
    def test_explicit_only(self) -> None:
        self.assertTrue(set(NEW_IDS) <= EXPLICIT_ONLY_ENTRY_HINTS)

    def test_explicit_ids_route_home(self) -> None:
        for eid in NEW_IDS:
            with self.subTest(eid=eid):
                r = route_domains(f"Explain {eid}.")
                self.assertEqual(r.domain, HOMES[eid])
                summoned = [e.entry_id for e in summon(f"Explain {eid}.", top_k=5).compiled_entries]
                self.assertIn(eid, summoned)

    def test_everyday_words_do_not_lift(self) -> None:
        for text in (
            "Please give your consent before the appointment.",
            "The app asks for authorization to access your camera.",
            "Train a classifier on the spam dataset.",
            "The host welcomed every guest by the door.",
            "The AI writes code.",
        ):
            with self.subTest(text=text):
                self.assertNotIn(route_domains(text).domain, {"soul_bomb_sovereignty"})
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertNotIn("SC-SCC-001", ids)

    def test_scc_needs_review_on_explicit_id(self) -> None:
        packet = compile_semantic_packet("Explain SC-SCC-001.")
        self.assertTrue(packet.needs_review)
        self.assertIn("SC-SCC-001", [x["entry_id"] for x in packet.needs_review_entries])
        ids = [x["entry_id"] for x in (compile_semantic_packet("Explain SC-CONSENT-001.").needs_review_entries or [])]
        self.assertNotIn("SC-SCC-001", ids)


if __name__ == "__main__":
    unittest.main()
