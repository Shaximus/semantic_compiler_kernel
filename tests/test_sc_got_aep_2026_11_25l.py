"""2026-11-25l Archetypal Evolution Principle and Game of Thrones ecosystem (Shax t593u).

SC-AEP-001 (method), SC-GOT-001 (ecosystem hub), SC-GOT-JON-001 (Jon, Bran) and
SC-GOT-MTN-001 (Oberyn, the Mountain): honest grading (tier by rule, no gate above
0.9 without a confirmed prediction), recorded lore corrections with show and books
kept apart, the candidate-not-proof safeguard, short router inputs, explicit-only
routing, the three provisional defaults raising needs_review, the earlier forced
matches listed for re-reading, and a verbatim evidence file with its hash.
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
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-25l"
SOURCE = EVIDENCE / "t593u_message_body.txt"
NEW_IDS = ("SC-AEP-001", "SC-GOT-001", "SC-GOT-JON-001", "SC-GOT-MTN-001")
EXPECTED = {"SC-AEP-001": 0.83, "SC-GOT-001": 0.82, "SC-GOT-JON-001": 0.82, "SC-GOT-MTN-001": 0.832}
PENDING = ("SC-AEP-001", "SC-GOT-001", "SC-GOT-JON-001")


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class GotSchemaAndGradeTests(unittest.TestCase):
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
        src = SOURCE.read_text(encoding="utf-8")
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertLess(len(e["input"]), 400)
                self.assertTrue(e["input"].startswith(eid))
                body = e["v2_extensions"]["source_text"]
                self.assertIn(src, body)
                self.assertGreater(len(body), len(src) + 2000)

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

    def test_layers_kept_separate_and_books_labelled(self) -> None:
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
        self.assertTrue({"CANON", "CANON_BOOKS", "TRADITION", "SHAX_INTERPRETATION", "ANALOGOUS", "COMPILER"} <= grades)

    def test_safeguard_candidate_not_proof(self) -> None:
        aep = ENTRIES["SC-AEP-001"]
        self.assertIn("candidate", aep["input"].lower())
        self.assertIn("not proof", aep["input"].lower())
        self.assertTrue(any("never proof" in g for g in aep["outputs"]["guardrails"]))
        for eid in NEW_IDS:
            with self.subTest(eid=eid):
                reasons = " ".join(ENTRIES[eid]["tier_reasons"])
                self.assertIn("candidate correspondence, not proof", reasons)

    def test_method_tracks_three_things_and_era_vocabulary(self) -> None:
        text = json.dumps(ENTRIES["SC-AEP-001"], ensure_ascii=False)
        for s in ("inheritance", "recombination", "outcome", "royal genealogy", "genetic compatibility",
                  "parasitic symbiosis", "biological reconstruction", "Gen 6:4", "emergent"):
            self.assertIn(s, text)

    def test_earlier_forced_matches_listed_not_rewritten(self) -> None:
        doc = (REPO_ROOT / "docs" / "SC-AEP-001_ARCHETYPAL_EVOLUTION_PRINCIPLE.md").read_text(encoding="utf-8")
        for s in ("Lucifer = Vegeta", "SC-DU-001", "SC-TRIAD-001", "Sukuna", "single being who split", "STARCRAFT_ABILITY_THEOLOGY_MAP", "not rewritten"):
            self.assertIn(s, doc)
        # The earlier entries are untouched by this batch.
        vessel = (REPO_ROOT / "docs" / "SC-VESSEL-001_VESSEL_EQUILIBRIUM.md").read_text(encoding="utf-8")
        self.assertIn("DRAFT 0.5", vessel)
        self.assertNotIn("SC-AEP-001", vessel)

    def test_lore_corrections_recorded(self) -> None:
        jon = ENTRIES["SC-GOT-JON-001"]["outputs"]["correction"]
        for s in ("no Kingsguard bargain", "Night's Watch", "Arya", "Olly", "Elia Martell", "BOOKS"):
            self.assertIn(s, jon)
        mtn = ENTRIES["SC-GOT-MTN-001"]["outputs"]["correction"]
        for s in ("never uses the name Robert Strong", "not confirmed", "kills Qyburn", "Who gave you the order?"):
            self.assertIn(s, mtn)
        hub = ENTRIES["SC-GOT-001"]["outputs"]["correction"]
        for s in ("Children of the Forest made the White Walkers", "Arya", "Viserion", "Night's King"):
            self.assertIn(s, hub)

    def test_consent_and_triad_links(self) -> None:
        for eid in ("SC-GOT-001", "SC-GOT-JON-001", "SC-GOT-MTN-001"):
            with self.subTest(eid=eid):
                xrefs = ENTRIES[eid]["metadata"]["cross_references"]
                for x in ("SC-TRIAD-001", "SC-CONSENT-001", "SC-AEP-001"):
                    self.assertIn(x, xrefs)
                    self.assertEqual(ENTRIES[eid]["metadata"]["cross_reference_resolution"][x]["status"], "RESOLVED")
        self.assertIn("SC-TRIAD-SC-001", ENTRIES["SC-GOT-001"]["metadata"]["cross_references"])
        self.assertIn("SC-TRIAD-SG-001", ENTRIES["SC-GOT-JON-001"]["metadata"]["cross_references"])
        self.assertIn("SC-NEPH-001", ENTRIES["SC-AEP-001"]["metadata"]["unresolved_cross_references"])
        self.assertNotIn("SC-NEPH-001", MANIFEST_IDS)

    def test_provisional_defaults_listed(self) -> None:
        pending_doc = (REPO_ROOT / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        for eid in PENDING:
            with self.subTest(eid=eid):
                meta = ENTRIES[eid]["metadata"]
                self.assertIs(meta["pending_deliberation"], True)
                self.assertEqual(meta["deliberation_status"], "PROVISIONAL_DEFAULT")
                self.assertIn(eid.lower(), meta["review_trigger_terms"])
                self.assertIn(f"## {eid} ", pending_doc)
                self.assertTrue(any(c["tig_grade"] == "PROVISIONAL_DEFAULT" for c in ENTRIES[eid]["analysis"]["claims"]))
        self.assertNotIn("pending_deliberation", ENTRIES["SC-GOT-MTN-001"]["metadata"])

    def test_evidence_hash_and_privacy(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertIn(sha, readme)
        src = SOURCE.read_text(encoding="utf-8")
        self.assertIn("Archetypal Evolution Principle", src)
        self.assertIn("multiple Nephilim archetypes combining", src)
        for e in ENTRIES.values():
            self.assertIn(sha, e["metadata"]["source_draft"])
        blob = "\n".join([readme, src] + [json.dumps(e, ensure_ascii=False) for e in ENTRIES.values()])
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))


class GotRoutingTests(unittest.TestCase):
    def test_all_four_are_explicit_only(self) -> None:
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
            "Winter is coming and the snow is deep on the mountain.",
            "We watched Game of Thrones last night.",
            "The dragon kite flew over the throne room.",
            "Jon Snow knows nothing.",
            "An archetype is a recurring pattern in stories.",
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
        for text in ("Explain SC-GOT-MTN-001.", "Jon Snow knows nothing.", "The AI writes code.", "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertFalse(set(PENDING) & set(ids))


if __name__ == "__main__":
    unittest.main()
