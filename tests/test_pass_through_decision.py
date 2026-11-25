"""PASS_THROUGH: no resolved target means 'forward the prompt to the host AI'."""

from __future__ import annotations

import json
import unittest

from semantic_compiler import Decision, SemanticPacket, compile_semantic_packet
from semantic_compiler.core.pipeline import (
    EMPTY_INPUT_ERROR_CLASS,
    PASS_THROUGH_REASON,
    PASS_THROUGH_ROUTE,
)
from semantic_compiler.core.scoring import STRUCTURAL_FIT_MIN

OUT_OF_DOMAIN = (
    "remind me to call mom at 6",
    "Summarize my last 3 emails and draft a reply to the one from my landlord.",
    "Purple sleeps horizontally under Tuesday.",
)


class PassThroughTests(unittest.TestCase):
    def test_no_target_prompts_pass_through(self) -> None:
        for text in OUT_OF_DOMAIN:
            with self.subTest(text=text):
                pkt = compile_semantic_packet(text)
                self.assertIsInstance(pkt, SemanticPacket)
                self.assertIs(pkt.decision, Decision.PASS_THROUGH)
                self.assertEqual(pkt.status, "pass_through")
                self.assertFalse(pkt.target_systems)
                self.assertIsNone(pkt.semantic_error_class)
                self.assertFalse(pkt.compiler_errors)
                self.assertIn(PASS_THROUGH_REASON, pkt.compiler_warnings)
                self.assertEqual(pkt.route_to, [PASS_THROUGH_ROUTE])
                # The original prompt is preserved for forwarding.
                self.assertEqual(pkt.raw_input, text)
                data = json.loads(json.dumps(pkt.to_dict()))
                self.assertEqual(data["decision"], "PASS_THROUGH")
                self.assertTrue(pkt.dataset_row)

    def test_forward_text_is_byte_for_byte_original(self) -> None:
        prompts = (
            "remind me to call mom at 6",
            "  remind me\r\nto call mom   at 6 \t\n",
            "caf\u00e9 \U0001F600 na\u0131ve \u200b zero-width",
            "half emoji \ud83d here",  # lone surrogate: raw_input is sanitized, forward_text is not
            "a\x00b",
        )
        for text in prompts:
            with self.subTest(text=text):
                pkt = compile_semantic_packet(text)
                self.assertIs(pkt.decision, Decision.PASS_THROUGH)
                self.assertEqual(pkt.forward_text, text)
                self.assertEqual(
                    pkt.forward_text.encode("utf-8", "surrogatepass"),
                    text.encode("utf-8", "surrogatepass"),
                )

    def test_forward_text_only_set_for_pass_through(self) -> None:
        for text in ("", "The GPU is the weapon; support gems consume VRAM."):
            with self.subTest(text=text):
                self.assertIsNone(compile_semantic_packet(text).forward_text)

    def test_existing_decision_values_unchanged(self) -> None:
        # PASS_THROUGH is appended; existing integer values must not move.
        self.assertEqual(Decision.NEEDS_REVISION.value, 5)
        self.assertEqual(Decision.REJECT.value, 9)
        self.assertEqual(Decision.PASS_THROUGH.value, 10)
        self.assertEqual(Decision.AMBIGUOUS.value, 11)

    def test_empty_input_stays_reject(self) -> None:
        pkt = compile_semantic_packet("   ")
        self.assertIs(pkt.decision, Decision.REJECT)
        self.assertEqual(pkt.semantic_error_class, EMPTY_INPUT_ERROR_CLASS)

    def test_low_fit_with_target_stays_needs_revision(self) -> None:
        pkt = compile_semantic_packet("The GPU is the weapon; support gems consume VRAM.")
        self.assertTrue(pkt.target_systems)
        self.assertLess(pkt.scores["structural_fit"], STRUCTURAL_FIT_MIN)
        self.assertIs(pkt.decision, Decision.NEEDS_REVISION)

    def test_semantic_error_without_target_still_rejects(self) -> None:
        pkt = compile_semantic_packet("The Sun orbits the Earth because it is loyal.")
        self.assertIs(pkt.decision, Decision.REJECT)


if __name__ == "__main__":
    unittest.main()
