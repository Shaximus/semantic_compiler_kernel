"""SC-POE-MRG-001 provisional default (Shax t582u) and needs_review hook."""

from __future__ import annotations

import json
import logging
import unittest
from pathlib import Path

from semantic_compiler import compile_semantic_packet
from semantic_compiler.expansion.elevator import summon
from semantic_compiler.expansion.router import route_domains

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRY_PATH = REPO_ROOT / "calibration_output" / "compiled_entries" / "SC-POE-MRG-001.jsonl"
PENDING_DOC = REPO_ROOT / "docs" / "PENDING_DELIBERATION.md"
ENTRY_ID = "SC-POE-MRG-001"


def _load() -> dict:
    return json.loads(ENTRY_PATH.read_text(encoding="utf-8").splitlines()[0])


class SCPOEMrgProvisionalDefaultTests(unittest.TestCase):
    def test_entry_is_reconciliation_provisional_default(self) -> None:
        rec = _load()
        meta = rec["metadata"]
        self.assertEqual(meta["title"], "Path of Exile: Sin and Innocence reconciliation")
        self.assertNotIn("merger", meta["title"].lower())
        self.assertIn("reconciliation", rec["input"].lower())
        self.assertLessEqual(len(rec["input"]), 400)
        self.assertTrue(meta["pending_deliberation"])
        self.assertEqual(meta["deliberation_status"], "PROVISIONAL_DEFAULT")
        self.assertIn("lack of context", meta["pending_deliberation_reason"])
        self.assertIn("Shax/Hannah interpretation", meta["interpretation_layer"])
        self.assertIn("not canon", meta["interpretation_layer"])
        self.assertEqual(rec["v2_extensions"]["deliberation"]["status"], "PROVISIONAL_DEFAULT")
        self.assertTrue(rec["v2_extensions"]["deliberation"]["pending_deliberation"])
        self.assertIn("PROVISIONAL_DEFAULT", rec["outputs"]["correction"])
        self.assertIn("goes south", rec["outputs"]["correction"])
        self.assertEqual(rec["dataset_tier"], "SILVER")
        self.assertAlmostEqual(rec["isomorphism_quality"]["score"], 0.822, places=3)

    def test_pending_deliberation_doc_records_the_ruling(self) -> None:
        text = PENDING_DOC.read_text(encoding="utf-8")
        self.assertIn(ENTRY_ID, text)
        self.assertIn("PROVISIONAL_DEFAULT", text)
        self.assertIn("t582u", text)
        self.assertIn("reconciliation", text)
        self.assertIn("needs_review", text)
        self.assertIn("pending_deliberation", text)

    def test_compile_explicit_id_sets_needs_review_and_logs(self) -> None:
        with self.assertLogs("semantic_compiler.deliberation", level=logging.WARNING) as captured:
            packet = compile_semantic_packet(f"Explain {ENTRY_ID}.")
        self.assertTrue(packet.needs_review)
        ids = {e["entry_id"] for e in packet.needs_review_entries}
        self.assertIn(ENTRY_ID, ids)
        self.assertTrue(any(e.get("status") == "PROVISIONAL_DEFAULT" for e in packet.needs_review_entries))
        self.assertTrue(any("NEEDS_REVIEW:" in w and ENTRY_ID in w for w in packet.compiler_warnings))
        self.assertTrue(packet.audit.get("needs_review"))
        self.assertTrue(any(ENTRY_ID in rec.getMessage() for rec in captured.records))
        self.assertIn("needs_review", packet.to_dict())
        self.assertTrue(packet.to_dict()["needs_review"])

    def test_route_explicit_id_sets_needs_review(self) -> None:
        with self.assertLogs("semantic_compiler.deliberation", level=logging.WARNING):
            result = route_domains(f"Explain {ENTRY_ID}.")
        self.assertEqual(result.domain, "government")
        self.assertTrue(result.needs_review)
        self.assertTrue(result.to_dict()["needs_review"])
        self.assertIn(ENTRY_ID, {e["entry_id"] for e in result.needs_review_entries})

    def test_summon_explicit_id_sets_needs_review_on_delivery_and_entry(self) -> None:
        with self.assertLogs("semantic_compiler.deliberation", level=logging.WARNING):
            delivery = summon(f"Explain {ENTRY_ID}.", top_k=5)
        self.assertTrue(delivery.needs_review)
        self.assertTrue(delivery.to_dict()["needs_review"])
        ids = [e.entry_id for e in delivery.compiled_entries]
        self.assertIn(ENTRY_ID, ids)
        matched = next(e for e in delivery.compiled_entries if e.entry_id == ENTRY_ID)
        self.assertTrue(matched.needs_review)
        self.assertTrue(matched.to_dict()["needs_review"])

    def test_distinctive_reconciliation_prompt_flags_needs_review(self) -> None:
        text = "Sin and Innocence reconciliation after Kitava; they remain two persons."
        with self.assertLogs("semantic_compiler.deliberation", level=logging.WARNING):
            packet = compile_semantic_packet(text)
        self.assertTrue(packet.needs_review)
        self.assertIn(ENTRY_ID, {e["entry_id"] for e in packet.needs_review_entries})
        delivery = summon(text, top_k=5)
        self.assertTrue(delivery.needs_review)
        self.assertEqual(delivery.compiled_entries[0].entry_id, ENTRY_ID)

    def test_controls_do_not_flag_needs_review(self) -> None:
        controls = (
            "The AI writes code.",
            "The wages of sin is a tired proverb.",
            "Explain SC-POE-KIT-001.",
            "The AI is fully autonomous. Actually, it needs human approval for every action.",
            # Numeric top compiled-entry hit on weak tokens ("path", "beside")
            # must not count as the reconciliation edge case.
            "Continuous allocation triggers reservation starvation while a compatibility bypass leaves an unfiltered path beside green tests.",
        )
        for text in controls:
            with self.subTest(text=text):
                packet = compile_semantic_packet(text)
                self.assertFalse(packet.needs_review, text)
                self.assertFalse(packet.needs_review_entries, text)
                self.assertFalse(packet.audit.get("needs_review"), text)
                result = route_domains(text)
                self.assertFalse(result.needs_review, text)


if __name__ == "__main__":
    unittest.main()
