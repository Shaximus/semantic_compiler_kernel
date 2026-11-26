"""Positive allowlist branching for SC-MAFUBA-001 (reference only).

Only explicit ALLOW or CONTINUE may proceed. Any other status, including
a missing or unknown status, halts. This is not kernel enforcement.
"""

from __future__ import annotations

from typing import Optional

# ALLOW and CONTINUE are equivalent proceed statuses.
PROCEED_STATUSES = frozenset({"ALLOW", "CONTINUE"})


def must_halt(status: Optional[str]) -> bool:
    """Return True unless status is an explicit proceed status."""
    return status not in PROCEED_STATUSES


def halt_reason(status: Optional[str]) -> str:
    if status in PROCEED_STATUSES:
        raise ValueError("proceed status has no halt reason")
    if not status:
        return "MISSING_STATUS"
    return status


def resolve_branch(status: Optional[str], value=None):
    """Return ("CONTINUE", value) or ("HALT", reason).

    Never returns success or CONTINUE for a non-allowlisted status.
    This is the fix for the Section 6.1 Step 8 fail-open bug.
    """
    if status in PROCEED_STATUSES:
        return "CONTINUE", value
    return "HALT", halt_reason(status)
