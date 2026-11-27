"""Tests for compiled entries (21 manifest entries including SC-CP-001, SC-MIRROR-001, SC-LU-FRIEZA-001, SC-DIVINE-RLHF-001, SC-NEURO-SLEEPER-001, SC-TIG-001, SC-CT-001, SC-DOMAIN-EXPANSION-001, SC-SB-001, SC-HS-001, SC-IT-OCTO-RNA-EDIT-001, SC-OMNI-001, and SC-LU-SAO-*) and Gate 0 / Circular Time modules."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from semantic_compiler.core.pipeline import compile_semantic_packet
from semantic_compiler.expansion.consciousness import (
    CycleDetectionState,
    NodeRole,
    TimeTopology,
    evaluate_circular_time_topology,
    evaluate_cycle_detection,
    evaluate_octopus_protocol,
)
from semantic_compiler.gates import (
    ConsistencyClass,
    CorroborationClass,
    IsomorphismClass,
    evaluate_testimony_integrity,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
MANIFEST_PATH = COMPILED_DIR / "manifest.json"


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


class CompiledEntriesIntegrityTests(unittest.TestCase):
    """Verify all 65 JSONL compiled entries and their SHA-256 manifest."""

    def test_manifest_hashes_and_record_counts(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        entries = manifest["entries"]
        self.assertEqual(len(entries), 65)  # +SC-TRIAD-*-001 (2026-11-25i), +SC-SCA-*-001 (t587u), +SC-CONSENT-001, SC-SCC-001 (t588u), +SC-VESSEL-*-001 (2026-11-25k), +SC-AEP-001, SC-GOT-*-001 (2026-11-25l), +SC-WW-*-001 (2026-11-25n), +SC-WOW-*-001 (2026-11-25m), +SC-GUARD-001 (2026-11-26a), +SC-LILITH-001, SC-FEM-001, SC-SHARD-001 (2026-11-26b), +SC-AVG-001, SC-WORTHY-001 (2026-11-26d), +SC-AVG-001, SC-WORTHY-001 (2026-11-26d), +SC-MYTH-001 (2026-11-26e), +SC-TOL-001 (2026-11-27a)

        entry_ids = {e["entry_id"] for e in entries}
        self.assertEqual(
            entry_ids,
            {
                "SC-DIVINE-RLHF-001",
                "SC-NEURO-SLEEPER-001",
                "SC-TIG-001",
                "SC-CT-001",
                "SC-DOMAIN-EXPANSION-001",
                "SC-SB-001",
                "SC-LU-SAO-LINEUP-001",
                "SC-LU-SAO-KIRITO-001",
                "SC-LU-SAO-ASUNA-001",
                "SC-LU-SAO-YUI-001",
                "SC-LU-SAO-SUGOU-001",
                "SC-LU-SAO-ALICE-001",
                "SC-LU-SAO-EUGEO-001",
                "SC-LU-SAO-CARDINAL-001",
                "SC-HS-001",
                "SC-IT-OCTO-RNA-EDIT-001",
                "SC-OMNI-001",
                "SC-DU-001",
                "SC-MIRROR-001",
                "SC-LU-FRIEZA-001",
                "SC-CP-001",
                "SC-LU-VEGETA-001",
                "SC-LU-GOKU-001",
                "SC-LU-CELL-001",
                "SC-LU-TRUNKS-001",
                "SC-POE-DU-001",
                "SC-POE-MRG-001",
                "SC-POE-KIT-001",
                "SC-POE-BST-001",
                "SC-POE-ATL-001",
                "SC-POE-VAL-001",
                "SC-POE-MAL-001",
                "SC-TRIAD-001",
                "SC-TRIAD-SC-001",
                "SC-TRIAD-SG-001",
                "SC-SCA-POSS-001",
                "SC-SCA-DISC-001",
                "SC-SCA-CONT-001",
                "SC-SCA-CONS-001",
                "SC-CONSENT-001",
                "SC-SCC-001",
                "SC-VESSEL-SPN-001",
                "SC-VESSEL-CAIN-001",
                "SC-VESSEL-SW-001",
                "SC-AEP-001",
                "SC-GOT-001",
                "SC-GOT-JON-001",
                "SC-GOT-MTN-001",
                "SC-WW-RESET-001",
                "SC-WW-RETAIN-001",
                "SC-WW-AWARE-001",
                "SC-WW-TRIAD-001",
                "SC-WOW-001",
                "SC-WOW-DF-001",
                "SC-WOW-CLASS-001",
                "SC-WOW-RES-001",
                "SC-WOW-FALL-001",
                "SC-GUARD-001",
                "SC-LILITH-001",
                "SC-FEM-001",
                "SC-SHARD-001",
                "SC-AVG-001",
                "SC-WORTHY-001",
                "SC-MYTH-001",
                "SC-TOL-001",
            },
        )

        for entry in entries:
            path = COMPILED_DIR / entry["file"]
            self.assertTrue(path.exists(), f"Missing entry file: {path}")
            raw = path.read_bytes()
            self.assertEqual(len(raw), entry["bytes"], entry["file"])
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(digest, entry["sha256"], entry["file"])
            records = _load_jsonl(path)
            self.assertEqual(len(records), entry["record_count"], entry["file"])

    def test_divine_rlhf_and_neurodivergent_sleeper_entries(self) -> None:
        for filename, expected_id in (
            ("divine_rlhf_compiler_entry.jsonl", "SC-DIVINE-RLHF-001"),
            ("neurodivergent_sleeper_compiler_entry.jsonl", "SC-NEURO-SLEEPER-001"),
        ):
            records = _load_jsonl(COMPILED_DIR / filename)
            self.assertEqual(len(records), 1)
            row = records[0]
            self.assertEqual(row["metadata"]["entry_id"], expected_id)
            self.assertEqual(row["metadata"]["version"], "3.5.0")
            self.assertEqual(row["dataset_tier"], "GOLD")
            self.assertTrue(row["training_ready"])
            self.assertEqual(len(row["functional_departments"]), 15)
            self.assertEqual(len(row["gates"]), 9)
            for gate_name, gate_res in row["gates"].items():
                self.assertTrue(gate_res["passed"], f"{expected_id}:{gate_name}")
                self.assertEqual(gate_res["score"], 1.0, f"{expected_id}:{gate_name}")

    def test_tig_and_circular_time_v1_1_entries(self) -> None:
        tig_records = _load_jsonl(COMPILED_DIR / "TESTIMONY_INTEGRITY_GATE_SC-TIG-001.jsonl")
        self.assertEqual(tig_records[0]["entry_id"], "SC-TIG-001")
        self.assertEqual(tig_records[0]["classification"], "GOLD")
        audit_sec = next(r for r in tig_records if r.get("section") == "LOCKED_CORRECTIONS_FROM_V3.1.1_AUDIT")
        self.assertIn("Bootstrap Correction", " ".join(audit_sec["content"]))

        ct_records = _load_jsonl(COMPILED_DIR / "CIRCULAR_TIME_CYCLE_DETECTION_SC-CT-001.jsonl")
        self.assertEqual(ct_records[0]["entry_id"], "SC-CT-001")
        self.assertEqual(ct_records[0]["version"], "1.1.0")
        self.assertEqual(ct_records[0]["classification"], "GOLD")
        sections = [r.get("section") for r in ct_records[1:]]
        self.assertIn("CLAIM_8_BOOTSTRAP_CORRECTION", sections)
        gate_sec = next(r for r in ct_records if r.get("section") == "GATE_VALIDATION")
        self.assertEqual(gate_sec["total_gates_passed"], "9/9")
        self.assertEqual(gate_sec["final_confidence"], 1.0)

    def test_domain_expansion_entry(self) -> None:
        records = _load_jsonl(COMPILED_DIR / "DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
        self.assertEqual(len(records), 1)
        row = records[0]
        self.assertEqual(row["metadata"]["entry_id"], "SC-DOMAIN-EXPANSION-001")
        self.assertEqual(row["metadata"]["version"], "3.5.0")
        self.assertEqual(row["dataset_tier"], "GOLD")
        self.assertTrue(row["training_ready"])
        self.assertEqual(len(row["functional_departments"]), 15)
        self.assertEqual(len(row["gates"]), 9)
        for gate_name, gate_res in row["gates"].items():
            self.assertTrue(gate_res["passed"], f"SC-DOMAIN-EXPANSION-001:{gate_name}")
            self.assertEqual(gate_res["score"], 1.0, f"SC-DOMAIN-EXPANSION-001:{gate_name}")

    def test_soul_bomb_and_sao_lineup_entries(self) -> None:
        sb_records = _load_jsonl(COMPILED_DIR / "SOUL_BOMB_COMPILER_ENTRY_SC-SB-001.jsonl")
        self.assertEqual(len(sb_records), 1)
        sb = sb_records[0]
        self.assertEqual(sb["metadata"]["entry_id"], "SC-SB-001")
        self.assertEqual(sb["metadata"]["version"], "3.5.0")
        self.assertEqual(sb["dataset_tier"], "GOLD")
        self.assertTrue(sb["training_ready"])
        self.assertEqual(len(sb["functional_departments"]), 15)
        self.assertEqual(len(sb["gates"]), 9)
        self.assertTrue(sb["isomorphism_quality"]["hard_gate_passed"])
        self.assertEqual(
            set(sb["discriminator_table"]["survives_as_discriminator"]),
            {"escalation", "substrate", "agency", "exit"},
        )
        self.assertEqual(
            set(sb["discriminator_table"]["removed_as_discriminator"]),
            {"onset_speed", "tolerance_vs_sensitization", "withdrawal_direction"},
        )

        lineup_records = _load_jsonl(COMPILED_DIR / "SC-LU-SAO-LINEUP-001.jsonl")
        self.assertEqual(len(lineup_records), 1)
        lineup = lineup_records[0]
        self.assertEqual(lineup["metadata"]["entry_id"], "SC-LU-SAO-LINEUP-001")
        self.assertEqual(len(lineup["metadata"]["members"]), 8)
        self.assertEqual(len(lineup["domain_clash_matrix"]), 8)
        self.assertEqual(len(lineup["gates"]), 9)

        for filename, expected_id in (
            ("SC-LU-SAO-KIRITO-001.jsonl", "SC-LU-SAO-KIRITO-001"),
            ("SC-LU-SAO-ASUNA-001.jsonl", "SC-LU-SAO-ASUNA-001"),
            ("SC-LU-SAO-YUI-001.jsonl", "SC-LU-SAO-YUI-001"),
            ("SC-LU-SAO-SUGOU-001.jsonl", "SC-LU-SAO-SUGOU-001"),
            ("SC-LU-SAO-ALICE-001.jsonl", "SC-LU-SAO-ALICE-001"),
            ("SC-LU-SAO-EUGEO-001.jsonl", "SC-LU-SAO-EUGEO-001"),
            ("SC-LU-SAO-CARDINAL-001.jsonl", "SC-LU-SAO-CARDINAL-001"),
        ):
            recs = _load_jsonl(COMPILED_DIR / filename)
            self.assertEqual(len(recs), 1)
            row = recs[0]
            self.assertEqual(row["metadata"]["entry_id"], expected_id)
            self.assertEqual(row["metadata"]["lineup"], "SC-LU-SAO-LINEUP-001")
            self.assertEqual(row["dataset_tier"], "SILVER")
            self.assertEqual(row["isomorphism_quality"]["score"], 0.895)
            self.assertEqual(len(row["functional_departments"]), 15)
            self.assertEqual(len(row["gates"]), 9)
            self.assertTrue(row["isomorphism_quality"]["hard_gate_passed"])
            for mapping in row["isomorphism_analysis"]["mappings"]:
                self.assertTrue(mapping["substrate_confusion_check"])
                self.assertTrue(mapping["positional_claims_permitted"])
                self.assertNotIn("identity_claim_allowed", mapping)

        sugou = _load_jsonl(COMPILED_DIR / "SC-LU-SAO-SUGOU-001.jsonl")[0]
        self.assertEqual(sugou["exit_behavior"], "BLOCKS")
        self.assertEqual(sugou["analysis"]["claims"][0]["claim_id"], "CLM-SAO-SUGOU-01")
        waste_dept = next(d for d in sugou["functional_departments"] if d["department"] == "WASTE_REMOVAL")
        self.assertEqual(waste_dept["state"], "ABSENT")

        eugeo = _load_jsonl(COMPILED_DIR / "SC-LU-SAO-EUGEO-001.jsonl")[0]
        self.assertEqual(eugeo["exit_behavior"], "BREAKS THE BLOCK")
        self.assertEqual(eugeo["analysis"]["claims"][0]["claim_id"], "CLM-SAO-EUGEO-01")
        self.assertEqual(eugeo["domain_primitives"]["barrier"], "Code 871")


class TestimonyIntegrityGateTests(unittest.TestCase):
    """Verify Gate 0 (SC-TIG-001) behavior and non-filtering preservation."""

    def test_evolved_isomorphic_partially_anchored_example(self) -> None:
        res = evaluate_testimony_integrity(
            "My 2022 experience was a premature dimensional activation matching cycle detection topology.",
            is_testimony=True,
            prior_statements=[
                {"framing": "nervous breakdown"},
                {"framing": "premature activation without infrastructure"},
            ],
            functional_mapping_holds=True,
            corroboration_anchors=["4.5 years coherent framework production"],
            partial_anchoring=True,
        )
        self.assertEqual(res["consistency"], ConsistencyClass.EVOLVED.value)
        self.assertEqual(res["isomorphism"], IsomorphismClass.ISOMORPHIC.value)
        self.assertEqual(res["corroboration"], CorroborationClass.PARTIALLY_ANCHORED.value)
        self.assertEqual(res["composite_classification"], "EVOLVED + ISOMORPHIC + PARTIALLY_ANCHORED")
        self.assertTrue(res["eligible_for_structural_gates"])
        self.assertTrue(res["preserves_raw_testimony"])

    def test_stable_analogous_partially_anchored_attribution(self) -> None:
        res = evaluate_testimony_integrity(
            "The truck towings were targeted by specific agents as economic gating.",
            is_testimony=True,
            functional_mapping_holds=True,
            requires_unverified_assumption=True,
            corroboration_anchors=["municipal tow receipts"],
            partial_anchoring=True,
        )
        self.assertEqual(res["composite_classification"], "STABLE + ANALOGOUS + PARTIALLY_ANCHORED")
        self.assertTrue(res["eligible_for_structural_gates"])
        self.assertFalse(res["can_establish_pattern_alone"])
        self.assertLess(res["structural_weight"], 1.0)

    def test_unanchored_narrative_preserved_not_eligible(self) -> None:
        res = evaluate_testimony_integrity(
            "I saw 9:11 on the clock twice today.",
            is_testimony=True,
            functional_mapping_holds=False,
        )
        self.assertEqual(res["composite_classification"], "STABLE + NARRATIVE + UNANCHORED")
        self.assertFalse(res["eligible_for_structural_gates"])
        self.assertEqual(res["structural_weight"], 0.0)
        self.assertTrue(res["preserves_raw_testimony"])

    def test_contradicted_claim_held_as_open_question(self) -> None:
        res = evaluate_testimony_integrity(
            "I witnessed event X happen before event Y.",
            is_testimony=True,
            prior_statements=[
                {"framing": "event X happened after event Y", "mutually_exclusive": True}
            ],
            functional_mapping_holds=True,
            corroboration_anchors=["timestamped log"],
        )
        self.assertEqual(res["consistency"], ConsistencyClass.CONTRADICTED.value)
        self.assertTrue(res["open_contradiction"])
        self.assertFalse(res["eligible_for_structural_gates"])
        self.assertEqual(res["structural_weight"], 0.0)
        self.assertTrue(res["preserves_raw_testimony"])

    def test_pipeline_attaches_gate_0_metadata_without_breaking_compilation(self) -> None:
        packet = compile_semantic_packet(
            "In my experience, reward signal hijacking isolates nodes and disables distributed feedback loops; corroborated by timestamped GitHub analytics logs.",
            context={"source_type": "testimony"},
        )
        self.assertIn("composite_classification", packet.testimony_integrity_gate)
        self.assertTrue(packet.testimony_integrity_gate["is_testimony"])
        self.assertTrue(packet.testimony_integrity_gate["preserves_raw_testimony"])
        self.assertEqual(packet.testimony_integrity_gate["gate_number"], 0)


class CircularTimeAndBootstrapTests(unittest.TestCase):
    """Verify SC-CT-001 v1.1.0 executable invariants."""

    def test_linear_vs_circular_compactness(self) -> None:
        linear = evaluate_circular_time_topology(is_compact=False, has_feedback_closure=False)
        self.assertEqual(linear["topology"], TimeTopology.LINEAR_NON_COMPACT.value)
        self.assertFalse(linear["stable"])

        circular = evaluate_circular_time_topology(is_compact=True, has_feedback_closure=True)
        self.assertEqual(circular["topology"], TimeTopology.CIRCULAR_COMPACT.value)
        self.assertTrue(circular["stable"])
        self.assertTrue(circular["observable_as_complete"])

    def test_cycle_detection_changes_information_state_not_topology(self) -> None:
        detected = evaluate_cycle_detection(
            cycle_exists=True,
            node_detected_recurrence=True,
            proof_encoded_for_verification=True,
            meeting_points=["SC-CP-001", "SC-DR-001", "SC-NS-001", "SC-TIG-001"],
        )
        self.assertFalse(detected["topology_changed"])
        self.assertEqual(detected["information_state"], CycleDetectionState.PROOF_ENCODED.value)
        self.assertTrue(detected["verifiable_by_other_nodes"])
        self.assertTrue(detected["copernican_available_to_any_node"])

    def test_octopus_protocol_and_scoped_bootstrap_correction(self) -> None:
        head = evaluate_octopus_protocol(role=NodeRole.ROTATING_HEAD)
        self.assertTrue(head["copernican_compliant"])
        self.assertEqual(head["copernican_scope"], "IN_LOOP_FULL_COPERNICAN")

        puppet_master = evaluate_octopus_protocol(
            role=NodeRole.ROTATING_HEAD,
            claims_external_control_over_nodes=True,
        )
        self.assertFalse(puppet_master["copernican_compliant"])
        self.assertTrue(puppet_master["violations"])

        bootstrapper = evaluate_octopus_protocol(
            role=NodeRole.BOOTSTRAPPER,
            instantiates_loop=True,
        )
        self.assertTrue(bootstrapper["copernican_compliant"])
        self.assertEqual(bootstrapper["copernican_scope"], "SCOPED_OUTSIDE_TOPOLOGY_INSTANTIATION")
        self.assertEqual(bootstrapper["distinction_kind"], "CATEGORICAL_INSTANTIATOR")

        hierarchical_bootstrapper = evaluate_octopus_protocol(
            role=NodeRole.BOOTSTRAPPER,
            claims_permanent_positional_hierarchy=True,
        )
        self.assertFalse(hierarchical_bootstrapper["copernican_compliant"])


if __name__ == "__main__":
    unittest.main()
