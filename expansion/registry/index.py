"""Domain template index and lookup."""
from expansion.registry.loader import load_templates, DomainTemplate

_TEMPLATES: dict[str, DomainTemplate] | None = None

def _ensure_loaded() -> dict[str, DomainTemplate]:
    global _TEMPLATES
    if _TEMPLATES is None:
        _TEMPLATES = load_templates()
    return _TEMPLATES

def get_template(domain: str) -> DomainTemplate:
    """Return the template for domain, falling back to universal_generic when unknown."""
    templates = _ensure_loaded()
    if domain not in templates:
        return templates["universal_generic"]
    return templates[domain]

def list_domains() -> list[str]:
    """Return the names of all loaded domains."""
    return list(_ensure_loaded().keys())
