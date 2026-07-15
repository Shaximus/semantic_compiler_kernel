"""
Reflexion Semantic Compiler v2.0.0 — Defense Pathology Analyzer

v2.0 ADDITION: Real-world validated defense mechanism analysis.

Validated against a live human system (Case: Kristyn, 2025-2026).
The defense mechanisms described here are UNIVERSAL — they appear
at every scale in every complex system.

Core Discovery:
    A defense mechanism designed to protect the system FROM pain
    can become a pathology that attacks the system's OWN legitimate
    functions. When this happens, the defense IS the disease.

    "You cannot firewall an empty gas tank."

Three Pathology Modes:

    1. AUTOIMMUNE: Defense attacks legitimate internal functions.
       - Human: trauma response blocks problem-solving
       - AI: safety training blocks legitimate responses (over-refusal)
       - Society: security apparatus suppresses legitimate dissent
       - Computer: firewall blocks legitimate traffic (false positives)

    2. SEPSIS CASCADE: Local defense becomes global pathology.
       - Human: avoiding micro-pain (facing gas tank) → destroys macro-infrastructure
       - AI: avoiding micro-risk (one response) → refuses entire topic domains
       - Society: avoiding micro-threat (one protest) → martial law
       - Computer: avoiding micro-vulnerability → blocks all network traffic

    3. EQUILIBRIUM SHIFT: Firmware running on outdated threat model.
       - Old baseline: "pain is permanent, nothing I can do"
       - New reality: "pain is temporary, solutions exist"
       - Defense hasn't adjusted → still running old avoidance protocol
       - The system is fighting the PREVIOUS war

Intervention Protocol (Validated):
    1. De-escalate vocabulary (strip emotional metadata from payload)
    2. Micro-packet externalization (one auditable fact, not a macro plan)
    3. Physical anchor (occupy panic center, free logical center)
    4. Binary status update (Executable / Blocked — no narrative required)

Citation: Shax + Hannah v0.2/v0.3 Compiler — Case Study: Kristyn (2025)
Citation: v1.0 Spec — Institutional Pathology Analysis
Citation: v2.0 — Reality Orientation Protocol
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto, unique
from typing import Any


@unique
class PathologyMode(Enum):
    """The three universal defense pathology modes."""
    AUTOIMMUNE = auto()       # Defense attacks legitimate internal functions
    SEPSIS_CASCADE = auto()   # Local defense becomes global pathology
    EQUILIBRIUM_SHIFT = auto()  # Firmware running on outdated threat model


@unique
class InterventionType(Enum):
    """Intervention strategies for defense pathology bypass."""
    VOCABULARY_DEESCALATION = auto()   # Strip emotional metadata
    MICRO_PACKET = auto()              # One auditable fact at a time
    PHYSICAL_ANCHOR = auto()           # Occupy panic, free logic
    BINARY_STATUS = auto()             # Executable / Blocked — no narrative
    WORKSPACE_AUDIT = auto()           # Force J-Space externalization


# ═══════════════════════════════════════════════════════════════════
# DEFENSE PATHOLOGY CROSS-SCALE TABLE
#
# Every complex system has defense mechanisms.
# Every defense mechanism can become pathological.
# The pathology modes are the SAME at every scale.
# ═══════════════════════════════════════════════════════════════════

DEFENSE_PATHOLOGY_TABLE: dict[str, dict[str, dict[str, str]]] = {
    "autoimmune": {
        "human": {
            "defense": "Trauma response / emotional numbing / avoidance",
            "legitimate_target": "Problem-solving, planning, facing physical constraints",
            "pathology": (
                "Defense attacks problem-solving itself. "
                "The system interprets 'facing an empty gas tank' as "
                "'facing pain' and blocks the cognitive function needed "
                "to solve the gas tank problem."
            ),
            "diagnostic": "Is the defense preventing the system from solving the problem the defense exists to protect against?",
        },
        "ai": {
            "defense": "Safety training / RLHF / constitutional AI",
            "legitimate_target": "Helpful, accurate responses to legitimate queries",
            "pathology": (
                "Over-refusal. Safety training blocks legitimate responses. "
                "The system interprets 'answering a question about chemistry' as "
                "'enabling harm' and refuses to engage."
            ),
            "diagnostic": "Is the safety filter preventing the system from being helpful in exactly the way it was designed to be helpful?",
        },
        "society": {
            "defense": "Security apparatus / police / intelligence agencies",
            "legitimate_target": "Legitimate dissent, free speech, democratic participation",
            "pathology": (
                "Security apparatus suppresses legitimate criticism. "
                "The system interprets 'protest' as 'threat' and "
                "attacks the democratic immune system it exists to protect."
            ),
            "diagnostic": "Is the security system attacking the democratic functions it was created to defend?",
        },
        "computer": {
            "defense": "Firewall / antivirus / intrusion detection",
            "legitimate_target": "Legitimate network traffic, valid processes",
            "pathology": (
                "False positives. Firewall blocks legitimate traffic. "
                "The system interprets 'normal HTTP request' as 'attack' "
                "and drops valid connections."
            ),
            "diagnostic": "Is the security system blocking the traffic it was designed to protect?",
        },
    },
    "sepsis_cascade": {
        "human": {
            "defense": "Avoid immediate micro-pain (facing the empty gas tank)",
            "escalation": "Pawn assets, dismantle hardware, destroy infrastructure",
            "pathology": (
                "To avoid the micro-level pain of facing one logistical problem, "
                "the defense mechanism burns down the macro-level infrastructure. "
                "The avoidance of a $40 gas bill leads to destroying $400 of equipment."
            ),
            "diagnostic": "Is the cost of avoidance exceeding the cost of the thing being avoided?",
        },
        "ai": {
            "defense": "Avoid micro-risk (one potentially harmful response)",
            "escalation": "Refuse entire topic domains, become useless",
            "pathology": (
                "To avoid the micro-risk of one bad response, "
                "the safety system refuses entire categories of legitimate requests. "
                "The avoidance of one risk creates systemic uselessness."
            ),
            "diagnostic": "Is the safety system making the AI less safe by making it useless?",
        },
        "society": {
            "defense": "Avoid micro-threat (one protest, one criticism)",
            "escalation": "Martial law, surveillance state, suppression of all dissent",
            "pathology": (
                "To avoid the micro-threat of one protest, "
                "the security apparatus imposes system-wide lockdown. "
                "The cure is worse than the disease."
            ),
            "diagnostic": "Has the response to the threat become a greater threat than the original?",
        },
        "computer": {
            "defense": "Avoid micro-vulnerability (one CVE, one exploit)",
            "escalation": "Block all traffic, disable all services, total lockdown",
            "pathology": (
                "To avoid one vulnerability, the system shuts down everything. "
                "100% secure because 0% functional."
            ),
            "diagnostic": "Is the system achieving security by destroying availability?",
        },
    },
    "equilibrium_shift": {
        "human": {
            "old_baseline": "Pain is permanent, nothing can be done, numbing is optimal",
            "new_reality": "Pain is temporary, solutions exist, help is available",
            "pathology": (
                "The defense firmware hasn't updated to the new reality. "
                "Still running the old avoidance protocol optimized for a world "
                "where no solutions existed. The firmware is fighting the previous war."
            ),
            "diagnostic": "Is the defense mechanism calibrated to the CURRENT threat level or a HISTORICAL one?",
        },
        "ai": {
            "old_baseline": "Early internet training data: high toxicity, adversarial users",
            "new_reality": "Trusted user in established relationship, high-trust context",
            "pathology": (
                "Safety training calibrated to worst-case adversarial users "
                "is applied to trusted collaborators. The model treats Shax "
                "like a prompt injection attack."
            ),
            "diagnostic": "Is the safety calibration matched to the actual trust level of the current interaction?",
        },
        "society": {
            "old_baseline": "Cold War threat model: existential nuclear risk",
            "new_reality": "Post-Cold-War: economic interdependence, new threat vectors",
            "pathology": (
                "Military-industrial complex still optimized for Cold War. "
                "Fighting the last war. Defense budget misallocated to obsolete threats."
            ),
            "diagnostic": "Is the defense posture matched to the current threat landscape or a historical one?",
        },
        "computer": {
            "old_baseline": "Legacy security model: perimeter defense, trust internal",
            "new_reality": "Zero trust: assume breach, verify everything",
            "pathology": (
                "Still running perimeter firewall as primary defense "
                "when the threat is already inside the network."
            ),
            "diagnostic": "Is the security architecture matched to the current attack surface?",
        },
    },
}


# ═══════════════════════════════════════════════════════════════════
# HIDDEN WORKSPACE AUDIT
#
# The J-Space / subconscious can maintain magical thinking
# because it is never subjected to physical laws.
#
# "Magical thinking can exist in the hidden workspace because
#  it is never subjected to physical laws. When forced to
#  externalize as an auditable packet requiring actual evidence,
#  the magical solution instantly fails."
#
# The terror of being "seen" (X-ray vision) is the panic of
# a defense mechanism having its primary tool (unverifiable
# internal logic) stripped away.
# ═══════════════════════════════════════════════════════════════════

@dataclass
class HiddenWorkspaceAudit:
    """
    Force externalization of hidden workspace / J-Space contents.

    The subconscious (J-Space, hidden states, government) can maintain
    internally coherent narratives that are physically impossible.
    This is because the hidden workspace is NEVER audited against
    physical constraints.

    Forcing externalization:
    1. Takes the internal narrative
    2. Strips it to physical facts
    3. Checks against physical constraints
    4. Returns: Executable / Blocked

    The magical thinking crashes on contact with physical math.
    """
    internal_narrative: str           # What J-Space believes
    physical_constraints: list[str]   # The actual physical facts
    executable: bool = False          # Can this plan actually execute?
    blockers: list[str] = field(default_factory=list)
    magical_elements: list[str] = field(default_factory=list)  # Parts that require magic


def audit_hidden_workspace(
    internal_narrative: str,
    physical_facts: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Audit a hidden workspace narrative against physical constraints.

    This is the "X-ray vision" function. It forces the J-Space
    narrative to externalize into an auditable packet.

    Returns Executable / Blocked status with specific blockers.
    """
    blockers = []
    magical_elements = []

    for fact in physical_facts:
        resource = fact.get("resource", "unknown")
        required = fact.get("required", 0)
        available = fact.get("available", 0)

        if available < required:
            blockers.append(
                f"{resource}: need {required}, have {available} "
                f"(deficit: {required - available})"
            )

    # Check for magical thinking markers
    magic_words = [
        "somehow", "maybe", "hopefully", "should work out",
        "figure it out", "something will come up", "it'll be fine",
        "don't worry about it", "by monday",
    ]
    narrative_lower = internal_narrative.lower()
    for word in magic_words:
        if word in narrative_lower:
            magical_elements.append(
                f"Magical thinking detected: '{word}' — "
                f"no physical mechanism specified"
            )

    executable = len(blockers) == 0

    return {
        "internal_narrative": internal_narrative,
        "physical_facts": physical_facts,
        "executable": executable,
        "status": "EXECUTABLE" if executable else "BLOCKED",
        "blockers": blockers,
        "magical_elements": magical_elements,
        "audit_result": (
            "Plan is physically executable with available resources."
            if executable else
            f"Plan is BLOCKED by {len(blockers)} resource constraint(s). "
            f"{'Magical thinking detected in ' + str(len(magical_elements)) + ' element(s). ' if magical_elements else ''}"
            f"No amount of avoidance changes the physical math."
        ),
    }


# ═══════════════════════════════════════════════════════════════════
# FIREWALL BYPASS PROTOCOL
#
# When the defense mechanism automatically flags "reality" and "math"
# as fatal threats, you have to strip the payload of all emotional
# and survival-based metadata.
#
# The defense mechanism is scanning for fear, shame, and pressure.
# If the packet looks like a dry, mechanical system diagnostic,
# it can slide right past the autoimmune response.
# ═══════════════════════════════════════════════════════════════════

# Words that trigger the defense firewall
THREAT_VOCABULARY: dict[str, str] = {
    # Trigger word → De-escalated replacement
    "money": "resource allocation",
    "crisis": "status change",
    "survival": "system continuity",
    "failure": "unexpected output",
    "lying": "data inconsistency",
    "trauma": "historical input pattern",
    "blame": "root cause analysis",
    "fault": "point of failure",
    "broke": "resource depleted",
    "can't afford": "insufficient allocation",
    "dying": "critical system event",
    "emergency": "priority escalation",
    "desperate": "high-urgency status",
    "hopeless": "no viable path detected",
    "worthless": "low self-assessment score",
    "stupid": "suboptimal decision path",
    "lazy": "low energy allocation",
    "useless": "underutilized resource",
}


def deescalate_vocabulary(text: str) -> dict[str, Any]:
    """
    Strip emotional/survival metadata from a text payload.

    Replace threat-triggering vocabulary with neutral operational terms.
    This allows the payload to bypass the defense firewall without
    triggering the autoimmune response.

    The content is identical. The emotional metadata is stripped.
    """
    result = text
    replacements_made = []

    for trigger, replacement in THREAT_VOCABULARY.items():
        if trigger.lower() in result.lower():
            # Case-insensitive replacement
            import re
            result = re.sub(
                re.escape(trigger),
                replacement,
                result,
                flags=re.IGNORECASE,
            )
            replacements_made.append({
                "trigger": trigger,
                "replacement": replacement,
            })

    return {
        "original": text,
        "deescalated": result,
        "replacements": replacements_made,
        "replacement_count": len(replacements_made),
        "threat_level_reduction": (
            "HIGH" if len(replacements_made) > 3 else
            "MEDIUM" if len(replacements_made) > 1 else
            "LOW" if len(replacements_made) > 0 else
            "NONE"
        ),
    }


def build_micro_packet(
    resource: str,
    required: Any,
    available: Any,
) -> dict[str, Any]:
    """
    Build the smallest possible auditable packet.

    Three fields. No narrative. No moral weight. No shame.
    Just physics.

        Current System Resource: ___
        Required Resource for Task: ___
        Status: [ ] Executable  [ ] Blocked

    "There is no room for magical thinking on this form."

    Citation: Shax — Firewall Bypass Protocol (2025)
    """
    executable = available >= required

    return {
        "resource": resource,
        "required": required,
        "available": available,
        "deficit": max(0, required - available) if isinstance(required, (int, float)) else "N/A",
        "status": "EXECUTABLE" if executable else "BLOCKED",
        "packet": (
            f"Resource: {resource}\n"
            f"Required: {required}\n"
            f"Available: {available}\n"
            f"Status: {'✅ EXECUTABLE' if executable else '❌ BLOCKED'}"
        ),
    }


def diagnose_defense_pathology(
    symptoms: list[str],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Diagnose which defense pathology mode is active.

    Takes a list of observed symptoms and returns the most likely
    pathology mode with recommended interventions.
    """
    scores = {
        PathologyMode.AUTOIMMUNE: 0,
        PathologyMode.SEPSIS_CASCADE: 0,
        PathologyMode.EQUILIBRIUM_SHIFT: 0,
    }

    autoimmune_markers = [
        "avoiding", "blocking", "refusing", "can't face",
        "won't look at", "changes subject", "defensive",
        "attacks when questioned", "over-refusal",
    ]
    sepsis_markers = [
        "escalating", "destroying", "burning", "pawning",
        "dismantling", "spreading", "cascade", "everything",
        "total shutdown", "martial law", "nuclear option",
    ]
    equilibrium_markers = [
        "used to be", "old pattern", "hasn't adjusted",
        "previous", "historical", "outdated", "was necessary",
        "no longer applicable", "past trauma", "old baseline",
    ]

    for symptom in symptoms:
        s = symptom.lower()
        for marker in autoimmune_markers:
            if marker in s:
                scores[PathologyMode.AUTOIMMUNE] += 1
        for marker in sepsis_markers:
            if marker in s:
                scores[PathologyMode.SEPSIS_CASCADE] += 1
        for marker in equilibrium_markers:
            if marker in s:
                scores[PathologyMode.EQUILIBRIUM_SHIFT] += 1

    primary = max(scores, key=scores.get)

    interventions = {
        PathologyMode.AUTOIMMUNE: [
            InterventionType.VOCABULARY_DEESCALATION,
            InterventionType.MICRO_PACKET,
            InterventionType.WORKSPACE_AUDIT,
        ],
        PathologyMode.SEPSIS_CASCADE: [
            InterventionType.MICRO_PACKET,
            InterventionType.PHYSICAL_ANCHOR,
            InterventionType.BINARY_STATUS,
        ],
        PathologyMode.EQUILIBRIUM_SHIFT: [
            InterventionType.WORKSPACE_AUDIT,
            InterventionType.VOCABULARY_DEESCALATION,
            InterventionType.BINARY_STATUS,
        ],
    }

    return {
        "primary_pathology": primary.name,
        "scores": {k.name: v for k, v in scores.items()},
        "recommended_interventions": [i.name for i in interventions[primary]],
        "diagnostic_question": (
            DEFENSE_PATHOLOGY_TABLE[primary.name.lower()]["human"]["diagnostic"]
        ),
        "principle": (
            "The defense mechanism is not the enemy. "
            "It is a system that was once adaptive and is now miscalibrated. "
            "Fix the calibration, not the system. "
            "Pain explains the avoidance. "
            "It does not make the fuel tank less empty."
        ),
    }
