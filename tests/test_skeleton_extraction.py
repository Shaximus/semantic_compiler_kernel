"""
Tests for dependency-free structural skeleton extraction.
"""

import unittest

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.extraction.skeleton import (
    _extract_actors,
    _extract_objects,
    _tokenize,
)


class SkeletonExtractionTests(unittest.TestCase):
    """Verify actors and objects are extracted from raw input."""

    def _packet(self, text: str) -> SemanticPacket:
        return SemanticPacket(raw_input=text)

    def test_tokenize_preserves_words(self):
        tokens = _tokenize("The AI reads the file.")
        self.assertEqual(tokens, ["The", "AI", "reads", "the", "file"])

    def test_extracts_subject_as_actor(self):
        packet = self._packet("The company has an immune system.")
        actors = _extract_actors(packet)
        self.assertIn("company", actors)

    def test_extracts_object_phrases(self):
        packet = self._packet("The company has an immune system.")
        objects = _extract_objects(packet)
        self.assertIn("immune system", objects)

    def test_no_determiners_in_phrases(self):
        packet = self._packet("The AI reads the file.")
        objects = _extract_objects(packet)
        for obj in objects:
            self.assertFalse(obj.startswith("the "))
            self.assertFalse(obj.startswith("an "))

    def test_proper_noun_actor(self):
        packet = self._packet("Kimberly routes the mail to Logos.")
        actors = _extract_actors(packet)
        self.assertIn("kimberly", actors)

    def test_plural_objects(self):
        packet = self._packet("The system detects threats and logs events.")
        objects = _extract_objects(packet)
        self.assertIn("threats", objects)
        self.assertIn("events", objects)

    def test_does_not_extract_adjective_as_object(self):
        packet = self._packet("The company has an immune system.")
        objects = _extract_objects(packet)
        self.assertNotIn("immune", objects)

    def test_role_noun_subsumed_by_compound(self):
        packet = self._packet("The company has an immune system.")
        actors = _extract_actors(packet)
        # "system" should not appear as a standalone actor when it is part
        # of the object phrase "immune system".
        self.assertNotIn("system", actors)


if __name__ == "__main__":
    unittest.main()
