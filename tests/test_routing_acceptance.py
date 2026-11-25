"""Acceptance tests for router-fed compile decisions (ROUTING_SPEC 2026-11-25).

COMPILED          recognized domain, adequate structure
NEEDS_REVISION    recognized domain, insufficient input (structural_fit < 0.55)
AMBIGUOUS         close top-2 routing; candidates listed, host asks the user
PASS_THROUGH      no credible domain; original prompt forwarded byte-for-byte
REJECT            empty / whitespace (invalid mode raises ValueError)
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from semantic_compiler import compile_semantic_packet
from semantic_compiler.core.pipeline import (
    AMBIGUOUS_ROUTE,
    PASS_THROUGH_ROUTE,
    ROUTED_DOMAIN_WARNING_PREFIX,
)
from semantic_compiler.core.scoring import STRUCTURAL_FIT_MIN
from semantic_compiler.core.types import Decision

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "routing_eval"
README_EXAMPLE = "The GPU is the weapon; support gems consume VRAM."
FRIEZA = (
    "Frieza survives the Spirit Bomb while Kid Buu is erased; collective input interacts "
    "with the target's internal structure rather than its morality, so the Spirit Bomb is "
    "a structure test, not a moral test."
)


def _acceptance() -> dict[str, dict]:
    rows = (FIXTURES / "acceptance.jsonl").read_text(encoding="utf-8").splitlines()
    return {r["id"]: r for r in (json.loads(x) for x in rows if x.strip())}


class RejectAndErrorTests(unittest.TestCase):
    def test_empty_and_whitespace_are_rejected(self) -> None:
        for text in ("", "   \n\t "):
            with self.subTest(text=repr(text)):
                self.assertEqual(compile_semantic_packet(text).decision, Decision.REJECT)

    def test_invalid_mode_is_an_explicit_error(self) -> None:
        with self.assertRaises(ValueError):
            compile_semantic_packet("A crane lifts beams.", mode="NOT_A_MODE")


class PassThroughTests(unittest.TestCase):
    def test_out_of_domain_prompts_pass_through_never_needs_revision(self) -> None:
        lines = (FIXTURES / "out_of_domain.txt").read_text(encoding="utf-8").splitlines()
        prompts = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
        self.assertGreaterEqual(len(prompts), 30)
        for text in prompts:
            with self.subTest(text=text):
                packet = compile_semantic_packet(text)
                self.assertEqual(packet.decision, Decision.PASS_THROUGH)
                self.assertEqual(packet.route_to, [PASS_THROUGH_ROUTE])
                self.assertEqual(packet.forward_text, text)

    def test_phone_and_conversation_pass_through(self) -> None:
        for text in (
            "Is my phone battery dying faster because of the new update?",
            "Summarize my last 3 emails and draft a reply to the one from my landlord.",
            "What should I cook for dinner tonight?",
        ):
            with self.subTest(text=text):
                self.assertEqual(compile_semantic_packet(text).decision, Decision.PASS_THROUGH)

    def test_pass_through_preserves_input_byte_for_byte(self) -> None:
        text = "  Is my phone battery dying?\r\n\U0001F50B \ud83d  tabs\tand NUL\x00 "
        packet = compile_semantic_packet(text)
        self.assertEqual(packet.decision, Decision.PASS_THROUGH)
        self.assertIs(type(packet.forward_text), str)
        self.assertEqual(packet.forward_text, text)

    def test_lone_weak_table_keyword_no_longer_forces_a_target(self) -> None:
        # "Server" alone used to give computation? -> organizational -> NEEDS_REVISION.
        packet = compile_semantic_packet("The server responded.")
        self.assertEqual(packet.decision, Decision.PASS_THROUGH)


class RoutedCompileTests(unittest.TestCase):
    def test_valid_invariant_compiles_in_routed_domain(self) -> None:
        packet = compile_semantic_packet(
            "A building with foundation, load-bearing frame, electrical wiring, plumbing, "
            "HVAC, and a weather-sealed envelope."
        )
        self.assertEqual(packet.decision, Decision.COMPILED)
        self.assertEqual(packet.selected_target, "construction")
        self.assertGreaterEqual(packet.scores["structural_fit"], STRUCTURAL_FIT_MIN)
        self.assertTrue(
            any(w.startswith(ROUTED_DOMAIN_WARNING_PREFIX) for w in packet.compiler_warnings)
        )
        self.assertEqual(packet.routing_candidates[0]["domain"], "construction")

    def test_recognized_domain_with_missing_structure_needs_revision(self) -> None:
        packet = compile_semantic_packet("The Android bootloader verifies the kernel signature.")
        self.assertEqual(packet.decision, Decision.NEEDS_REVISION)
        self.assertEqual(packet.selected_target, "mobile_security")
        self.assertLess(packet.scores["structural_fit"], STRUCTURAL_FIT_MIN)

    def test_frieza_invariant_compiles_in_soul_bomb_sovereignty(self) -> None:
        packet = compile_semantic_packet(FRIEZA)
        self.assertEqual(packet.decision, Decision.COMPILED)
        self.assertEqual(packet.selected_target, "soul_bomb_sovereignty")

    def test_frieza_paraphrase_targets_soul_bomb_sovereignty(self) -> None:
        packet = compile_semantic_packet(_acceptance()["frieza_para_1"]["text"])
        self.assertEqual(packet.selected_target, "soul_bomb_sovereignty")

    def test_readme_example_targets_buildcraft_domain(self) -> None:
        # Fit stays 0.45 (< 0.55); the fit floor is unchanged by routing.
        packet = compile_semantic_packet(README_EXAMPLE)
        self.assertEqual(packet.selected_target, "ci_build_invariants")
        self.assertEqual(packet.decision, Decision.NEEDS_REVISION)
        self.assertAlmostEqual(packet.scores["structural_fit"], 0.45, places=2)

    def test_cross_frame_analogy_keeps_table_fast_path(self) -> None:
        packet = compile_semantic_packet(
            "A backup system preserves data like DNA preserves genetic information."
        )
        self.assertNotEqual(packet.decision, Decision.PASS_THROUGH)
        self.assertTrue(packet.target_systems)

    def test_explicit_mode_keeps_weak_table_target(self) -> None:
        packet = compile_semantic_packet(
            "The computer has no CPU and no storage subsystem.",
            mode="STRUCTURAL_RECONSTRUCTION",
        )
        self.assertNotEqual(packet.decision, Decision.PASS_THROUGH)
        self.assertEqual(
            compile_semantic_packet("The computer has no CPU and no storage subsystem.").decision,
            Decision.PASS_THROUGH,
        )


class AmbiguityTests(unittest.TestCase):
    def test_close_cross_domain_input_is_explicitly_ambiguous(self) -> None:
        cases = _acceptance()
        for case_id in ("ambiguous_attestation", "ambiguous_tethering"):
            with self.subTest(case=case_id):
                case = cases[case_id]
                packet = compile_semantic_packet(case["text"])
                self.assertEqual(packet.decision, Decision.AMBIGUOUS)
                self.assertEqual(packet.status, "ambiguous")
                self.assertEqual(packet.route_to, [AMBIGUOUS_ROUTE])
                self.assertIsNone(packet.forward_text)
                top2 = {c["domain"] for c in packet.routing_candidates[:2]}
                self.assertEqual(top2, set(case["any_of"]))
                self.assertTrue(packet.next_questions)
                self.assertNotEqual(packet.decision, Decision.NEEDS_REVISION)


if __name__ == "__main__":
    unittest.main()
