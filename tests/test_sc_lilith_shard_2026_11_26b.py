"""2026-11-26b Lilith layers, feminine lineage, and Usurped-Shard (Shax t598u).

SC-LILITH-001: sourced historical layers, kept apart.
SC-FEM-001: archetypal lineage scored under SC-AEP-001 only; three hypotheses
not collapsed; Catherine / near-creation slot is a provisional default.
SC-SHARD-001: Usurped-Shard / Captured-Collective pattern; Zerg versus Goa'uld
mechanisms; ownership confusion; the pasted audit is truncated after 2.3;
throne-versus-fracture is a provisional default.

Honest grading (tier by rule, no gate above 0.9 without a confirmed prediction),
short router input, explicit-only routing, pending IDs raising needs_review,
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
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-26b"
SOURCE = EVIDENCE / "t598u_message_body.txt"
MAP_DOC = REPO_ROOT / "docs" / "LILITH_LINEAGE_AND_USURPED_SHARD_2026-11-26b.md"
NEW_IDS = ("SC-LILITH-001", "SC-FEM-001", "SC-SHARD-001")
EXPECTED = {"SC-LILITH-001": 0.832, "SC-FEM-001": 0.821, "SC-SHARD-001": 0.838}
PENDING = ("SC-FEM-001", "SC-SHARD-001")
NOT_PENDING = ("SC-LILITH-001",)
EVIDENCE_SHA = "fac583d94fff10873a3b136570a9af7f958711afa4443b39f8898037ab41c9ea"


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class LilithShardSchemaAndGradeTests(unittest.TestCase):
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
            self.assertTrue(any(g.lower().startswith("do not") for g in e["outputs"]["guardrails"]))
            self.assertIn("candidate correspondence, not proof", " ".join(e["tier_reasons"]))
        self.assertTrue({"CANON", "TRADITION", "SHAX_INTERPRETATION", "ANALOGOUS", "COMPILER"} <= grades)


class LilithShardContentTests(unittest.TestCase):
    def test_lilith_layers_and_corrections(self) -> None:
        e = ENTRIES["SC-LILITH-001"]
        body = e["v2_extensions"]["source_text"]
        corr = e["outputs"]["correction"]
        for s in ("lilītu", "ardat-lilī", "Isaiah 34:14", "incantation bowls",
                  "Alphabet of Ben Sira", "Treatise on the Left Emanation",
                  "Isaac ha-Kohen", "Samael", "not interchangeable in every historical source",
                  "another incarnation of Satan", "not an established doctrine"):
            self.assertIn(s, body)
        self.assertIn("Genesis does not name Lilith", corr)
        self.assertIn("demonic layer is earlier", corr)
        self.assertIn("8th-10th century", corr)
        self.assertIn("Lilith the Elder", corr)
        self.assertIn("Naamah is a separate figure", corr)
        self.assertNotIn("pending_deliberation", e["metadata"])

    def test_feminine_lineage_hypotheses_and_catherine(self) -> None:
        body = ENTRIES["SC-FEM-001"]["v2_extensions"]["source_text"]
        corr = ENTRIES["SC-FEM-001"]["outputs"]["correction"]
        for s in ("Ontological", "Archetypal", "Relational",
                  "same primordial soul", "Not canon",
                  "Proverbs 8", "1 Cor 1:24",
                  "Justin Martyr", "Irenaeus", "New Eve",
                  "Catherine of Alexandria", "near the beginning of creation",
                  "do not invent a creation-era Catherine"):
            self.assertIn(s, body)
        self.assertIn("No tradition was found that places any Catherine", corr)
        self.assertIn("typology, not identity", corr)
        for x in ("SC-AEP-001", "SC-LILITH-001"):
            self.assertIn(x, ENTRIES["SC-FEM-001"]["metadata"]["cross_references"])

    def test_shard_stages_lore_and_truncation(self) -> None:
        body = ENTRIES["SC-SHARD-001"]["v2_extensions"]["source_text"]
        corr = ENTRIES["SC-SHARD-001"]["outputs"]["correction"]
        for s in ("Five stages", "ownership confusion",
                  "control-plane capture", "vessel capture",
                  "engineered the Overmind", "Queen of Blades", "Primal Zerg",
                  "Zerus", "Dehaka", "genetic memory is vertical",
                  "Sarcophagus", "Oma Desala", "Egeria", "Tok'ra",
                  "truncated", "restoration test"):
            self.assertIn(s, body)
        self.assertIn("Amon engineered it", corr)
        self.assertIn("not shards of one primordial consciousness", corr)
        self.assertIn("truncated at the colon after section 2.3", corr)
        self.assertIn("missing remainder is not invented", corr)
        for x in ("SC-GUARD-001", "SC-CONSENT-001", "SC-TRIAD-SG-001"):
            self.assertIn(x, ENTRIES["SC-SHARD-001"]["metadata"]["cross_references"])

    def test_map_doc_covers_brief(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        for s in ("SC-LILITH-001", "SC-FEM-001", "SC-SHARD-001",
                  "Isaiah 34:14", "Alphabet of Ben Sira",
                  "Treatise on the Left Emanation", "Samael is not uniformly Satan",
                  "Three hypotheses", "Catherine of Alexandria",
                  "No tradition was found", "ownership confusion",
                  "control-plane capture", "vessel capture",
                  "truncated at the colon", "fragmentation plus a feedback break"):
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
        for eid in NOT_PENDING:
            with self.subTest(eid=eid):
                self.assertNotIn("pending_deliberation", ENTRIES[eid]["metadata"])

    def test_evidence_hash_theory_text_and_privacy(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        raw = SOURCE.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(sha, EVIDENCE_SHA)
        self.assertIn(sha, readme)
        src = raw.decode("utf-8")
        self.assertIn("Isaiah 34:14", src)
        self.assertIn("same primordial soul", src)
        self.assertIn("ownership confusion", src)
        self.assertIn("Your pasted section ends at the colon after 2.3", src)
        self.assertIn("The pasted audit is truncated here, at the colon after section 2.3", src)
        self.assertNotIn("http", src)
        self.assertNotIn("openai.com", src)
        for e in ENTRIES.values():
            self.assertIn(sha, e["metadata"]["source_draft"])
        blob = "\n".join([readme, src, MAP_DOC.read_text(encoding="utf-8")] + [json.dumps(e, ensure_ascii=False) for e in ENTRIES.values()])
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))


class LilithShardRoutingTests(unittest.TestCase):
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
            "The museum catalog lists a lilith figure next to eve and mary.",
            "Sophia asked Catherine about wisdom class.",
            "The zerg rushed the natural and claimed the throne.",
            "That vessel needs a new gasket.",
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
        lilith = compile_semantic_packet("Explain SC-LILITH-001.")
        self.assertNotIn("SC-LILITH-001", [x["entry_id"] for x in (lilith.needs_review_entries or [])])
        for text in ("Explain SC-WOW-RES-001.", "Explain SC-GOT-MTN-001.",
                     "The zerg rushed the natural and claimed the throne.",
                     "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertFalse(set(PENDING) & set(ids))


if __name__ == "__main__":
    unittest.main()
