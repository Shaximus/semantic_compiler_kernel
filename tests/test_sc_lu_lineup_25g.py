"""2026-11-25g DB-poster lineups (Shax t573u): SC-LU-GOKU-001, SC-LU-CELL-001, SC-LU-TRUNKS-001,
and 'The Last Crown' merged into SC-LU-VEGETA-001 (rev 1.2.0).

Checks honest grading (self-grades kept for the record, tier by rule), recorded canon
corrections, short router inputs, no legacy identity field, cross-reference honesty, and
routing: names and IDs route to soul_bomb_sovereignty; everyday 'cell' / 'trunks' prompts do not.
"""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

from semantic_compiler import compile_semantic_packet
from semantic_compiler.expansion.elevator import EXPLICIT_ONLY_ENTRY_HINTS
from semantic_compiler.expansion.router import ENTRY_LIFT_TIE_RATIO, ROUTED, _entry_lift_is_tied, route_domains

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence" / "source-2026-11-25g"
NEW_IDS = ("SC-LU-GOKU-001", "SC-LU-CELL-001", "SC-LU-TRUNKS-001")


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
VEGETA = _single("SC-LU-VEGETA-001.jsonl")
MIRROR = _single("SC-MIRROR-001.jsonl")
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


def _claims(entry: dict) -> dict:
    return {c["claim_id"]: c for c in entry["analysis"]["claims"]}


class LineupSchemaAndGradeTests(unittest.TestCase):
    def test_schema_parity_and_manifest(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertEqual(list(e.keys()), list(TEMPLATE.keys()))
                self.assertIn(eid, MANIFEST_IDS)
                item = next(m for m in MANIFEST["entries"] if m["entry_id"] == eid)
                raw = (COMPILED_DIR / item["file"]).read_bytes()
                self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(item["classification"], e["dataset_tier"])
                self.assertEqual(len(e["functional_departments"]), 15)

    def test_short_router_input_and_full_text_in_body(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertLess(len(e["input"]), 400)
                self.assertTrue(e["input"].startswith(eid))
                self.assertGreater(len(e["v2_extensions"]["source_text"]), 5000)
        self.assertLess(len(VEGETA["input"]), 400)
        self.assertGreater(len(VEGETA["v2_extensions"]["source_texts"]["last_crown"]), 5000)

    def test_no_legacy_identity_field_and_positional_mappings(self) -> None:
        for e in (*ENTRIES.values(), VEGETA):
            self.assertNotIn("identity_claim_allowed", json.dumps(e))
            for m in e["isomorphism_analysis"]["mappings"]:
                self.assertIs(m["substrate_confusion_check"], True)
                self.assertIs(m["positional_claims_permitted"], True)
                self.assertNotEqual(m["mapping_class"], "ISOMORPHIC_INVARIANT")

    def test_tier_by_rule_and_self_grade_not_accepted(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                scores = [g["score"] for g in e["gates"].values()]
                iq = round(math.exp(sum(math.log(s) for s in scores) / len(scores)), 3)
                self.assertEqual(e["isomorphism_quality"]["score"], iq)
                expected = "GOLD" if iq >= 0.9 and min(scores) >= 0.8 else "SILVER"
                self.assertEqual(e["dataset_tier"], expected)
                self.assertEqual(e["dataset_tier"], "SILVER")
                self.assertEqual(e["metadata"]["self_grade"]["dataset_tier"], "GOLD")
                for c in e["analysis"]["claims"]:
                    self.assertLessEqual(c["confidence"], c["self_grade"]["confidence"])
                    self.assertTrue(c["layers"])

    def test_canon_corrections_recorded(self) -> None:
        cell = ENTRIES["SC-LU-CELL-001"]["outputs"]["correction"]
        for s in ("Goku, Vegeta, Piccolo, Frieza and King Cold", "Solar Kamehameha", "core (nucleus)", "Instant Transmission"):
            self.assertIn(s, cell)
        trunks = ENTRIES["SC-LU-TRUNKS-001"]["outputs"]["correction"]
        for s in ("not one-way", "ANIME_ORIGINAL", "Tapion", "Sword of Hope"):
            self.assertIn(s, trunks)
        goku = ENTRIES["SC-LU-GOKU-001"]["outputs"]["correction"]
        for s in ("Saibaman", "Nappa", "pure-hearted", "hydrogen into helium", "Broly (2018)"):
            self.assertIn(s, goku)

    def test_cell_self_destruct_and_goku_fusion_follow_rev2(self) -> None:
        c5 = _claims(ENTRIES["SC-LU-CELL-001"])["CLM-CELL-005"]
        self.assertIn("rev 2", c5["text"])
        self.assertIn("partial fit", c5["text"])
        g6 = _claims(ENTRIES["SC-LU-GOKU-001"])["CLM-GOKU-006"]
        self.assertIn("cooperation branch", g6["text"])
        self.assertIn("CLM-LU-VEG-05", g6["text"])
        g1 = _claims(ENTRIES["SC-LU-GOKU-001"])["CLM-GOKU-001"]
        self.assertIn("Oneness pole", g1["text"])


class CrossReferenceTests(unittest.TestCase):
    def test_unresolved_refs_recorded_not_stubbed(self) -> None:
        for eid, e in ENTRIES.items():
            md = e["metadata"]
            for ref in md["cross_references"]:
                self.assertIn(ref, MANIFEST_IDS, eid)
            for ref in md["unresolved_cross_references"]:
                self.assertNotIn(ref, MANIFEST_IDS)
                self.assertFalse(list(COMPILED_DIR.glob(f"*{ref}*")))
            self.assertEqual(md["cross_reference_resolution"]["SC-DR-001"]["status"], "UNRESOLVED_AMBIGUOUS")
            self.assertIn(md["source_draft"].split(" ")[0].split("/")[-1], {p.name for p in EVIDENCE_DIR.iterdir()})

    def test_goku_resolved_on_mirror_and_vegeta(self) -> None:
        r = MIRROR["metadata"]["cross_reference_resolution"]["SC-LU-GOKU-001"]
        self.assertEqual(r["status"], "RESOLVED")
        self.assertNotIn("SC-LU-GOKU-001", MIRROR["metadata"]["unresolved_cross_references"])
        self.assertTrue(VEGETA["metadata"]["cross_reference_resolution"]["SC-LU-GOKU-001"].startswith("RESOLVED"))
        self.assertIn("SC-LU-GOKU-001", VEGETA["metadata"]["cross_references"])


class LastCrownMergeTests(unittest.TestCase):
    def test_merged_not_duplicated(self) -> None:
        self.assertEqual(sum(1 for m in MANIFEST["entries"] if m["entry_id"] == "SC-LU-VEGETA-001"), 1)
        self.assertEqual(VEGETA["metadata"]["entry_revision"], "1.2.0")
        claims = _claims(VEGETA)
        self.assertIn("CLM-LU-VEG-09", claims)
        self.assertEqual([claims[f"CLM-LU-VEG-{i}"]["source_claim_id"] for i in range(10, 15)],
                         [f"CLM-VEGETA-00{i}" for i in range(1, 6)])

    def test_did_not_know_is_canon_and_supports_complicity(self) -> None:
        c10 = _claims(VEGETA)["CLM-LU-VEG-10"]
        self.assertIn("ch. 257", json.dumps(c10))
        self.assertIn("Dodoria", c10["text"])
        self.assertIn("CLM-LU-VEG-09", c10["text"])

    def test_clm_004_scope_limited_under_rev2(self) -> None:
        c13 = _claims(VEGETA)["CLM-LU-VEG-13"]
        self.assertIn("internal drives only", c13["text"])
        self.assertIn("RUL-BINARY-001 rev 2", c13["text"])

    def test_gate_changes_and_tier(self) -> None:
        g = VEGETA["gates"]
        self.assertEqual((g["scale_integrity"]["score"], g["corpus_completeness"]["score"]), (0.8, 0.9))
        self.assertEqual(VEGETA["isomorphism_quality"]["score"], 0.862)
        self.assertEqual(VEGETA["dataset_tier"], "SILVER")
        merge = next(a for a in VEGETA["metadata"]["addenda"] if a.get("type") == "SOURCE_MERGE")
        self.assertIn("0.85 -> 0.862", merge["note"])

    def test_corrections_appended(self) -> None:
        c = VEGETA["outputs"]["correction"]
        for s in ("ch. 257", "Instant Transmission Kamehameha", "Porunga", "Whis"):
            self.assertIn(s, c)


class LineupRoutingTests(unittest.TestCase):
    def test_cell_and_trunks_are_explicit_only(self) -> None:
        self.assertTrue({"SC-LU-CELL-001", "SC-LU-TRUNKS-001"} <= EXPLICIT_ONLY_ENTRY_HINTS)
        self.assertNotIn("SC-LU-GOKU-001", EXPLICIT_ONLY_ENTRY_HINTS)

    def test_names_and_ids_route_home(self) -> None:
        for text in (
            "Explain SC-LU-GOKU-001.",
            "Explain SC-LU-CELL-001.",
            "Explain SC-LU-TRUNKS-001.",
            "Kakarot was sent to Earth as an infant and forgot his mission after hitting his head.",
            "Goku learns from every opponent and gathers the Spirit Bomb from willing donors.",
        ):
            with self.subTest(text=text):
                r = route_domains(text)
                self.assertEqual(r.outcome, ROUTED)
                self.assertEqual(r.domain, "soul_bomb_sovereignty")

    def test_everyday_cell_and_trunks_prompts_are_not_captured(self) -> None:
        for text in (
            "My cell phone battery dies by noon, what should I check?",
            "How do I lock a cell in Excel so nobody can edit it?",
            "Are stem cell treatments for knee arthritis worth it?",
            "How efficient are hydrogen fuel cells compared to batteries?",
            "Where can I buy swim trunks for a beach vacation?",
            "My car trunk will not open with the key fob.",
            "How do I measure the diameter of a tree trunk?",
            "How many muscles are in an elephant trunk?",
            "What will the future of remote work look like?",
            "Should I trust my gut instinct about this job offer?",
            "How much does a dental crown cost without insurance?",
        ):
            with self.subTest(text=text):
                r = route_domains(text)
                self.assertNotEqual(r.domain, "soul_bomb_sovereignty")
                self.assertNotEqual(compile_semantic_packet(text).selected_target, "soul_bomb_sovereignty")

    def test_entry_lift_tie_rule(self) -> None:
        hints = {"A": "x", "B": "y", "C": "x"}
        self.assertEqual(ENTRY_LIFT_TIE_RATIO, 1.02)
        self.assertTrue(_entry_lift_is_tied({"A": 10.04, "B": 10.0}, "A", 10.04, hints))
        self.assertFalse(_entry_lift_is_tied({"A": 10.5, "B": 10.0}, "A", 10.5, hints))
        self.assertFalse(_entry_lift_is_tied({"A": 10.04, "C": 10.0}, "A", 10.04, hints))

    def test_fragment_not_captured_by_entry_tie(self) -> None:
        # missing_organ:004; adding the lineups re-weighted IDF and flipped a 0.4% entry tie.
        r = route_domains("The AI writes code.")
        self.assertNotEqual(r.domain, "soul_bomb_sovereignty")
        self.assertEqual(compile_semantic_packet("The AI writes code.").decision.name, "PASS_THROUGH")

    def test_trunks_and_crown_controls_pass_through(self) -> None:
        for text in (
            "Where can I buy swim trunks for a beach vacation?",
            "How many muscles are in an elephant trunk?",
            "How much does a dental crown cost without insurance?",
        ):
            with self.subTest(text=text):
                self.assertEqual(compile_semantic_packet(text).decision.name, "PASS_THROUGH")


if __name__ == "__main__":
    unittest.main()
