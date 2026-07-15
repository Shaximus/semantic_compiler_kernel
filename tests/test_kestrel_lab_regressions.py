from __future__ import annotations

import unittest

import semantic_compiler
from semantic_compiler import compile_semantic_packet


class KestrelLabRegressionTests(unittest.TestCase):
    def test_decision_dependent_outputs_are_not_stale(self):
        packet = compile_semantic_packet(
            "The nervous system routes signals like a network routes packets."
        )
        decision = packet.decision.name
        self.assertEqual(packet.routing_packet.get("decision"), decision)
        self.assertIn(f"Decision: {decision}.", packet.executive_translation)
        self.assertNotIn("PENDING", packet.executive_translation)

    def test_sensitive_qwen_export_does_not_echo_raw_input(self):
        secret = "Private customer token ABC-123 must remain internal."
        packet = compile_semantic_packet(
            secret,
            context={
                "privacy_sensitivity": "SENSITIVE",
                "external_training_use": "forbidden",
            },
        )
        user_messages = [
            m["content"]
            for m in packet.qwen_sft_output.get("messages", [])
            if m.get("role") == "user"
        ]
        self.assertTrue(user_messages)
        self.assertTrue(all(secret not in message for message in user_messages))
        self.assertTrue(any("sha256=" in message for message in user_messages))
        self.assertFalse(packet.qwen_sft_output["metadata"]["qwen_sft_ready"])

    def test_package_version_matches_release(self):
        self.assertEqual(semantic_compiler.__version__, "2.1.3")


if __name__ == "__main__":
    unittest.main()
