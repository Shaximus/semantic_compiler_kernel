"""Robustness of compile_semantic_packet against malformed mobile input."""

from __future__ import annotations

import json
import unittest

from semantic_compiler import SemanticPacket, compile_semantic_packet


class CompileInputRobustnessTests(unittest.TestCase):
    def test_lone_surrogate_does_not_crash(self) -> None:
        # A half emoji (high surrogate without its pair), as a JS/JNI text
        # bridge can produce.
        pkt = compile_semantic_packet("I love this \ud83d phone")
        self.assertIsInstance(pkt, SemanticPacket)
        self.assertNotIn("\ud83d", pkt.raw_input)
        self.assertIn("\ufffd", pkt.raw_input)
        self.assertTrue(pkt.source_context.source_hash)
        # The dataset row must be exportable as UTF-8 JSON.
        json.dumps(pkt.dataset_row, ensure_ascii=False, default=str).encode("utf-8")

    def test_valid_emoji_is_preserved(self) -> None:
        pkt = compile_semantic_packet("I love this \U0001F600 phone")
        self.assertIn("\U0001F600", pkt.raw_input)

    def test_non_str_input_raises_type_error(self) -> None:
        for bad in (None, 42, b"bytes"):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    compile_semantic_packet(bad)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
