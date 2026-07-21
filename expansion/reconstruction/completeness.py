"""Scope-aware completeness assessment."""
from expansion.registry.loader import DomainTemplate

def assess_completeness(system_model: dict, template: DomainTemplate) -> str:
    """Return completeness scope: whole_system_claimed | fragmentary | unknown."""
    if system_model.get("claims_complete_system"):
        return "whole_system_claimed"
    if len(system_model.get("components", [])) < 2:
        return "fragmentary"
    return "unknown"
