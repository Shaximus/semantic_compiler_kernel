"""V2.2 system model schema validation."""
import json
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "v2_2_system_model.schema.json"

with open(SCHEMA_PATH) as _f:
    V2_2_SYSTEM_MODEL_SCHEMA = json.load(_f)


def validate_system_model(model: dict) -> list[str]:
    """Validate a V2.2 system model. Returns list of errors.

    Checks required top-level fields and nested required fields per
    expansion/schemas/v2_2_system_model.schema.json (the contract).
    """
    errors = []
    required = V2_2_SYSTEM_MODEL_SCHEMA["required"]
    for field in required:
        if field not in model:
            errors.append(f"missing required field: {field}")
    for section in ("universal_functional_graph", "pathology_profile", "reconstruction", "advisor"):
        value = model.get(section)
        if not isinstance(value, dict):
            if section in model:
                errors.append(f"{section} must be an object")
            continue
        for nested in V2_2_SYSTEM_MODEL_SCHEMA["properties"][section].get("required", []):
            if nested not in value:
                errors.append(f"missing required field: {section}.{nested}")
    return errors
