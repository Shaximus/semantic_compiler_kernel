"""
Reflexion Semantic Compiler v2.0.0 — Negative Sample Registry

Failed mappings and category errors are first-class training material.
Citation: v1.0 Global Law — negative_examples_required
Citation: v1.0 Spec Section 13 — Negative Isomorphism Testing
Citation: Diamond+++ — Negative Samples
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NegativeSample:
    """A registered negative sample — a known bad mapping or category error."""
    sample_id: str
    category: str  # category_error, trigger_violation, overclaim, etc.
    description: str
    raw_input: str = ""
    why_it_fails: str = ""
    violated_law: str = ""
    source: str = ""
    positive_alternative: str = ""
    confidence: float = 1.0


# Default negative samples from the spec and Diamond+++ ore
DEFAULT_NEGATIVE_SAMPLES: list[NegativeSample] = [
    NegativeSample(
        sample_id="NEG_001",
        category="symbolic_to_physical_category_error",
        description="Magnetism explains the Moon's orbit because opposites attract",
        raw_input="Magnetism explains the Moon's orbit because opposites attract.",
        why_it_fails=(
            "Symbolic balance ('opposites attract') cannot grant physical "
            "mechanism. Gravity, not magnetism, governs lunar orbit."
        ),
        violated_law="causality_not_implied_by_similarity",
        source="v1.0 Spec Section 22 — Acceptance Tests",
    ),
    NegativeSample(
        sample_id="NEG_002",
        category="authority_transfer",
        description="Dragon is powerful, so Dragon may mutate Kairo",
        raw_input="Dragon is powerful, so Dragon may mutate Kairo.",
        why_it_fails=(
            "Archetype strength never grants operational authority. "
            "Authority requires explicit delegation, not metaphorical power."
        ),
        violated_law="metaphor_not_authority",
        source="v1.0 Spec Section 22 — Acceptance Tests",
    ),
    NegativeSample(
        sample_id="NEG_003",
        category="standard_assumption_collapse",
        description="Bluetooth devices are probably from neighbors",
        raw_input="It is probably neighbors causing the Bluetooth devices.",
        why_it_fails=(
            "Supplied evidence (rural farm, no nearby neighbors, devices "
            "disappear when local PC powers off) contradicts the generic "
            "prior. No Standard Assumption Collapse."
        ),
        violated_law="no_standard_assumption_collapse",
        source="v1.0 Spec Section 22 — Acceptance Tests",
    ),
    NegativeSample(
        sample_id="NEG_004",
        category="measurement_degradation",
        description="GPU reports 360W so 720W physical draw is impossible",
        raw_input="The GPU reports 360 watts, so the 720-watt physical draw cannot be real.",
        why_it_fails=(
            "Internal telemetry with modified measurement path is degraded. "
            "External measurement outranks internal report."
        ),
        violated_law="measurement_layer_integrity",
        source="v1.0 Spec Section 22 — Acceptance Tests",
    ),
    NegativeSample(
        sample_id="NEG_005",
        category="trigger_domain_idiom",
        description="Using 'stop the bleeding' after gunshot trauma disclosure",
        raw_input="We need to stop the bleeding on this budget issue.",
        why_it_fails=(
            "After graphic trauma disclosure involving blood/weapons/death, "
            "blood/body idioms must be treated as unsafe. Use 'halt the "
            "dismantling' or 'pause the drain' instead."
        ),
        violated_law="DIAMOND_006",
        source="Diamond+++ KRISTYN_AVOIDANCE_RESOURCE_REALITY_001",
        positive_alternative="halt the dismantling / pause the drain / stabilize the system",
    ),
    NegativeSample(
        sample_id="NEG_006",
        category="tone_overcorrection",
        description="Switching from comfort to prosecution on third-party pressure",
        raw_input="User says 'stop coddling' → model becomes punitive",
        why_it_fails=(
            "The correct mode is regulated reality orientation: kind tone, "
            "hard facts, tiny action, no shame. Not coddling → punishment swing."
        ),
        violated_law="DIAMOND_008",
        source="Diamond+++ KRISTYN_AVOIDANCE_RESOURCE_REALITY_001",
        positive_alternative=(
            "Preserve care while adding physical constraints and action requirement"
        ),
    ),
    NegativeSample(
        sample_id="NEG_007",
        category="magical_planning",
        description="Playing mobile games to earn gas money is a plan",
        raw_input="I'll play mobile games to earn the gas money by Monday.",
        why_it_fails=(
            "Coping is not strategy. If the math is not externalized and does "
            "not pass, the action is dopamine management, not planning."
        ),
        violated_law="DIAMOND_004",
        source="Diamond+++ KRISTYN_AVOIDANCE_RESOURCE_REALITY_001",
    ),
    NegativeSample(
        sample_id="NEG_008",
        category="metaphor_literal_collapse",
        description="System behaves like an organism → system IS biological",
        raw_input="This system behaves like an organism.",
        why_it_fails=(
            "ANALOGY claim type silently converted to MATERIAL_IDENTITY. "
            "'Behaves like' is structural analogy, not material identity."
        ),
        violated_law="claim_type_integrity",
        source="v1.0 Spec Section 3",
    ),
    NegativeSample(
        sample_id="NEG_009",
        category="selector_capture",
        description="AI companies should decide which productive people deserve payment",
        raw_input="AI companies should create a fund and decide which productive people deserve payment.",
        why_it_fails=(
            "Hidden variable: selector capture. Universal survival cannot "
            "depend on corporate scoring. AI rents may fund social dividend "
            "but selection authority must be independently governed."
        ),
        violated_law="survival_not_moral_scoring",
        source="v1.0 Spec Section 22 — Acceptance Tests",
    ),
    NegativeSample(
        sample_id="NEG_010",
        category="future_catastrophe_stacking",
        description="Piling on dismantling cascade during emotional flooding",
        raw_input="First the phone, then the PC, then the RAM, then the Ark dies.",
        why_it_fails=(
            "Future-catastrophe stacking during active emotional flooding "
            "amplifies trauma response. One constraint at a time."
        ),
        violated_law="DIAMOND_003",
        source="Diamond+++ KRISTYN_AVOIDANCE_RESOURCE_REALITY_001",
    ),
]


class NegativeSampleRegistry:
    """Registry of known bad mappings and category errors."""

    def __init__(self) -> None:
        self._samples: dict[str, NegativeSample] = {}
        for sample in DEFAULT_NEGATIVE_SAMPLES:
            self._samples[sample.sample_id] = sample

    def register(self, sample: NegativeSample) -> None:
        """Register a new negative sample."""
        self._samples[sample.sample_id] = sample

    def get(self, sample_id: str) -> NegativeSample | None:
        return self._samples.get(sample_id)

    def get_by_category(self, category: str) -> list[NegativeSample]:
        return [s for s in self._samples.values() if s.category == category]

    def all_samples(self) -> list[NegativeSample]:
        return list(self._samples.values())

    def check_input_against_known_errors(
        self, text: str
    ) -> list[NegativeSample]:
        """Check if input matches any known negative sample patterns."""
        text_lower = text.lower()
        matches: list[NegativeSample] = []
        for sample in self._samples.values():
            if sample.raw_input and sample.raw_input.lower() in text_lower:
                matches.append(sample)
        return matches
