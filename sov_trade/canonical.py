"""RFC 8785 JSON Canonicalization Scheme (JCS) for signed envelopes.

Signed objects in this package use only JSON types that JCS defines
unambiguously: objects, arrays, strings, integers, booleans and null.
Floating-point numbers are rejected (PROVISIONAL_DEFAULT: integer
time and value fields only; see docs/PENDING_DELIBERATION.md).
"""

from __future__ import annotations

import json
import math
from typing import Any


class CanonicalizationError(ValueError):
    """The value cannot be canonically serialized under this profile."""


def _utf16_key(key: str) -> list[int]:
    """Sort key per RFC 8785: UTF-16 code units."""
    return [ord(ch) for ch in key.encode("utf-16-be").decode("utf-16-be")]


def _serialize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        raise CanonicalizationError(
            "floating-point numbers are not accepted in signed objects"
        )
    if isinstance(value, (bytes, bytearray, memoryview)):
        raise CanonicalizationError("bytes are not a JSON type; use a hex or integer field")
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_serialize(item) for item in value) + "]"
    if isinstance(value, dict):
        for key in value:
            if not isinstance(key, str):
                raise CanonicalizationError("object keys must be strings")
        items = sorted(value.items(), key=lambda kv: _utf16_key(kv[0]))
        inner = ",".join(
            json.dumps(k, ensure_ascii=False, separators=(",", ":"))
            + ":"
            + _serialize(v)
            for k, v in items
        )
        return "{" + inner + "}"
    raise CanonicalizationError(f"unsupported type: {type(value).__name__}")


def canonical_json(value: Any) -> bytes:
    """Return the UTF-8 JCS encoding of *value*."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise CanonicalizationError("non-finite floats are not accepted")
    return _serialize(value).encode("utf-8")
