"""Positive allowlist branching for SC-MAFUBA-001 (reference only).

Only explicit ALLOW or CONTINUE may proceed. Any other status, including
a missing, unknown, malformed, wrongly-typed, or str-subclass status, halts.
This is not kernel enforcement.
"""

from __future__ import annotations

from typing import Any

# ALLOW and CONTINUE are equivalent proceed statuses.
PROCEED_STATUSES = frozenset({"ALLOW", "CONTINUE"})


def _proceeds(status: Any) -> bool:
    # Exact type check: a str subclass can override __eq__/__hash__ and
    # impersonate a proceed status; unhashable values must not raise here.
    return type(status) is str and status in PROCEED_STATUSES


def must_halt(status: Any) -> bool:
    """Return True unless status is an explicit proceed status."""
    return not _proceeds(status)


def halt_reason(status: Any) -> str:
    if _proceeds(status):
        raise ValueError("proceed status has no halt reason")
    if status is None or status == "":
        return "MISSING_STATUS"
    if type(status) is not str:
        return "MALFORMED_STATUS"
    return status


def resolve_branch(status: Any, value=None):
    """Return ("CONTINUE", value) or ("HALT", reason).

    Never returns success or CONTINUE for a non-allowlisted status.
    This is the fix for the Section 6.1 Step 8 fail-open bug.
    """
    if _proceeds(status):
        return "CONTINUE", value
    return "HALT", halt_reason(status)
