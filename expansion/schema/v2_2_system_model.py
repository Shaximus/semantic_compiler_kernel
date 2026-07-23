"""V2.2 system model schema validation (jsonschema, Draft 2020-12)."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "v2_2_system_model.schema.json"

with open(SCHEMA_PATH) as _f:
    V2_2_SYSTEM_MODEL_SCHEMA = json.load(_f)

_VALIDATOR = Draft202012Validator(V2_2_SYSTEM_MODEL_SCHEMA)


def validate_system_model(model: dict) -> list[str]:
    """Validate a V2.2 system model. Returns list of errors.

    Uses jsonschema Draft 2020-12 validation against
    expansion/schemas/v2_2_system_model.schema.json (the contract), matching
    the approach of core.dataset.validate_dataset_row.
    """
    errors = []
    for e in _VALIDATOR.iter_errors(model):
        path = ".".join(str(p) for p in e.absolute_path)
        errors.append(f"{path}: {e.message}" if path else e.message)
    return errors
