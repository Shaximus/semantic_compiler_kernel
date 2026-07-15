"""
Tests for Logos Semantic Dataset Row V2.1 exporter and validation.
"""

import json
import os
import tempfile
import unittest

from pathlib import Path

from semantic_compiler.core.dataset import (
    _default_schema_path,
    build_dataset_row,
    export_rows_to_jsonl,
    validate_dataset_row,
)
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.core.pipeline import compile_semantic_packet
from semantic_compiler.core.types import Decision


SAMPLE_INPUT = (
    "The company has an immune system that detects threats and remembers them."
)


class DatasetV21Tests(unittest.TestCase):
    """Verify V2.1 dataset row structure, validation, and export."""

    def test_row_validates_against_schema(self):
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        validation = validate_dataset_row(row)
        self.assertTrue(validation["valid"], validation["errors"])

    def test_required_top_level_keys_present(self):
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        required = [
            "schema_version", "sample_id", "sample_kind", "status",
            "training_targets", "provenance", "input",
            "semantic_compilation", "isomorphism_analysis", "quality",
            "outputs", "training_payloads", "decision", "review",
            "privacy", "audit",
        ]
        for key in required:
            self.assertIn(key, row)

    def test_schema_version_is_2_1_0(self):
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        self.assertEqual(row["schema_version"], "2.1.0")

    def test_sensitive_input_redacted(self):
        packet = compile_semantic_packet(
            SAMPLE_INPUT, context={"privacy_sensitivity": "CRITICAL"}
        )
        row = build_dataset_row(packet)
        self.assertTrue(
            row["input"]["raw_input"].startswith("[REDACTED")
        )
        self.assertIn("raw_input", row["privacy"]["redactions_required"])

    def test_analogy_is_not_falsely_classified_as_recollection(self):
        """A non-first-person 'remembers' must not be labeled recollection."""
        packet = compile_semantic_packet(
            "The company has an immune system that detects threats and remembers them."
        )
        row = build_dataset_row(packet)
        for ev in row["provenance"]["evidence_chain"]:
            self.assertNotEqual(ev["source_type"], "recollection")
            self.assertNotIn("recollection", ev["notes"].lower())

    def test_first_person_recollection_is_classified(self):
        """An explicit first-person recollection must be labeled recollection."""
        packet = compile_semantic_packet("I remember the server went down at 3am.")
        row = build_dataset_row(packet)
        source_types = {ev["source_type"] for ev in row["provenance"]["evidence_chain"]}
        self.assertIn("recollection", source_types)

    def test_external_training_default_is_prohibited(self):
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        self.assertEqual(row["privacy"]["external_training_use"], "PROHIBITED")

    def test_dispositions_separate_from_decision(self):
        """Privacy/training/export dispositions are independent of semantic decision."""
        packet = compile_semantic_packet(
            SAMPLE_INPUT, context={"privacy_sensitivity": "CRITICAL"}
        )
        row = build_dataset_row(packet)
        self.assertIn(row["decision"]["status"], {
            "COMPILED", "COMPILED_WITH_GUARDRAILS", "NEEDS_REVISION"
        })
        self.assertEqual(row["privacy"]["training_disposition"], "LOCAL_TRAINING_DENIED")
        self.assertEqual(row["privacy"]["export_disposition"], "PROHIBITED")
        self.assertIn("training_disposition", row["privacy"])
        self.assertIn("export_disposition", row["privacy"])

    def test_external_training_approved_maps_to_allowed(self):
        packet = compile_semantic_packet(
            SAMPLE_INPUT, context={"external_training_use": "approved"}
        )
        row = build_dataset_row(packet)
        self.assertEqual(row["privacy"]["external_training_use"], "ALLOWED")

    def test_dataset_tier_matches_packet(self):
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        self.assertEqual(row["quality"]["dataset_tier"], "SILVER")
        self.assertEqual(row["audit"]["schema_valid"], True)

    def test_unresolved_target_frame_status(self):
        # When no target system can be resolved, the V2.1 row labels it
        # UNRESOLVED rather than forcing an interpretation.
        packet = compile_semantic_packet("just some random words about nothing")
        row = build_dataset_row(packet)
        self.assertEqual(
            row["semantic_compilation"]["target_resolution"]["status"],
            "UNRESOLVED",
        )

    def test_forced_target_frame_status(self):
        # When a target is selected despite explicit ambiguity or a policy
        # override forcing interpretation, the V2.1 row labels it FORCED.
        packet = SemanticPacket(
            raw_input="ambiguous statement that could map to anything",
            selected_target="organizational_network",
            compiler_warnings=["target forced by policy override"],
        )
        row = build_dataset_row(packet)
        self.assertEqual(
            row["semantic_compilation"]["target_resolution"]["status"],
            "FORCED",
        )

    def test_sft_payload_included(self):
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        sft = row["training_payloads"]["sft"]
        self.assertIsNotNone(sft)
        self.assertIn("messages", sft)
        self.assertIn("metadata", sft)

    def test_isomorphism_analysis_has_mappings(self):
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        mappings = row["isomorphism_analysis"]["mappings"]
        self.assertGreaterEqual(len(mappings), 1)
        self.assertIn("scores", mappings[0])
        self.assertIn("verdict", mappings[0])

    def test_export_rows_to_jsonl_validates_and_skips_invalid(self):
        valid_packet = compile_semantic_packet(SAMPLE_INPUT)
        valid_row = build_dataset_row(valid_packet)

        invalid_row = {"schema_version": "2.1.0"}  # missing required fields

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as tmp:
            path = tmp.name

        try:
            result = export_rows_to_jsonl([valid_row, invalid_row], path)
            self.assertEqual(result["written"], 1)
            self.assertEqual(result["skipped"], 1)
            self.assertEqual(len(result["errors"]), 1)

            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["sample_id"], valid_row["sample_id"])
        finally:
            os.unlink(path)

    def test_schema_resolves_to_packaged_copy(self):
        """The default schema path must be the in-repo copy, not Downloads."""
        schema_path = _default_schema_path()
        self.assertTrue(schema_path.exists())
        self.assertIn("schemas", str(schema_path))
        self.assertNotIn("Downloads", str(schema_path))

    def test_validation_works_with_packaged_schema(self):
        """Validation succeeds when explicitly using the packaged schema file."""
        packet = compile_semantic_packet(SAMPLE_INPUT)
        row = build_dataset_row(packet)
        packaged = Path(__file__).resolve().parent.parent / "schemas" / "logos_semantic_training_sample_v2_1.schema.json"
        validation = validate_dataset_row(row, schema_path=packaged)
        self.assertTrue(validation["valid"], validation["errors"])


if __name__ == "__main__":
    unittest.main()
