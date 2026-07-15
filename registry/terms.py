"""
Reflexion Semantic Compiler v2.0.0 — Term Registry

Maintains a registry of known terms, their canonical translations,
and domain-specific meanings. This is the noun and function lookup
table that the translation layer uses.

Citation: v1.0 Spec Section 23 — Runtime Package Design (registry/)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TermEntry:
    """A registered term with its canonical translation."""
    term_id: str
    surface_form: str
    canonical_form: str
    domain: str = ""
    scale: str = ""
    claim_type: str = ""
    definition: str = ""
    translations: dict[str, str] = field(default_factory=dict)
    forbidden_interpretations: list[str] = field(default_factory=list)
    era_lock: Optional[str] = None
    notes: str = ""


class TermRegistry:
    """
    In-memory term registry with lookup and registration.

    This registry is the source of truth for noun and function translations.
    It maintains versioned entries and supports domain-specific lookups.
    """

    def __init__(self) -> None:
        self._terms: dict[str, TermEntry] = {}
        self._version: str = "2.0.0"
        self._load_defaults()

    @property
    def version(self) -> str:
        return self._version

    def register(self, entry: TermEntry) -> None:
        """Register or update a term entry."""
        self._terms[entry.term_id] = entry

    def lookup(self, surface_form: str) -> TermEntry | None:
        """Look up a term by its surface form (case-insensitive)."""
        normalized = surface_form.lower().strip()
        for entry in self._terms.values():
            if entry.surface_form.lower() == normalized:
                return entry
            if entry.canonical_form.lower() == normalized:
                return entry
        return None

    def lookup_by_domain(self, domain: str) -> list[TermEntry]:
        """Get all terms in a given domain."""
        return [
            e for e in self._terms.values()
            if e.domain.lower() == domain.lower()
        ]

    def all_terms(self) -> list[TermEntry]:
        """Return all registered terms."""
        return list(self._terms.values())

    def match_input(self, text: str) -> list[TermEntry]:
        """Find all terms whose surface form appears in the text."""
        normalized = text.lower()
        matches: list[TermEntry] = []
        for entry in self._terms.values():
            if entry.surface_form.lower() in normalized:
                matches.append(entry)
        return matches

    def _load_defaults(self) -> None:
        """Load default Reflexion terms."""
        defaults = [
            TermEntry(
                term_id="TERM_001",
                surface_form="immune system",
                canonical_form="security_and_quality_control",
                domain="biology",
                definition="Biological threat detection, classification, response, memory, and tolerance",
                translations={
                    "organizational": "security department + quality control",
                    "computational": "firewall + antivirus + access control",
                    "national": "police + military + intelligence",
                },
            ),
            TermEntry(
                term_id="TERM_002",
                surface_form="nervous system",
                canonical_form="telecommunications_and_routing",
                domain="biology",
                definition="Signal transmission, routing, and coordination across distributed system",
                translations={
                    "organizational": "internal communications + mail routing",
                    "computational": "network stack + IPC + message queue",
                    "national": "internet + phones + postal system",
                },
            ),
            TermEntry(
                term_id="TERM_003",
                surface_form="organism",
                canonical_form="complex_adaptive_system",
                domain="biology",
                definition="Self-maintaining system with internal departments, boundaries, and feedback loops",
                translations={
                    "organizational": "organization with functional departments",
                    "computational": "distributed system with services",
                    "national": "nation-state with institutions",
                },
            ),
            TermEntry(
                term_id="TERM_004",
                surface_form="cancer",
                canonical_form="subsystem_optimizing_against_whole",
                domain="pathology",
                definition="Component replicating without constraint, consuming shared resources",
                translations={
                    "organizational": "department capturing budget/authority at org expense",
                    "computational": "runaway process / resource leak / fork bomb",
                    "national": "regulatory capture / corruption",
                },
            ),
            TermEntry(
                term_id="TERM_005",
                surface_form="autoimmune",
                canonical_form="defense_attacking_legitimate_function",
                domain="pathology",
                definition="Security/defense system misidentifying internal components as threats",
                translations={
                    "organizational": "compliance blocking productive work",
                    "computational": "firewall blocking legitimate traffic",
                    "national": "surveillance state targeting citizens",
                    "personal": "trauma response attacking safe relationships",
                },
            ),
            TermEntry(
                term_id="TERM_006",
                surface_form="Goku",
                canonical_form="read_only_loose_wire_scout",
                domain="reflexion_role",
                definition="Active defense scout that inventories, classifies, reports, and routes. Does NOT execute destructive repairs.",
                translations={
                    "operational": "read-only diagnostic agent",
                },
                forbidden_interpretations=[
                    "production mutation authority",
                    "destructive repair",
                    "secret access",
                ],
                era_lock="post_buu_saga",
            ),
            TermEntry(
                term_id="TERM_007",
                surface_form="Dragon",
                canonical_form="cross_plane_semantic_translator",
                domain="reflexion_role",
                definition="Translates ambiguous cross-domain meanings. Does not own operational authority.",
                translations={
                    "operational": "semantic disambiguation and translation layer",
                },
                forbidden_interpretations=[
                    "runtime mutation",
                    "authority override",
                ],
            ),
            TermEntry(
                term_id="TERM_008",
                surface_form="debt",
                canonical_form="future_claim_coordination_promise",
                domain="economics",
                definition="Future claim / coordination promise / resource-allocation contract. Meaning varies by system role.",
                translations={
                    "household": "obligation that must be serviced from earned income",
                    "business": "obligation serviced through revenue/profit/capital",
                    "sovereign": "liability in self-issued currency, constrained by productive capacity",
                },
                forbidden_interpretations=[
                    "universal meaning across all system types",
                    "household budget metaphor applied to sovereign currency issuer",
                ],
                notes="Citation: Diamond+++ Economic Architecture Translation Rule",
            ),
            TermEntry(
                term_id="TERM_009",
                surface_form="Hawking radiation",
                canonical_form="information_escaping_storage_boundary",
                domain="cosmology",
                definition="Thermal radiation emitted from black hole event horizon — information escaping containment",
                translations={
                    "computational": "file deletion / garbage collection at storage boundary",
                    "organizational": "information leak from secure perimeter",
                },
                notes="v2.0 Cosmological Mapping",
            ),
            TermEntry(
                term_id="TERM_010",
                surface_form="dark matter",
                canonical_form="invisible_structural_overhead",
                domain="cosmology",
                definition="Unobservable matter that provides structural integrity — invisible computational cost",
                translations={
                    "computational": "background processes / rendering overhead / system overhead",
                    "organizational": "administrative burden / bureaucratic overhead",
                },
                notes="v2.0 Cosmological Mapping",
            ),
        ]

        for entry in defaults:
            self.register(entry)
