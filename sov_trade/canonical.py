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


# I-JSON (RFC 7493) / RFC 8785: numbers are IEEE 754 doubles, so only
# integers in [-(2**53 - 1), 2**53 - 1] round-trip exactly.
MAX_SAFE_INTEGER = 2**53 - 1


def _utf16_key(key: str) -> bytes:
    """Sort key per RFC 8785 section 3.2.3: UTF-16 code units.

    Big-endian UTF-16 bytes compare in the same order as the sequence of
    16-bit code units, so astral characters (surrogate pairs, 0xD800+)
    sort before U+E000..U+FFFF, as the RFC requires. Lone surrogates
    are not valid JSON text and are rejected.
    """
    try:
        return key.encode("utf-16-be")
    except UnicodeEncodeError as exc:
        raise CanonicalizationError("object key contains a lone surrogate") from exc


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
        if abs(value) > MAX_SAFE_INTEGER:
            # PROVISIONAL_DEFAULT (docs/PENDING_DELIBERATION.md): integers
            # outside the I-JSON safe range are refused, not rounded.
            raise CanonicalizationError("integer outside the I-JSON safe range")
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
    try:
        return _serialize(value).encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CanonicalizationError("string contains a lone surrogate") from exc
    except RecursionError as exc:
        raise CanonicalizationError("value is nested too deeply") from exc
