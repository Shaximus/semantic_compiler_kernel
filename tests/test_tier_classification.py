"""
Tests for dataset tier classification.
"""

import unittest

from semantic_compiler.core.dataset import _classify_tier
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.core.types import DatasetTier, Decision


class TierClassificationTests(unittest.TestCase):
    """Verify dataset tier classification uses packet fields correctly."""

    def _packet(
        self,
        decision: Decision | None,
        dataset_value: float = 0.0,
        contradictions: list[dict] | None = None,
        negative_tests: list[dict] | None = None,
        residuals: list[str] | None = None,
    ) -> SemanticPacket:
        packet = SemanticPacket(
            decision=decision,
            scores={"dataset_value": dataset_value},
            contradictions=contradictions or [],
            negative_isomorphism_tests=negative_tests or [],
            residual_mismatches=residuals or [],
        )
        return packet

    def test_none_decision_is_bronze(self):
        packet = self._packet(decision=None)
        self.assertEqual(_classify_tier(packet), DatasetTier.BRONZE)

    def test_reject_decision_is_reject(self):
        packet = self._packet(decision=Decision.REJECT)
        self.assertEqual(_classify_tier(packet), DatasetTier.REJECT)

    def test_quarantine_decision_is_reject(self):
        packet = self._packet(decision=Decision.QUARANTINE)
        self.assertEqual(_classify_tier(packet), DatasetTier.REJECT)

    def test_compiled_with_default_value_is_silver(self):
        packet = self._packet(decision=Decision.COMPILED, dataset_value=0.5)
        self.assertEqual(_classify_tier(packet), DatasetTier.SILVER)

    def test_gold_requires_resolved_contradiction(self):
        packet = self._packet(
            decision=Decision.COMPILED,
            dataset_value=0.75,
            contradictions=[{"repair": "clarified scope"}],
        )
        self.assertEqual(_classify_tier(packet), DatasetTier.GOLD)

    def test_gold_without_correction_is_silver(self):
        packet = self._packet(
            decision=Decision.COMPILED,
            dataset_value=0.75,
            contradictions=[{"type": "DIRECT_NEGATION"}],
        )
        self.assertEqual(_classify_tier(packet), DatasetTier.SILVER)

    def test_diamond_requires_correction_and_negative_tests(self):
        packet = self._packet(
            decision=Decision.COMPILED,
            dataset_value=0.90,
            contradictions=[{"resolved": True}],
            negative_tests=[{"attack_result": "SURVIVED"}],
        )
        self.assertEqual(_classify_tier(packet), DatasetTier.DIAMOND)

    def test_diamond_plus_requires_all_criteria(self):
        packet = self._packet(
            decision=Decision.COMPILED,
            dataset_value=0.97,
            contradictions=[{"resolved": True}],
            negative_tests=[{"attack_result": "SURVIVED"}],
            residuals=["residual mismatch acknowledged"],
        )
        self.assertEqual(_classify_tier(packet), DatasetTier.DIAMOND_PLUS)


if __name__ == "__main__":
    unittest.main()
