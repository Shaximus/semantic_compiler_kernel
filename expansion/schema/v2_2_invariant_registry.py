"""V2.2 invariant-registry / corpus report schema validation (Draft 2020-12)."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "v2_2_invariant_registry.schema.json"

with open(SCHEMA_PATH) as _f:
    V2_2_INVARIANT_REGISTRY_SCHEMA = json.load(_f)

_VALIDATOR = Draft202012Validator(V2_2_INVARIANT_REGISTRY_SCHEMA)


def _format_error(e) -> str:
    path = ".".join(str(p) for p in e.absolute_path)
    return f"{path}: {e.message}" if path else e.message


def validate_corpus_report(report: dict) -> list[str]:
    """Validate a full corpus report. Returns list of errors ([] = valid)."""
    return [_format_error(e) for e in _VALIDATOR.iter_errors(report)]


def validate_invariant_registry(registry: list) -> list[str]:
    """Validate just the invariant registry array. Returns list of errors."""
    invariant_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "array",
        "items": V2_2_INVARIANT_REGISTRY_SCHEMA["$defs"]["invariant"],
    }
    # Resolve the local $refs inside the invariant def against the full schema.
    full = dict(V2_2_INVARIANT_REGISTRY_SCHEMA)
    full.update(invariant_schema)
    full.pop("required", None)
    full.pop("properties", None)
    validator = Draft202012Validator(full)
    return [_format_error(e) for e in validator.iter_errors(registry)]
