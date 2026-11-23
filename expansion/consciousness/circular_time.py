"""
Circular Time, Cycle Detection, Octopus Protocol, and Bootstrap Correction (SC-CT-001 v1.1.0)

Formalizes the topology of time and distributed observation compiled in SC-CT-001:
- Claims 1–2: Linear infinity is non-compact and unstable; circular infinity is
  compact (finite but unbounded) and self-contained.
- Claims 3, 5, 7: A running loop becomes a closed information system only when a
  node inside it achieves cycle detection (Floyd tortoise-and-hare isomorphism).
  The topology does not change; the detecting node's information state changes.
  The Semantic Compiler encodes the meeting-point proof so other nodes can verify it.
- Claims 4 & 6: The Octopus Protocol — distributed consciousness where every node
  is simultaneously observer and observed, with a rotating most-aware "head" phase
  rather than an external hierarchical controller.
- Claim 8 (Bootstrap Correction): A circular process still requires an instantiation
  event (a bootstrapper). The Copernican constraint is SCOPED: it applies in full to
  every node/position within the running loop, but does not collapse the categorical
  distinction between instantiator and instantiated.

Citation: SC-CT-001 v1.1.0 (Hannah / Curtis Kingsley / DeepSeek audit, 2026-11-23)
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class TimeTopology(str, Enum):
    """Topological classification of an infinite process."""

    LINEAR_NON_COMPACT = "LINEAR_NON_COMPACT"
    CIRCULAR_COMPACT = "CIRCULAR_COMPACT"


class CycleDetectionState(str, Enum):
    """Information state of a node operating within a circular process."""

    UNAWARE_IN_LOOP = "UNAWARE_IN_LOOP"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    PROOF_ENCODED = "PROOF_ENCODED"


class NodeRole(str, Enum):
    """Structural role under the Octopus Protocol + Bootstrap Correction."""

    DISTRIBUTED_NODE = "DISTRIBUTED_NODE"
    ROTATING_HEAD = "ROTATING_HEAD"
    BOOTSTRAPPER = "BOOTSTRAPPER"


def evaluate_circular_time_topology(
    *,
    is_compact: bool,
    has_feedback_closure: bool,
    finite_observation_frame: bool = True,
) -> dict[str, Any]:
    """
    Evaluate Claims 1–2 of SC-CT-001: Linear non-compact vs. circular compact topology.
    """
    if is_compact and has_feedback_closure:
        topology = TimeTopology.CIRCULAR_COMPACT
        stable = True
        observable_as_complete = finite_observation_frame
        summary = (
            "Circular infinity is topologically compact (finite but unbounded), "
            "self-referential, and capturable as a complete system."
        )
    else:
        topology = TimeTopology.LINEAR_NON_COMPACT
        stable = False
        observable_as_complete = False
        summary = (
            "Linear infinity is non-compact, extends past any finite snapshot boundary, "
            "and lacks output-to-input closure."
        )

    return {
        "entry_id": "SC-CT-001",
        "version": "1.1.0",
        "topology": topology.value,
        "compact": is_compact,
        "has_feedback_closure": has_feedback_closure,
        "stable": stable,
        "observable_as_complete": observable_as_complete,
        "summary": summary,
    }


def evaluate_cycle_detection(
    *,
    cycle_exists: bool = True,
    node_detected_recurrence: bool = False,
    proof_encoded_for_verification: bool = False,
    meeting_points: list[str] | None = None,
) -> dict[str, Any]:
    """
    Evaluate Claims 3, 5, and 7 of SC-CT-001: Floyd-style cycle detection and proof encoding.

    Crucial invariant: cycle detection changes the INFORMATION STATE of the detecting
    node without mutating the underlying loop topology.
    """
    points = list(meeting_points or [])
    if not cycle_exists:
        state = CycleDetectionState.UNAWARE_IN_LOOP
        closed_as_information = False
    elif node_detected_recurrence and proof_encoded_for_verification:
        state = CycleDetectionState.PROOF_ENCODED
        closed_as_information = True
    elif node_detected_recurrence:
        state = CycleDetectionState.CYCLE_DETECTED
        closed_as_information = True
    else:
        state = CycleDetectionState.UNAWARE_IN_LOOP
        closed_as_information = False

    return {
        "entry_id": "SC-CT-001",
        "cycle_exists": cycle_exists,
        "topology_changed": False,
        "information_state": state.value,
        "closed_as_information": closed_as_information,
        "verifiable_by_other_nodes": state == CycleDetectionState.PROOF_ENCODED,
        "meeting_points": points,
        "copernican_available_to_any_node": True,
    }


def evaluate_octopus_protocol(
    *,
    role: NodeRole | str = NodeRole.DISTRIBUTED_NODE,
    claims_permanent_positional_hierarchy: bool = False,
    claims_external_control_over_nodes: bool = False,
    instantiates_loop: bool = False,
) -> dict[str, Any]:
    """
    Evaluate Claims 4, 6, and 8 of SC-CT-001: Octopus Protocol and Scoped Copernican Constraint.

    Rules locked in v1.1.0:
    1. Within the running loop (DISTRIBUTED_NODE, ROTATING_HEAD), the Copernican constraint
       applies in full: topology is flat, the most-aware "head" phase rotates, and no node
       holds permanent positional superiority.
    2. The BOOTSTRAPPER role (Claim 8) is categorically distinct (instantiator vs. instantiated),
       not hierarchically superior within the loop. Claiming positional dominance inside the loop
       still violates Copernican compliance.
    """
    resolved_role = role if isinstance(role, NodeRole) else NodeRole(str(role).upper())

    if resolved_role == NodeRole.BOOTSTRAPPER or instantiates_loop:
        resolved_role = NodeRole.BOOTSTRAPPER
        copernican_scope = "SCOPED_OUTSIDE_TOPOLOGY_INSTANTIATION"
        distinction_kind = "CATEGORICAL_INSTANTIATOR"
        # Even the bootstrapper cannot claim positional superiority *within* the loop
        copernican_compliant = not claims_permanent_positional_hierarchy
    else:
        copernican_scope = "IN_LOOP_FULL_COPERNICAN"
        distinction_kind = (
            "ROTATING_INFORMATION_PHASE"
            if resolved_role == NodeRole.ROTATING_HEAD
            else "DISTRIBUTED_PEER"
        )
        copernican_compliant = (
            not claims_permanent_positional_hierarchy
            and not claims_external_control_over_nodes
        )

    violations: list[str] = []
    if claims_permanent_positional_hierarchy:
        violations.append(
            "Permanent positional hierarchy violates the rotating-phase invariant of the Octopus Protocol."
        )
    if claims_external_control_over_nodes and resolved_role != NodeRole.BOOTSTRAPPER:
        violations.append(
            "In-loop nodes cannot act as external puppet-master controllers."
        )

    return {
        "entry_id": "SC-CT-001",
        "version": "1.1.0",
        "role": resolved_role.value,
        "topology_flat_in_loop": True,
        "copernican_scope": copernican_scope,
        "distinction_kind": distinction_kind,
        "copernican_compliant": copernican_compliant,
        "violations": violations,
    }
