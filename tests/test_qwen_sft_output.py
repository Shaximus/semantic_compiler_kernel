"""
Acceptance tests for Qwen AgentWorld SFT output generation.

Citation: Reflexion SFT Sample Format v1.0
"""

import unittest

from semantic_compiler.core.pipeline import compile_semantic_packet, build_qwen_sft_output
from semantic_compiler.core.types import Decision, DatasetTier


SAMPLE_INPUT = (
    "The company has an immune system that detects threats and remembers them."
)


class QwenSftOutputTests(unittest.TestCase):
    """Verify Qwen SFT sample structure and default-deny policy."""

    def test_qwen_sft_output_structure(self):
        """A compiled packet must produce the Qwen chat-format structure."""
        packet = compile_semantic_packet(SAMPLE_INPUT)

        sft = packet.qwen_sft_output
        self.assertIn("messages", sft)
        self.assertIn("metadata", sft)

        messages = sft["messages"]
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[2]["role"], "assistant")

        # System prompt identifies Logos
        self.assertIn("Logos_", messages[0]["content"])

        # User content uses Compile: prefix
        self.assertTrue(messages[1]["content"].startswith("Compile:"))

        metadata = sft["metadata"]
        self.assertEqual(metadata["sample_id"], packet.packet_id)
        self.assertFalse(metadata["qwen_sft_ready"])  # default-deny
        self.assertEqual(metadata["review_status"], "draft")
        self.assertIn("readiness_reasons", metadata)

    def test_default_deny_blocks_external_training(self):
        """By default, no sample is promoted to qwen_sft_ready."""
        packet = compile_semantic_packet(SAMPLE_INPUT)
        self.assertFalse(packet.qwen_sft_output["metadata"]["qwen_sft_ready"])
        reasons = packet.qwen_sft_output["metadata"]["readiness_reasons"]
        self.assertTrue(
            any("external_training_use is forbidden" in r for r in reasons)
        )

    def test_explicit_approval_can_make_sample_ready(self):
        """With explicit approval and clean gates, qwen_sft_ready can become true."""
        context = {
            "privacy_sensitivity": "PUBLIC",
            "external_training_use": "approved",
            "dataset_tier": "GOLD",
        }
        packet = compile_semantic_packet(SAMPLE_INPUT, context=context)
        packet.decision = Decision.COMPILED
        packet.scores["hard_gates_passed"] = 1.0

        sft = build_qwen_sft_output(packet)
        self.assertTrue(sft["metadata"]["qwen_sft_ready"])
        self.assertEqual(sft["metadata"]["review_status"], "accepted")
        self.assertEqual(sft["metadata"]["privacy"], "public_safe")

    def test_sensitive_input_is_redacted(self):
        """Sensitive/Critical inputs keep Compile prefix in user message."""
        context = {"privacy_sensitivity": "CRITICAL"}
        packet = compile_semantic_packet(SAMPLE_INPUT, context=context)

        user_content = packet.qwen_sft_output["messages"][1]["content"]
        self.assertTrue(user_content.startswith("Compile (redacted):"))

    def test_assistant_content_contains_structured_packet(self):
        """Assistant message follows Diamond++ structured packet format."""
        packet = compile_semantic_packet(SAMPLE_INPUT)
        assistant = packet.qwen_sft_output["messages"][2]["content"]

        self.assertIn("**Mode:**", assistant)
        self.assertIn("**Decision:**", assistant)
        self.assertIn("**Source frames:**", assistant)


if __name__ == "__main__":
    unittest.main()
