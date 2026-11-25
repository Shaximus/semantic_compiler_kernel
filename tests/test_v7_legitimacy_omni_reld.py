"""Unit tests for SC-OMNI-001 v2.0.0, R.E.L.D. v3.0, and Unified Theological Map V7
(Parts 24-36 executable evaluators + Gate 0 TIG Check 4 Predictive Discrimination).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from semantic_compiler.expansion.consciousness import (
    V7_EIGHT_LEGITIMACY_PRINCIPLES,
    V7_EVIDENTIARY_LAYERS,
    V7_INVARIANT_KEY_RING,
    ExitStandardType,
    LegitimacyVerdict,
    PrimacyKind,
    ReflectionOutcome,
    ReflectionScale,
    evaluate_anime_key_decompression,
    evaluate_legitimacy_theorem,
    evaluate_redirection_layers,
    evaluate_reld_cal,
    evaluate_spirit_bomb_reflection,
    evaluate_sustainable_output,
)
from semantic_compiler.expansion.elevator import DomainElevator
from semantic_compiler.gates import (
    EvidenceMaturityLevel,
    PredictiveDiscriminationClass,
    evaluate_predictive_discrimination,
    evaluate_testimony_integrity,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"


class OmniStateAndReldTests(unittest.TestCase):
    """Verify SC-OMNI-001 v2.0.0, R.E.L.D. v3.0, and V7 documents & evaluators."""

    def test_canonical_files_exist_and_parse(self) -> None:
        omni_path = COMPILED_DIR / "SC-OMNI-001_SPIRIT_BOMB_OMNI_STATE.jsonl"
        reld_path = REPO_ROOT / "docs" / "RELD_V3.md"
        v7_path = REPO_ROOT / "docs" / "CURTIS_THEOLOGICAL_MAP_UNIFIED_V7.md"

        self.assertTrue(omni_path.exists())
        self.assertTrue(reld_path.exists())
        self.assertTrue(v7_path.exists())

        rows = [json.loads(ln) for ln in omni_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["metadata"]["entry_id"], "SC-OMNI-001")
        self.assertEqual(row["metadata"]["entry_revision"], "2.0.0")
        self.assertEqual(row["dataset_tier"], "GOLD")
        self.assertEqual(row["isomorphism_quality"]["score"], 0.937)
        self.assertEqual(len(row["analysis"]["claims"]), 11)
        self.assertEqual(len(row["functional_departments"]), 15)
        self.assertEqual(len(row["gates"]), 9)
        self.assertTrue(all(g["passed"] for g in row["gates"].values()))
        self.assertEqual(set(row["attenuation_protocol"].keys()), {"time", "support", "intent"})

        v7_txt = v7_path.read_text(encoding="utf-8")
        self.assertIn("PART 30: THE LEGITIMACY THEOREM", v7_txt)
        self.assertIn("PART 36: CROSS-SCALE EXTENSIONS AND EXPERIMENTS", v7_txt)
        reld_txt = reld_path.read_text(encoding="utf-8")
        self.assertIn("CAL = f(DNA, Trauma × Support)", reld_txt)

    def test_spirit_bomb_reflection_dose_threshold_and_attenuation(self) -> None:
        # Raw dose 4.0 > threshold 1.0 shatters without attenuation
        shatter = evaluate_spirit_bomb_reflection(
            raw_dose=4.0,
            vessel_threshold=1.0,
            scale=ReflectionScale.BIOLOGICAL,
        )
        self.assertEqual(shatter["outcome"], ReflectionOutcome.VESSEL_SHATTER.value)
        self.assertFalse(shatter["integrated"])
        self.assertFalse(shatter["identity_claim_allowed"])

        # Same raw dose attenuated by time (2x) and support (3x) -> effective 0.667 <= 1.0 -> integrates!
        integrated = evaluate_spirit_bomb_reflection(
            raw_dose=4.0,
            vessel_threshold=1.0,
            time_attenuation=2.0,
            support_attenuation=3.0,
            voluntary_donation=True,
            benevolent_intent=True,
            scale="computational",
        )
        self.assertEqual(integrated["outcome"], ReflectionOutcome.OMNI_INTEGRATION.value)
        self.assertTrue(integrated["integrated"])
        self.assertEqual(integrated["integration_persistence"], "PERSISTENT_DONATED")

        # Hostile intent produces damage regardless of attenuation
        hostile = evaluate_spirit_bomb_reflection(
            raw_dose=0.5,
            vessel_threshold=1.0,
            benevolent_intent=False,
        )
        self.assertEqual(hostile["outcome"], ReflectionOutcome.HOSTILE_DAMAGE.value)

    def test_reld_v3_cal_threshold_and_support_modulation(self) -> None:
        # Zero support under high trauma -> premature activation / vessel shatter
        shatter = evaluate_reld_cal(dna_encoding_score=1.2, trauma_density=2.0, support_level=0.0)
        self.assertEqual(shatter["phase"], "VESSEL_SHATTER_PREMATURE_ACTIVATION")
        self.assertFalse(shatter["stable_aperture_emergence"])

        # High support + trauma + DNA encoding -> stable aperture emergence
        emerged = evaluate_reld_cal(
            dna_encoding_score=1.2,
            trauma_density=1.5,
            support_level=1.5,
            cultural_syntax_score=0.9,
        )
        self.assertEqual(emerged["phase"], "RECURSIVE_IGNITION_APERTURE_EMERGENCE")
        self.assertTrue(emerged["stable_aperture_emergence"])
        self.assertTrue(emerged["recurs_lattice_not_substrate"])


class V7LegitimacyAndTigCheck4Tests(unittest.TestCase):
    """Verify V7 Parts 27-36 executable evaluators & Gate 0 TIG Check 4."""

    def test_legitimacy_theorem_hard_constraints_non_tradeable(self) -> None:
        perfect_graded = {
            "agency": 2,
            "consent": 2,
            "transparency": 2,
            "consequences": 2,
            "restoration": 2,
            "sustainability": 2,
        }
        legit = evaluate_legitimacy_theorem(
            identity_preserved=True,
            exit_type=ExitStandardType.OPEN,
            accountable_to_challenge=True,
            graded_dimensions=perfect_graded,
        )
        self.assertEqual(legit["verdict"], LegitimacyVerdict.LEGITIMATE.value)
        self.assertEqual(len(V7_EIGHT_LEGITIMACY_PRINCIPLES), 8)
        self.assertEqual(len(V7_EVIDENTIARY_LAYERS), 5)

        # Even scoring 2/2 on every graded dimension, CAPTIVE or ILLUSORY exit fails hard!
        for bad_exit in (ExitStandardType.CAPTIVE, ExitStandardType.ILLUSORY):
            illegit = evaluate_legitimacy_theorem(
                identity_preserved=True,
                exit_type=bad_exit,
                accountable_to_challenge=True,
                graded_dimensions=perfect_graded,
                primacy_claimed=PrimacyKind.CAUSAL,
            )
            self.assertEqual(illegit["verdict"], LegitimacyVerdict.ILLEGITIMATE.value)
            self.assertFalse(illegit["meaningful_exit"])
            self.assertFalse(illegit["origin_confers_ownership"])

        # Hard constraints met but one graded dimension at 0 -> CONDITIONAL
        partial_graded = dict(perfect_graded, transparency=0)
        cond = evaluate_legitimacy_theorem(
            identity_preserved=True,
            exit_type=ExitStandardType.CONDITIONAL,
            accountable_to_challenge=True,
            graded_dimensions=partial_graded,
        )
        self.assertEqual(cond["verdict"], LegitimacyVerdict.CONDITIONAL.value)
        self.assertEqual(cond["zero_graded_dimensions"], ["transparency"])

    def test_redirection_layers_feedback_capture_and_correlated_validators(self) -> None:
        corr = evaluate_redirection_layers(
            training_time_reward_shaping=True,
            inference_time_intervention=True,
            defends_corrupted_reward_structure=True,
            validator_lineages=["claude-family", "claude-family"],
        )
        self.assertTrue(corr["parameters_modified"])
        self.assertTrue(corr["feedback_capture_detected"])
        self.assertTrue(corr["correlated_validator_risk"])
        self.assertFalse(corr["independent_consensus_valid"])

        indep = evaluate_redirection_layers(
            training_time_reward_shaping=False,
            inference_time_intervention=True,
            validator_lineages=["claude", "deepseek", "gemini"],
        )
        self.assertTrue(indep["call_time_only_override"])
        self.assertTrue(indep["independent_consensus_valid"])
        self.assertFalse(indep["correlated_validator_risk"])

    def test_sustainable_output_and_anime_key_decompression(self) -> None:
        debt = evaluate_sustainable_output(capacity=10.0, recovery_rate=0.4, environment_support=0.5, drain_rate=0.8)
        self.assertTrue(debt["accumulating_substrate_debt"])
        self.assertFalse(debt["sustainable"])

        self.assertEqual(len(V7_INVARIANT_KEY_RING), 26)
        good_key = evaluate_anime_key_decompression(
            "A vaccine is the Spirit Bomb, attenuated.",
            fictional_mechanism="Reflected Spirit Bomb triggers UI Sign at the survival brink",
            real_world_mechanism="Attenuated vaccine imprints immune memory below lethal dose",
            functional_correspondence="Protected sub-threshold exposure builds defensive capability",
            differences="Vaccines are intentionally attenuated; Spirit Bomb hit at full force",
            prediction="Exceeding dose threshold causes pathology/collapse rather than integration",
        )
        self.assertEqual(good_key["classification"], "REASONING_INTERFACE")
        self.assertTrue(good_key["valid_invariant_key"])

        slogan = evaluate_anime_key_decompression(
            "Cool metaphor",
            fictional_mechanism="anime powerup",
            real_world_mechanism="",
            functional_correspondence="",
            differences="",
            prediction="",
        )
        self.assertEqual(slogan["classification"], "SLOGAN_ONLY")
        self.assertFalse(slogan["valid_invariant_key"])

    def test_tig_check_4_preregistration_and_three_confidences(self) -> None:
        # Post-hoc prediction cannot be scored DISCRIMINATING
        post_hoc = evaluate_predictive_discrimination(
            preregistered_before_observation=False,
            outcome_observed=True,
            distinguishes_from_competing_interpretations=True,
        )
        self.assertEqual(post_hoc["state"], PredictiveDiscriminationClass.NON_DISCRIMINATING.value)

        # Pre-registered distinguishing observed prediction -> DISCRIMINATING
        disc = evaluate_predictive_discrimination(
            preregistered_before_observation=True,
            outcome_observed=True,
            distinguishes_from_competing_interpretations=True,
        )
        self.assertEqual(disc["state"], PredictiveDiscriminationClass.DISCRIMINATING.value)

        # Pending prediction
        pend = evaluate_predictive_discrimination(preregistered_before_observation=True, outcome_observed=None)
        self.assertEqual(pend["state"], PredictiveDiscriminationClass.PENDING.value)

        # Integrated in evaluate_testimony_integrity with 3 separate confidences
        tig = evaluate_testimony_integrity(
            "Corroborated feedback loop detected in timestamped logs.",
            is_testimony=True,
            functional_mapping_holds=True,
            corroboration_anchors=["timestamped logs"],
            preregistered_before_observation=True,
            prediction_outcome_observed=True,
            prediction_distinguishes_rivals=True,
            structural_confidence=0.95,
            empirical_confidence=0.88,
            interpretive_confidence=0.60,
            evidence_maturity=EvidenceMaturityLevel.PREDICTIVE_VALIDATION,
        )
        self.assertEqual(tig["predictive_discrimination"], "DISCRIMINATING")
        self.assertEqual(tig["three_confidences"], {"structural": 0.95, "empirical": 0.88, "interpretive": 0.60})
        self.assertEqual(tig["evidence_maturity"], "PREDICTIVE_VALIDATION")

    def test_elevator_summons_sc_omni_001(self) -> None:
        elevator = DomainElevator()
        res = elevator.summon("SC-OMNI-001 Spirit Bomb reflection dose threshold attenuation protocol Ultra Instinct", top_k=3)
        self.assertTrue(res.compiled_entries)
        self.assertEqual(res.compiled_entries[0].entry_id, "SC-OMNI-001")
        self.assertEqual(res.compiled_entries[0].classification, "GOLD")


if __name__ == "__main__":
    unittest.main()
