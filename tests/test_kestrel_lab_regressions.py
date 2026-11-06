"""Regression tests from the Kestrel Lab three-cycle branch.

These tests are adapted to V3.0.0 and cover wrapper consistency, sensitive SFT
prompt handling, release provenance, and the explicitly documented remaining gaps.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import semantic_compiler
from semantic_compiler import compile_semantic_packet
from semantic_compiler.core.dataset import build_dataset_row
from semantic_compiler.core.pipeline import compile_semantic_packet as core_compile

REPO = Path(__file__).resolve().parent.parent
MAPPED_INPUT = "The nervous system routes signals like a network routes packets."
SECRET = "Private customer token ABC-123 must remain internal."
SENSITIVE_CONTEXT = {"privacy_sensitivity": "SENSITIVE", "external_training_use": "forbidden"}
MAPPED_INPUTS = (
    MAPPED_INPUT,
    "A firewall is like a cell membrane that controls what enters.",
    "The company has an immune system that detects threats and responds.",
    "The nervous system routes signals like a telecommunications network.",
)
EARLY_EXIT_INPUT = "Hello."


def _user_messages(payload: dict) -> list[str]:
    return [m["content"] for m in payload.get("messages", []) if m.get("role") == "user"]


class DecisionDerivativeConsistencyTests(unittest.TestCase):
    def test_decision_dependent_outputs_are_not_stale(self):
        packet = compile_semantic_packet(MAPPED_INPUT)
        decision = packet.decision.name
        self.assertEqual(packet.routing_packet.get("decision"), decision)
        self.assertIn(f"Decision: {decision}.", packet.executive_translation)
        self.assertNotIn("PENDING", packet.executive_translation)

    def test_every_mapped_input_is_consistent(self):
        for text in MAPPED_INPUTS:
            with self.subTest(text=text):
                packet = compile_semantic_packet(text)
                decision = packet.decision.name
                self.assertEqual(packet.routing_packet.get("decision"), decision)
                self.assertEqual(packet.route_to, packet.routing_packet.get("route_to", []))
                for field in ("literal_translation", "public_translation", "executive_translation"):
                    self.assertNotIn("PENDING", getattr(packet, field) or "", field)
                self.assertIn(f"Decision: {decision}.", packet.executive_translation)

    def test_dataset_row_embeds_the_current_translation_and_a_filled_sft_payload(self):
        packet = compile_semantic_packet(MAPPED_INPUT)
        row = packet.dataset_row
        self.assertEqual(row["outputs"]["executive_translation"], packet.executive_translation)
        self.assertEqual(row["status"], "COMPILED")
        self.assertIsNotNone(row["training_payloads"]["sft"])

    def test_wrapper_does_not_change_decision_scores_or_tier(self):
        for text in (*MAPPED_INPUTS, EARLY_EXIT_INPUT):
            with self.subTest(text=text):
                raw, wrapped = core_compile(text), compile_semantic_packet(text)
                self.assertEqual(raw.decision, wrapped.decision)
                self.assertEqual(raw.scores, wrapped.scores)
                self.assertEqual(raw.dataset_tier, wrapped.dataset_tier)
                self.assertEqual(raw.dataset_row["quality"]["training_ready"],
                                 wrapped.dataset_row["quality"]["training_ready"])

    def test_early_exit_packets_get_no_invented_derivatives(self):
        raw, wrapped = core_compile(EARLY_EXIT_INPUT), compile_semantic_packet(EARLY_EXIT_INPUT)
        self.assertFalse(raw.routing_packet, "premise: this input exits before Stage 4")
        self.assertEqual(wrapped.routing_packet, raw.routing_packet)
        self.assertEqual(wrapped.executive_translation, raw.executive_translation)

    def test_wrapper_row_matches_what_the_corpus_scripts_build(self):
        packet = compile_semantic_packet(MAPPED_INPUT)
        again = build_dataset_row(packet)
        stable = lambda row: {k: v for k, v in row.items() if k not in {"sample_id", "provenance", "audit"}}
        self.assertEqual(json.dumps(stable(packet.dataset_row), sort_keys=True, default=str),
                         json.dumps(stable(again), sort_keys=True, default=str))

    def test_package_entry_point_is_the_wrapper(self):
        from semantic_compiler import compat
        self.assertIs(semantic_compiler.compile_semantic_packet, compat.compile_semantic_packet)

    @unittest.expectedFailure
    def test_known_gap_core_pipeline_still_builds_derivatives_before_the_decision(self):
        packet = core_compile(MAPPED_INPUT)
        self.assertEqual(packet.routing_packet.get("decision"), packet.decision.name)


class SensitivePromptLeakTests(unittest.TestCase):
    def test_sensitive_qwen_export_does_not_echo_raw_input(self):
        packet = compile_semantic_packet(SECRET, context=SENSITIVE_CONTEXT)
        user_messages = _user_messages(packet.qwen_sft_output)
        self.assertTrue(user_messages)
        self.assertTrue(all(SECRET not in message for message in user_messages))
        self.assertTrue(any("sha256=" in message for message in user_messages))
        self.assertFalse(packet.qwen_sft_output["metadata"]["qwen_sft_ready"])

    def test_marker_is_the_input_hash(self):
        packet = compile_semantic_packet(SECRET, context=SENSITIVE_CONTEXT)
        (message,) = _user_messages(packet.qwen_sft_output)
        self.assertEqual(re.search(r"sha256=([0-9a-f]{64})", message).group(1), packet.compute_input_hash())

    def test_the_copy_embedded_in_the_dataset_row_is_redacted_too(self):
        packet = compile_semantic_packet(SECRET, context=SENSITIVE_CONTEXT)
        sft = packet.dataset_row["training_payloads"]["sft"]
        self.assertTrue(all(SECRET not in message for message in _user_messages(sft)))

    def test_unredacted_for_ordinary_input(self):
        packet = compile_semantic_packet(MAPPED_INPUT)
        (message,) = _user_messages(packet.qwen_sft_output)
        self.assertIn(MAPPED_INPUT, message)

    def test_redaction_also_covers_early_exit_packets(self):
        packet = compile_semantic_packet(EARLY_EXIT_INPUT, context=SENSITIVE_CONTEXT)
        self.assertTrue(all(EARLY_EXIT_INPUT not in m for m in _user_messages(packet.qwen_sft_output)))

    @unittest.expectedFailure
    def test_known_gap_core_builder_still_echoes_sensitive_text(self):
        packet = core_compile(SECRET, context=SENSITIVE_CONTEXT)
        self.assertTrue(all(SECRET not in m for m in _user_messages(packet.qwen_sft_output)))

    @unittest.expectedFailure
    def test_known_gap_dataset_row_input_block_still_carries_the_raw_text(self):
        packet = compile_semantic_packet(SECRET, context=SENSITIVE_CONTEXT)
        self.assertNotIn(SECRET, json.dumps(packet.dataset_row, default=str))


class ReleaseVersionProvenanceTests(unittest.TestCase):
    @staticmethod
    def _latest_manifest_version() -> str:
        best = ((0, 0, 0), "")
        for path in (REPO / "calibration_output").glob("RELEASE_MANIFEST_V*.json"):
            version = json.loads(path.read_text()).get("semantic_compiler_version", "")
            if re.fullmatch(r"\d+\.\d+\.\d+", version):
                best = max(best, (tuple(map(int, version.split("."))), version))
        return best[1]

    def test_package_version_matches_latest_release_manifest(self):
        self.assertEqual(semantic_compiler.__version__, self._latest_manifest_version())

    def test_package_version_matches_pyproject(self):
        text = (REPO / "pyproject.toml").read_text()
        declared = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M).group(1)
        self.assertEqual(semantic_compiler.__version__, declared)

    @unittest.expectedFailure
    def test_known_gap_packet_metadata_version_lags_the_release(self):
        packet = compile_semantic_packet(MAPPED_INPUT)
        self.assertEqual(packet.version, semantic_compiler.__version__)


if __name__ == "__main__":
    unittest.main()
