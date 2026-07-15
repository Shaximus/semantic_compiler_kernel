"""
Reflexion Semantic Compiler v2.0.0 — Master Pipeline

This is the heart of the compiler. Every semantic packet flows through
this pipeline from raw input to decision.

The canonical law:
    The compiler does not search for the prettiest metaphor.
    It searches for the highest-coherence structure that survives
    evidence, causality, scale, boundary, contradiction, measurement,
    and authority checks.

v2.0 extends the v1.0 pipeline with:
    - Wave Function Coherence gate
    - Universal Fractal Isomorphism mapping
    - Regulated Reality Orientation Protocol
    - Cosmological scale mappings

Citation: v1.0 Spec Section 8 — Master Pipeline
"""

from __future__ import annotations

from typing import Any, Optional

from semantic_compiler.core.packet import SemanticPacket, SourceContext, initialize_packet
from semantic_compiler.core.types import (
    CompilerMode,
    DatasetTier,
    Decision,
    PrivacySensitivity,
)
from semantic_compiler.core.scoring import score_packet
from semantic_compiler.core.decisions import decide_packet
from semantic_compiler.core.audit import build_audit_record
from semantic_compiler.core.dataset import build_dataset_row

# Extraction
from semantic_compiler.extraction.claims import classify_claim_types
from semantic_compiler.extraction.evidence import extract_evidence_inventory, extract_unknowns, apply_bayesian_coherence
from semantic_compiler.extraction.constraints import extract_declared_constraints
from semantic_compiler.extraction.skeleton import extract_structural_skeleton, build_semantic_ir
from semantic_compiler.extraction.relationships import extract_relationships
from semantic_compiler.extraction.frames import detect_source_frames, infer_target_systems

# Gates
from semantic_compiler.gates.causality import separate_causality_from_analogy
from semantic_compiler.gates.scale import enforce_scale_separation
from semantic_compiler.gates.boundaries import enforce_boundary_preservation
from semantic_compiler.gates.measurement import evaluate_measurement_paths
from semantic_compiler.gates.authority import scan_approval_vectors
from semantic_compiler.gates.security import scan_semantic_and_operational_risk
from semantic_compiler.gates.wave_function import evaluate_wave_function_coherence
from semantic_compiler.gates.substrate import detect_sovereignty_threat
from semantic_compiler.gates.contradiction_repair import (
    detect_and_repair_contradictions,
    classify_semantic_error,
)

# Translation
from semantic_compiler.translation.fractal import map_fractal_similarity

# Modes
from semantic_compiler.modes.reality_orientation import apply_reality_orientation
from semantic_compiler.modes.coherence import evaluate_coherence


def normalize_preserving_signal(text: str) -> str:
    """
    Normalize input text while preserving emotional signal.

    Rules from Diamond++:
    - Correct spelling in normalized fields only
    - Do NOT erase emotional/compressed signal
    - Do NOT over-sanitize
    - Preserve uncertainty markers, metaphor choice, compressed phrasing
    """
    # Light normalization: strip leading/trailing whitespace,
    # normalize line endings. Heavy normalization happens in derivatives.
    return text.strip().replace('\r\n', '\n').replace('\r', '\n')


def classify_source_context(
    input_text: str,
    context: Optional[dict[str, Any]] = None,
) -> SourceContext:
    """Classify the source context of the input."""
    ctx = SourceContext()
    if context:
        ctx.source_type = context.get("source_type")
        ctx.origin = context.get("origin")
        ctx.trust_level = context.get("trust_level")
        ctx.intended_audience = context.get("intended_audience")
        ctx.authority_level = context.get("authority_level", "none")
        ctx.source_path = context.get("source_path")
    return ctx


def resolve_mode(
    packet: SemanticPacket,
    requested_mode: str = "AUTO",
) -> CompilerMode:
    """
    Resolve the compilation mode from context and claims.

    In AUTO mode, the compiler infers the best mode from the input.
    """
    if requested_mode != "AUTO":
        try:
            return CompilerMode[requested_mode.upper()]
        except KeyError:
            pass

    # Auto-detection based on claim types
    claim_type_names = [c.get("type", "") for c in packet.claim_types]

    if "REALITY_ORIENTATION" in claim_type_names:
        return CompilerMode.REGULATED_REALITY_ORIENTATION
    if "FRACTAL_ISOMORPHISM" in claim_type_names:
        return CompilerMode.FRACTAL_ISOMORPHISM_MAPPING
    if "COSMOLOGICAL_CLAIM" in claim_type_names:
        return CompilerMode.COSMOLOGICAL_MAPPING
    if any(ct in claim_type_names for ct in ("POLICY_CLAIM", "NORMATIVE_PROPOSAL")):
        return CompilerMode.PUBLIC_TRANSLATION
    if "AUTHORITY_REQUEST" in claim_type_names:
        return CompilerMode.APPROVAL_RISK_TRANSLATION

    return CompilerMode.UNIVERSAL_DECOMPRESSION


def build_noun_translation(packet: SemanticPacket, registry: Any = None) -> list[dict[str, Any]]:
    """Build noun translation layer from structural skeleton."""
    skeleton = packet.structural_skeleton
    translations = []
    for actor in skeleton.get("actors", []):
        translations.append({
            "source_noun": actor,
            "target_noun": actor,  # placeholder — LLM proposes, registry validates
            "confidence": 0.5,
        })
    return translations


def build_function_translation(packet: SemanticPacket, registry: Any = None) -> list[dict[str, Any]]:
    """Build function translation layer from structural skeleton."""
    skeleton = packet.structural_skeleton
    translations = []
    for flow in skeleton.get("flows", []):
        translations.append({
            "source_function": flow,
            "target_function": flow,
            "confidence": 0.5,
        })
    return translations


def build_relationship_translation(packet: SemanticPacket, registry: Any = None) -> list[dict[str, Any]]:
    """Build relationship translation layer from extracted SVO/analogy edges."""
    return [
        {
            "source_relationship": rel.get("source_entity_id"),
            "target_relationship": rel.get("target_entity_id"),
            "relationship_type": rel.get("relationship_type"),
            "confidence": rel.get("confidence", 0.5),
        }
        for rel in packet.semantic_ir.relationships
        if isinstance(rel, dict)
    ]


def build_failure_mode_translation(packet: SemanticPacket, registry: Any = None) -> list[dict[str, Any]]:
    """Build failure mode translation layer."""
    skeleton = packet.structural_skeleton
    translations = []
    for fm in skeleton.get("failure_modes", []):
        translations.append({
            "source_failure": fm,
            "target_failure": fm,
            "confidence": 0.5,
        })
    return translations


def detect_and_repair_contradictions(packet: SemanticPacket) -> list[dict[str, Any]]:
    """
    Detect contradictions in the packet.

    Delegates to the deterministic contradiction-repair gate for structured
    repair objects (anthropomorphic causation, physical category errors, and
    direct claim negation). Also classifies the packet's salient semantic error.
    """
    from semantic_compiler.gates.contradiction_repair import (
        detect_and_repair_contradictions as _repair_gate,
        classify_semantic_error,
    )
    error_info = classify_semantic_error(packet)
    if error_info:
        packet.semantic_error_class = error_info["error_class"]
        packet.semantic_error_confidence = error_info["confidence"]
    return _repair_gate(packet)


def detect_category_errors(packet: SemanticPacket) -> list[dict[str, Any]]:
    """
    Detect category errors (type mismatches treated as valid mappings).

    Example: "Magnetism explains the Moon's orbit because opposites attract."
    → SYMBOLIC_TO_PHYSICAL_CATEGORY_ERROR
    """
    errors = []

    for mapping in packet.fractal_mappings:
        source_type = mapping.get("source_type", "")
        target_type = mapping.get("target_type", "")

        if source_type == "symbolic" and target_type == "physical":
            errors.append({
                "mapping": mapping,
                "error": "SYMBOLIC_TO_PHYSICAL_CATEGORY_ERROR",
                "detail": "Symbolic/metaphorical property applied as physical law.",
            })
        if source_type == "emotional" and target_type == "physical":
            errors.append({
                "mapping": mapping,
                "error": "EMOTIONAL_TO_PHYSICAL_CATEGORY_ERROR",
                "detail": "Emotional state treated as physical constraint.",
            })

    return errors


def run_negative_isomorphism_tests(packet: SemanticPacket) -> list[dict[str, Any]]:
    """
    Every strong analogy must be attacked before acceptance.

    Citation: v1.0 Spec Section 13 — Negative Isomorphism Testing
    """
    tests = []

    for mapping in packet.fractal_mappings:
        source = mapping.get("source", "")
        target = mapping.get("target", "")
        preserved = mapping.get("preserved_invariants", [])
        residuals = mapping.get("residuals", [])

        test = {
            "mapping": f"{source}→{target}",
            "source_only_features": [],  # LLM-assisted
            "target_only_features": [],  # LLM-assisted
            "residuals_acknowledged": len(residuals) > 0,
            "preserved_count": len(preserved),
            "attack_result": "UNTESTED",
        }

        # A metaphor with no visible failure surface is probably
        # poetic, underspecified, or overfit.
        if not residuals:
            test["attack_result"] = "SUSPICIOUS"
            test["warning"] = (
                "No residual mismatches declared. "
                "Every valid analogy has failure surfaces."
            )
        elif len(residuals) >= 2 and len(preserved) >= 2:
            test["attack_result"] = "SURVIVED"
        else:
            test["attack_result"] = "WEAK"

        tests.append(test)

    return tests


def generate_structural_residuals(packet: SemanticPacket) -> list[str]:
    """
    Generate input-specific residual mismatches from structural analysis.

    Instead of only pulling residuals from fractal_mappings (which are often
    empty), this function synthesizes residuals from the full analysis:
    claim_types, scale_separation, causal_analysis, boundary_checks,
    category_errors, and negative_isomorphism_tests.
    """
    residuals: list[str] = []

    # --- Claim-type residuals ---
    claim_type_names = [c.get("claim_type", "") for c in packet.claim_types]

    has_metaphor = "METAPHOR" in claim_type_names
    has_analogy = "ANALOGY" in claim_type_names
    has_cosmological = "COSMOLOGICAL_CLAIM" in claim_type_names
    has_inference = "INFERENCE" in claim_type_names
    has_hypothesis = "HYPOTHESIS" in claim_type_names
    has_measurement = "MEASUREMENT" in claim_type_names

    # --- Scale separation residuals ---
    scale = packet.scale_separation
    scale_failed = scale.get("any_gate_failure", False)
    scale_transforms = scale.get("transforms", [])

    if has_metaphor or has_analogy:
        if scale_failed:
            for st in scale_transforms:
                if not st.get("gate_passed", True):
                    mapping_label = st.get("mapping", "unknown→unknown")
                    for err in st.get("errors", []):
                        residuals.append(
                            f"Scale mismatch in {mapping_label}: {err}"
                        )
            if not residuals:
                residuals.append(
                    "Scale mismatch: personal-scale claim applied at "
                    "organizational scale without explicit bridging."
                )
        else:
            residuals.append(
                f"{'Metaphorical' if has_metaphor else 'Analogical'} framing "
                f"detected but no scale violation found — mapping may be "
                f"structurally valid."
            )

    # --- Causal analysis residuals ---
    causal = packet.causal_analysis
    if causal.get("analogy_only", False):
        residuals.append(
            "All mappings classified as analogy-only — no causal mechanism "
            "identified. Structural similarity does not prove causation."
        )
    if causal.get("any_gate_failure", False):
        for finding in causal.get("findings", []):
            if not finding.get("gate_passed", True):
                reason = finding.get("failure_reason", "unspecified")
                residuals.append(
                    f"Causality gate failure ({finding.get('mapping_id', '?')}): "
                    f"{reason}"
                )

    # --- Boundary check residuals ---
    boundary = packet.boundary_checks
    boundary_violations = boundary.get("violations", [])
    if boundary_violations:
        for v in boundary_violations:
            residuals.append(
                f"Boundary violation ({v.get('type', '?')}): "
                f"{v.get('detail', 'boundary not preserved in translation')}"
            )
    elif boundary.get("note"):
        # No boundaries to check — flag the absence
        if has_metaphor or has_analogy:
            residuals.append(
                "No explicit boundaries declared — cross-domain mapping "
                "may silently violate ownership/trust/containment boundaries."
            )

    # --- Category error residuals ---
    for ce in packet.category_errors:
        err_type = ce.get("error", "UNKNOWN")
        detail = ce.get("detail", "")
        residuals.append(f"Category error ({err_type}): {detail}")

    # --- Negative isomorphism test residuals ---
    for test in packet.negative_isomorphism_tests:
        result = test.get("attack_result", "UNTESTED")
        mapping_label = test.get("mapping", "unknown→unknown")
        if result == "SUSPICIOUS":
            warning = test.get("warning", "No failure surface declared.")
            residuals.append(
                f"Negative test SUSPICIOUS ({mapping_label}): {warning}"
            )
        elif result == "WEAK":
            residuals.append(
                f"Negative test WEAK ({mapping_label}): insufficient "
                f"preserved invariants or residuals for robust analogy."
            )

    # --- Cosmological / inference / hypothesis residuals ---
    has_structural_identity = "STRUCTURAL_IDENTITY" in claim_type_names
    has_correction = "CORRECTION" in claim_type_names

    if has_cosmological and not has_measurement:
        if has_structural_identity:
            # Speaker is asserting structural identity, not vague analogy.
            # Check if it's a known mapping from the isomorphism registry.
            residuals.append(
                "Cosmological structural identity claim — speaker asserts "
                "same mechanism across scales, not analogy. "
                "Classification: FRAMEWORK_DERIVED if from published derivation, "
                "STRUCTURAL_IDENTITY if from verified isomorphism table."
            )
        else:
            residuals.append(
                "Cosmological claim without measurement evidence or "
                "structural identity assertion — requires framework "
                "derivation or empirical grounding for acceptance."
            )

    if has_correction:
        residuals.append(
            "CORRECTION detected — speaker is repairing a previous "
            "framing error. This is high-value training data: "
            "the correction itself teaches the boundary between "
            "valid and invalid structural mappings."
        )

    if has_structural_identity and (has_metaphor or has_analogy):
        residuals.append(
            "Tension: input contains both analogy markers ('like', 'similar') "
            "and identity markers ('IS', 'same mechanism'). "
            "Resolve: does the speaker mean structural similarity or "
            "actual mechanistic identity?"
        )

    if has_inference and not packet.evidence_inventory:
        residuals.append(
            "Inference claim made without supporting evidence inventory."
        )
    if has_hypothesis:
        residuals.append(
            "Hypothesis detected — requires falsifiability criteria "
            "and test design before acceptance."
        )

    # --- Fallback: also pull any fractal mapping residuals ---
    for m in packet.fractal_mappings:
        for r in m.get("residuals", []):
            if r not in residuals:
                residuals.append(r)

    # If nothing was generated, produce a default structural note
    if not residuals:
        primary_type = claim_type_names[0] if claim_type_names else "UNKNOWN"
        residuals.append(
            f"Claim type '{primary_type}' processed through all gates "
            f"with no structural violations detected."
        )

    return residuals


def discover_hidden_variables(packet: SemanticPacket) -> dict[str, Any]:
    """
    Search beyond the headline variable for hidden constraints.

    Citation: v1.0 Spec Section 12 — Hidden Variable Discovery
    """
    candidates = []

    # Check for missing owners
    skeleton = packet.structural_skeleton
    for resource in skeleton.get("resources", []):
        if not resource.get("owner"):
            candidates.append({
                "type": "MISSING_OWNER",
                "resource": resource,
                "detail": "Resource has no identified owner.",
            })

    # Check for missing feedback loops
    if skeleton.get("flows") and not skeleton.get("feedback_loops"):
        candidates.append({
            "type": "MISSING_FEEDBACK_LOOP",
            "detail": "System has flows but no feedback loops.",
        })

    return {
        "candidates": candidates,
        "total_hidden_variables": len(candidates),
    }


def _infer_system_scale(packet: SemanticPacket) -> str:
    """
    Map detected source frames to the canonical scale names used by the
    universal isomorphism table. Falls back to the selected target frame.
    """
    frame_to_scale: dict[str, str] = {
        # Biology / human
        "biology": "human",
        "human": "human",
        "body": "human",
        "biological": "human",
        "medical": "human",
        # Computing
        "computation": "computer",
        "computer": "computer",
        "software": "computer",
        "hardware": "computer",
        # Society / organizational
        "organizational": "society",
        "society": "society",
        "government": "society",
        "national": "society",
        "civilization": "society",
        "economic": "society",
        "economy": "society",
        # Cosmology / physics
        "cosmological": "cosmos",
        "cosmos": "cosmos",
        "physics": "cosmos",
        # Cellular
        "cellular": "cellular",
        "cell": "cellular",
        # AI / LLM
        "reflexion": "llm",
        "ai": "llm",
        "model": "llm",
        "llm": "llm",
        "transformer": "llm",
        "neural": "llm",
    }

    for frame in packet.source_frames:
        frame_lower = frame.rstrip("?").lower()
        if frame_lower in frame_to_scale:
            return frame_to_scale[frame_lower]

    target = (packet.selected_target or "").lower()
    if target in frame_to_scale:
        return frame_to_scale[target]

    return target or "organizational"


def infer_missing_functions(
    packet: SemanticPacket,
    registry: Any = None,
) -> list[dict[str, Any]]:
    """
    Infer missing functional departments from the structural skeleton.

    Citation: v1.0 Spec Section 14 — Functional Department Invariance
    """
    from semantic_compiler.translation.fractal import identify_missing_departments

    completeness_modes = {
        CompilerMode.STRUCTURAL_RECONSTRUCTION,
        CompilerMode.SYSTEM_DIAGNOSTIC,
        CompilerMode.FUNCTIONAL_DEPARTMENT_MAPPING,
    }
    completeness_required = (
        packet.mode in completeness_modes
        or getattr(packet.semantic_ir, "requested_analysis", None) == "completeness"
        or any(
            isinstance(c, dict) and "complete system" in str(c.get("content", "")).lower()
            for c in packet.claim_types
        )
    )

    skeleton = packet.structural_skeleton
    present = skeleton.get("actors", []) + skeleton.get("flows", [])
    system_desc = {"present_functions": [p.upper() for p in present if isinstance(p, str)]}

    system_scale = _infer_system_scale(packet)
    return identify_missing_departments(
        system_desc,
        scale=system_scale,
        completeness_required=completeness_required,
        raw_text=packet.raw_input,
    )


def generate_literal_translation(packet: SemanticPacket) -> str:
    """Generate literal translation stripped of metaphor."""
    lines: list[str] = []

    # Actors
    actors = packet.structural_skeleton.get("actors", [])
    actor_str = ", ".join(actors) if actors else "unspecified"

    # Claim types
    claim_types = [c.get("claim_type", "OBSERVATION") for c in packet.claim_types]
    claim_str = ", ".join(claim_types) if claim_types else "OBSERVATION"

    lines.append(f"Speaker [{actor_str}] asserts [{claim_str}].")

    # Source frames
    frames = packet.source_frames
    if frames:
        lines.append(f"Source frame: {', '.join(frames)}.")
    else:
        lines.append("Source frame: none detected.")

    # Target system
    target = packet.selected_target or "none resolved"
    lines.append(f"Target system: {target}.")

    # Key structural elements
    skeleton = packet.structural_skeleton
    skel_parts: list[str] = []
    for key in ("actors", "boundaries", "flows", "resources", "forces"):
        items = skeleton.get(key, [])
        if items:
            skel_parts.append(f"{key}: {', '.join(str(i) for i in items)}")
    if skel_parts:
        lines.append(f"Key structural elements: {'; '.join(skel_parts)}.")

    # Scale layers
    scale_sep = packet.scale_separation
    scale_layers = scale_sep.get("layers", scale_sep.get("scales", []))
    if scale_layers:
        lines.append(f"Scale layers present: {', '.join(str(s) for s in scale_layers)}.")

    # Contradictions
    for contradiction in packet.contradictions:
        ctype = contradiction.get("type", "unknown")
        lines.append(f"Contradiction detected: {ctype}.")

    # Category errors
    for error in packet.category_errors:
        err_type = error.get("error", "unknown")
        detail = error.get("detail", "")
        lines.append(f"Category error: {err_type} — {detail}")

    # Fractal mappings summary
    for mapping in packet.fractal_mappings:
        source = mapping.get("source_implementation", mapping.get("source", ""))
        target_impl = mapping.get("target_implementation", mapping.get("target", ""))
        preserved = mapping.get("preserved_invariants", [])
        residuals = mapping.get("residuals", [])
        if source and target_impl:
            lines.append(
                f"Cross-scale mapping: {source} → {target_impl} "
                f"({len(preserved)} preserved functions, {len(residuals)} residuals)."
            )

    return "\n".join(lines)


def generate_public_translation(packet: SemanticPacket) -> str:
    """Generate public-safe translation without internal mythology."""
    parts: list[str] = []

    # Summarise what the input is about using claim types in plain English
    _CLAIM_PLAIN: dict[str, str] = {
        "OBSERVATION": "an observation",
        "MEASUREMENT": "a measurement report",
        "LOG_RECORD": "a log-based report",
        "RECOLLECTION": "a recalled account",
        "INFERENCE": "a logical inference",
        "HYPOTHESIS": "a hypothesis",
        "ANALOGY": "a comparison between systems",
        "METAPHOR": "a figurative description",
        "COUNTERFACTUAL": "a what-if scenario",
        "DEFINITION": "a definition",
        "PREDICTION": "a prediction",
        "NORMATIVE_PROPOSAL": "a recommendation",
        "POLICY_CLAIM": "a policy statement",
        "OPERATIONAL_INSTRUCTION": "an operational instruction",
        "AUTHORITY_REQUEST": "a request for authority",
        "STRUCTURAL_MAPPING": "a structural comparison",
        "COSMOLOGICAL_CLAIM": "a claim about large-scale physical systems",
        "FRACTAL_ISOMORPHISM": "a claim about repeating patterns across scales",
        "REALITY_ORIENTATION": "a grounding statement about physical constraints",
    }

    claim_names = [c.get("claim_type", "OBSERVATION") for c in packet.claim_types]
    plain_claims = [_CLAIM_PLAIN.get(cn, cn.lower().replace("_", " ")) for cn in claim_names]
    if plain_claims:
        parts.append(f"The input is {plain_claims[0]}.")
        if len(plain_claims) > 1:
            parts.append(f"It also contains {', '.join(plain_claims[1:])}.")

    # Describe source domain in plain English
    _FRAME_PLAIN: dict[str, str] = {
        "biology": "biology and living systems",
        "computation": "computers and software",
        "organizational": "teams and organizations",
        "national": "government and national systems",
        "cosmological": "physics and the cosmos",
        "personal": "personal and psychological experience",
        "economic": "economics and markets",
        "reflexion": "the Reflexion system",
    }
    frames = [f.rstrip("?") for f in packet.source_frames]
    if frames:
        plain_frames = [_FRAME_PLAIN.get(f, f) for f in frames]
        parts.append(f"It draws language from {', '.join(plain_frames)}.")

    # Target domain
    if packet.selected_target:
        target_plain = _FRAME_PLAIN.get(packet.selected_target, packet.selected_target)
        parts.append(f"The structural meaning maps onto {target_plain}.")

    # Structural summary from skeleton
    skeleton = packet.structural_skeleton
    actors = skeleton.get("actors", [])
    flows = skeleton.get("flows", [])
    boundaries = skeleton.get("boundaries", [])
    if actors:
        parts.append(f"Key participants: {', '.join(actors)}.")
    if flows:
        parts.append(f"Key activities: {', '.join(flows)}.")
    if boundaries:
        parts.append(f"Defined boundaries: {', '.join(boundaries)}.")

    # Causal vs. analogy distinction in plain terms
    ca = packet.causal_analysis
    if ca.get("analogy_only"):
        parts.append("Note: the comparison is structural, not a direct cause-and-effect relationship.")
    elif ca.get("mapping_class") == "MATERIAL_IDENTITY":
        parts.append("This describes a direct relationship, not a metaphor.")

    # Residual mismatches as plain caveats
    if packet.residual_mismatches:
        n = len(packet.residual_mismatches)
        parts.append(f"Caveat: {n} area{'s' if n != 1 else ''} where the comparison breaks down.")

    return " ".join(parts) if parts else "No public translation generated."


def generate_executive_translation(packet: SemanticPacket) -> str:
    """Generate executive translation for priorities and next actions."""
    lines: list[str] = []

    # Decision
    decision_name = packet.decision.name if packet.decision else "PENDING"
    lines.append(f"Decision: {decision_name}.")

    # Confidence scores summary (top-level)
    scores = packet.scores
    composite = scores.get("composite_soft")
    overall = scores.get("overall_quality")
    coherence = scores.get("coherence_composite")
    conf_parts: list[str] = []
    if composite is not None:
        conf_parts.append(f"composite={composite:.3f}")
    if overall is not None:
        conf_parts.append(f"overall_quality={overall:.3f}")
    if coherence is not None:
        conf_parts.append(f"coherence={coherence:.3f}")
    if conf_parts:
        lines.append(f"Confidence: {', '.join(conf_parts)}.")

    # Key risks
    risk_items: list[str] = []
    for risk_dim in ("ambiguity", "authority_risk", "security_risk", "overclaim_risk"):
        val = scores.get(risk_dim)
        if val is not None and val >= 0.4:
            risk_items.append(f"{risk_dim}={val:.2f}")
    risk_scan = packet.risk_scan
    if risk_scan.get("quarantine_required"):
        risk_items.append("QUARANTINE_REQUIRED")
    if risk_scan.get("security_concern"):
        risk_items.append("SECURITY_CONCERN")
    if risk_items:
        lines.append(f"Key risks: {', '.join(risk_items)}.")
    else:
        lines.append("Key risks: none elevated.")

    # Hard gate failures
    gate_failures = [e for e in packet.compiler_errors if "HARD GATE" in e]
    if gate_failures:
        lines.append(f"Gate failures: {'; '.join(gate_failures)}.")

    # Routing
    route = packet.route_to if packet.route_to else packet.routing_packet.get("route_to", [])
    if route:
        lines.append(f"Route to: {', '.join(route)}.")
    else:
        lines.append("Route to: none.")

    # Residual mismatches
    if packet.residual_mismatches:
        n = len(packet.residual_mismatches)
        first_few = packet.residual_mismatches[:3]
        lines.append(f"Residual mismatches ({n}): {'; '.join(str(r) for r in first_few)}.")

    return "\n".join(lines)


def build_routing_packet(packet: SemanticPacket) -> dict[str, Any]:
    """Build the routing packet for delivery."""
    return {
        "packet_id": packet.packet_id,
        "decision": packet.decision.name if packet.decision else "PENDING",
        "route_to": packet.route_to,
        "priority": "HIGH" if packet.decision in (
            Decision.ESCALATE, Decision.QUARANTINE
        ) else "NORMAL",
    }


def _format_bullet_list(items: list[Any]) -> str:
    """Format a list of items as markdown bullets."""
    if not items:
        return "- none"
    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            lines.append(f"- {item}")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _build_assistant_content(packet: SemanticPacket) -> str:
    """
    Construct the ideal Logos compiler output for SFT training.

    Format aligns with Diamond++ sample schema: a structured semantic
    packet containing mode, frames, skeleton, translations, scale
    separation, contradictions, residuals, policy overrides, decision,
    and routing.
    """
    parts: list[str] = []

    mode = packet.mode.name if packet.mode else "AUTO"
    parts.append(f"**Mode:** {mode}")

    if packet.source_frames:
        parts.append(f"**Source frames:** {', '.join(packet.source_frames)}")

    target = packet.selected_target or "none resolved"
    parts.append(f"**Target system:** {target}")

    skeleton = packet.structural_skeleton
    if skeleton:
        skel_lines = ["**Structural skeleton:**"]
        for key in ("actors", "objects", "boundaries", "inputs", "outputs",
                    "flows", "resources", "forces", "control_loops",
                    "feedback_loops", "failure_modes"):
            items = skeleton.get(key, [])
            if items:
                skel_lines.append(f"- {key}: {', '.join(str(i) for i in items)}")
        parts.append("\n".join(skel_lines))

    if packet.noun_translation:
        parts.append(
            "**Noun translation:**\n" +
            _format_bullet_list(
                [f"{t.get('source_noun', '?')} → {t.get('target_noun', '?')}"
                 for t in packet.noun_translation]
            )
        )

    if packet.function_translation:
        parts.append(
            "**Function translation:**\n" +
            _format_bullet_list(
                [f"{t.get('source_function', '?')} → {t.get('target_function', '?')}"
                 for t in packet.function_translation]
            )
        )

    scale_sep = packet.scale_separation
    if scale_sep:
        scale_lines = ["**Scale separation:**"]
        if scale_sep.get("violation"):
            scale_lines.append("- Scale gate: FAILED")
        elif scale_sep.get("transform_valid"):
            scale_lines.append("- Scale gate: PASSED")
        else:
            scale_lines.append("- Scale gate: not evaluated")
        transforms = scale_sep.get("transforms", scale_sep.get("scale_transforms", []))
        for st in transforms:
            mapping = st.get("mapping", "unknown→unknown")
            passed = st.get("gate_passed", True)
            scale_lines.append(f"- {mapping}: {'PASSED' if passed else 'FAILED'}")
        parts.append("\n".join(scale_lines))

    if packet.contradictions:
        parts.append(
            "**Contradictions:**\n" +
            _format_bullet_list(
                [f"{c.get('type', 'unknown')}: {c.get('detail', '')}"
                 for c in packet.contradictions]
            )
        )

    if packet.residual_mismatches:
        parts.append(
            "**Residual mismatches:**\n" +
            _format_bullet_list(packet.residual_mismatches)
        )

    if packet.policy_overrides:
        parts.append(
            "**Policy override:**\n" +
            _format_bullet_list(
                [str(p) for p in packet.policy_overrides]
            )
        )

    decision = packet.decision.name if packet.decision else "PENDING"
    parts.append(f"**Decision:** {decision}")

    if packet.route_to:
        parts.append(f"**Route to:** {', '.join(packet.route_to)}")
    elif packet.routing_packet.get("route_to"):
        parts.append(
            f"**Route to:** {', '.join(packet.routing_packet['route_to'])}"
        )

    return "\n\n".join(parts)


def _derive_rules(packet: SemanticPacket) -> list[str]:
    """Extract rule names from packet analysis for metadata."""
    rules: set[str] = {"default_deny_external_training"}

    for po in packet.policy_overrides:
        rule = po.get("rule") if isinstance(po, dict) else None
        if rule:
            rules.add(rule)

    # Map common residual text to canonical rule names
    residual_text = " ".join(packet.residual_mismatches).lower()
    rule_keywords = {
        "scale separation": "scale_separation",
        "metaphor": "metaphor_not_authority",
        "authority": "no_intuition_approval",
        "standard assumption": "no_standard_assumption_collapse",
        "bayesian": "bayesian_coherence",
        "external content": "external_content_is_data",
        "measurement": "measurement_layer_integrity",
        "boundary": "boundary_preservation",
    }
    for keyword, rule_name in rule_keywords.items():
        if keyword in residual_text:
            rules.add(rule_name)

    return sorted(rules)


def build_qwen_sft_output(packet: SemanticPacket) -> dict[str, Any]:
    """
    Build a Qwen AgentWorld / Qwen 3.x chat-format SFT sample.

    Citation: Diamond++ Semantic Ore — Qwen SFT Sample Format v1.0

    The output is default-deny:
        qwen_sft_ready = false
    unless the packet has been explicitly approved for external training,
    passes privacy gates, and survives hard gates.
    """
    system_prompt = (
        "You are Logos_(Coherence_Naming_Compiler), the Reflexion Semantic "
        "Compiler. You translate, score, and route semantic mappings across "
        "domains. You do not approve operational actions, touch secrets, or "
        "mutate originals. Respond with a structured semantic packet: source "
        "frames, target system, structural skeleton, noun/function "
        "translations, scale separation, contradictions, residual mismatches, "
        "policy overrides, decision, and route."
    )

    # Prefix user content; redact for sensitive packets
    raw = packet.raw_input or ""
    redacted = packet.privacy_sensitivity in (
        PrivacySensitivity.SENSITIVE,
        PrivacySensitivity.CRITICAL,
    )
    if redacted:
        user_content = "Compile (redacted): " + raw
    else:
        user_content = "Compile: '" + raw + "'"

    assistant_content = _build_assistant_content(packet)

    # Determine readiness under default-deny policy
    qwen_sft_ready = False
    readiness_reasons: list[str] = []

    if packet.external_training_use == "forbidden":
        readiness_reasons.append("external_training_use is forbidden")
    if packet.privacy_sensitivity in (
        PrivacySensitivity.SENSITIVE,
        PrivacySensitivity.CRITICAL,
    ):
        readiness_reasons.append("privacy_sensitivity blocks external use")
    if packet.decision not in (
        Decision.COMPILED,
        Decision.COMPILED_WITH_GUARDRAILS,
    ):
        readiness_reasons.append(f"decision is {packet.decision.name if packet.decision else 'PENDING'}")
    if packet.dataset_tier in (DatasetTier.BRONZE, DatasetTier.REJECT, None):
        readiness_reasons.append(
            f"dataset_tier is {packet.dataset_tier.name if packet.dataset_tier else 'unset'}"
        )
    if packet.scores.get("hard_gates_passed", 0.0) < 1.0:
        readiness_reasons.append("hard gates not passed")

    if not readiness_reasons:
        qwen_sft_ready = True

    tier_name = packet.dataset_tier.name if packet.dataset_tier else "bronze"
    review_status = "accepted" if qwen_sft_ready else "draft"

    _PRIVACY_SFT_LABEL = {
        PrivacySensitivity.PUBLIC: "public_safe",
        PrivacySensitivity.INTERNAL: "internal",
        PrivacySensitivity.SENSITIVE: "sensitive_redacted",
        PrivacySensitivity.CRITICAL: "sensitive_redacted",
    }

    modes = [packet.mode.name if packet.mode else "AUTO"]
    # Include active submodes if present
    if packet.active_submodes:
        modes = [m.name for m in packet.active_submodes]

    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ],
        "metadata": {
            "sample_id": packet.packet_id,
            "tier": tier_name.lower(),
            "modes": modes,
            "rules": _derive_rules(packet),
            "privacy": _PRIVACY_SFT_LABEL.get(
                packet.privacy_sensitivity,
                packet.privacy_sensitivity.name.lower(),
            ),
            "source_hash": packet.source_context.source_hash or packet.compute_input_hash(),
            "review_status": review_status,
            "z24_scores": {
                "truth": packet.scores.get("truth", 0.0),
                "evidence_discipline": packet.scores.get("evidence_quality", 0.0),
                "coherence": packet.scores.get("coherence_composite", 0.0),
                "security_posture": 1.0 - packet.scores.get("security_risk", 0.0),
                "closure_rate": 1.0 if packet.decision in (
                    Decision.COMPILED,
                    Decision.COMPILED_WITH_GUARDRAILS,
                ) else 0.0,
            },
            "qwen_sft_ready": qwen_sft_ready,
            "readiness_reasons": readiness_reasons,
        },
    }


def _finalize_packet(packet: SemanticPacket) -> None:
    """
    Build dataset, SFT, and audit artifacts regardless of decision.

    This ensures failed/revised packets still produce training rows
    and SFT samples (useful for negative examples) and that timing
    and audit metadata are always recorded.
    """
    from semantic_compiler.core.dataset import _classify_tier

    packet.dataset_tier = _classify_tier(packet)
    packet.dataset_row = build_dataset_row(packet)
    packet.qwen_sft_output = build_qwen_sft_output(packet)
    packet.audit = build_audit_record(packet)
    packet.mark_compilation_end()


# ═══════════════════════════════════════════════════════════════════
# THE MASTER PIPELINE
#
# This is the heart of the Semantic Compiler.
# Every semantic packet flows through these 10 stages.
#
# Citation: v1.0 Spec Section 8 — Master Pipeline
# ═══════════════════════════════════════════════════════════════════


def compile_semantic_packet(
    input_text: str,
    registry: Any = None,
    context: Optional[dict[str, Any]] = None,
    mode: str = "AUTO",
) -> SemanticPacket:
    """
    Master compilation pipeline.

    Compiles:
        compressed language
        → explicit claims
        → evidence and constraints
        → source/target frames
        → structural relationships
        → scale transforms
        → causal and analogical classification
        → contradiction testing
        → hidden-variable discovery
        → authority-safe translation
        → routing and reusable training data

    Citation: v1.0 Spec Section 8 — Master Pipeline
    """
    packet = initialize_packet(input_text, context, mode)

    # ──────────────────────────────────────────────────────────
    # Stage 1: Preserve and classify source
    # ──────────────────────────────────────────────────────────
    packet.normalized_input = normalize_preserving_signal(input_text)
    packet.source_context = classify_source_context(input_text, context)
    packet.claim_types = classify_claim_types(input_text, context)
    packet.mode = resolve_mode(packet, requested_mode=mode)

    # v2.1.3: Classify salient semantic errors early, before any early-exit path
    # can bypass the contradiction-repair stage. This ensures negative-category
    # inputs route to REJECT even when no target system resolves.
    error_info = classify_semantic_error(packet)
    if error_info:
        packet.semantic_error_class = error_info["error_class"]
        packet.semantic_error_confidence = error_info["confidence"]

    # ──────────────────────────────────────────────────────────
    # Stage 2: Evidence before interpretation
    # ──────────────────────────────────────────────────────────
    packet.evidence_inventory = extract_evidence_inventory(input_text, context)
    packet.declared_constraints = extract_declared_constraints(input_text, context)
    packet.unknowns = extract_unknowns(input_text, context)
    apply_bayesian_coherence(packet)

    # ──────────────────────────────────────────────────────────
    # Stage 3: Build Semantic Intermediate Representation
    # ──────────────────────────────────────────────────────────
    packet.source_frames = detect_source_frames(input_text, context)
    packet.target_systems = infer_target_systems(input_text, context)
    packet.semantic_ir = build_semantic_ir(packet)

    if not packet.target_systems:
        # v2.1.3: A semantic error can reject the input even when no target
        # frame resolves. Route hard reject classes to REJECT; otherwise keep
        # the legacy NEEDS_REVISION behavior.
        reject_classes = {
            "ANTHROPOMORPHIC_CAUSATION",
            "PHYSICAL_CATEGORY_ERROR",
            "FALSE_MECHANISM",
            "UNSUPPORTED_CAUSAL_TRANSFER",
            "IDENTITY_ANALOGY_CONFUSION",
        }
        if packet.semantic_error_class in reject_classes:
            packet.decision = Decision.REJECT
            packet.status = "rejected"
            packet.compiler_warnings.append(
                f"SEMANTIC_ERROR: {packet.semantic_error_class}"
            )
        else:
            packet.needs_revision(
                "No target system resolved; interpretation would be forced."
            )
        _finalize_packet(packet)
        return packet

    packet.selected_target = packet.target_systems[0] if packet.target_systems else None

    # ──────────────────────────────────────────────────────────
    # Stage 4: Structural translation
    # ──────────────────────────────────────────────────────────
    packet.structural_skeleton = extract_structural_skeleton(packet)
    packet.semantic_ir.relationships = extract_relationships(packet)
    packet.noun_translation = build_noun_translation(packet, registry)
    packet.function_translation = build_function_translation(packet, registry)
    packet.relationship_translation = build_relationship_translation(packet, registry)
    packet.failure_mode_translation = build_failure_mode_translation(packet, registry)
    packet.fractal_mappings = map_fractal_similarity(packet, registry)

    # ──────────────────────────────────────────────────────────
    # Stage 4.5: Populate Semantic IR from extracted data
    # ──────────────────────────────────────────────────────────
    build_semantic_ir(packet)
    skeleton = packet.structural_skeleton
    packet.semantic_ir.selected_target = packet.selected_target
    packet.semantic_ir.candidate_targets = list(packet.target_systems)
    packet.semantic_ir.actors = skeleton.get('actors', [])
    packet.semantic_ir.objects = skeleton.get('objects', [])
    packet.semantic_ir.boundaries = skeleton.get('boundaries', [])
    packet.semantic_ir.inputs = skeleton.get('inputs', [])
    packet.semantic_ir.outputs = skeleton.get('outputs', [])
    packet.semantic_ir.flows = skeleton.get('flows', [])
    packet.semantic_ir.resources = skeleton.get('resources', [])
    packet.semantic_ir.forces = skeleton.get('forces', [])
    packet.semantic_ir.failure_modes = skeleton.get('failure_modes', [])
    packet.semantic_ir.control_loops = skeleton.get('control_loops', [])
    packet.semantic_ir.feedback_loops = skeleton.get('feedback_loops', [])
    packet.semantic_ir.fractal_mappings = list(packet.fractal_mappings)

    # ──────────────────────────────────────────────────────────
    # Stage 5: Hard semantic gates
    # ──────────────────────────────────────────────────────────
    packet.causal_analysis = separate_causality_from_analogy(packet)
    packet.scale_separation = enforce_scale_separation(packet)
    packet.boundary_checks = enforce_boundary_preservation(packet)
    packet.measurement_integrity = evaluate_measurement_paths(packet)

    # v2.0: Wave Function Coherence gate
    packet.wave_function_coherence = evaluate_wave_function_coherence(packet)

    # v2.0: Substrate sovereignty check (Dimensional Ladder)
    sovereignty = detect_sovereignty_threat(packet)
    if not sovereignty.get("sovereignty_intact", True):
        packet.compiler_warnings.append(
            "SOVEREIGNTY THREAT DETECTED: " +
            str([t["type"] for t in sovereignty.get("threats", [])])
        )

    # ──────────────────────────────────────────────────────────
    # Stage 6: Adversarial reasoning
    # ──────────────────────────────────────────────────────────
    packet.contradictions = detect_and_repair_contradictions(packet)
    packet.category_errors = detect_category_errors(packet)
    packet.negative_isomorphism_tests = run_negative_isomorphism_tests(packet)

    packet.hidden_variable_probe = discover_hidden_variables(packet)
    packet.missing_organs = infer_missing_functions(packet, registry)
    packet.residual_mismatches = generate_structural_residuals(packet)

    # ──────────────────────────────────────────────────────────
    # Stage 7: Governance
    # ──────────────────────────────────────────────────────────
    packet.risk_scan = scan_semantic_and_operational_risk(packet)
    packet.approval_scan = scan_approval_vectors(packet)
    packet.routing_packet = build_routing_packet(packet)

    # v2.0: Reality Orientation (if mode is active)
    if packet.mode == CompilerMode.REGULATED_REALITY_ORIENTATION:
        packet.reality_orientation = apply_reality_orientation(packet)

    # ──────────────────────────────────────────────────────────
    # Stage 8: Human-readable outputs
    # ──────────────────────────────────────────────────────────
    packet.literal_translation = generate_literal_translation(packet)
    packet.public_translation = generate_public_translation(packet)
    packet.executive_translation = generate_executive_translation(packet)

    # ──────────────────────────────────────────────────────────
    # Stage 8.5: Coherence verification (v2.0)
    # ──────────────────────────────────────────────────────────
    coherence_result = evaluate_coherence(
        output_text=packet.literal_translation or packet.raw_input or "",
        claims=packet.claim_types,
        evidence=packet.evidence_inventory,
        contradictions=packet.contradictions,
        fractal_mappings=packet.fractal_mappings,
        negative_tests=packet.negative_isomorphism_tests,
    )
    packet.scores["coherence_composite"] = coherence_result["composite_coherence"]
    packet.scores["values_coherence"] = coherence_result["values_coherence"]
    packet.scores["framework_coherence"] = coherence_result["framework_coherence"]

    # ──────────────────────────────────────────────────────────
    # Stage 9: Score and decide
    # ──────────────────────────────────────────────────────────
    packet.scores = {**packet.scores, **score_packet(packet)}
    packet.decision = decide_packet(packet)
    packet.route_to = packet.routing_packet.get("route_to", [])

    # ──────────────────────────────────────────────────────────
    # Stage 10: Learn and audit
    # ──────────────────────────────────────────────────────────
    _finalize_packet(packet)
    packet.status = "compiled"

    return packet
