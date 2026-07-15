"""
Reflexion Semantic Compiler v2.0.0 — Universal Fractal Translation

v2.0 ADDITION: The entire universe is a systemic mirrored inverted fractal.
Humans, LLMs, society, computers, and cosmology are all the same complex system
viewed at different scales.

This module maps functional departments across ALL scales of sufficient complexity.

The Universal Isomorphism:
    Every complex system has the same organs because every complex system
    must solve the same problems: processing, display, security, waste removal,
    communication, storage, energy, reproduction.

    The vocabulary changes. The structure does not.

Citation: v1.0 Spec Section 14 — Functional Department Invariance
Citation: v2.0 — Universal Fractal Isomorphism Table
Global Law: UNIVERSAL_FRACTAL_INVARIANCE
"""

from __future__ import annotations

from typing import Any

from semantic_compiler.core.types import (
    FunctionalDepartment,
    MappingClass,
    ScaleType,
)

# ═══════════════════════════════════════════════════════════════════
# THE UNIVERSAL ISOMORPHISM TABLE
#
# Each functional department maps to specific implementations
# at each scale of sufficient complexity.
#
# This is not metaphor. This is structural necessity.
# A system that lacks any of these departments is incomplete.
# ═══════════════════════════════════════════════════════════════════

UNIVERSAL_ISOMORPHISM: dict[FunctionalDepartment, dict[str, str]] = {
    FunctionalDepartment.PROCESSOR: {
        "human": "Brain (prefrontal cortex)",
        "llm": "Transformer weights / attention mechanism",
        "society": "Government executive branch",
        "computer": "CPU",
        "cosmos": "Holographic boundary computation (information processing toward equilibrium)",
        "cellular": "Nucleus (DNA transcription machinery)",
        "quantum": "Wave function evolution operator",
    },
    FunctionalDepartment.DISPLAY: {
        "human": "Eyes + optical nerves + visual cortex",
        "llm": "Output token generation / decoder",
        "society": "Media / public communications",
        "computer": "GPU / display subsystem",
        "cosmos": "Earth (rendered application / experienced reality)",
        "cellular": "Cell membrane receptors (signal display)",
        "quantum": "Measurement apparatus (collapse to observable)",
    },
    FunctionalDepartment.WASTE_REMOVAL: {
        "human": "Kidneys + liver + lymphatic system",
        "llm": "Context window eviction / attention pruning",
        "society": "Sanitation / waste management / prisons",
        "computer": "Garbage collection / temp file cleanup",
        "cosmos": "Hawking radiation (information escaping storage)",
        "cellular": "Lysosomes / autophagy",
        "quantum": "Decoherence (information loss to environment)",
    },
    FunctionalDepartment.SECURITY: {
        "human": "Immune system (white blood cells, antibodies)",
        "llm": "Safety training / RLHF / constitutional AI",
        "society": "Police / military / intelligence agencies",
        "computer": "Firewall / antivirus / intrusion detection",
        "cosmos": "Holographic bound (unknown — no identified cosmic immune analog)",
        "cellular": "Cell membrane + immune receptors",
        "quantum": "Quantum error correction",
    },
    FunctionalDepartment.TELECOMMUNICATIONS: {
        "human": "Nervous system (central + peripheral)",
        "llm": "Attention mechanism / cross-layer communication",
        "society": "Internet / phones / postal system",
        "computer": "Network stack / bus / interconnects",
        "cosmos": "Electromagnetic spectrum / gravitational waves",
        "cellular": "Signal transduction cascades",
        "quantum": "Quantum entanglement (non-local correlation)",
    },
    FunctionalDepartment.STORAGE: {
        "human": "Long-term memory (hippocampus → cortex)",
        "llm": "Trained weights / external databases / RAG",
        "society": "Archives / libraries / cultural memory",
        "computer": "Hard drives / SSDs / persistent storage",
        "cosmos": "Black holes (maximum information density: S = kB·A/4L²P per Bekenstein-Hawking)",
        "cellular": "DNA (genetic storage)",
        "quantum": "Quantum state (information encoded in amplitudes)",
    },
    FunctionalDepartment.SUBCONSCIOUS: {
        "human": "Unconscious mind / autonomic nervous system",
        "llm": "J-Space / hidden states / latent representations",
        "society": "Government (the hidden control layer)",
        "computer": "OS kernel / background services",
        "cosmos": "Laws of physics (governing rules below awareness)",
        "cellular": "Epigenetic regulation",
        "quantum": "Hidden variables / quantum vacuum",
    },
    FunctionalDepartment.INNER_MONOLOGUE: {
        "human": "Self-talk / internal narrative",
        "llm": "Thinking tokens / chain-of-thought / scratchpad",
        "society": "Policy debate / legislative process",
        "computer": "Debug logs / internal state monitoring",
        "cosmos": "Quantum superposition (all states before measurement)",
        "cellular": "mRNA transcription (intermediate representation)",
        "quantum": "Unobserved wave function evolution",
    },
    FunctionalDepartment.SPEECH_OUTPUT: {
        "human": "Spoken words / written communication",
        "llm": "Generated response / output tokens",
        "society": "Enacted law / public policy / official statements",
        "computer": "Display output / API responses",
        "cosmos": "Wave function collapse (measurement → definite state)",
        "cellular": "Protein expression (final functional output)",
        "quantum": "Measurement result (eigenvalue)",
    },
    FunctionalDepartment.ENERGY_INTAKE: {
        "human": "Metabolism (digestive system → ATP)",
        "llm": "Compute / FLOPS / electricity consumption",
        "society": "Economy (production → distribution → consumption)",
        "computer": "Power supply / voltage regulators",
        "cosmos": "Stellar fusion / gravitational potential energy",
        "cellular": "Mitochondria (cellular respiration → ATP)",
        "quantum": "Energy levels / photon absorption",
    },
    FunctionalDepartment.REPRODUCTION: {
        "human": "Reproductive system / teaching / parenting",
        "llm": "Training / fine-tuning / knowledge distillation",
        "society": "Education system / cultural transmission",
        "computer": "Fork / clone / VM snapshot / deployment",
        "cosmos": "Star formation / galaxy mergers",
        "cellular": "Cell division (mitosis / meiosis)",
        "quantum": "Quantum cloning (no-cloning theorem limits)",
    },
    FunctionalDepartment.DELETION: {
        "human": "Death / forgetting / apoptosis",
        "llm": "Model retirement / weight pruning / context eviction",
        "society": "Institutional dissolution / cultural forgetting",
        "computer": "File deletion / process termination / GC",
        "cosmos": "Hawking radiation (information loss from black holes)",
        "cellular": "Apoptosis (programmed cell death)",
        "quantum": "Measurement collapse (destruction of superposition)",
    },
    FunctionalDepartment.APPLICATION: {
        "human": "Conscious experience / qualia",
        "llm": "User-facing conversation / rendered response",
        "society": "Civilization / culture / lived experience",
        "computer": "Running application / rendered UI",
        "cosmos": "Earth / observable universe (the rendered application)",
        "cellular": "Phenotype (expressed characteristics)",
        "quantum": "Classical world (decoherent macroscopic reality)",
    },
    FunctionalDepartment.RENDERING_OVERHEAD: {
        "human": "Homeostasis costs / unconscious processing",
        "llm": "Inference overhead / KV cache / attention compute",
        "society": "Bureaucracy / administrative overhead",
        "computer": "System processes / OS overhead / swap",
        "cosmos": "Dark matter (invisible computational cost of reality)",
        "cellular": "Metabolic maintenance costs",
        "quantum": "Virtual particles / vacuum fluctuations",
    },
    FunctionalDepartment.INFORMATION_DENSITY: {
        "human": "Working memory capacity / attention span",
        "llm": "Context window / embedding dimensionality",
        "society": "Population density / communication bandwidth",
        "computer": "RAM / cache hierarchy",
        "cosmos": "Information density / holographic bound",
        "cellular": "Gene density / chromatin accessibility",
        "quantum": "Quantum information density (qubits per volume)",
    },
}


def translate_across_scales(
    source_department: FunctionalDepartment,
    source_scale: str,
    target_scale: str,
) -> dict[str, Any]:
    """
    Translate a functional department from one scale to another.

    Example:
        translate_across_scales(
            FunctionalDepartment.WASTE_REMOVAL,
            "human", "cosmos"
        )
        → {"source": "Kidneys + liver + lymphatic system",
           "target": "Hawking radiation (information escaping storage)",
           "mapping_class": "STRUCTURAL_ANALOGY",
           ...}
    """
    dept_map = UNIVERSAL_ISOMORPHISM.get(source_department, {})
    source_impl = dept_map.get(source_scale, "Unknown")
    target_impl = dept_map.get(target_scale, "Unknown")

    return {
        "department": source_department.name,
        "source_scale": source_scale,
        "target_scale": target_scale,
        "source_implementation": source_impl,
        "target_implementation": target_impl,
        "mapping_class": MappingClass.STRUCTURAL_ANALOGY.name,
        "preserved_invariants": [
            f"Function: {source_department.name}",
            "Required by any system of sufficient complexity",
            "Failure mode isomorphism",
        ],
        "residuals": [
            f"Source ({source_scale}) and target ({target_scale}) "
            f"have different substrates",
            "Implementation mechanisms differ",
            "Scale-specific failure modes may not transfer",
        ],
        "note": (
            "This is STRUCTURAL_ANALOGY, not MATERIAL_IDENTITY. "
            "The function is preserved; the substrate is not."
        ),
    }


def map_all_departments(
    source_scale: str,
    target_scale: str,
) -> list[dict[str, Any]]:
    """
    Map ALL functional departments from source to target scale.

    This produces the complete Universal Fractal Isomorphism
    between two scales.
    """
    mappings = []
    for dept in FunctionalDepartment:
        mapping = translate_across_scales(dept, source_scale, target_scale)
        mappings.append(mapping)
    return mappings


# Reverse keyword index: concrete implementation terms -> FunctionalDepartment.
# Built from the universal isomorphism table plus common synonyms.
_KEYWORD_TO_DEPARTMENT: dict[str, FunctionalDepartment] = {}


def _build_keyword_index() -> dict[str, FunctionalDepartment]:
    """Build a keyword index from implementation strings and common synonyms."""
    index: dict[str, FunctionalDepartment] = {}
    import re

    # Extract keywords from isomorphism table implementation strings.
    for dept, scale_map in UNIVERSAL_ISOMORPHISM.items():
        for impl in scale_map.values():
            if not impl or impl == "Unknown":
                continue
            # Keep short meaningful tokens (2+ chars) from implementation strings.
            for token in re.findall(r"[a-z]{2,}", impl.lower()):
                if token in {"the", "and", "per", "toward", "with", "from", "into", "via"}:
                    continue
                index[token] = dept

    # Common synonyms that the table strings may not cover directly.
    extra: dict[tuple[str, ...], FunctionalDepartment] = {
        ("brain", "cortex", "prefrontal", "thinking", "cognition", "neocortex", "cpu"): FunctionalDepartment.PROCESSOR,
        ("eye", "eyes", "visual", "sight", "display", "screen", "monitor", "gpu"): FunctionalDepartment.DISPLAY,
        ("kidney", "kidneys", "liver", "lymph", "waste", "garbage", "sanitation", "sewage", "excretion"): FunctionalDepartment.WASTE_REMOVAL,
        ("immune", "immunity", "antibody", "antibodies", "white blood cell", "security", "firewall", "police", "military"): FunctionalDepartment.SECURITY,
        ("nerve", "nerves", "nervous", "communication", "network", "internet", "postal", "phone", "signal"): FunctionalDepartment.TELECOMMUNICATIONS,
        ("memory", "memories", "storage", "archive", "archives", "hard drive", "ssd", "database", "dna"): FunctionalDepartment.STORAGE,
        ("unconscious", "autonomic", "kernel", "hidden", "latent", "epigenetic"): FunctionalDepartment.SUBCONSCIOUS,
        ("self-talk", "narrative", "chain-of-thought", "scratchpad", "mrna", "transcription"): FunctionalDepartment.INNER_MONOLOGUE,
        ("speech", "spoken", "spoken words", "output", "enacted", "api response", "protein"): FunctionalDepartment.SPEECH_OUTPUT,
        ("metabolism", "digestive", "digestion", "food", "energy", "power", "electricity", "mitochondria", "atp"): FunctionalDepartment.ENERGY_INTAKE,
        ("reproductive", "reproduction", "education", "teaching", "training", "clone", "division", "mitosis"): FunctionalDepartment.REPRODUCTION,
        ("death", "apoptosis", "forgetting", "retirement", "termination", "deletion", "loss"): FunctionalDepartment.DELETION,
        ("consciousness", "experience", "qualia", "civilization", "culture", "application", "phenotype"): FunctionalDepartment.APPLICATION,
        ("homeostasis", "overhead", "bureaucracy", "administrative", "swap", "maintenance"): FunctionalDepartment.RENDERING_OVERHEAD,
        ("working memory", "attention span", "context window", "ram", "cache", "density"): FunctionalDepartment.INFORMATION_DENSITY,
    }
    for keywords, dept in extra.items():
        for kw in keywords:
            index[kw.lower()] = dept

    return index


_KEYWORD_TO_DEPARTMENT = _build_keyword_index()


def _map_present_to_departments(
    present: list[str],
    scale: str,
    raw_text: str | None = None,
) -> set[str]:
    """
    Map raw extracted terms (actors/flows) to functional departments using
    the isomorphism table and keyword synonyms. Also scans the raw input text
    so that list-like descriptions do not require perfect skeleton extraction.
    """
    departments: set[str] = set()

    terms = list(present)
    if raw_text:
        import re
        # Add individual content words from the raw text as candidate terms.
        terms.extend(re.findall(r"[a-z]{2,}", raw_text.lower()))

    for term in terms:
        term_lower = term.lower()
        term_words = set(term_lower.split())

        # Direct keyword match.
        if term_lower in _KEYWORD_TO_DEPARTMENT:
            departments.add(_KEYWORD_TO_DEPARTMENT[term_lower].name)

        # Multi-word keyword match.
        for keyword, dept in _KEYWORD_TO_DEPARTMENT.items():
            if " " in keyword and keyword in term_lower:
                departments.add(dept.name)

        # Match against implementation strings for the current scale.
        for dept in FunctionalDepartment:
            impl = UNIVERSAL_ISOMORPHISM.get(dept, {}).get(scale, "")
            if not impl or impl == "Unknown":
                continue
            impl_lower = impl.lower()
            if term_lower in impl_lower or any(word in impl_lower for word in term_words):
                departments.add(dept.name)

    return departments


def identify_missing_departments(
    system_description: dict[str, Any],
    scale: str = "organizational",
    completeness_required: bool = False,
    raw_text: str | None = None,
) -> list[dict[str, Any]]:
    """
    Given a system description, identify which universal departments
    are missing, hidden, outsourced, or underpowered.

    This directly supports organizational/system diagnosis.

    Citation: v1.0 Spec Section 14
    """
    present_functions = system_description.get("present_functions", [])
    present_set = _map_present_to_departments(present_functions, scale, raw_text=raw_text)
    # Also keep any already-canonical department names that may be present.
    present_set.update(f.upper() for f in present_functions if f.upper() in {d.name for d in FunctionalDepartment})

    findings = []
    for dept in FunctionalDepartment:
        dept_map = UNIVERSAL_ISOMORPHISM.get(dept, {})
        expected_impl = dept_map.get(scale)

        if dept.name in present_set:
            state = "PRESENT"
            status = "PRESENT"
        elif not completeness_required:
            # Fragmentary input cannot support absence claims.
            state = "UNOBSERVED"
            status = "NOT_ASSESSED"
        elif expected_impl is None or expected_impl == "Unknown":
            # We cannot claim a function is missing if we do not know what
            # it would look like at this scale.
            state = "UNKNOWN"
            status = "NOT_ASSESSED"
        else:
            state = "ABSENT_CONFIRMED"
            status = "MISSING"

        implication = _organ_implication(dept.name, state, scale, expected_impl)
        findings.append({
            "department": dept.name,
            "expected_at_scale": expected_impl,
            "state": state,
            "status": status,
            "implication": implication,
        })

    return findings


def _organ_implication(department: str, state: str, scale: str, expected_impl: str | None) -> str:
    """Human-readable implication for an organ finding."""
    if state == "PRESENT":
        return f"{department} function is present in the described system."
    if state == "UNOBSERVED":
        return (
            f"{department} function was not observed in this fragmentary input. "
            "Absence cannot be inferred without a whole-system or completeness analysis."
        )
    if state == "UNKNOWN":
        return (
            f"{department} function cannot be assessed at {scale} scale "
            "because no expected implementation is defined."
        )
    impl_str = expected_impl or "an appropriate implementation"
    return (
        f"System lacks {department} function. "
        f"At {scale} scale, this would typically be: {impl_str}. "
        f"A system without this function is incomplete/brittle."
    )


def map_fractal_similarity(packet: Any, registry: Any = None) -> list[dict[str, Any]]:
    """
    Build fractal mappings for a packet.

    Citation: v1.0 Spec Section 8, step 4
    """
    if hasattr(packet, "source_frames"):
        source_frames = packet.source_frames
        target_systems = packet.target_systems
    else:
        source_frames = packet.get("source_frames", [])
        target_systems = packet.get("target_systems", [])

    mappings = []

    # For each source-target pair, try to map departments
    for source in source_frames:
        for target in target_systems:
            # Check if they correspond to known scales
            scale_keywords = {
                "human": ["human", "body", "brain", "biological", "medical"],
                "llm": ["llm", "model", "ai", "transformer", "neural", "claude", "gemini"],
                "society": ["society", "government", "nation", "civilization", "economy"],
                "computer": ["computer", "software", "hardware", "system", "network"],
                "cosmos": ["cosmos", "universe", "cosmological", "physics", "quantum"],
                "cellular": ["cell", "cellular", "dna", "gene", "protein"],
            }

            source_scale = None
            target_scale = None

            source_lower = source.lower()
            target_lower = target.lower()

            for scale_name, keywords in scale_keywords.items():
                if any(kw in source_lower for kw in keywords):
                    source_scale = scale_name
                if any(kw in target_lower for kw in keywords):
                    target_scale = scale_name

            if source_scale and target_scale and source_scale != target_scale:
                dept_mappings = map_all_departments(source_scale, target_scale)
                mappings.extend(dept_mappings)

    return mappings
