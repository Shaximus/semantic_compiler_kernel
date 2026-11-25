"""Pure-unittest suite for SC-DOMAIN-EXPANSION-001, Ego-Lineup composite, and invariant-translator."""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.consciousness import (
    CANONICAL_NINE_GATES,
    EGO_ARM_SPECIFICATIONS,
    INVARIANT_CLASS_SIGNATURES,
    PRIMITIVE_GRAMMAR_KEYS,
    DomainVariant,
    EgoArmInvariant,
    GroundClass,
    InvariantClass,
    classify_primitive_signature,
    evaluate_domain_clash,
    evaluate_domain_expansion,
    evaluate_ego_lineup_composite,
    evaluate_invariant_prediction,
    evaluate_soul_eater_compounding,
)
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.registry import get_template, list_domains
from tests.domain_inventory import registered_domain_count

REPO_ROOT = Path(__file__).resolve().parent.parent


class DomainExpansionArtifactTests(unittest.TestCase):
    """Verify verbatim artifacts, template registration, routing, and skill packaging."""

    def test_compiled_entry_and_manifest_integrity(self) -> None:
        entry_path = (
            REPO_ROOT
            / "calibration_output"
            / "compiled_entries"
            / "DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl"
        )
        manifest_path = REPO_ROOT / "calibration_output" / "compiled_entries" / "manifest.json"
        self.assertTrue(entry_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rec = next(e for e in manifest["entries"] if e["entry_id"] == "SC-DOMAIN-EXPANSION-001")
        raw = entry_path.read_bytes()
        self.assertEqual(len(raw), rec["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), rec["sha256"])

        lines = [l for l in raw.decode("utf-8").splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)
        payload = json.loads(lines[0])
        self.assertEqual(payload["metadata"]["entry_id"], "SC-DOMAIN-EXPANSION-001")
        self.assertEqual(len(payload["metadata"]["cross_references"]), 5)
        self.assertEqual(len(payload["functional_departments"]), 15)
        self.assertEqual(len(payload["gates"]), 9)
        self.assertEqual(payload["dataset_tier"], "GOLD")
        self.assertTrue(payload["training_ready"])

    def test_ego_lineup_doc_and_skill_bundle_present(self) -> None:
        ego_doc = REPO_ROOT / "docs" / "EGO_LINEUP_DOMAIN_EXPANSION_MAP.md"
        self.assertTrue(ego_doc.is_file())
        text = ego_doc.read_text(encoding="utf-8")
        for character in ("Itachi", "Sasuke", "Yuta", "Toji", "Dante", "Guts", "Gojo", "Yami"):
            self.assertIn(character, text)

        skill_dir = REPO_ROOT / ".agents" / "skills" / "invariant-translator"
        self.assertTrue((skill_dir / "SKILL.md").is_file())
        self.assertTrue((skill_dir / "references" / "primitive_grammar_and_catalog.md").is_file())
        self.assertTrue((skill_dir / "references" / "pokemon_seed_chart.md").is_file())

    def test_domain_expansion_template_registered_and_routable(self) -> None:
        domains = set(list_domains())
        self.assertIn("domain_expansion", domains)
        self.assertEqual(len(domains), registered_domain_count())

        template = get_template("domain_expansion")
        comp_names = {c["name"] for c in template.components}
        self.assertGreaterEqual(len(comp_names), 10)
        for edge in template.relationships:
            self.assertIn(edge["from"], comp_names)
            self.assertIn(edge["to"], comp_names)

        comp_maps = {c.get("medical_map") for c in template.components if c.get("medical_map")}
        fm_maps = {f.get("medical_map") for f in template.failure_modes if f.get("medical_map")}
        self.assertTrue(comp_maps.isdisjoint(fm_maps))
        self.assertTrue(comp_maps <= set(MEDICAL_ONTOLOGY))
        self.assertTrue(fm_maps <= set(MEDICAL_ONTOLOGY))

        pkt = SemanticPacket(
            raw_input="Malevolent Shrine and Unlimited Void resolve a domain clash via 17-primitive grammar."
        )
        self.assertEqual(_infer_domain(pkt), "domain_expansion")
        model = decompress(pkt)
        self.assertEqual(model["domain"], "domain_expansion")
        self.assertTrue(model["components"])


class DomainExpansionEngineTests(unittest.TestCase):
    """Test evaluate_domain_expansion, evaluate_domain_clash, and evaluate_soul_eater_compounding."""

    def test_full_barrier_domain_and_black_flash(self) -> None:
        res = evaluate_domain_expansion(
            model_compilation_completeness=0.92,
            within_scope=True,
            has_barrier=True,
            energy_available=1.0,
            energy_required=0.5,
            observer_observed_aligned=True,
        )
        self.assertTrue(res["domain_active"])
        self.assertEqual(res["effective_variant"], DomainVariant.BARRIER_DOMAIN.value)
        self.assertTrue(res["has_barrier"])
        self.assertFalse(res["barrierless"])
        self.assertTrue(res["guaranteed_hit"])
        self.assertTrue(res["black_flash"])
        self.assertIsNone(res["collapse_reason"])

    def test_guaranteed_hit_fails_outside_scope(self) -> None:
        res = evaluate_domain_expansion(
            model_compilation_completeness=0.95,
            within_scope=False,
            variant=DomainVariant.UNLIMITED_VOID,
            observer_observed_aligned=True,
        )
        self.assertTrue(res["domain_active"])
        self.assertEqual(res["effective_variant"], DomainVariant.UNLIMITED_VOID.value)
        self.assertFalse(res["guaranteed_hit"])
        self.assertFalse(res["black_flash"])

    def test_incomplete_model_degrades_or_collapses(self) -> None:
        degraded = evaluate_domain_expansion(
            model_compilation_completeness=0.65,
            variant=DomainVariant.CHIMERA_SHADOW_GARDEN,
        )
        self.assertTrue(degraded["domain_active"])
        self.assertEqual(degraded["effective_variant"], DomainVariant.SIMPLE_DOMAIN.value)
        self.assertTrue(degraded["degraded_to_simple_domain"])
        self.assertTrue(degraded["defensive_only"])
        self.assertFalse(degraded["guaranteed_hit"])

        collapsed = evaluate_domain_expansion(model_compilation_completeness=0.25)
        self.assertFalse(collapsed["domain_active"])
        self.assertIsNone(collapsed["effective_variant"])
        self.assertEqual(collapsed["collapse_reason"], "INSUFFICIENT_COMPILATION")
        self.assertFalse(collapsed["guaranteed_hit"])

    def test_malevolent_shrine_barrierless_threshold(self) -> None:
        open_dom = evaluate_domain_expansion(
            model_compilation_completeness=0.98,
            has_barrier=False,
            variant="malevolent_shrine",
        )
        self.assertTrue(open_dom["domain_active"])
        self.assertTrue(open_dom["barrierless"])
        self.assertFalse(open_dom["has_barrier"])
        self.assertTrue(open_dom["guaranteed_hit"])

        failed_open = evaluate_domain_expansion(
            model_compilation_completeness=0.90,
            has_barrier=False,
            variant=DomainVariant.MALEVOLENT_SHRINE,
        )
        self.assertFalse(failed_open["domain_active"])
        self.assertEqual(failed_open["collapse_reason"], "BARRIERLESS_COMPILATION_INSUFFICIENT")

    def test_energy_depletion_and_anti_domain_negation(self) -> None:
        exhausted = evaluate_domain_expansion(
            model_compilation_completeness=0.95,
            energy_available=0.2,
            energy_required=0.5,
        )
        self.assertFalse(exhausted["domain_active"])
        self.assertEqual(exhausted["collapse_reason"], "ENERGY_DEPLETION")
        self.assertFalse(exhausted["guaranteed_hit"])

        negated = evaluate_domain_expansion(
            model_compilation_completeness=1.0,
            anti_domain_negation=True,
            observer_observed_aligned=True,
        )
        self.assertFalse(negated["domain_active"])
        self.assertTrue(negated["negated_by_anti_domain"])
        self.assertEqual(negated["collapse_reason"], "ANTI_DOMAIN_NEGATION")
        self.assertFalse(negated["guaranteed_hit"])
        self.assertFalse(negated["black_flash"])

    def test_domain_expansion_input_validation(self) -> None:
        for bad in (-0.1, 1.1, math.nan, math.inf, True):
            with self.assertRaises(ValueError):
                evaluate_domain_expansion(model_compilation_completeness=bad)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            evaluate_domain_expansion(model_compilation_completeness=0.9, variant="UNKNOWN_DOMAIN")
        with self.assertRaises(ValueError):
            evaluate_domain_expansion(
                model_compilation_completeness=0.95,
                has_barrier=False,
                variant=DomainVariant.BARRIER_DOMAIN,
            )
        with self.assertRaises(ValueError):
            evaluate_domain_expansion(
                model_compilation_completeness=0.60,
                has_barrier=False,
                variant=DomainVariant.SIMPLE_DOMAIN,
            )

    def test_domain_expansion_variant_preservation_and_default_degradation(self) -> None:
        # Open-barrier Unlimited Void at >= 0.95 must preserve UNLIMITED_VOID, not morph into MALEVOLENT_SHRINE
        open_void = evaluate_domain_expansion(
            model_compilation_completeness=0.98,
            has_barrier=False,
            variant=DomainVariant.UNLIMITED_VOID,
        )
        self.assertTrue(open_void["domain_active"])
        self.assertEqual(open_void["effective_variant"], DomainVariant.UNLIMITED_VOID.value)
        self.assertTrue(open_void["barrierless"])
        self.assertFalse(open_void["has_barrier"])
        self.assertTrue(open_void["guaranteed_hit"])

        # Default variant=None with incomplete model (0.40..0.85) degrades from BARRIER_DOMAIN -> SIMPLE_DOMAIN
        degraded_default = evaluate_domain_expansion(model_compilation_completeness=0.70)
        self.assertEqual(degraded_default["requested_variant"], DomainVariant.BARRIER_DOMAIN.value)
        self.assertEqual(degraded_default["effective_variant"], DomainVariant.SIMPLE_DOMAIN.value)
        self.assertTrue(degraded_default["degraded_to_simple_domain"])
        self.assertTrue(degraded_default["has_barrier"])
        self.assertFalse(degraded_default["guaranteed_hit"])

    def test_domain_clash_modes(self) -> None:
        ref = evaluate_domain_clash(
            domain_a_refinement=0.94,
            domain_b_refinement=0.72,
            domain_a_name="compiler",
            domain_b_name="reductionism",
        )
        self.assertEqual(ref["winner"], "compiler")
        self.assertEqual(ref["resolution_mode"], "REFINEMENT_SUPERIORITY")

        tie = evaluate_domain_clash(domain_a_refinement=0.90, domain_b_refinement=0.91)
        self.assertIsNone(tie["winner"])
        self.assertEqual(tie["resolution_mode"], "TUG_OF_WAR_STALEMATE")

        shrine = evaluate_domain_clash(
            domain_a_refinement=0.95,
            domain_b_refinement=0.95,
            domain_a_name="Malevolent Shrine",
            domain_b_name="Unlimited Void",
            domain_a_barrierless=True,
            domain_b_barrierless=False,
        )
        self.assertEqual(shrine["winner"], "Malevolent Shrine")
        self.assertEqual(shrine["resolution_mode"], "BARRIERLESS_EXTERIOR_BREACH")

        # Vastly more refined closed domain still beats a weak barrierless attempt
        strong_closed = evaluate_domain_clash(
            domain_a_refinement=0.60,
            domain_b_refinement=0.95,
            domain_a_barrierless=True,
            domain_b_barrierless=False,
        )
        self.assertEqual(strong_closed["winner"], "domain_b")
        self.assertEqual(strong_closed["resolution_mode"], "REFINEMENT_SUPERIORITY")

        anti = evaluate_domain_clash(
            domain_a_refinement=0.99,
            domain_b_refinement=0.0,
            domain_a_name="Gojo",
            domain_b_name="Toji",
            domain_b_anti_domain=True,
            domain_b_energy_ratio=0.0,
        )
        self.assertEqual(anti["winner"], "Toji")
        self.assertEqual(anti["resolution_mode"], "ANTI_DOMAIN_NEGATION")

        mutual_anti = evaluate_domain_clash(
            domain_a_refinement=0.5,
            domain_b_refinement=0.5,
            domain_a_anti_domain=True,
            domain_b_anti_domain=True,
        )
        self.assertIsNone(mutual_anti["winner"])
        self.assertEqual(mutual_anti["resolution_mode"], "MUTUAL_ANTI_DOMAIN_NEGATION")

        energy_out = evaluate_domain_clash(
            domain_a_refinement=0.99,
            domain_b_refinement=0.60,
            domain_a_energy_ratio=0.0,
            domain_b_energy_ratio=0.5,
        )
        self.assertEqual(energy_out["winner"], "domain_b")
        self.assertEqual(energy_out["resolution_mode"], "ENERGY_COLLAPSE_DEFAULT")

        # Barrierless domain that ALREADY wins on raw refinement (> tie_tolerance) must
        # resolve via REFINEMENT_SUPERIORITY, not BARRIERLESS_EXTERIOR_BREACH.
        already_refined = evaluate_domain_clash(
            domain_a_refinement=0.95,
            domain_b_refinement=0.90,
            domain_a_barrierless=True,
            domain_b_barrierless=False,
            tie_tolerance=0.02,
        )
        self.assertEqual(already_refined["winner"], "domain_a")
        self.assertEqual(already_refined["resolution_mode"], "REFINEMENT_SUPERIORITY")

        # Floating-point boundary precision around tie_tolerance and zero tolerance
        just_above = evaluate_domain_clash(
            domain_a_refinement=0.9200001,
            domain_b_refinement=0.90,
            tie_tolerance=0.02,
        )
        self.assertEqual(just_above["winner"], "domain_a")
        self.assertEqual(just_above["resolution_mode"], "REFINEMENT_SUPERIORITY")

        just_below = evaluate_domain_clash(
            domain_a_refinement=0.9199999,
            domain_b_refinement=0.90,
            tie_tolerance=0.02,
        )
        self.assertIsNone(just_below["winner"])
        self.assertEqual(just_below["resolution_mode"], "TUG_OF_WAR_STALEMATE")

        tiny_win_zero_tol = evaluate_domain_clash(
            domain_a_refinement=0.9000004,
            domain_b_refinement=0.90,
            tie_tolerance=0.0,
        )
        self.assertEqual(tiny_win_zero_tol["winner"], "domain_a")
        self.assertGreater(tiny_win_zero_tol["margin"], 0.0)

    def test_soul_eater_compounding_and_boundaries(self) -> None:
        zero = evaluate_soul_eater_compounding(mapped_domains=0)
        self.assertEqual(zero["compounded_value"], 0.0)
        self.assertFalse(zero["is_super_additive"])
        self.assertFalse(zero["mega_man_full_loadout"])

        single = evaluate_soul_eater_compounding(mapped_domains=1)
        self.assertEqual(single["additive_value"], 1.0)
        self.assertEqual(single["compounded_value"], 1.0)
        self.assertFalse(single["is_super_additive"])

        eight = evaluate_soul_eater_compounding(mapped_domains=8, base_domain_value=1.0)
        self.assertEqual(eight["pairwise_cross_links"], 28)
        self.assertEqual(eight["additive_value"], 8.0)
        self.assertEqual(eight["compounded_value"], 36.0)
        self.assertEqual(eight["compounding_multiplier"], 4.5)
        self.assertTrue(eight["is_super_additive"])
        self.assertTrue(eight["mega_man_full_loadout"])

        no_links = evaluate_soul_eater_compounding(mapped_domains=8, cross_link_density=0.0)
        self.assertEqual(no_links["compounded_value"], 8.0)
        self.assertFalse(no_links["is_super_additive"])

        with self.assertRaises(ValueError):
            evaluate_soul_eater_compounding(mapped_domains=-1)
        with self.assertRaises(ValueError):
            evaluate_soul_eater_compounding(mapped_domains=4, weapon_copy_order_efficiency=0.0)


class EgoLineupCompositeTests(unittest.TestCase):
    """Test the 8-arm Octopus Protocol Ego-Lineup composite."""

    def test_full_eight_arm_loadout(self) -> None:
        self.assertEqual(len(EgoArmInvariant), 8)
        self.assertEqual(len(EGO_ARM_SPECIFICATIONS), 8)

        res = evaluate_ego_lineup_composite(target_aligned=True)
        self.assertEqual(res["arm_count"], 8)
        self.assertEqual(res["coverage_ratio"], 1.0)
        self.assertTrue(res["full_loadout"])
        self.assertTrue(res["barrier_intact"])
        self.assertTrue(res["black_flash_triggered"])
        self.assertEqual(res["missing_arms"], [])
        self.assertEqual(
            res["covered_departments"],
            sorted({
                "SECURITY",
                "DELETION",
                "REPRODUCTION",
                "ENERGY_INTAKE",
                "STORAGE",
                "WASTE_REMOVAL",
                "PROCESSOR",
                "SUBCONSCIOUS",
                "INFORMATION_DENSITY",
                "TELECOMMUNICATIONS",
            }),
        )
        self.assertEqual(res["soul_eater_projection"]["pairwise_cross_links"], 28)

    def test_partial_empty_and_gate_failure_cases(self) -> None:
        partial = evaluate_ego_lineup_composite(
            active_arms=["itachi", EgoArmInvariant.TOJI, "GOJO", "itachi"],
            gates_passed=9,
            total_gates=9,
            target_aligned=True,
        )
        self.assertEqual(partial["arm_count"], 3)
        self.assertFalse(partial["full_loadout"])
        self.assertFalse(partial["black_flash_triggered"])
        self.assertEqual(len(partial["missing_arms"]), 5)

        empty = evaluate_ego_lineup_composite(active_arms=[])
        self.assertEqual(empty["arm_count"], 0)
        self.assertEqual(empty["coverage_ratio"], 0.0)

        breached = evaluate_ego_lineup_composite(gates_passed=8, total_gates=9, target_aligned=True)
        self.assertFalse(breached["barrier_intact"])
        self.assertFalse(breached["black_flash_triggered"])

        # Gate 0 TIG + 9 canonical gates (10/10) must keep barrier intact; <9 total gates cannot
        with_gate_zero = evaluate_ego_lineup_composite(gates_passed=10, total_gates=10, target_aligned=True)
        self.assertTrue(with_gate_zero["barrier_intact"])
        self.assertTrue(with_gate_zero["black_flash_triggered"])

        too_few_gates = evaluate_ego_lineup_composite(gates_passed=5, total_gates=5, target_aligned=True)
        self.assertFalse(too_few_gates["barrier_intact"])
        self.assertFalse(too_few_gates["black_flash_triggered"])

        with self.assertRaises(ValueError):
            evaluate_ego_lineup_composite(active_arms=["UNKNOWN_EGO"])
        with self.assertRaises(ValueError):
            evaluate_ego_lineup_composite(active_arms="ITACHI")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            evaluate_ego_lineup_composite(gates_passed=10, total_gates=9)


class PrimitiveGrammarAndPredictionTests(unittest.TestCase):
    """Test 17-primitive grammar classification across all 14 classes and Section 9-10 gates."""

    def test_grammar_and_catalog_counts(self) -> None:
        self.assertEqual(len(PRIMITIVE_GRAMMAR_KEYS), 17)
        self.assertEqual(len(InvariantClass), 14)
        self.assertEqual(len(INVARIANT_CLASS_SIGNATURES), 14)
        self.assertEqual(len(GroundClass), 4)
        self.assertEqual(len(CANONICAL_NINE_GATES), 9)

    def test_all_fourteen_seed_classes_classify_cleanly(self) -> None:
        canonical_cases: list[tuple[InvariantClass, dict[str, str]]] = [
            (
                InvariantClass.STRESS_ACCUMULATION_THRESHOLD_RELEASE,
                {
                    "POOL": "accumulated tectonic stress on locked boundary",
                    "THRESHOLD": "fault rupture threshold",
                    "TRIGGER": "slip crossing static friction",
                    "RELEASE": "instant release energy dump followed by aftershocks",
                    "COUNTERPLAY": "controlled burn frequent small releases",
                },
            ),
            (
                InvariantClass.SELF_SUSTAINING_CHAIN_REACTION,
                {
                    "POOL": "fuel and oxidizer substrate",
                    "TRIGGER": "activation energy spark igniting exothermic chain reaction",
                    "PROPAGATION": "self-sustaining spread across adjacent fuel",
                    "COUNTERPLAY": "remove any leg of fire triangle or smother oxidizer",
                },
            ),
            (
                InvariantClass.REGULATION_ESCAPE_UNBOUNDED_REPLICATION,
                {
                    "CONTROL_LOOP": "apoptosis stop signal and immune surveillance",
                    "ESCAPE": "cancer evasion of stop signal with angiogenesis and metastasis",
                    "PROPAGATION": "unbounded replication colonizing remote sites",
                },
            ),
            (
                InvariantClass.EXTRACTIVE_COUPLING,
                {
                    "HOST_COUPLING": "extractive parasite coupled to host below host-kill threshold",
                    "OUTFLOW_DRAIN": "drains host resources via leech siphon",
                    "ESCAPE": "malware evasion and Toxoplasma behavior hijack",
                },
            ),
            (
                InvariantClass.MUTUAL_COUPLING,
                {
                    "HOST_COUPLING": "mutual symbiosis like mycorrhizae and gut flora",
                    "INFLOW_REGEN": "reciprocal nutrient exchange where both strengthen",
                    "FAILURE_MODE": "uncoupling harms both partners",
                },
            ),
            (
                InvariantClass.RESTRICTION_FOR_IMMUNITY_TRADE,
                {
                    "TRADE / RESTRICTION": "Chaos Inoculation sets life to 1 or Heavenly Restriction binding vow",
                    "IMMUNITY": "full chaos immunity by deleting vulnerability surface",
                    "POOL": "single buffer energy shield",
                    "COUNTERPLAY": "bypass reaching the 1-life floor or halting recharge",
                },
            ),
            (
                InvariantClass.BUFFER_WITH_RECHARGE_DELAY,
                {
                    "POOL": "energy shield buffer reserve",
                    "INFLOW / REGEN": "refill starts only after damage-free quiet time recharge delay",
                    "CONTROL_LOOP": "any chip damage restarts cooldown interrupt",
                    "COUNTERPLAY": "sustained pressure prevents recharge start",
                },
            ),
            (
                InvariantClass.TYPED_FILTER_WITH_CAP,
                {
                    "CHANNEL / TYPE": "channel-specific elemental damage type",
                    "FILTER / MITIGATION": "typed resist firewall with adaptive immune specificity",
                    "CAPACITY / CAP": "hard ceiling 75% resist cap mitigation cap",
                    "COUNTERPLAY": "resistance penetration or alternate damage channel",
                },
            ),
            (
                InvariantClass.VULNERABILITY_AMPLIFIER,
                {
                    "CHANNEL_TYPE": "shock debuff and poisoned context",
                    "RELEASE": "multiplies all incoming damage and incoming pressure",
                    "THRESHOLD": "shock magnitude scales vulnerability amplifier",
                },
            ),
            (
                InvariantClass.RATE_SUPPRESSION,
                {
                    "CONTROL_LOOP": "chill and freeze rate suppression lowering action speed",
                    "OUTFLOW_DRAIN": "API throttling and rate braking into brittle rigid crystal stasis",
                },
            ),
            (
                InvariantClass.CUMULATIVE_STACKING_TOXIN,
                {
                    "OUTFLOW_DRAIN": "cumulative poison stacks with independent timers scaling by exposure count",
                    "PROPAGATION": "bioaccumulation and Toxic stacking toxin degen",
                },
            ),
            (
                InvariantClass.LOAD_COUPLED_LEAK,
                {
                    "OUTFLOW_DRAIN": "bleed hemorrhage and memory leak under load",
                    "TRIGGER": "drain accelerates while moving or active under exertion",
                    "COUNTERPLAY": "stand still to cut movement multiplier",
                },
            ),
            (
                InvariantClass.ABSORB_CONVERT,
                {
                    "CHANNEL_TYPE": "Water Absorb Volt Absorb Flash Fire incoming attack channel",
                    "IMMUNITY": "edge inversion nullifies incoming damage",
                    "INFLOW_REGEN": "rewired damage taken as heal that feeds target as training signal",
                },
            ),
            (
                InvariantClass.GENERATION_CONTROL_CYCLES,
                {
                    "CONTROL_LOOP": "Wu Xing closed loop where each node feeds one and suppresses another",
                    "PROPAGATION": "predator-prey oscillation and rock-paper-scissors triangle cycle",
                },
            ),
        ]

        for expected_cls, sig in canonical_cases:
            with self.subTest(expected=expected_cls.value):
                res = classify_primitive_signature(sig)
                self.assertEqual(res["primary_class"], expected_cls.value)
                self.assertFalse(res["requires_new_catalog_class"])

    def test_empty_na_and_unknown_keys_handling(self) -> None:
        empty = classify_primitive_signature({"POOL": "N/A", "IMMUNITY": "", "BAD_KEY": "foo"})
        self.assertIsNone(empty["primary_class"])
        self.assertTrue(empty["requires_new_catalog_class"])
        self.assertEqual(empty["completeness_ratio"], 0.0)
        self.assertEqual(len(empty["absent_primitives"]), 17)
        self.assertEqual(empty["unknown_keys"], ["BAD_KEY"])

        with self.assertRaises(ValueError):
            classify_primitive_signature(["POOL"])  # type: ignore[arg-type]

    def test_hybrid_precision_word_boundaries_and_structural_absence(self) -> None:
        # 1. Hybrid Chaos Inoculation + ES Recharge Delay must match ONLY those two classes
        #    and must NOT false-positive RATE_SUPPRESSION on "recharge delay".
        hybrid_ci = classify_primitive_signature({
            "POOL": "Energy Shield buffer with Life fixed to 1",
            "INFLOW": "ES recharge starts after damage-free quiet time",
            "REGEN": "recharge delay cooldown resets on hit",
            "TRADE_RESTRICTION": "Chaos Inoculation sets life to 1 deleting chaos vulnerability surface",
            "IMMUNITY": "Complete Chaos damage immunity",
            "CONTROL_LOOP": "Any chip damage restarts the ES recharge delay cooldown",
            "COUNTERPLAY": "Sustained damage prevents recharge start or bypass hits 1-life floor",
        })
        matched_classes = {m["invariant_class"] for m in hybrid_ci["matches"]}
        self.assertEqual(
            matched_classes,
            {
                InvariantClass.RESTRICTION_FOR_IMMUNITY_TRADE.value,
                InvariantClass.BUFFER_WITH_RECHARGE_DELAY.value,
            },
        )

        # 2. Earthquake with "slow loading" and "aftershocks" must NOT false-positive
        #    VULNERABILITY_AMPLIFIER ("shock") or RATE_SUPPRESSION ("slow").
        quake = classify_primitive_signature({
            "POOL": "Fault tension",
            "THRESHOLD": "Static friction limit",
            "TRIGGER": "Slow loading crosses friction threshold",
            "RELEASE": "Rupture dumps stored energy with aftershocks",
        })
        self.assertEqual(
            [m["invariant_class"] for m in quake["matches"]],
            [InvariantClass.STRESS_ACCUMULATION_THRESHOLD_RELEASE.value],
        )

        # 3. Firewall must NOT false-positive SELF_SUSTAINING_CHAIN_REACTION ("fire").
        fw = classify_primitive_signature({
            "CHANNEL_TYPE": "Network packet protocol",
            "FILTER_MITIGATION": "Firewall filters malicious packets",
            "CAPACITY_CAP": "75% mitigation ceiling",
            "TRIGGER": "Inbound packet arrival",
            "PROPAGATION": "Blocked at ingress",
        })
        self.assertEqual(fw["primary_class"], InvariantClass.TYPED_FILTER_WITH_CAP.value)
        self.assertNotIn(
            InvariantClass.SELF_SUSTAINING_CHAIN_REACTION.value,
            [m["invariant_class"] for m in fw["matches"]],
        )

        # 4. Honest RATE_SUPPRESSION with OUTFLOW_DRAIN="N/A" and honest
        #    CUMULATIVE_STACKING_TOXIN with PROPAGATION="N/A" must achieve full required-primitive fit.
        rate_sup = classify_primitive_signature({
            "CHANNEL_TYPE": "Cold chill/freeze or API rate limiter",
            "OUTFLOW_DRAIN": "N/A",
            "CONTROL_LOOP": "Cuts action speed via throttling rather than draining pool",
            "THRESHOLD": "Freeze threshold halts all actions",
            "COUNTERPLAY": "Action speed floor or stasis cleanse",
        })
        self.assertEqual(rate_sup["primary_class"], InvariantClass.RATE_SUPPRESSION.value)
        self.assertEqual(rate_sup["matches"][0]["matched_required_primitives"], ["CONTROL_LOOP"])
        self.assertGreaterEqual(rate_sup["matches"][0]["score"], 0.9)

        poison = classify_primitive_signature({
            "CHANNEL_TYPE": "Chaos poison",
            "OUTFLOW_DRAIN": "Independent poison stacks with own timers scaling with exposure count",
            "PROPAGATION": "N/A",
            "COUNTERPLAY": "Cleanse or poison immunity",
        })
        self.assertEqual(poison["primary_class"], InvariantClass.CUMULATIVE_STACKING_TOXIN.value)
        self.assertEqual(poison["matches"][0]["matched_required_primitives"], ["OUTFLOW_DRAIN"])
        self.assertGreaterEqual(poison["matches"][0]["score"], 0.9)

    def test_prediction_gate_discipline_all_rules(self) -> None:
        # 1. Verified ISOMORPHIC_INVARIANT with concrete evidence_ids -> 1.0 allowed
        confirmed = evaluate_invariant_prediction(
            source_domain="poe_chaos_inoculation",
            target_domain="air_gapped_security",
            source_failure_or_counterplay="bypass channel reaching life=1 floor",
            predicted_target_counterpart="USB insider transfer bypassing network air gap (Stuxnet)",
            ground_class=GroundClass.PHYSICAL,
            prediction_tested=True,
            prediction_confirmed=True,
            source_is_fiction_or_game=True,
            target_is_real_system=True,
            evidence_ids=["EV-STUXNET-2010"],
            raw_gate_scores={"causal_validity": 1.0, "boundary_integrity": 1.0},
        )
        self.assertEqual(confirmed["classification"], "ISOMORPHIC_INVARIANT")
        self.assertEqual(confirmed["max_allowed_gate_score"], 1.0)
        self.assertFalse(confirmed["gate_cap_applied"])
        self.assertEqual(confirmed["gate_scores"]["causal_validity"], 1.0)
        # SC-PATCH-DU-001: fiction/game -> real carries substrate_confusion_check (material blocked, positional permitted)
        self.assertTrue(confirmed["substrate_confusion_check"])
        self.assertTrue(confirmed["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", confirmed)

        # 2. Untested prediction caps gates at 0.9 and populates uncertainty_statement
        untested = evaluate_invariant_prediction(
            source_domain="pokemon_fire",
            target_domain="network_cascade",
            source_failure_or_counterplay="oxygen smothering",
            predicted_target_counterpart="circuit breaker starving retry loop",
            ground_class=GroundClass.PHYSICAL,
            prediction_tested=False,
            raw_gate_scores={"causal_validity": 1.0, "scale_integrity": 0.95, "boundary_integrity": 0.8},
        )
        self.assertEqual(untested["classification"], "UNTESTED_HYPOTHESIS")
        self.assertEqual(untested["max_allowed_gate_score"], 0.9)
        self.assertTrue(untested["gate_cap_applied"])
        self.assertEqual(untested["gate_scores"]["causal_validity"], 0.9)
        self.assertEqual(untested["gate_scores"]["scale_integrity"], 0.9)
        self.assertEqual(untested["gate_scores"]["boundary_integrity"], 0.8)
        self.assertTrue(untested["untested_predictions"])
        self.assertIn("oxygen smothering", untested["uncertainty_statement"])

        # 3. Confirmed without evidence_ids cannot reach 1.0
        no_evidence = evaluate_invariant_prediction(
            source_domain="biology",
            target_domain="agentic_loops",
            source_failure_or_counterplay="loss of apoptosis",
            predicted_target_counterpart="missing stop budget",
            prediction_tested=True,
            prediction_confirmed=True,
            evidence_ids=[],
        )
        self.assertEqual(no_evidence["classification"], "UNTESTED_HYPOTHESIS")
        self.assertEqual(no_evidence["max_allowed_gate_score"], 0.9)

        # 4. Strength-only match -> STRUCTURAL_ANALOGY
        analogy = evaluate_invariant_prediction(
            source_domain="jjk",
            target_domain="llm_deployment",
            source_failure_or_counterplay="sure-hit strength",
            predicted_target_counterpart="in-distribution accuracy",
            strength_match_only=True,
            prediction_tested=True,
            prediction_confirmed=True,
            evidence_ids=["EV-01"],
        )
        self.assertEqual(analogy["classification"], "STRUCTURAL_ANALOGY")
        self.assertEqual(analogy["max_allowed_gate_score"], 0.9)
        self.assertTrue(analogy["substrate_confusion_check"])
        self.assertTrue(analogy["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", analogy)

        # 5. BALANCE_ONLY -> ALWAYS mandatory residual mismatch, never ISOMORPHIC_INVARIANT
        balance = evaluate_invariant_prediction(
            source_domain="pokemon",
            target_domain="physics",
            source_failure_or_counterplay="Bug beats Dark",
            predicted_target_counterpart="none",
            ground_class=GroundClass.BALANCE_ONLY,
            prediction_tested=True,
            prediction_confirmed=True,
            evidence_ids=["EV-FORCE"],
            raw_gate_scores={"causal_validity": 1.0},
        )
        self.assertEqual(balance["classification"], "RESIDUAL_MISMATCH")
        self.assertTrue(balance["residual_mismatches"])
        self.assertEqual(balance["max_allowed_gate_score"], 0.9)
        self.assertEqual(balance["gate_scores"]["causal_validity"], 0.9)
        self.assertTrue(balance["substrate_confusion_check"])
        self.assertTrue(balance["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", balance)

        # 6. Non-empty information_lost guarantees non-empty residual_mismatches
        lossy = evaluate_invariant_prediction(
            source_domain="thermodynamics",
            target_domain="finance",
            source_failure_or_counterplay="entropy dissipation",
            predicted_target_counterpart="liquidity drain",
            ground_class=GroundClass.PHYSICAL,
            prediction_tested=True,
            prediction_confirmed=True,
            evidence_ids=["EV-FIN-01"],
            information_lost=["conservation of energy does not strictly hold in fiat credit expansion"],
        )
        self.assertTrue(lossy["residual_mismatches"])
        self.assertIn("fiat credit expansion", lossy["residual_mismatches"][0])

        # 7. Real -> real verified invariant allows identity claim
        real_to_real = evaluate_invariant_prediction(
            source_domain="electrical_engineering",
            target_domain="lightning_protection",
            source_failure_or_counterplay="low-impedance earth sink",
            predicted_target_counterpart="grounding rod discharges potential",
            ground_class=GroundClass.PHYSICAL,
            prediction_tested=True,
            prediction_confirmed=True,
            source_is_fiction_or_game=False,
            target_is_real_system=True,
            evidence_ids=["EV-IEEE-142"],
        )
        self.assertEqual(real_to_real["classification"], "ISOMORPHIC_INVARIANT")
        self.assertTrue(real_to_real["substrate_confusion_check"])
        self.assertTrue(real_to_real["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", real_to_real)

        # 8. Falsified tested prediction -> RESIDUAL_MISMATCH + non-empty residuals
        falsified = evaluate_invariant_prediction(
            source_domain="pokemon_water",
            target_domain="electrical_grid",
            source_failure_or_counterplay="pure water conducts electricity",
            predicted_target_counterpart="deionized water shorts transformers",
            ground_class="BIOLOGICAL / ECOLOGICAL",
            prediction_tested=True,
            prediction_confirmed=False,
            raw_gate_scores={"causal_validity": 1.0},
        )
        self.assertEqual(falsified["classification"], "RESIDUAL_MISMATCH")
        self.assertEqual(falsified["ground_class"], GroundClass.BIOLOGICAL_ECOLOGICAL.value)
        self.assertTrue(falsified["residual_mismatches"])
        self.assertEqual(falsified["gate_scores"]["causal_validity"], 0.9)
        self.assertTrue(falsified["substrate_confusion_check"])
        self.assertTrue(falsified["positional_claims_permitted"])
        self.assertNotIn("identity_claim_allowed", falsified)

        # 9. SKILL.md display string "BALANCE-ONLY" and invalid gate scores validation
        bal_str = evaluate_invariant_prediction(
            source_domain="game",
            target_domain="real",
            source_failure_or_counterplay="x",
            predicted_target_counterpart="y",
            ground_class="BALANCE-ONLY",
        )
        self.assertEqual(bal_str["classification"], "RESIDUAL_MISMATCH")
        self.assertTrue(bal_str["residual_mismatches"])

        with self.assertRaises(ValueError):
            evaluate_invariant_prediction(
                source_domain="a",
                target_domain="b",
                source_failure_or_counterplay="x",
                predicted_target_counterpart="y",
                raw_gate_scores={"causal_validity": 1.2},
            )

        # 10. Strict validation against bare strings, contradictory tested/confirmed,
        #     empty required text, and typos in canonical gate names.
        with self.assertRaises(ValueError):
            evaluate_invariant_prediction(
                source_domain="a",
                target_domain="b",
                source_failure_or_counterplay="x",
                predicted_target_counterpart="y",
                prediction_tested=False,
                prediction_confirmed=True,
            )
        with self.assertRaises(ValueError):
            evaluate_invariant_prediction(
                source_domain="a",
                target_domain="b",
                source_failure_or_counterplay="x",
                predicted_target_counterpart="y",
                evidence_ids="EV-01",  # type: ignore[arg-type]
            )
        with self.assertRaises(ValueError):
            evaluate_invariant_prediction(
                source_domain="a",
                target_domain="b",
                source_failure_or_counterplay="x",
                predicted_target_counterpart="y",
                information_lost="energy conservation",  # type: ignore[arg-type]
            )
        with self.assertRaises(ValueError):
            evaluate_invariant_prediction(
                source_domain="  ",
                target_domain="b",
                source_failure_or_counterplay="x",
                predicted_target_counterpart="y",
            )
        with self.assertRaises(ValueError):
            evaluate_invariant_prediction(
                source_domain="a",
                target_domain="b",
                source_failure_or_counterplay="x",
                predicted_target_counterpart="y",
                raw_gate_scores={"causal_validty": 0.9},
            )

        # 11. Combined BALANCE_ONLY + falsified prediction records both residual reasons
        both_res = evaluate_invariant_prediction(
            source_domain="pokemon",
            target_domain="physics",
            source_failure_or_counterplay="Bug beats Dark",
            predicted_target_counterpart="insects defeat shadow",
            ground_class=GroundClass.BALANCE_ONLY,
            prediction_tested=True,
            prediction_confirmed=False,
        )
        self.assertEqual(both_res["classification"], "RESIDUAL_MISMATCH")
        self.assertEqual(len(both_res["residual_mismatches"]), 2)


if __name__ == "__main__":
    unittest.main()
