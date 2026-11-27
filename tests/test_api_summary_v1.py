"""summary_v1 size/privacy contract and SEMANTIC_COMPILER_CACHE_DIR override."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from semantic_compiler import compile_semantic_packet
from semantic_compiler.api import SUMMARY_SCHEMA, compile_json, summary_v1
from semantic_compiler.expansion.registry.loader import (
    TEMPLATE_DIR,
    _MEM_CACHE,
    _sidecar_cache_path,
    load_templates,
)

PROMPT_DIR = Path(__file__).resolve().parent / "fixtures" / "kernel_mobile_prompts"
TYPICAL_SUMMARY_MAX_BYTES = 2048
REQUIRED_KEYS = (
    "schema",
    "compiler",
    "version",
    "decision",
    "status",
    "dataset_tier",
    "selected_target",
    "target_systems",
    "scores",
    "routing_candidates",
)
FORBIDDEN_DEFAULT_KEYS = ("raw_input", "normalized_input", "forward_text")


def _prompt_texts() -> list[tuple[str, str]]:
    return [
        (path.stem, path.read_text(encoding="utf-8").strip())
        for path in sorted(PROMPT_DIR.glob("*.txt"))
    ]


def test_fixtures_are_the_six_kernel_mobile_prompts() -> None:
    stems = [stem for stem, _ in _prompt_texts()]
    assert stems == [
        "01_short_fragment",
        "02_readme_gem",
        "03_kv_cache",
        "04_android_security",
        "05_clinic_redesign",
        "06_long_multi_domain",
    ]


@pytest.mark.parametrize("stem,text", _prompt_texts())
def test_summary_v1_schema_omits_raw_input_and_stays_small(stem: str, text: str) -> None:
    packet = compile_semantic_packet(text)
    summary = summary_v1(packet)
    payload = json.dumps(summary, default=str, separators=(",", ":")).encode("utf-8")

    assert summary["schema"] == SUMMARY_SCHEMA
    for key in REQUIRED_KEYS:
        assert key in summary, key
    for key in FORBIDDEN_DEFAULT_KEYS:
        assert key not in summary
    # Full source text must not leak into the default summary.
    assert text not in json.dumps(summary, default=str)
    assert text not in payload.decode("utf-8")
    # Typical budget: 2 KiB. The six characterization prompts must all fit.
    assert len(payload) <= TYPICAL_SUMMARY_MAX_BYTES, (
        f"{stem} summary_v1 is {len(payload)} bytes (budget {TYPICAL_SUMMARY_MAX_BYTES})"
    )
    full = json.dumps(packet.to_dict(), default=str, separators=(",", ":")).encode("utf-8")
    assert len(payload) < len(full)
    assert "raw_input" in packet.to_dict()


def test_summary_v1_opt_in_includes_raw_input() -> None:
    text = "The GPU is the weapon; support gems consume VRAM."
    packet = compile_semantic_packet(text)
    summary = summary_v1(packet, include_raw_input=True)
    assert summary["raw_input"] == text
    assert summary["normalized_input"] == packet.normalized_input
    assert summary["forward_text"] == packet.forward_text
    default = summary_v1(packet)
    assert "raw_input" not in default
    assert "forward_text" not in default
    via_compile = compile_json(text, include_raw_input=True)
    assert via_compile["raw_input"] == text
    assert via_compile["forward_text"] == packet.forward_text


def test_compile_json_forward_text_only_when_opted_in() -> None:
    # Short fragment currently exits PASS_THROUGH and may set forward_text.
    text = (PROMPT_DIR / "01_short_fragment.txt").read_text(encoding="utf-8").strip()
    packet = compile_semantic_packet(text)
    default = summary_v1(packet)
    assert "forward_text" not in default
    assert "raw_input" not in default
    opted = summary_v1(packet, include_raw_input=True)
    assert opted["raw_input"] == text
    assert opted["normalized_input"] == packet.normalized_input
    assert "forward_text" in opted
    assert opted["forward_text"] == packet.forward_text


def test_cache_dir_env_override_writes_sidecar_outside_default_temp(tmp_path, monkeypatch) -> None:
    cache_dir = tmp_path / "sck-cache"
    monkeypatch.setenv("SEMANTIC_COMPILER_CACHE_DIR", str(cache_dir))
    _MEM_CACHE.clear()
    try:
        templates = load_templates()
        assert templates
        override_path = _sidecar_cache_path(TEMPLATE_DIR.resolve())
        assert override_path.parent == cache_dir
        assert override_path.is_file()
        # Default tempdir must not be used while the override is set.
        monkeypatch.delenv("SEMANTIC_COMPILER_CACHE_DIR")
        default_path = _sidecar_cache_path(TEMPLATE_DIR.resolve())
        assert default_path != override_path
        assert override_path.parent != default_path.parent
    finally:
        _MEM_CACHE.clear()


_NEVER_IN_SUMMARY_RECORD_KEYS = (
    "claim",
    "self_reported",
    "externally_observed",
    "external_source",
    "mapping",
)


def _assert_keys_absent(obj, forbidden: tuple[str, ...]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            assert key not in forbidden, key
            _assert_keys_absent(value, forbidden)
    elif isinstance(obj, list):
        for item in obj:
            _assert_keys_absent(item, forbidden)


def test_summary_v1_omits_measurement_gate_record_payloads() -> None:
    # Measurement-gate records (gates/measurement.py) carry claim values and
    # observed telemetry, but they are stored on packet.measurement_integrity,
    # not packet.contradictions / packet.category_errors. If one is present on
    # those lists anyway, compact records must not copy the payload keys.
    packet = compile_semantic_packet("remind me to call mom at 6")
    record = {
        "claim": "gpu_utilization_percent",
        "self_reported": 5,
        "externally_observed": 60,
        "external_source": "nvidia-smi",
        "ruling": "EXTERNAL_OBSERVATION_PREVAILS",
        "law": "output_over_self_report",
        "mapping": {"source": "gpu_utilization_percent", "target": "nvidia-smi"},
    }
    packet.contradictions.append(record)
    packet.category_errors.append(dict(record))
    summary = summary_v1(packet)
    # No allowlisted keys on this record (ruling/law do not flow into these lists).
    assert summary["contradictions"] == [{}]
    assert summary["category_errors"] == [{}]
    _assert_keys_absent(summary, _NEVER_IN_SUMMARY_RECORD_KEYS)
    blob = json.dumps(summary, default=str)
    for key in _NEVER_IN_SUMMARY_RECORD_KEYS:
        assert key not in blob
    for leaked in ("gpu_utilization_percent", "nvidia-smi"):
        assert leaked not in blob


def test_summary_v1_keeps_category_error_and_omits_mapping() -> None:
    # detect_category_errors (core/pipeline.py) emits error, detail, and mapping.
    # Compile does not currently populate category_errors: map_fractal_similarity
    # never sets source_type/target_type, so the detector's predicates never fire.
    # Inject a record in that exact shape, including a mapping dict.
    packet = compile_semantic_packet(
        "Magnetism explains the Moon's orbit because opposites attract."
    )
    assert packet.category_errors == []
    record = {
        "mapping": {
            "source": "opposites attract",
            "target": "Moon's orbit",
            "source_type": "symbolic",
            "target_type": "physical",
        },
        "error": "SYMBOLIC_TO_PHYSICAL_CATEGORY_ERROR",
        "detail": "Symbolic/metaphorical property applied as physical law.",
    }
    packet.category_errors.append(record)
    summary = summary_v1(packet)
    assert summary["category_errors"] == [
        {
            "error": "SYMBOLIC_TO_PHYSICAL_CATEGORY_ERROR",
            "detail": "Symbolic/metaphorical property applied as physical law.",
        }
    ]
    row = summary["category_errors"][0]
    assert row != {}
    assert row["error"] == "SYMBOLIC_TO_PHYSICAL_CATEGORY_ERROR"
    assert "mapping" not in row
    _assert_keys_absent(summary, _NEVER_IN_SUMMARY_RECORD_KEYS)
    row_blob = json.dumps(row, default=str)
    assert "opposites attract" not in row_blob
    assert "Moon's orbit" not in row_blob
    assert "source_type" not in row_blob

# Everyday mobile prompts from the 2026-11-25 Chief of Staff merge report
# (dogfood at 9ec2f81). Those runs returned NEEDS_REVISION with no target
# and "No target system resolved; interpretation would be forced." After
# Decision.PASS_THROUGH and router-first compile, the same no-target prompts
# exit PASS_THROUGH. This is the shape hosted callers see today.
_MERGE_REPORT_NO_TARGET_PROMPTS = (
    "Summarize my last 3 emails and draft a reply to the one from my landlord.",
    "Is my phone battery dying faster because of the new update?",
    "remind me to call mom at 6",
    "Explain why my code throws a null pointer when the list is empty",
)

# Prompt whose summary is fully stable (no routing_candidate scores to pin).
_STABLE_NO_TARGET_PROMPT = "remind me to call mom at 6"

_SUMMARY_V1_KEY_ORDER = (
    "schema",
    "compiler",
    "version",
    "decision",
    "status",
    "dataset_tier",
    "mode",
    "selected_target",
    "target_systems",
    "source_frames",
    "routing_candidates",
    "scores",
    "unknowns",
    "contradictions",
    "category_errors",
    "semantic_error_class",
    "semantic_error_confidence",
    "testimony_integrity",
    "risk_flags",
    "needs_review",
    "route_to",
    "next_questions",
    "compiler_warnings",
)

_NO_TARGET_NULL_KEYS = (
    "selected_target",
    "semantic_error_class",
    "semantic_error_confidence",
)

_NO_TARGET_EMPTY_KEYS = (
    "target_systems",
    "source_frames",
    "scores",
    "unknowns",
    "contradictions",
    "category_errors",
    "next_questions",
)


@pytest.mark.parametrize("text", _MERGE_REPORT_NO_TARGET_PROMPTS)
def test_summary_v1_everyday_no_target_decision_and_reasons(text: str) -> None:
    from semantic_compiler.core.pipeline import PASS_THROUGH_REASON, PASS_THROUGH_ROUTE

    summary = compile_json(text)
    assert list(summary) == list(_SUMMARY_V1_KEY_ORDER)
    for key in FORBIDDEN_DEFAULT_KEYS:
        assert key not in summary
    assert summary["decision"] == "PASS_THROUGH"
    assert summary["status"] == "pass_through"
    assert summary["dataset_tier"] == "BRONZE"
    assert summary["mode"] == "UNIVERSAL_DECOMPRESSION"
    assert summary["compiler_warnings"] == [PASS_THROUGH_REASON]
    assert summary["route_to"] == [PASS_THROUGH_ROUTE]
    assert summary["needs_review"] is False
    for key in _NO_TARGET_NULL_KEYS:
        assert summary[key] is None, key
    for key in _NO_TARGET_EMPTY_KEYS:
        assert summary[key] in ([], {}), key
    # Stage 3 no-target exit does not score the packet.
    assert summary["scores"] == {}
    assert text not in json.dumps(summary, default=str)


def test_summary_v1_no_target_exact_shape_for_stable_everyday_prompt() -> None:
    from semantic_compiler.core.packet import COMPILER_VERSION
    from semantic_compiler.core.pipeline import PASS_THROUGH_REASON, PASS_THROUGH_ROUTE

    summary = compile_json(_STABLE_NO_TARGET_PROMPT)
    assert summary == {
        "schema": SUMMARY_SCHEMA,
        "compiler": "Reflexion Semantic Compiler",
        "version": COMPILER_VERSION,
        "decision": "PASS_THROUGH",
        "status": "pass_through",
        "dataset_tier": "BRONZE",
        "mode": "UNIVERSAL_DECOMPRESSION",
        "selected_target": None,
        "target_systems": [],
        "source_frames": [],
        "routing_candidates": [],
        "scores": {},
        "unknowns": [],
        "contradictions": [],
        "category_errors": [],
        "semantic_error_class": None,
        "semantic_error_confidence": None,
        "testimony_integrity": {
            "is_testimony": False,
            "consistency": "STABLE",
            "isomorphism": "NARRATIVE",
            "corroboration": "UNANCHORED",
            "composite_classification": "STABLE + NARRATIVE + UNANCHORED",
        },
        "risk_flags": {
            "quarantine_required": False,
            "gate_status": "PASSED",
        },
        "needs_review": False,
        "route_to": [PASS_THROUGH_ROUTE],
        "next_questions": [],
        "compiler_warnings": [PASS_THROUGH_REASON],
    }
