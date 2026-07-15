"""
Tests for scope-aware missing-organ / functional-department detection.
"""

import unittest

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.core.types import CompilerMode
from semantic_compiler.translation.fractal import identify_missing_departments


class MissingOrganScopeTests(unittest.TestCase):
    """Missing-organ detector must not claim absence from fragmentary input."""

    def test_fragmentary_analogy_marks_unobserved(self):
        """A one-sentence analogy cannot support confirmed absence claims."""
        system = {"present_functions": ["SECURITY"]}
        result = identify_missing_departments(system, scale="organizational")

        for finding in result:
            self.assertIn(
                finding["state"],
                {"PRESENT", "UNOBSERVED", "UNKNOWN"},
                f"{finding['department']} should not be ABSENT_CONFIRMED for fragmentary input",
            )
            self.assertNotEqual(finding["status"], "MISSING")

    def test_whole_system_mode_allows_absent_confirmed(self):
        """In structural-reconstruction mode, confirmed absence may be reported."""
        system = {"present_functions": ["SECURITY"]}
        result = identify_missing_departments(
            system, scale="computer", completeness_required=True
        )

        states = {f["state"] for f in result}
        self.assertIn("ABSENT_CONFIRMED", states)

        absent = [f for f in result if f["state"] == "ABSENT_CONFIRMED"]
        for f in absent:
            self.assertNotEqual(f["expected_at_scale"], "Unknown")
            self.assertIsNotNone(f["expected_at_scale"])

    def test_unknown_scale_does_not_confirm_absence(self):
        """If expected implementation at scale is unknown, absence is not confirmed."""
        system = {"present_functions": []}
        result = identify_missing_departments(
            system, scale="quantum", completeness_required=True
        )

        for f in result:
            if f["expected_at_scale"] is None or f["expected_at_scale"] == "Unknown":
                self.assertNotEqual(f["state"], "ABSENT_CONFIRMED")


class PipelineMissingOrganTests(unittest.TestCase):
    """Missing-organ behavior through the full pipeline."""

    def test_default_mode_does_not_emit_missing(self):
        from semantic_compiler.core.pipeline import compile_semantic_packet

        packet = compile_semantic_packet(
            "The immune system is like a security team."
        )
        for finding in packet.missing_organs:
            self.assertNotEqual(finding["status"], "MISSING")

    def test_structural_reconstruction_does_not_use_unobserved(self):
        from semantic_compiler.core.pipeline import compile_semantic_packet

        packet = compile_semantic_packet(
            "The computer has no CPU and no storage subsystem.",
            mode="STRUCTURAL_RECONSTRUCTION",
        )
        # In completeness mode, findings must be either confirmed, present,
        # or explicitly unknown — never the fragmentary "unobserved" state.
        states = {f["state"] for f in packet.missing_organs}
        self.assertNotIn("UNOBSERVED", states)
        self.assertTrue(
            states.issubset({"PRESENT", "ABSENT_CONFIRMED", "UNKNOWN", "NOT_ASSESSED"}),
            f"Unexpected states in completeness mode: {states}",
        )

    def test_incomplete_system_not_training_ready(self):
        """An explicitly incomplete system cannot be a clean positive SFT target."""
        from semantic_compiler.core.dataset import build_dataset_row
        from semantic_compiler.core.pipeline import compile_semantic_packet

        packet = compile_semantic_packet(
            "The computer has no CPU and no storage subsystem.",
            mode="STRUCTURAL_RECONSTRUCTION",
        )
        row = build_dataset_row(packet)
        self.assertTrue(
            any(f.get("state") == "ABSENT_CONFIRMED" for f in packet.missing_organs)
        )
        self.assertFalse(row["quality"]["training_ready"])


if __name__ == "__main__":
    unittest.main()
