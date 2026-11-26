"""2026-11-25m World of Warcraft through theology (Shax t594u).

SC-WOW-001 (cosmology hub), SC-WOW-DF-001 (Dragonflight and the Tok'ra/Goa'uld consent
split), SC-WOW-CLASS-001 (thirteen classes), SC-WOW-RES-001 (resurrection range) and
SC-WOW-FALL-001 (the guardian's fall): honest grading (tier by rule, no gate above 0.9
without a confirmed prediction), recorded lore corrections with game, novel and announced
content kept apart, the candidate-not-proof safeguard, short router inputs, explicit-only
routing, the four provisional defaults raising needs_review, and a verbatim evidence file
with its hash.
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
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-25m"
SOURCE = EVIDENCE / "t594u_message_body.txt"
MAP_DOC = REPO_ROOT / "docs" / "WOW_THEOLOGY_MAP.md"
NEW_IDS = ("SC-WOW-001", "SC-WOW-DF-001", "SC-WOW-CLASS-001", "SC-WOW-RES-001", "SC-WOW-FALL-001")
EXPECTED = {"SC-WOW-001": 0.82, "SC-WOW-DF-001": 0.838, "SC-WOW-CLASS-001": 0.82,
            "SC-WOW-RES-001": 0.843, "SC-WOW-FALL-001": 0.826}
PENDING = ("SC-WOW-001", "SC-WOW-DF-001", "SC-WOW-CLASS-001", "SC-WOW-FALL-001")
CLASSES = ("Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Death Knight", "Shaman", "Mage",
           "Warlock", "Monk", "Druid", "Demon Hunter", "Evoker")


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class WowSchemaAndGradeTests(unittest.TestCase):
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
            self.assertIn("candidate correspondence, not proof", " ".join(e["tier_reasons"]))
        self.assertTrue({"CANON", "CANON_NOVEL", "ANNOUNCED", "TRADITION", "SHAX_INTERPRETATION", "ANALOGOUS", "COMPILER"} <= grades)


class WowContentTests(unittest.TestCase):
    def test_all_thirteen_classes_and_devourer(self) -> None:
        text = ENTRIES["SC-WOW-CLASS-001"]["v2_extensions"]["source_text"]
        for c in CLASSES:
            self.assertIn(f"| {c} |", text)
        self.assertIn("Devourer", text)
        self.assertIn("NAME_BORROWING", text)
        self.assertIn("SC-SCA-CONS-001", ENTRIES["SC-WOW-CLASS-001"]["metadata"]["cross_references"])

    def test_dragonflight_shax_framing_and_breaks(self) -> None:
        df = ENTRIES["SC-WOW-DF-001"]
        body = df["v2_extensions"]["source_text"]
        self.assertIn("the good Tok'ra versus the bad ghouls", body)
        for s in ("Oathbinder", "proto-dragon eggs", "Nasz'uro", "Vyranoth", "Iridikron", "Murozond", "Azeroth herself"):
            self.assertIn(s, body)
        corr = df["outputs"]["correction"]
        for s in ("from Azeroth herself", "not from the titans", "Ebyssian", "Nyxondra", "Iridikron was not defeated", "NOVEL"):
            self.assertIn(s, corr)
        for x in ("SC-TRIAD-SG-001", "SC-CONSENT-001", "SC-SCC-001"):
            self.assertIn(x, df["metadata"]["cross_references"])

    def test_triad_holds_and_breaks_recorded(self) -> None:
        body = ENTRIES["SC-WOW-001"]["v2_extensions"]["source_text"]
        for s in ("## Holds", "## Breaks", "Titans / Old Gods / Jailer", "Order / Void / Death", "re-origination", "weapon of tyranny"):
            self.assertIn(s, body)
        corr = ENTRIES["SC-WOW-001"]["outputs"]["correction"]
        for s in ("judge of souls, not an afterlife", "sealed, not killed", "ANNOUNCED"):
            self.assertIn(s, corr)

    def test_resurrection_range_and_consent(self) -> None:
        body = ENTRIES["SC-WOW-RES-001"]["v2_extensions"]["source_text"]
        for s in ("Light's Hope", "Bolvar", "Forsaken", "Sylvanas", "Arthas", "Illidan", "1 Sam 28", "SC-GOT-MTN-001"):
            self.assertIn(s, body)
        self.assertIn("Arthas was not raised", ENTRIES["SC-WOW-RES-001"]["outputs"]["correction"])
        self.assertNotIn("pending_deliberation", ENTRIES["SC-WOW-RES-001"]["metadata"])

    def test_guardian_fall_instances_and_exclusions(self) -> None:
        body = ENTRIES["SC-WOW-FALL-001"]["v2_extensions"]["source_text"]
        for s in ("Sargeras", "Zovaal", "Neltharion", "Arthas", "Malygos", "PARTIAL", "EXCLUDED", "1 Sam 13:11-12", "voluntary successor"):
            self.assertIn(s, body)

    def test_map_doc_covers_brief(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        for s in ("Ragnaros", "Nefarian", "Onyxia", "C'Thun", "Kel'Thuzad", "Illidan", "Kil'jaeden", "Lich King", "Yogg-Saron",
                  "Deathwing", "Garrosh", "Archimonde", "Gul'dan", "Argus", "N'Zoth", "Sylvanas", "Jailer", "Fyrakk", "Raszageth",
                  "Primalists", "Iridikron", "Xal'atath", "Ansurek", "Dimensius", "The Last Titan", "Midnight"):
            self.assertIn(s, doc)
        for c in CLASSES:
            self.assertIn(c, doc)

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

    def test_evidence_hash_verbatim_and_privacy(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        raw = SOURCE.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        self.assertIn(sha, readme)
        src = raw.decode("utf-8")
        self.assertIn("the good Tok'ra versus the bad ghouls", src)
        self.assertIn("dragonflight", src)
        for e in ENTRIES.values():
            self.assertIn(sha, e["metadata"]["source_draft"])
        blob = "\n".join([readme, src, MAP_DOC.read_text(encoding="utf-8")] + [json.dumps(e, ensure_ascii=False) for e in ENTRIES.values()])
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))
        self.assertNotRegex(blob.lower(), r"rank(ed)? 1\d|mythic\+ rating of shax|world rank")


class WowRoutingTests(unittest.TestCase):
    def test_all_five_are_explicit_only(self) -> None:
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
            "My paladin hit level 80 last night.",
            "The dragon kite flew over the field.",
            "I play a hunter in World of Warcraft.",
            "The titans of industry met in Davos.",
            "remind me to call mom at 6",
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
        for text in ("Explain SC-WOW-RES-001.", "My paladin hit level 80 last night.", "The AI writes code.", "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertFalse(set(PENDING) & set(ids))


if __name__ == "__main__":
    unittest.main()
