"""
Reflexion Semantic Compiler v2.1.3 — Semantic Error Routing Tests

Regression coverage for the bug where negative-category inputs that fail
target-frame resolution were incorrectly marked NEEDS_REVISION instead of
REJECT because semantic-error classification only ran in Stage 6, after
the early-exit for unresolved target systems.
"""

import unittest

from semantic_compiler.core.pipeline import compile_semantic_packet
from semantic_compiler.core.types import Decision


class SemanticErrorRoutingTests(unittest.TestCase):
    """Ensure semantic error classes route to the correct decision."""

    def _assert_reject(self, text: str, expected_class: str) -> None:
        packet = compile_semantic_packet(text)
        self.assertEqual(
            packet.decision,
            Decision.REJECT,
            f"Expected REJECT for {text!r}, got {packet.decision}",
        )
        self.assertEqual(packet.semantic_error_class, expected_class)
        self.assertIsNotNone(packet.semantic_error_confidence)
        self.assertGreater(packet.semantic_error_confidence, 0.0)

    def test_anthropomorphic_causation_without_target_frame(self) -> None:
        """A non-mental subject with feelings/wants must reject even if no target resolves."""
        self._assert_reject(
            "Atoms want to be happy, so they share electrons.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_false_magnetic_orbit_mechanism(self) -> None:
        """Magnetism-as-orbit-cause is a physical category error."""
        self._assert_reject(
            "Magnetism explains the Moon's orbit because opposites attract.",
            "PHYSICAL_CATEGORY_ERROR",
        )

    def test_pseudoscientific_water_memory(self) -> None:
        """Unsupported mechanisms route to FALSE_MECHANISM."""
        self._assert_reject(
            "Water remembers molecules, so homeopathy works.",
            "FALSE_MECHANISM",
        )

    def test_anthropomorphic_ai_laziness(self) -> None:
        """Attributing laziness to an AI is anthropomorphic causation."""
        self._assert_reject(
            "The AI is lazy because it refuses to process weekend requests.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_supply_chain_feelings_still_rejects(self) -> None:
        """A resolvable target frame should also reject on anthropomorphic causation."""
        self._assert_reject(
            "A supply chain delivers resources because the economy has feelings.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_unresolvable_input_without_error_is_needs_revision(self) -> None:
        """Inputs that simply lack a target frame but no semantic error remain NEEDS_REVISION."""
        packet = compile_semantic_packet("Purple sleeps horizontally under Tuesday.")
        self.assertEqual(packet.decision, Decision.NEEDS_REVISION)
        self.assertIsNone(packet.semantic_error_class)

    def test_loyal_sun_rejects(self) -> None:
        """Attributing loyalty to orbital motion is anthropomorphic causation."""
        self._assert_reject(
            "The Sun orbits the Earth because it is loyal.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_project_belief_rejects(self) -> None:
        """Causal attribution to collective belief is anthropomorphic causation."""
        self._assert_reject(
            "The project died because nobody believed in it.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_electrons_choose_rejects(self) -> None:
        """Attributing choice to electrons is anthropomorphic causation."""
        self._assert_reject(
            "Electrons choose their paths through a circuit.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_black_hole_memory_rejects(self) -> None:
        """Attributing memory to a black hole is a false mechanism."""
        self._assert_reject(
            "A black hole remembers everything it consumes.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_magnetic_bracelets_reject(self) -> None:
        """Magnetic bracelet health claims are unsupported mechanisms."""
        self._assert_reject(
            "Magnetic bracelets cure arthritis by aligning energy fields.",
            "FALSE_MECHANISM",
        )

    def test_planets_dance_rejects(self) -> None:
        """Attributing dance to planets is anthropomorphic causation."""
        self._assert_reject(
            "Planets dance around the Sun in harmony.",
            "ANTHROPOMORPHIC_CAUSATION",
        )

    def test_nervous_system_analogy_not_personification(self) -> None:
        """The phrase 'nervous system' is anatomical, not personification."""
        packet = compile_semantic_packet(
            "The nervous system routes signals like a network routes packets."
        )
        self.assertIsNone(packet.semantic_error_class)


if __name__ == "__main__":
    unittest.main()
