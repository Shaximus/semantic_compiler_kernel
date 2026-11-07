"""Regression coverage for the buildcraft/compute ontology."""

from __future__ import annotations

import unittest

from semantic_compiler.registry.buildcraft import BUILDCRAFT_MAPPINGS, get_buildcraft_mapping
from semantic_compiler.translation.buildcraft import (
    ALIASES,
    RULES,
    resolve_buildcraft_entries,
    resolve_buildcraft_mappings,
    summarize_buildcraft_ontology,
)
from semantic_compiler.translation.structural_resolver import resolve_rules


class BuildcraftOntologyTests(unittest.TestCase):
    def test_mapping_ids_are_unique(self) -> None:
        ids = [mapping.mapping_id for mapping in BUILDCRAFT_MAPPINGS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_mapping_has_invariants_and_residuals(self) -> None:
        for mapping in BUILDCRAFT_MAPPINGS:
            self.assertGreaterEqual(len(mapping.preserved_invariants), 3, mapping.mapping_id)
            self.assertGreaterEqual(len(mapping.residuals), 2, mapping.mapping_id)

    def test_slots_items_and_software_remain_distinct(self) -> None:
        entries = resolve_buildcraft_entries(
            "PCIe slots are weapon slots; the GPU is the weapon; "
            "the CPU socket is the body armour slot and the CPU is the armour."
        )
        ids = {entry.mapping_id for entry in entries}
        self.assertTrue({"BUILD_002", "BUILD_003", "BUILD_004", "BUILD_005"}.issubset(ids))

    def test_vram_is_mana_reservation(self) -> None:
        entries = resolve_buildcraft_entries("VRAM allocation is mana reservation.")
        self.assertIn("BUILD_010", {entry.mapping_id for entry in entries})

    def test_llm_runtime_and_compatibility_layers_remain_distinct(self) -> None:
        entries = resolve_buildcraft_entries(
            "The LLM is the active skill gem; MTP is a support gem; "
            "CUDA and PyTorch define runtime compatibility."
        )
        ids = {entry.mapping_id for entry in entries}
        self.assertTrue({"BUILD_007", "BUILD_008", "BUILD_009"}.issubset(ids))

    def test_repository_role_is_classified_by_function(self) -> None:
        mapping = get_buildcraft_mapping("BUILD_011")
        self.assertIsNotNone(mapping)
        assert mapping is not None
        joined = " ".join(mapping.preserved_invariants).lower()
        self.assertIn("artifact format", joined)

    def test_rtx_pro_mapping_rejects_literal_identity(self) -> None:
        mappings = resolve_buildcraft_mappings(
            "The RTX PRO 6000 Blackwell 96 GB is a mirror-tier 10 link bow."
        )
        premium = next(mapping for mapping in mappings if mapping["mapping_id"] == "BUILD_014")
        self.assertFalse(premium["identity_claim_allowed"])
        self.assertEqual(premium["mapping_class"], "STRUCTURAL_ANALOGY")

    def test_dense_statement_recovers_hierarchy(self) -> None:
        entries = resolve_buildcraft_entries(
            "PCIe slots hold the GPU, the CPU carries utility, "
            "the LLM and support gems consume VRAM through CUDA and PyTorch."
        )
        ids = {entry.mapping_id for entry in entries}
        self.assertTrue({"BUILD_002", "BUILD_004", "BUILD_005", "BUILD_007", "BUILD_008", "BUILD_009", "BUILD_010"}.issubset(ids))

    def test_summary_exposes_canonical_chain(self) -> None:
        summary = summarize_buildcraft_ontology(
            "Reflexion of Building uses PCIe weapon slots and VRAM mana reservation."
        )
        chain = " ".join(summary["canonical_chain"])
        self.assertIn("PCIe accelerator slot", chain)
        self.assertIn("VRAM occupancy", chain)

    # --- Founder eureka 2026-07-23: BUILD_015-BUILD_018 ---

    def test_pc_case_is_character_selection_screen(self) -> None:
        entries = resolve_buildcraft_entries(
            "The PC case is the character selection screen: the vessel chosen at creation."
        )
        self.assertIn("BUILD_015", {entry.mapping_id for entry in entries})

    def test_motherboard_is_race_base_class(self) -> None:
        entries = resolve_buildcraft_entries("The motherboard is the race, not the gear.")
        ids = {entry.mapping_id for entry in entries}
        self.assertIn("BUILD_016", ids)
        mapping = get_buildcraft_mapping("BUILD_016")
        assert mapping is not None
        joined = " ".join(mapping.preserved_invariants).lower()
        self.assertIn("socket types", joined)
        self.assertIn("expansion ceilings", joined)

    def test_mtp_is_multi_projectile_support(self) -> None:
        mappings = resolve_buildcraft_mappings("MTP is literally multi-projectile support.")
        ids = {mapping["mapping_id"] for mapping in mappings}
        self.assertIn("BUILD_017", ids)
        mtp = next(mapping for mapping in mappings if mapping["mapping_id"] == "BUILD_017")
        self.assertFalse(mtp["identity_claim_allowed"])
        self.assertEqual(mtp["mapping_class"], "STRUCTURAL_ANALOGY")
        joined = " ".join(mtp["preserved_invariants"]).lower()
        self.assertIn("acceptance rate", joined)
        self.assertIn("accuracy rating", joined)
        self.assertIn("breakpoint", joined)

    def test_mirror_tier_gpu_is_mirror_of_kalandra(self) -> None:
        entries = resolve_buildcraft_entries(
            "A mirror-tier GPU like the RTX PRO 6000 96GB is a Mirror-of-Kalandra-tier item."
        )
        ids = {entry.mapping_id for entry in entries}
        self.assertIn("BUILD_018", ids)
        mapping = get_buildcraft_mapping("BUILD_018")
        assert mapping is not None
        joined = " ".join(mapping.preserved_invariants).lower()
        self.assertIn("no upgrade path", joined)
        self.assertIn("perfect roll", joined)

    def test_static_vs_dynamic_guardrail_on_records(self) -> None:
        for mapping_id in ("BUILD_015", "BUILD_016", "BUILD_017", "BUILD_018"):
            mapping = get_buildcraft_mapping(mapping_id)
            assert mapping is not None
            guardrails = " ".join(mapping.to_fractal_mapping()["guardrails"]).lower()
            self.assertIn("static at craft time", guardrails, mapping_id)
            self.assertIn("optimization structure", guardrails, mapping_id)
            self.assertIn("breakpoints", guardrails, mapping_id)
            self.assertFalse(mapping.to_fractal_mapping()["identity_claim_allowed"], mapping_id)


class BuildcraftResolverRegressionTests(unittest.TestCase):
    """Regressions for the 2026-11 resolver review.

    Each test pins a defect that was reproduced against the shipped V3.0.0
    resolver before it was repaired.
    """

    @staticmethod
    def _structural_ids(text: str) -> set[str]:
        _, matches = resolve_rules(text, ALIASES, RULES)
        return {match.rule_id for match in matches}

    @staticmethod
    def _final_ids(text: str) -> set[str]:
        return {entry.mapping_id for entry in resolve_buildcraft_entries(text)}

    def test_slot_sentences_resolve_slot_mappings_not_item_mappings(self) -> None:
        # Previously "CPU socket is the body armour slot" structurally resolved
        # BUILD_005 (CPU is armour) and "accelerator slot is the weapon slot"
        # resolved BUILD_004 (GPU is weapon): the longer slot alias was
        # overwritten by the item alias it contained.
        self.assertEqual(self._structural_ids("PCIe slots are weapon slots."), {"BUILD_002"})
        self.assertEqual(self._structural_ids("The CPU socket is the body armour slot."), {"BUILD_003"})
        self.assertEqual(self._structural_ids("The accelerator slot is the weapon slot."), {"BUILD_002"})

    def test_slot_sentences_do_not_assert_their_item_through_fallback(self) -> None:
        self.assertEqual(self._final_ids("The CPU socket is the body armour slot."), {"BUILD_003"})
        self.assertEqual(self._final_ids("The accelerator slot is the weapon slot."), {"BUILD_002"})

    def test_complete_build_does_not_resolve_topology(self) -> None:
        # BUILD_001 was keyed on the same concept as BUILD_012.
        ids = self._final_ids("This is a complete build.")
        self.assertIn("BUILD_012", ids)
        self.assertNotIn("BUILD_001", ids)
        self.assertIn(
            "BUILD_001",
            self._final_ids("The motherboard topology is the equipment paper doll."),
        )

    def test_trigger_layer_respects_word_boundaries(self) -> None:
        # "abi" in capability/probability, "repo" in report, "gem" in management.
        for text in (
            "The new capability improves probability estimates.",
            "The quarterly report is due Friday.",
            "The management model is strong.",
        ):
            self.assertEqual(self._final_ids(text), set(), text)

    def test_trigger_layer_keeps_plural_and_inflected_recall(self) -> None:
        ids = self._final_ids("Several GPUs reserved VRAM; the drivers and repos matter.")
        self.assertTrue({"BUILD_004", "BUILD_010", "BUILD_009", "BUILD_011"}.issubset(ids), ids)

    def test_negated_relation_is_not_structural_support(self) -> None:
        for text in ("A GPU is not a weapon.", "The GPU isn't a weapon."):
            self.assertNotIn("BUILD_004", self._structural_ids(text), text)
            mappings = {m["mapping_id"]: m for m in resolve_buildcraft_mappings(text)}
            self.assertIn(
                "relation_negated_in_source",
                mappings["BUILD_004"]["resolver_evidence"]["reasons"],
                text,
            )

    def test_non_equivalence_relation_is_not_equivalence_evidence(self) -> None:
        self.assertNotIn("BUILD_007", self._structural_ids("The LLM uses an active skill."))

    def test_vram_reservation_resolves_structurally(self) -> None:
        # BUILD_010 has two alternative relation patterns; neither could reach
        # the threshold on its own before the fix.
        self.assertIn("BUILD_010", self._structural_ids("VRAM allocation is mana reservation."))
        self.assertIn("BUILD_010", self._structural_ids("The LLM and MTP consume VRAM."))


if __name__ == "__main__":
    unittest.main()
