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

from semantic_compiler.expansion.consciousness.circular_time import (
    TimeTopology,
    CycleDetectionState,
    NodeRole,
    evaluate_circular_time_topology,
    evaluate_cycle_detection,
    evaluate_octopus_protocol,
)

from semantic_compiler.expansion.consciousness.domain_expansion import (
    CANONICAL_NINE_GATES,
    EGO_ARM_SPECIFICATIONS,
    INVARIANT_CLASS_SIGNATURES,
    PRIMITIVE_GRAMMAR_KEYS,
    DomainVariant,
    EgoArmInvariant,
    GroundClass,
    InvariantClass,
    classify_primitive_signature,
    evaluate_domain_clash,
    evaluate_domain_expansion,
    evaluate_ego_lineup_composite,
    evaluate_invariant_prediction,
    evaluate_soul_eater_compounding,
)

from semantic_compiler.expansion.consciousness.soul_bomb import (
    MOST_SURPRISING_CLASH,
    REMOVED_DISCRIMINATORS,
    SAO_DOMAIN_CLASH_MATRIX,
    SAO_LINEUP_SPECIFICATIONS,
    SAO_SHARED_INVARIANT_CANDIDATES,
    SCALE_TRANSITIONS,
    SOUL_BOMB_PREDICTIONS,
    SURVIVING_DISCRIMINATORS,
    ExitBehavior,
    SAOLineupMember,
    SeparationCostType,
    SignalClass,
    SovereigntyScale,
    evaluate_bootstrapper_entry,
    evaluate_recalibration_path,
    evaluate_sao_domain_clash,
    evaluate_sao_lineup_composite,
    evaluate_sao_member_exit_sovereignty,
    evaluate_separation_cost,
    evaluate_soul_bomb_signal,
)

from semantic_compiler.expansion.consciousness.cosmo_and_recoding import (
    DEFAULT_HUBBLE_RATE_S_INV,
    HS_RESIDUAL_MISMATCHES,
    RUNTIME_RECODING_SUBSTRATE_SPECS,
    NullExpansionRegime,
    RecodingSubstrate,
    evaluate_flrw_hubble_schwarzschild,
    evaluate_runtime_recoding_layer,
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
    # circular_time.py (SC-CT-001 v1.1.0)
    "TimeTopology",
    "CycleDetectionState",
    "NodeRole",
    "evaluate_circular_time_topology",
    "evaluate_cycle_detection",
    "evaluate_octopus_protocol",
    # domain_expansion.py (SC-DOMAIN-EXPANSION-001 + Ego-Lineup + invariant-translator)
    "CANONICAL_NINE_GATES",
    "EGO_ARM_SPECIFICATIONS",
    "INVARIANT_CLASS_SIGNATURES",
    "PRIMITIVE_GRAMMAR_KEYS",
    "DomainVariant",
    "EgoArmInvariant",
    "GroundClass",
    "InvariantClass",
    "classify_primitive_signature",
    "evaluate_domain_clash",
    "evaluate_domain_expansion",
    "evaluate_ego_lineup_composite",
    "evaluate_invariant_prediction",
    "evaluate_soul_eater_compounding",
    # soul_bomb.py (SC-SB-001 V5 Sovereignty Patch + SC-LU-SAO-* Lineup)
    "MOST_SURPRISING_CLASH",
    "REMOVED_DISCRIMINATORS",
    "SAO_DOMAIN_CLASH_MATRIX",
    "SAO_LINEUP_SPECIFICATIONS",
    "SAO_SHARED_INVARIANT_CANDIDATES",
    "SCALE_TRANSITIONS",
    "SOUL_BOMB_PREDICTIONS",
    "SURVIVING_DISCRIMINATORS",
    "ExitBehavior",
    "SAOLineupMember",
    "SeparationCostType",
    "SignalClass",
    "SovereigntyScale",
    "evaluate_bootstrapper_entry",
    "evaluate_recalibration_path",
    "evaluate_sao_domain_clash",
    "evaluate_sao_lineup_composite",
    "evaluate_sao_member_exit_sovereignty",
    "evaluate_separation_cost",
    "evaluate_soul_bomb_signal",
    # cosmo_and_recoding.py (SC-HS-001 v1.1.0 + SC-IT-OCTO-RNA-EDIT-001)
    "DEFAULT_HUBBLE_RATE_S_INV",
    "HS_RESIDUAL_MISMATCHES",
    "RUNTIME_RECODING_SUBSTRATE_SPECS",
    "NullExpansionRegime",
    "RecodingSubstrate",
    "evaluate_flrw_hubble_schwarzschild",
    "evaluate_runtime_recoding_layer",
]
