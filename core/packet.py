"""
Reflexion Semantic Compiler v2.0.0 — Universal Semantic Packet

The canonical data structure that flows through the entire compilation pipeline.
Every field corresponds to a stage in the master pipeline (Section 8).

v2.0 extends the v1.0 packet with fractal_mappings, wave_function_coherence,
cosmological_anchors, reality_orientation state, and privacy sensitivity.

Citation: v1.0 Spec Section 6 — Universal Semantic Packet v1.0
Citation: v1.0 Spec Section 8 — Master Pipeline
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from semantic_compiler.core.types import (
    AuthorityType,
    CompilerMode,
    DatasetTier,
    Decision,
    PrivacySensitivity,
    WaveFunctionState,
)
from semantic_compiler.core.semantic_ir import SemanticIR


@dataclass
class SourceContext:
    """Provenance metadata for the raw input."""
    source_type: Optional[str] = None
    origin: Optional[str] = None
    trust_level: Optional[str] = None
    intended_audience: Optional[str] = None
    authority_level: str = "none"
    source_path: Optional[str] = None
    source_hash: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class SemanticPacket:
    """
    Universal Semantic Packet v2.0.

    This is the master data structure that flows through every stage of
    the compilation pipeline. It begins as a draft and progresses through
    extraction, translation, gate checks, scoring, and decision.

    Citation: v1.0 Spec Section 6 — Universal Semantic Packet
    """

    # --- Identity ---
    compiler: str = "Reflexion Semantic Compiler"
    version: str = "2.0.0"
    packet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mode: Optional[CompilerMode] = None
    active_submodes: list[CompilerMode] = field(default_factory=list)
    status: str = "draft"

    # --- Raw input ---
    raw_input: Optional[str] = None
    normalized_input: Optional[str] = None

    # --- Provenance ---
    source_context: SourceContext = field(default_factory=SourceContext)

    # --- Typing ---
    claim_types: list[dict[str, Any]] = field(default_factory=list)
    semantic_types: dict[str, Any] = field(default_factory=dict)

    # --- Semantic IR ---
    semantic_ir: SemanticIR = field(default_factory=SemanticIR)

    # --- Evidence layer (Section 5) ---
    evidence_inventory: list[dict[str, Any]] = field(default_factory=list)
    declared_constraints: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    generic_priors: list[str] = field(default_factory=list)
    evidence_updates: list[dict[str, Any]] = field(default_factory=list)
    rejected_assumptions: list[str] = field(default_factory=list)

    # --- Frame detection ---
    source_frames: list[str] = field(default_factory=list)
    target_systems: list[str] = field(default_factory=list)
    selected_target: Optional[str] = None
    candidate_interpretations: list[dict[str, Any]] = field(default_factory=list)

    # --- Structural translation ---
    registry_matches: list[dict[str, Any]] = field(default_factory=list)
    structural_skeleton: dict[str, Any] = field(default_factory=dict)

    noun_translation: list[dict[str, Any]] = field(default_factory=list)
    function_translation: list[dict[str, Any]] = field(default_factory=list)
    relationship_translation: list[dict[str, Any]] = field(default_factory=list)
    failure_mode_translation: list[dict[str, Any]] = field(default_factory=list)
    fractal_mappings: list[dict[str, Any]] = field(default_factory=list)

    # --- Hard gates ---
    causal_analysis: dict[str, Any] = field(default_factory=dict)
    macro_micro_checks: dict[str, Any] = field(default_factory=dict)
    scale_separation: dict[str, Any] = field(default_factory=dict)
    boundary_checks: dict[str, Any] = field(default_factory=dict)
    measurement_integrity: dict[str, Any] = field(default_factory=dict)

    # --- v2.0 gate additions ---
    wave_function_coherence: dict[str, Any] = field(default_factory=dict)
    cosmological_anchors: list[dict[str, Any]] = field(default_factory=list)

    # --- Adversarial reasoning ---
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    category_errors: list[dict[str, Any]] = field(default_factory=list)
    negative_isomorphism_tests: list[dict[str, Any]] = field(default_factory=list)

    hidden_variable_probe: dict[str, Any] = field(default_factory=dict)
    missing_organs: list[dict[str, Any]] = field(default_factory=list)
    residual_mismatches: list[str] = field(default_factory=list)
    policy_overrides: list[dict[str, Any]] = field(default_factory=list)

    # --- Governance ---
    risk_scan: dict[str, Any] = field(default_factory=dict)
    approval_scan: dict[str, Any] = field(default_factory=dict)
    routing_packet: dict[str, Any] = field(default_factory=dict)

    # --- v2.0: Reality Orientation ---
    reality_orientation: dict[str, Any] = field(default_factory=dict)
    trauma_keyword_blacklist: list[str] = field(default_factory=list)

    # --- Human-readable outputs ---
    literal_translation: Optional[str] = None
    public_translation: Optional[str] = None
    executive_translation: Optional[str] = None

    # --- Scoring and decision ---
    scores: dict[str, float] = field(default_factory=dict)
    decision: Optional[Decision] = None
    route_to: list[str] = field(default_factory=list)
    next_questions: list[str] = field(default_factory=list)

    # --- v2.1.3: Semantic error classification for decision routing ---
    semantic_error_class: Optional[str] = None
    semantic_error_confidence: Optional[float] = None

    # --- Dataset and audit ---
    dataset_row: dict[str, Any] = field(default_factory=dict)
    audit: dict[str, Any] = field(default_factory=dict)
    dataset_tier: Optional[DatasetTier] = None

    # --- v2.0.2: Qwen AgentWorld SFT output ---
    qwen_sft_output: dict[str, Any] = field(default_factory=dict)

    # --- v2.0: Privacy ---
    privacy_sensitivity: PrivacySensitivity = PrivacySensitivity.INTERNAL
    external_training_use: str = "forbidden"

    # --- Compilation metadata ---
    compilation_start: Optional[str] = None
    compilation_end: Optional[str] = None
    compiler_errors: list[str] = field(default_factory=list)
    compiler_warnings: list[str] = field(default_factory=list)

    def compute_input_hash(self) -> str:
        """Compute SHA-256 hash of the raw input for provenance."""
        if self.raw_input is None:
            return ""
        return hashlib.sha256(self.raw_input.encode("utf-8")).hexdigest()

    def mark_compilation_start(self) -> None:
        """Record compilation start timestamp."""
        self.compilation_start = datetime.now(timezone.utc).isoformat()
        self.status = "compiling"

    def mark_compilation_end(self) -> None:
        """Record compilation end timestamp."""
        self.compilation_end = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the entire packet to a dictionary."""
        import dataclasses
        result = dataclasses.asdict(self)
        # Convert enums to their names for serialization
        if self.mode:
            result["mode"] = self.mode.name
        if self.decision:
            result["decision"] = self.decision.name
        if self.dataset_tier:
            result["dataset_tier"] = self.dataset_tier.name
        result["privacy_sensitivity"] = self.privacy_sensitivity.name
        result["active_submodes"] = [m.name for m in self.active_submodes]
        return result

    def needs_revision(self, reason: str) -> SemanticPacket:
        """
        Mark packet as needing revision with a reason.
        This is the 'needs_revision' exit from the pipeline.
        """
        self.decision = Decision.NEEDS_REVISION
        self.status = "needs_revision"
        self.compiler_warnings.append(reason)
        self.next_questions.append(reason)
        return self


def initialize_packet(
    input_text: str,
    context: Optional[dict[str, Any]] = None,
    mode: str = "AUTO",
) -> SemanticPacket:
    """
    Initialize a new semantic packet from raw input.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 1
    """
    packet = SemanticPacket(
        raw_input=input_text,
        status="draft",
    )
    packet.mark_compilation_start()

    # Set source hash
    packet.source_context.source_hash = packet.compute_input_hash()
    packet.source_context.timestamp = datetime.now(timezone.utc).isoformat()

    # Apply context if provided
    if context:
        if "source_type" in context:
            packet.source_context.source_type = context["source_type"]
        if "origin" in context:
            packet.source_context.origin = context["origin"]
        if "trust_level" in context:
            packet.source_context.trust_level = context["trust_level"]
        if "authority_level" in context:
            packet.source_context.authority_level = context["authority_level"]
        if "source_path" in context:
            packet.source_context.source_path = context["source_path"]
        if "intended_audience" in context:
            packet.source_context.intended_audience = context["intended_audience"]
        if "constraints" in context:
            packet.declared_constraints = list(context["constraints"])
        if "measurement_path_modified" in context:
            packet.measurement_integrity["context_declared_modified"] = True
        if "privacy_sensitivity" in context:
            try:
                packet.privacy_sensitivity = PrivacySensitivity[
                    context["privacy_sensitivity"].upper()
                ]
            except (KeyError, AttributeError):
                pass
        if "external_training_use" in context:
            packet.external_training_use = context["external_training_use"]
        if "dataset_tier" in context:
            try:
                packet.dataset_tier = DatasetTier[
                    context["dataset_tier"].upper()
                ]
            except (KeyError, AttributeError):
                pass

    return packet
