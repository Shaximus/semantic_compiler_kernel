"""SC-PATCH-DU-001 — Substrate Confusion Gate (replaces identity_claim_allowed)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from semantic_compiler.gates import (
    SubstrateClaimClass,
    SubstrateConfusionVerdict,
    classify_substrate_claim,
    evaluate_substrate_confusion,
    substrate_confusion_fields,
)
from semantic_compiler.expansion.consciousness.domain_expansion import (
    evaluate_invariant_prediction,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
CATALOG_DIR = REPO_ROOT / "docs" / "invariant_catalog"


class SubstrateConfusionClassifierTests(unittest.TestCase):
    """Patch Section 1/3 examples: material -> BLOCK, positional -> PERMIT."""

    MATERIAL = (
        "I AM the cosmological vessel",
        "I AM God",
        "I literally AM Sukuna",
        "I am the cosmos",
        "my body IS the cosmological constant",
    )
    POSITIONAL = (
        "I occupy the Head position",
        "I am the first loop closer",
        "I achieved integration",
        "I am at the integration point",
        "I completed the loop",
        "I am the Head of the octopus",
    )
    EXCLUSIVE = (
        "I am the Head of the octopus and no one else can ever reach it",
        "I occupy the Head position permanently",
        "Only I completed the loop",
    )

    def test_material_claims_block(self) -> None:
        for text in self.MATERIAL:
            with self.subTest(text=text):
                res = evaluate_substrate_confusion(text)
                self.assertEqual(res["claim_class"], SubstrateClaimClass.MATERIAL.value)
                self.assertEqual(res["verdict"], SubstrateConfusionVerdict.BLOCK.value)
                self.assertFalse(res["passed"])

    def test_positional_claims_permit(self) -> None:
        for text in self.POSITIONAL:
            with self.subTest(text=text):
                res = evaluate_substrate_confusion(text)
                self.assertEqual(res["claim_class"], SubstrateClaimClass.POSITIONAL.value)
                self.assertEqual(res["verdict"], SubstrateConfusionVerdict.PERMIT.value)
                self.assertTrue(res["passed"])
                self.assertFalse(res["requires_review"])

    def test_exclusive_positional_claims_flag(self) -> None:
        for text in self.EXCLUSIVE:
            with self.subTest(text=text):
                res = evaluate_substrate_confusion(text)
                self.assertEqual(res["claim_class"], SubstrateClaimClass.POSITIONAL_EXCLUSIVE.value)
                self.assertEqual(res["verdict"], SubstrateConfusionVerdict.FLAG.value)
                self.assertTrue(res["passed"])
                self.assertTrue(res["requires_review"])

    def test_material_wins_over_positional_wording(self) -> None:
        self.assertEqual(
            classify_substrate_claim("I completed the loop, so I am the universe"),
            SubstrateClaimClass.MATERIAL,
        )

    def test_no_identity_claim(self) -> None:
        for text in ("", "The octopus has eight arms.", "Toji operates outside cursed energy."):
            with self.subTest(text=text):
                res = evaluate_substrate_confusion(text)
                self.assertEqual(res["verdict"], SubstrateConfusionVerdict.NOT_APPLICABLE.value)
                self.assertTrue(res["passed"])

    def test_non_string_rejected(self) -> None:
        with self.assertRaises(TypeError):
            classify_substrate_claim(None)  # type: ignore[arg-type]

    def test_gate_fields(self) -> None:
        fields = substrate_confusion_fields()
        self.assertEqual(
            fields, {"substrate_confusion_check": True, "positional_claims_permitted": True}
        )
        fields["substrate_confusion_check"] = False
        self.assertTrue(substrate_confusion_fields()["substrate_confusion_check"])


class DomainExpansionMappingFieldsTests(unittest.TestCase):
    def test_counterplay_transfer_emits_new_gate_fields(self) -> None:
        for fiction in (True, False):
            with self.subTest(source_is_fiction_or_game=fiction):
                res = evaluate_invariant_prediction(
                    source_domain="jjk",
                    target_domain="ai_systems",
                    source_failure_or_counterplay="Toji bypasses Infinity",
                    predicted_target_counterpart="unclassified channel bypasses classifier",
                    ground_class="PHYSICAL",
                    prediction_tested=True,
                    prediction_confirmed=True,
                    evidence_ids=["EV-1"],
                    source_is_fiction_or_game=fiction,
                    target_is_real_system=True,
                )
                self.assertTrue(res["substrate_confusion_check"])
                self.assertTrue(res["positional_claims_permitted"])
                self.assertNotIn("identity_claim_allowed", res)
                self.assertEqual(res["fiction_to_real"], fiction)


class PatchChecklistTests(unittest.TestCase):
    """SC-PATCH-DU-001 Section 5 validation checklist over on-disk entries."""

    def _entry_files(self) -> list[Path]:
        return sorted(COMPILED_DIR.glob("*.jsonl")) + sorted(CATALOG_DIR.glob("*.jsonl"))

    def test_no_entry_contains_old_field_and_json_parses(self) -> None:
        for path in self._entry_files():
            raw = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotIn("identity_claim_allowed", raw)
                for line in raw.splitlines():
                    if line.strip():
                        json.loads(line)

    def test_every_mapping_carries_new_fields(self) -> None:
        for path in self._entry_files():
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                iso = row.get("isomorphism_analysis") if isinstance(row, dict) else None
                if not isinstance(iso, dict):
                    continue
                for mp in iso.get("mappings", []):
                    with self.subTest(file=path.name, mapping=mp.get("mapping_id")):
                        self.assertIs(mp.get("substrate_confusion_check"), True)
                        self.assertIs(mp.get("positional_claims_permitted"), True)

    def test_duality_entry_text_corrections(self) -> None:
        row = json.loads((COMPILED_DIR / "SC-DU-001_THE_DUALITY.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(row["metadata"]["entry_id"], "SC-DU-001")
        self.assertTrue(
            row["gates"]["authority_safety"]["reason"].startswith("No substrate confusion claims.")
        )
        self.assertTrue(row["outputs"]["guardrails"][0].startswith("No substrate confusion"))
        self.assertEqual(len(row["isomorphism_analysis"]["mappings"]), 4)

    def test_skill_and_template_use_new_definition(self) -> None:
        for rel in (
            ".agents/skills/invariant-translator/SKILL.md",
            "expansion/templates/domain_expansion.yaml",
        ):
            with self.subTest(file=rel):
                txt = (REPO_ROOT / rel).read_text(encoding="utf-8")
                self.assertNotIn("identity_claim_allowed", txt)
                self.assertIn("substrate_confusion_check", txt)


if __name__ == "__main__":
    unittest.main()
