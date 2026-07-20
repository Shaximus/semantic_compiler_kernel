"""Resolve Path of Exile buildcraft shorthand into typed compute mappings."""

from __future__ import annotations

import re

from semantic_compiler.registry.buildcraft import BUILDCRAFT_MAPPINGS, BuildcraftMapping


def _normalize(text: str) -> str:
    normalized = text.casefold().replace("’", "'").replace("–", "-").replace("—", "-")
    normalized = re.sub(r"[^a-z0-9+./' -]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _trigger_matches(text: str, trigger: str) -> bool:
    normalized_trigger = _normalize(trigger)
    return bool(normalized_trigger and normalized_trigger in text)


def resolve_buildcraft_entries(text: str) -> list[BuildcraftMapping]:
    """Return every explicitly or densely implied buildcraft mapping."""
    normalized = _normalize(text)
    if not normalized:
        return []

    by_id = {mapping.mapping_id: mapping for mapping in BUILDCRAFT_MAPPINGS}
    matches: list[BuildcraftMapping] = []
    seen: set[str] = set()

    def add(mapping_id: str) -> None:
        if mapping_id not in seen:
            matches.append(by_id[mapping_id])
            seen.add(mapping_id)

    for mapping in BUILDCRAFT_MAPPINGS:
        if any(_trigger_matches(normalized, trigger) for trigger in mapping.triggers):
            add(mapping.mapping_id)

    # Recover the hierarchy from compressed founder shorthand.
    if "pcie" in normalized:
        add("BUILD_002")
    if "gpu" in normalized or "accelerator" in normalized:
        add("BUILD_004")
    if "cpu socket" in normalized or "cpu slot" in normalized:
        add("BUILD_003")
    if "cpu" in normalized and any(word in normalized for word in ("armor", "armour", "body")):
        add("BUILD_005")
    if "vram" in normalized and any(word in normalized for word in ("mana", "reserve", "allocation")):
        add("BUILD_010")
    if "llm" in normalized or "model" in normalized:
        if "gem" in normalized or "skill" in normalized:
            add("BUILD_007")
    if any(word in normalized for word in ("cuda", "pytorch", "pypi", "driver", "abi")):
        add("BUILD_009")
    if any(word in normalized for word in ("repo", "repository", "package")):
        add("BUILD_011")
    if "rtx pro 6000" in normalized or ("blackwell" in normalized and "96 gb" in normalized):
        add("BUILD_014")

    # A dense statement spanning three or more layers should preserve the
    # complete slot -> item -> component -> reservation chain.
    hierarchy_signals = sum(
        signal in normalized
        for signal in ("pcie", "gpu", "cpu", "llm", "gem", "vram", "cuda", "pytorch")
    )
    if hierarchy_signals >= 3:
        if "pcie" in normalized:
            add("BUILD_002")
        if "gpu" in normalized:
            add("BUILD_004")
        if "cpu" in normalized:
            add("BUILD_005")
        if "llm" in normalized or "model" in normalized:
            add("BUILD_007")
        if "gem" in normalized or "mtp" in normalized or "drafter" in normalized:
            add("BUILD_008")
        if "vram" in normalized:
            add("BUILD_010")

    return matches


def resolve_buildcraft_mappings(text: str) -> list[dict[str, object]]:
    return [entry.to_fractal_mapping() for entry in resolve_buildcraft_entries(text)]


def summarize_buildcraft_ontology(text: str) -> dict[str, object]:
    entries = resolve_buildcraft_entries(text)
    return {
        "ontology": "BUILDCRAFT_COMPUTE_ONTOLOGY",
        "mapping_ids": [entry.mapping_id for entry in entries],
        "layers": [entry.layer for entry in entries],
        "canonical_chain": [
            "motherboard/chassis topology -> equipment paper doll",
            "PCIe accelerator slot -> weapon slot",
            "CPU socket/host position -> body-armour slot",
            "GPU/accelerator -> equipped weapon",
            "CPU package -> equipped body armour",
            "hardware integration capacity -> item sockets and links",
            "LLM/application -> active skill gem",
            "runtime/drafter/cache/framework -> support gem",
            "CUDA/PyTorch/drivers/ABI -> compatibility requirements",
            "VRAM occupancy -> mana reservation",
            "deployed architecture -> complete build",
        ],
        "global_guardrail": "Preserve relationship grammar without claiming material identity.",
    }
