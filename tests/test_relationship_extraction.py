"""
Reflexion Semantic Compiler v2.1.3 — Relationship Extraction Tests

Coverage for relative-clause subjects, coordinated verbs, and pronoun
antecedent resolution in the lightweight SVO/analogy relationship extractor.
"""

import unittest

from semantic_compiler.core.pipeline import compile_semantic_packet


class RelationshipExtractionTests(unittest.TestCase):
    """Ensure explicit relationships are extracted from common constructions."""

    def _find_relationships(self, text: str) -> list[dict]:
        packet = compile_semantic_packet(text)
        return packet.semantic_ir.relationships

    def _has_rel(self, relationships: list[dict], subj: str, pred: str, obj: str) -> bool:
        subj_lower = subj.lower()
        obj_lower = obj.lower()
        pred_lower = pred.lower()
        for rel in relationships:
            if (
                rel.get("source_entity_id", "").lower() == subj_lower
                and rel.get("target_entity_id", "").lower() == obj_lower
                and rel.get("predicate", "").lower() == pred_lower
            ):
                return True
        return False

    def test_relative_clause_subject(self) -> None:
        """A noun phrase modified by 'that VERB OBJ' becomes the subject."""
        rels = self._find_relationships(
            "The company has an immune system that detects threats."
        )
        self.assertTrue(
            self._has_rel(rels, "immune system", "detects", "threats"),
            f"Expected immune system->detects->threats in {rels}",
        )

    def test_relative_clause_with_which(self) -> None:
        """'which' introduces a clause whose subject is the antecedent."""
        rels = self._find_relationships(
            "A firewall is a membrane which filters packets."
        )
        self.assertTrue(
            self._has_rel(rels, "membrane", "filters", "packets"),
            f"Expected membrane->filters->packets in {rels}",
        )

    def test_coordinated_verbs(self) -> None:
        """'X detects and remembers Y' yields two relationships."""
        rels = self._find_relationships(
            "The company has an immune system that detects threats and remembers them."
        )
        self.assertTrue(self._has_rel(rels, "immune system", "detects", "threats"))
        self.assertTrue(self._has_rel(rels, "immune system", "remembers", "threats"))

    def test_pronoun_antecedent_resolution(self) -> None:
        """A pronoun object resolves to the most recent concrete object."""
        rels = self._find_relationships(
            "The immune system detects threats and remembers them."
        )
        # "them" should be resolved to "threats".
        self.assertFalse(
            self._has_rel(rels, "immune system", "remembers", "them"),
            "Pronoun object 'them' should not remain unresolved.",
        )
        self.assertTrue(
            self._has_rel(rels, "immune system", "remembers", "threats"),
            f"Expected immune system->remembers->threats in {rels}",
        )

    def test_analogy_edge_extracted(self) -> None:
        """Analogy markers produce ANALOGOUS_TO edges."""
        rels = self._find_relationships("A firewall is like a cell membrane.")
        analogy_rels = [r for r in rels if r.get("relationship_type") == "ANALOGOUS_TO"]
        self.assertTrue(
            any(r.get("source_entity_id", "").lower() == "firewall" for r in analogy_rels)
        )
        self.assertTrue(
            any(r.get("target_entity_id", "").lower() == "cell membrane" for r in analogy_rels)
        )


if __name__ == "__main__":
    unittest.main()
