"""Discriminative router: filler suppression, abstention, ambiguity, anchors.

Fixtures live in tests/fixtures/routing_eval/. Labeled in-domain data is the
225-sample decompression calibration corpus (5 inputs x 45 domains).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from semantic_compiler.expansion.elevator import summon
from semantic_compiler.expansion.router import (
    ABSTAIN,
    AMBIGUOUS,
    FILLER_WORDS,
    PROTECTED_RELATIONAL_WORDS,
    ROUTED,
    _query_units,
    route_domains,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "routing_eval"
README_EXAMPLE = "The GPU is the weapon; support gems consume VRAM."


def _ood_prompts() -> list[str]:
    lines = (FIXTURES / "out_of_domain.txt").read_text(encoding="utf-8").splitlines()
    return [ln for ln in lines if ln.strip() and not ln.startswith("#")]


def _acceptance() -> dict[str, dict]:
    rows = (FIXTURES / "acceptance.jsonl").read_text(encoding="utf-8").splitlines()
    return {r["id"]: r for r in (json.loads(x) for x in rows if x.strip())}


class FillerSuppressionTests(unittest.TestCase):
    def test_protected_relational_words_are_never_filler(self) -> None:
        for word in ("not", "without", "before", "after", "only", "never", "no", "unless", "except"):
            with self.subTest(word=word):
                self.assertIn(word, PROTECTED_RELATIONAL_WORDS)
                self.assertNotIn(word, FILLER_WORDS)

    def test_protected_words_stay_in_phrase_stream(self) -> None:
        _tokens, phrases = _query_units("diagnosis happens before paperwork, not after")
        self.assertIn("happens before paperwork", phrases)
        self.assertTrue(any("not after" in p for p in phrases))

    def test_filler_is_not_evidence(self) -> None:
        tokens, _ = _query_units("Is my phone battery dying faster because of the new update?")
        for filler in ("my", "faster", "because", "new"):
            self.assertNotIn(filler, tokens)


class DogfoodRegressionTests(unittest.TestCase):
    """Routes seen while dogfooding main @ 9ec2f81 (summon picked a domain on filler)."""

    def assertAbstains(self, text: str) -> None:
        result = route_domains(text)
        self.assertEqual(result.outcome, ABSTAIN, result.to_dict())
        bay = summon(text)
        self.assertEqual(bay.primary_domain, "universal_generic")
        self.assertEqual(bay.matched_domains, ())
        self.assertEqual(bay.routing.outcome, ABSTAIN)

    def test_phone_battery_no_longer_poe_chaos_inoculation(self) -> None:
        self.assertAbstains("Is my phone battery dying faster because of the new update?")

    def test_landlord_email_no_longer_speculative_decoding(self) -> None:
        self.assertAbstains(
            "Summarize my last 3 emails and draft a reply to the one from my landlord."
        )

    def test_readme_example_routes_on_buildcraft_anchor_not_filler(self) -> None:
        # ci_build_invariants is the domain derived from the Buildcraft (PoE -> compute)
        # ontology, so it is the intended home of the README example. Before the fix it
        # won on the loose tokens "support" + "vram"; now it must carry the
        # buildcraft phrase "support gems" as evidence.
        result = route_domains(README_EXAMPLE)
        self.assertEqual(result.outcome, ROUTED)
        self.assertEqual(result.domain, "ci_build_invariants")
        self.assertIn("support gems", result.candidates[0].phrase_matches)


class AbstainAndRouteTests(unittest.TestCase):
    def test_out_of_domain_prompts_abstain(self) -> None:
        for text in _ood_prompts():
            with self.subTest(text=text):
                self.assertEqual(route_domains(text).outcome, ABSTAIN)

    def test_labeled_calibration_precision_and_recall(self) -> None:
        path = ROOT / "calibration_output" / "decompression_calibration_v2_2.jsonl"
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        correct = wrong = 0
        for row in rows:
            result = route_domains(row["input_text"])
            if result.domain == row["domain"]:
                correct += 1
            elif result.outcome == ROUTED:
                wrong += 1
        precision = correct / (correct + wrong)
        recall = correct / len(rows)
        # Measured at introduction: precision 0.977, recall 0.942 (225 samples).
        self.assertGreaterEqual(precision, 0.95)
        self.assertGreaterEqual(recall, 0.90)

    def test_explicit_compiled_entry_ids_route_home(self) -> None:
        for entry_id, domain in (
            ("SC-OMNI-001", "soul_bomb_sovereignty"),
            ("SC-TIG-001", "reflexion"),
            ("SC-IT-OCTO-RNA-EDIT-001", "biology"),
        ):
            with self.subTest(entry_id=entry_id):
                result = route_domains(entry_id)
                self.assertEqual((result.outcome, result.domain), (ROUTED, domain))

    def test_candidates_are_ranked_with_confidence_and_margin(self) -> None:
        result = route_domains(
            "PagedAttention and RadixAttention share KV cache block tables during prefill."
        )
        self.assertEqual(result.domain, "kv_cache_inference")
        scores = [c.score for c in result.candidates]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(0.0 <= result.confidence <= 1.0)
        self.assertGreater(result.margin, 0.15)


class AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = _acceptance()

    def test_frieza_spirit_bomb_invariant_routes_to_soul_bomb_sovereignty(self) -> None:
        for case_id in ("frieza_core", "frieza_para_1"):
            with self.subTest(case=case_id):
                result = route_domains(self.cases[case_id]["text"])
                self.assertEqual(result.domain, "soul_bomb_sovereignty", result.to_dict())

    def test_frieza_paraphrase_load_bearing_structure(self) -> None:
        # Was a known limit ("load-bearing structure" pulled to construction).
        # Since SC-LU-FRIEZA-001 (2026-11-25) "frieza" is a soul_bomb_sovereignty
        # context anchor, so the named paraphrase routes home. The unnamed
        # paraphrase below is still a lexical-router limit.
        result = route_domains(self.cases["frieza_para_2"]["text"])
        self.assertEqual(result.domain, "soul_bomb_sovereignty")

    @unittest.expectedFailure
    def test_frieza_paraphrase_without_names(self) -> None:
        # Known limit: no Dragon Ball names; "energy" + "chaos" pull to poe_chaos_inoculation.
        result = route_domains(self.cases["frieza_para_3"]["text"])
        self.assertEqual(result.domain, "soul_bomb_sovereignty")

    def test_close_cross_domain_inputs_are_ambiguous_with_candidates(self) -> None:
        for case_id in ("ambiguous_attestation", "ambiguous_tethering"):
            with self.subTest(case=case_id):
                case = self.cases[case_id]
                result = route_domains(case["text"])
                self.assertEqual(result.outcome, AMBIGUOUS, result.to_dict())
                self.assertIsNone(result.domain)
                top2 = {c.domain for c in result.candidates[:2]}
                self.assertEqual(top2, set(case["any_of"]))


if __name__ == "__main__":
    unittest.main()
