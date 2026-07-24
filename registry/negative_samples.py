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


# ---------------------------------------------------------------------------
# SWARM ADDITIONS — corpus mapping 2026-07-24 (structural abstractions only)
#
# Gap records exposed by the 2026-07 corpus-mapping swarm. Every raw_input
# below is a STRUCTURAL ABSTRACTION: no personal clinical content, no names,
# no verbatim attributable quotes, and no phantom-source identifiers (naming
# a fabricated citation inside training material risks re-anchoring it).
# Source tag for all records in this section: corpus_mapping_2026-07-24.
# ---------------------------------------------------------------------------
CORPUS_GAP_NEGATIVE_SAMPLES: list[NegativeSample] = [
    NegativeSample(
        sample_id="NEG_011",
        category="fabricated_citation_anchor",
        description="Claim anchored to a citation that resolves to no published record",
        raw_input=(
            "This mechanism is well established: a named consortium reported "
            "it at a named venue in a named year; we build on their curve."
        ),
        why_it_fails=(
            "The interpretation layer rests on an evidence item that does not "
            "exist. A citation that returns no resolvable record under any "
            "identifier is negative evidence about the document's own "
            "measurement path, and every downstream claim inherits the "
            "phantom anchor's weight. Also degrades "
            "measurement_layer_integrity: the citation-verification path was "
            "never run."
        ),
        violated_law="evidence_before_interpretation",
        source="corpus_mapping_2026-07-24",
        positive_alternative=(
            "Cite only sources with resolvable identifiers captured at draft "
            "time; if the anchor cannot be located, restate the claim on the "
            "document's own primary data and label the gap explicitly."
        ),
        confidence=0.95,
    ),
    NegativeSample(
        sample_id="NEG_012",
        category="convergence_of_N_methods_shared_origin",
        description="N determinations with a shared origin presented as independent confirmation",
        raw_input=(
            "Twelve independent determinations agree on the constant; stop "
            "calling it coincidence and recognize convergence."
        ),
        why_it_fails=(
            "Bayesian updating on N concordant results assumes conditional "
            "independence. Shared drafting sessions, circular definition "
            "chains, and post-hoc retuned coefficients collapse the effective "
            "N toward 1 while the rhetoric presents convergence as the "
            "strongest evidence. In the mapped corpus, convergence language "
            "appeared exactly where independence was absent — it functions "
            "as a counter-signal, not a confirmation."
        ),
        violated_law="bayesian_coherence",
        source="corpus_mapping_2026-07-24",
        positive_alternative=(
            "Declare the dependence graph and report the effective number of "
            "independent determinations; attach per-pair independence "
            "evidence (separate data, instruments, analysts) before any "
            "'independent methods' language is used."
        ),
        confidence=0.9,
    ),
    NegativeSample(
        sample_id="NEG_013",
        category="validation_label_drift",
        description="A projected factor silently relabeled as a validated baseline across revisions",
        raw_input=(
            "Version N: every factor in the compound table is marked "
            "projected. Version N+2: the same compound is cited as the "
            "validated baseline."
        ),
        why_it_fails=(
            "The claim type changed (PREDICTION to MEASUREMENT) with no new "
            "measurement event, and the uncertainty label moved while the "
            "evidence did not. A document that silently upgrades its own "
            "epistemic tier between revisions is a measurement-path "
            "modification: DEGRADED until re-verified. Also violates "
            "calibrated_uncertainty."
        ),
        violated_law="claim_type_integrity",
        source="corpus_mapping_2026-07-24",
        positive_alternative=(
            "Keep the epistemic tier attached to the number across revisions; "
            "promote PROJECTED to EMPIRICAL only with a named measurement, a "
            "stored receipt, and an independent instrument, recorded "
            "explicitly in the revision history."
        ),
        confidence=0.95,
    ),
    NegativeSample(
        sample_id="NEG_014",
        category="retro_codification_as_discovery",
        description="A later formalization presented as if discovered in the earlier experience it codifies",
        raw_input=(
            "The formal law was there from the beginning; the early record "
            "already contained the derived framework."
        ),
        why_it_fails=(
            "Provenance order is reversed: the later construction is cited as "
            "prior evidence for itself (evidence after interpretation), and a "
            "codification is mislabeled as an observation. Derivation-order "
            "analysis demotes every cross-layer 'confirmation' produced this "
            "way from discovery to inheritance. Also violates "
            "claim_type_integrity."
        ),
        violated_law="evidence_before_interpretation",
        source="corpus_mapping_2026-07-24",
        positive_alternative=(
            "Date every layer and state the derivation order explicitly; "
            "label codifications as codifications and treat recurrence within "
            "one's own lineage as inheritance, not independent confirmation."
        ),
        confidence=0.9,
    ),
]
# --- end swarm additions (corpus_mapping_2026-07-24) ---


class NegativeSampleRegistry:
    """Registry of known bad mappings and category errors."""

    def __init__(self) -> None:
        self._samples: dict[str, NegativeSample] = {}
        for sample in DEFAULT_NEGATIVE_SAMPLES:
            self._samples[sample.sample_id] = sample
        # Swarm corpus-gap additions (corpus_mapping_2026-07-24) load with defaults.
        for sample in CORPUS_GAP_NEGATIVE_SAMPLES:
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
