"""
Reflexion Semantic Compiler — Gate 0: Testimony Integrity Gate (TIG / SC-TIG-001)

A formal pre-gate for first-person testimony within the Semantic Compiler Kernel.
The TIG separates structural truth (scale-invariant isomorphic patterns) from
narrative truth (the witness's evolving interpretation of their own experience).

Design invariant:
    The TIG is INPUT CLASSIFICATION, not INPUT FILTERING.
    Nothing is rejected or deleted by the TIG. Every testimony-derived input is
    preserved and tagged with its composite classification:
        [ConsistencyClass] + [IsomorphismClass] + [CorroborationClass]

    The downstream structural gates then weight testimony-derived evidence
    according to this classification:
    - STABLE/EVOLVED + ISOMORPHIC + ANCHORED enters as primary structural evidence (weight 1.0).
    - CONTRADICTED claims are held as open questions until witness resolution (structural weight 0.0).
    - NARRATIVE claims remain preserved in the testimony corpus without entering structural gates (weight 0.0).
    - UNANCHORED claims support already-established patterns as converging evidence but cannot
      establish a structural pattern on their own.

Citation: SC-TIG-001 v1.0.0 (Hannah / Curtis Kingsley / DeepSeek audit, 2026-11-23)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from semantic_compiler.core.packet import SemanticPacket


class ConsistencyClass(str, Enum):
    """Gate 1 of TIG — tracks evolution of witness framing over time."""

    STABLE = "STABLE"
    EVOLVED = "EVOLVED"
    CONTRADICTED = "CONTRADICTED"


class IsomorphismClass(str, Enum):
    """Gate 2 of TIG — tests functional structural mapping vs surface narrative."""

    ISOMORPHIC = "ISOMORPHIC"
    ANALOGOUS = "ANALOGOUS"
    NARRATIVE = "NARRATIVE"


class CorroborationClass(str, Enum):
    """Gate 3 of TIG — separates externally anchored records from subjective perception."""

    ANCHORED = "ANCHORED"
    PARTIALLY_ANCHORED = "PARTIALLY_ANCHORED"
    UNANCHORED = "UNANCHORED"


class PredictiveDiscriminationClass(str, Enum):
    """Gate 4 of TIG (V7 Part 33.1) — tests whether an interpretation predicts what rivals do not."""

    DISCRIMINATING = "DISCRIMINATING"
    NON_DISCRIMINATING = "NON_DISCRIMINATING"
    FAILED = "FAILED"
    PENDING = "PENDING"


class EvidenceMaturityLevel(str, Enum):
    """V7 Part 33.3 six-rung Evidence Maturity Ladder."""

    OBSERVATION = "OBSERVATION"
    CORROBORATION = "CORROBORATION"
    STRUCTURAL_CORRESPONDENCE = "STRUCTURAL_CORRESPONDENCE"
    PREDICTIVE_VALIDATION = "PREDICTIVE_VALIDATION"
    INDEPENDENT_REPLICATION = "INDEPENDENT_REPLICATION"
    EXPLANATORY_SUPERIORITY = "EXPLANATORY_SUPERIORITY"


_FIRST_PERSON_TESTIMONY_PATTERNS = (
    re.compile(r"\b(i experienced|i witnessed|i saw|my experience|in my own life|personally experienced)\b", re.I),
    re.compile(r"\b(testimony|first-person|lived experience|synchronicit(?:y|ies))\b", re.I),
)

_ANCHOR_PATTERNS = (
    re.compile(r"\b(log|logs|screenshot|screenshots|gps|fitbit|github|analytics|sha256|sqlite|pcap|medical record|bank statement|timestamped|corroborat(?:ed|ion)|forensic artifact)\b", re.I),
)

_ATTRIBUTION_ASSUMPTION_PATTERNS = (
    re.compile(r"\b(targeted by|deliberately caused by|specific agents|orchestrated against me|intentionally directed)\b", re.I),
)

_STRUCTURAL_PATTERN_PATTERNS = (
    re.compile(r"\b(isomorph(?:ic|ism)|invariant|feedback loop|control loop|architecture|topology|substrate|cycle detection|reward signal|gating|scale-invariant|functional structure)\b", re.I),
)


@dataclass
class TIGClassification:
    """Composite output of Gate 0 (Testimony Integrity Gate)."""

    is_testimony: bool
    consistency: ConsistencyClass
    isomorphism: IsomorphismClass
    corroboration: CorroborationClass
    structural_weight: float
    eligible_for_structural_gates: bool
    can_establish_pattern_alone: bool
    preserves_raw_testimony: bool = True
    open_contradiction: bool = False
    evolution_history: list[str] = field(default_factory=list)
    corroboration_anchors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    predictive_discrimination: Optional[PredictiveDiscriminationClass] = None
    prediction_preregistered: Optional[bool] = None
    three_confidences: Optional[dict[str, Optional[float]]] = None
    evidence_maturity: Optional[EvidenceMaturityLevel] = None
    entry_id: str = "SC-TIG-001"
    gate_number: int = 0

    @property
    def composite_classification(self) -> str:
        return f"{self.consistency.value} + {self.isomorphism.value} + {self.corroboration.value}"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "entry_id": self.entry_id,
            "gate_number": self.gate_number,
            "is_testimony": self.is_testimony,
            "consistency": self.consistency.value,
            "isomorphism": self.isomorphism.value,
            "corroboration": self.corroboration.value,
            "composite_classification": self.composite_classification,
            "structural_weight": self.structural_weight,
            "eligible_for_structural_gates": self.eligible_for_structural_gates,
            "can_establish_pattern_alone": self.can_establish_pattern_alone,
            "preserves_raw_testimony": self.preserves_raw_testimony,
            "open_contradiction": self.open_contradiction,
            "evolution_history": list(self.evolution_history),
            "corroboration_anchors": list(self.corroboration_anchors),
            "notes": list(self.notes),
        }
        if self.predictive_discrimination is not None:
            payload["predictive_discrimination"] = self.predictive_discrimination.value
            payload["prediction_preregistered"] = self.prediction_preregistered
        if self.three_confidences is not None:
            payload["three_confidences"] = dict(self.three_confidences)
        if self.evidence_maturity is not None:
            payload["evidence_maturity"] = self.evidence_maturity.value
        return payload


def evaluate_predictive_discrimination(
    *,
    preregistered_before_observation: bool,
    outcome_observed: Optional[bool] = None,
    distinguishes_from_competing_interpretations: bool = False,
) -> dict[str, Any]:
    """Evaluate TIG Check 4: Predictive Discrimination (V7 Part 33.1).

    Enforces the V7 pre-registration rule: a prediction written *after* the
    outcome is already known can never be scored ``DISCRIMINATING``.
    """
    if outcome_observed is None:
        state = PredictiveDiscriminationClass.PENDING
        reason = "Prediction recorded; test outcome not yet observed."
    elif outcome_observed is False:
        state = PredictiveDiscriminationClass.FAILED
        reason = "Pre-specified prediction was not observed."
    elif not preregistered_before_observation:
        state = PredictiveDiscriminationClass.NON_DISCRIMINATING
        reason = (
            "Post-hoc prediction written after observation cannot be scored DISCRIMINATING "
            "(V7 Part 33.1 pre-registration rule)."
        )
    elif distinguishes_from_competing_interpretations:
        state = PredictiveDiscriminationClass.DISCRIMINATING
        reason = "Pre-registered prediction distinguishes the interpretation from competing alternatives and was observed."
    else:
        state = PredictiveDiscriminationClass.NON_DISCRIMINATING
        reason = "Competing interpretations explain the same observed outcome equally."

    return {
        "check_number": 4,
        "check_name": "predictive_discrimination",
        "state": state.value,
        "preregistered_before_observation": bool(preregistered_before_observation),
        "outcome_observed": outcome_observed,
        "distinguishes_from_competing_interpretations": bool(distinguishes_from_competing_interpretations),
        "reason": reason,
    }


def _compute_structural_weight(
    consistency: ConsistencyClass,
    isomorphism: IsomorphismClass,
    corroboration: CorroborationClass,
) -> tuple[float, bool, bool]:
    """
    Compute structural evidence weight and gate eligibility from composite TIG classes.

    Returns:
        (structural_weight, eligible_for_structural_gates, can_establish_pattern_alone)
    """
    if consistency == ConsistencyClass.CONTRADICTED:
        return 0.0, False, False

    if isomorphism == IsomorphismClass.NARRATIVE:
        return 0.0, False, False

    iso_factor = 1.0 if isomorphism == IsomorphismClass.ISOMORPHIC else 0.6
    corr_factor = {
        CorroborationClass.ANCHORED: 1.0,
        CorroborationClass.PARTIALLY_ANCHORED: 0.85,
        CorroborationClass.UNANCHORED: 0.4,
    }[corroboration]

    weight = round(iso_factor * corr_factor, 4)
    eligible = True
    can_establish_alone = (
        isomorphism == IsomorphismClass.ISOMORPHIC
        and corroboration in (CorroborationClass.ANCHORED, CorroborationClass.PARTIALLY_ANCHORED)
    )
    return weight, eligible, can_establish_alone


def evaluate_testimony_integrity(
    claim_text: str,
    *,
    is_testimony: Optional[bool] = None,
    prior_statements: Optional[list[dict[str, Any]]] = None,
    raw_observations_consistent: bool = True,
    mutually_exclusive_claims: bool = False,
    framing_evolved: Optional[bool] = None,
    matched_pattern: Optional[str] = None,
    functional_mapping_holds: Optional[bool] = None,
    requires_unverified_assumption: Optional[bool] = None,
    corroboration_anchors: Optional[list[str]] = None,
    partial_anchoring: bool = False,
    preregistered_before_observation: Optional[bool] = None,
    prediction_outcome_observed: Optional[bool] = None,
    prediction_distinguishes_rivals: bool = False,
    structural_confidence: Optional[float] = None,
    empirical_confidence: Optional[float] = None,
    interpretive_confidence: Optional[float] = None,
    evidence_maturity: Optional[EvidenceMaturityLevel | str] = None,
) -> dict[str, Any]:
    """
    Run Gate 0 (Testimony Integrity Gate / SC-TIG-001) on a claim.

    The TIG classifies testimony across three axes:
        1. Consistency Vector (STABLE / EVOLVED / CONTRADICTED)
        2. Structural Isomorphism Check (ISOMORPHIC / ANALOGOUS / NARRATIVE)
        3. Corroboration Anchor (ANCHORED / PARTIALLY_ANCHORED / UNANCHORED)

    Nothing is dropped or invalidated — raw testimony is always preserved.
    """
    text = claim_text or ""
    notes: list[str] = []
    evolution_history: list[str] = []

    detected_testimony = any(p.search(text) for p in _FIRST_PERSON_TESTIMONY_PATTERNS)
    effective_is_testimony = detected_testimony if is_testimony is None else bool(is_testimony)

    # ── Gate 1: Consistency Vector ──
    if prior_statements:
        for stmt in prior_statements:
            framing = str(stmt.get("framing") or stmt.get("text") or "").strip()
            if framing:
                evolution_history.append(framing)
            if stmt.get("mutually_exclusive"):
                mutually_exclusive_claims = True
            if stmt.get("raw_observation_conflict"):
                raw_observations_consistent = False

    if mutually_exclusive_claims or not raw_observations_consistent:
        consistency = ConsistencyClass.CONTRADICTED
        notes.append(
            "Mutually exclusive claims detected; held as open question pending witness resolution."
        )
    elif framing_evolved or (
        len(evolution_history) >= 2 and len(set(evolution_history)) > 1
    ):
        consistency = ConsistencyClass.EVOLVED
        notes.append(
            "Raw observational data consistent across framings; current framing used with evolution history preserved."
        )
    else:
        consistency = ConsistencyClass.STABLE

    # ── Gate 2: Structural Isomorphism Check ──
    inferred_structural = bool(matched_pattern) or any(
        p.search(text) for p in _STRUCTURAL_PATTERN_PATTERNS
    )
    inferred_assumption = any(
        p.search(text) for p in _ATTRIBUTION_ASSUMPTION_PATTERNS
    )

    if functional_mapping_holds is False:
        isomorphism = IsomorphismClass.NARRATIVE
        notes.append(
            "Event does not map to a compiled pattern at the functional level; preserved as raw testimony."
        )
    elif functional_mapping_holds is True:
        if requires_unverified_assumption or inferred_assumption:
            isomorphism = IsomorphismClass.ANALOGOUS
            notes.append(
                "Functional structure partially maps, but causal/agent attribution requires assumptions beyond testimony."
            )
        else:
            isomorphism = IsomorphismClass.ISOMORPHIC
    else:
        if inferred_structural and (requires_unverified_assumption or inferred_assumption):
            isomorphism = IsomorphismClass.ANALOGOUS
            notes.append(
                "Causal attribution requires external corroboration; enters as supporting evidence."
            )
        elif inferred_structural:
            isomorphism = IsomorphismClass.ISOMORPHIC
        else:
            isomorphism = IsomorphismClass.NARRATIVE
            notes.append(
                "No functional structural mapping detected; remains in testimony corpus as raw data."
            )

    # ── Gate 3: Corroboration Anchor ──
    anchors = [str(a).strip() for a in (corroboration_anchors or []) if str(a).strip()]
    if not anchors:
        for pat in _ANCHOR_PATTERNS:
            for match in pat.finditer(text):
                token = match.group(0)
                if token not in anchors:
                    anchors.append(token)

    if anchors and not partial_anchoring and not (requires_unverified_assumption or inferred_assumption):
        corroboration = CorroborationClass.ANCHORED
    elif anchors or partial_anchoring:
        corroboration = CorroborationClass.PARTIALLY_ANCHORED
        notes.append(
            "Verifiable elements enter at full weight; perception-dependent attributions enter at reduced weight."
        )
    else:
        corroboration = CorroborationClass.UNANCHORED
        notes.append(
            "No independent external anchor provided; valid as converging evidence for established patterns only."
        )

    weight, eligible, can_establish_alone = _compute_structural_weight(
        consistency, isomorphism, corroboration
    )

    # ── Gate 4 (Optional, V7 Part 33.1): Predictive Discrimination ──
    pred_disc: Optional[PredictiveDiscriminationClass] = None
    if preregistered_before_observation is not None:
        pd_eval = evaluate_predictive_discrimination(
            preregistered_before_observation=preregistered_before_observation,
            outcome_observed=prediction_outcome_observed,
            distinguishes_from_competing_interpretations=prediction_distinguishes_rivals,
        )
        pred_disc = PredictiveDiscriminationClass(pd_eval["state"])
        notes.append(f"TIG Check 4 ({pred_disc.value}): {pd_eval['reason']}")

    # ── Three Separate Confidences (V7 Part 33.2: never collapsed into one number) ──
    three_conf: Optional[dict[str, Optional[float]]] = None
    if any(c is not None for c in (structural_confidence, empirical_confidence, interpretive_confidence)):
        three_conf = {
            "structural": structural_confidence,
            "empirical": empirical_confidence,
            "interpretive": interpretive_confidence,
        }

    # ── Evidence Maturity Ladder (V7 Part 33.3) ──
    maturity_enum: Optional[EvidenceMaturityLevel] = None
    if evidence_maturity is not None:
        maturity_enum = (
            evidence_maturity
            if isinstance(evidence_maturity, EvidenceMaturityLevel)
            else EvidenceMaturityLevel(str(evidence_maturity).strip().upper())
        )

    result = TIGClassification(
        is_testimony=effective_is_testimony,
        consistency=consistency,
        isomorphism=isomorphism,
        corroboration=corroboration,
        structural_weight=weight,
        eligible_for_structural_gates=eligible,
        can_establish_pattern_alone=can_establish_alone,
        preserves_raw_testimony=True,
        open_contradiction=(consistency == ConsistencyClass.CONTRADICTED),
        evolution_history=evolution_history,
        corroboration_anchors=anchors,
        notes=notes,
        predictive_discrimination=pred_disc,
        prediction_preregistered=preregistered_before_observation,
        three_confidences=three_conf,
        evidence_maturity=maturity_enum,
    )
    return result.to_dict()


def classify_packet_testimony(
    packet: SemanticPacket,
    context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Run Gate 0 (TIG) on a SemanticPacket as non-filtering pre-gate metadata.

    Reads optional structured TIG hints from ``context["tig"]`` when supplied,
    or evaluates ``packet.raw_input`` directly. Always preserves the packet and
    never blocks or deletes testimony.
    """
    tig_cfg = {}
    if isinstance(context, dict):
        if isinstance(context.get("tig"), dict):
            tig_cfg = context["tig"]
        elif context.get("source_type") == "testimony":
            tig_cfg = {"is_testimony": True}

    return evaluate_testimony_integrity(
        packet.raw_input or "",
        is_testimony=tig_cfg.get("is_testimony"),
        prior_statements=tig_cfg.get("prior_statements"),
        raw_observations_consistent=tig_cfg.get("raw_observations_consistent", True),
        mutually_exclusive_claims=tig_cfg.get("mutually_exclusive_claims", False),
        framing_evolved=tig_cfg.get("framing_evolved"),
        matched_pattern=tig_cfg.get("matched_pattern"),
        functional_mapping_holds=tig_cfg.get("functional_mapping_holds"),
        requires_unverified_assumption=tig_cfg.get("requires_unverified_assumption"),
        corroboration_anchors=tig_cfg.get("corroboration_anchors"),
        partial_anchoring=tig_cfg.get("partial_anchoring", False),
    )
