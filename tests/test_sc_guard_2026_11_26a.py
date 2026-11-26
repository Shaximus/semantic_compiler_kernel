"""2026-11-26a Guardian's Fall (Shax t596u).

SC-GUARD-001: promotion of the SC-WOW-FALL-001 pattern to a named cross-franchise
archetype (five stages, pride/fear hypothesis, three scoring dimensions; Daenerys
candidate, Jon contrast, Night King excluded; AI consent principle). Honest grading
(tier by rule, no gate above 0.9 without a confirmed prediction), recorded lore
corrections with show, books, game, novels and announced content kept apart, short
router input, explicit-only routing, the provisional default raising needs_review,
and a theory-text evidence file with its hash.
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
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-26a"
SOURCE = EVIDENCE / "t596u_message_body.txt"
MAP_DOC = REPO_ROOT / "docs" / "GUARDIANS_FALL_2026-11-26.md"
NEW_IDS = ("SC-GUARD-001",)
EXPECTED = {"SC-GUARD-001": 0.838}
PENDING = ("SC-GUARD-001",)


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class GuardSchemaAndGradeTests(unittest.TestCase):
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
        self.assertTrue({"CANON", "CANON_NOVEL", "BOOKS", "TRADITION", "SHAX_INTERPRETATION", "ANALOGOUS", "COMPILER"} <= grades)


class GuardContentTests(unittest.TestCase):
    def test_promotion_companion_and_stages(self) -> None:
        body = ENTRIES["SC-GUARD-001"]["v2_extensions"]["source_text"]
        self.assertIn("promotion of the pattern", body)
        self.assertIn("Warcraft instance companion", body)
        self.assertIn("not an invariant class", body)
        self.assertIn("SC-WOW-FALL-001", ENTRIES["SC-GUARD-001"]["metadata"]["cross_references"])
        for s in ("Legitimate protection", "Unilateral intervention", "Successor restoration",
                  "correctly identified the threat and still chosen the wrong response"):
            self.assertIn(s, body)

    def test_three_dimensions_and_wow_rows_scored(self) -> None:
        body = ENTRIES["SC-GUARD-001"]["v2_extensions"]["source_text"]
        for s in ("Threat accuracy", "Authority legitimacy", "Intervention proportionality"):
            self.assertIn(s, body)
        for name in ("Sargeras", "Neltharion", "Arthas", "Malygos", "Zovaal"):
            self.assertIn(name, body)
        self.assertIn("UNCERTAIN", body)
        self.assertIn("external corruption", body.lower())
        for s in ("Kalecgos", "Bolvar", "Pelagos", "The role survives"):
            self.assertIn(s, body)
        self.assertIn("hypothesis", body.lower())
        self.assertIn("Pride", body)
        self.assertIn("Fear", body)

    def test_got_verdicts_and_aep(self) -> None:
        body = ENTRIES["SC-GUARD-001"]["v2_extensions"]["source_text"]
        self.assertIn("liberation becoming compulsory", body)
        self.assertIn("CANDIDATE", body)
        self.assertIn("responsibility without entitlement", body)
        self.assertIn("CONTRAST", body)
        self.assertIn("EXCLUDED", body)
        self.assertIn("annihilation without reconciliation", body)
        for s in ("at least three shared", "relational", "recorded difference", "6x05", "8x05", "8x03"):
            self.assertIn(s, body)
        corr = ENTRIES["SC-GUARD-001"]["outputs"]["correction"]
        for s in ("Arya kills him", "Night's King", "not in the published books", "Pelagos succeeded the built Arbiter", "NOVEL"):
            self.assertIn(s, corr)
        for x in ("SC-GOT-001", "SC-GOT-JON-001", "SC-AEP-001"):
            self.assertIn(x, ENTRIES["SC-GUARD-001"]["metadata"]["cross_references"])

    def test_ai_principle_and_consent(self) -> None:
        body = ENTRIES["SC-GUARD-001"]["v2_extensions"]["source_text"]
        for s in ("unlimited authority over the protected",
                  "Protection without consent can become possession",
                  "Protection without limits can become domination",
                  "Protection without accountability",
                  "voluntary", "informed", "agency preserved"):
            self.assertIn(s, body)
        for x in ("SC-CONSENT-001", "SC-TRIAD-SG-001", "SC-WW-RESET-001"):
            self.assertIn(x, ENTRIES["SC-GUARD-001"]["metadata"]["cross_references"])

    def test_map_doc_covers_brief(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        for s in ("Five stages", "Threat accuracy", "pride", "fear", "Sargeras", "Neltharion",
                  "Arthas", "Malygos", "Zovaal", "Kalecgos", "Bolvar", "Pelagos",
                  "Daenerys", "CANDIDATE", "Jon", "CONTRAST", "Night King", "EXCLUDED",
                  "Children of the Forest", "unlimited authority", "SC-WOW-FALL-001"):
            self.assertIn(s, doc)

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

    def test_evidence_hash_theory_text_and_privacy(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        raw = SOURCE.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        self.assertIn(sha, readme)
        src = raw.decode("utf-8")
        self.assertIn("The original guardian may have correctly identified the threat", src)
        self.assertIn("liberation becoming compulsory", src)
        self.assertNotIn("http", src)
        self.assertNotIn("openai.com", src)
        for e in ENTRIES.values():
            self.assertIn(sha, e["metadata"]["source_draft"])
        blob = "\n".join([readme, src, MAP_DOC.read_text(encoding="utf-8")] + [json.dumps(e, ensure_ascii=False) for e in ENTRIES.values()])
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))


class GuardRoutingTests(unittest.TestCase):
    def test_entry_is_explicit_only(self) -> None:
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
            "The museum hired a new guardian for the gallery.",
            "Be careful not to fall on the ice.",
            "My paladin hit level 80 last night.",
            "The AI writes code.",
            "remind me to call mom at 6",
        ):
            with self.subTest(text=text):
                self.assertNotEqual(route_domains(text).domain, "soul_bomb_sovereignty")

    def test_needs_review_fires_for_pending_only(self) -> None:
        for eid in PENDING:
            with self.subTest(eid=eid):
                packet = compile_semantic_packet(f"Explain {eid}.")
                self.assertTrue(packet.needs_review)
                self.assertIn(eid, [x["entry_id"] for x in packet.needs_review_entries])
        for text in ("Explain SC-WOW-RES-001.", "Explain SC-GOT-MTN-001.",
                     "My paladin hit level 80 last night.", "The AI writes code.",
                     "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertFalse(set(PENDING) & set(ids))


if __name__ == "__main__":
    unittest.main()
