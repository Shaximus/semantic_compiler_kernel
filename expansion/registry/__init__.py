"""Domain template registry."""
from .loader import DomainTemplate, load_templates
from .index import get_template, list_domains

__all__ = ["DomainTemplate", "load_templates", "get_template", "list_domains"]
