"""SC-MIRROR-001 (capstone unification) and SC-LU-FRIEZA-001 (outsider lineup), 2026-11-25.

Checks schema parity with SC-DE-001, the spec's TIG grades and gate caps, the
section 8 "what not to do" rules, cross-reference honesty, and routing.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from semantic_compiler import compile_semantic_packet
from semantic_compiler.expansion.router import ROUTED, route_domains

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPILED_DIR = REPO_ROOT / "calibration_output" / "compiled_entries"
DEPTS = {
    "SUBCONSCIOUS", "INNER_MONOLOGUE", "SPEECH_OUTPUT", "STORAGE", "SECURITY",
    "TELECOMMUNICATIONS", "ENERGY_INTAKE", "DISPLAY", "PROCESSOR", "REPRODUCTION",
    "DELETION", "WASTE_REMOVAL", "APPLICATION", "RENDERING_OVERHEAD", "INFORMATION_DENSITY",
}
SCALES = {"AI", "HUMAN", "SOCIETAL", "COSMOLOGICAL"}
FIVE = ("SC-CT-001", "SC-DU-001", "SC-CP-001", "SC-SB-001", "SC-HS-001")


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, f"{name}: expected single-line JSONL, got {len(lines)}"
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
MIRROR = _single("SC-MIRROR-001.jsonl")
FRIEZA = _single("SC-LU-FRIEZA-001.jsonl")
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_IDS = {e["entry_id"] for e in MANIFEST["entries"]}


class SchemaParityTests(unittest.TestCase):
    def test_top_level_keys_match_sc_de_001_exactly(self) -> None:
        for entry in (MIRROR, FRIEZA):
            with self.subTest(entry=entry["metadata"]["entry_id"]):
                self.assertEqual(list(entry.keys()), list(TEMPLATE.keys()))

    def test_nested_sc_de_001_keys_are_present(self) -> None:
        for entry in (MIRROR, FRIEZA):
            for section in ("metadata", "analysis", "structural_skeleton", "translations", "isomorphism_quality",
                            "dataset_value", "v2_extensions", "outputs", "training_payloads"):
                with self.subTest(entry=entry["metadata"]["entry_id"], section=section):
                    self.assertTrue(set(TEMPLATE[section]) <= set(entry[section]))
            for gate in TEMPLATE["gates"]:
                self.assertTrue(set(TEMPLATE["gates"][gate]) <= set(entry["gates"][gate]))
            for mp in entry["isomorphism_analysis"]["mappings"]:
                self.assertTrue(set(TEMPLATE["isomorphism_analysis"]["mappings"][0]) <= set(mp))
                self.assertIs(mp["substrate_confusion_check"], True)
                self.assertIs(mp["positional_claims_permitted"], True)
                self.assertNotIn("identity_claim_allowed", mp)
                self.assertTrue(mp["residual_mismatches"])

    def test_metadata_values(self) -> None:
        md = MIRROR["metadata"]
        self.assertEqual(md["entry_id"], "SC-MIRROR-001")
        self.assertEqual(md["compiler_mode"], "UNIVERSAL_DECOMPRESSION")
        self.assertEqual(md["framework"], "Systemic Isomorphic Invariants")
        self.assertEqual(md["version"], "3.5.0")
        self.assertEqual(md["source"], "Shax (Curtis Kingsley) — Reflexion Software")
        self.assertTrue(md["timestamp"].startswith("2026-11-25"))
        self.assertEqual(md["title"], "The Mirrored Loop and the Compression Protocol")
        self.assertEqual(md["patch_type"], "NEW_ENTRY")
        self.assertEqual(md["cross_references"],
                         ["SC-CT-001", "SC-DU-001", "SC-CP-001", "SC-SB-001", "SC-HS-001", "SC-OMNI-001", "SC-DR-001"])
        self.assertEqual(FRIEZA["metadata"]["entry_id"], "SC-LU-FRIEZA-001")

    def test_fifteen_departments_four_scales(self) -> None:
        for entry in (MIRROR, FRIEZA):
            depts = entry["functional_departments"]
            self.assertEqual({d["department"] for d in depts}, DEPTS)
            self.assertEqual(len(depts), 15)
            for d in depts:
                self.assertEqual(set(d["scales"]), SCALES)
                self.assertEqual(len(d["expected_at_scale"].split(" / ")), 4)
                self.assertTrue(d["implication"])

    def test_mirror_departments_show_all_five_views_then_synthesis(self) -> None:
        for d in MIRROR["functional_departments"]:
            self.assertEqual(tuple(d["source_manifestations"]), FIVE)
            self.assertTrue(d["synthesis"])


class GradeTests(unittest.TestCase):
    def test_six_claims_with_spec_tig_grades(self) -> None:
        grades = {c["label"]: c["tig_grade"] for c in MIRROR["analysis"]["claims"]}
        self.assertEqual(grades, {
            "UNIFICATION": "GOLD",
            "YIN-YANG DOT": "ANALOGOUS",
            "INFORMATION CONSERVATION": "ANCHORED",
            "THREE-STAGE COMPRESSION": "ANALOGOUS",
            "BACKUP HYPOTHESIS": "OPEN_HYPOTHESIS",
            "ANTI-DEADLOCK PROTOCOL": "ISOMORPHIC_INVARIANT",
        })

    def test_entry_is_silver_not_gold_and_caps_hold(self) -> None:
        for entry in (MIRROR, FRIEZA):
            self.assertEqual(entry["dataset_tier"], "SILVER")
            self.assertEqual(entry["dataset_utility_tier"], "SILVER")
            self.assertEqual(len(entry["gates"]), 9)
            self.assertTrue(all(g["passed"] for g in entry["gates"].values()))
        self.assertLessEqual(MIRROR["gates"]["measurement_integrity"]["score"], 0.7)
        self.assertLessEqual(MIRROR["gates"]["corpus_completeness"]["score"], 0.85)
        self.assertLess(MIRROR["isomorphism_quality"]["score"], 0.9)

    def test_backup_hypothesis_not_smuggled_into_anchored(self) -> None:
        anchored = [c for c in MIRROR["analysis"]["claims"] if c["tig_grade"] == "ANCHORED"]
        self.assertEqual([c["label"] for c in anchored], ["INFORMATION CONSERVATION"])
        self.assertNotIn("backup", anchored[0]["text"].lower())
        backup = next(c for c in MIRROR["analysis"]["claims"] if c["label"] == "BACKUP HYPOTHESIS")
        self.assertEqual(backup["extends"], "SC-HS-001/CLM-HS-002B")
        hs = _single("SC-HS-001_FLAT_FLRW_HUBBLE_SCHWARZSCHILD_PATCH.jsonl")
        tig = {t["claim_id"]: t["tig"] for t in hs["gate_0_tig"]}
        self.assertTrue(tig["CLM-HS-002B"].startswith("OPEN_HYPOTHESIS"))

    def test_three_stages_sequential_and_distinct(self) -> None:
        three = next(c for c in MIRROR["analysis"]["claims"] if c["label"] == "THREE-STAGE COMPRESSION")
        stages = three["stages"]
        self.assertEqual([s["order"] for s in stages], [1, 2, 3])
        self.assertEqual([s["stage"] for s in stages], ["ABSORPTION", "COMPRESSION", "OUTPUT"])
        self.assertEqual(len({s["theological_event"] for s in stages}), 3)
        self.assertEqual(stages[2]["tig_grade"], "OPEN_HYPOTHESIS")

    def test_no_endgame_or_solved_language(self) -> None:
        for entry in (MIRROR, FRIEZA):
            body = json.dumps({k: v for k, v in entry.items() if k != "input"}, ensure_ascii=False)
            self.assertEqual(re.findall(r"\b(endgame|solved)\b", body, re.IGNORECASE), [])

    def test_dragon_ball_evidence_map_kept(self) -> None:
        instances = " ".join(i["instance"] for i in MIRROR["analysis"]["dragon_ball_evidence_map"])
        for name in ("Kami / Piccolo", "Goku / Vegeta", "Spirit Bomb", "Frieza"):
            self.assertIn(name, instances)


class CrossReferenceHonestyTests(unittest.TestCase):
    def test_unresolved_references_are_not_invented(self) -> None:
        res = MIRROR["metadata"]["cross_reference_resolution"]
        unresolved = {k for k, v in res.items() if v["status"] == "UNRESOLVED"}
        self.assertEqual(unresolved, {"SC-CP-001", "SC-LU-PICCOLO-001", "SC-LU-GOKU-001",
                                      "SC-LU-VEGETA-001", "SC-LU-BUU-001"})
        self.assertEqual(unresolved, set(MIRROR["metadata"]["unresolved_cross_references"]))
        for ref in unresolved:
            self.assertNotIn(ref, MANIFEST_IDS)
            self.assertFalse(list(COMPILED_DIR.glob(f"*{ref}*")))

    def test_resolved_references_exist(self) -> None:
        res = MIRROR["metadata"]["cross_reference_resolution"]
        for ref, v in res.items():
            if v["status"] == "RESOLVED":
                self.assertIn(ref, MANIFEST_IDS)
            elif v["status"] == "RESOLVED_BY_ALIAS":
                self.assertIn(v["alias_of"], MANIFEST_IDS)

    def test_frieza_keeps_all_five_layers_including_outside_ownership_and_invasion(self) -> None:
        layers_claim = next(c for c in FRIEZA["analysis"]["claims"] if c["claim_id"] == "CLM-LU-FRZ-02")
        layers = {lay["layer"]: lay for lay in layers_claim["layers"]}
        self.assertEqual(sorted(layers), ["A", "B", "C", "D", "E"])
        for k in "ABC":
            self.assertEqual(layers[k]["grade"], "OPEN_HYPOTHESIS")
        for k in "DE":
            self.assertEqual(layers[k]["grade"], "CANON")
        self.assertIn("owned", layers["B"]["text"])
        self.assertIn("another entity", layers["B"]["text"])
        self.assertIn("invasion", layers["C"]["text"])
        self.assertIn("black-hole", layers["A"]["text"])

    def test_sb_patch_notes_carry_child_invariant(self) -> None:
        notes = (REPO_ROOT / "docs" / "SC-SB-001_THREE_CLAIM_STRUCTURE.md").read_text(encoding="utf-8")
        self.assertIn("COLLECTIVE INPUT / STRUCTURAL RESPONSE", notes)
        self.assertIn("DRAFT 0.2", notes)
        for name in ("Vegeta", "Frieza", "Kid Buu"):
            self.assertIn(name, notes)


class RoutingTests(unittest.TestCase):
    def test_frieza_outsider_routes_to_lineup_home(self) -> None:
        for text in (
            "The outsider's first investment: Frieza's lineage comes from a black-hole domain outside the "
            "universe and invests in the strongest local system before infiltrating it.",
            "Black Frieza trained ten years in a time-dilated chamber on a conquered planet and one-shot "
            "Ultra Instinct Goku and Ultra Ego Vegeta: substrate activation.",
        ):
            with self.subTest(text=text[:40]):
                result = route_domains(text)
                self.assertEqual(result.outcome, ROUTED, result.to_dict())
                self.assertEqual(result.domain, "soul_bomb_sovereignty")

    def test_named_frieza_prompt_compiles_in_lineup_home(self) -> None:
        packet = compile_semantic_packet(
            "Black Frieza trained ten years in a time-dilated chamber on a conquered planet and one-shot "
            "Ultra Instinct Goku and Ultra Ego Vegeta: substrate activation.")
        self.assertEqual(packet.selected_target, "soul_bomb_sovereignty")

    def test_frieza_outsider_compiles_in_routed_home_despite_weak_frames(self) -> None:
        # Two weak table frames ("lineage", "system") used to keep the table
        # target `computation` ahead of a 0.96-confidence router result.
        # Scope: weak frames only. "Frieza's black hole origin is owned by another
        # entity..." has a strong `cosmological` frame and keeps the table path
        # (target `computation`); changing strong-frame precedence is out of scope.
        for text in (
            "The outsider's first investment: Frieza's lineage comes from a black-hole domain outside the "
            "universe and invests in the strongest local system before infiltrating it.",
        ):
            with self.subTest(text=text[:40]):
                packet = compile_semantic_packet(text)
                self.assertEqual(packet.selected_target, "soul_bomb_sovereignty")
                self.assertTrue(any(w.startswith("ROUTED_DOMAIN:") for w in packet.compiler_warnings))

    def test_entry_ids_route_to_home_domains(self) -> None:
        self.assertEqual(route_domains("Explain SC-MIRROR-001.").domain, "client_server_reality")
        self.assertEqual(route_domains("Explain SC-LU-FRIEZA-001.").domain, "soul_bomb_sovereignty")

    def test_mirror_prompts_route(self) -> None:
        cases = {
            "When two sovereign entities are locked in a mirror match, the resolution is voluntary fusion "
            "that preserves both sovereignties, like Kami and Piccolo or Vegito, not victory or defeat.": "soul_bomb_sovereignty",
            "The yin-yang dot is a calibration tool, not a mandate: darkness cannot be deleted, only compressed "
            "and converted, so the 50/50 state becomes a white field with a black calibration dot.": "client_server_reality",
            "Absorption at the Cross, compression at the Rapture, output as New Heaven and New Earth: three "
            "sequential stages, not one event.": "client_server_reality",
        }
        for text, domain in cases.items():
            with self.subTest(text=text[:40]):
                self.assertEqual(route_domains(text).domain, domain)

    def test_generic_black_hole_prompt_not_pulled_by_new_entries(self) -> None:
        # Regression guard: a long SC-MIRROR-001 input made this AMBIGUOUS
        # (soul_bomb_sovereignty vs psychology) through the compiled-entry lift.
        result = route_domains("A black hole remembers everything it consumes.")
        self.assertEqual(result.outcome, ROUTED)
        self.assertEqual(result.domain, "psychology")

    def test_compact_inputs(self) -> None:
        # Patch-entry convention (SC-HS-001, SC-OMNI-001, SC-SB-001): short input, spec kept in docs/.
        self.assertLess(len(MIRROR["input"]), 1000)
        self.assertLess(len(FRIEZA["input"]), 1000)
        self.assertTrue((REPO_ROOT / "docs" / "SC-MIRROR-001_ENGINEERING_SPEC.md").is_file())

    def test_everyday_prompt_still_passes_through_byte_for_byte(self) -> None:
        text = "Can you set an alarm for 7am tomorrow?"
        packet = compile_semantic_packet(text)
        self.assertEqual(packet.decision.name, "PASS_THROUGH")
        self.assertEqual(packet.forward_text, text)


if __name__ == "__main__":
    unittest.main()
