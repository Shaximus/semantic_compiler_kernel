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
    assert "normalized_input" in summary
    default = summary_v1(packet)
    assert "raw_input" not in default
    via_compile = compile_json(text, include_raw_input=True)
    assert via_compile["raw_input"] == text


def test_compile_json_forward_text_only_when_opted_in() -> None:
    # Short fragment currently exits PASS_THROUGH and may set forward_text.
    text = (PROMPT_DIR / "01_short_fragment.txt").read_text(encoding="utf-8").strip()
    packet = compile_semantic_packet(text)
    default = summary_v1(packet)
    assert "forward_text" not in default
    assert "raw_input" not in default
    opted = summary_v1(packet, include_raw_input=True)
    assert opted["raw_input"] == text
    if packet.forward_text is not None:
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
