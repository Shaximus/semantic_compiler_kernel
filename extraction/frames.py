"""
Reflexion Semantic Compiler v2.0.0 — Source/Target Frame Detection

Citation: v1.0 Spec Section 8 — Master Pipeline, steps 3.2-3.4
"""

from __future__ import annotations

from typing import Any


# Known frames / domains for detection
KNOWN_FRAMES: dict[str, list[str]] = {
    "biology": [
        "organism", "cell", "immune", "nervous", "organ", "tissue",
        "metabolism", "DNA", "protein", "membrane", "disease",
        "kidney", "blood", "brain", "liver", "heart", "lung", "body",
        "oxygen", "circulatory", "antibody", "pathogen",
    ],
    "computation": [
        "CPU", "GPU", "RAM", "process", "thread", "memory", "disk",
        "network", "firewall", "server", "database", "API",
        "algorithm", "software", "hardware", "program", "queue", "cache",
    ],
    "organizational": [
        "department", "team", "employee", "manager", "CEO", "board",
        "budget", "HR", "policy", "meeting", "org chart",
        "company", "organization", "system", "process", "role", "function",
        "judicial", "court", "dispute", "supply chain",
    ],
    "national": [
        "government", "law", "policy", "citizen", "tax", "military",
        "police", "congress", "president", "constitution",
    ],
    "cosmological": [
        "universe", "galaxy", "star", "black hole", "dark matter",
        "quantum", "photon", "gravity", "spacetime", "cosmos",
        "hawking", "heliosphere", "radiation",
    ],
    "personal": [
        "trauma", "anxiety", "defense", "avoidance", "trigger",
        "nervous system", "fight or flight", "freeze", "grounding",
    ],
    "economic": [
        "UBI", "currency", "debt", "GDP", "market", "trade",
        "inflation", "supply", "demand", "labor",
    ],
    "reflexion": [
        "Goku", "Dragon", "Kestrel", "Logos", "Courier", "Hestia",
        "Whis", "Aegis", "Arbiter", "Kairo", "PentaCLI",
        "Hephaestus", "Bellwether", "Scribe", "Post Office",
    ],
}


def detect_source_frames(
    input_or_packet: Any,
    context_or_registry: Any = None,
) -> list[str]:
    """
    Detect which source domain frames are present in the input.
    Accepts either (raw_text, context) or (packet, registry).
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 3.2
    """
    if isinstance(input_or_packet, str):
        text = input_or_packet.lower()
        registry = None
    else:
        text = (input_or_packet.raw_input or "").lower()
        registry = context_or_registry
    detected: list[str] = []

    for frame_name, keywords in KNOWN_FRAMES.items():
        match_count = sum(1 for kw in keywords if kw.lower() in text)
        if match_count >= 2:  # At least 2 keywords to count as a frame
            detected.append(frame_name)
        elif match_count == 1:
            # Single match — add with lower confidence
            detected.append(f"{frame_name}?")

    # Check registry for additional matches
    if registry and hasattr(registry, "match_input"):
        raw = input_or_packet if isinstance(input_or_packet, str) else (input_or_packet.raw_input or "")
        term_matches = registry.match_input(raw)
        for match in term_matches:
            if match.domain and match.domain not in detected:
                detected.append(match.domain)

    return detected


def infer_target_systems(
    input_or_packet: Any,
    context_or_registry: Any = None,
) -> list[str]:
    """
    Infer what target systems the input could be translated to.
    Accepts either (raw_text, context) or (packet, registry).
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 3.3
    """
    if isinstance(input_or_packet, str):
        # When called with raw text, detect frames first
        source_frames = detect_source_frames(input_or_packet, context_or_registry)
    else:
        source_frames = input_or_packet.source_frames
    targets: list[str] = []

    # For each source frame, suggest natural target frames
    frame_targets: dict[str, list[str]] = {
        "biology": ["organizational", "computation", "national"],
        "computation": ["organizational", "biology", "cosmological"],
        "organizational": ["computation", "biology", "national"],
        "national": ["organizational", "biology", "computation"],
        "cosmological": ["computation", "biology", "organizational"],
        "personal": ["organizational", "computation"],
        "economic": ["organizational", "national"],
        "reflexion": ["organizational", "computation"],
    }

    for frame in source_frames:
        clean_frame = frame.rstrip("?")
        if clean_frame in frame_targets:
            for target in frame_targets[clean_frame]:
                if target not in targets and target != clean_frame:
                    targets.append(target)

    return targets


def generate_candidate_interpretations(
    packet: Any,
    registry: Any = None,
) -> list[dict[str, Any]]:
    """
    Generate candidate interpretations from source frames to target systems.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 3.4
    """
    candidates: list[dict[str, Any]] = []

    for target in packet.target_systems:
        candidates.append({
            "target_system": target,
            "source_frames": [f for f in packet.source_frames if not f.endswith("?")],
            "confidence": 0.5,
            "requires_scale_transform": True,
        })

    return candidates


def select_target_system(packet: Any) -> str | None:
    """
    Select the best target system from candidates.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 3.5
    """
    if packet.candidate_interpretations:
        # Sort by confidence and return highest
        sorted_candidates = sorted(
            packet.candidate_interpretations,
            key=lambda c: c.get("confidence", 0.0),
            reverse=True,
        )
        return sorted_candidates[0].get("target_system")
    return None
