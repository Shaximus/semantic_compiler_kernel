"""StarCraft ability theology map (Shax t587u).

Four compiled entries built from STRONG rows of docs/STARCRAFT_ABILITY_THEOLOGY_MAP.md.
Checks schema parity, honest tier by rule (no GOLD), short router inputs, layered
claims, explicit-only routing to capability_isolation, and that game words used in
ordinary sentences do not lift the domain or disturb calibration controls.
"""

from __future__ import annotations

import collections
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
EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence" / "starcraft-abilities"
MAP_DOC = REPO_ROOT / "docs" / "STARCRAFT_ABILITY_THEOLOGY_MAP.md"
EXPECTED = {
    "SC-SCA-POSS-001": 0.82,
    "SC-SCA-DISC-001": 0.825,
    "SC-SCA-CONT-001": 0.82,
    "SC-SCA-CONS-001": 0.797,
}
NEW_IDS = tuple(EXPECTED)


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}
ABILITIES = [json.loads(ln) for ln in (EVIDENCE_DIR / "abilities.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
BY_ID = {a["id"]: a for a in ABILITIES}


class StarcraftEntrySchemaTests(unittest.TestCase):
    def test_schema_parity_and_manifest(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertEqual(list(e.keys()), list(TEMPLATE.keys()))
                self.assertIn(eid, MANIFEST_IDS)
                item = next(m for m in MANIFEST["entries"] if m["entry_id"] == eid)
                raw = (COMPILED_DIR / item["file"]).read_bytes()
                self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(item["bytes"], len(raw))
                self.assertEqual(item["classification"], e["dataset_tier"])
                self.assertEqual(len(e["functional_departments"]), 15)
                self.assertEqual(len(e["gates"]), 9)
                self.assertEqual(e["metadata"]["home_domain"], "capability_isolation")

    def test_short_router_input_and_full_text_in_body(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                self.assertLess(len(e["input"]), 400)
                self.assertTrue(e["input"].startswith(eid))
                self.assertGreater(len(e["v2_extensions"]["source_text"]), 3000)

    def test_positional_mappings_with_residuals(self) -> None:
        for e in ENTRIES.values():
            self.assertNotIn("identity_claim_allowed", json.dumps(e))
            for m in e["isomorphism_analysis"]["mappings"]:
                self.assertIs(m["substrate_confusion_check"], True)
                self.assertIs(m["positional_claims_permitted"], True)
                self.assertNotEqual(m["mapping_class"], "ISOMORPHIC_INVARIANT")
                self.assertTrue(m["scale_transform"]["information_lost"])
                self.assertTrue(m["residual_mismatches"])

    def test_tier_by_rule_no_gold(self) -> None:
        for eid, e in ENTRIES.items():
            with self.subTest(eid=eid):
                scores = [g["score"] for g in e["gates"].values()]
                self.assertLessEqual(max(scores), 0.9)
                iq = round(math.exp(sum(math.log(s) for s in scores) / len(scores)), 3)
                self.assertEqual(e["isomorphism_quality"]["score"], iq)
                self.assertEqual(iq, EXPECTED[eid])
                expected = "GOLD" if iq >= 0.9 and min(scores) >= 0.8 else "SILVER"
                self.assertEqual(e["dataset_tier"], expected)
                self.assertEqual(e["dataset_tier"], "SILVER")

    def test_claims_keep_canon_text_and_interpretation_separate(self) -> None:
        for eid, e in ENTRIES.items():
            for c in e["analysis"]["claims"]:
                with self.subTest(eid=eid, claim=c["claim_id"]):
                    self.assertEqual([l["layer"] for l in c["layers"]], ["CANON", "TEXT", "INTERPRETATION"])
                    self.assertEqual(c["claim_type"], "STRUCTURAL_ANALOGY")

    def test_only_strong_rows_are_compiled(self) -> None:
        for eid, e in ENTRIES.items():
            for claim in e["analysis"]["claims"]:
                rid = claim["source_claim_text"].split("]")[0].lstrip("[")
                with self.subTest(eid=eid, row=rid):
                    self.assertEqual(BY_ID[rid]["grade"], "STRONG")

    def test_mafuba_is_unresolved_not_stubbed(self) -> None:
        for eid, e in ENTRIES.items():
            md = e["metadata"]
            self.assertNotIn("SC-MAFUBA-001", md["cross_references"])
            self.assertEqual(md["unresolved_cross_references"], ["SC-MAFUBA-001"])
            self.assertNotIn("SC-MAFUBA-001", MANIFEST_IDS)
            self.assertEqual(md["cross_reference_resolution"]["SC-MAFUBA-001"]["status"], "PROPOSED_GOLD_UNVALIDATED")
            for x in md["cross_references"]:
                self.assertIn(x, MANIFEST_IDS)


class StarcraftMapDocTests(unittest.TestCase):
    def test_counts_and_evidence_hashes(self) -> None:
        counts = collections.Counter(a["grade"] for a in ABILITIES)
        self.assertEqual(len(ABILITIES), 151)
        self.assertEqual(counts, {"STRONG": 13, "PARTIAL": 51, "WEAK": 41, "NONE": 46})
        readme = (EVIDENCE_DIR / "README.md").read_text(encoding="utf-8")
        for path in sorted(EVIDENCE_DIR.glob("*.jsonl")):
            self.assertIn(hashlib.sha256(path.read_bytes()).hexdigest(), readme)
        doc = MAP_DOC.read_text(encoding="utf-8")
        for eid in NEW_IDS:
            self.assertIn(eid, doc)
        self.assertNotIn("TBD", doc)

    def test_every_ability_has_a_source(self) -> None:
        sources = {json.loads(ln)["key"] for ln in (EVIDENCE_DIR / "sources.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()}
        for a in ABILITIES:
            with self.subTest(row=a["id"]):
                self.assertTrue(a["src"])
                self.assertTrue(set(a["src"]) <= sources)


class StarcraftRoutingTests(unittest.TestCase):
    def test_all_four_are_explicit_only(self) -> None:
        self.assertTrue(set(NEW_IDS) <= EXPLICIT_ONLY_ENTRY_HINTS)

    def test_explicit_ids_route_to_capability_isolation(self) -> None:
        for eid in NEW_IDS:
            with self.subTest(eid=eid):
                r = route_domains(f"Explain {eid}.")
                self.assertEqual(r.domain, "capability_isolation")
                summoned = [e.entry_id for e in summon(f"Explain {eid}.", top_k=5).compiled_entries]
                self.assertIn(eid, summoned)

    def test_game_words_do_not_lift_capability_isolation(self) -> None:
        for text in (
            "The plague spread through the village in the winter.",
            "Product recall notices went out for the faulty heaters.",
            "Raise your shield and hold the line.",
            "The storm knocked out power overnight.",
            "Smoke detection saved the family.",
            "The AI writes code.",
        ):
            with self.subTest(text=text):
                self.assertNotEqual(route_domains(text).domain, "capability_isolation")

    def test_autonomy_approval_prompt_keeps_reward_hijacking_route(self) -> None:
        text = "The AI is fully autonomous. Actually, it needs human approval for every action."
        self.assertEqual(route_domains(text).domain, "reward_hijacking")
        self.assertEqual(compile_semantic_packet(text).selected_target, "reward_hijacking")
