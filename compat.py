"""Kestrel Lab compatibility wrapper for V2.1.3.

This module leaves the canonical pipeline implementation untouched while fixing
post-decision derivative consistency and sensitive-input leakage at the package
entry point.
"""
from __future__ import annotations

from semantic_compiler.core.pipeline import (
    compile_semantic_packet as _compile,
    build_routing_packet,
    generate_literal_translation,
    generate_public_translation,
    generate_executive_translation,
    build_qwen_sft_output,
)
from semantic_compiler.core.dataset import build_dataset_row
from semantic_compiler.core.audit import build_audit_record
from semantic_compiler.core.types import PrivacySensitivity


def _redact_sensitive_qwen_user_content(packet) -> None:
    """Ensure sensitive raw text never survives in the exported SFT prompt."""
    if packet.privacy_sensitivity not in {
        PrivacySensitivity.SENSITIVE,
        PrivacySensitivity.CRITICAL,
    }:
        return
    messages = packet.qwen_sft_output.get("messages", [])
    for message in messages:
        if message.get("role") == "user":
            digest = packet.compute_input_hash()
            message["content"] = f"Compile (redacted input; sha256={digest})"


def compile_semantic_packet(input_text, registry=None, context=None, mode="AUTO"):
    """Compile and then rebuild all decision-dependent derivative artifacts."""
    packet = _compile(input_text, registry=registry, context=context, mode=mode)

    # The V2.1.3 core pipeline creates these artifacts before the final decision.
    # Rebuild them so no exported surface retains PENDING or stale routing state.
    packet.routing_packet = build_routing_packet(packet)
    packet.route_to = list(packet.routing_packet.get("route_to", []))
    packet.literal_translation = generate_literal_translation(packet)
    packet.public_translation = generate_public_translation(packet)
    packet.executive_translation = generate_executive_translation(packet)

    # Rebuild decision-dependent training and audit derivatives.
    packet.dataset_row = build_dataset_row(packet)
    packet.qwen_sft_output = build_qwen_sft_output(packet)
    _redact_sensitive_qwen_user_content(packet)
    packet.audit = build_audit_record(packet)
    return packet
