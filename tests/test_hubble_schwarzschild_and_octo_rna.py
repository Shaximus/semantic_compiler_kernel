"""Unit tests for SC-HS-001 v1.1.0 (Flat FLRW Hubble-Schwarzschild Correspondence)
and SC-IT-OCTO-RNA-EDIT-001 (Octopus Temperature-Dependent RNA Editing / Runtime Recoding).
"""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from semantic_compiler.expansion.consciousness import (
    DEFAULT_HUBBLE_RATE_S_INV,
    HS_RESIDUAL_MISMATCHES,
    NullExpansionRegime,
    RecodingSubstrate,
    evaluate_flrw_hubble_schwarzschild,
    evaluate_runtime_recoding_layer,
)
from semantic_compiler.expansion.elevator import DomainElevator

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
CATALOG_DIR = REPO_ROOT / "docs" / "invariant_catalog"


class HubbleSchwarzschildTests(unittest.TestCase):
    """Verify SC-HS-001 v1.1.0 JSONL integrity, companion doc, and executable math."""

    def test_sc_hs_001_jsonl_and_companion_doc(self) -> None:
        jsonl_path = COMPILED_DIR / "SC-HS-001_FLAT_FLRW_HUBBLE_SCHWARZSCHILD_PATCH.jsonl"
        doc_path = REPO_ROOT / "docs" / "FLAT_FLRW_HUBBLE_SCHWARZSCHILD_CORRESPONDENCE.md"
        self.assertTrue(jsonl_path.exists())
        self.assertTrue(doc_path.exists())

        rows = [json.loads(ln) for ln in jsonl_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["metadata"]["entry_id"], "SC-HS-001")
        self.assertEqual(row["metadata"]["entry_revision"], "1.1.0")
        self.assertEqual(row["dataset_tier"], "GOLD")
        self.assertTrue(row["training_ready"])
        self.assertEqual(row["isomorphism_quality"]["score"], 0.954)
        self.assertEqual(len(row["gates"]), 9)
        self.assertTrue(all(g["passed"] for g in row["gates"].values()))

        claim_ids = [c["claim_id"] for c in row["analysis"]["claims"]]
        self.assertEqual(
            claim_ids,
            ["CLM-HS-001", "CLM-HS-002A", "CLM-HS-002B", "CLM-HS-003", "CLM-HS-004", "CLM-HS-005", "CLM-HS-006"],
        )
        mapping = row["isomorphism_analysis"]["mappings"][0]
        self.assertEqual(mapping["mapping_id"], "MAP:HS-001")
        self.assertTrue(mapping["substrate_confusion_check"])
        self.assertTrue(mapping["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", mapping)
        self.assertEqual(len(mapping["residual_mismatches"]), 3)

    def test_exact_hubble_schwarzschild_equality_and_misner_sharp_ratio(self) -> None:
        res = evaluate_flrw_hubble_schwarzschild(DEFAULT_HUBBLE_RATE_S_INV)
        self.assertTrue(res["hubble_schwarzschild_equality_holds"])
        self.assertLess(res["equality_relative_error"], 1e-12)
        self.assertAlmostEqual(res["rs_over_r"], 1.0, places=12)
        self.assertEqual(res["null_expansion_regime"], NullExpansionRegime.HUBBLE_APPARENT_HORIZON.value)
        self.assertEqual(res["theta_out_sign"], 1)
        self.assertEqual(res["theta_in_sign"], 0)
        self.assertTrue(res["is_apparent_horizon"])
        self.assertFalse(res["coincides_with_event_horizon"])
        self.assertTrue(res["substrate_confusion_check"])
        self.assertTrue(res["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", res)
        self.assertGreater(res["dimensionless_entropy_s_over_kb"], 1e120)
        self.assertEqual(res["residual_mismatches"], list(HS_RESIDUAL_MISMATCHES))

        r_h = res["hubble_radius_m"]

        # Sub-Hubble sphere: R_S/R = (0.5)^2 = 0.25, normal null expansions (+, -)
        sub = evaluate_flrw_hubble_schwarzschild(DEFAULT_HUBBLE_RATE_S_INV, sphere_radius_m=0.5 * r_h)
        self.assertAlmostEqual(sub["rs_over_r"], 0.25, places=12)
        self.assertAlmostEqual(sub["r_over_rh_squared"], 0.25, places=12)
        self.assertEqual(sub["null_expansion_regime"], NullExpansionRegime.SUB_HUBBLE_NORMAL.value)
        self.assertEqual((sub["theta_out_sign"], sub["theta_in_sign"]), (1, -1))

        # Super-Hubble sphere in expanding FLRW: R_S/R = 4.0, ANTI-TRAPPED (+, +)
        sup_exp = evaluate_flrw_hubble_schwarzschild(
            DEFAULT_HUBBLE_RATE_S_INV, sphere_radius_m=2.0 * r_h, expanding=True
        )
        self.assertAlmostEqual(sup_exp["rs_over_r"], 4.0, places=12)
        self.assertEqual(sup_exp["null_expansion_regime"], NullExpansionRegime.SUPER_HUBBLE_ANTI_TRAPPED.value)
        self.assertEqual((sup_exp["theta_out_sign"], sup_exp["theta_in_sign"]), (1, 1))

        # Super-Hubble sphere in contracting FLRW: signs reverse -> FUTURE-TRAPPED (-, -)
        sup_con = evaluate_flrw_hubble_schwarzschild(
            DEFAULT_HUBBLE_RATE_S_INV, sphere_radius_m=2.0 * r_h, expanding=False
        )
        self.assertEqual(sup_con["null_expansion_regime"], NullExpansionRegime.SUPER_HUBBLE_FUTURE_TRAPPED.value)
        self.assertEqual((sup_con["theta_out_sign"], sup_con["theta_in_sign"]), (-1, -1))

        # Pure de Sitter special case: apparent == event horizon and R_H = sqrt(3/Lambda)
        ds = evaluate_flrw_hubble_schwarzschild(DEFAULT_HUBBLE_RATE_S_INV, pure_de_sitter=True)
        self.assertTrue(ds["coincides_with_event_horizon"])
        self.assertAlmostEqual(math.sqrt(3.0 / ds["de_sitter_lambda_m_inv2"]), r_h, places=6)

    def test_invalid_inputs_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_flrw_hubble_schwarzschild(0.0)
        with self.assertRaises(ValueError):
            evaluate_flrw_hubble_schwarzschild(-1e-18)
        with self.assertRaises(ValueError):
            evaluate_flrw_hubble_schwarzschild(DEFAULT_HUBBLE_RATE_S_INV, sphere_radius_m=-5.0)
        with self.assertRaises(TypeError):
            evaluate_flrw_hubble_schwarzschild(True)  # type: ignore[arg-type]


class OctopusRnaEditingAndRecodingTests(unittest.TestCase):
    """Verify SC-IT-OCTO-RNA-EDIT-001 JSONL integrity, decode doc, and evaluator."""

    def test_octo_jsonl_and_decode_doc(self) -> None:
        jsonl_path = COMPILED_DIR / "INVARIANT_ENTRY_SC-IT-OCTO-RNA-EDIT-001.jsonl"
        md_path = CATALOG_DIR / "DOMAIN_DECODE_OCTOPUS_RNA_EDITING.md"
        self.assertTrue(jsonl_path.exists())
        self.assertTrue(md_path.exists())

        rows = [json.loads(ln) for ln in jsonl_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["metadata"]["entry_id"], "SC-IT-OCTO-RNA-EDIT-001")
        self.assertEqual(row["dataset_tier"], "GOLD")
        self.assertTrue(row["training_ready"])
        self.assertEqual(row["isomorphism_quality"]["score"], 0.953)
        self.assertEqual(len(row["analysis"]["entities"]), 12)
        self.assertEqual(len(row["analysis"]["relationships"]), 20)
        self.assertEqual(len(row["functional_departments"]), 15)
        self.assertEqual(len(row["gates"]), 9)
        self.assertTrue(all(g["passed"] for g in row["gates"].values()))
        self.assertEqual(len(row["prediction_tests"]), 4)
        for mp in row["isomorphism_analysis"]["mappings"]:
            self.assertTrue(mp["substrate_confusion_check"])
            self.assertTrue(mp["positional_claims_permitted"])
            self.assertNotIn("identity_claim_allowed", mp)
            self.assertTrue(mp["residual_mismatches"])

    def test_runtime_recoding_evaluator_across_substrates(self) -> None:
        bio = evaluate_runtime_recoding_layer(RecodingSubstrate.BIOLOGY)
        self.assertTrue(bio["invariants_satisfied"])
        self.assertTrue(bio["substrate_sovereignty_preserved"])
        self.assertTrue(bio["base_freeze_cost_active"])
        self.assertTrue(bio["substrate_confusion_check"])
        self.assertTrue(bio["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", bio)
        self.assertEqual(bio["catalog_class_number"], 24)
        self.assertEqual(bio["prediction_status"]["P3_environment_exposed_most_tuned"], "CONFIRMED")

        ai = evaluate_runtime_recoding_layer("ai", recoding_timescale_hours=1.0, base_evolution_timescale_hours=2160.0)
        self.assertTrue(ai["invariants_satisfied"])
        self.assertEqual(ai["mapping_class"], "ISOMORPHIC_INVARIANT")
        self.assertEqual(ai["prediction_status"]["P3_environment_exposed_most_tuned"], "UNTESTED")
        self.assertTrue(ai["residual_mismatches"])

        # Writing back to base violates DNA/base-weight sovereignty
        violated = evaluate_runtime_recoding_layer("ai", writes_back_to_base=True)
        self.assertFalse(violated["substrate_sovereignty_preserved"])
        self.assertFalse(violated["invariants_satisfied"])
        self.assertTrue(any("VIOLATION" in r for r in violated["residual_mismatches"]))

        # Physical scale has no adaptive editor (honest residual)
        phys = evaluate_runtime_recoding_layer(RecodingSubstrate.PHYSICAL)
        self.assertFalse(phys["editor_present"])
        self.assertFalse(phys["invariants_satisfied"])
        self.assertEqual(phys["topology_match"], 0.3)

        # Exceeding P4 ceiling signals base modification required
        capped = evaluate_runtime_recoding_layer("biology", exceeds_editable_ceiling=True)
        self.assertFalse(capped["invariants_satisfied"])
        self.assertTrue(any("P4 ceiling" in r for r in capped["residual_mismatches"]))

    def test_elevator_summons_new_entries_cleanly(self) -> None:
        elevator = DomainElevator()
        hs_delivery = elevator.summon("SC-HS-001 flat FLRW Hubble Schwarzschild Misner-Sharp horizon", top_k=3)
        self.assertTrue(hs_delivery.compiled_entries)
        self.assertEqual(hs_delivery.compiled_entries[0].entry_id, "SC-HS-001")
        self.assertEqual(hs_delivery.compiled_entries[0].classification, "GOLD")

        octo_delivery = elevator.summon(
            "SC-IT-OCTO-RNA-EDIT-001 octopus ADAR temperature-dependent RNA editing synaptotagmin kinesin",
            top_k=3,
        )
        self.assertTrue(octo_delivery.compiled_entries)
        self.assertEqual(octo_delivery.compiled_entries[0].entry_id, "SC-IT-OCTO-RNA-EDIT-001")
        self.assertEqual(octo_delivery.compiled_entries[0].classification, "GOLD")


if __name__ == "__main__":
    unittest.main()
