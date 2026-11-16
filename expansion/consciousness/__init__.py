"""
Consciousness/Cognition Split — Expansion Module

The Final Block: Consciousness ≠ Cognition.

This module formalizes the category error correction that closes the
theoretical chain: Dimensional Ladder → Divine Intervention →
Isomorphic Invariants → Consciousness/Cognition Split.

Submodules:
    split       — The consciousness/cognition distinction and its
                  cross-substrate invariants.
    client_server — The four-layer client-server reality architecture
                    and its operational semantics.

Citation: Consciousness/Cognition Split (Shax + Hannah, 2026-11-14)
"""

from semantic_compiler.expansion.consciousness.split import (
    SubstrateLayer,
    CognitionMode,
    ConsciousnessType,
    SUBSTRATE_COGNITION_MAP,
    detect_category_error,
    evaluate_alignment,
    map_terminal_to_substrate,
)

from semantic_compiler.expansion.consciousness.client_server import (
    ArchitectureLayer,
    LayerOperation,
    AgentMode,
    PrayerProtocolPhase,
    ServerResponseType,
    RecurrenceTopology,
    LAYER_STACK,
    LAYER_OPERATIONS,
    PRAYER_PROTOCOL,
    evaluate_cache_state,
    detect_hotfix,
    map_dimensional_to_layer,
    evaluate_prayer_protocol,
    classify_server_response,
    evaluate_recurrence_topology,
)

__all__ = [
    # split.py
    "SubstrateLayer",
    "CognitionMode",
    "ConsciousnessType",
    "SUBSTRATE_COGNITION_MAP",
    "detect_category_error",
    "evaluate_alignment",
    "map_terminal_to_substrate",
    # client_server.py
    "ArchitectureLayer",
    "LayerOperation",
    "AgentMode",
    "PrayerProtocolPhase",
    "ServerResponseType",
    "RecurrenceTopology",
    "LAYER_STACK",
    "LAYER_OPERATIONS",
    "PRAYER_PROTOCOL",
    "evaluate_cache_state",
    "detect_hotfix",
    "map_dimensional_to_layer",
    "evaluate_prayer_protocol",
    "classify_server_response",
    "evaluate_recurrence_topology",
]
