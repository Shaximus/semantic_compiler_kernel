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

import re
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


# ---------------------------------------------------------------------------
# Scale vocabulary
# ---------------------------------------------------------------------------

# Single source of truth for "which scale does this frame name belong to".
# ``core.pipeline._infer_system_scale`` and ``map_fractal_similarity`` used to
# keep separate, divergent copies. The frame detector emits names such as
# "biology", "computation", "organizational", "economic" and "reflexion", but
# the keyword table in ``map_fractal_similarity`` matched none of them, so almost
# every frame pair silently produced zero fractal mappings.
FRAME_TO_SCALE: dict[str, str] = {
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

# Legacy free-text keyword fallback for frame names not in FRAME_TO_SCALE.
_SCALE_KEYWORDS: dict[str, list[str]] = {
    "human": ["human", "body", "brain", "biological", "medical"],
    "llm": ["llm", "model", "ai", "transformer", "neural", "claude", "gemini"],
    "society": ["society", "government", "nation", "civilization", "economy"],
    "computer": ["computer", "software", "hardware", "system", "network"],
    "cosmos": ["cosmos", "universe", "cosmological", "physics", "quantum"],
    "cellular": ["cell", "cellular", "dna", "gene", "protein"],
}


def scale_for_frame(frame: str | None) -> str | None:
    """Resolve a frame/target name to a canonical scale, or None."""
    if not frame:
        return None
    key = frame.strip().rstrip("?").lower()
    if key in FRAME_TO_SCALE:
        return FRAME_TO_SCALE[key]
    for scale_name, keywords in _SCALE_KEYWORDS.items():
        # Whole-word match: "ai" must not match "chain" or "domain".
        if any(re.search(rf"(?<![a-z]){re.escape(kw)}(?![a-z])", key) for kw in keywords):
            return scale_name
    return None


def _legacy_scale_for_frame(frame: str) -> str | None:
    """V3.0.0 behaviour: substring keyword match, last matching scale wins."""
    lowered = frame.lower()
    scale = None
    for scale_name, keywords in _SCALE_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            scale = scale_name
    return scale


# ---------------------------------------------------------------------------
# Department presence detection
# ---------------------------------------------------------------------------
#
# Maps free text to the functional departments it gives evidence for. Earlier
# versions substring-matched every word of the raw input against every
# implementation string, so function words ("in", "of", "to") and the system's
# own name ("cell" in "A cell has a nucleus") marked most departments PRESENT,
# which defeated missing-organ detection whenever raw text was supplied. On the
# shipped labeled benchmark that cost 16 of 82 absences (recall 0.805).
#
# Evidence, strongest first (all matching is whole-token, plural-folded):
#   1. Phrase evidence: a table segment of the department at the ACTIVE scale
#      ("attention mechanism", "trained weights", "cell membrane") appears as a
#      contiguous phrase. A phrase shared by several departments is evidence
#      for each of them. A one-word segment counts only if no other department
#      lists that word at this scale.
#   2. Curated synonyms (scale independent): "terminator" -> DELETION, ...
#   3. Token evidence for words left over: a word that several departments list
#      resolves to the FIRST-listed department at the scale (PROCESSOR is
#      listed first). This keeps "A society has a government" from also
#      marking SUBCONSCIOUS, whose table entry is also "Government".
#   4. Never evidence: function words, generic table words, the system's own
#      name at the active scale, and anything inside a negation window
#      ("no CPU", "without a firewall").

_STOPWORDS = frozenset(
    "the and per toward with from into via of to in or is as by at on it an be no not "
    "for a are was were has have had there their its this that these those which what "
    "who but if then than so such can will would could should may might must also only "
    "just very more most some any all each other both one two three include includes "
    "included including contain contains consist consists system systems function "
    "functions state states information process processes mechanism structure layer "
    "level data unit part parts type types kind kinds".split()
)

# Words that name the system itself at a given scale; mentioning the system is
# not evidence that any particular organ exists.
_SCALE_SELF_TOKENS: dict[str, frozenset[str]] = {
    "human": frozenset({"human", "body", "person"}),
    "llm": frozenset({"llm", "model", "ai"}),
    "society": frozenset({"society", "societie"}),
    "computer": frozenset({"computer", "machine"}),
    "cosmos": frozenset({"cosmos", "universe"}),
    "cellular": frozenset({"cell", "cellular"}),
    "quantum": frozenset({"quantum"}),
}

_NEGATORS = frozenset({
    "no", "not", "without", "lacks", "lack", "lacking", "missing", "absent",
    "never", "nor", "neither", "nothing", "cannot",
})
_NEGATION_RESET = frozenset({"but", "however", "although", "though", "yet", "while", "whereas"})
_NEGATION_WINDOW = 4

# Two-letter table tokens that are real acronyms (everything else needs 3+ letters).
_SHORT_TOKENS = frozenset({"os", "gc"})

_TOKEN_RE = re.compile(r"[a-z]+(?:-[a-z]+)*")
_SEGMENT_SPLIT_RE = re.compile(r"\s*(?:/|\+|→|,|;|—)\s*")


def _stem(token: str) -> str:
    """Cheap plural folding: kidneys->kidney, antibodies->antibody, weights->weight."""
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us")):
        return token[:-1]
    return token


def _usable_token(token: str) -> bool:
    if token in _STOPWORDS:
        return False
    return len(token) >= 3 or token in _SHORT_TOKENS


# Curated single-word synonyms -> FunctionalDepartment.
_KEYWORD_TO_DEPARTMENT: dict[str, FunctionalDepartment] = {}
# Curated multi-word / hyphenated synonyms.
_PHRASE_TO_DEPARTMENT: dict[str, FunctionalDepartment] = {}
# scale -> list of (department, segment tokens, is_head) from the table, in table order.
_SEGMENTS: dict[str, list[tuple[FunctionalDepartment, tuple[str, ...], bool]]] = {}
# scale -> head token -> departments listing it, in table order.
_HEAD_TOKEN_DEPARTMENTS: dict[str, dict[str, list[FunctionalDepartment]]] = {}


def _build_keyword_index() -> dict[str, FunctionalDepartment]:
    """Build the curated synonym indexes (single words returned; phrases populated)."""
    index: dict[str, FunctionalDepartment] = {}

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
        # "terminator"/"terminate"/"retire" cover agentive and verb forms of the
        # table's "termination"/"retirement" ("process terminator", "model retired").
        ("death", "apoptosis", "forgetting", "retirement", "retire", "retired", "termination",
         "terminator", "terminate", "deletion", "loss"): FunctionalDepartment.DELETION,
        ("consciousness", "experience", "qualia", "civilization", "culture", "application", "phenotype"): FunctionalDepartment.APPLICATION,
        ("homeostasis", "overhead", "bureaucracy", "administrative", "swap", "maintenance"): FunctionalDepartment.RENDERING_OVERHEAD,
        ("working memory", "attention span", "context window", "ram", "cache", "density"): FunctionalDepartment.INFORMATION_DENSITY,
    }
    for keywords, dept in extra.items():
        for kw in keywords:
            kw = kw.lower()
            if " " in kw or "-" in kw:
                _PHRASE_TO_DEPARTMENT[kw] = dept
            else:
                index[kw] = dept
    return index


def _segment_tokens(text: str) -> tuple[str, ...]:
    return tuple(_stem(tok) for tok in _TOKEN_RE.findall(text.lower()))


def _build_table_index() -> None:
    """Split every implementation string into head and gloss segments, per scale.

    "Hawking radiation (information escaping storage)" has the head segment
    "hawking radiation" and the gloss segment "information escaping storage".
    Only head words may act as single-token evidence; a gloss is explanatory
    prose, so only its multi-word phrases count.
    """
    for dept, scale_map in UNIVERSAL_ISOMORPHISM.items():
        for scale, impl in scale_map.items():
            if not impl or impl == "Unknown":
                continue
            head, _, rest = impl.partition("(")
            gloss = rest.rsplit(")", 1)[0] if rest else ""
            segments = _SEGMENTS.setdefault(scale, [])
            head_tokens = _HEAD_TOKEN_DEPARTMENTS.setdefault(scale, {})
            for is_head, chunk in ((True, head), (False, gloss)):
                for part in _SEGMENT_SPLIT_RE.split(chunk):
                    tokens = _segment_tokens(part)
                    if not tokens:
                        continue
                    segments.append((dept, tokens, is_head))
                    if is_head:
                        for token in tokens:
                            if _usable_token(token):
                                owners = head_tokens.setdefault(token, [])
                                if dept not in owners:
                                    owners.append(dept)


_KEYWORD_TO_DEPARTMENT = _build_keyword_index()
_build_table_index()


def _tokens_with_negation(sentence: str) -> list[tuple[str, bool]]:
    """Tokenize a sentence, flagging tokens inside a negation window."""
    tokens: list[tuple[str, bool]] = []
    remaining = 0
    for token in _TOKEN_RE.findall(sentence):
        if token in _NEGATORS:
            remaining = _NEGATION_WINDOW
            tokens.append((token, False))
        elif token in _NEGATION_RESET:
            remaining = 0
            tokens.append((token, False))
        elif remaining > 0:
            remaining -= 1
            tokens.append((token, True))
        else:
            tokens.append((token, False))
    return tokens


def _find_phrase(tokens: list[str | None], phrase: tuple[str, ...]) -> list[int]:
    """Start indexes where ``phrase`` occurs contiguously in ``tokens``."""
    width = len(phrase)
    return [
        start
        for start in range(len(tokens) - width + 1)
        if all(tokens[start + k] == phrase[k] for k in range(width))
    ]


def _curated_phrase_tokens() -> dict[tuple[str, ...], FunctionalDepartment]:
    return {
        tuple(_stem(part) for part in re.split(r"[ ]", phrase)): dept
        for phrase, dept in _PHRASE_TO_DEPARTMENT.items()
    }


_CURATED_PHRASES = _curated_phrase_tokens()


def _sentence_departments(sentence: str, scale: str, self_tokens: frozenset[str]) -> set[str]:
    tagged = _tokens_with_negation(sentence)
    if not tagged:
        return set()

    # Hyphenated words ("chain-of-thought") stay whole; negated tokens become
    # None so they can never start or complete a match.
    surface: list[str | None] = [None if negated else _stem(tok) for tok, negated in tagged]
    consumed = [False] * len(surface)
    found: set[str] = set()

    def claim(start: int, width: int, dept: FunctionalDepartment) -> None:
        found.add(dept.name)
        for k in range(start, start + width):
            consumed[k] = True

    # 1. Table-segment phrases at the active scale. Segments are tried against
    #    the surface text and against the text with the system's own name
    #    removed, so "membrane receptors" matches the segment "cell membrane
    #    receptors" and "cell membrane" matches "cell membrane".
    stripped_index = [i for i, tok in enumerate(surface) if tok is not None and tok not in self_tokens]
    stripped = [surface[i] for i in stripped_index]
    heads_by_token = _HEAD_TOKEN_DEPARTMENTS.get(scale, {})
    for dept, tokens, _is_head in _SEGMENTS.get(scale, ()):
        if len(tokens) == 1:
            token = tokens[0]
            owners = heads_by_token.get(token, ())
            distinctive = len(owners) == 1 and owners[0] == dept
            if not distinctive or not _usable_token(token) or token in self_tokens:
                continue
            for start in _find_phrase(surface, tokens):
                claim(start, 1, dept)
            continue
        for start in _find_phrase(surface, tokens):
            claim(start, len(tokens), dept)
        reduced = tuple(tok for tok in tokens if tok not in self_tokens)
        if len(reduced) >= 2 and reduced != tokens:
            for start in _find_phrase(stripped, reduced):
                for k in range(start, start + len(reduced)):
                    consumed[stripped_index[k]] = True
                found.add(dept.name)

    # 2. Curated multi-word synonyms.
    for tokens, dept in _CURATED_PHRASES.items():
        for start in _find_phrase(surface, tokens):
            claim(start, len(tokens), dept)

    # 3. Remaining words: curated single-word synonyms, then table head words.
    for index, token in enumerate(surface):
        if token is None or consumed[index]:
            continue
        raw = tagged[index][0]
        if token in self_tokens or not _usable_token(raw) or not _usable_token(token):
            continue
        curated = _KEYWORD_TO_DEPARTMENT.get(raw) or _KEYWORD_TO_DEPARTMENT.get(token)
        if curated is not None:
            found.add(curated.name)
        owners = heads_by_token.get(token)
        if owners:
            # First-listed department at this scale wins an ambiguous word.
            found.add(owners[0].name)
        if "-" in raw:
            for part in raw.split("-"):
                part_token = _stem(part)
                if part_token in self_tokens or not _usable_token(part):
                    continue
                curated = _KEYWORD_TO_DEPARTMENT.get(part) or _KEYWORD_TO_DEPARTMENT.get(part_token)
                if curated is not None:
                    found.add(curated.name)
                part_owners = heads_by_token.get(part_token)
                if part_owners:
                    found.add(part_owners[0].name)

    return found


def _map_present_to_departments(
    present: list[str],
    scale: str,
    raw_text: str | None = None,
) -> set[str]:
    """
    Map raw extracted terms (actors/flows) and the raw input text to functional
    departments they give evidence for at ``scale``. See the rules above.
    """
    departments: set[str] = set()
    self_tokens = _SCALE_SELF_TOKENS.get(scale, frozenset())

    texts = [t for t in present if isinstance(t, str)]
    if raw_text:
        texts.append(raw_text)

    for text in texts:
        for sentence in re.split(r"[.;!?\n]+", text.lower()):
            departments |= _sentence_departments(sentence, scale, self_tokens)

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


def map_fractal_similarity(
    packet: Any,
    registry: Any = None,
    *,
    resolve_frames: bool = False,
) -> list[dict[str, Any]]:
    """
    Build fractal mappings for a packet.

    Citation: v1.0 Spec Section 8, step 4

    ``resolve_frames=False`` (default) keeps the shipped V3.0.0 behaviour: frame
    names are matched against a free-text keyword table, which in practice
    matches almost none of the names the frame detector emits ("computation",
    "organizational", "reflexion", ...), so most packets get no mappings.

    ``resolve_frames=True`` resolves frame names through ``FRAME_TO_SCALE``. It is
    opt-in because it changes frozen-core output: the mappings it produces carry
    lower-case scale names ("human", "society") that the frozen dataset schema
    2.1.0 enum rejects, so enabling it requires a schema-aware translation step
    first (see the V3.0.0 review report).
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
            if resolve_frames:
                source_scale = scale_for_frame(source)
                target_scale = scale_for_frame(target)
            else:
                source_scale = _legacy_scale_for_frame(source)
                target_scale = _legacy_scale_for_frame(target)

            if source_scale and target_scale and source_scale != target_scale:
                dept_mappings = map_all_departments(source_scale, target_scale)
                mappings.extend(dept_mappings)

    return mappings
