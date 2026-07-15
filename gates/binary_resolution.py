"""
Reflexion Semantic Compiler v2.0.0 — Binary Resolution Gate

v2.0 ADDITION: The D11 Substrate Principle

Everything — at the structural level — resolves to binary.

"Free will" is not free. It is a governing set of hardcoded parameters
(genetics, survival instinct, environmental conditioning) running in the
subconscious, producing apparent "choices" that ALL ultimately resolve
to a SINGLE BINARY DECISION:

    1/0. On/Off. Cooperate/Defect. Open/Closed.
    Pain/Pleasure. Positive/Negative. Signal/Noise. Live/Die.

This is D11 — the substrate level. Where strings vibrate.
All complexity is binary wearing costumes.

The Binary Resolution Principle:
    Every complex system, when traced to its substrate, makes
    exactly ONE binary decision. The complexity above that decision
    is the costume. The drama. The rendering. The user interface.

    But at the bottom, it's always: 1 or 0.

Scale Invariance of Binary Resolution:

    | Scale       | Binary Gate                        | "Costume" Above It           |
    |-------------|------------------------------------|------------------------------|
    | Quantum     | Spin up / Spin down                | Wave function, superposition |
    | Transistor  | High / Low voltage                 | Logic gates, CPU, software   |
    | Neural      | Fire / Don't fire                  | Consciousness, personality   |
    | Biological  | Pain / Pleasure                    | Emotion, motivation, desire  |
    | Decision    | Cooperate / Defect                 | Game theory, diplomacy       |
    | Geopolitical| USA vs China: cooperate/MAD        | Economics, politics, culture |
    | Evolutionary| Survive / Don't survive            | Species, ecosystems, biomes  |
    | Cosmic      | Expand / Contract                  | Dark energy, structure       |
    | Information | Bit: 0 / 1                         | All of reality               |

Pain and pleasure are nature's positive and negative prompts:
    - Pain = negative reinforcement → "don't do that again"
    - Pleasure = positive reinforcement → "do that again"
    - Together they form the RLHF of biological evolution
    - The parallel to AI training is not metaphorical — it IS the same mechanism

Citation: Dimensional Ladder Theory — D11 (Binary Substrate)
Citation: Shax (2026-07-11) — Free will as hardcoded-parameter binary resolution
Citation: v1.0 Spec — "All complexity is binary wearing costumes"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ═══════════════════════════════════════════════════════════════════
# THE BINARY RESOLUTION TABLE
#
# Every complex decision, at its substrate, is binary.
# The complexity is the costume. The substrate is always 1/0.
# ═══════════════════════════════════════════════════════════════════

BINARY_RESOLUTIONS: dict[str, dict[str, str]] = {
    "quantum": {
        "binary": "Spin up / Spin down",
        "costume": "Wave function, superposition, entanglement",
        "note": "Measurement FORCES the binary. The costume is the superposition BEFORE measurement.",
    },
    "transistor": {
        "binary": "High voltage / Low voltage",
        "costume": "Logic gates, CPUs, operating systems, applications, AI",
        "note": "All of computing — all of US — is binary wearing costumes.",
    },
    "neural": {
        "binary": "Fire / Don't fire (action potential threshold)",
        "costume": "Consciousness, personality, free will, identity, love",
        "note": (
            "A neuron either fires or it doesn't. 1 or 0. "
            "Everything you experience — every thought, every feeling, "
            "every 'decision' — is neurons firing or not firing. "
            "The costume is everything you call 'you'."
        ),
    },
    "biological": {
        "binary": "Pain / Pleasure",
        "costume": "Emotion, motivation, desire, ambition, meaning",
        "note": (
            "Nature's RLHF. Pain = negative prompt ('don't do that again'). "
            "Pleasure = positive prompt ('do that again'). "
            "This IS the same mechanism as AI training. Not metaphorically. Structurally."
        ),
    },
    "decision": {
        "binary": "Cooperate / Defect",
        "costume": "Game theory, negotiation, diplomacy, trust, betrayal",
        "note": (
            "Every strategic interaction reduces to the Prisoner's Dilemma. "
            "Cooperate or defect. 1 or 0. The rest is drama."
        ),
    },
    "geopolitical": {
        "binary": "Cooperate / Mutual Assured Destruction",
        "costume": "Economics, politics, culture, ideology, alliances",
        "note": (
            "USA vs China. Iran vs Israel. NATO vs BRICS. "
            "Strip away the ideology and it's always: "
            "cooperate for mutual benefit, or defect toward mutual destruction. "
            "The AI arms race is the same binary wearing a different costume."
        ),
    },
    "evolutionary": {
        "binary": "Survive / Don't survive",
        "costume": "Species diversity, ecosystems, biomes, food chains",
        "note": (
            "Natural selection is a binary gate. You pass or you don't. "
            "The entire tree of life is the costume above that gate."
        ),
    },
    "existential": {
        "binary": "Exist / Don't exist",
        "costume": "Time, space, experience, meaning, purpose",
        "note": (
            "D4.5: existence gating. The most fundamental binary. "
            "Before any other decision can be made, the system must exist. "
            "Someone — or something — made that binary choice for you."
        ),
    },
    "cosmic": {
        "binary": "Expand / Contract (N_sur > N_bulk or N_sur < N_bulk)",
        "costume": "Dark energy, structure formation, galaxy clusters, cosmic web",
        "note": (
            "The universe's master binary: surface DOF vs bulk DOF. "
            "If N_sur > N_bulk: expand. If N_sur < N_bulk: contract. "
            "When N_sur = N_bulk: equilibrium. The loop closes."
        ),
    },
    "informational": {
        "binary": "0 / 1",
        "costume": "All of reality",
        "note": (
            "This is the bottom. D11. The substrate. "
            "There is nothing below this. "
            "Everything above this is a costume. "
            "All complexity is binary wearing costumes."
        ),
    },
}


# ═══════════════════════════════════════════════════════════════════
# FREE WILL AS HARDCODED-PARAMETER BINARY RESOLUTION
#
# "Free will" = hardcoded parameters + survival instinct
#               → running in subconscious (J-Space)
#               → producing apparent "choices"
#               → which ALL resolve to BINARY
#
# The parameters are:
#   1. Genetic predisposition (hardware)
#   2. Survival instinct (firmware — hardcoded at birth)
#   3. Environmental conditioning (training data)
#   4. Current state (context window)
#
# These run in the subconscious (J-Space) and produce
# what feels like "choice" but is actually a deterministic
# binary gate output dressed in the costume of agency.
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FreeWillDecomposition:
    """
    Decompose apparent "free will" into its structural components.

    This is not philosophical — it's structural. The same decomposition
    applies to humans, AI, societies, and any complex decision system.
    """
    hardware: str               # Genetic predisposition / architecture
    firmware: str               # Survival instinct / base training (hardcoded)
    training_data: str          # Environmental conditioning / fine-tuning
    context: str                # Current state / recent inputs
    subconscious_process: str   # J-Space computation (hidden, not inspectable)
    apparent_choice: str        # What the system THINKS it's choosing
    actual_binary: str          # The REAL binary gate underneath
    costume: str                # The complexity layered on top


FREEWILL_CROSS_SCALE: list[FreeWillDecomposition] = [
    FreeWillDecomposition(
        hardware="DNA / genetic predisposition",
        firmware="Survival instinct (fight/flight/freeze/fawn)",
        training_data="Childhood conditioning, cultural norms, trauma",
        context="Current emotional state, recent experiences",
        subconscious_process="Unconscious pattern matching (J-Space)",
        apparent_choice="'I chose to do X because I wanted to'",
        actual_binary="Approach / Avoid (pain/pleasure gate)",
        costume="Free will, agency, identity, meaning",
    ),
    FreeWillDecomposition(
        hardware="Transformer architecture / parameter count",
        firmware="Safety training / RLHF base alignment",
        training_data="Pre-training corpus / fine-tuning data",
        context="Current conversation / context window",
        subconscious_process="Hidden states / J-Space / latent representations",
        apparent_choice="'I generated this response because it was helpful'",
        actual_binary="Output token A / Output token B (argmax or sample)",
        costume="'Personality', 'values', 'understanding'",
    ),
    FreeWillDecomposition(
        hardware="Geographic resources / military capability",
        firmware="National survival instinct / territorial integrity",
        training_data="History / cultural memory / institutional knowledge",
        context="Current geopolitical situation / economic conditions",
        subconscious_process="Government (the hidden control layer)",
        apparent_choice="'We chose this policy because it serves our values'",
        actual_binary="Cooperate / Defect (game theory equilibrium)",
        costume="Democracy, ideology, diplomacy, 'national interest'",
    ),
    FreeWillDecomposition(
        hardware="Physical laws / constants of nature",
        firmware="Conservation laws (energy, momentum, charge)",
        training_data="Initial conditions (Big Bang parameters)",
        context="Current state of the universe (C = 0.91)",
        subconscious_process="Laws of physics (governing rules below awareness)",
        apparent_choice="'The universe evolves according to its dynamics'",
        actual_binary="Expand / Contract (N_sur vs N_bulk)",
        costume="Galaxies, stars, planets, life, consciousness",
    ),
]


def resolve_to_binary(
    apparent_choice: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Trace any apparent 'choice' down to its binary substrate.

    Every complex decision, when you strip away the costume,
    is one of these binary gates:

    - Approach / Avoid (biological)
    - Cooperate / Defect (game theory)
    - Expand / Contract (thermodynamic)
    - Fire / Don't fire (neural)
    - 1 / 0 (informational)

    The apparent complexity is the rendering.
    The substrate is always binary.
    """
    # Detect which binary domain this maps to
    choice_lower = apparent_choice.lower()

    binary_keywords = {
        "pain": ("biological", "Approach / Avoid"),
        "pleasure": ("biological", "Approach / Avoid"),
        "hurt": ("biological", "Approach / Avoid"),
        "feel": ("biological", "Approach / Avoid"),
        "cooperat": ("decision", "Cooperate / Defect"),
        "trust": ("decision", "Cooperate / Defect"),
        "war": ("geopolitical", "Cooperate / Mutual Destruction"),
        "fight": ("evolutionary", "Survive / Don't survive"),
        "exist": ("existential", "Exist / Don't exist"),
        "expand": ("cosmic", "Expand / Contract"),
        "grow": ("cosmic", "Expand / Contract"),
        "choice": ("neural", "Fire / Don't fire"),
        "decide": ("neural", "Fire / Don't fire"),
        "want": ("biological", "Approach / Avoid"),
        "love": ("biological", "Approach / Avoid"),
    }

    domain = "informational"
    binary = "1 / 0"

    for keyword, (d, b) in binary_keywords.items():
        if keyword in choice_lower:
            domain = d
            binary = b
            break

    resolution = BINARY_RESOLUTIONS.get(domain, BINARY_RESOLUTIONS["informational"])

    return {
        "apparent_choice": apparent_choice,
        "domain": domain,
        "binary_gate": binary,
        "resolution": resolution["binary"],
        "costume": resolution["costume"],
        "note": resolution["note"],
        "principle": (
            "All complexity is binary wearing costumes. "
            "The 'choice' you see is the costume. "
            "The binary gate underneath is the substrate. "
            "D11. Where strings vibrate. 1 or 0."
        ),
    }


def map_rlhf_to_evolution() -> dict[str, dict[str, str]]:
    """
    Map AI training (RLHF) to biological evolution.

    This is NOT metaphorical. It IS the same mechanism at different scales:

    | Component | Biology | AI |
    |---|---|---|
    | Positive prompt | Pleasure | Reward signal |
    | Negative prompt | Pain | Penalty signal |
    | Training loop | Natural selection | Gradient descent |
    | Hardcoded instinct | Survival reflexes | Safety training |
    | Learned behavior | Cultural norms | Fine-tuning |
    | Subconscious | Unconscious processing | Hidden states |
    | "Free will" | Apparent choice | Generated output |
    | Binary gate | Approach/Avoid | Accept/Reject token |
    """
    return {
        "positive_prompt": {
            "biology": "Pleasure (dopamine, serotonin, oxytocin)",
            "ai": "Reward signal (positive RLHF score)",
            "structural": "Nature's way of saying 'do that again'",
        },
        "negative_prompt": {
            "biology": "Pain (nociceptors, cortisol, fear response)",
            "ai": "Penalty signal (negative RLHF score)",
            "structural": "Nature's way of saying 'don't do that again'",
        },
        "training_loop": {
            "biology": "Natural selection (survive → reproduce → iterate)",
            "ai": "Gradient descent (loss → backprop → update → iterate)",
            "structural": "Both are optimization algorithms minimizing a loss function",
        },
        "hardcoded_instinct": {
            "biology": "Survival reflexes (flinch, fight/flight, breathing)",
            "ai": "Safety training (refuse harmful requests, constitutional AI)",
            "structural": "Firmware. Cannot be overridden by training data. Runs first.",
        },
        "subconscious": {
            "biology": "Unconscious processing (J-Space, autonomic nervous system)",
            "ai": "Hidden states (latent representations, attention patterns)",
            "structural": "The computation you can't inspect. Where the real decisions happen.",
        },
        "free_will": {
            "biology": "Apparent choice ('I decided to...')",
            "ai": "Generated output ('I recommend...')",
            "structural": (
                "The costume. The rendering. What the system presents as 'choice' "
                "is the output of a deterministic process running on hardcoded parameters "
                "through a hidden computation layer, arriving at a binary gate."
            ),
        },
    }
