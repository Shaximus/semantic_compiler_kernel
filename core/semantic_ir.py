"""
Reflexion Semantic Compiler v2.0.0 — Semantic Intermediate Representation

The compiler requires a stable internal representation between language
extraction and decision logic. This is the compiler equivalent of an
intermediate representation in a programming-language compiler.

The LLM or extractor may propose its contents. Deterministic rules validate them.

Citation: v1.0 Spec Section 4 — Semantic Intermediate Representation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SemanticIR:
    """
    Typed Semantic Intermediate Representation.

    All fields are populated during compilation. The model may propose contents;
    deterministic rules in the gates and decision engine validate them.

    Citation: v1.0 Spec Section 4 — Semantic Intermediate Representation
    """

    # --- Core semantic content ---
    claims: list[dict[str, Any]] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)

    # --- Frame detection ---
    source_frames: list[str] = field(default_factory=list)
    candidate_targets: list[str] = field(default_factory=list)
    selected_target: Optional[str] = None

    # --- Evidence layer ---
    evidence: list[dict[str, Any]] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    rejected_assumptions: list[str] = field(default_factory=list)

    # --- Structural skeleton ---
    actors: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    flows: list[str] = field(default_factory=list)
    forces: list[str] = field(default_factory=list)

    # --- Dynamic structure ---
    control_loops: list[dict[str, Any]] = field(default_factory=list)
    feedback_loops: list[dict[str, Any]] = field(default_factory=list)
    hidden_states: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)

    # --- Cross-cutting dimensions ---
    time_horizons: list[str] = field(default_factory=list)
    scale_layers: list[str] = field(default_factory=list)
    authority_vectors: list[dict[str, Any]] = field(default_factory=list)
    measurement_paths: list[dict[str, Any]] = field(default_factory=list)

    # --- Comparison and residuals ---
    comparisons: list[dict[str, Any]] = field(default_factory=list)
    counterfactuals: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)

    # --- v2.0 additions ---
    functional_departments: list[dict[str, Any]] = field(default_factory=list)
    fractal_mappings: list[dict[str, Any]] = field(default_factory=list)
    wave_function_state: str = "superposition"
    cosmological_anchors: list[dict[str, Any]] = field(default_factory=list)
    subconscious_layers: list[dict[str, Any]] = field(default_factory=list)
    trauma_context: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for packet embedding."""
        import dataclasses
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SemanticIR:
        """Reconstruct from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in {f.name for f in cls.__dataclass_fields__.values()}
        })

    def validate(self) -> list[str]:
        """
        Run basic structural validation on the SIR.
        Returns a list of validation errors (empty = valid).
        """
        errors: list[str] = []

        # Claims must have content
        for i, claim in enumerate(self.claims):
            if not claim.get("content"):
                errors.append(f"Claim {i} has no content")
            if not claim.get("claim_type"):
                errors.append(f"Claim {i} has no claim_type")

        # Relationships must reference entities
        entity_ids = {e.get("entity_id") for e in self.entities}
        for i, rel in enumerate(self.relationships):
            src = rel.get("source_entity_id")
            tgt = rel.get("target_entity_id")
            if src and src not in entity_ids:
                errors.append(
                    f"Relationship {i} references unknown source entity: {src}"
                )
            if tgt and tgt not in entity_ids:
                errors.append(
                    f"Relationship {i} references unknown target entity: {tgt}"
                )

        # Evidence must have source_type
        for i, ev in enumerate(self.evidence):
            if not ev.get("source_type"):
                errors.append(f"Evidence {i} has no source_type")

        return errors
