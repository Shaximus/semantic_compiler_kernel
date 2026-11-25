"""Empty input rejection, mode validation, and enum-name serialization."""

from __future__ import annotations

import json
import unittest

from semantic_compiler import CompilerMode, Decision, compile_semantic_packet
from semantic_compiler.core.pipeline import EMPTY_INPUT_ERROR_CLASS

README_EXAMPLE = "The GPU is the weapon; support gems consume VRAM."


class EmptyInputTests(unittest.TestCase):
    def test_empty_and_whitespace_are_rejected_distinctly(self) -> None:
        for text in ("", "   ", "\n\t \r\n"):
            with self.subTest(text=text):
                pkt = compile_semantic_packet(text)
                self.assertIs(pkt.decision, Decision.REJECT)
                self.assertEqual(pkt.semantic_error_class, EMPTY_INPUT_ERROR_CLASS)
                self.assertEqual(pkt.status, "rejected")
                self.assertTrue(any("EMPTY_INPUT" in e for e in pkt.compiler_errors))
                # Still a finalized packet: dataset row and audit are built.
                self.assertTrue(pkt.dataset_row)
                self.assertEqual(pkt.raw_input, text)

    def test_non_empty_input_is_not_flagged_empty(self) -> None:
        pkt = compile_semantic_packet(README_EXAMPLE)
        self.assertNotEqual(pkt.semantic_error_class, EMPTY_INPUT_ERROR_CLASS)


class ModeValidationTests(unittest.TestCase):
    def test_unknown_mode_raises_value_error_listing_valid_modes(self) -> None:
        with self.assertRaises(ValueError) as cm:
            compile_semantic_packet(README_EXAMPLE, mode="FOO")
        msg = str(cm.exception)
        self.assertIn("'FOO'", msg)
        for mode in CompilerMode:
            self.assertIn(mode.name, msg)

    def test_non_string_mode_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            compile_semantic_packet(README_EXAMPLE, mode=3)  # type: ignore[arg-type]

    def test_unknown_mode_raises_even_for_empty_input(self) -> None:
        with self.assertRaises(ValueError):
            compile_semantic_packet("", mode="FOO")

    def test_default_mode_auto_detects(self) -> None:
        pkt = compile_semantic_packet(README_EXAMPLE)
        self.assertIsNot(pkt.mode, CompilerMode.AUTO)

    def test_lowercase_auto_auto_detects_like_default(self) -> None:
        # Previously "auto" resolved to CompilerMode.AUTO and skipped detection.
        default = compile_semantic_packet(README_EXAMPLE)
        lower = compile_semantic_packet(README_EXAMPLE, mode="auto")
        self.assertIs(lower.mode, default.mode)

    def test_explicit_mode_by_name_enum_and_case(self) -> None:
        for mode in ("CONTRADICTION_SOLVER", "contradiction_solver",
                     CompilerMode.CONTRADICTION_SOLVER):
            with self.subTest(mode=mode):
                pkt = compile_semantic_packet(README_EXAMPLE, mode=mode)  # type: ignore[arg-type]
                self.assertIs(pkt.mode, CompilerMode.CONTRADICTION_SOLVER)


class EnumNameSerializationTests(unittest.TestCase):
    """to_dict() is the JSON surface: enums must appear by name, not int."""

    def test_to_dict_uses_enum_names_and_is_json_serializable(self) -> None:
        for text in (README_EXAMPLE, ""):
            with self.subTest(text=text):
                pkt = compile_semantic_packet(text)
                data = json.loads(json.dumps(pkt.to_dict()))
                self.assertEqual(data["decision"], pkt.decision.name)
                self.assertEqual(data["mode"], pkt.mode.name)
                self.assertIsInstance(data["decision"], str)
                json.dumps(pkt.dataset_row)


if __name__ == "__main__":
    unittest.main()
