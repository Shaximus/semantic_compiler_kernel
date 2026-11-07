"""Regression coverage for department-presence detection (missing-organ input).

Each test pins a defect reproduced against the shipped V3.0.0 detector, which
substring-matched every word of the raw text against every table string and so
marked most departments PRESENT on function words and on the system's own name.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from semantic_compiler.translation.fractal import (
    FRAME_TO_SCALE,
    UNIVERSAL_ISOMORPHISM,
    _map_present_to_departments,
    identify_missing_departments,
    map_fractal_similarity,
    scale_for_frame,
)

BENCHMARK_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "evaluate_missing_organ.py"


def present(text: str, scale: str) -> set[str]:
    return _map_present_to_departments([], scale, raw_text=text)


class PresenceLeakRegressionTests(unittest.TestCase):
    def test_function_words_are_never_evidence(self) -> None:
        # 10 of 15 departments were PRESENT on this sentence before the fix.
        self.assertEqual(present("It is in the of to and from with at on by.", "cellular"), set())

    def test_system_name_is_not_evidence_of_an_organ(self) -> None:
        self.assertEqual(present("A cell has a nucleus.", "cellular"), {"PROCESSOR"})
        self.assertEqual(present("A society has a government and media.", "society"), {"PROCESSOR", "DISPLAY"})
        self.assertEqual(present("An LLM has transformer weights.", "llm"), {"PROCESSOR"})

    def test_negated_mentions_are_not_presence(self) -> None:
        self.assertEqual(present("The company has no security team.", "society"), set())
        self.assertEqual(present("The computer runs without a firewall.", "computer"), set())
        # Negation does not leak across a contrast.
        self.assertEqual(present("There is no firewall, but the CPU works.", "computer"), {"PROCESSOR"})

    def test_shared_table_phrase_is_evidence_for_every_owner(self) -> None:
        # "attention mechanism" is listed for both PROCESSOR and TELECOMMUNICATIONS.
        self.assertTrue({"PROCESSOR", "TELECOMMUNICATIONS"} <= present("It uses an attention mechanism.", "llm"))
        self.assertIn("SECURITY", present("The cell membrane guards the interior.", "cellular"))

    def test_plurals_and_agent_forms_are_recognised(self) -> None:
        self.assertIn("WASTE_REMOVAL", present("It has kidneys.", "human"))
        self.assertIn("STORAGE", present("It has hard drives.", "computer"))
        self.assertIn("DELETION", present("It has a process terminator.", "computer"))

    def test_words_matched_as_whole_tokens_only(self) -> None:
        # "ram" must not fire inside "program", "ssd" inside "classdd", etc.
        self.assertNotIn("INFORMATION_DENSITY", present("The program ran.", "computer"))
        self.assertIn("INFORMATION_DENSITY", present("It has RAM.", "computer"))

    def test_explicit_canonical_names_still_count_via_identify(self) -> None:
        findings = identify_missing_departments(
            {"present_functions": ["PROCESSOR"]}, scale="cellular", completeness_required=True, raw_text="Nothing here."
        )
        states = {f["department"]: f["state"] for f in findings}
        self.assertEqual(states["PROCESSOR"], "PRESENT")
        self.assertEqual(states["DISPLAY"], "ABSENT_CONFIRMED")


class AbsenceStateTests(unittest.TestCase):
    def test_incomplete_cell_confirms_absence_of_unmentioned_organs(self) -> None:
        findings = identify_missing_departments(
            {"present_functions": []}, scale="cellular", completeness_required=True, raw_text="A cell has a nucleus."
        )
        states = {f["department"]: f["state"] for f in findings}
        self.assertEqual(states["PROCESSOR"], "PRESENT")
        for dept in ("DISPLAY", "SECURITY", "ENERGY_INTAKE", "REPRODUCTION", "DELETION"):
            self.assertEqual(states[dept], "ABSENT_CONFIRMED", dept)

    def test_fragment_input_never_confirms_absence(self) -> None:
        findings = identify_missing_departments(
            {"present_functions": []}, scale="cellular", completeness_required=False, raw_text="A cell has a nucleus."
        )
        self.assertNotIn("ABSENT_CONFIRMED", {f["state"] for f in findings})


class ScaleResolutionTests(unittest.TestCase):
    def test_frame_names_the_detector_emits_resolve(self) -> None:
        for frame, scale in (
            ("computation", "computer"),
            ("organizational", "society"),
            ("reflexion", "llm"),
            ("biology", "human"),
            ("Cosmological?", "cosmos"),
        ):
            self.assertEqual(scale_for_frame(frame), scale, frame)

    def test_keyword_fallback_uses_whole_words(self) -> None:
        self.assertIsNone(scale_for_frame("chain"))  # "ai" inside "chain"
        self.assertIsNone(scale_for_frame(""))
        self.assertIsNone(scale_for_frame(None))

    def test_frame_table_values_are_known_scales(self) -> None:
        table_scales = {scale for mapping in UNIVERSAL_ISOMORPHISM.values() for scale in mapping}
        self.assertLessEqual(set(FRAME_TO_SCALE.values()), table_scales)

    def test_frame_table_has_not_drifted_from_the_pipeline_copy(self) -> None:
        # core.pipeline._infer_system_scale keeps its own copy of this table because
        # core/ is under the V3.0.0 freeze. Keep the two identical.
        from semantic_compiler.core.packet import SemanticPacket
        from semantic_compiler.core.pipeline import _infer_system_scale

        for frame, scale in FRAME_TO_SCALE.items():
            packet = SemanticPacket(raw_input="x", source_frames=[frame])
            self.assertEqual(_infer_system_scale(packet), scale, frame)

    def test_default_similarity_is_unchanged_and_opt_in_resolves(self) -> None:
        packet = {"source_frames": ["computation"], "target_systems": ["biology"]}
        self.assertEqual(map_fractal_similarity(packet), [])
        resolved = map_fractal_similarity(packet, resolve_frames=True)
        self.assertGreater(len(resolved), 0)


class BenchmarkRegressionTests(unittest.TestCase):
    """Pin the shipped labeled benchmark. The V3.0.0 detector scored recall 0.805."""

    def test_benchmark_floor(self) -> None:
        spec = importlib.util.spec_from_file_location("evaluate_missing_organ_under_test", BENCHMARK_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        results = [module.evaluate_example(example) for example in module.load_benchmark(module.BENCHMARK_PATH)]
        metrics = module.compute_metrics(results)
        self.assertGreaterEqual(metrics["absent_confirmed_precision"], 0.90)
        self.assertGreaterEqual(metrics["absent_confirmed_recall"], 0.95)
        self.assertLessEqual(metrics["fragment_false_positive_rate"], 0.10)


if __name__ == "__main__":
    unittest.main()
