"""
Reflexion Semantic Compiler v2.0.0 — Security Gate

Scans for security risks, quarantine requirements, and
sensitive data handling.

Citation: v1.0 Spec Section 2 — Global Laws
Citation: Diamond++ — Artifact Safety Rules
"""

from __future__ import annotations

from typing import Any

from semantic_compiler.core.types import PrivacySensitivity


# Patterns that trigger quarantine
QUARANTINE_PATTERNS = [
    "credentials", "private_key", "secret_key", "api_key",
    "password", "token", "exploit", "injection",
    "cloudflare_token", "ssh_key", "pgp_key",
]


def scan_semantic_and_operational_risk(packet: Any) -> dict[str, Any]:
    """
    Scan a packet for security and operational risks.

    Checks for:
    - Credentials or secrets in content
    - Quarantine-worthy content
    - Privacy sensitivity violations
    - External training use restrictions

    Citation: Diamond++ — Artifact Safety Rules
    """
    if hasattr(packet, "raw_input"):
        raw = packet.raw_input or ""
        privacy = packet.privacy_sensitivity
    else:
        raw = packet.get("raw_input", "")
        privacy = packet.get("privacy_sensitivity", PrivacySensitivity.INTERNAL)

    raw_lower = raw.lower()
    quarantine_required = False
    quarantine_reasons = []
    risks = []

    # Check for credential patterns
    for pattern in QUARANTINE_PATTERNS:
        if pattern in raw_lower:
            quarantine_required = True
            quarantine_reasons.append(
                f"Potential credential/security content detected: '{pattern}'"
            )

    # Check privacy sensitivity
    if isinstance(privacy, str):
        try:
            privacy = PrivacySensitivity[privacy.upper()]
        except KeyError:
            privacy = PrivacySensitivity.INTERNAL

    if privacy == PrivacySensitivity.CRITICAL:
        risks.append({
            "type": "PRIVACY",
            "severity": "CRITICAL",
            "detail": "Content marked as critically sensitive. "
                     "External training use prohibited.",
        })

    return {
        "quarantine_required": quarantine_required,
        "quarantine_reasons": quarantine_reasons,
        "risks": risks,
        "privacy_sensitivity": privacy.name if hasattr(privacy, 'name') else str(privacy),
        "gate_status": "QUARANTINE" if quarantine_required else "PASSED",
    }
