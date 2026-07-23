"""Known-good architecture patterns."""
from semantic_compiler.expansion.advisor.improvements import AdvisorSuggestion

KNOWN_PATTERNS: list[AdvisorSuggestion] = [
    AdvisorSuggestion(
        kind="architecture_improvement",
        description="defense_in_depth",
        medical_ontology_reference="immune_system",
        confidence=0.9,
        evidence=["layered boundaries reduce single-point failure"],
        domain_specific_translation="multiple independent defense layers",
        estimated_impact="high",
    ),
    AdvisorSuggestion(
        kind="resilience_training",
        description="stress_test_boundary",
        medical_ontology_reference="vaccination",
        confidence=0.85,
        evidence=["pre-emptive hardening against known threats"],
        domain_specific_translation="adversarial input testing",
        estimated_impact="medium",
    ),
]
