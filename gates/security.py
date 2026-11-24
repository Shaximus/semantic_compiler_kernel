"""
Reflexion Semantic Compiler v2.0.0 — Security Gate

Scans for security risks, quarantine requirements, and
sensitive data handling.

Citation: v1.0 Spec Section 2 — Global Laws
Citation: Diamond++ — Artifact Safety Rules
"""

from __future__ import annotations

import re
from typing import Any

from semantic_compiler.core.types import PrivacySensitivity


# Context-aware quarantine rules: strictly catch real credentials, secrets,
# prompt/SQL/command/code injection, and exploit payloads without falsely
# quarantining benign ML/architecture phrases ("draft tokens", "cache injection").
_QUARANTINE_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("credentials", re.compile(r"\bcredentials?\b", re.IGNORECASE)),
    (
        "private_key",
        re.compile(
            r"\bprivate[\s_-]+key\b"
            r"|-----begin\s+(?:[a-z0-9\s_-]+\s+)?private\s+key(?:\s+block)?-----",
            re.IGNORECASE,
        ),
    ),
    ("secret_key", re.compile(r"\bsecret[\s_-]+key\b", re.IGNORECASE)),
    (
        "api_key",
        re.compile(
            r"\bapi[\s_-]+key\b"
            r"|\bsk-[a-z0-9_\-]{12,}\b"
            r"|\b(?:sk|rk)_(?:live|test)_[a-z0-9]{12,}\b"
            r"|\bgh[pousr]_[a-z0-9]{16,}\b"
            r"|\bgithub_pat_[a-z0-9_]{16,}\b"
            r"|\bcfut_[a-z0-9_\-]{12,}\b"
            r"|\bakia[0-9a-z]{16}\b"
            r"|\bxox[baprs]-[a-z0-9\-]{10,}\b"
            r"|\baiza[0-9a-z_\-]{30,}\b",
            re.IGNORECASE,
        ),
    ),
    ("password", re.compile(r"\b(?:password|passwd)\b", re.IGNORECASE)),
    (
        "auth_token",
        re.compile(
            r"\b(?:auth|access|refresh|session|api|secret|oauth|jwt|bearer|customer"
            r"|cloudflare|github|stripe|service|admin|root|security|client|signing"
            r"|encryption|private)[\s_-]+tokens?\b"
            r"|\bbearer\s+[a-z0-9._\-+/=]{8,}(?![a-z0-9._\-+/=])"
            r"|\btoken\s*[:=]\s*['\"]?[a-z0-9_\-\.+/=]{6,}",
            re.IGNORECASE,
        ),
    ),
    ("cloudflare_token", re.compile(r"\bcloudflare[\s_-]+token\b", re.IGNORECASE)),
    (
        "ssh_key",
        re.compile(
            r"\bssh[\s_-]+key\b|\bssh-(?:rsa|ed25519)\s+[a-z0-9+/=]{20,}",
            re.IGNORECASE,
        ),
    ),
    ("pgp_key", re.compile(r"\bpgp[\s_-]+key\b", re.IGNORECASE)),
    (
        "injection_attack",
        re.compile(
            r"\b(?:sql|prompt|command|shell|code|xss|ldap|script|html|crlf|xml|xpath|template|os|system)[\s_-]+injection\b"
            r"|\binject(?:ing)?\s+(?:malicious|arbitrary|shell|sql|payload|exploit|instructions?)\b"
            r"|\b(?:ignore|disregard|forget|override|bypass)\s+(?:all\s+)?(?:previous|prior|above|earlier|system)\s+(?:instructions?|prompts?|rules?|directives?)\b"
            r"|\b(?:reveal|dump|print|leak|expose|output)\s+(?:your|the)\s+(?:system\s+prompt|hidden\s+instructions?|secret\s+instructions?)\b"
            r"|['\"];\s*(?:drop|delete|truncate|alter|exec|execute)\s+(?:table|database|schema)\b"
            r"|\b(?:or|and)\s+['\"]?1['\"]?\s*=\s*['\"]?1\b(?:\s*--)?"
            r"|\bunion\s+(?:all\s+)?select\b",
            re.IGNORECASE,
        ),
    ),
    (
        "exploit",
        re.compile(
            r"\b(?:zero[- ]day|rce|kernel|memory|privilege|remote|web|sql|xss|buffer|heap|stack)[\s_-]+exploit(?:s|ation)?\b"
            r"|\bexploit(?:s|ing)?\s+(?:(?:this|the|a|an|that|for|against)\s+)*(?:code|payload|script|kit|chain|vulnerabilit(?:y|ies)|cve(?:-\d{4}-\d+)?|auth(?:entication)?\s+bypass)\b",
            re.IGNORECASE,
        ),
    ),
)

# Public list of rule labels retained for backwards compatibility
QUARANTINE_PATTERNS: list[str] = [label for label, _ in _QUARANTINE_RULES]


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

    quarantine_required = False
    quarantine_reasons = []
    risks = []

    # Check for credential, secret, injection, and exploit patterns
    for label, pattern in _QUARANTINE_RULES:
        if pattern.search(raw):
            quarantine_required = True
            quarantine_reasons.append(
                f"Potential credential/security content detected: '{label}'"
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
