"""Domain template index and lookup."""
from expansion.registry.loader import load_templates, DomainTemplate

_TEMPLATES: dict[str, DomainTemplate] | None = None

def _ensure_loaded() -> dict[str, DomainTemplate]:
    global _TEMPLATES
    if _TEMPLATES is None:
        _TEMPLATES = load_templates()
    return _TEMPLATES

def get_template(domain: str) -> DomainTemplate:
    templates = _ensure_loaded()
    if domain not in templates:
        return templates["universal_generic"]
    return templates[domain]

def list_domains() -> list[str]:
    return list(_ensure_loaded().keys())
