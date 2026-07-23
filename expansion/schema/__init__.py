"""Domain template validation (jsonschema, Draft 2020-12)."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

DOMAIN_TEMPLATE_SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "domain-template.schema.json"

with open(DOMAIN_TEMPLATE_SCHEMA_PATH) as _f:
    DOMAIN_TEMPLATE_SCHEMA = json.load(_f)

_VALIDATOR = Draft202012Validator(DOMAIN_TEMPLATE_SCHEMA)


def validate_domain_template(template: dict) -> list[str]:
    """Validate a domain template against the schema. Returns list of errors."""
    errors = []
    for e in _VALIDATOR.iter_errors(template):
        path = ".".join(str(p) for p in e.absolute_path)
        errors.append(f"{path}: {e.message}" if path else e.message)
    return errors
