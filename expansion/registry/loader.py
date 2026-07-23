"""Load and validate domain templates."""
import yaml
from dataclasses import dataclass
from pathlib import Path
from semantic_compiler.expansion.schema import validate_domain_template

@dataclass(frozen=True)
class DomainTemplate:
    domain: str
    version: float
    description: str
    components: list[dict]
    relationships: list[dict]
    invariants: list[str]
    failure_modes: list[dict]
    architecture_patterns: list[dict]

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

def load_templates(template_dir: Path | None = None) -> dict[str, DomainTemplate]:
    """Load and validate all *.yaml domain templates from template_dir, keyed by domain."""
    template_dir = template_dir or TEMPLATE_DIR
    templates: dict[str, DomainTemplate] = {}
    for path in template_dir.glob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        errors = validate_domain_template(data)
        if errors:
            raise ValueError(f"Invalid template {path}: {errors}")
        tmpl = DomainTemplate(**data)
        templates[tmpl.domain] = tmpl
    return templates
