"""2026-11-25k Vessel equilibrium extensions (Shax t589u/t590u/t592u).

SC-VESSEL-SPN-001 (Supernatural), SC-VESSEL-CAIN-001 (Cain/Abel inheritance)
and SC-VESSEL-SW-001 (Star Wars): honest grading (tier by rule, no gate above
0.9 without a confirmed prediction), recorded lore corrections, separate
layers (canon, tradition, Shax, compiler), short router inputs, explicit-only
routing, the two provisional defaults raising needs_review, and evidence
files that carry only the fictional and theological structure.
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

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-25k"
NEW_IDS = ("SC-VESSEL-SPN-001", "SC-VESSEL-CAIN-001", "SC-VESSEL-SW-001")
EXPECTED = {"SC-VESSEL-SPN-001": 0.826, "SC-VESSEL-CAIN-001": 0.813, "SC-VESSEL-SW-001": 0.82}
PENDING = ("SC-VESSEL-SPN-001", "SC-VESSEL-CAIN-001")
SOURCES = ("t589u_message_body.txt", "t590u_relayed_summary.md", "t592u_relayed_summary.md")


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class VesselSchemaAndGradeTests(unittest.TestCase):
    def test_schema_parity_and_manifest(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertEqual(list(e.keys()), list(TEMPLATE.keys()))
                item = next(m for m in MANIFEST["entries"] if m["entry_id"] == eid)
                raw = (COMPILED_DIR / item["file"]).read_bytes()
                self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(item["classification"], e["dataset_tier"])
                self.assertEqual(len(e["functional_departments"]), 15)
                for x in e["metadata"]["cross_references"]:
                    self.assertIn(x, MANIFEST_IDS)

    def test_short_router_input_and_full_text_in_body(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertLess(len(e["input"]), 400)
                self.assertTrue(e["input"].startswith(eid))
                body = e["v2_extensions"]["source_text"]
                self.assertGreater(len(body), 5000)
                for name in SOURCES:
                    self.assertIn((EVIDENCE / name).read_text(encoding="utf-8"), body)

    def test_tier_by_rule_no_gold_for_beauty(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                scores = [g["score"] for g in e["gates"].values()]
                iq = round(math.exp(sum(math.log(s) for s in scores) / len(scores)), 3)
                self.assertEqual(e["isomorphism_quality"]["score"], iq)
                self.assertEqual(iq, EXPECTED[eid])
                self.assertEqual(e["dataset_tier"], "GOLD" if iq >= 0.9 and min(scores) >= 0.8 else "SILVER")
                self.assertEqual(e["dataset_tier"], "SILVER")
                self.assertLessEqual(max(scores), 0.9)
                self.assertTrue(all(g["passed"] for g in e["gates"].values()))

    def test_layers_kept_separate(self) -> None:
        grades = set()
        for e in ENTRIES.values():
            for c in e["analysis"]["claims"]:
                self.assertTrue(c["layers"])
                grades |= {layer["grade"] for layer in c["layers"]}
            for m in e["isomorphism_analysis"]["mappings"]:
                self.assertIs(m["substrate_confusion_check"], True)
                self.assertEqual(m["mapping_class"], "STRUCTURAL_ANALOGY")
                self.assertTrue(m["residual_mismatches"])
            self.assertTrue(any("literal" in g.lower() for g in e["outputs"]["guardrails"]))
        self.assertTrue({"CANON", "TRADITION", "SHAX_INTERPRETATION", "ANALOGOUS", "COMPILER"} <= grades)

    def test_self_identification_is_symbolic_and_ungraded(self) -> None:
        claims = ENTRIES["SC-VESSEL-SPN-001"]["analysis"]["claims"]
        c = next(c for c in claims if "Sam and Dean merged" in c["text"])
        self.assertIn("not a literal claim", c["text"])
        self.assertTrue(c["tig_grade"].startswith("UNGRADED"))
        self.assertEqual({layer["grade"] for layer in c["layers"]}, {"SHAX_INTERPRETATION"})

    def test_lore_corrections_recorded(self) -> None:
        spn = ENTRIES["SC-VESSEL-SPN-001"]["outputs"]["correction"]
        for s in ("13x23", "Apocalypse World Michael", "Swan Song", "swallow the finger", "Enchain", "permission"):
            self.assertIn(s, spn)
        cain = ENTRIES["SC-VESSEL-CAIN-001"]["outputs"]["correction"]
        for s in ("Genesis 4:15", "protection", "First Born", "lock and key on the Darkness", "Dean asked for the Mark", "Amara", "15x19"):
            self.assertIn(s, cain)
        sw = ENTRIES["SC-VESSEL-SW-001"]["outputs"]["correction"]
        for s in ("mechanical hand", "own choice", "twins", "Rise of Skywalker"):
            self.assertIn(s, sw)

    def test_consent_and_triad_links(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                xrefs = e["metadata"]["cross_references"]
                for x in ("SC-TRIAD-001", "SC-CONSENT-001", "SC-SCC-001"):
                    self.assertIn(x, xrefs)
                    self.assertIn(x, MANIFEST_IDS)
                    self.assertEqual(e["metadata"]["cross_reference_resolution"][x]["status"], "RESOLVED")
                # The parent draft stays uncompiled.
                self.assertIn("SC-VESSEL-001", e["metadata"]["unresolved_cross_references"])
                self.assertNotIn("SC-VESSEL-001", MANIFEST_IDS)
        self.assertIn("SC-TRIAD-SG-001", ENTRIES["SC-VESSEL-SPN-001"]["metadata"]["cross_references"])
        self.assertIn("SC-POE-MRG-001", ENTRIES["SC-VESSEL-CAIN-001"]["metadata"]["cross_references"])

    def test_provisional_defaults_listed(self) -> None:
        pending_doc = (REPO_ROOT / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        for eid in PENDING:
            with self.subTest(eid=eid):
                meta = ENTRIES[eid]["metadata"]
                self.assertIs(meta["pending_deliberation"], True)
                self.assertEqual(meta["deliberation_status"], "PROVISIONAL_DEFAULT")
                self.assertIn(eid.lower(), meta["review_trigger_terms"])
                self.assertIn(eid, pending_doc)
        self.assertNotIn("pending_deliberation", ENTRIES["SC-VESSEL-SW-001"]["metadata"])

    def test_evidence_hashes_and_privacy(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        for name in SOURCES:
            sha = hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest()
            self.assertIn(sha, readme)
            for e in ENTRIES.values():
                self.assertIn(sha, e["metadata"]["source_draft"])
        for name in ("t590u_relayed_summary.md", "t592u_relayed_summary.md"):
            self.assertIn("RELAYED SUMMARY", (EVIDENCE / name).read_text(encoding="utf-8"))
        blob = "\n".join([readme] + [(EVIDENCE / n).read_text(encoding="utf-8") for n in SOURCES]
                         + [json.dumps(e, ensure_ascii=False) for e in ENTRIES.values()])
        # No contact details in the evidence or the entries.
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))


class VesselRoutingTests(unittest.TestCase):
    def test_all_three_are_explicit_only(self) -> None:
        self.assertTrue(set(NEW_IDS) <= EXPLICIT_ONLY_ENTRY_HINTS)

    def test_explicit_ids_route_home(self) -> None:
        for eid in NEW_IDS:
            with self.subTest(eid=eid):
                r = route_domains(f"Explain {eid}.")
                self.assertEqual(r.domain, "soul_bomb_sovereignty")
                summoned = [e.entry_id for e in summon(f"Explain {eid}.", top_k=5).compiled_entries]
                self.assertIn(eid, summoned)

    def test_everyday_words_do_not_lift(self) -> None:
        for text in (
            "The vessel docked at the harbour at noon.",
            "My brother and I watched Supernatural last night.",
            "Luke refuses to fight his father.",
            "Cain and Abel were brothers.",
            "May the Force be with you.",
            "The AI writes code.",
        ):
            with self.subTest(text=text):
                self.assertNotEqual(route_domains(text).domain, "soul_bomb_sovereignty")

    def test_needs_review_fires_for_pending_only(self) -> None:
        for eid in PENDING:
            with self.subTest(eid=eid):
                packet = compile_semantic_packet(f"Explain {eid}.")
                self.assertTrue(packet.needs_review)
                self.assertIn(eid, [x["entry_id"] for x in packet.needs_review_entries])
        for text in ("Explain SC-VESSEL-SW-001.", "Cain and Abel were brothers.", "The AI writes code.", "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertFalse(set(PENDING) & set(ids))


if __name__ == "__main__":
    unittest.main()
