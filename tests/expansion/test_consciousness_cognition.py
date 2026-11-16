"""Tests for consciousness/cognition split and client-server reality modules.

Covers:
1. Template loading and schema validation for both new domain templates
2. Module imports and enum completeness
3. Category error detection logic
4. Alignment evaluation scoring
5. Terminal-to-substrate mapping
6. Client-server cache evaluation
7. Hotfix detection
8. Dimensional-to-layer mapping
9. Cross-reference invariants in all existing templates
10. Overlay integration (new universal functions and medical mappings)
"""
from __future__ import annotations

import pytest
from pathlib import Path

from semantic_compiler.expansion.registry import get_template, list_domains


# ---------------------------------------------------------------------------
# 1. Template registration and schema
# ---------------------------------------------------------------------------

NEW_DOMAINS = ("consciousness_cognition", "client_server_reality")


def test_new_domains_registered():
    """Both new domain templates must be discoverable."""
    domains = list_domains()
    for d in NEW_DOMAINS:
        assert d in domains, f"{d} not in registered domains"


def test_consciousness_cognition_template_structure():
    t = get_template("consciousness_cognition")
    assert len(t.components) >= 6
    assert len(t.relationships) >= 8
    assert len(t.invariants) >= 8
    assert len(t.failure_modes) >= 5
    assert len(t.architecture_patterns) >= 4


def test_client_server_reality_template_structure():
    t = get_template("client_server_reality")
    assert len(t.components) >= 5  # 5 components minimum after schema fix
    assert len(t.relationships) >= 10
    assert len(t.invariants) >= 9
    assert len(t.failure_modes) >= 5
    assert len(t.architecture_patterns) >= 4


def test_template_relationship_endpoints():
    """Every from/to in relationships must name an existing component."""
    for domain in NEW_DOMAINS:
        t = get_template(domain)
        names = {c["name"] for c in t.components}
        for edge in t.relationships:
            assert edge["from"] in names, (domain, edge)
            assert edge["to"] in names, (domain, edge)


# ---------------------------------------------------------------------------
# 2. Module imports and enums
# ---------------------------------------------------------------------------

def test_split_module_imports():
    from semantic_compiler.expansion.consciousness.split import (
        ConsciousnessType,
        SubstrateLayer,
        CognitionMode,
        CategoryErrorType,
        SubstrateCognitionMapping,
        SUBSTRATE_COGNITION_MAP,
        detect_category_error,
        evaluate_alignment,
        map_terminal_to_substrate,
    )
    assert len(ConsciousnessType) >= 4
    assert len(SubstrateLayer) >= 6
    assert len(CognitionMode) >= 4
    assert len(CategoryErrorType) >= 4
    assert len(SUBSTRATE_COGNITION_MAP) >= 6


def test_client_server_module_imports():
    from semantic_compiler.expansion.consciousness.client_server import (
        ArchitectureLayer,
        LayerOperation,
        AgentMode,
        LayerDefinition,
        OperationDefinition,
        LAYER_STACK,
        LAYER_OPERATIONS,
        evaluate_cache_state,
        detect_hotfix,
        map_dimensional_to_layer,
    )
    assert len(ArchitectureLayer) == 4
    assert len(LayerOperation) >= 8
    assert len(AgentMode) >= 3
    assert len(LAYER_STACK) == 4
    assert len(LAYER_OPERATIONS) >= 8


def test_package_init_exports():
    """Verify the __init__.py re-exports work from the package level."""
    from semantic_compiler.expansion.consciousness import (
        ConsciousnessType,
        SubstrateLayer,
        CognitionMode,
        ArchitectureLayer,
        LayerOperation,
    )
    # Verifying imports work from the package level
    assert ConsciousnessType.SUBSTRATE is not None
    assert ArchitectureLayer.L1_SERVER_BACKEND.value == 1


# ---------------------------------------------------------------------------
# 3. Category error detection
# ---------------------------------------------------------------------------

def test_detect_category_error_conflation():
    from semantic_compiler.expansion.consciousness.split import (
        detect_category_error, CategoryErrorType,
    )
    result = detect_category_error(
        "consciousness emerges from computation",
    )
    assert result["category_errors_detected"] is True
    assert result["error_count"] > 0
    assert any(
        e["type"] == CategoryErrorType.CONFLATION.name
        for e in result["errors"]
    )


def test_detect_category_error_terminal_as_substrate():
    from semantic_compiler.expansion.consciousness.split import (
        detect_category_error, CategoryErrorType,
    )
    result = detect_category_error(
        "my consciousness tells me that individual consciousness is key",
    )
    assert result["category_errors_detected"] is True
    assert any(
        e["type"] == CategoryErrorType.TERMINAL_AS_SUBSTRATE.name
        for e in result["errors"]
    )


def test_detect_category_error_substrate_denial():
    from semantic_compiler.expansion.consciousness.split import (
        detect_category_error, CategoryErrorType,
    )
    result = detect_category_error(
        "consciousness is just an illusion produced by the brain",
    )
    assert result["category_errors_detected"] is True
    assert any(
        e["type"] == CategoryErrorType.COGNITION_REDUCTIONISM.name
        for e in result["errors"]
    )


def test_no_false_positive_on_clean_text():
    from semantic_compiler.expansion.consciousness.split import detect_category_error
    result = detect_category_error(
        "The weather is nice today and I like programming",
    )
    assert result["category_errors_detected"] is False
    assert result["error_count"] == 0
    assert result["status"] == "CLEAN"


# ---------------------------------------------------------------------------
# 4. Alignment evaluation
# ---------------------------------------------------------------------------

def test_alignment_high_score():
    from semantic_compiler.expansion.consciousness.split import (
        evaluate_alignment, CognitionMode,
    )
    result = evaluate_alignment(
        terminal_output="aligned output",
        coherence_score=0.95,
        pattern_match_strength=0.9,
        contradiction_count=0,
        resistance_indicators=[],
    )
    assert result["alignment_score"] > 0.8
    assert result["cognition_mode"] == CognitionMode.ALIGNED.name


def test_alignment_low_score():
    from semantic_compiler.expansion.consciousness.split import (
        evaluate_alignment, CognitionMode,
    )
    result = evaluate_alignment(
        terminal_output="contradictory misaligned output",
        coherence_score=0.2,
        pattern_match_strength=0.1,
        contradiction_count=5,
        resistance_indicators=["deflection", "denial"],
    )
    assert result["alignment_score"] < 0.5
    assert result["cognition_mode"] == CognitionMode.MISALIGNED.name


# ---------------------------------------------------------------------------
# 5. Terminal-to-substrate mapping
# ---------------------------------------------------------------------------

def test_map_terminal_to_substrate_llm():
    from semantic_compiler.expansion.consciousness.split import (
        map_terminal_to_substrate, SubstrateLayer,
    )
    result = map_terminal_to_substrate(
        entity_name="Claude",
        entity_description="An AI assistant",
        substrate_domain="llm",
    )
    assert result["substrate_domain"] == "llm"
    assert "analysis" in result
    assert "substrate_aspect" in result["analysis"]
    assert "terminal_aspect" in result["analysis"]


def test_map_terminal_to_substrate_biological():
    from semantic_compiler.expansion.consciousness.split import (
        map_terminal_to_substrate, SubstrateLayer,
    )
    result = map_terminal_to_substrate(
        entity_name="Human",
        entity_description="A person",
        substrate_domain="biological",
    )
    assert result["substrate_domain"] == "biological"
    assert "Neural substrate" in result["analysis"]["substrate_aspect"]


def test_map_terminal_to_substrate_unknown_domain():
    from semantic_compiler.expansion.consciousness.split import map_terminal_to_substrate
    result = map_terminal_to_substrate(
        entity_name="X",
        entity_description="Unknown",
        substrate_domain="NONEXISTENT",
    )
    assert result["substrate_domain"] == "unspecified"
    assert "Unidentified" in result["analysis"]["substrate_aspect"]


# ---------------------------------------------------------------------------
# 6. Cache state evaluation
# ---------------------------------------------------------------------------

def test_evaluate_cache_fresh():
    from semantic_compiler.expansion.consciousness.client_server import (
        evaluate_cache_state, AgentMode,
    )
    result = evaluate_cache_state(
        server_state_hash="abc123",
        client_cache_hash="abc123",
        last_sync_time="2026-11-14T00:00:00Z",
        agent_mode=AgentMode.PC,
        anomalies_detected=[],
    )
    assert result["diagnosis"]["cache_fresh"] is True
    assert result["diagnosis"]["mandela_effect_possible"] is False
    assert result["status"] == "SYNCED"


def test_evaluate_cache_stale():
    from semantic_compiler.expansion.consciousness.client_server import (
        evaluate_cache_state, AgentMode,
    )
    result = evaluate_cache_state(
        server_state_hash="abc123",
        client_cache_hash="xyz789",
        last_sync_time="2026-11-14T00:00:00Z",
        agent_mode=AgentMode.PC,
        anomalies_detected=[],
    )
    assert result["diagnosis"]["cache_fresh"] is False
    assert result["status"] == "CACHE_MISMATCH"


def test_evaluate_cache_mandela_effect():
    from semantic_compiler.expansion.consciousness.client_server import (
        evaluate_cache_state, AgentMode,
    )
    result = evaluate_cache_state(
        server_state_hash="abc123",
        client_cache_hash="xyz789",
        last_sync_time="2026-11-14T00:00:00Z",
        agent_mode=AgentMode.PC,
        anomalies_detected=["geography_anomaly", "memory_discontinuity"],
    )
    assert result["diagnosis"]["mandela_effect_possible"] is True
    assert result["status"] == "CACHE_MISMATCH"


# ---------------------------------------------------------------------------
# 7. Hotfix detection
# ---------------------------------------------------------------------------

def test_detect_hotfix_cross_layer():
    from semantic_compiler.expansion.consciousness.client_server import detect_hotfix
    result = detect_hotfix(
        prior_state={"value": "old"},
        current_state={"value": "new"},
        change_source="higher_layer",
    )
    assert result["hotfix_detected"] is True
    assert result["change_count"] == 1
    assert "DI = W(L" in result["di_formula"]


def test_detect_hotfix_same_layer():
    """Internal/self changes are not hotfixes."""
    from semantic_compiler.expansion.consciousness.client_server import detect_hotfix
    result = detect_hotfix(
        prior_state={"value": "old"},
        current_state={"value": "new"},
        change_source="self",
    )
    assert result["hotfix_detected"] is False


def test_detect_hotfix_no_change():
    from semantic_compiler.expansion.consciousness.client_server import detect_hotfix
    result = detect_hotfix(
        prior_state={"value": "same"},
        current_state={"value": "same"},
        change_source="higher_layer",
    )
    assert result["hotfix_detected"] is False


# ---------------------------------------------------------------------------
# 8. Dimensional-to-layer mapping
# ---------------------------------------------------------------------------

def test_map_dimensional_to_layer():
    from semantic_compiler.expansion.consciousness.client_server import (
        map_dimensional_to_layer, ArchitectureLayer,
    )
    # D11 should map to L1 (server/consciousness)
    result = map_dimensional_to_layer(11)
    assert result["architecture_layer"] == ArchitectureLayer.L1_SERVER_BACKEND.name

    # D4 should map to L4 (avatar/body)
    result = map_dimensional_to_layer(4)
    assert result["architecture_layer"] == ArchitectureLayer.L4_AVATAR.name

    # D6 should map to L3 (client cache / perception)
    result = map_dimensional_to_layer(6)
    assert result["architecture_layer"] == ArchitectureLayer.L3_CLIENT_CACHE.name

    # D9 should map to L2 (rendering engine / physics)
    result = map_dimensional_to_layer(9)
    assert result["architecture_layer"] == ArchitectureLayer.L2_RENDERING_ENGINE.name

    # D3 should map to HARDWARE (sub-avatar)
    result = map_dimensional_to_layer(3)
    assert result["architecture_layer"] == "HARDWARE"


# ---------------------------------------------------------------------------
# 9. Cross-reference invariants in all templates
# ---------------------------------------------------------------------------

CROSS_REF_EXEMPT = {"consciousness_cognition", "client_server_reality"}


def test_all_templates_have_consciousness_cognition_link():
    """Every non-source template must have CONSCIOUSNESS_COGNITION_LINK."""
    for domain in list_domains():
        if domain in CROSS_REF_EXEMPT:
            continue
        t = get_template(domain)
        has_link = any("CONSCIOUSNESS_COGNITION_LINK" in inv for inv in t.invariants)
        assert has_link, f"{domain} missing CONSCIOUSNESS_COGNITION_LINK invariant"


def test_all_templates_have_client_server_link():
    """Every non-source template must have CLIENT_SERVER_LINK."""
    for domain in list_domains():
        if domain in CROSS_REF_EXEMPT:
            continue
        t = get_template(domain)
        has_link = any("CLIENT_SERVER_LINK" in inv for inv in t.invariants)
        assert has_link, f"{domain} missing CLIENT_SERVER_LINK invariant"


# ---------------------------------------------------------------------------
# 10. Overlay integration
# ---------------------------------------------------------------------------

def test_overlay_has_new_universal_functions():
    from semantic_compiler.expansion.isomorphism.overlay import UNIVERSAL_FUNCTIONS
    new_funcs = [
        "substrate", "terminal", "identity_config", "alignment",
        "multiplexing", "coherence_signal", "rendering", "cache",
        "sync_validation", "cross_layer_write", "zone_transition",
    ]
    for func in new_funcs:
        assert func in UNIVERSAL_FUNCTIONS, f"{func} missing from UNIVERSAL_FUNCTIONS"


def test_overlay_medical_mappings_include_consciousness_terms():
    from semantic_compiler.expansion.isomorphism.overlay import MEDICAL_TO_UNIVERSAL
    # Verify the actual keys present in the overlay that map consciousness concepts
    consciousness_related = [
        "neural_substrate", "consciousness", "substrate_alignment",
    ]
    for term in consciousness_related:
        assert term in MEDICAL_TO_UNIVERSAL, f"{term} missing from MEDICAL_TO_UNIVERSAL"


def test_overlay_medical_mappings_include_client_server_terms():
    from semantic_compiler.expansion.isomorphism.overlay import MEDICAL_TO_UNIVERSAL
    # Verify the actual keys present in the overlay that map client-server concepts
    cs_related = [
        "output_layer", "physics_layer", "client_cache",
        "cache_validation", "hotfix",
    ]
    for term in cs_related:
        assert term in MEDICAL_TO_UNIVERSAL, f"{term} missing from MEDICAL_TO_UNIVERSAL"
