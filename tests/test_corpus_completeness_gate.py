"""
Tests for the corpus-completeness gate.
"""

import unittest

from semantic_compiler.gates.corpus_completeness import (
    CorpusCompletenessGate,
    CorpusState,
)


class CorpusCompletenessTests(unittest.TestCase):
    """Verify bounded corpus-completeness states."""

    def test_present_in_current_context(self):
        gate = CorpusCompletenessGate(
            manifest={"current_context": {"Lagrangian": {}}}
        )
        result = gate.check("Lagrangian", ["Lagrangian", "action"])
        self.assertEqual(result["state"], CorpusState.PRESENT_IN_CURRENT_CONTEXT.value)
        self.assertTrue(result["passed"])

    def test_search_not_performed(self):
        gate = CorpusCompletenessGate(manifest={})
        result = gate.check("Lagrangian", ["Lagrangian"])
        self.assertEqual(result["state"], CorpusState.SEARCH_NOT_PERFORMED.value)
        self.assertIsNone(result["passed"])

    def test_found_in_linked_corpus(self):
        def search(terms):
            return [{"path": "docs/theory.md"}]

        gate = CorpusCompletenessGate(manifest={}, search_fn=search)
        result = gate.check("Lagrangian", ["Lagrangian", "action"])
        self.assertEqual(result["state"], CorpusState.FOUND_IN_LINKED_CORPUS.value)
        self.assertTrue(result["passed"])
        self.assertIn("docs/theory.md", result["hits"])

    def test_not_found_within_search_scope(self):
        def search(terms):
            return []

        gate = CorpusCompletenessGate(manifest={}, search_fn=search)
        result = gate.check("Lagrangian", ["Lagrangian"])
        self.assertEqual(result["state"], CorpusState.NOT_FOUND_WITHIN_SEARCH_SCOPE.value)
        self.assertIsNone(result["passed"])

    def test_absent_from_locked_corpus_requires_explicit_call(self):
        gate = CorpusCompletenessGate(manifest={})
        result = gate.confirm_absent_from_locked_corpus(
            claim_component="Lagrangian",
            query_terms=["Lagrangian", "action"],
            coverage_ratio=1.0,
            corpus_manifest_hash="sha256:abc",
            corpus_version="v1.0",
        )
        self.assertEqual(
            result["state"], CorpusState.ABSENT_FROM_VERSION_LOCKED_CORPUS.value
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["search_record"].coverage_ratio, 1.0)


if __name__ == "__main__":
    unittest.main()
