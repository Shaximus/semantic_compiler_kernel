"""Tests for the canonical medical ontology (Semantic Compiler V2.2 expansion)."""
import unittest


class TestMedicalOntology(unittest.TestCase):
    def test_ontology_contains_core_concepts(self):
        try:
            from expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY, get_concept
        except ModuleNotFoundError:
            # unittest discovery binds `expansion` to tests/expansion; import via repo package
            from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY, get_concept
        for concept in ["homeostasis", "immune_system", "pathogen", "cancer", "autoimmune", "sepsis"]:
            self.assertIn(concept, MEDICAL_ONTOLOGY)
        concept = get_concept("homeostasis")
        self.assertEqual(concept.name, "homeostasis")
        self.assertTrue(concept.description)


if __name__ == "__main__":
    unittest.main()
