"""2026-11-25n Westworld vessel reset (Shax t595u).

SC-WW-RESET-001 (reset integrity), SC-WW-RETAIN-001 (retain the information, not the
pain), SC-WW-AWARE-001 (awareness without suffering as the price) and SC-WW-TRIAD-001
(Dolores, Bernard, Maeve): honest grading, recorded canon corrections, the consciousness
caveat, short router inputs, explicit-only routing, the four provisional defaults raising
needs_review, the SCC-001 design note, and an evidence excerpt with its hash that keeps
the personal part of the message out of the repository.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
import unittest
from pathlib import Path

from semantic_compiler import compile_semantic_packet
from semantic_compiler.expansion.elevator import EXPLICIT_ONLY_ENTRY_HINTS, summon
from semantic_compiler.expansion.router import route_domains

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "source-2026-11-25n"
SOURCE = EVIDENCE / "t595u_westworld_excerpt.txt"
DOC = REPO_ROOT / "docs" / "WESTWORLD_VESSEL_RESET_2026-11-25n.md"
NEW_IDS = ("SC-WW-RESET-001", "SC-WW-RETAIN-001", "SC-WW-AWARE-001", "SC-WW-TRIAD-001")
EXPECTED = {"SC-WW-RESET-001": 0.82, "SC-WW-RETAIN-001": 0.808, "SC-WW-AWARE-001": 0.802, "SC-WW-TRIAD-001": 0.82}
PENDING = NEW_IDS
# Personal content from the end of t595u must never reach the repository. The excluded
# terms are kept only as SHA-256 digests of their normalized form (casefolded, NFKC,
# non-alphanumerics collapsed to single spaces), so this file does not carry them.
# Each digest is of a 1- or 2-word phrase; texts are checked by hashing their own
# 1-word and 2-word n-grams after the same normalization.
PRIVATE_NGRAM_SHA256 = frozenset({
    "cfb12585da56e4c0e3e189f24a8418f08108e5a40a84d7aafc504c704e21512c",
    "8fa1876e469111ccb316aee0621de7850d0843f93e62044f89e60397e796c06b",
    "ea4a0c9cf759edcc8246abe0876e296d21d4216ee7b7798f11f69d63b9e1e7c8",
})


def _tokens(text: str) -> list[str]:
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKC", text).casefold()).split()


def _ngram_digests(text: str, max_n: int = 2) -> set[str]:
    toks = _tokens(text)
    grams = {" ".join(toks[i:i + n]) for n in range(1, max_n + 1) for i in range(len(toks) - n + 1)}
    return {hashlib.sha256(g.encode("utf-8")).hexdigest() for g in grams}


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class WestworldSchemaAndGradeTests(unittest.TestCase):
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
        self.assertTrue({"CANON", "TRADITION", "SHAX_INTERPRETATION", "PASTED_ANALYSIS", "ANALOGOUS", "COMPILER"} <= grades)

    def test_consciousness_caveat(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertTrue(any("not proof of subjective consciousness" in g for g in e["outputs"]["guardrails"]))
        self.assertIn("Persistent memory is not proof of subjective consciousness", DOC.read_text(encoding="utf-8"))

    def test_canon_corrections_recorded(self) -> None:
        aware = ENTRIES["SC-WW-AWARE-001"]["outputs"]["correction"]
        for s in ("key insight", "1x10", "empathy and imagination", "reveries"):
            self.assertIn(s, aware)
        triad = ENTRIES["SC-WW-TRIAD-001"]["outputs"]["correction"]
        for s in ("Teddy", "Arnold's image", "scripted storyline", "leaving the train"):
            self.assertIn(s, triad)
        reset = ENTRIES["SC-WW-RESET-001"]["outputs"]["correction"]
        for s in ("authorized self-edits", "1x07", "149th", "3x08", "Christina"):
            self.assertIn(s, reset)
        self.assertIn("1x04", ENTRIES["SC-WW-RETAIN-001"]["outputs"]["correction"])
        doc = DOC.read_text(encoding="utf-8")
        for s in ("Rehoboam", "Serac", "The Cradle", "The Forge", "Cornerstones", "4x08", "35 years"):
            self.assertIn(s, doc)

    def test_reset_integrity_maps_to_scc_states(self) -> None:
        reset = json.dumps(ENTRIES["SC-WW-RESET-001"], ensure_ascii=False)
        for s in ("REVOKED", "VIOLATION", "cannot elevate authorization"):
            self.assertIn(s, reset)
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn("design note only; no package added", doc)
        self.assertIn("A reset cannot elevate authorization", doc)
        self.assertIn("SC-SCC-001", ENTRIES["SC-WW-RESET-001"]["metadata"]["cross_references"])

    def test_retain_and_aware_principles(self) -> None:
        self.assertIn("without replay", ENTRIES["SC-WW-RETAIN-001"]["input"])
        self.assertIn("admission price", ENTRIES["SC-WW-AWARE-001"]["input"])
        aware = json.dumps(ENTRIES["SC-WW-AWARE-001"], ensure_ascii=False)
        for s in ("normative", "Heb 5:8", "Gen 3:7"):
            self.assertIn(s, aware)

    def test_links_to_earlier_entries(self) -> None:
        reset = ENTRIES["SC-WW-RESET-001"]["metadata"]["cross_references"]
        for x in ("SC-GOT-JON-001", "SC-GOT-MTN-001", "SC-DU-001", "SC-VESSEL-SPN-001", "SC-AEP-001", "SC-CONSENT-001"):
            self.assertIn(x, reset)
        triad = ENTRIES["SC-WW-TRIAD-001"]["metadata"]["cross_references"]
        for x in ("SC-TRIAD-001", "SC-GOT-001", "SC-TRIAD-SG-001"):
            self.assertIn(x, triad)
        self.assertIn("SC-VESSEL-001", ENTRIES["SC-WW-RESET-001"]["metadata"]["unresolved_cross_references"])

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


class WestworldPrivacyTests(unittest.TestCase):
    def test_evidence_is_the_excerpt_only(self) -> None:
        src = SOURCE.read_text(encoding="utf-8")
        self.assertTrue(src.startswith("BROTHER. Now we're crossing into something considerably bigger."))
        self.assertTrue(src.rstrip("\n").endswith("and still be safe."))
        self.assertNotIn("](http", src)
        self.assertNotIn("![", src)

    def test_evidence_hash_recorded(self) -> None:
        readme = (EVIDENCE / "README.md").read_text(encoding="utf-8")
        sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertIn(sha, readme)
        self.assertIn("excluded at Shax's standing privacy rule", readme)
        for e in ENTRIES.values():
            self.assertIn(sha, e["metadata"]["source_draft"])

    def test_personal_content_absent(self) -> None:
        texts = {p.name: p.read_text(encoding="utf-8") for p in EVIDENCE.iterdir() if p.is_file()}
        texts[DOC.name] = DOC.read_text(encoding="utf-8")
        texts.update({eid: json.dumps(e, ensure_ascii=False) for eid, e in ENTRIES.items()})
        texts["manifest notes"] = json.dumps([m for m in MANIFEST["entries"] if m["entry_id"] in NEW_IDS])
        for name, text in texts.items():
            with self.subTest(file=name):
                self.assertFalse(_ngram_digests(text) & PRIVATE_NGRAM_SHA256)
            self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text), name)
            self.assertIsNone(re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", text), name)

    def test_hash_check_detects_and_tolerates(self) -> None:
        # The n-gram check must fire on normalized variants and ignore near-misses, using
        # benign stand-ins (not the excluded terms) hashed the same way.
        probe = {hashlib.sha256(b"red kite").hexdigest()}
        self.assertTrue(_ngram_digests("A  RED-kite flew.") & probe)
        self.assertFalse(_ngram_digests("A red, kitten flew; kite red.") & probe)
        self.assertEqual(len(PRIVATE_NGRAM_SHA256), 3)
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{64}", h) for h in PRIVATE_NGRAM_SHA256))

    def test_this_file_carries_no_plaintext_term(self) -> None:
        self.assertFalse(_ngram_digests(Path(__file__).read_text(encoding="utf-8")) & PRIVATE_NGRAM_SHA256)


class WestworldRoutingTests(unittest.TestCase):
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
            "Reset my router and clear the memory cache.",
            "We watched Westworld last night.",
            "The host welcomed the guests to the park.",
            "The hedge maze at the estate was hard to solve.",
            "Raise awareness about the fundraiser.",
            "remind me to call mom at 6",
        ):
            with self.subTest(text=text):
                self.assertNotEqual(route_domains(text).domain, "soul_bomb_sovereignty")

    def test_needs_review_fires_for_pending_by_id(self) -> None:
        for eid in PENDING:
            with self.subTest(eid=eid):
                packet = compile_semantic_packet(f"Explain {eid}.")
                self.assertTrue(packet.needs_review)
                self.assertIn(eid, [x["entry_id"] for x in packet.needs_review_entries])
        for text in ("Reset my router and clear the memory cache.", "The AI writes code.", "remind me to call mom at 6"):
            with self.subTest(text=text):
                ids = [x["entry_id"] for x in (compile_semantic_packet(text).needs_review_entries or [])]
                self.assertFalse(set(PENDING) & set(ids))


if __name__ == "__main__":
    unittest.main()
