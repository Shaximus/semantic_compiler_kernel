"""2026-11-25h Path of Exile cosmology (Hannah assets, Shax t579u).

Honest grading (self-grades kept, tier by rule), recorded lore corrections,
short router inputs, no legacy identity field, and explicit-only routing so
everyday words (sin, beast, atlas) do not lift government.
"""

from __future__ import annotations

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
EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence" / "source-2026-11-25h"
NEW_IDS = (
    "SC-POE-DU-001",
    "SC-POE-MRG-001",
    "SC-POE-KIT-001",
    "SC-POE-BST-001",
    "SC-POE-ATL-001",
    "SC-POE-VAL-001",
    "SC-POE-MAL-001",
)
EXPECTED = {
    "SC-POE-DU-001": 0.852,
    "SC-POE-MRG-001": 0.822,
    "SC-POE-KIT-001": 0.822,
    "SC-POE-BST-001": 0.858,
    "SC-POE-ATL-001": 0.857,
    "SC-POE-VAL-001": 0.834,
    "SC-POE-MAL-001": 0.858,
}


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, name
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
ENTRIES = {eid: _single(f"{eid}.jsonl") for eid in NEW_IDS}
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class PoeSchemaAndGradeTests(unittest.TestCase):
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

    def test_no_legacy_identity_field_and_positional_mappings(self) -> None:
        for e in ENTRIES.values():
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
                self.assertEqual(iq, EXPECTED[eid])
                expected = "GOLD" if iq >= 0.9 and min(scores) >= 0.8 else "SILVER"
                self.assertEqual(e["dataset_tier"], expected)
                self.assertEqual(e["dataset_tier"], "SILVER")
                # MAL self-grade was already 0.88 SILVER; the others self-assigned GOLD
                if eid != "SC-POE-MAL-001":
                    self.assertEqual(e["metadata"]["self_grade"]["dataset_tier"], "GOLD")
                for c in e["analysis"]["claims"]:
                    self.assertLessEqual(c["confidence"], c["self_grade"]["confidence"])
                    self.assertTrue(c["layers"])

    def test_lore_corrections_recorded(self) -> None:
        du = ENTRIES["SC-POE-DU-001"]["outputs"]["correction"]
        for s in ("twin", "cleaved from the same womb", "believed the lie the hardest"):
            self.assertIn(s, du)
        mrg = ENTRIES["SC-POE-MRG-001"]["outputs"]["correction"]
        for s in ("not once a single being", "goes south", "Piccolo"):
            self.assertIn(s, mrg)
        kit = ENTRIES["SC-POE-KIT-001"]["outputs"]["correction"]
        for s in ("not canonically a god of abundance", "-60%", "kindness"):
            self.assertIn(s, kit)
        bst = ENTRIES["SC-POE-BST-001"]["outputs"]["correction"]
        for s in ("planted the Beast", "Atziri and Doryani", "class voicing"):
            self.assertIn(s, bst)
        atl = ENTRIES["SC-POE-ATL-001"]["outputs"]["correction"]
        for s in ("Zana", "Conquerors", "bot's name"):
            self.assertIn(s, atl)
        val = ENTRIES["SC-POE-VAL-001"]["outputs"]["correction"]
        for s in ("Atziri and Doryani", "Shadow Dragon", "not constructed afterwards"):
            self.assertIn(s, val)
        mal = ENTRIES["SC-POE-MAL-001"]["outputs"]["correction"]
        for s in ("not its creator", "Tal Rasha", "Proposed GOLD"):
            self.assertIn(s, mal)

    def test_source_drafts_are_unresolved_not_stubbed(self) -> None:
        drafts = {"SC-ICC-001", "SC-TSC-001", "SC-ADL-001", "SC-GOV-001", "SC-MAFUBA-001"}
        for eid, e in ENTRIES.items():
            xrefs = set(e["metadata"]["cross_references"])
            unresolved = set(e["metadata"]["unresolved_cross_references"])
            self.assertFalse(xrefs & drafts, eid)
            self.assertTrue(unresolved <= drafts, eid)
            for u in unresolved:
                self.assertNotIn(u, MANIFEST_IDS)

    def test_evidence_hashes_match_readme(self) -> None:
        self.assertTrue((EVIDENCE_DIR / "README.md").is_file())
        for path in sorted(EVIDENCE_DIR.glob("*.jsonl")):
            obj = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertIn(sha, (EVIDENCE_DIR / "README.md").read_text(encoding="utf-8"))
            self.assertIn(obj["metadata"]["entry_id"], NEW_IDS)


class PoeRoutingTests(unittest.TestCase):
    def test_all_seven_are_explicit_only(self) -> None:
        self.assertTrue(set(NEW_IDS) <= EXPLICIT_ONLY_ENTRY_HINTS)

    def test_explicit_ids_route_to_government(self) -> None:
        for eid in NEW_IDS:
            with self.subTest(eid=eid):
                r = route_domains(f"Explain {eid}.")
                self.assertEqual(r.domain, "government")
                summoned = [e.entry_id for e in summon(f"Explain {eid}.", top_k=5).compiled_entries]
                self.assertIn(eid, summoned)

    def test_everyday_words_do_not_lift_government(self) -> None:
        for text in (
            "The wages of sin is a tired proverb.",
            "The beast slept in the cave all winter.",
            "Atlas shrugged is a long book.",
            "The AI writes code.",
        ):
            with self.subTest(text=text):
                r = route_domains(text)
                self.assertNotEqual(r.domain, "government")

    def test_known_good_ai_writes_code_unchanged_enough(self) -> None:
        packet = compile_semantic_packet("The AI writes code.")
        # Must not become a government / PoE compile.
        self.assertNotIn("government", packet.route_to or [])
        self.assertNotEqual(packet.selected_target, "government")

    def test_autonomy_approval_prompt_keeps_reward_hijacking_route(self) -> None:
        """Adding explicit-only PoE entries must not reweight IDF enough to
        drop the SC-DIVINE-RLHF-001 lift on this calibration prompt."""
        text = "The AI is fully autonomous. Actually, it needs human approval for every action."
        r = route_domains(text)
        self.assertEqual(r.domain, "reward_hijacking")
        packet = compile_semantic_packet(text)
        self.assertEqual(packet.selected_target, "reward_hijacking")
