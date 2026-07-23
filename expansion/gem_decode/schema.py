"""Gem-build schema validation (jsonschema, Draft 2020-12)."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "schemas"
    / "v2_2_gem_build.schema.json"
)

with open(SCHEMA_PATH) as _f:
    V2_2_GEM_BUILD_SCHEMA = json.load(_f)

_VALIDATOR = Draft202012Validator(V2_2_GEM_BUILD_SCHEMA)


def validate_gem_build(record: dict) -> list[str]:
    """Validate a decoded gem build. Returns list of errors ([] = valid)."""
    errors = []
    for e in _VALIDATOR.iter_errors(record):
        path = ".".join(str(p) for p in e.absolute_path)
        errors.append(f"{path}: {e.message}" if path else e.message)
    return errors
