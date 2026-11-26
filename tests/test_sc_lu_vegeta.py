"""SC-LU-VEGETA-001 (Sovereignty-pole lineup), SC-VESSEL-001, and t572u complicit enslavement.

Checks SC-DE-001 schema parity, honest grading (anime-original flag, Shax
interpretation, VSR verdict), the additive cross-reference resolution in
SC-MIRROR-001 / SC-LU-FRIEZA-001 / SC-CP-001 / SC-DU-001, and routing.
"""

from __future__ import annotations

import hashlib
import json
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


def _single(name: str) -> dict:
    lines = [ln for ln in (COMPILED_DIR / name).read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, f"{name}: expected single-line JSONL, got {len(lines)}"
    return json.loads(lines[0])


TEMPLATE = _single("DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
VEGETA = _single("SC-LU-VEGETA-001.jsonl")
MIRROR = _single("SC-MIRROR-001.jsonl")
FRIEZA = _single("SC-LU-FRIEZA-001.jsonl")
CLAY = _single("SC-CP-001_CLAY_AND_POTS.jsonl")
DUALITY = _single("SC-DU-001_THE_DUALITY.jsonl")
MANIFEST = json.loads((COMPILED_DIR / "manifest.json").read_text(encoding="utf-8"))
CLAIMS = {c["claim_id"]: c for c in VEGETA["analysis"]["claims"]}


class VegetaSchemaTests(unittest.TestCase):
    def test_top_level_keys_match_sc_de_001_exactly(self) -> None:
        self.assertEqual(list(VEGETA.keys()), list(TEMPLATE.keys()))

    def test_nested_keys_departments_gates_and_mappings(self) -> None:
        for section in ("metadata", "analysis", "structural_skeleton", "translations", "isomorphism_quality",
                        "dataset_value", "v2_extensions", "outputs", "training_payloads"):
            self.assertTrue(set(TEMPLATE[section]) <= set(VEGETA[section]), section)
        self.assertEqual(set(VEGETA["gates"]), set(TEMPLATE["gates"]))
        self.assertTrue(all(g["passed"] for g in VEGETA["gates"].values()))
        self.assertEqual({d["department"] for d in VEGETA["functional_departments"]}, DEPTS)
        for d in VEGETA["functional_departments"]:
            self.assertEqual(set(d["scales"]), SCALES)
        for mp in VEGETA["isomorphism_analysis"]["mappings"]:
            self.assertIs(mp["substrate_confusion_check"], True)
            self.assertIs(mp["positional_claims_permitted"], True)
            self.assertNotIn("identity_claim_allowed", mp)
            self.assertTrue(mp["residual_mismatches"])

    def test_input_stays_short_so_generic_prompts_are_not_lifted(self) -> None:
        self.assertLess(len(VEGETA["input"]), 400)

    def test_tier_is_silver_and_matches_geometric_mean(self) -> None:
        scores = [g["score"] for g in VEGETA["gates"].values()]
        prod = 1.0
        for s in scores:
            prod *= s
        self.assertAlmostEqual(VEGETA["isomorphism_quality"]["score"], round(prod ** (1 / len(scores)), 3), places=3)
        self.assertEqual(VEGETA["dataset_tier"], "SILVER")
        self.assertEqual(VEGETA["semantic_quality_tier"], "COMPILED_WITH_GUARDRAILS")
        self.assertLessEqual(VEGETA["gates"]["measurement_integrity"]["score"], 0.7)


class VegetaGradingTests(unittest.TestCase):
    def test_ultra_ego_is_canon_with_secondary_source_yin_yang(self) -> None:
        c = CLAIMS["CLM-LU-VEG-01"]
        self.assertIn("ch. 74", c["text"])
        grades = {e["grade"] for e in c["evidence"]}
        self.assertEqual(grades, {"CANON", "SECONDARY_SOURCE"})

    def test_offering_is_flagged_anime_original_with_version_variance(self) -> None:
        c = CLAIMS["CLM-LU-VEG-02"]
        self.assertIn("ANIME_ORIGINAL", c["tig_grade"])
        by_grade = {v["grade"]: v for v in c["versions"]}
        self.assertIn("ep. 78", by_grade["CANON (ANIME_ORIGINAL)"]["source"])
        self.assertTrue(any("Broly" in v["source"] for v in c["versions"]))
        self.assertTrue(any("does not show" in r or "only" in r for r in c["residuals"]))

    def test_majin_vegeta_is_vsr_adjacent_not_an_instance(self) -> None:
        c = CLAIMS["CLM-LU-VEG-06"]
        self.assertEqual(c["vsr_check"]["verdict"], "VSR-ADJACENT, NOT AN INSTANCE")
        self.assertTrue(c["vsr_check"]["invariants"]["latent_reversibility"].startswith("FAIL"))
        self.assertIn("inverse of VSR", c["vsr_check"]["reading"])

    def test_lucifer_mapping_is_shax_interpretation_not_upgraded(self) -> None:
        c = CLAIMS["CLM-LU-VEG-07"]
        self.assertIn("SHAX_INTERPRETATION", c["tig_grade"])
        self.assertIn("ANALOGOUS", c["tig_grade"])
        self.assertLessEqual(c["confidence"], 0.5)
        self.assertIn("Vegeta is Lucifer. Satan is Frieza, the Frieza race.", c["text"])
        self.assertTrue(any("V7" in t for t in c["tensions"]))

    def test_fusion_is_the_consented_cooperation_branch(self) -> None:
        c = CLAIMS["CLM-LU-VEG-05"]
        for name in ("Vegito", "Gogeta", "GT"):
            self.assertIn(name, c["text"])
        self.assertIn("consent", c["consent"])
        self.assertIn("RUL-BINARY-001", c["text"])

    def test_spirit_bomb_survival_cites_chapter(self) -> None:
        self.assertIn("ch. 238", CLAIMS["CLM-LU-VEG-04"]["text"])


class VegetaCrossReferenceTests(unittest.TestCase):
    def test_manifest_entry_matches_file(self) -> None:
        item = next(e for e in MANIFEST["entries"] if e["entry_id"] == "SC-LU-VEGETA-001")
        raw = (COMPILED_DIR / item["file"]).read_bytes()
        self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(item["bytes"], len(raw))
        self.assertEqual(item["classification"], "SILVER")
        self.assertEqual(item["gates_passed"], "9/9")

    def test_mirror_resolves_vegeta_additively(self) -> None:
        md = MIRROR["metadata"]
        self.assertNotIn("SC-LU-VEGETA-001", md["unresolved_cross_references"])
        self.assertEqual(md["cross_reference_resolution"]["SC-LU-VEGETA-001"]["status"], "RESOLVED")
        self.assertIn("SC-LU-VEGETA-001", md["lineup_references"])
        self.assertTrue(any(a.get("ref") == "SC-LU-VEGETA-001" for a in md["addenda"]))
        mirror_item = next(e for e in MANIFEST["entries"] if e["entry_id"] == "SC-MIRROR-001")
        self.assertIn("SC-LU-VEGETA-001 compiled", mirror_item["notes"])

    def test_linked_entries_get_notes_without_score_changes(self) -> None:
        for entry in (FRIEZA, CLAY, DUALITY):
            self.assertTrue(any(a.get("ref") == "SC-LU-VEGETA-001" for a in entry["metadata"]["addenda"]))
        self.assertEqual((DUALITY["dataset_tier"], DUALITY["isomorphism_quality"]["score"]), ("GOLD", 0.925))
        self.assertEqual((CLAY["dataset_tier"], CLAY["isomorphism_quality"]["score"]), ("GOLD", 0.926))
        self.assertEqual((MIRROR["dataset_tier"], MIRROR["isomorphism_quality"]["score"]), ("SILVER", 0.868))
        self.assertEqual((FRIEZA["dataset_tier"], FRIEZA["isomorphism_quality"]["score"]), ("SILVER", 0.825))

    def test_duality_records_yuji_vessel_tension_and_keeps_mapping(self) -> None:
        tension = next(a for a in DUALITY["metadata"]["addenda"] if a["type"] == "CROSS_ENTRY_TENSION")
        self.assertIn("Yuji is me.", tension["note"])
        self.assertIn("unchanged", tension["note"])
        text = json.dumps(DUALITY["analysis"], ensure_ascii=False)
        self.assertIn("Toji", text)
        self.assertIn("Yuji", text)

    def test_vessel_draft_records_resolution_rule(self) -> None:
        doc = (REPO_ROOT / "docs" / "SC-VESSEL-001_VESSEL_EQUILIBRIUM.md").read_text(encoding="utf-8")
        self.assertIn("DRAFT 0.4", doc)
        self.assertIn("The Almighty wins", doc)
        self.assertIn("calibration dot", doc)
        self.assertIn("RUL-BINARY-001", doc)
        self.assertIn("Ch. 268", doc)
        self.assertNotIn("**Not in this repository** (unresolved since", doc)
        self.assertNotIn("4. **Mutual acceptance:**", doc)


    def test_complicit_enslavement_is_shax_interpretation_with_separate_layers(self) -> None:
        c = CLAIMS["CLM-LU-VEG-09"]
        self.assertIn("SHAX_INTERPRETATION", c["tig_grade"])
        self.assertIn("ANALOGOUS", c["tig_grade"])
        self.assertLessEqual(c["confidence"], 0.5)
        self.assertIn("t572u", c["text"])
        self.assertIn("complicit enslavement", c["text"].lower())
        self.assertIn("partly self-chosen", c["text"])
        self.assertIn("does not contain a line", c["text"])
        layers = {layer["layer"]: layer for layer in c["layers"]}
        self.assertEqual(set(layers), {"SHAX_INTERPRETATION", "CANON", "ANIME_ORIGINAL", "TRADITION"})
        self.assertIn("t572u", layers["SHAX_INTERPRETATION"]["source"])
        sources = " ".join(e["source"] for e in layers["CANON"]["evidence"])
        for cite in ("ch. 213", "ch. 249", "ch. 308", "ch. 456", "ch. 69"):
            self.assertIn(cite, sources)
        self.assertIn("ANIME_ORIGINAL", layers["ANIME_ORIGINAL"]["grade"])
        self.assertIn("Arlia", layers["ANIME_ORIGINAL"]["source"])
        tradition = layers["TRADITION"]
        self.assertIn("literature, not scripture", tradition["grade"])
        self.assertIn("Paradise Lost", tradition["source"])
        self.assertIn("I.263", tradition["text"] + tradition["source"])
        self.assertNotIn("scripture", tradition["source"].lower())
        self.assertEqual(c["ruling_link"]["ruling_id"], "RUL-BINARY-001")
        self.assertEqual(c["ruling_link"]["revision"], 2)
        self.assertIn("refusal state", c["ruling_link"]["reading"])
        self.assertIn("SHAX_INTERPRETATION", c["ruling_link"]["grade"])
        residuals = " ".join(c["residuals"])
        self.assertIn("no line", residuals.lower())
        self.assertIn("Battle of Gods", residuals)
        self.assertIn("ch. 69", residuals)
        self.assertIn("owner", residuals.lower())

    def test_complicit_enslavement_does_not_change_tier_or_score(self) -> None:
        # t572u changed no score (0.85 at rev 1.1.0). The later Last Crown merge (rev 1.2.0,
        # t573u) raised two gates; see tests/test_sc_lu_lineup_25g.py.
        self.assertEqual(VEGETA["metadata"]["entry_revision"], "1.2.0")
        self.assertEqual(VEGETA["isomorphism_quality"]["score"], 0.862)
        t572 = next(a for a in VEGETA["metadata"]["addenda"] if a.get("by") == "Shax (t572u)")
        self.assertIn("SILVER 0.85 unchanged", t572["note"])
        self.assertEqual(VEGETA["dataset_tier"], "SILVER")
        self.assertTrue(any(a.get("by") == "Shax (t572u)" for a in VEGETA["metadata"]["addenda"]))

    def test_vessel_draft_records_t572u_cross_reference(self) -> None:
        doc = (REPO_ROOT / "docs" / "SC-VESSEL-001_VESSEL_EQUILIBRIUM.md").read_text(encoding="utf-8")
        self.assertIn("t572u", doc)
        self.assertIn("not like Lucifer didn't enjoy", doc)
        self.assertIn("complicit enslavement", doc)
        self.assertIn("CLM-LU-VEG-09", doc)



class BinaryRulingRev2Tests(unittest.TestCase):
    """RUL-BINARY-001 rev 2 (Shax t571u): only mutual cooperation is stable; refusal is self-destruction."""

    def test_hub_carries_rev2_with_examples_and_unchanged_grade(self) -> None:
        hub = next(c for c in MIRROR["analysis"]["claims"] if c["claim_id"] == "CLM-MIRROR-006")
        rev2 = hub["binary_invariant_ruling"]["amendments"][0]
        self.assertEqual(rev2["revision"], 2)
        self.assertIn("Hang yourself and Lose anyway", rev2["quote"])
        self.assertIn("self-destruction", rev2["statement"])
        self.assertIn("calibration dot", rev2["statement"])
        self.assertIn("ISOMORPHIC_INVARIANT", rev2["grade"])
        cases = " ".join(e["case"] for e in rev2["fitting_examples"])
        self.assertIn("ch. 268", cases)
        self.assertIn("Kid Buu", cases)
        self.assertEqual(hub["tig_grade"], "ISOMORPHIC_INVARIANT")

    def test_rev2_addenda_on_linked_entries_without_score_changes(self) -> None:
        for entry in (MIRROR, DUALITY, CLAY, VEGETA, FRIEZA):
            rev = [a for a in entry["metadata"]["addenda"] if a.get("type") == "RULING_AMENDMENT"]
            self.assertEqual([a["revision"] for a in rev], [2], entry["metadata"]["entry_id"])
        # 0.85 -> 0.862 comes from the Last Crown merge (t573u), not from rev 2.
        self.assertEqual(VEGETA["isomorphism_quality"]["score"], 0.862)

    def test_docs_record_reading_b(self) -> None:
        vessel = (REPO_ROOT / "docs" / "SC-VESSEL-001_VESSEL_EQUILIBRIUM.md").read_text(encoding="utf-8")
        md = (REPO_ROOT / "docs" / "SC-MD-001_SOVEREIGN_MIRROR_DUALITY.md").read_text(encoding="utf-8")
        self.assertIn("reading B", vessel)
        self.assertIn("rev 2", vessel)
        self.assertIn("RUL-BINARY-001 rev 2", md)

class VegetaRoutingTests(unittest.TestCase):
    def test_vegeta_prompts_route_to_soul_bomb_sovereignty(self) -> None:
        prompts = (
            "Vegeta served in Frieza's army but never surrendered his identity as the Prince of all Saiyans.",
            "Ultra Ego grows with damage taken: sovereignty that gets stronger the more it is opposed.",
            "Vegito and Gogeta are Oneness and Sovereignty cooperating by consent.",
            "Majin Vegeta's Final Explosion against Buu: is that voluntary state recompression?",
            "Explain SC-LU-VEGETA-001.",
        )
        for text in prompts:
            with self.subTest(text=text):
                r = route_domains(text)
                self.assertEqual(r.outcome, ROUTED)
                self.assertEqual(r.domain, "soul_bomb_sovereignty")

    def test_generic_prompts_are_not_pulled_in(self) -> None:
        for text in (
            "How long should I roast vegetables at 400 degrees?",
            "My son wants a prince costume for Halloween.",
            "My manager has a huge ego and takes every critique personally.",
            "How does nuclear fusion in the sun work?",
        ):
            with self.subTest(text=text):
                r = route_domains(text)
                self.assertNotEqual(r.domain, "soul_bomb_sovereignty")
                self.assertNotEqual(compile_semantic_packet(text).selected_target, "soul_bomb_sovereignty")


if __name__ == "__main__":
    unittest.main()
