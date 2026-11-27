"""2026-11-26e comparative mythology matrix (Shax t605u/t606u).

Material Shax supplied by pasting a ChatGPT conversation; the analysis is that
assistant's. SC-MYTH-001: Greek / Egyptian / Norse trio as three distinct
legitimacy questions across a ten-field matrix, the Ori worship-power loop as a
self-sourced-legitimacy capture invariant, four other pantheons left open.

Honest grading (tier by rule, no gate above 0.9), source / retelling / Age of
Mythology layers kept apart, citation stubs not treated as sources,
explicit-only routing, the pending ID raising needs_review, and a verbatim
evidence file with its hash.
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
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-26e"
SOURCE = EVIDENCE / "t605u_message_body.txt"
MAP_DOC = REPO_ROOT / "docs" / "AEP_COMPARATIVE_MYTHOLOGY_2026-11-26e.md"
EID = "SC-MYTH-001"
EVIDENCE_SHA = "2626a0c4ea9be1c7312cc1c7b9f1c96395bb88e3abfb4bc5e95ebcbce7f7b809"


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRY = _single(f"{EID}.jsonl")
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class MythSchemaAndGradeTests(unittest.TestCase):
    def test_schema_parity_and_manifest(self) -> None:
        self.assertEqual(list(ENTRY.keys()), list(TEMPLATE.keys()))
        item = next(m for m in MANIFEST["entries"] if m["entry_id"] == EID)
        raw = (COMPILED_DIR / item["file"]).read_bytes()
        self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(item["classification"], ENTRY["dataset_tier"])
        self.assertEqual(len(ENTRY["functional_departments"]), 15)
        for x in ENTRY["metadata"]["cross_references"]:
            self.assertIn(x, MANIFEST_IDS)
        self.assertIn("SC-WORTHY-001", ENTRY["metadata"]["cross_references"])

    def test_short_router_input_and_full_text_in_body(self) -> None:
        src = SOURCE.read_text(encoding="utf-8")
        self.assertLess(len(ENTRY["input"]), 400)
        self.assertTrue(ENTRY["input"].startswith(EID))
        body = ENTRY["v2_extensions"]["source_text"]
        self.assertIn(src, body)
        self.assertGreater(len(body), len(src) + 2000)

    def test_tier_by_rule_no_gold(self) -> None:
        scores = [g["score"] for g in ENTRY["gates"].values()]
        iq = round(math.exp(sum(math.log(s) for s in scores) / len(scores)), 3)
        self.assertEqual(ENTRY["isomorphism_quality"]["score"], iq)
        self.assertEqual(iq, 0.81)
        self.assertEqual(min(scores), 0.75)
        self.assertEqual(ENTRY["dataset_tier"], "SILVER")
        self.assertLessEqual(max(scores), 0.9)
        self.assertTrue(all(g["passed"] for g in ENTRY["gates"].values()))

    def test_layers_kept_separate(self) -> None:
        grades = {layer["grade"] for c in ENTRY["analysis"]["claims"] for layer in c["layers"]}
        self.assertTrue({"CANON", "TRADITION", "LATER_RETELLING", "AOM", "PASTED_ANALYSIS", "COMPILER"} <= grades)
        self.assertTrue(any(g.lower().startswith("do not") for g in ENTRY["outputs"]["guardrails"]))


class MythContentTests(unittest.TestCase):
    def test_trio_and_matrix(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        for s in ("### 6.1 Greek", "### 6.2 Egyptian", "### 6.3 Norse", "## 7. Domain translation",
                  "## 4. The Ori worship-power loop as a capture invariant"):
            self.assertIn(s, doc)

    def test_other_pantheons_left_open(self) -> None:
        doc = MAP_DOC.read_text(encoding="utf-8")
        self.assertIn("## 8. Open", doc)
        for s in ("Chinese", "Japanese", "Aztec"):
            self.assertIn(s, doc)

    def test_boundary_recurrence_not_history(self) -> None:
        g = " ".join(ENTRY["outputs"]["guardrails"])
        self.assertIn("recurrence", g)
        self.assertIn("citation stubs", g)

    def test_attribution_and_catherine(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        self.assertIn("ChatGPT", readme)
        self.assertIn("not by Shax", readme)
        doc = MAP_DOC.read_text(encoding="utf-8")
        self.assertIn("Catherine remains unresolved", doc)
        self.assertNotIn("if present", doc)

    def test_provisional_default_listed(self) -> None:
        pending_doc = (REPO_ROOT / "docs" / "PENDING_DELIBERATION.md").read_text(encoding="utf-8")
        meta = ENTRY["metadata"]
        self.assertIs(meta["pending_deliberation"], True)
        self.assertEqual(meta["deliberation_status"], "PROVISIONAL_DEFAULT")
        self.assertIn(EID.lower(), meta["review_trigger_terms"])
        self.assertIn(f"## {EID} ", pending_doc)

    def test_evidence_hash_and_privacy(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        raw = SOURCE.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(sha, EVIDENCE_SHA)
        self.assertIn(sha, readme)
        self.assertIn(str(len(raw)), readme)
        src = raw.decode("utf-8")
        self.assertTrue(src.startswith("[t605u"))
        self.assertIn(sha, ENTRY["metadata"]["source_draft"])
        blob = "\n".join([readme, src, MAP_DOC.read_text(encoding="utf-8"), json.dumps(ENTRY, ensure_ascii=False)])
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", blob))
        self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", blob))


class MythRoutingTests(unittest.TestCase):
    def test_entry_is_explicit_only(self) -> None:
        self.assertIn(EID, EXPLICIT_ONLY_ENTRY_HINTS)

    def test_explicit_id_routes_home(self) -> None:
        r = route_domains(f"Explain {EID}.")
        self.assertEqual(r.domain, "soul_bomb_sovereignty")
        self.assertIn(EID, [e.entry_id for e in summon(f"Explain {EID}.", top_k=5).compiled_entries])

    def test_everyday_words_do_not_lift(self) -> None:
        for text in ("I love Greek mythology and Zeus.", "Odin and Thor in the Ragnarok movie were fun.",
                     "Who were the Titans?", "Age of Mythology is my favourite game.",
                     "remind me to call mom at 6"):
            with self.subTest(text=text):
                self.assertNotEqual(route_domains(text).domain, "soul_bomb_sovereignty")

    def test_needs_review_fires_for_explicit_id_only(self) -> None:
        packet = compile_semantic_packet(f"Explain {EID}.")
        self.assertTrue(packet.needs_review)
        self.assertIn(EID, [x["entry_id"] for x in packet.needs_review_entries])
        for text in ("Explain SC-WORTHY-001.", "I love Greek mythology and Zeus.", "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertNotIn(EID, ids)


if __name__ == "__main__":
    unittest.main()
