"""Domain template validation."""
import json
from pathlib import Path

DOMAIN_TEMPLATE_SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "domain-template.schema.json"

def validate_domain_template(template: dict) -> list[str]:
    """Validate a domain template against the schema. Returns list of errors."""
    errors = []
    required = ["domain", "version", "description", "components", "relationships", "invariants", "failure_modes", "architecture_patterns"]
    for field in required:
        if field not in template:
            errors.append(f"missing required field: {field}")
    for fm in template.get("failure_modes", []):
        if "medical_map" not in fm:
            errors.append(f"failure_mode {fm.get('name')} missing medical_map")
    return errors
