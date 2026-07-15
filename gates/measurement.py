"""
Reflexion Semantic Compiler v2.0.0 — Measurement Layer Integrity Gate

Hard gate: modified sensors, wrappers, proxies, logs, or reporting paths
reduce telemetry to an unverified claim.

Observed output and external confirmation outrank internal status claims.

Canonical translations:
    reported power      != physical power
    reported clock      != effective throughput
    process alive       != service healthy
    packet delivered    != delivery observed
    agent says complete != artifact and test evidence exist
    GDP rising          != population economically secure
    nvidia-smi says 5%  != GPU actually idle (fan at 60% is ground truth)

Citation: v1.0 Spec Section 11 — Measurement-Layer Integrity
Global Law: measurement_layer_integrity
Global Law: output_over_self_report
"""

from __future__ import annotations

from typing import Any


def evaluate_measurement_path(path: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate a single measurement path for integrity.

    A measurement path is the chain from the thing being measured
    to the observer. If any link in that chain has been modified,
    the measurement is degraded.
    """
    modified = path.get("modified", False)
    integrity = path.get("integrity", "unknown")
    has_external_confirmation = path.get("external_confirmation", False)
    has_reproduction = path.get("reproducible_test", False)

    if modified:
        return {
            "path": path,
            "status": "DEGRADED",
            "gate_passed": False,
            "required_confirmation": (
                "External measurement or observed workload output. "
                "Internal telemetry with modified measurement path "
                "cannot be trusted."
            ),
            "can_recover": has_external_confirmation,
        }
    elif integrity == "unknown":
        return {
            "path": path,
            "status": "UNVERIFIED",
            "gate_passed": False,
            "required_confirmation": "Controlled reproducible test",
            "can_recover": has_reproduction,
        }
    elif integrity == "intact" or integrity == "verified":
        return {
            "path": path,
            "status": "INTACT",
            "gate_passed": True,
            "required_confirmation": None,
            "can_recover": True,
        }
    else:
        return {
            "path": path,
            "status": "UNKNOWN",
            "gate_passed": False,
            "required_confirmation": "Integrity state not recognized",
            "can_recover": False,
        }


def check_self_report_contradiction(
    self_report: dict[str, Any],
    external_observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Check whether self-reported status contradicts external observation.

    Global Law: output_over_self_report
    Observed output and external confirmation outrank internal status claims.

    This is the nvidia-smi vs fan-speed problem.
    This is the GPU-reports-5%-but-fan-at-60% problem.
    This is the agent-says-complete-but-no-artifact-exists problem.
    """
    contradictions = []

    for obs in external_observations:
        claim_field = obs.get("contradicts_claim", "")
        obs_value = obs.get("observed_value")
        reported_value = self_report.get(claim_field)

        if reported_value is not None and obs_value is not None:
            if str(reported_value) != str(obs_value):
                contradictions.append({
                    "claim": claim_field,
                    "self_reported": reported_value,
                    "externally_observed": obs_value,
                    "external_source": obs.get("source", "unknown"),
                    "ruling": "EXTERNAL_OBSERVATION_PREVAILS",
                    "law": "output_over_self_report",
                })

    return {
        "contradictions": contradictions,
        "self_report_reliable": len(contradictions) == 0,
        "gate_passed": len(contradictions) == 0,
    }


def evaluate_measurement_paths(packet: Any) -> dict[str, Any]:
    """
    Master measurement integrity gate.

    Extracts all measurement paths from the packet and evaluates
    each one for integrity.

    Citation: v1.0 Spec Section 8, step 5
    """
    if hasattr(packet, "evidence_inventory"):
        evidence = packet.evidence_inventory
    else:
        evidence = packet.get("evidence_inventory", [])

    # Extract measurement paths from evidence
    measurement_paths = [
        e for e in evidence
        if e.get("source_type") == "measurement"
        or e.get("is_measurement_path", False)
    ]

    # Also check context-declared modifications
    context_modified = False
    if hasattr(packet, "measurement_integrity"):
        ctx = packet.measurement_integrity
    else:
        ctx = packet.get("measurement_integrity", {})
    if ctx.get("context_declared_modified"):
        context_modified = True

    findings = []
    any_degraded = False

    for path in measurement_paths:
        finding = evaluate_measurement_path(path)
        findings.append(finding)
        if not finding["gate_passed"]:
            any_degraded = True

    # If context declared modification, the whole measurement layer is suspect
    if context_modified:
        any_degraded = True
        findings.append({
            "path": {"source": "context_declaration"},
            "status": "DEGRADED",
            "gate_passed": False,
            "required_confirmation": (
                "Context explicitly declared measurement path modified. "
                "All internal telemetry from this source is unverified."
            ),
            "can_recover": False,
        })

    return {
        "paths": findings,
        "any_degraded": any_degraded,
        "gate_status": "FAILED" if any_degraded else "PASSED",
        "decisive_rule": (
            "Internal telemetry is degraded; "
            "external measurement outranks the report."
            if any_degraded else "Measurement paths intact."
        ),
    }
