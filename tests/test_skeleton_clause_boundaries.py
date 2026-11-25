"""Noun phrases in the structural skeleton must not span clause punctuation."""

from __future__ import annotations

import unittest

from semantic_compiler import compile_semantic_packet

README_EXAMPLE = "The GPU is the weapon; support gems consume VRAM."


def _phrases(pkt) -> list[str]:
    sk = pkt.structural_skeleton
    return [p.lower() for p in sk.get("actors", []) + sk.get("objects", [])]


def _spans(phrase: str, left: set[str], right: set[str]) -> bool:
    words = set(phrase.split())
    return bool(words & left) and bool(words & right)


class SkeletonClauseBoundaryTests(unittest.TestCase):
    def assertNoPhraseSpans(self, text: str, sep: str) -> list[str]:
        left_txt, right_txt = text.split(sep, 1)
        left = {w.strip(".,").lower() for w in left_txt.split()}
        right = {w.strip(".,").lower() for w in right_txt.split()}
        shared = left & right
        left -= shared
        right -= shared
        pkt = compile_semantic_packet(text)
        phrases = _phrases(pkt)
        for phrase in phrases:
            self.assertFalse(
                _spans(phrase, left, right),
                f"{phrase!r} spans {sep!r} in {text!r}",
            )
        return phrases

    def test_readme_example_semicolon(self) -> None:
        phrases = self.assertNoPhraseSpans(README_EXAMPLE, ";")
        self.assertIn("gpu", phrases)

    def test_metaphor_semicolon(self) -> None:
        # Previously produced the actor "organism cash flow".
        phrases = self.assertNoPhraseSpans(
            "The company is a living organism; cash flow is blood.", ";"
        )
        self.assertNotIn("organism cash flow", phrases)
        self.assertIn("cash flow", phrases)
        self.assertIn("company", phrases)

    def test_colon(self) -> None:
        # Previously produced the actor "rule memory".
        phrases = self.assertNoPhraseSpans("Rule: memory loads the cache", ":")
        self.assertIn("memory", phrases)

    def test_sentence_boundary(self) -> None:
        # Previously produced the actor "brain a network".
        phrases = self.assertNoPhraseSpans(
            "Explain the brain. A network routes packets.", "."
        )
        self.assertIn("network", phrases)

    def test_readme_example_after_prior_sentence(self) -> None:
        # Kernel Mobile prompt 06 produced the actor "paperwork the gpu".
        text = (
            "A clinic redesigns intake so diagnosis happens before paperwork. "
            + README_EXAMPLE
        )
        phrases = _phrases(compile_semantic_packet(text))
        self.assertNotIn("paperwork the gpu", phrases)
        self.assertIn("gpu", phrases)


if __name__ == "__main__":
    unittest.main()
