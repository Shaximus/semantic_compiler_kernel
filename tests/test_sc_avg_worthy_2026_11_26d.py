"""2026-11-26d Avengers × Diablo II × Path of Exile AEP map (t603u).

Material Shax supplied by pasting a ChatGPT conversation; the analysis is that
assistant's. SC-AVG-001: the map (specialization gate, party composition,
interpretive per-Avenger tables, Groot no forced match, Vision as a vessel with
agency, open extensions not done). SC-WORTHY-001: capability is not legitimate
authority (Ghrab Thaar checked; Mjölnir unverified from paste; SCC-001-AC PR #95).

Honest grading (tier by rule, no gate above 0.9 without a confirmed prediction),
canon / tradition / interpretation layers kept apart, citation stubs not treated
as sources, explicit-only routing, pending IDs raising needs_review, and a
verbatim evidence file with its hash.
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
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-26d"
SOURCE = EVIDENCE / "t603u_message_body.txt"
MAP_DOC = REPO_ROOT / "docs" / "AVENGERS_D2_POE_AEP_MAP_2026-11-26d.md"
NEW_IDS = ("SC-AVG-001", "SC-WORTHY-001")
EXPECTED = {"SC-AVG-001": 0.813, "SC-WORTHY-001": 0.822}
EVIDENCE_SHA = "9ee6ad562a66d86020686f29f14bec9fd95550ae7adebdd7320f175003d654ca"
STUBS = ("DIABLO II +1", "Fandom +1", "PoE Source +1")


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class AvgWorthySchemaAndGradeTests(unittest.TestCase):
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
        self.assertEqual(len(MANIFEST["entries"]), 64)  # +SC-MYTH-001 (2026-11-26e)
        self.assertEqual(sum(1 for m in MANIFEST["entries"] if m["classification"] == "GOLD"), 11)

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
            self.assertTrue(any(g.lower().startswith("do not") for g in e["outputs"]["guardrails"]))
            self.assertIn("candidate correspondence, not proof", " ".join(e["tier_reasons"]))
        self.assertTrue({"CANON_VERIFIED", "SECONDARY_VERIFIED", "CANON_UNVERIFIED_FROM_PASTE",
                         "TRADITION_UNVERIFIED_FROM_PASTE", "PASTED_ASSISTANT_INTERPRETATION",
                         "COMPILER"} <= grades)


class AvgWorthyContentTests(unittest.TestCase):
    def test_three_invariants(self) -> None:
        body = ENTRIES["SC-AVG-001"]["v2_extensions"]["source_text"]
        for s in ("Worthiness invariant: capability is not legitimate authority",
                  "Specialization-gate invariant", "Party-composition invariant",
                  "capability is not function, and function is not authority",
                  "Labyrinth", "distributed build", "SCC-001-AC path 1, PR #95"):
            self.assertIn(s, body)

    def test_interpretive_tables_not_official(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        self.assertIn("not official Marvel or Blizzard classifications", doc)
        self.assertIn("not official Marvel or GGG classifications", doc)
        self.assertIn("no claim of derivation", doc)
        for name in ("Thor", "Captain America", "Iron Man", "Hulk", "Black Widow", "Hawkeye",
                     "Scarlet Witch", "Doctor Strange", "Vision", "Loki", "Groot", "Shang-Chi"):
            self.assertRegex(doc, rf"\| {re.escape(name)} \|.*\| INTERPRETIVE|\| {re.escape(name)} \|.*NO_FORCED_MATCH")

    def test_groot_no_forced_match_and_vision_vessel(self) -> None:
        e = ENTRIES["SC-AVG-001"]
        body = e["v2_extensions"]["source_text"]
        self.assertIn("NO_FORCED_MATCH", body)
        self.assertIn("PoE 1 has no Druid starting class", body)
        self.assertIn("Groot", e["outputs"]["correction"])
        self.assertIn("constructed vessel with independent agency", body)
        self.assertIn("not equipment", body)
        self.assertNotIn("Druid", [line.split("|")[1].strip() for line in body.splitlines()
                                   if line.startswith("| Druid ")] or ["x"])

    def test_open_extensions_not_done(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        self.assertIn("**Villain roster.**", doc)
        self.assertIn("**Nephilim collective structure.**", doc)
        self.assertEqual(doc.count("NOT DONE."), 2)
        self.assertIn("SC-NEPH-001", ENTRIES["SC-AVG-001"]["metadata"]["unresolved_cross_references"])
        self.assertEqual(ENTRIES["SC-AVG-001"]["metadata"]["cross_reference_resolution"]["SC-NEPH-001"]["status"], "NAMED_NOT_PRESENT")

    def test_worthiness_canon_and_correction(self) -> None:
        e = ENTRIES["SC-WORTHY-001"]
        body = e["v2_extensions"]["source_text"]
        corr = e["outputs"]["correction"]
        self.assertIn("CANON_VERIFIED", body)
        self.assertIn("The Arreat Summit", body)
        self.assertIn("prove himself worthy of victory", body)
        self.assertIn("relic is destroyed", corr)
        self.assertIn("unverified from paste", corr)
        for x in ("SC-SHARD-001", "SC-GUARD-001", "SC-AEP-001"):
            self.assertIn(x, e["metadata"]["cross_references"])
        self.assertIn("PR #95", body)
        self.assertNotIn("SCC-001-AC", e["metadata"]["cross_references"])

    def test_citation_stubs_marked_unverified(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        for s in STUBS:
            self.assertIn(s, doc)
            self.assertIn(s, readme)
        self.assertIn("citation stubs", doc)
        self.assertIn("UNVERIFIED_FROM_PASTE", doc)
        for e in ENTRIES.values():
            self.assertTrue(any("citation stub" in g for g in e["outputs"]["guardrails"]) or "citation stub" in e["outputs"]["correction"])

    def test_attribution_pasted_assistant(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        self.assertIn("pasted it from a ChatGPT conversation", readme)
        self.assertIn("not by Shax", readme)
        self.assertIn("Inline image embeds (poster and class-art URLs) are omitted", readme)
        for e in ENTRIES.values():
            self.assertIn("pasted from a ChatGPT conversation", e["metadata"]["source_draft"])

    def test_provisional_defaults_listed(self) -> None:
        pending_doc = (REPO_ROOT / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        for eid in NEW_IDS:
            with self.subTest(eid=eid):
                meta = ENTRIES[eid]["metadata"]
                self.assertIs(meta["pending_deliberation"], True)
                self.assertEqual(meta["deliberation_status"], "PROVISIONAL_DEFAULT")
                self.assertIn(eid.lower(), meta["review_trigger_terms"])
                self.assertIn(f"## {eid} ", pending_doc)
                self.assertTrue(any(c["tig_grade"] == "PROVISIONAL_DEFAULT" for c in ENTRIES[eid]["analysis"]["claims"]))

    def test_evidence_hash_and_privacy(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        raw = SOURCE.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(sha, EVIDENCE_SHA)
        self.assertIn(sha, readme)
        self.assertIn(str(len(raw)), readme)
        src = raw.decode("utf-8")
        self.assertTrue(src.startswith("[t603u"))
        self.assertIn("inline image embeds", src.splitlines()[0])
        self.assertIn("Hammer of Ghrab Thaar", src)
        self.assertIn("I wouldn't force a perfect match", src)
        self.assertNotIn("http", src)
        for e in ENTRIES.values():
            self.assertIn(sha, e["metadata"]["source_draft"])
        blob = "\n".join([readme, src, MAP_DOC.read_text(encoding="utf-8")] + [json.dumps(e, ensure_ascii=False) for e in ENTRIES.values()])
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))


class AvgWorthyRoutingTests(unittest.TestCase):
    def test_entries_are_explicit_only(self) -> None:
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
            "We watched the Avengers movie and Thor's hammer was great.",
            "My paladin build in Diablo needs a better hammer.",
            "Which Path of Exile class should I pick for my first party?",
            "Is he worthy of the promotion?",
            "remind me to call mom at 6",
        ):
            with self.subTest(text=text):
                self.assertNotEqual(route_domains(text).domain, "soul_bomb_sovereignty")

    def test_needs_review_fires_for_explicit_ids_only(self) -> None:
        for eid in NEW_IDS:
            with self.subTest(eid=eid):
                packet = compile_semantic_packet(f"Explain {eid}.")
                self.assertTrue(packet.needs_review)
                self.assertIn(eid, [x["entry_id"] for x in packet.needs_review_entries])
        for text in ("Explain SC-WOW-RES-001.", "Explain SC-GOT-MTN-001.",
                     "My paladin build in Diablo needs a better hammer.",
                     "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertFalse(set(NEW_IDS) & set(ids))


if __name__ == "__main__":
    unittest.main()
