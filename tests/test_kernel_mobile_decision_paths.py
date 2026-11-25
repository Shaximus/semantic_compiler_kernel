"""Characterization tests for Kernel Mobile's six bench prompts.

These pin the *decision path*, not latency: Stage 3 no-target early exit
(PASS_THROUGH since the pass-through change; 04 and 05 resolve a target since
the router feeds compile) versus a `structural_fit` hard
floor, versus a clean COMPILED result.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_compiler import compile_semantic_packet
from semantic_compiler.core.pipeline import PASS_THROUGH_REASON, PASS_THROUGH_ROUTE
from semantic_compiler.core.scoring import STRUCTURAL_FIT_MIN
from semantic_compiler.core.types import Decision

PROMPT_DIR = Path(__file__).resolve().parent / "fixtures" / "kernel_mobile_prompts"

# (filename stem, expected decision name, expected driver)
CASES = [
    ("01_short_fragment", "PASS_THROUGH", "NO_TARGET_SYSTEM_RESOLVED"),
    ("02_readme_gem", "NEEDS_REVISION", "LOW_STRUCTURAL_FIT"),
    ("03_kv_cache", "NEEDS_REVISION", "LOW_STRUCTURAL_FIT"),
    # Router feed: the router recognizes these domains (mobile_security, medical).
    ("04_android_security", "COMPILED", "COMPILED"),
    ("05_clinic_redesign", "NEEDS_REVISION", "LOW_STRUCTURAL_FIT"),
    ("06_long_multi_domain", "COMPILED", "COMPILED"),
]


def _load(stem: str) -> str:
    return (PROMPT_DIR / f"{stem}.txt").read_text(encoding="utf-8")


def _driver(packet) -> str:
    if packet.decision == Decision.COMPILED:
        return "COMPILED"
    if (
        packet.decision == Decision.PASS_THROUGH
        and not packet.target_systems
        and PASS_THROUGH_REASON in packet.compiler_warnings
    ):
        return "NO_TARGET_SYSTEM_RESOLVED"
    scores = packet.scores or {}
    structural_fit = scores.get("structural_fit")
    if (
        packet.decision == Decision.NEEDS_REVISION
        and packet.target_systems
        and structural_fit is not None
        and structural_fit < STRUCTURAL_FIT_MIN
    ):
        return "LOW_STRUCTURAL_FIT"
    return f"UNCHARACTERIZED:{packet.decision}"


@pytest.mark.parametrize("stem,decision,driver", CASES)
def test_kernel_mobile_prompt_decision_path(stem: str, decision: str, driver: str) -> None:
    packet = compile_semantic_packet(_load(stem))
    assert packet.decision.name == decision
    assert _driver(packet) == driver

    if driver == "NO_TARGET_SYSTEM_RESOLVED":
        assert not packet.target_systems
        assert PASS_THROUGH_REASON in packet.compiler_warnings
        assert packet.route_to == [PASS_THROUGH_ROUTE]
        assert packet.semantic_error_class is None
        assert not packet.compiler_errors
        # Stage 3 returns before score_packet; scores stay empty.
        assert not packet.scores
    elif driver == "LOW_STRUCTURAL_FIT":
        assert packet.target_systems
        assert packet.scores
        assert packet.scores["structural_fit"] < STRUCTURAL_FIT_MIN
        # Hard gates are not the reason these two fail.
        assert packet.scores.get("hard_gates_passed") == 1.0
    elif driver == "COMPILED":
        assert packet.target_systems
        assert packet.scores
        assert packet.scores["structural_fit"] >= STRUCTURAL_FIT_MIN
        assert packet.scores.get("hard_gates_passed") == 1.0
