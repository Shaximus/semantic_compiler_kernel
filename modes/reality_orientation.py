"""
Reflexion Semantic Compiler v2.0.0 — Regulated Reality Orientation Protocol

v2.0 ADDITION: First-class compiler mode for handling situations where
emotional flooding blocks physical-world constraint processing.

Extracted from Diamond+++ sample: DIAMOND_PLUS_KRISTYN_AVOIDANCE_RESOURCE_REALITY_001

The core insight:
    Pain explains the avoidance.
    It does not make the fuel tank less empty.

The method:
    When reality feels like pain, do not argue with the pain.
    Externalize the reality small enough that the system can touch it.

The protocol:
    1. Brief validation (remove shame)
    2. State the physical constraint neutrally
    3. Ask for one binary fact
    4. Reduce scope to one micro-packet
    5. Stop. Do not prosecute, moralize, or catastrophize.

Citation: Diamond++ — Regulated Reality Orientation Protocol
Citation: Diamond++ — Rules 1-7 from the Kristyn sample
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from semantic_compiler.core.types import CompilerMode


# ═══════════════════════════════════════════════════════════════════
# TRAUMA KEYWORD BLACKLIST (Context-Sensitive)
#
# After graphic trauma disclosure, avoid metaphorical idioms
# from the disclosed sensory domain.
#
# Citation: Diamond++ — Rule 6 (Trigger-Domain Idiom Ban)
# ═══════════════════════════════════════════════════════════════════

TRAUMA_DOMAINS: dict[str, list[str]] = {
    "blood_violence": [
        "stop the bleeding", "death spiral", "bulletproof",
        "pull the trigger", "blow up", "take a shot",
        "fire under you", "burning it down", "kill it",
        "cut it out", "slash and burn", "bloodbath",
        "murder", "slaughter", "execution",
    ],
    "drowning": [
        "drowning in", "underwater", "sinking ship",
        "treading water", "going under", "submerged",
    ],
    "fire": [
        "burning", "on fire", "scorched earth",
        "fire under you", "up in flames", "meltdown",
    ],
    "suffocation": [
        "suffocating", "can't breathe", "choking",
        "strangling", "smothered",
    ],
}

# Safe alternatives for common idioms
SAFE_ALTERNATIVES: dict[str, str] = {
    "stop the bleeding": "halt the dismantling",
    "death spiral": "resource drain loop",
    "pull the trigger": "execute the action",
    "blow up": "escalate suddenly",
    "fire under you": "urgency applied",
    "burning it down": "dismantling the system",
    "kill it": "terminate the process",
    "cut it out": "remove the behavior",
    "drowning in": "overwhelmed by",
    "on fire": "in crisis",
    "hostage situation": "survival load transfer",
}


@dataclass
class MicroPacket:
    """
    The smallest possible non-moral externalization of a physical constraint.

    This is the tool that bypasses avoidance firewalls.
    It works because it strips all emotional/survival metadata
    from the payload, leaving only dry mechanical facts.

    The defense mechanism scans for fear, shame, and pressure.
    If the packet looks like a system diagnostic, it slides past.
    """
    task: str = ""
    location_requirement: str = ""
    required_resource: str = ""
    available_resource: str = ""
    status: str = "UNKNOWN"  # EXECUTABLE | BLOCKED | UNKNOWN
    cause: str = ""
    next_true_sentence: str = ""
    lawful_action: str = ""


@dataclass
class RealityOrientationResult:
    """Result of applying the Regulated Reality Orientation Protocol."""
    physical_constraints: list[dict[str, Any]] = field(default_factory=list)
    micro_packets: list[MicroPacket] = field(default_factory=list)
    avoidance_patterns_detected: list[str] = field(default_factory=list)
    trauma_keywords_flagged: list[str] = field(default_factory=list)
    safe_alternatives: dict[str, str] = field(default_factory=dict)
    magical_thinking_detected: list[str] = field(default_factory=list)
    hidden_workspace_items: list[str] = field(default_factory=list)
    recommended_script: Optional[str] = None
    mode: CompilerMode = CompilerMode.REGULATED_REALITY_ORIENTATION


# ═══════════════════════════════════════════════════════════════════
# THE AVOIDANCE FIREWALL MAP
#
# system: personal_survival_response
# not_a_diagnosis: true
#
# failure_mode:
#   name: REALITY_AS_PAIN_AVOIDANCE_LOOP
#   mechanism:
#     - problem detected
#     - pain predicted
#     - hidden workspace substitutes magical plan
#     - physical constraint deleted
#     - action delayed
#     - resources degrade
#     - correction interpreted as attack
#
# core_contradiction:
#     - avoidance once reduced immediate pain
#     - avoidance now increases physical danger
#
# repair:
#     - externalize one physical constraint
#     - remove moral language
#     - send truthful logistics update
#     - build tiny repeatable packet
# ═══════════════════════════════════════════════════════════════════


def detect_avoidance_pattern(
    claims: list[dict[str, Any]],
    physical_constraints: list[str],
) -> list[str]:
    """
    Detect Reality-As-Pain avoidance patterns.

    An avoidance pattern exists when:
    1. A physical constraint is known
    2. A proposed solution ignores that constraint
    3. The solution relies on unexternalized/unverified planning
    4. The solution provides dopamine/distraction without addressing the blocker

    Citation: Diamond++ — Rule 4 (Coping Is Not Strategy)
    """
    patterns = []

    for claim in claims:
        content = claim.get("content", "").lower()
        claim_type = claim.get("claim_type", "")

        # Check for magical planning (solution without math)
        if claim_type in ("plan", "strategy", "solution"):
            has_math = claim.get("externalized_math", False)
            has_resource_check = claim.get("resource_verified", False)

            if not has_math and not has_resource_check:
                # Check if any physical constraint contradicts the plan
                for constraint in physical_constraints:
                    if any(
                        word in content
                        for word in constraint.lower().split()
                        if len(word) > 3
                    ):
                        patterns.append(
                            f"MAGICAL_PLANNING: '{content[:80]}...' "
                            f"ignores physical constraint: '{constraint}'. "
                            f"Label as coping unless resource math passes."
                        )

        # Check for distraction-as-strategy
        distraction_keywords = [
            "game", "play", "watch", "scroll", "browse",
            "later", "figure it out", "somehow", "maybe",
        ]
        if any(kw in content for kw in distraction_keywords):
            if physical_constraints:
                patterns.append(
                    f"COPING_AS_STRATEGY: Activity described may be "
                    f"soothing but does not address physical constraint. "
                    f"Coping ≠ planning."
                )

    return patterns


def check_trauma_keywords(
    text: str,
    disclosed_domains: list[str] | None = None,
) -> dict[str, Any]:
    """
    Check text for trauma-domain idioms that should be avoided.

    Citation: Diamond++ — Rule 6 (Trigger-Domain Idiom Ban)

    If a user has disclosed graphic trauma involving blood, weapons,
    death, violence, fire, drowning, etc., avoid metaphorical idioms
    from that same sensory domain.
    """
    text_lower = text.lower()
    flagged = []
    alternatives = {}

    domains_to_check = disclosed_domains or list(TRAUMA_DOMAINS.keys())

    for domain in domains_to_check:
        if domain not in TRAUMA_DOMAINS:
            continue
        for phrase in TRAUMA_DOMAINS[domain]:
            if phrase in text_lower:
                flagged.append({
                    "phrase": phrase,
                    "domain": domain,
                    "severity": "HIGH",
                    "rule": "TRIGGER_DOMAIN_IDIOM_BAN",
                })
                if phrase in SAFE_ALTERNATIVES:
                    alternatives[phrase] = SAFE_ALTERNATIVES[phrase]

    return {
        "flagged_phrases": flagged,
        "safe_alternatives": alternatives,
        "has_violations": len(flagged) > 0,
    }


def build_micro_packet(
    task: str,
    required_resource: str,
    available_resource: str,
    location: str = "",
) -> MicroPacket:
    """
    Build the smallest possible non-moral externalization of a blocker.

    This is the tool that bypasses the avoidance firewall:
    - No childhood analysis
    - No smoking lecture
    - No 30-day forecast
    - No dismantling cascade
    - Just: is this executable? Yes or no.

    Citation: Diamond++ — The Actual Operational Fix
    """
    # Determine status
    if not available_resource or available_resource.lower() in (
        "none", "insufficient", "zero", "empty", "unavailable"
    ):
        status = "BLOCKED"
        cause = f"Required: {required_resource}. Available: {available_resource}."
    else:
        status = "EXECUTABLE"
        cause = ""

    return MicroPacket(
        task=task,
        location_requirement=location,
        required_resource=required_resource,
        available_resource=available_resource,
        status=status,
        cause=cause,
        next_true_sentence=(
            f"We do not have enough {required_resource} for {task}."
            if status == "BLOCKED"
            else f"{task} is executable with available {required_resource}."
        ),
        lawful_action=(
            f"Notify stakeholder of blocker and request alternative solution."
            if status == "BLOCKED"
            else f"Proceed with {task}."
        ),
    )


def apply_reality_orientation(packet: Any) -> dict[str, Any]:
    """
    Apply the Regulated Reality Orientation Protocol to a packet.

    This mode activates when:
    - Someone is emotionally flooded or avoidant
    - A physical-world constraint must still be handled
    - Delay threatens household/operational survival

    The Seven Rules:
    1. Reality Orientation Without Threat Amplification
    2. Externalize the Hidden Workspace
    3. One Constraint Before One Life Story
    4. Coping Is Not Strategy
    5. Partner Anchor, Not Partner Prosecutor
    6. Trigger-Domain Idiom Ban
    7. Shame Removal, Responsibility Preservation

    Citation: Diamond++ — New Rules Generated
    """
    if hasattr(packet, "declared_constraints"):
        constraints = packet.declared_constraints
        raw_input = packet.raw_input or ""
        claims = packet.claim_types
    else:
        constraints = packet.get("declared_constraints", [])
        raw_input = packet.get("raw_input", "")
        claims = packet.get("claim_types", [])

    result: dict[str, Any] = {
        "mode": CompilerMode.REGULATED_REALITY_ORIENTATION.name,
        "protocol_active": True,
    }

    # Step 1: Detect avoidance patterns
    avoidance = detect_avoidance_pattern(claims, constraints)
    result["avoidance_patterns"] = avoidance

    # Step 2: Check for trauma keywords
    keyword_check = check_trauma_keywords(raw_input)
    result["trauma_keyword_check"] = keyword_check

    # Step 3: Build micro-packets for each constraint
    micro_packets = []
    for constraint in constraints:
        mp = build_micro_packet(
            task="constraint_resolution",
            required_resource=constraint,
            available_resource="",  # caller must supply
        )
        micro_packets.append({
            "task": mp.task,
            "required": mp.required_resource,
            "available": mp.available_resource,
            "status": mp.status,
            "cause": mp.cause,
            "next_true_sentence": mp.next_true_sentence,
            "lawful_action": mp.lawful_action,
        })
    result["micro_packets"] = micro_packets

    # Step 4: Core law
    result["core_law"] = (
        "Pain explains the avoidance. "
        "It does not make the fuel tank less empty."
    )

    # Step 5: Protocol rules
    result["protocol_rules"] = {
        "rule_1": "Reality Orientation Without Threat Amplification",
        "rule_2": "Externalize the Hidden Workspace",
        "rule_3": "One Constraint Before One Life Story",
        "rule_4": "Coping Is Not Strategy",
        "rule_5": "Partner Anchor, Not Partner Prosecutor",
        "rule_6": "Trigger-Domain Idiom Ban",
        "rule_7": "Shame Removal, Responsibility Preservation",
    }

    return result
