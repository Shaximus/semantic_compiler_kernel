"""
Reflexion Semantic Compiler v2.0.0 — Universal Department Invariance Table

Complex systems repeatedly require equivalent organs. This module defines
the universal functional departments and their cross-domain manifestations.

When a function appears absent, the compiler classifies it as:
MISSING, HIDDEN, OUTSOURCED, DUPLICATED, CAPTURED, UNDERPOWERED, MISASSIGNED.

Citation: v1.0 Spec Section 14 — Functional Department Invariance
Citation: v2.0 — Universal Fractal Isomorphism Table
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from semantic_compiler.core.types import FunctionalDepartment, OrganStatus, ScaleType


@dataclass
class DepartmentManifest:
    """How a functional department manifests at a particular scale."""
    department: FunctionalDepartment
    scale: ScaleType
    manifestation: str
    description: str = ""
    failure_modes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# v1.0 Core Functional Departments (from Spec Section 14)
# ---------------------------------------------------------------------------

CORE_DEPARTMENTS_V1: list[dict[str, str]] = [
    {"function": "boundary / skin", "category": "SECURITY"},
    {"function": "threat detection / immune patrol", "category": "SECURITY"},
    {"function": "emergency response / inflammation", "category": "SECURITY"},
    {"function": "repair / healing", "category": "PROCESSOR"},
    {"function": "resource distribution / circulation", "category": "ENERGY_INTAKE"},
    {"function": "communication / nervous system", "category": "TELECOMMUNICATIONS"},
    {"function": "memory / archive", "category": "STORAGE"},
    {"function": "governance / executive control", "category": "PROCESSOR"},
    {"function": "arbitration / law", "category": "SUBCONSCIOUS"},
    {"function": "waste removal / sanitation", "category": "WASTE_REMOVAL"},
    {"function": "growth / construction", "category": "REPRODUCTION"},
    {"function": "training / reproduction of capability", "category": "REPRODUCTION"},
    {"function": "quality control / immune tolerance", "category": "SECURITY"},
    {"function": "energy intake / metabolism", "category": "ENERGY_INTAKE"},
    {"function": "death / archive / recycling", "category": "DELETION"},
]


# ---------------------------------------------------------------------------
# v2.0 Universal Fractal Isomorphism Table
# ---------------------------------------------------------------------------

UNIVERSAL_ISOMORPHISM_TABLE: dict[str, dict[str, str]] = {
    # FunctionalDepartment.name → {ScaleType.name → manifestation}

    "PROCESSOR": {
        "QUANTUM": "Quantum computation",
        "CELLULAR": "Nucleus / DNA transcription",
        "COMPONENT": "CPU / ALU",
        "PROCESS": "Main execution thread",
        "AGENT": "Prefrontal cortex / reasoning",
        "TEAM": "Team lead",
        "DEPARTMENTAL": "Department head",
        "ORGANIZATIONAL": "Executive team",
        "INSTITUTIONAL": "Board / governance body",
        "NATIONAL": "Government executive branch",
        "CIVILIZATIONAL": "Civilizational leadership consensus",
        "COSMOLOGICAL": "Central gravitational body / star",
    },
    "DISPLAY": {
        "QUANTUM": "Observable / measurement output",
        "CELLULAR": "Cell signaling display / bioluminescence",
        "COMPONENT": "GPU / display adapter",
        "PROCESS": "stdout / render pipeline",
        "AGENT": "Eyes + optical nerves / visual cortex",
        "TEAM": "Sprint demo / status board",
        "DEPARTMENTAL": "Department dashboard",
        "ORGANIZATIONAL": "Public communications",
        "INSTITUTIONAL": "Media / public affairs",
        "NATIONAL": "National media / press",
        "CIVILIZATIONAL": "Civilizational cultural output",
        "COSMOLOGICAL": "Electromagnetic radiation / light",
    },
    "WASTE_REMOVAL": {
        "QUANTUM": "Decoherence / information loss",
        "CELLULAR": "Lysosome / autophagy",
        "COMPONENT": "Garbage collector / memory deallocation",
        "PROCESS": "Process cleanup / temp file removal",
        "AGENT": "Kidneys + liver / excretion",
        "TEAM": "Retrospective / debt cleanup",
        "DEPARTMENTAL": "Audit / compliance cleanup",
        "ORGANIZATIONAL": "Sanitation / waste management dept",
        "INSTITUTIONAL": "Regulatory enforcement cleanup",
        "NATIONAL": "Sanitation infrastructure / EPA",
        "CIVILIZATIONAL": "Environmental remediation",
        "COSMOLOGICAL": "Hawking radiation / entropy increase",
    },
    "SECURITY": {
        "QUANTUM": "No-cloning theorem / quantum encryption",
        "CELLULAR": "Cell membrane / immune response",
        "COMPONENT": "Firewall / access control",
        "PROCESS": "Sandbox / permission system",
        "AGENT": "Immune system / fight-or-flight",
        "TEAM": "Code review / access gates",
        "DEPARTMENTAL": "Security team / access policies",
        "ORGANIZATIONAL": "Security department",
        "INSTITUTIONAL": "Regulatory compliance / legal",
        "NATIONAL": "Police + military + intelligence",
        "CIVILIZATIONAL": "Alliance defense systems",
        "COSMOLOGICAL": "Heliosphere / magnetosphere boundary",
    },
    "TELECOMMUNICATIONS": {
        "QUANTUM": "Quantum entanglement / teleportation",
        "CELLULAR": "Chemical signaling / ion channels",
        "COMPONENT": "Network stack / bus",
        "PROCESS": "IPC / message queue",
        "AGENT": "Nervous system / sensory input",
        "TEAM": "Chat / standup / email",
        "DEPARTMENTAL": "Internal comms / mail routing",
        "ORGANIZATIONAL": "Enterprise communication system",
        "INSTITUTIONAL": "Institutional communication channels",
        "NATIONAL": "Internet + phones + postal",
        "CIVILIZATIONAL": "Cross-civilization communication",
        "COSMOLOGICAL": "Electromagnetic spectrum / gravity waves",
    },
    "STORAGE": {
        "QUANTUM": "Quantum information / qubit state",
        "CELLULAR": "DNA / epigenetic memory",
        "COMPONENT": "Hard drive / SSD / RAM",
        "PROCESS": "Database / file system",
        "AGENT": "Memory / hippocampus",
        "TEAM": "Wiki / documentation",
        "DEPARTMENTAL": "Department archives",
        "ORGANIZATIONAL": "Enterprise knowledge base",
        "INSTITUTIONAL": "National archives / libraries",
        "NATIONAL": "Archives / libraries / registries",
        "CIVILIZATIONAL": "Civilizational knowledge corpus",
        "COSMOLOGICAL": "Black holes / information preservation",
    },
    "SUBCONSCIOUS": {
        "QUANTUM": "Laws of physics / fundamental constants",
        "CELLULAR": "Epigenetic regulation / gene silencing",
        "COMPONENT": "BIOS / firmware / microcode",
        "PROCESS": "OS kernel / init system",
        "AGENT": "Subconscious / J-Space / autonomic",
        "TEAM": "Unwritten team norms",
        "DEPARTMENTAL": "Departmental culture / implicit rules",
        "ORGANIZATIONAL": "Corporate culture / implicit values",
        "INSTITUTIONAL": "Institutional norms / precedent",
        "NATIONAL": "Government / constitution / law",
        "CIVILIZATIONAL": "Civilizational moral framework",
        "COSMOLOGICAL": "Laws of physics / mathematical structure",
    },
    "INNER_MONOLOGUE": {
        "QUANTUM": "Quantum superposition / uncollapsed states",
        "CELLULAR": "Gene expression regulation",
        "COMPONENT": "CPU pipeline / branch prediction",
        "PROCESS": "Internal logging / debug trace",
        "AGENT": "Thinking tokens / inner speech",
        "TEAM": "Team deliberation / brainstorm",
        "DEPARTMENTAL": "Policy debate / draft proposals",
        "ORGANIZATIONAL": "Strategic planning / board deliberation",
        "INSTITUTIONAL": "Policy drafting / committee debate",
        "NATIONAL": "Legislative debate / public discourse",
        "CIVILIZATIONAL": "Philosophical discourse",
        "COSMOLOGICAL": "Quantum superposition states",
    },
    "SPEECH_OUTPUT": {
        "QUANTUM": "Wave function collapse / measurement",
        "CELLULAR": "Protein expression / cell output",
        "COMPONENT": "System output / API response",
        "PROCESS": "Process output / return value",
        "AGENT": "Speech / model output / action",
        "TEAM": "Team decision / deliverable",
        "DEPARTMENTAL": "Department policy / report",
        "ORGANIZATIONAL": "Company announcement / product release",
        "INSTITUTIONAL": "Law / regulation / ruling",
        "NATIONAL": "Law / policy / executive order",
        "CIVILIZATIONAL": "Civilizational paradigm shift",
        "COSMOLOGICAL": "Wave function collapse / observed state",
    },
    "ENERGY_INTAKE": {
        "QUANTUM": "Energy absorption / photon capture",
        "CELLULAR": "Mitochondria / ATP production",
        "COMPONENT": "Power supply / voltage regulator",
        "PROCESS": "CPU cycles / resource allocation",
        "AGENT": "Metabolism / food intake",
        "TEAM": "Budget / resource allocation",
        "DEPARTMENTAL": "Departmental budget",
        "ORGANIZATIONAL": "Revenue / economy",
        "INSTITUTIONAL": "Funding / taxation",
        "NATIONAL": "National economy / GDP",
        "CIVILIZATIONAL": "Civilizational energy production",
        "COSMOLOGICAL": "Stellar fusion / energy production",
    },
    "REPRODUCTION": {
        "QUANTUM": "Quantum copying (limited by no-cloning)",
        "CELLULAR": "Cell division / mitosis",
        "COMPONENT": "Fork / clone / VM snapshot",
        "PROCESS": "Process spawning / fork()",
        "AGENT": "Training / learning / education",
        "TEAM": "Onboarding / knowledge transfer",
        "DEPARTMENTAL": "Department training program",
        "ORGANIZATIONAL": "Hiring / training pipeline",
        "INSTITUTIONAL": "Education system",
        "NATIONAL": "Education + immigration + birth",
        "CIVILIZATIONAL": "Cultural transmission",
        "COSMOLOGICAL": "Star formation / galaxy seeding",
    },
    "DELETION": {
        "QUANTUM": "Quantum decoherence / information erasure",
        "CELLULAR": "Apoptosis / programmed cell death",
        "COMPONENT": "File deletion / memory free",
        "PROCESS": "Process termination / cleanup",
        "AGENT": "Death / forgetting",
        "TEAM": "Team dissolution / project end",
        "DEPARTMENTAL": "Department restructuring",
        "ORGANIZATIONAL": "Company shutdown / bankruptcy",
        "INSTITUTIONAL": "Institutional dissolution",
        "NATIONAL": "State collapse / revolution",
        "CIVILIZATIONAL": "Civilizational decline",
        "COSMOLOGICAL": "Hawking radiation / heat death",
    },
    "APPLICATION": {
        "QUANTUM": "Observed quantum state",
        "CELLULAR": "Cell function / phenotype",
        "COMPONENT": "Display output / rendered frame",
        "PROCESS": "Application / running program",
        "AGENT": "Conscious experience / rendered reality",
        "TEAM": "Team output / product",
        "DEPARTMENTAL": "Department deliverables",
        "ORGANIZATIONAL": "Product / service",
        "INSTITUTIONAL": "Institutional output / service",
        "NATIONAL": "National infrastructure / services",
        "CIVILIZATIONAL": "Civilizational achievements",
        "COSMOLOGICAL": "Earth / rendered experience / planets",
    },
    "RENDERING_OVERHEAD": {
        "QUANTUM": "Virtual particle fluctuations",
        "CELLULAR": "Metabolic waste / heat",
        "COMPONENT": "System overhead / background processes",
        "PROCESS": "GC pauses / context switches",
        "AGENT": "Cognitive load / unconscious processing",
        "TEAM": "Meeting overhead / coordination cost",
        "DEPARTMENTAL": "Administrative overhead",
        "ORGANIZATIONAL": "Bureaucratic overhead",
        "INSTITUTIONAL": "Regulatory compliance cost",
        "NATIONAL": "Government overhead / bureaucracy",
        "CIVILIZATIONAL": "Civilizational coordination cost",
        "COSMOLOGICAL": "Dark matter / dark energy",
    },
    "INFORMATION_DENSITY": {
        "QUANTUM": "Quantum information / entanglement entropy",
        "CELLULAR": "Gene density / protein diversity",
        "COMPONENT": "RAM / cache density",
        "PROCESS": "Working set size / memory pressure",
        "AGENT": "Cognitive capacity / working memory",
        "TEAM": "Team knowledge density",
        "DEPARTMENTAL": "Departmental expertise density",
        "ORGANIZATIONAL": "Institutional knowledge",
        "INSTITUTIONAL": "Research output density",
        "NATIONAL": "Population density / education level",
        "CIVILIZATIONAL": "Civilizational knowledge density",
        "COSMOLOGICAL": "Information density / Bekenstein bound",
    },
}


def get_manifestation(
    department: FunctionalDepartment,
    scale: ScaleType,
) -> str:
    """
    Look up how a functional department manifests at a given scale.

    Returns the manifestation string or 'UNKNOWN' if not mapped.
    """
    dept_row = UNIVERSAL_ISOMORPHISM_TABLE.get(department.name, {})
    return dept_row.get(scale.name, "UNKNOWN")


def get_all_departments_at_scale(scale: ScaleType) -> dict[str, str]:
    """Get all functional departments and their manifestations at a given scale."""
    result: dict[str, str] = {}
    for dept_name, scale_map in UNIVERSAL_ISOMORPHISM_TABLE.items():
        result[dept_name] = scale_map.get(scale.name, "UNKNOWN")
    return result


def get_all_scales_for_department(
    department: FunctionalDepartment,
) -> dict[str, str]:
    """Get all scale manifestations for a given department."""
    return dict(UNIVERSAL_ISOMORPHISM_TABLE.get(department.name, {}))


def diagnose_missing_organs(
    system_description: dict[str, Any],
    scale: ScaleType,
) -> list[dict[str, Any]]:
    """
    Given a system description, identify which functional departments
    appear to be missing, hidden, or underpowered.

    Citation: v1.0 Spec Section 14 — Functional Department Invariance

    Args:
        system_description: dict with 'present_functions' list of strings
        scale: the scale at which to evaluate

    Returns:
        List of organ diagnostics with status classification
    """
    present = set(
        f.upper() for f in system_description.get("present_functions", [])
    )
    results: list[dict[str, Any]] = []

    for dept_name, scale_map in UNIVERSAL_ISOMORPHISM_TABLE.items():
        manifestation = scale_map.get(scale.name, "UNKNOWN")
        dept_enum = FunctionalDepartment[dept_name]

        # Check if this department's function appears in the system
        is_present = any(
            dept_name.lower() in p.lower() or
            manifestation.lower() in p.lower()
            for p in present
        ) if present else False

        if is_present:
            status = OrganStatus.PRESENT
        else:
            # Default to MISSING — deeper analysis can refine
            status = OrganStatus.MISSING

        results.append({
            "department": dept_name,
            "expected_manifestation": manifestation,
            "status": status.name,
            "scale": scale.name,
        })

    return results
