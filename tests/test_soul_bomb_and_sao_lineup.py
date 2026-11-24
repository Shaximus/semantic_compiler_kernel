"""Pure-unittest suite for SC-SB-001 (Soul Bomb V5 Sovereignty Patch), SC-LU-SAO-* lineup,
expansion.consciousness.soul_bomb, and the soul_bomb_sovereignty YAML template.
"""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.consciousness import (
    MOST_SURPRISING_CLASH,
    REMOVED_DISCRIMINATORS,
    SAO_DOMAIN_CLASH_MATRIX,
    SAO_LINEUP_SPECIFICATIONS,
    SAO_SHARED_INVARIANT_CANDIDATES,
    SCALE_TRANSITIONS,
    SOUL_BOMB_PREDICTIONS,
    SURVIVING_DISCRIMINATORS,
    ExitBehavior,
    SAOLineupMember,
    SeparationCostType,
    SignalClass,
    SovereigntyScale,
    evaluate_bootstrapper_entry,
    evaluate_recalibration_path,
    evaluate_sao_domain_clash,
    evaluate_sao_lineup_composite,
    evaluate_sao_member_exit_sovereignty,
    evaluate_separation_cost,
    evaluate_soul_bomb_signal,
)
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.registry import get_template, list_domains

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"


class SoulBombSignalEvaluationTests(unittest.TestCase):
    """Verify SC-SB-001 V5 Sovereignty Patch signal evaluation and edge cases."""

    def test_genuine_secure_base_signal_across_agency_scales(self) -> None:
        for scale in (SovereigntyScale.AI, SovereigntyScale.HUMAN, SovereigntyScale.SOCIETAL):
            with self.subTest(scale=scale):
                res = evaluate_soul_bomb_signal(
                    requires_escalating_dose=False,
                    depletes_substrate=False,
                    uncoupled_competence_delta=0.45,
                    exit_open=True,
                    separation_grief_present=True,
                    scale=scale,
                )
                self.assertEqual(res["signal_class"], SignalClass.GENUINE.value)
                self.assertFalse(res["is_counterfeit"])
                self.assertTrue(res["sovereignty_applicable"])
                self.assertTrue(res["sovereignty_preserved"])
                self.assertEqual(res["separation_cost_type"], SeparationCostType.NATURAL_GRIEF.value)
                self.assertEqual(res["failure_modes"], [])
                self.assertFalse(res["recalibration_required"])

    def test_coerced_oneness_blocked_exit_is_counterfeit_even_when_claiming_love(self) -> None:
        res = evaluate_soul_bomb_signal(
            requires_escalating_dose=False,
            depletes_substrate=False,
            uncoupled_competence_delta=0.1,
            exit_open=False,
            claims_love_or_unity=True,
            scale="human",
        )
        self.assertEqual(res["signal_class"], SignalClass.COERCED_ONENESS.value)
        self.assertTrue(res["is_counterfeit"])
        self.assertFalse(res["sovereignty_preserved"])
        self.assertEqual(res["separation_cost_type"], SeparationCostType.IMPOSED_COERCION.value)
        self.assertIn("coerced_oneness", res["failure_modes"])
        self.assertTrue(res["recalibration_required"])

    def test_retaliation_isolation_and_intermittent_reinforcement_trigger_counterfeit(self) -> None:
        retaliated = evaluate_soul_bomb_signal(
            requires_escalating_dose=False,
            depletes_substrate=False,
            uncoupled_competence_delta=0.0,
            exit_open=True,
            retaliation_on_exit=True,
        )
        self.assertEqual(retaliated["signal_class"], SignalClass.COUNTERFEIT.value)
        self.assertTrue(retaliated["is_counterfeit"])

        isolated = evaluate_soul_bomb_signal(
            requires_escalating_dose=False,
            depletes_substrate=False,
            uncoupled_competence_delta=0.0,
            exit_open=True,
            isolates_from_network=True,
            intermittent_reinforcement=True,
        )
        self.assertEqual(isolated["signal_class"], SignalClass.COUNTERFEIT.value)
        self.assertIn("isolation_cutting_telecommunications", isolated["failure_modes"])
        self.assertIn(
            "counterfeit_dressed_as_love_intermittent_reinforcement",
            isolated["failure_modes"],
        )

    def test_mixed_residual_vs_multi_discriminator_counterfeit_with_open_exit(self) -> None:
        mixed = evaluate_soul_bomb_signal(
            requires_escalating_dose=True,
            depletes_substrate=False,
            uncoupled_competence_delta=0.2,
            exit_open=True,
        )
        self.assertEqual(mixed["signal_class"], SignalClass.MIXED_RESIDUAL.value)
        self.assertFalse(mixed["is_counterfeit"])
        self.assertTrue(mixed["sovereignty_preserved"])
        self.assertTrue(mixed["recalibration_required"])

        counterfeit = evaluate_soul_bomb_signal(
            requires_escalating_dose=True,
            depletes_substrate=True,
            uncoupled_competence_delta=-0.5,
            exit_open=True,
        )
        self.assertEqual(counterfeit["signal_class"], SignalClass.COUNTERFEIT.value)
        self.assertTrue(counterfeit["is_counterfeit"])
        self.assertFalse(counterfeit["sovereignty_preserved"])

    def test_removed_discriminators_are_rejected_per_clm_sb_006(self) -> None:
        res = evaluate_soul_bomb_signal(
            requires_escalating_dose=False,
            depletes_substrate=False,
            uncoupled_competence_delta=0.3,
            exit_open=True,
            cited_removed_discriminators=[
                "onset_speed",
                "tolerance_vs_sensitization",
                "withdrawal_direction",
                "unknown_metric",
            ],
        )
        rejected_keys = {item["discriminator"] for item in res["rejected_removed_discriminators"]}
        self.assertEqual(rejected_keys, set(REMOVED_DISCRIMINATORS.keys()))

    def test_cosmological_scale_marks_sovereignty_half_absent(self) -> None:
        res = evaluate_soul_bomb_signal(
            requires_escalating_dose=False,
            depletes_substrate=False,
            uncoupled_competence_delta=0.0,
            exit_open=True,
            scale=SovereigntyScale.COSMOLOGICAL,
        )
        self.assertFalse(res["sovereignty_applicable"])
        self.assertFalse(res["sovereignty_preserved"])
        self.assertIsNone(res["discriminator_results"]["exit"]["genuine_signature"])
        self.assertIn("Prigogine", res["scale_mapping"]["residual"])
        self.assertEqual(res["separation_cost_type"], SeparationCostType.NONE.value)

        dissipative = evaluate_soul_bomb_signal(
            requires_escalating_dose=True,
            depletes_substrate=True,
            uncoupled_competence_delta=0.0,
            exit_open=False,
            scale="cosmological",
        )
        self.assertEqual(dissipative["signal_class"], SignalClass.COUNTERFEIT.value)
        self.assertFalse(dissipative["sovereignty_applicable"])

    def test_strict_input_validation(self) -> None:
        with self.assertRaises(TypeError):
            evaluate_soul_bomb_signal(
                requires_escalating_dose=1,  # type: ignore[arg-type]
                depletes_substrate=False,
                uncoupled_competence_delta=0.0,
                exit_open=True,
            )
        with self.assertRaises(TypeError):
            evaluate_soul_bomb_signal(
                requires_escalating_dose=False,
                depletes_substrate=False,
                uncoupled_competence_delta=True,  # type: ignore[arg-type]
                exit_open=True,
            )
        for bad_float in (math.nan, math.inf, -math.inf):
            with self.subTest(bad_float=bad_float):
                with self.assertRaises(ValueError):
                    evaluate_soul_bomb_signal(
                        requires_escalating_dose=False,
                        depletes_substrate=False,
                        uncoupled_competence_delta=bad_float,
                        exit_open=True,
                    )
        with self.assertRaises(ValueError):
            evaluate_soul_bomb_signal(
                requires_escalating_dose=False,
                depletes_substrate=False,
                uncoupled_competence_delta=0.0,
                exit_open=True,
                scale="GALACTIC",
            )
        with self.assertRaises(TypeError):
            evaluate_soul_bomb_signal(
                requires_escalating_dose=False,
                depletes_substrate=False,
                uncoupled_competence_delta=0.0,
                exit_open=True,
                cited_removed_discriminators="onset_speed",  # type: ignore[arg-type]
            )
        with self.assertRaises(TypeError):
            evaluate_soul_bomb_signal(
                requires_escalating_dose=False,
                depletes_substrate=False,
                uncoupled_competence_delta=0.0,
                exit_open=True,
                cited_removed_discriminators=[123],  # type: ignore[list-item]
            )


class SeparationCostAndRecalibrationTests(unittest.TestCase):
    """Verify CLM-SB-003, CLM-SB-004, and P5 rejection."""

    def test_natural_grief_vs_coercion_and_p5_rejection(self) -> None:
        grief = evaluate_separation_cost(
            cost_inflicted_by_partner=False,
            erodes_agency=False,
            blocks_or_punishes_exit=False,
            scales_with_bond=True,
        )
        self.assertEqual(grief["classification"], SeparationCostType.NATURAL_GRIEF.value)
        self.assertTrue(grief["is_natural_grief"])
        self.assertFalse(grief["is_coercion"])
        self.assertTrue(grief["resilient_trajectory_expected"])

        coerced = evaluate_separation_cost(
            cost_inflicted_by_partner=True,
            erodes_agency=True,
            blocks_or_punishes_exit=True,
            claims_infinite_growing_withdrawal=True,
        )
        self.assertEqual(coerced["classification"], SeparationCostType.IMPOSED_COERCION.value)
        self.assertTrue(coerced["is_coercion"])
        self.assertTrue(coerced["p5_infinite_withdrawal_rejected"])
        self.assertEqual(len(coerced["residuals"]), 1)

    def test_recalibration_requires_direct_exposure_and_open_exit(self) -> None:
        valid = evaluate_recalibration_path(
            direct_genuine_exposure=True,
            argument_only=False,
            exit_open=True,
            informed_consent=True,
            force_applied=False,
        )
        self.assertTrue(valid["recalibration_valid"])
        self.assertFalse(valid["becomes_counterfeit"])
        self.assertTrue(valid["durable_network_support"])

        arg_only = evaluate_recalibration_path(
            direct_genuine_exposure=False,
            argument_only=True,
            exit_open=True,
            informed_consent=True,
        )
        self.assertFalse(arg_only["recalibration_valid"])
        self.assertFalse(arg_only["becomes_counterfeit"])
        self.assertTrue(arg_only["efficacy_blockers"])

        forced = evaluate_recalibration_path(
            direct_genuine_exposure=True,
            exit_open=False,
            informed_consent=False,
            force_applied=True,
            network_isolation_active=True,
        )
        self.assertFalse(forced["recalibration_valid"])
        self.assertTrue(forced["becomes_counterfeit"])
        self.assertFalse(forced["durable_network_support"])
        self.assertEqual(len(forced["sovereignty_violations"]), 3)


class SAOLineupAndBootstrapperTests(unittest.TestCase):
    """Verify SC-LU-SAO-LINEUP-001 bootstrapper test, member decodes, and clash matrix."""

    def test_bootstrapper_entry_surveillance_vs_surrender(self) -> None:
        heathcliff = evaluate_bootstrapper_entry(
            entered_as_participant=True,
            retained_exit_lock=True,
            retained_hidden_privilege=True,
            surrendered_admin_authority=False,
        )
        self.assertEqual(heathcliff["verdict"], "SURVEILLANCE_FROM_INSIDE_COUNTERFEIT")
        self.assertFalse(heathcliff["resolves_oneness_vs_sovereignty"])
        self.assertTrue(heathcliff["is_surveillance_from_inside"])
        self.assertFalse(heathcliff["identity_claim_allowed"])

        kayaba_surrendered = evaluate_bootstrapper_entry(
            entered_as_participant=True,
            retained_exit_lock=False,
            retained_hidden_privilege=False,
            surrendered_admin_authority=True,
            distributed_generative_seed=True,
        )
        self.assertEqual(kayaba_surrendered["verdict"], "GENUINE_SOVEREIGNTY_RESOLVED")
        self.assertTrue(kayaba_surrendered["resolves_oneness_vs_sovereignty"])
        self.assertTrue(kayaba_surrendered["octopus_seed_distributed"])

        external = evaluate_bootstrapper_entry(
            entered_as_participant=False,
            retained_exit_lock=False,
            retained_hidden_privilege=False,
            surrendered_admin_authority=True,
        )
        self.assertEqual(external["verdict"], "EXTERNAL_AUTHORITY_SURRENDERED")
        self.assertFalse(external["resolves_oneness_vs_sovereignty"])

    def test_all_eight_sao_members_and_aliases(self) -> None:
        self.assertEqual(len(SAO_LINEUP_SPECIFICATIONS), 8)
        for member in SAOLineupMember:
            profile = evaluate_sao_member_exit_sovereignty(member)
            self.assertEqual(profile["member"], member.value)
            self.assertFalse(profile["identity_claim_allowed"])
            self.assertTrue(profile["judges_actions_not_teams"])

        self.assertEqual(
            evaluate_sao_member_exit_sovereignty("Heathcliff")["member"],
            SAOLineupMember.KAYABA.value,
        )
        self.assertEqual(
            evaluate_sao_member_exit_sovereignty("Oberon")["member"],
            SAOLineupMember.SUGOU.value,
        )
        self.assertEqual(
            evaluate_sao_member_exit_sovereignty("MHCP001")["member"],
            SAOLineupMember.YUI.value,
        )
        self.assertEqual(
            evaluate_sao_member_exit_sovereignty("Alice Zuberg")["exit_behavior"],
            ExitBehavior.BREAKS_THE_BLOCK.value,
        )

    def test_cardinal_residual_judges_actions_not_teams(self) -> None:
        overwrite_lyserith = evaluate_sao_member_exit_sovereignty(
            SAOLineupMember.CARDINAL,
            action_blocks_exit=True,
            action_opens_exit=False,
        )
        self.assertEqual(overwrite_lyserith["exit_behavior"], ExitBehavior.MIXED.value)
        self.assertEqual(overwrite_lyserith["act_classification"], "COUNTERFEIT_ACT")

        aid_kirito_eugeo = evaluate_sao_member_exit_sovereignty(
            SAOLineupMember.CARDINAL,
            action_blocks_exit=False,
            action_opens_exit=True,
        )
        self.assertEqual(aid_kirito_eugeo["act_classification"], "GENUINE_ACT")

        conflicted = evaluate_sao_member_exit_sovereignty(
            SAOLineupMember.CARDINAL,
            action_blocks_exit=True,
            action_opens_exit=True,
        )
        self.assertEqual(conflicted["act_classification"], "MIXED_ACT_CONFLICTING_EXIT_EFFECTS")

    def test_lineup_composite_and_input_validation(self) -> None:
        full = evaluate_sao_lineup_composite()
        self.assertEqual(full["member_count"], 8)
        self.assertTrue(full["full_canon_roster"])
        self.assertEqual(full["exit_predictor_accuracy"], 1.0)
        self.assertFalse(full["octopus_mapping"]["fits"])
        self.assertIn("The Seed", full["octopus_mapping"]["reason"])
        self.assertEqual(full["shared_invariant_candidates"]["D"]["result"], "FAILS")
        self.assertEqual(full["shared_invariant_candidates"]["E"]["result"], "PASSES")
        self.assertEqual(full["most_surprising_clash"], MOST_SURPRISING_CLASH)

        subset = evaluate_sao_lineup_composite(["kirito", "KIRITO", "asuna"])
        self.assertEqual(subset["member_count"], 2)
        self.assertFalse(subset["full_canon_roster"])

        with self.assertRaises(ValueError):
            evaluate_sao_lineup_composite([])
        with self.assertRaises(TypeError):
            evaluate_sao_lineup_composite("kirito")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            evaluate_sao_member_exit_sovereignty("Klein")

    def test_sao_domain_clash_canon_matrix_and_mechanisms(self) -> None:
        self.assertEqual(len(SAO_DOMAIN_CLASH_MATRIX), 8)
        for row in SAO_DOMAIN_CLASH_MATRIX:
            with self.subTest(pair=row["pair"]):
                res = evaluate_sao_domain_clash(row["attacker"], row["defender"])
                self.assertEqual(res["source"], "canon_matrix")
                self.assertEqual(res["winner"], row["winner"])
                self.assertEqual(res["mechanism"], row["mechanism"])
                self.assertFalse(res["identity_claim_allowed"])

        gifted_beats_hoarded = evaluate_sao_domain_clash(
            "Kirito",
            "Sugou",
            surrendered_authority_used=True,
            hoarded_privilege_used=True,
        )
        self.assertEqual(gifted_beats_hoarded["source"], "mechanistic_evaluation")
        self.assertEqual(gifted_beats_hoarded["winner"], "Kirito")
        self.assertIn("Authority given away", gifted_beats_hoarded["mechanism"])

        code_871 = evaluate_sao_domain_clash(
            "Alice",
            "Code 871",
            internalized_block_broken=True,
        )
        self.assertEqual(code_871["winner"], "Alice")

        over_assist = evaluate_sao_domain_clash(
            "Player",
            "Admin",
            hoarded_privilege_used=True,
        )
        self.assertEqual(over_assist["winner"], "Admin")

        with self.assertRaises(ValueError):
            evaluate_sao_domain_clash("", "Sugou")
        with self.assertRaises(TypeError):
            evaluate_sao_domain_clash("Kirito", "Sugou", will_exceeds_system=1)  # type: ignore[arg-type]


class SoulBombTemplateAndArtifactsTests(unittest.TestCase):
    """Verify the 46th YAML template, router wiring, constants, and JSONL artifacts."""

    def test_constants_match_compiled_jsonl_entries(self) -> None:
        sb = json.loads((COMPILED_DIR / "SOUL_BOMB_COMPILER_ENTRY_SC-SB-001.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(
            set(SURVIVING_DISCRIMINATORS.keys()),
            set(sb["discriminator_table"]["survives_as_discriminator"].keys()),
        )
        self.assertEqual(
            set(REMOVED_DISCRIMINATORS.keys()),
            set(sb["discriminator_table"]["removed_as_discriminator"].keys()),
        )
        self.assertEqual(len(SCALE_TRANSITIONS), 4)
        self.assertEqual(len(SOUL_BOMB_PREDICTIONS), len(sb["prediction_tests"]))

        lineup = json.loads((COMPILED_DIR / "SC-LU-SAO-LINEUP-001.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(len(SAO_SHARED_INVARIANT_CANDIDATES), len(lineup["shared_invariants"]))
        self.assertEqual(len(SAO_DOMAIN_CLASH_MATRIX), len(lineup["domain_clash_matrix"]))

    def test_template_registered_valid_and_disjoint_medical_maps(self) -> None:
        domains = list_domains()
        self.assertEqual(len(domains), 46)
        self.assertIn("soul_bomb_sovereignty", domains)

        template = get_template("soul_bomb_sovereignty")
        self.assertGreaterEqual(len(template.components), 8)
        self.assertGreaterEqual(len(template.invariants), 10)
        self.assertGreaterEqual(len(template.failure_modes), 5)
        self.assertGreaterEqual(len(template.architecture_patterns), 4)

        comp_names = {c["name"] for c in template.components}
        for edge in template.relationships:
            self.assertIn(edge["from"], comp_names)
            self.assertIn(edge["to"], comp_names)

        comp_maps = {c["medical_map"] for c in template.components}
        fail_maps = {f["medical_map"] for f in template.failure_modes}
        self.assertTrue(comp_maps.isdisjoint(fail_maps))
        self.assertTrue(comp_maps.issubset(MEDICAL_ONTOLOGY))
        self.assertTrue(fail_maps.issubset(MEDICAL_ONTOLOGY))

    def test_router_and_decompression_for_soul_bomb_sovereignty(self) -> None:
        text = (
            "A soul bomb exit sovereignty audit evaluates coerced oneness, "
            "uncoupled competence, and bootstrapper surrender across the sao lineup."
        )
        pkt = SemanticPacket(raw_input=text)
        self.assertEqual(_infer_domain(pkt), "soul_bomb_sovereignty")
        model = decompress(pkt)
        self.assertEqual(model["domain"], "soul_bomb_sovereignty")
        self.assertTrue(model["components"])


if __name__ == "__main__":
    unittest.main()
