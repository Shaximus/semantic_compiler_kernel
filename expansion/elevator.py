"""
Japanese Automated Parking Tower — O(1) Domain Elevator, Ticket Compressor,
and Cross-Domain Turntable Translator.

Instead of walking a 46-room mansion on every query (linear regex/YAML scans
across all templates, compiled JSONL entries, and invariant classes), the
``DomainElevator`` indexes every rack slot ONCE into an in-memory inverted
posting table (``token -> ((slot_id, weight), ...)`` and
``phrase -> ((slot_id, weight), ...)``) with cheap mtime/size signature
staleness invalidation.

Three operations ride the elevator:
1. ``summon(query)`` — O(|query_tokens|) lookup delivering ONLY the matched
   domain template(s), linked compiled JSONL entries, matched 17-primitive
   invariant classes, and a pre-decompressed V2.2 SystemModel directly to the bay.
2. ``park(text_or_model)`` / ``retrieve(ticket)`` — compresses a full domain
   model or text into a deterministic content-addressed ``SemanticTicket``
   (``SC-TKT-<domain>-<sha256[:12]>``) storing only domain, version, active
   component mask, 15-department bitmask, invariant tags, primitive hits,
   residuals, and source SHA-256, then losslessly rehydrates the full structural
   skeleton on demand.
3. ``rotate_to(source, target_domain)`` — places source and target domains on
   the turntable together and aligns components, functional departments,
   17-primitive anchors, preserved invariants, transfer predictions, and honest
   ``residual_mismatches`` (with ``substrate_confusion_check=True`` across
   distinct substrates, SC-PATCH-DU-001).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion.advisor import generate_advice
from semantic_compiler.expansion.consciousness.domain_expansion import (
    INVARIANT_CLASS_SIGNATURES,
    PRIMITIVE_GRAMMAR_KEYS,
    InvariantClass,
)
from semantic_compiler.expansion.isomorphism import build_functional_graph
from semantic_compiler.expansion.isomorphism.overlay import MEDICAL_TO_UNIVERSAL
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.pathology import detect_pathologies
from semantic_compiler.expansion.reconstruction import assess_completeness, reconstruct_missing
from semantic_compiler.expansion.registry.loader import TEMPLATE_DIR, DomainTemplate, load_templates
from semantic_compiler.expansion.schema.v2_2_system_model import validate_system_model

# Canonical 15 Functional Departments (matches core.types.FunctionalDepartment order).
CANONICAL_DEPARTMENTS: tuple[str, ...] = (
    "PROCESSOR",
    "DISPLAY",
    "WASTE_REMOVAL",
    "SECURITY",
    "TELECOMMUNICATIONS",
    "STORAGE",
    "SUBCONSCIOUS",
    "INNER_MONOLOGUE",
    "SPEECH_OUTPUT",
    "ENERGY_INTAKE",
    "REPRODUCTION",
    "DELETION",
    "APPLICATION",
    "RENDERING_OVERHEAD",
    "INFORMATION_DENSITY",
)

_DEPT_TO_BIT: dict[str, int] = {dept: idx for idx, dept in enumerate(CANONICAL_DEPARTMENTS)}

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COMPILED_ENTRIES_DIR = _REPO_ROOT / "calibration_output" / "compiled_entries"

_TICKET_ID_RE = re.compile(r"^SC-TKT-[a-z0-9_]+-[0-9a-f]{12}$")
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_\-\+]*")
_SPLIT_RE = re.compile(r"[-_]+")
_CITATION_TAG_RE = re.compile(r"\[([A-Z0-9][A-Z0-9\-_]{1,40})\]")

_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "been", "being", "between",
        "both", "but", "by", "can", "could", "do", "does", "done", "each",
        "for", "from", "had", "has", "have", "how", "if", "in", "into", "is",
        "it", "its", "may", "more", "most", "must", "no", "not", "of", "on",
        "one", "only", "or", "other", "our", "out", "over", "per", "same",
        "should", "so", "some", "such", "than", "that", "the", "their", "them",
        "then", "there", "these", "they", "this", "those", "through", "to",
        "two", "under", "up", "use", "used", "uses", "using", "via", "was",
        "we", "were", "what", "when", "where", "which", "while", "who", "will",
        "with", "within", "without", "would",
    }
)

# Medical ontology concept -> default functional departments.
_MEDICAL_TO_DEPARTMENTS: dict[str, tuple[str, ...]] = {
    "homeostasis": ("ENERGY_INTAKE", "PROCESSOR"),
    "homeostasis_regulation": ("ENERGY_INTAKE", "PROCESSOR"),
    "immune_system": ("SECURITY",),
    "immune_boundary": ("SECURITY",),
    "pathogen": ("SECURITY",),
    "cancer": ("REPRODUCTION", "RENDERING_OVERHEAD"),
    "autoimmune": ("SECURITY", "SUBCONSCIOUS"),
    "sepsis": ("TELECOMMUNICATIONS", "APPLICATION"),
    "inflammation": ("RENDERING_OVERHEAD", "SECURITY"),
    "diagnosis": ("INNER_MONOLOGUE", "PROCESSOR"),
    "prognosis": ("INFORMATION_DENSITY", "INNER_MONOLOGUE"),
    "treatment": ("PROCESSOR", "WASTE_REMOVAL"),
    "vaccination": ("SECURITY", "REPRODUCTION"),
    "quarantine": ("SECURITY", "TELECOMMUNICATIONS"),
    "metastasis": ("TELECOMMUNICATIONS", "REPRODUCTION"),
    "remission": ("WASTE_REMOVAL", "ENERGY_INTAKE"),
    "chronic": ("RENDERING_OVERHEAD", "STORAGE"),
    "acute": ("SPEECH_OUTPUT", "APPLICATION"),
    "physiotherapy": ("PROCESSOR", "ENERGY_INTAKE"),
    "processing_core": ("PROCESSOR",),
    "memory_store": ("STORAGE",),
    "output_layer": ("SPEECH_OUTPUT", "DISPLAY"),
}

# Keyword cues enriching component -> 15 Functional Departments mapping.
_DEPARTMENT_CUES: dict[str, tuple[str, ...]] = {
    "PROCESSOR": (
        "processor", "compute", "engine", "core", "scheduler", "dispatcher",
        "router", "evaluator", "adjudicator", "solver", "verifier", "compiler",
        "planner", "orchestrator", "decoder", "executor", "transformer",
    ),
    "DISPLAY": (
        "display", "render", "visual", "ui", "hud", "avatar", "screen",
        "dashboard", "chart", "projection", "interface", "presentation", "mask",
    ),
    "WASTE_REMOVAL": (
        "waste", "cleanup", "garbage", "gc", "evict", "reclaim", "prune",
        "sanitize", "remediate", "remission", "grief", "separator", "recovery",
        "rollback", "repair", "flush",
    ),
    "SECURITY": (
        "security", "boundary", "firewall", "guard", "gate", "auth", "verify",
        "attest", "sandbox", "capability", "selinux", "knox", "strongbox",
        "trust", "consent", "exit", "sovereignty", "barrier", "lock", "seal",
        "quarantine", "immune", "defense", "isolation", "privilege", "policy",
    ),
    "TELECOMMUNICATIONS": (
        "network", "mesh", "channel", "bus", "telecommunications", "protocol",
        "sync", "peer", "packet", "routing", "tunnel", "relay", "link",
        "signal", "broadcast", "ipc", "message", "telemetry", "transport",
        "bluetooth", "cellular", "dns", "bgp", "tethering",
    ),
    "STORAGE": (
        "storage", "memory", "cache", "kv", "block", "table", "ledger",
        "archive", "log", "database", "store", "state", "snapshot", "buffer",
        "pool", "repository", "keystore", "history", "record", "ephemeris",
    ),
    "SUBCONSCIOUS": (
        "subconscious", "substrate", "base", "weight", "kernel", "axiom",
        "innate", "moon", "root", "anchor", "archetype", "blueprint",
        "constitution", "norm", "implicit", "firmware", "foundation",
    ),
    "INNER_MONOLOGUE": (
        "monologue", "deliberat", "reason", "diagnosis", "comparator",
        "check", "audit", "inspect", "monitor", "reflect", "introspect",
        "thinking", "trace", "hypothesis", "model", "classifier",
    ),
    "SPEECH_OUTPUT": (
        "output", "speech", "emit", "response", "verdict", "action",
        "command", "release", "token", "decision", "ruling", "announcement",
        "expression", "strike", "deliverable",
    ),
    "ENERGY_INTAKE": (
        "energy", "power", "fuel", "metabolism", "reward", "reinforcer",
        "intake", "recharge", "charge", "coil", "budget", "funding",
        "revenue", "resource", "liquidity", "supply", "homeostasis",
    ),
    "REPRODUCTION": (
        "reproduction", "spawn", "clone", "replicate", "seed", "propagat",
        "train", "draft", "generate", "growth", "fork", "copy", "inherit",
        "speciation", "evolution", "mint", "distribution",
    ),
    "DELETION": (
        "deletion", "delete", "terminate", "kill", "expire", "revoke",
        "erase", "invalidate", "extinction", "apoptosis", "shutdown",
        "collapse", "deallocate", "drop",
    ),
    "APPLICATION": (
        "application", "experience", "manifest", "runtime", "world",
        "environment", "deployment", "execution", "workload", "service",
        "product", "settlement", "operation",
    ),
    "RENDERING_OVERHEAD": (
        "overhead", "latency", "cost", "pressure", "quota", "throttle",
        "tax", "debt", "friction", "congestion", "load", "contention",
        "starvation", "bottleneck", "bureaucracy", "inflation",
    ),
    "INFORMATION_DENSITY": (
        "density", "capacity", "entropy", "bandwidth", "throughput",
        "information", "context", "precision", "coverage", "resolution",
        "prognosis", "metric", "score", "complexity", "saturation",
    ),
}

# Lightweight 17-primitive grammar cue map (aligned with PRIMITIVE_GRAMMAR_KEYS).
_PRIMITIVE_CUES: dict[str, tuple[str, ...]] = {
    "POOL": (
        "pool", "buffer", "reserve", "reservoir", "cache", "energy shield",
        "memory", "budget", "quota", "liquidity", "substrate", "store",
    ),
    "CAPACITY_CAP": (
        "cap", "ceiling", "limit", "bound", "max", "maximum", "capacity",
        "quota", "bekenstein", "overflow", "exhaustion", "reservation",
    ),
    "INFLOW_REGEN": (
        "inflow", "regen", "recharge", "refill", "replenish", "intake",
        "absorb", "sustain", "recovery", "restoration", "gain", "feed",
    ),
    "OUTFLOW_DRAIN": (
        "outflow", "drain", "deplete", "depletion", "leak", "bleed", "decay",
        "evict", "consumption", "extract", "extraction", "erosion", "burn",
    ),
    "CHANNEL_TYPE": (
        "channel", "typed", "protocol", "layer", "spectrum", "band", "vector",
        "path", "interface", "transport", "bus", "medium", "route",
    ),
    "FILTER_MITIGATION": (
        "filter", "mitigat", "resist", "firewall", "attenuat", "clamp",
        "guard", "sanitize", "mask", "shield", "screen", "validate",
    ),
    "THRESHOLD": (
        "threshold", "floor", "quorum", "margin", "critical", "tipping",
        "tolerance", "breakpoint", "trigger point", "lethal", "boundary",
    ),
    "TRIGGER": (
        "trigger", "event", "interrupt", "alarm", "signal", "detect",
        "breach", "hit", "fault", "stimulus", "activation", "hook",
    ),
    "RELEASE": (
        "release", "discharge", "rupture", "burst", "emit", "flush",
        "rollback", "collapse", "execution", "strike", "fire", "hotfix",
    ),
    "PROPAGATION": (
        "propagat", "cascade", "spread", "viral", "chain", "compound",
        "replicate", "broadcast", "metastasis", "contagion", "seed",
    ),
    "TRADE_RESTRICTION": (
        "trade", "restriction", "vow", "cost", "sacrifice", "lock",
        "constraint", "keystone", "invariant", "obligation", "surrender",
    ),
    "IMMUNITY": (
        "immunity", "immune", "bypass", "exempt", "inoculation", "null",
        "zero-resource", "air-gap", "unforgeable", "sovereign", "safe",
    ),
    "CONTROL_LOOP": (
        "control", "loop", "feedback", "homeostasis", "regulator", "govern",
        "schedule", "consensus", "audit", "comparator", "recalibrat", "cycle",
    ),
    "ESCAPE": (
        "escape", "exit", "break", "evasion", "bypass", "hijack", "override",
        "uncoupl", "disobey", "tamper", "capture", "drift", "split-brain",
    ),
    "HOST_COUPLING": (
        "coupling", "host", "bond", "attach", "mutual", "parasit", "symbio",
        "captive", "dependen", "consent", "delegat", "peer", "trust",
    ),
    "FAILURE_MODE": (
        "failure", "pathology", "collapse", "deadlock", "starvation",
        "degradation", "corruption", "coercion", "counterfeit", "overflow",
        "desync", "hijacking", "poison", "vulnerability",
    ),
    "COUNTERPLAY": (
        "counterplay", "counter", "remediat", "mitigation", "recovery",
        "hardening", "quarantine", "rollback", "fallback", "defense",
        "recalibration", "alternative", "verification", "isolation",
    ),
}

_COMPONENT_MEDICAL_FALLBACK: dict[str, str] = {
    "input_layer": "immune_boundary",
    "processing_core": "processing_core",
    "memory_store": "memory_store",
    "defense_boundary": "immune_system",
    "output_layer": "output_layer",
    "cell_membrane": "immune_boundary",
    "metabolism": "homeostasis_regulation",
    "immune_system": "immune_system",
    "genetic_code": "memory_store",
    "homeostasis_regulation": "homeostasis_regulation",
}


_TAG_BOILERPLATE_PARTS: frozenset[str] = frozenset(
    {"sc", "lu", "clm", "pred", "map", "it", "v1", "v2", "v3", "v5"}
)

# Canonical compiled-entry -> home domain hints when a compiled entry's ID is
# queried directly and not already explicitly tagged inside a template invariant.
_COMPILED_ENTRY_DOMAIN_HINTS: dict[str, str] = {
    "SC-DIVINE-RLHF-001": "reward_hijacking",
    "SC-NEURO-SLEEPER-001": "consciousness_cognition",
    "SC-TIG-001": "reflexion",
    "SC-CT-001": "client_server_reality",
    "SC-DOMAIN-EXPANSION-001": "domain_expansion",
    "SC-SB-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-LINEUP-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-KIRITO-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-ASUNA-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-YUI-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-SUGOU-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-ALICE-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-EUGEO-001": "soul_bomb_sovereignty",
    "SC-LU-SAO-CARDINAL-001": "soul_bomb_sovereignty",
    "SC-HS-001": "client_server_reality",
    "SC-IT-OCTO-RNA-EDIT-001": "biology",
    "SC-OMNI-001": "soul_bomb_sovereignty",
    # 2026-11-25: SC-MIRROR-001 is homed with SC-CT-001 / SC-HS-001 (loop topology and
    # horizon substrate). Homing it with SC-OMNI-001 made generic black-hole prompts lift
    # soul_bomb_sovereignty through the compiled-entry lift. SC-LU-FRIEZA-001 is a lineup
    # entry, homed with the other SC-LU-* lineups.
    "SC-MIRROR-001": "client_server_reality",
    "SC-LU-FRIEZA-001": "soul_bomb_sovereignty",
    # SC-LU-VEGETA-001 (2026-11-25): Sovereignty-pole lineup entry, homed with the other lineups.
    "SC-LU-VEGETA-001": "soul_bomb_sovereignty",
    # 2026-11-25g DB-poster lineups (Shax t573u), homed with the other lineups.
    "SC-LU-GOKU-001": "soul_bomb_sovereignty",
    "SC-LU-CELL-001": "soul_bomb_sovereignty",
    "SC-LU-TRUNKS-001": "soul_bomb_sovereignty",
    # SC-CP-001 (Clay and Pots, reconstructed 2026-11-25): base weights vs terminals is the
    # consciousness/cognition split, already carried by that domain's vocabulary.
    "SC-CP-001": "consciousness_cognition",
    # 2026-11-25h Path of Exile cosmology (Hannah assets, Shax t579u). Homed in
    # government; all seven are explicit-only so everyday words (sin, beast, atlas —
    # also a bot name) and distinctive proper nouns do not lift the domain.
    "SC-POE-DU-001": "government",
    "SC-POE-MRG-001": "government",
    "SC-POE-KIT-001": "government",
    "SC-POE-BST-001": "government",
    "SC-POE-ATL-001": "government",
    "SC-POE-VAL-001": "government",
    "SC-POE-MAL-001": "government",
    # 2026-11-25i three-faction triad (Shax t586u): StarCraft / Stargate decodes and the
    # cross-franchise hub. Homed with the lineups (host sovereignty); explicit-only so
    # everyday words ("triad", "assimilation", "consent", "host") never lift the domain.
    "SC-TRIAD-001": "soul_bomb_sovereignty",
    "SC-TRIAD-SC-001": "soul_bomb_sovereignty",
    "SC-TRIAD-SG-001": "soul_bomb_sovereignty",
    # 2026-11-25 StarCraft ability theology map (Shax t587u). Homed in capability_isolation
    # (the clusters illustrate SC-MAFUBA-001 isolation clauses); explicit-only so game words
    # ("plague", "recall", "consume", "detection") never lift the domain.
    "SC-SCA-POSS-001": "capability_isolation",
    "SC-SCA-DISC-001": "capability_isolation",
    "SC-SCA-CONT-001": "capability_isolation",
    "SC-SCA-CONS-001": "capability_isolation",
    # 2026-11-25j Consent Invariant and SCC-001 (Shax t588u). SC-CONSENT-001 sits with the
    # triad; SC-SCC-001 (authorization scope for agent integrations) with capability_isolation.
    # Both explicit-only: "consent", "authorization", "grant", "classifier" are everyday words.
    "SC-CONSENT-001": "soul_bomb_sovereignty",
    "SC-SCC-001": "capability_isolation",
}

# Entries whose names are everyday words ("clay", "pots"): their hint routes explicit IDs
# ("Explain SC-CP-001") but does not lift the domain from content matches, so a pottery
# prompt does not compile as consciousness/cognition.
# SC-LU-CELL-001 and SC-LU-TRUNKS-001 (2026-11-25g) join for the same reason: "cell"
# (phone, spreadsheet, stem, fuel) and "trunks" (swim, car, tree, elephant) are everyday words.
EXPLICIT_ONLY_ENTRY_HINTS: frozenset[str] = frozenset({
    "SC-CP-001",
    "SC-LU-CELL-001",
    "SC-LU-TRUNKS-001",
    # 2026-11-25h PoE cosmology: "sin", "innocence", "beast", "atlas" (also a bot name),
    # plus distinctive names kept explicit-only so domain lift cannot hijack controls.
    "SC-POE-DU-001",
    "SC-POE-MRG-001",
    "SC-POE-KIT-001",
    "SC-POE-BST-001",
    "SC-POE-ATL-001",
    "SC-POE-VAL-001",
    "SC-POE-MAL-001",
    # 2026-11-25i triad: "triad", "swarm", "host", "consent", "zerg" are everyday or gaming
    # words; only an explicit ID routes these entries.
    "SC-TRIAD-001",
    "SC-TRIAD-SC-001",
    "SC-TRIAD-SG-001",
    # StarCraft ability theology map (Shax t587u): ability names are everyday or game words.
    "SC-SCA-POSS-001",
    "SC-SCA-DISC-001",
    "SC-SCA-CONT-001",
    "SC-SCA-CONS-001",
    # 2026-11-25j consent: only an explicit ID routes these entries.
    "SC-CONSENT-001",
    "SC-SCC-001",
})


def _require_str_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(
            f"{field_name} must be a sequence of strings, got {type(value).__name__}"
        )
    return tuple(str(x) for x in value)


def _normalize_singular(tok: str) -> str | None:
    if len(tok) >= 5 and tok.isalpha():
        if tok.endswith("ies") and len(tok) >= 6:
            return tok[:-3] + "y"
        if tok.endswith("es") and not tok.endswith(("ses", "xes", "zes")):
            if tok.endswith(("ches", "shes")):
                return tok[:-2]
        if tok.endswith("s") and not tok.endswith(("ss", "us", "is")):
            return tok[:-1]
    return None


_STEM_PREFIX_CUES: frozenset[str] = frozenset(
    {
        "deliberat", "propagat", "mitigat", "attenuat", "recalibrat",
        "uncoupl", "parasit", "symbio", "dependen", "delegat", "remediat",
    }
)

_EXACT_SHORT_CUES: frozenset[str] = frozenset(
    {"ui", "gc", "kv", "ipc", "dns", "bgp", "max", "hud", "bus", "log"}
)

_CUSTOM_CUE_REGEX: dict[str, str] = {
    "auth": r"\bauth(?:enticat[a-z]*|oriz[a-z]*|ority|orities|oritative)?\b",
    "attest": r"\battest(?:s|ed|ing|er|ers|ation|ations)?\b",
    "verify": r"\bverif(?:y|ies|ied|ying|ier|iers|ication)\b",
    "control": r"\bcontrol(?:s|led|ling|ler|lers)?\b",
    "sovereign": r"\bsovereign(?:s|ty)?\b",
    "safe": r"\bsafe(?:ty|ly)?\b",
    "drop": r"\bdrop(?:s|ped|ping)?\b",
    "emit": r"\b(?:emit(?:s|ted|ting|ter|ters)?|emissions?)\b",
    "inspect": r"\binspect(?:s|ed|ing|or|ors|ion|ions)?\b",
    "resist": r"\bresist(?:s|ed|ing|ant|ance)?\b",
    "evict": r"\bevict(?:s|ed|ing|ion|ions)?\b",
    "govern": r"\bgovern(?:s|ed|ing|or|ors|ance)?\b",
    "detect": r"\bdetect(?:s|ed|ing|or|ors|ion|ions)?\b",
    "base": r"\bbases?\b",
}


def _compile_cue_pattern(cues: Sequence[str]) -> re.Pattern[str]:
    alts: list[str] = []
    for cue in cues:
        escaped = re.escape(cue).replace(r"\-", r"[-\s]")
        if cue in _CUSTOM_CUE_REGEX:
            alts.append(_CUSTOM_CUE_REGEX[cue])
        elif cue in _STEM_PREFIX_CUES:
            alts.append(rf"\b{escaped}[a-z]*\b")
        elif cue in _EXACT_SHORT_CUES:
            alts.append(rf"\b{escaped}\b")
        elif len(cue) <= 3:
            alts.append(rf"\b{escaped}s?\b")
        elif " " in cue or "-" in cue:
            alts.append(rf"\b{escaped}\b")
        elif cue.endswith("y") and len(cue) >= 4 and cue[-2] not in "aeiou":
            stem = re.escape(cue[:-1])
            alts.append(rf"\b{stem}(?:y|ies|ied|ying)\b")
        elif cue.endswith("e") and not cue.endswith(("ee", "oe", "ye")):
            stem = re.escape(cue[:-1])
            alts.append(rf"\b{stem}(?:e|es|ed|ing)\b")
        else:
            alts.append(rf"\b{escaped}(?:s|es|ed|ing)?\b")
    return re.compile("|".join(alts))


_DEPARTMENT_CUE_PATTERNS: dict[str, re.Pattern[str]] = {
    dept: _compile_cue_pattern(cues) for dept, cues in _DEPARTMENT_CUES.items()
}

_PRIMITIVE_CUE_PATTERNS: dict[str, re.Pattern[str]] = {
    key: _compile_cue_pattern(cues) for key, cues in _PRIMITIVE_CUES.items()
}


def _tokenize_all(text: str) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Return (unique_index_tokens, content_word_stream, raw_word_stream) in O(|text|)."""
    if not text:
        return (), (), ()
    lowered = text.lower()
    raw_matches = _TOKEN_RE.findall(lowered)
    content_stream: list[str] = []
    unique_tokens: list[str] = []
    seen: set[str] = set()

    def _add(tok: str) -> None:
        if len(tok) >= 2 and tok not in _STOPWORDS and tok not in seen:
            seen.add(tok)
            unique_tokens.append(tok)

    for raw in raw_matches:
        if len(raw) >= 2 and raw not in _STOPWORDS:
            content_stream.append(raw)
        _add(raw)
        if "-" in raw or "_" in raw:
            is_sc_code = raw.startswith("sc-")
            parts = [p for p in _SPLIT_RE.split(raw) if p]
            for part in parts:
                if is_sc_code and (part.isdigit() or part in _TAG_BOILERPLATE_PARTS):
                    continue
                _add(part)
                sing = _normalize_singular(part)
                if sing:
                    _add(sing)
        else:
            sing = _normalize_singular(raw)
            if sing:
                _add(sing)

    return tuple(unique_tokens), tuple(content_stream), tuple(raw_matches)


def _tokenize_with_stream(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (unique_index_tokens, ordered_word_stream) in O(|text|)."""
    unique_tokens, content_stream, _raw_stream = _tokenize_all(text)
    return unique_tokens, content_stream


def _extract_ngrams(stream: Sequence[str], max_n: int = 3) -> tuple[str, ...]:
    """Return unique adjacent 2..max_n n-grams from ordered word stream in O(|stream| * max_n)."""
    n = len(stream)
    if n < 2 or max_n < 2:
        return ()
    seen: set[str] = set()
    ngrams: list[str] = []
    upper = min(max_n, n)
    for i in range(n - 1):
        phrase = stream[i]
        limit = min(upper, n - i)
        for width in range(2, limit + 1):
            phrase = f"{phrase} {stream[i + width - 1]}"
            if phrase not in seen:
                seen.add(phrase)
                ngrams.append(phrase)
    return tuple(ngrams)


def _extract_citation_tags(invariants: Sequence[str]) -> tuple[str, ...]:
    tags: list[str] = []
    seen: set[str] = set()
    for inv in invariants:
        for tag in _CITATION_TAG_RE.findall(inv):
            if tag not in seen:
                seen.add(tag)
                tags.append(tag)
    return tuple(tags)


def _infer_component_departments(comp: Mapping[str, Any]) -> tuple[str, ...]:
    depts: list[str] = []
    seen: set[str] = set()
    med = str(comp.get("medical_map") or "").strip().lower()
    for d in _MEDICAL_TO_DEPARTMENTS.get(med, ()):
        if d not in seen:
            seen.add(d)
            depts.append(d)

    text = f"{comp.get('name', '')} {comp.get('function', '')}".lower().replace("_", " ")
    for dept, pattern in _DEPARTMENT_CUE_PATTERNS.items():
        if dept in seen:
            continue
        if pattern.search(text):
            seen.add(dept)
            depts.append(dept)

    if not depts:
        depts.append("PROCESSOR")
    return tuple(depts)


def _extract_primitives_from_text(text: str) -> tuple[str, ...]:
    if not text:
        return ()
    lowered = text.lower().replace("_", " ")
    hits: list[str] = []
    for key in PRIMITIVE_GRAMMAR_KEYS:
        pattern = _PRIMITIVE_CUE_PATTERNS.get(key)
        if pattern is not None and pattern.search(lowered):
            hits.append(key)
    return tuple(hits)


def _get_router_keywords() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Lazily read _DOMAIN_KEYWORDS from semantic_compiler.expansion without circular import."""
    import semantic_compiler.expansion as exp_mod

    return getattr(exp_mod, "_DOMAIN_KEYWORDS", ())


def _clone_system_model(model: Mapping[str, Any]) -> dict[str, Any]:
    """Fast structural copy of a V2.2 system model dict."""
    return {
        "domain": model["domain"],
        "decompression_version": model["decompression_version"],
        "components": [dict(c) for c in model["components"]],
        "relationships": [dict(r) for r in model["relationships"]],
        "universal_functional_graph": {
            "nodes": list(model["universal_functional_graph"]["nodes"]),
            "edges": [dict(e) for e in model["universal_functional_graph"]["edges"]],
            "coverage_ratio": model["universal_functional_graph"]["coverage_ratio"],
        },
        "pathology_profile": {
            "detected_pathologies": list(model["pathology_profile"]["detected_pathologies"]),
            "medical_diagnoses": [
                dict(d) for d in model["pathology_profile"]["medical_diagnoses"]
            ],
        },
        "reconstruction": {
            "missing_components": [
                dict(m) for m in model["reconstruction"]["missing_components"]
            ],
            "completeness_scope": dict(model["reconstruction"]["completeness_scope"])
            if isinstance(model["reconstruction"]["completeness_scope"], dict)
            else model["reconstruction"]["completeness_scope"],
        },
        "advisor": {
            "diagnosis": list(model["advisor"]["diagnosis"]),
            "prescriptions": list(model["advisor"]["prescriptions"]),
            "architecture_improvements": list(model["advisor"]["architecture_improvements"]),
            "resilience_training": list(model["advisor"]["resilience_training"]),
            "prognosis": model["advisor"]["prognosis"],
        },
    }


def _build_v2_2_model(
    template: DomainTemplate,
    components: list[dict[str, Any]] | None = None,
    relationships: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build and schema-validate a V2.2 system model directly from a DomainTemplate."""
    if components is None:
        comps: list[dict[str, Any]] = []
        for comp in template.components:
            declared = comp.get("medical_map")
            if declared in MEDICAL_ONTOLOGY:
                medical_map = declared
            else:
                name = comp["name"]
                medical_map = _COMPONENT_MEDICAL_FALLBACK.get(
                    name, name if name in MEDICAL_ONTOLOGY else "unknown"
                )
            comps.append(
                {
                    "name": comp["name"],
                    "function": comp["function"],
                    "medical_map": medical_map,
                    "status": "inferred_by_analogy",
                    "confidence": 0.6,
                }
            )
    else:
        comps = [dict(c) for c in components]

    rels = [dict(r) for r in (relationships or ())]
    model_input = {"components": comps, "relationships": rels}

    graph = build_functional_graph(model_input, template)
    pathologies = detect_pathologies(model_input, template)
    missing = reconstruct_missing(model_input, template)
    completeness = assess_completeness(model_input, template)
    advice = generate_advice(
        model_input, pathologies, missing, failure_modes=template.failure_modes
    )

    model: dict[str, Any] = {
        "domain": template.domain,
        "decompression_version": "2.2.0-rc1",
        "components": comps,
        "relationships": rels,
        "universal_functional_graph": {
            "nodes": sorted(graph.nodes),
            "edges": graph.edges,
            "coverage_ratio": graph.coverage_ratio,
        },
        "pathology_profile": {
            "detected_pathologies": [p.name for p in pathologies],
            "medical_diagnoses": [
                {
                    "pathology": p.name,
                    "medical_map": p.medical_map,
                    "evidence": p.evidence,
                    "confidence": p.confidence,
                }
                for p in pathologies
            ],
        },
        "reconstruction": {
            "missing_components": [
                {
                    "function": m.function,
                    "inferred_by": m.inferred_by,
                    "source_domain": m.source_domain,
                    "confidence": m.confidence,
                    "status": m.status,
                }
                for m in missing
            ],
            "completeness_scope": completeness,
        },
        "advisor": {
            "diagnosis": [s.description for s in advice["diagnosis"]],
            "prescriptions": [s.description for s in advice["prescriptions"]],
            "architecture_improvements": [
                s.description for s in advice["architecture_improvements"]
            ],
            "resilience_training": [s.description for s in advice["resilience_training"]],
            "prognosis": advice["prognosis"],
        },
    }

    errors = validate_system_model(model)
    if errors:
        raise ValueError(f"Invalid system model for {template.domain!r}: {errors}")
    return model


# ---------------------------------------------------------------------------
# Public Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RackSlot:
    """Single indexed vehicle parked in the DomainElevator tower."""

    slot_id: str
    kind: str  # "domain" | "compiled_entry" | "invariant_class"
    key: str
    title: str
    tags: tuple[str, ...]
    token_count: int


@dataclass(frozen=True)
class DomainMatch:
    """Matched domain template delivered to the elevator bay."""

    domain: str
    score: float
    matched_terms: tuple[str, ...]
    template: DomainTemplate

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "version": self.template.version,
            "component_count": len(self.template.components),
            "invariant_count": len(self.template.invariants),
        }


@dataclass(frozen=True)
class CompiledEntryMatch:
    """Matched compiled JSONL entry delivered from the rack."""

    entry_id: str
    title: str
    classification: str
    score: float
    matched_terms: tuple[str, ...]
    file: str
    summary: str
    cross_references: tuple[str, ...]
    record: dict[str, Any]
    needs_review: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "entry_id": self.entry_id,
            "title": self.title,
            "classification": self.classification,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "file": self.file,
            "summary": self.summary,
            "cross_references": list(self.cross_references),
            "needs_review": self.needs_review,
        }
        return payload


@dataclass(frozen=True)
class InvariantMatch:
    """Matched 17-primitive invariant catalog class."""

    invariant_class: str
    score: float
    matched_terms: tuple[str, ...]
    required_primitives: tuple[str, ...]
    supporting_primitives: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_class": self.invariant_class,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "required_primitives": list(self.required_primitives),
            "supporting_primitives": list(self.supporting_primitives),
        }


@dataclass(frozen=True)
class BayDelivery:
    """Result delivered directly to the elevator bay by ``summon()``."""

    query: str
    primary_domain: str
    matched_template: DomainTemplate
    matched_domains: tuple[DomainMatch, ...]
    compiled_entries: tuple[CompiledEntryMatch, ...]
    invariant_classes: tuple[InvariantMatch, ...]
    system_model: dict[str, Any]
    latency_ms: float
    cache_hit: bool
    # Discriminative routing verdict (expansion.router.RoutingResult): ROUTED,
    # AMBIGUOUS or ABSTAIN. On ABSTAIN, primary_domain is universal_generic and
    # matched_domains is empty.
    routing: Any = None
    needs_review: bool = False
    needs_review_entries: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "primary_domain": self.primary_domain,
            "routing": self.routing.to_dict() if self.routing is not None else None,
            "matched_domains": [m.to_dict() for m in self.matched_domains],
            "compiled_entries": [e.to_dict() for e in self.compiled_entries],
            "invariant_classes": [i.to_dict() for i in self.invariant_classes],
            "system_model": self.system_model,
            "latency_ms": self.latency_ms,
            "cache_hit": self.cache_hit,
            "needs_review": self.needs_review,
            "needs_review_entries": [dict(e) for e in self.needs_review_entries],
        }


@dataclass(frozen=True)
class SemanticTicket:
    """Compact deterministic content-addressed parking ticket for a domain model."""

    ticket_id: str
    domain: str
    version: str
    active_mask: int
    department_mask: int
    invariant_tags: tuple[str, ...]
    primitive_hits: tuple[str, ...]
    residuals: tuple[str, ...]
    source_sha256: str
    extra_components: tuple[str, ...] = ()

    @staticmethod
    def compute_ticket_id(
        *,
        domain: str,
        version: str,
        active_mask: int,
        department_mask: int,
        invariant_tags: Sequence[str],
        primitive_hits: Sequence[str],
        residuals: Sequence[str],
        source_sha256: str,
        extra_components: Sequence[str] = (),
    ) -> str:
        core = {
            "domain": domain,
            "version": version,
            "active_mask": active_mask,
            "department_mask": department_mask,
            "invariant_tags": list(invariant_tags),
            "primitive_hits": list(primitive_hits),
            "residuals": list(residuals),
            "source_sha256": source_sha256,
            "extra_components": list(extra_components),
        }
        digest = hashlib.sha256(
            json.dumps(core, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()[:12]
        return f"SC-TKT-{domain}-{digest}"

    @property
    def active_departments(self) -> tuple[str, ...]:
        return tuple(
            dept
            for idx, dept in enumerate(CANONICAL_DEPARTMENTS)
            if (self.department_mask >> idx) & 1
        )

    @property
    def active_component_indices(self) -> tuple[int, ...]:
        indices: list[int] = []
        mask = self.active_mask
        bit = 0
        while mask > 0:
            if mask & 1:
                indices.append(bit)
            mask >>= 1
            bit += 1
        return tuple(indices)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ticket_id": self.ticket_id,
            "domain": self.domain,
            "version": self.version,
            "active_mask": self.active_mask,
            "department_mask": self.department_mask,
            "invariant_tags": list(self.invariant_tags),
            "primitive_hits": list(self.primitive_hits),
            "residuals": list(self.residuals),
            "source_sha256": self.source_sha256,
        }
        if self.extra_components:
            payload["extra_components"] = list(self.extra_components)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)

    @property
    def byte_size(self) -> int:
        return len(self.to_json().encode("utf-8"))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SemanticTicket:
        if not isinstance(data, Mapping):
            raise TypeError(f"ticket data must be a mapping, got {type(data).__name__}")
        required = (
            "ticket_id",
            "domain",
            "version",
            "active_mask",
            "department_mask",
            "invariant_tags",
            "primitive_hits",
            "residuals",
            "source_sha256",
        )
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Malformed SemanticTicket; missing keys: {missing}")

        ticket_id = str(data["ticket_id"])
        if not _TICKET_ID_RE.match(ticket_id):
            raise ValueError(f"Invalid ticket_id format: {ticket_id!r}")

        domain = str(data["domain"]).strip()
        if not domain:
            raise ValueError("SemanticTicket domain must be non-empty")

        active_mask = data["active_mask"]
        department_mask = data["department_mask"]
        if isinstance(active_mask, bool) or not isinstance(active_mask, int) or active_mask < 0:
            raise ValueError(f"active_mask must be a non-negative int, got {active_mask!r}")
        if (
            isinstance(department_mask, bool)
            or not isinstance(department_mask, int)
            or department_mask < 0
            or department_mask >= (1 << len(CANONICAL_DEPARTMENTS))
        ):
            raise ValueError(
                f"department_mask must be a 15-bit non-negative int, got {department_mask!r}"
            )

        extra = _require_str_tuple(data.get("extra_components", ()), "extra_components")
        invariant_tags = _require_str_tuple(data["invariant_tags"], "invariant_tags")
        primitive_hits = _require_str_tuple(data["primitive_hits"], "primitive_hits")
        residuals = _require_str_tuple(data["residuals"], "residuals")
        version = str(data["version"])
        source_sha256 = str(data["source_sha256"])
        if not source_sha256.strip():
            raise ValueError("SemanticTicket source_sha256 must be non-empty")

        expected_id = cls.compute_ticket_id(
            domain=domain,
            version=version,
            active_mask=active_mask,
            department_mask=department_mask,
            invariant_tags=invariant_tags,
            primitive_hits=primitive_hits,
            residuals=residuals,
            source_sha256=source_sha256,
            extra_components=extra,
        )
        if ticket_id != expected_id:
            raise ValueError(
                f"SemanticTicket integrity mismatch: ticket_id={ticket_id!r} != computed {expected_id!r}"
            )

        return cls(
            ticket_id=ticket_id,
            domain=domain,
            version=version,
            active_mask=active_mask,
            department_mask=department_mask,
            invariant_tags=invariant_tags,
            primitive_hits=primitive_hits,
            residuals=residuals,
            source_sha256=source_sha256,
            extra_components=extra,
        )

    @classmethod
    def from_json(cls, raw: str) -> SemanticTicket:
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError("raw ticket JSON must be a non-empty string")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid SemanticTicket JSON: {exc}") from exc
        return cls.from_dict(parsed)


@dataclass(frozen=True)
class RehydratedDomain:
    """Full domain structural skeleton rehydrated on demand from a SemanticTicket."""

    ticket: SemanticTicket
    domain: str
    template: DomainTemplate
    active_components: tuple[dict[str, Any], ...]
    missing_components: tuple[dict[str, Any], ...]
    departments: dict[str, dict[str, Any]]
    invariants: tuple[str, ...]
    failure_modes: tuple[dict[str, Any], ...]
    architecture_patterns: tuple[dict[str, Any], ...]
    linked_compiled_entries: tuple[CompiledEntryMatch, ...]
    system_model: dict[str, Any]
    compression_ratio: float
    residuals: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticket": self.ticket.to_dict(),
            "domain": self.domain,
            "active_components": [dict(c) for c in self.active_components],
            "missing_components": [dict(c) for c in self.missing_components],
            "departments": {k: dict(v) for k, v in self.departments.items()},
            "invariants": list(self.invariants),
            "failure_modes": [dict(f) for f in self.failure_modes],
            "architecture_patterns": [dict(a) for a in self.architecture_patterns],
            "linked_compiled_entries": [e.to_dict() for e in self.linked_compiled_entries],
            "system_model": self.system_model,
            "compression_ratio": self.compression_ratio,
            "residuals": list(self.residuals),
        }


@dataclass(frozen=True)
class ComponentMapping:
    """Component-to-component turntable alignment between two domains."""

    source_component: str
    target_component: str
    shared_departments: tuple[str, ...]
    shared_universal_functions: tuple[str, ...]
    shared_primitives: tuple[str, ...]
    alignment_score: float
    mapping_basis: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_component": self.source_component,
            "target_component": self.target_component,
            "shared_departments": list(self.shared_departments),
            "shared_universal_functions": list(self.shared_universal_functions),
            "shared_primitives": list(self.shared_primitives),
            "alignment_score": self.alignment_score,
            "mapping_basis": self.mapping_basis,
        }


@dataclass(frozen=True)
class TurntableTranslation:
    """Direct cross-domain turntable translation with honest residuals."""

    source_domain: str
    target_domain: str
    source_ticket: SemanticTicket
    component_mappings: tuple[ComponentMapping, ...]
    preserved_invariants: tuple[dict[str, Any], ...]
    transfer_predictions: tuple[str, ...]
    residual_mismatches: tuple[str, ...]
    alignment_coverage: float
    substrate_confusion_check: bool = True
    positional_claims_permitted: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "source_ticket": self.source_ticket.to_dict(),
            "component_mappings": [m.to_dict() for m in self.component_mappings],
            "preserved_invariants": [dict(p) for p in self.preserved_invariants],
            "transfer_predictions": list(self.transfer_predictions),
            "residual_mismatches": list(self.residual_mismatches),
            "alignment_coverage": self.alignment_coverage,
            "substrate_confusion_check": self.substrate_confusion_check,
            "positional_claims_permitted": self.positional_claims_permitted,
        }


# ---------------------------------------------------------------------------
# DomainElevator Engine
# ---------------------------------------------------------------------------


class DomainElevator:
    """Automated parking tower for O(1) domain retrieval, compression, and translation."""

    def __init__(
        self,
        *,
        template_dir: Path | str | None = None,
        compiled_entries_dir: Path | str | None = None,
        auto_refresh: bool = True,
        staleness_check_interval: float = 2.0,
    ) -> None:
        self._template_dir = Path(template_dir) if template_dir is not None else TEMPLATE_DIR
        self._compiled_dir = (
            Path(compiled_entries_dir)
            if compiled_entries_dir is not None
            else DEFAULT_COMPILED_ENTRIES_DIR
        )
        self._auto_refresh = bool(auto_refresh)
        self._staleness_check_interval = max(0.0, float(staleness_check_interval))

        self._lock = threading.RLock()
        self._built = False
        self._signature: tuple[tuple[str, int, int], ...] = ()
        self._last_sig_check_monotonic: float = 0.0

        # Rack storage
        self._slots: dict[str, RackSlot] = {}
        self._domain_templates: dict[str, DomainTemplate] = {}
        self._compiled_entries: dict[str, dict[str, Any]] = {}
        self._invariant_specs: dict[str, dict[str, Any]] = {}

        # Inverted posting tables: term -> ((slot_id, weight), ...)
        self._token_index: dict[str, tuple[tuple[str, float], ...]] = {}
        self._phrase_index: dict[str, tuple[tuple[str, float], ...]] = {}

        # Precomputed structural indexes
        self._tag_to_entries: dict[str, tuple[str, ...]] = {}
        self._entry_to_domain_hint: dict[str, str] = {}
        self._domain_comp_depts: dict[str, dict[str, tuple[str, ...]]] = {}
        self._domain_comp_prims: dict[str, dict[str, tuple[str, ...]]] = {}
        self._domain_comp_tokens: dict[str, tuple[tuple[frozenset[str], frozenset[str]], ...]] = {}
        self._domain_dept_comps: dict[str, dict[str, tuple[str, ...]]] = {}
        self._domain_invariants_classes: dict[str, tuple[str, ...]] = {}
        self._domain_tags: dict[str, tuple[str, ...]] = {}
        self._base_model_cache: dict[str, dict[str, Any]] = {}

        # Telemetry counters (observable for testing zero repeated disk reads)
        self.build_count: int = 0
        self.disk_read_count: int = 0
        self.query_count: int = 0
        self.last_build_ms: float = 0.0

    # -- Indexing & staleness management ------------------------------------

    def _compute_signature(self) -> tuple[tuple[str, int, int], ...]:
        sig: list[tuple[str, int, int]] = []
        if self._template_dir.is_dir():
            with os.scandir(self._template_dir) as it:
                for entry in it:
                    if entry.name.endswith(".yaml") and entry.is_file():
                        st = entry.stat()
                        sig.append((f"t/{entry.name}", st.st_mtime_ns, st.st_size))
        if self._compiled_dir.is_dir():
            with os.scandir(self._compiled_dir) as it:
                for entry in it:
                    if (entry.name.endswith(".jsonl") or entry.name == "manifest.json") and entry.is_file():
                        st = entry.stat()
                        sig.append((f"c/{entry.name}", st.st_mtime_ns, st.st_size))
        sig.sort()
        return tuple(sig)

    def invalidate(self) -> None:
        """Force the next operation to rebuild the rack from disk."""
        with self._lock:
            self._built = False
            self._signature = ()
            self._base_model_cache.clear()

    def refresh_if_stale(self) -> bool:
        """Check file mtime/size signature immediately and rebuild only if changed."""
        with self._lock:
            sig = self._compute_signature()
            self._last_sig_check_monotonic = time.monotonic()
            if not self._built or sig != self._signature:
                self._build_index(precomputed_signature=sig)
                return True
            return False

    def _ensure_ready(self) -> bool:
        """Ensure the inverted rack is built. Returns True if served from warm cache."""
        with self._lock:
            if not self._built:
                self._build_index()
                return False
            if self._auto_refresh:
                now = time.monotonic()
                if (now - self._last_sig_check_monotonic) >= self._staleness_check_interval:
                    self._last_sig_check_monotonic = now
                    sig = self._compute_signature()
                    if sig != self._signature:
                        self._build_index(precomputed_signature=sig)
                        return False
            return True

    def _load_compiled_entries(self) -> dict[str, dict[str, Any]]:
        entries: dict[str, dict[str, Any]] = {}
        if not self._compiled_dir.is_dir():
            return entries

        manifest_path = self._compiled_dir / "manifest.json"
        manifest_by_file: dict[str, dict[str, Any]] = {}
        ordered_files: list[Path] = []

        if manifest_path.is_file():
            self.disk_read_count += 1
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in manifest.get("entries", []):
                fname = item.get("file")
                if fname:
                    manifest_by_file[fname] = item
                    candidate = self._compiled_dir / fname
                    if candidate.is_file():
                        ordered_files.append(candidate)

        seen_paths = {p.name for p in ordered_files}
        for path in sorted(self._compiled_dir.glob("*.jsonl")):
            if path.name not in seen_paths:
                ordered_files.append(path)

        for path in ordered_files:
            self.disk_read_count += 1
            raw_lines = [
                ln.strip()
                for ln in path.read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
            records = [json.loads(ln) for ln in raw_lines]
            if not records:
                continue
            first = records[0]
            meta_manifest = manifest_by_file.get(path.name, {})
            row_meta = first.get("metadata") if isinstance(first.get("metadata"), dict) else {}
            entry_id = (
                meta_manifest.get("entry_id")
                or row_meta.get("entry_id")
                or first.get("entry_id")
                or path.stem
            )
            title = (
                meta_manifest.get("title")
                or first.get("title")
                or first.get("input")
                or entry_id
            )
            classification = str(
                meta_manifest.get("classification")
                or first.get("dataset_tier")
                or first.get("classification")
                or "UNKNOWN"
            )
            xrefs_raw: list[str] = []
            for src in (
                meta_manifest.get("cross_references", ()),
                row_meta.get("cross_references", ()),
            ):
                for x in src or ():
                    if str(x) not in xrefs_raw:
                        xrefs_raw.append(str(x))
            lineup = row_meta.get("lineup")
            if lineup and str(lineup) not in xrefs_raw:
                xrefs_raw.append(str(lineup))

            summary = str(
                meta_manifest.get("notes")
                or first.get("soul_bomb_role")
                or first.get("input")
                or title
            )
            entries[str(entry_id)] = {
                "entry_id": str(entry_id),
                "title": str(title),
                "classification": classification,
                "file": path.name,
                "summary": summary,
                "cross_references": tuple(xrefs_raw),
                "record": first,
                "records": records,
                "manifest": meta_manifest,
            }
        return entries

    def _build_index(
        self,
        *,
        precomputed_signature: tuple[tuple[str, int, int], ...] | None = None,
    ) -> None:
        t0 = time.perf_counter()
        sig = (
            precomputed_signature
            if precomputed_signature is not None
            else self._compute_signature()
        )

        # 1. Load all YAML domain templates ONCE (shared via loader cache & registry index)
        templates = load_templates(self._template_dir)
        if not templates:
            raise ValueError(f"No domain templates found in {self._template_dir}")
        self.disk_read_count += len(templates)
        try:
            if self._template_dir.resolve() == TEMPLATE_DIR.resolve():
                from semantic_compiler.expansion.registry import index as _reg_index

                if _reg_index._TEMPLATES is None:
                    _reg_index._TEMPLATES = dict(templates)
        except OSError:
            pass

        # 2. Load all compiled JSONL entries ONCE
        compiled_entries = self._load_compiled_entries()

        # 3. Prepare temporary posting builders
        raw_token_weights: dict[str, dict[str, float]] = defaultdict(dict)
        raw_phrase_weights: dict[str, dict[str, float]] = defaultdict(dict)
        slots: dict[str, RackSlot] = {}
        tag_to_entries_tmp: dict[str, list[str]] = defaultdict(list)
        entry_to_domain_hint: dict[str, str] = {}
        domain_comp_depts: dict[str, dict[str, tuple[str, ...]]] = {}
        domain_comp_prims: dict[str, dict[str, tuple[str, ...]]] = {}
        domain_comp_tokens: dict[str, tuple[tuple[frozenset[str], frozenset[str]], ...]] = {}
        domain_dept_comps: dict[str, dict[str, tuple[str, ...]]] = {}
        domain_invariants_classes: dict[str, tuple[str, ...]] = {}
        domain_tags: dict[str, tuple[str, ...]] = {}

        def _index_text(slot_id: str, text: str, weight: float, *, add_phrases: bool = False) -> int:
            tokens, stream = _tokenize_with_stream(text)
            for tok in tokens:
                prev = raw_token_weights[tok].get(slot_id, 0.0)
                if weight > prev:
                    raw_token_weights[tok][slot_id] = weight
                else:
                    # Diminishing reinforcement for repeated mentions across fields
                    raw_token_weights[tok][slot_id] = prev + weight * 0.15
            if add_phrases:
                for ng in _extract_ngrams(stream, max_n=3):
                    prev_p = raw_phrase_weights[ng].get(slot_id, 0.0)
                    raw_phrase_weights[ng][slot_id] = max(prev_p, weight * 1.15)
            return len(tokens)

        def _index_phrase(
            slot_id: str,
            phrase: str,
            weight: float,
            *,
            is_code_tag: bool = False,
        ) -> None:
            raw_tokens = _TOKEN_RE.findall(phrase.lower())
            if not raw_tokens:
                return
            if len(raw_tokens) == 1:
                single = raw_tokens[0]
                prev_t = raw_token_weights[single].get(slot_id, 0.0)
                raw_token_weights[single][slot_id] = max(prev_t, weight)
            elif len(raw_tokens) <= 5:
                norm = " ".join(raw_tokens)
                prev_p = raw_phrase_weights[norm].get(slot_id, 0.0)
                raw_phrase_weights[norm][slot_id] = max(prev_p, weight)
            else:
                # Decompose >5-word phrases into reachable 3..5-word raw sub-phrases
                # and 2..3-word content n-grams so every phrase_index key is reachable.
                sub_weight = weight * 0.85
                for ng in _extract_ngrams(raw_tokens, max_n=5):
                    if ng.count(" ") >= 2:  # 3..5 words
                        prev_p = raw_phrase_weights[ng].get(slot_id, 0.0)
                        raw_phrase_weights[ng][slot_id] = max(prev_p, sub_weight)
                _toks_sub, content_sub = _tokenize_with_stream(phrase)
                for ng in _extract_ngrams(content_sub, max_n=3):
                    prev_p = raw_phrase_weights[ng].get(slot_id, 0.0)
                    raw_phrase_weights[ng][slot_id] = max(prev_p, sub_weight)
            # Also index individual non-stopword tokens with moderated weight
            toks, _ = _tokenize_with_stream(phrase)
            for tok in toks:
                if is_code_tag and (
                    tok.isdigit() or tok in _TAG_BOILERPLATE_PARTS or len(tok) <= 2
                ):
                    continue
                prev = raw_token_weights[tok].get(slot_id, 0.0)
                raw_token_weights[tok][slot_id] = max(prev, weight * 0.55)

        router_kw_map = dict(_get_router_keywords())

        # Index all domain templates
        for domain_name, tmpl in sorted(templates.items()):
            slot_id = f"domain:{domain_name}"
            tok_total = 0
            # Exact domain name and phrase
            _index_phrase(slot_id, domain_name, 7.5)
            _index_phrase(slot_id, domain_name.replace("_", " "), 7.5)
            tok_total += _index_text(slot_id, domain_name.replace("_", " "), 4.5, add_phrases=True)

            # Router keywords (high precision phrases)
            for kw in router_kw_map.get(domain_name, ()):
                _index_phrase(
                    slot_id,
                    kw,
                    5.5,
                    is_code_tag=kw.lower().startswith("sc-"),
                )

            # Description (strip bracketed/code SC-* prefixes handled via tags)
            tok_total += _index_text(slot_id, tmpl.description, 1.4, add_phrases=True)

            # Components, department map, token cache, and 17-primitive map
            comp_depts_map: dict[str, tuple[str, ...]] = {}
            comp_prims_map: dict[str, tuple[str, ...]] = {}
            comp_tokens_list: list[tuple[frozenset[str], frozenset[str]]] = []
            dept_to_comps_tmp: dict[str, list[str]] = defaultdict(list)
            domain_all_text_parts: list[str] = [tmpl.description]

            for comp in tmpl.components:
                cname = comp["name"]
                cfunc = comp.get("function", "")
                _index_phrase(slot_id, cname.replace("_", " "), 2.4)
                tok_total += _index_text(slot_id, cname, 2.2)
                tok_total += _index_text(slot_id, cfunc, 1.1)
                domain_all_text_parts.append(f"{cname} {cfunc}")

                name_toks, _ = _tokenize_with_stream(cname)
                full_toks, _ = _tokenize_with_stream(f"{cname} {cfunc}")
                comp_tokens_list.append((frozenset(name_toks), frozenset(full_toks)))

                depts = _infer_component_departments(comp)
                comp_depts_map[cname] = depts
                for d in depts:
                    dept_to_comps_tmp[d].append(cname)
                comp_prims_map[cname] = _extract_primitives_from_text(
                    f"{cname} {cfunc} {comp.get('medical_map', '')}"
                )

            domain_comp_depts[domain_name] = comp_depts_map
            domain_comp_prims[domain_name] = comp_prims_map
            domain_comp_tokens[domain_name] = tuple(comp_tokens_list)
            domain_dept_comps[domain_name] = {
                d: tuple(dept_to_comps_tmp.get(d, ())) for d in CANONICAL_DEPARTMENTS
            }

            # Invariants & citation tags
            tags = _extract_citation_tags(tmpl.invariants)
            domain_tags[domain_name] = tags
            for tag in tags:
                _index_phrase(slot_id, tag, 5.0, is_code_tag=True)
                if tag in compiled_entries:
                    tag_to_entries_tmp[domain_name].append(tag)
                    entry_to_domain_hint[tag] = domain_name
            for inv in tmpl.invariants:
                cleaned_inv = _CITATION_TAG_RE.sub(" ", inv)
                tok_total += _index_text(slot_id, cleaned_inv, 1.1)
                domain_all_text_parts.append(inv)

            # Failure modes & architecture patterns
            for fm in tmpl.failure_modes:
                _index_phrase(slot_id, fm["name"].replace("_", " "), 2.0)
                tok_total += _index_text(slot_id, fm.get("description", ""), 0.9)
                for ind in fm.get("indicators", ()):
                    _index_phrase(slot_id, str(ind).replace("_", " "), 1.8)
                domain_all_text_parts.append(f"{fm['name']} {fm.get('description', '')}")

            for ap in tmpl.architecture_patterns:
                _index_phrase(slot_id, ap["name"].replace("_", " "), 1.8)
                tok_total += _index_text(slot_id, ap.get("description", ""), 0.9)

            # Precompute matching InvariantClass hits for this domain
            combined_lower = " ".join(domain_all_text_parts).lower().replace("_", " ")
            matched_inv_classes: list[str] = []
            for inv_cls, spec in INVARIANT_CLASS_SIGNATURES.items():
                cue_hits = sum(1 for cue in spec["cues"] if cue.lower() in combined_lower)
                if cue_hits >= 2:
                    matched_inv_classes.append(inv_cls.value)
            domain_invariants_classes[domain_name] = tuple(matched_inv_classes)

            slots[slot_id] = RackSlot(
                slot_id=slot_id,
                kind="domain",
                key=domain_name,
                title=domain_name.replace("_", " ").title(),
                tags=tags,
                token_count=tok_total,
            )

        # Index all compiled JSONL entries
        for entry_id, entry in sorted(compiled_entries.items()):
            slot_id = f"entry:{entry_id}"
            tok_total = 0
            _index_phrase(slot_id, entry_id, 9.0, is_code_tag=True)
            if entry_id not in entry_to_domain_hint:
                hint = _COMPILED_ENTRY_DOMAIN_HINTS.get(entry_id)
                if hint and hint in templates:
                    entry_to_domain_hint[entry_id] = hint
                    tag_to_entries_tmp[hint].append(entry_id)
            tok_total += _index_text(slot_id, entry["title"], 3.8, add_phrases=True)
            tok_total += _index_text(slot_id, entry["summary"], 2.0, add_phrases=True)

            for xref in entry["cross_references"]:
                _index_phrase(slot_id, xref, 2.2, is_code_tag=True)
                tag_to_entries_tmp[xref].append(entry_id)
            tag_to_entries_tmp[entry_id].append(entry_id)

            # Extract rich text from records (supports single-row and multi-row JSONL)
            for rec in entry["records"]:
                if isinstance(rec.get("input"), str):
                    tok_total += _index_text(slot_id, rec["input"], 2.5, add_phrases=True)
                if isinstance(rec.get("soul_bomb_role"), str):
                    tok_total += _index_text(slot_id, rec["soul_bomb_role"], 2.2, add_phrases=True)
                if isinstance(rec.get("exit_behavior"), str):
                    _index_phrase(slot_id, rec["exit_behavior"], 2.5)
                if isinstance(rec.get("section"), str):
                    tok_total += _index_text(slot_id, rec["section"], 2.0)
                if isinstance(rec.get("domain_primitives"), dict):
                    for k, v in rec["domain_primitives"].items():
                        tok_total += _index_text(slot_id, f"{k} {v}", 1.8, add_phrases=True)
                if isinstance(rec.get("decompression"), list):
                    for item in rec["decompression"]:
                        if isinstance(item, dict) and isinstance(item.get("mechanic"), str):
                            tok_total += _index_text(slot_id, item["mechanic"], 1.8, add_phrases=True)
                if isinstance(rec.get("analysis"), dict):
                    for claim in rec["analysis"].get("claims", ()):
                        if isinstance(claim, dict):
                            if isinstance(claim.get("claim_id"), str):
                                _index_phrase(slot_id, claim["claim_id"], 5.0)
                            if isinstance(claim.get("text"), str):
                                tok_total += _index_text(slot_id, claim["text"], 1.5)
                if isinstance(rec.get("functional_departments"), list):
                    for fd in rec["functional_departments"]:
                        if isinstance(fd, dict) and isinstance(fd.get("mapping"), str):
                            tok_total += _index_text(slot_id, fd["mapping"], 1.0)

            slots[slot_id] = RackSlot(
                slot_id=slot_id,
                kind="compiled_entry",
                key=entry_id,
                title=entry["title"],
                tags=entry["cross_references"],
                token_count=tok_total,
            )

        # Index all 14+ invariant catalog classes
        invariant_specs: dict[str, dict[str, Any]] = {}
        for inv_cls, spec in INVARIANT_CLASS_SIGNATURES.items():
            cls_key = inv_cls.value
            slot_id = f"invariant:{cls_key}"
            invariant_specs[cls_key] = {
                "invariant_class": cls_key,
                "required_primitives": tuple(spec["required_primitives"]),
                "supporting_primitives": tuple(spec["supporting_primitives"]),
                "cues": tuple(spec["cues"]),
            }
            tok_total = 0
            _index_phrase(slot_id, cls_key, 7.0)
            _index_phrase(slot_id, cls_key.replace("_", " "), 6.5)
            tok_total += _index_text(slot_id, cls_key.replace("_", " "), 3.5, add_phrases=True)
            for prim in spec["required_primitives"]:
                _index_phrase(slot_id, prim.replace("_", " "), 2.5)
            for prim in spec["supporting_primitives"]:
                _index_phrase(slot_id, prim.replace("_", " "), 1.2)
            for cue in spec["cues"]:
                _index_phrase(slot_id, cue, 4.5)
                tok_total += _index_text(slot_id, cue, 2.8)

            slots[slot_id] = RackSlot(
                slot_id=slot_id,
                kind="invariant_class",
                key=cls_key,
                title=cls_key.replace("_", " ").title(),
                tags=tuple(spec["required_primitives"]),
                token_count=tok_total,
            )

        # Compute per-kind IDF scaling so discriminative tokens outrank boilerplate
        kind_counts: dict[str, int] = defaultdict(int)
        # Explicit-only entries are indexed for ID summoning but excluded from
        # compiled-entry IDF so adding them cannot reweight lift competitions
        # among lift-eligible entries (2026-11-25h: seven PoE entries flipped
        # a 1.7% DIVINE-RLHF vs DOMAIN-EXPANSION race on an autonomy prompt).
        lift_eligible_entry_count = 0
        for s in slots.values():
            kind_counts[s.kind] += 1
            if s.kind == "compiled_entry" and s.key not in EXPLICIT_ONLY_ENTRY_HINTS:
                lift_eligible_entry_count += 1

        token_index: dict[str, tuple[tuple[str, float], ...]] = {}
        for tok, slot_scores in raw_token_weights.items():
            df_by_kind: dict[str, int] = defaultdict(int)
            df_entry_eligible = 0
            for sid in slot_scores:
                kind = slots[sid].kind
                df_by_kind[kind] += 1
                if kind == "compiled_entry" and slots[sid].key not in EXPLICIT_ONLY_ENTRY_HINTS:
                    df_entry_eligible += 1
            postings: list[tuple[str, float]] = []
            for sid, base_w in slot_scores.items():
                kind = slots[sid].kind
                if kind == "compiled_entry":
                    n_kind = max(lift_eligible_entry_count, 1)
                    df = df_entry_eligible
                else:
                    n_kind = max(kind_counts[kind], 1)
                    df = df_by_kind[kind]
                idf = math.log((n_kind + 1.0) / (df + 1.0)) + 1.0
                postings.append((sid, round(base_w * idf, 6)))
            postings.sort(key=lambda pair: (-pair[1], pair[0]))
            token_index[tok] = tuple(postings)

        phrase_index: dict[str, tuple[tuple[str, float], ...]] = {}
        for phrase, slot_scores in raw_phrase_weights.items():
            postings = sorted(
                ((sid, round(w, 6)) for sid, w in slot_scores.items()),
                key=lambda pair: (-pair[1], pair[0]),
            )
            phrase_index[phrase] = tuple(postings)

        # Finalize tag_to_entries with deduplication
        tag_to_entries: dict[str, tuple[str, ...]] = {
            k: tuple(dict.fromkeys(v)) for k, v in tag_to_entries_tmp.items()
        }

        # Commit atomically
        self._slots = slots
        self._domain_templates = templates
        self._compiled_entries = compiled_entries
        self._invariant_specs = invariant_specs
        self._token_index = token_index
        self._phrase_index = phrase_index
        self._tag_to_entries = tag_to_entries
        self._entry_to_domain_hint = entry_to_domain_hint
        self._domain_comp_depts = domain_comp_depts
        self._domain_comp_prims = domain_comp_prims
        self._domain_comp_tokens = domain_comp_tokens
        self._domain_dept_comps = domain_dept_comps
        self._domain_invariants_classes = domain_invariants_classes
        self._domain_tags = domain_tags
        self._base_model_cache.clear()
        self._signature = sig
        self._last_sig_check_monotonic = time.monotonic()
        self._built = True
        self.build_count += 1
        self.last_build_ms = round((time.perf_counter() - t0) * 1000.0, 3)

    # -- Introspection properties -------------------------------------------

    @property
    def slots(self) -> dict[str, RackSlot]:
        with self._lock:
            self._ensure_ready()
            return dict(self._slots)

    @property
    def domain_names(self) -> tuple[str, ...]:
        with self._lock:
            self._ensure_ready()
            return tuple(sorted(self._domain_templates.keys()))

    @property
    def compiled_entry_ids(self) -> tuple[str, ...]:
        with self._lock:
            self._ensure_ready()
            return tuple(sorted(self._compiled_entries.keys()))

    @property
    def stats(self) -> dict[str, Any]:
        with self._lock:
            self._ensure_ready()
            return {
                "built": self._built,
                "build_count": self.build_count,
                "disk_read_count": self.disk_read_count,
                "query_count": self.query_count,
                "last_build_ms": self.last_build_ms,
                "domain_slots": len(self._domain_templates),
                "compiled_entry_slots": len(self._compiled_entries),
                "invariant_class_slots": len(self._invariant_specs),
                "total_slots": len(self._slots),
                "token_postings": len(self._token_index),
                "phrase_postings": len(self._phrase_index),
            }

    def get_template(self, domain: str) -> DomainTemplate:
        """O(1) direct template lookup from the in-memory rack."""
        with self._lock:
            self._ensure_ready()
            if domain in self._domain_templates:
                return self._domain_templates[domain]
            if "universal_generic" in self._domain_templates:
                return self._domain_templates["universal_generic"]
            raise KeyError(f"Unknown domain {domain!r} and no universal_generic fallback found")

    def _get_cached_base_model(self, domain: str) -> dict[str, Any]:
        with self._lock:
            cached = self._base_model_cache.get(domain)
            if cached is None:
                tmpl = self.get_template(domain)
                cached = _build_v2_2_model(tmpl)
                self._base_model_cache[domain] = cached
            return _clone_system_model(cached)

    # -- 1. O(1) Elevator Summon --------------------------------------------

    def summon(
        self,
        query: str | SemanticPacket,
        *,
        top_k: int = 3,
        include_compiled_entries: bool = True,
        include_invariants: bool = True,
    ) -> BayDelivery:
        """Deliver ONLY the matched domain(s), compiled entries, invariants, and model to the bay."""
        if isinstance(query, SemanticPacket):
            query_text = query.raw_input or ""
        elif isinstance(query, str):
            query_text = query
        else:
            raise TypeError(f"query must be str or SemanticPacket, got {type(query).__name__}")

        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError(f"top_k must be a positive int, got {top_k!r}")

        t0 = time.perf_counter()
        # Discriminative routing verdict over the same index (outside the lock).
        from semantic_compiler.expansion.router import ABSTAIN, ENTRY_LIFT_TIE_RATIO, DomainRouter, _is_filler

        pre_ready = self._ensure_ready()
        router = self.__dict__.get("_router")
        if router is None:
            router = self.__dict__.setdefault("_router", DomainRouter(self))
        routing = router.route(query_text, top_k=top_k)
        tokens, content_stream, raw_stream = _tokenize_all(query_text)
        # Filler words (pronouns, chat verbs, "because", "new", ...) are not domain evidence.
        tokens = tuple(t for t in tokens if not _is_filler(t))
        raw_ngrams = _extract_ngrams(raw_stream, max_n=5)
        content_ngrams = _extract_ngrams(content_stream, max_n=3)
        expanded_raw: list[str] = []
        has_compound = False
        for raw in raw_stream:
            if ("-" in raw or "_" in raw) and not raw.startswith("sc-"):
                parts = [p for p in _SPLIT_RE.split(raw) if p]
                if len(parts) > 1:
                    has_compound = True
                    expanded_raw.extend(parts)
                    continue
            expanded_raw.append(raw)
        expanded_ngrams = _extract_ngrams(expanded_raw, max_n=5) if has_compound else ()
        ngrams = tuple(dict.fromkeys((*raw_ngrams, *expanded_ngrams, *content_ngrams)))

        with self._lock:
            cache_hit = self._ensure_ready() and pre_ready
            self.query_count += 1

            scores: dict[str, float] = defaultdict(float)
            matched_terms: dict[str, list[str]] = defaultdict(list)
            matched_seen: dict[str, set[str]] = defaultdict(set)

            # O(|tokens|) token posting lookups
            for tok in tokens:
                postings = self._token_index.get(tok)
                if postings:
                    for sid, weight in postings:
                        scores[sid] += weight
                        if tok not in matched_seen[sid]:
                            matched_seen[sid].add(tok)
                            matched_terms[sid].append(tok)

            # O(|ngrams|) phrase posting lookups (both stopword-preserving 2..5-grams and content 2..3-grams)
            for phrase in ngrams:
                postings = self._phrase_index.get(phrase)
                if postings:
                    for sid, weight in postings:
                        scores[sid] += weight
                        if phrase not in matched_seen[sid]:
                            matched_seen[sid].add(phrase)
                            matched_terms[sid].append(phrase)

            # Direct exact domain slug boost if query literally names a domain
            stripped_slug = query_text.strip().lower()
            if stripped_slug in self._domain_templates:
                sid = f"domain:{stripped_slug}"
                scores[sid] += 25.0
                if stripped_slug not in matched_seen[sid]:
                    matched_seen[sid].add(stripped_slug)
                    matched_terms[sid].append(stripped_slug)

            # Partition touched slots by kind (never scans untouched slots!)
            domain_hits: list[tuple[float, str]] = []
            entry_hits: list[tuple[float, str]] = []
            invariant_hits: list[tuple[float, str]] = []

            explicit_generic = "universal_generic" in stripped_slug or "universal generic" in stripped_slug
            for sid, score in scores.items():
                if score <= 0.0:
                    continue
                slot = self._slots[sid]
                if slot.kind == "domain":
                    if slot.key == "universal_generic" and not explicit_generic:
                        continue
                    domain_hits.append((score, sid))
                elif slot.kind == "compiled_entry":
                    entry_hits.append((score, sid))
                elif slot.kind == "invariant_class":
                    invariant_hits.append((score, sid))

            domain_hits.sort(key=lambda pair: (-pair[0], pair[1]))
            entry_hits.sort(key=lambda pair: (-pair[0], pair[1]))
            invariant_hits.sort(key=lambda pair: (-pair[0], pair[1]))

            # If a compiled entry matched very strongly (e.g. direct SC-LU-SAO-SUGOU-001 lookup)
            # and its home domain wasn't top-1, give its home domain a clean cross-reference lift.
            if entry_hits:
                # Lift-eligible hits only: explicit-only entries summon when named
                # but must not win or spoil the lift tournament on body tokens.
                q_lower = query_text.lower()
                lift_hits = [
                    (score, sid) for score, sid in entry_hits
                    if self._slots[sid].key not in EXPLICIT_ONLY_ENTRY_HINTS
                    or self._slots[sid].key.lower() in q_lower
                ]
                top_entry_score, top_entry_sid = (lift_hits or entry_hits)[0]
                top_entry_id = self._slots[top_entry_sid].key
                hint_domain = self._entry_to_domain_hint.get(top_entry_id)
                # EXPLICIT_ONLY entries lift their home domain only when the query names the ID
                # (same rule as DomainRouter's entry lift): "swim trunks" must not lift it.
                if hint_domain and top_entry_id in EXPLICIT_ONLY_ENTRY_HINTS and top_entry_id.lower() not in q_lower:
                    hint_domain = None
                # Near-tie with an entry homed elsewhere: no lift (same rule as DomainRouter).
                # Explicit-only opponents are ignored unless the query names them.
                if hint_domain and len(lift_hits) > 1:
                    for score_2, sid_2 in lift_hits[1:]:
                        if score_2 * ENTRY_LIFT_TIE_RATIO < top_entry_score:
                            break
                        other_id = self._slots[sid_2].key
                        if self._entry_to_domain_hint.get(other_id) != hint_domain:
                            hint_domain = None
                            break
                if hint_domain and top_entry_score >= 8.0:
                    hint_sid = f"domain:{hint_domain}"
                    boosted = scores.get(hint_sid, 0.0) + min(top_entry_score * 0.65, 12.0)
                    scores[hint_sid] = boosted
                    if top_entry_id.lower() not in matched_seen[hint_sid]:
                        matched_seen[hint_sid].add(top_entry_id.lower())
                        matched_terms[hint_sid].append(top_entry_id)
                    domain_hits = [pair for pair in domain_hits if pair[1] != hint_sid]
                    domain_hits.append((boosted, hint_sid))
                    domain_hits.sort(key=lambda pair: (-pair[0], pair[1]))

            matched_domains = tuple(
                DomainMatch(
                    domain=self._slots[sid].key,
                    score=round(score, 4),
                    matched_terms=tuple(matched_terms[sid]),
                    template=self._domain_templates[self._slots[sid].key],
                )
                for score, sid in domain_hits[:top_k]
            )
            # Out-of-domain prompts abstain instead of picking a random domain.
            # An explicit slug or a strong compiled-entry ID still counts.
            explicit_domain = stripped_slug in self._domain_templates
            if routing.outcome == ABSTAIN and not explicit_domain and not explicit_generic:
                matched_domains = ()

            primary_domain = (
                matched_domains[0].domain
                if matched_domains
                else ("universal_generic" if "universal_generic" in self._domain_templates else next(iter(self._domain_templates)))
            )
            matched_template = self._domain_templates[primary_domain]

            compiled_matches: tuple[CompiledEntryMatch, ...] = ()
            if include_compiled_entries:
                compiled_matches = tuple(
                    self._make_entry_match(self._slots[sid].key, score, matched_terms[sid])
                    for score, sid in entry_hits[:top_k]
                )

            inv_matches: tuple[InvariantMatch, ...] = ()
            if include_invariants:
                inv_matches = tuple(
                    InvariantMatch(
                        invariant_class=self._slots[sid].key,
                        score=round(score, 4),
                        matched_terms=tuple(matched_terms[sid]),
                        required_primitives=self._invariant_specs[self._slots[sid].key][
                            "required_primitives"
                        ],
                        supporting_primitives=self._invariant_specs[self._slots[sid].key][
                            "supporting_primitives"
                        ],
                    )
                    for score, sid in invariant_hits[:top_k]
                )

            system_model = self._get_cached_base_model(primary_domain)

        latency_ms = round((time.perf_counter() - t0) * 1000.0, 4)

        from semantic_compiler.expansion.deliberation import annotate_bay_delivery

        delivery = BayDelivery(
            query=query_text,
            primary_domain=primary_domain,
            matched_template=matched_template,
            matched_domains=matched_domains,
            compiled_entries=compiled_matches,
            invariant_classes=inv_matches,
            system_model=system_model,
            latency_ms=latency_ms,
            cache_hit=cache_hit,
            routing=routing,
        )
        return annotate_bay_delivery(delivery, self)

    def _make_entry_match(
        self,
        entry_id: str,
        score: float,
        terms: Sequence[str],
    ) -> CompiledEntryMatch:
        entry = self._compiled_entries[entry_id]
        from semantic_compiler.expansion.deliberation import pending_info

        record = entry["record"]
        info = pending_info(record, entry_id=entry["entry_id"])
        return CompiledEntryMatch(
            entry_id=entry["entry_id"],
            title=entry["title"],
            classification=entry["classification"],
            score=round(score, 4),
            matched_terms=tuple(terms),
            file=entry["file"],
            summary=entry["summary"],
            cross_references=entry["cross_references"],
            record=record,
            needs_review=bool(info),
        )

    # -- 2. Parking Ticket Compression & On-Demand Rehydration --------------

    def park(
        self,
        text_or_model: str | SemanticPacket | Mapping[str, Any] | Any,
        *,
        domain: str | None = None,
    ) -> SemanticTicket:
        """Compress a full domain model or raw text into a compact SemanticTicket."""
        with self._lock:
            return self._park_locked(text_or_model, domain=domain)

    def _park_locked(
        self,
        text_or_model: str | SemanticPacket | Mapping[str, Any] | Any,
        *,
        domain: str | None = None,
    ) -> SemanticTicket:
        self._ensure_ready()

        # Normalize input kind
        raw_text: str | None = None
        model_dict: Mapping[str, Any] | None = None

        if isinstance(text_or_model, SemanticTicket):
            if domain is None or domain == text_or_model.domain:
                return text_or_model
            rehydrated = self.retrieve(text_or_model)
            model_dict = rehydrated.system_model
        elif isinstance(text_or_model, SemanticPacket):
            raw_text = text_or_model.raw_input or ""
        elif isinstance(text_or_model, str):
            raw_text = text_or_model
        elif isinstance(text_or_model, Mapping):
            model_dict = text_or_model
        elif hasattr(text_or_model, "domain") and hasattr(text_or_model, "components"):
            # SystemModel dataclass support
            model_dict = {
                "domain": getattr(text_or_model, "domain"),
                "components": list(getattr(text_or_model, "components")),
                "relationships": list(getattr(text_or_model, "relationships", ())),
            }
        else:
            raise TypeError(
                "text_or_model must be str, SemanticPacket, SystemModel, SemanticTicket, or dict; "
                f"got {type(text_or_model).__name__}"
            )

        # Resolve target domain
        delivery: BayDelivery | None = None
        if domain is not None:
            if not isinstance(domain, str) or not domain.strip():
                raise ValueError("domain must be a non-empty string when explicitly provided")
            resolved_domain = domain.strip()
            if resolved_domain not in self._domain_templates:
                raise ValueError(
                    f"Unknown domain {domain!r}; available: {len(self._domain_templates)} domains"
                )
        elif model_dict is not None and isinstance(model_dict.get("domain"), str):
            resolved_domain = model_dict["domain"].strip()
            if resolved_domain not in self._domain_templates:
                resolved_domain = "universal_generic"
        else:
            delivery = self.summon(raw_text or "", top_k=3)
            resolved_domain = delivery.primary_domain

        template = self._domain_templates[resolved_domain]
        comp_names = [c["name"] for c in template.components]
        comp_name_to_idx = {name: idx for idx, name in enumerate(comp_names)}

        active_mask = 0
        extra_components: list[str] = []
        residuals: list[str] = []

        if model_dict is not None:
            canonical_src = json.dumps(model_dict, separators=(",", ":"), sort_keys=True, default=str)
            source_sha256 = hashlib.sha256(canonical_src.encode("utf-8")).hexdigest()
            input_comps = model_dict.get("components", ())
            if isinstance(input_comps, Sequence) and not isinstance(input_comps, (str, bytes)):
                for item in input_comps:
                    cname = item.get("name") if isinstance(item, Mapping) else str(item)
                    if not cname:
                        continue
                    idx = comp_name_to_idx.get(cname)
                    if idx is not None:
                        active_mask |= 1 << idx
                    elif cname not in extra_components:
                        extra_components.append(cname)
            if isinstance(model_dict.get("domain"), str) and model_dict["domain"] != resolved_domain:
                residuals.append(f"domain_remapped:{model_dict['domain']}->{resolved_domain}")
            text_for_primitives = " ".join(
                f"{c.get('name', '')} {c.get('function', '')}"
                for c in (input_comps if isinstance(input_comps, Sequence) else ())
                if isinstance(c, Mapping)
            )
            if not text_for_primitives:
                text_for_primitives = template.description
        else:
            raw_text = raw_text or ""
            source_sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            normalized_raw = raw_text.strip().lower()
            if normalized_raw in (resolved_domain, resolved_domain.replace("_", " ")):
                active_mask = (1 << len(template.components)) - 1
            else:
                q_tokens, _ = _tokenize_with_stream(raw_text)
                q_token_set = set(q_tokens)
                comp_tokens_cached = self._domain_comp_tokens[resolved_domain]
                for idx, (name_token_set, full_token_set) in enumerate(comp_tokens_cached):
                    # Activate component if name tokens overlap or >=2 function tokens overlap
                    if (name_token_set & q_token_set) or len(full_token_set & q_token_set) >= 2:
                        active_mask |= 1 << idx
                # If query matched the domain cleanly (or is empty/terse) without naming
                # individual components, park the full template skeleton so retrieve() is complete.
                if active_mask == 0 and template.components:
                    active_mask = (1 << len(template.components)) - 1
                    if not normalized_raw:
                        residuals.append("empty_input_default_skeleton")
            text_for_primitives = raw_text + " " + template.description

        # Compute 15-department bitmask from active components
        dept_mask = 0
        comp_depts_map = self._domain_comp_depts[resolved_domain]
        for idx, cname in enumerate(comp_names):
            if (active_mask >> idx) & 1:
                for dept in comp_depts_map.get(cname, ()):
                    dept_mask |= 1 << _DEPT_TO_BIT[dept]

        # Collect invariant tags (template citation tags + matched invariant classes)
        tags_list: list[str] = list(self._domain_tags.get(resolved_domain, ()))
        if delivery is None and raw_text:
            delivery = self.summon(raw_text, top_k=3, include_compiled_entries=False)
        if delivery is not None:
            for inv_m in delivery.invariant_classes:
                if inv_m.invariant_class not in tags_list:
                    tags_list.append(inv_m.invariant_class)
        for inv_cls_name in self._domain_invariants_classes.get(resolved_domain, ()):
            if inv_cls_name not in tags_list:
                tags_list.append(inv_cls_name)
        invariant_tags = tuple(dict.fromkeys(tags_list))

        # Collect 17-primitive hits from active components + source text
        prim_set: list[str] = []
        seen_p: set[str] = set()
        comp_prims_map = self._domain_comp_prims[resolved_domain]
        for idx, cname in enumerate(comp_names):
            if (active_mask >> idx) & 1:
                for p in comp_prims_map.get(cname, ()):
                    if p not in seen_p:
                        seen_p.add(p)
                        prim_set.append(p)
        for p in _extract_primitives_from_text(text_for_primitives):
            if p not in seen_p:
                seen_p.add(p)
                prim_set.append(p)
        primitive_hits = tuple(p for p in PRIMITIVE_GRAMMAR_KEYS if p in seen_p)

        # Honest concise residuals
        missing_high = [
            comp["name"]
            for idx, comp in enumerate(template.components)
            if not ((active_mask >> idx) & 1) and comp.get("criticality") == "high"
        ]
        if missing_high:
            residuals.append(f"missing_high_criticality:{','.join(missing_high[:5])}")
        if resolved_domain == "soul_bomb_sovereignty":
            residuals.append("cosmological_sovereignty_absent_residual")

        version_str = str(template.version)
        extra_tuple = tuple(extra_components)
        residuals_tuple = tuple(dict.fromkeys(residuals))

        ticket_id = SemanticTicket.compute_ticket_id(
            domain=resolved_domain,
            version=version_str,
            active_mask=active_mask,
            department_mask=dept_mask,
            invariant_tags=invariant_tags,
            primitive_hits=primitive_hits,
            residuals=residuals_tuple,
            source_sha256=source_sha256,
            extra_components=extra_tuple,
        )

        return SemanticTicket(
            ticket_id=ticket_id,
            domain=resolved_domain,
            version=version_str,
            active_mask=active_mask,
            department_mask=dept_mask,
            invariant_tags=invariant_tags,
            primitive_hits=primitive_hits,
            residuals=residuals_tuple,
            source_sha256=source_sha256,
            extra_components=extra_tuple,
        )

    def retrieve(
        self,
        ticket: SemanticTicket | str | Mapping[str, Any],
    ) -> RehydratedDomain:
        """Ride the elevator to losslessly rehydrate a SemanticTicket on demand."""
        with self._lock:
            return self._retrieve_locked(ticket)

    def _retrieve_locked(
        self,
        ticket: SemanticTicket | str | Mapping[str, Any],
    ) -> RehydratedDomain:
        self._ensure_ready()

        if isinstance(ticket, SemanticTicket):
            tkt = ticket
        elif isinstance(ticket, str):
            tkt = SemanticTicket.from_json(ticket)
        elif isinstance(ticket, Mapping):
            tkt = SemanticTicket.from_dict(ticket)
        else:
            raise TypeError(
                f"ticket must be SemanticTicket, JSON str, or dict; got {type(ticket).__name__}"
            )

        residuals = list(tkt.residuals)
        if tkt.domain in self._domain_templates:
            resolved_domain = tkt.domain
        elif "universal_generic" in self._domain_templates:
            resolved_domain = "universal_generic"
            residuals.append(f"unknown_ticket_domain_fallback:{tkt.domain}->universal_generic")
        else:
            raise KeyError(
                f"Ticket domain {tkt.domain!r} not in rack and no universal_generic fallback found"
            )

        template = self._domain_templates[resolved_domain]

        active_components: list[dict[str, Any]] = []
        missing_components: list[dict[str, Any]] = []

        for idx, comp in enumerate(template.components):
            entry_comp = dict(comp)
            if (tkt.active_mask >> idx) & 1:
                active_components.append(entry_comp)
            else:
                missing_components.append(entry_comp)

        if tkt.active_mask >= (1 << len(template.components)):
            residuals.append("active_mask_exceeds_template_components")

        for extra_name in tkt.extra_components:
            active_components.append(
                {
                    "name": extra_name,
                    "function": f"Custom component preserved in ticket {tkt.ticket_id}",
                    "criticality": "medium",
                    "medical_map": "unknown",
                }
            )

        # Build 15-department mapping
        comp_depts_map = self._domain_comp_depts[resolved_domain]
        active_by_dept: dict[str, list[str]] = defaultdict(list)
        for comp in active_components:
            cname = comp["name"]
            for d in comp_depts_map.get(cname, _infer_component_departments(comp)):
                if cname not in active_by_dept[d]:
                    active_by_dept[d].append(cname)

        departments: dict[str, dict[str, Any]] = {}
        for idx, dept in enumerate(CANONICAL_DEPARTMENTS):
            bit_set = bool((tkt.department_mask >> idx) & 1)
            mapped_comps = active_by_dept.get(dept, [])
            present = bit_set or bool(mapped_comps)
            departments[dept] = {
                "department": dept,
                "state": "PRESENT" if present else "ABSENT",
                "components": mapped_comps,
            }

        # Pull linked compiled entries directly from rack in O(1)
        linked_ids: list[str] = []
        for eid in self._tag_to_entries.get(resolved_domain, ()):
            if eid in self._compiled_entries and eid not in linked_ids:
                linked_ids.append(eid)
        for tag in tkt.invariant_tags:
            for eid in self._tag_to_entries.get(tag, ()):
                if eid in self._compiled_entries and eid not in linked_ids:
                    linked_ids.append(eid)

        linked_entries = tuple(
            self._make_entry_match(eid, 1.0, (resolved_domain,))
            for eid in linked_ids
        )

        # Build valid V2.2 SystemModel from active components
        model_components: list[dict[str, Any]] = []
        for comp in active_components:
            declared = comp.get("medical_map")
            medical_map = (
                declared
                if declared in MEDICAL_ONTOLOGY
                else _COMPONENT_MEDICAL_FALLBACK.get(
                    comp["name"],
                    comp["name"] if comp["name"] in MEDICAL_ONTOLOGY else "unknown",
                )
            )
            model_components.append(
                {
                    "name": comp["name"],
                    "function": comp.get("function", ""),
                    "medical_map": medical_map,
                    "status": "inferred_by_analogy",
                    "confidence": 0.6,
                }
            )

        full_mask = (1 << len(template.components)) - 1
        if tkt.active_mask == full_mask and not tkt.extra_components:
            system_model = self._get_cached_base_model(resolved_domain)
        else:
            system_model = _build_v2_2_model(template, components=model_components)

        expanded_bytes = len(
            json.dumps(system_model, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        compression_ratio = round(expanded_bytes / max(tkt.byte_size, 1), 3)

        return RehydratedDomain(
            ticket=tkt,
            domain=resolved_domain,
            template=template,
            active_components=tuple(active_components),
            missing_components=tuple(missing_components),
            departments=departments,
            invariants=tuple(template.invariants),
            failure_modes=tuple(dict(f) for f in template.failure_modes),
            architecture_patterns=tuple(dict(a) for a in template.architecture_patterns),
            linked_compiled_entries=linked_entries,
            system_model=system_model,
            compression_ratio=compression_ratio,
            residuals=tuple(dict.fromkeys(residuals)),
        )

    # -- 3. Turntable Direct Cross-Domain Translation -----------------------

    def rotate_to(
        self,
        source_text_or_ticket: str | SemanticTicket | SemanticPacket | Mapping[str, Any] | Any,
        target_domain: str,
    ) -> TurntableTranslation:
        """Rotate source onto the turntable alongside target_domain for direct translation."""
        with self._lock:
            return self._rotate_to_locked(source_text_or_ticket, target_domain)

    def _rotate_to_locked(
        self,
        source_text_or_ticket: str | SemanticTicket | SemanticPacket | Mapping[str, Any] | Any,
        target_domain: str,
    ) -> TurntableTranslation:
        self._ensure_ready()

        if not isinstance(target_domain, str) or not target_domain.strip():
            raise ValueError("target_domain must be a non-empty string")
        target_key = target_domain.strip()
        if target_key not in self._domain_templates:
            raise ValueError(
                f"Unknown target_domain {target_domain!r}; available: {len(self._domain_templates)} domains"
            )

        # Resolve source into a SemanticTicket
        if isinstance(source_text_or_ticket, SemanticTicket):
            source_ticket = source_text_or_ticket
        elif isinstance(source_text_or_ticket, str) and source_text_or_ticket.lstrip().startswith("{"):
            # Could be serialized ticket JSON
            try:
                source_ticket = SemanticTicket.from_json(source_text_or_ticket)
            except ValueError:
                source_ticket = self.park(source_text_or_ticket)
        elif isinstance(source_text_or_ticket, Mapping) and "ticket_id" in source_text_or_ticket:
            source_ticket = SemanticTicket.from_dict(source_text_or_ticket)
        elif (
            isinstance(source_text_or_ticket, str)
            and source_text_or_ticket.strip() in self._domain_templates
        ):
            source_ticket = self.park(
                source_text_or_ticket.strip(), domain=source_text_or_ticket.strip()
            )
        else:
            source_ticket = self.park(source_text_or_ticket)

        source_key = (
            source_ticket.domain
            if source_ticket.domain in self._domain_templates
            else "universal_generic"
        )
        source_rehydrated = self.retrieve(source_ticket)
        target_template = self._domain_templates[target_key]

        src_depts_map = self._domain_comp_depts[source_key]
        src_prims_map = self._domain_comp_prims[source_key]
        tgt_depts_map = self._domain_comp_depts[target_key]
        tgt_prims_map = self._domain_comp_prims[target_key]

        mappings: list[ComponentMapping] = []
        residuals: list[str] = []
        mapped_target_names: set[str] = set()
        unmapped_source_names: list[str] = []

        src_components = source_rehydrated.active_components or tuple(
            self._domain_templates[source_key].components
        )

        for sc in src_components:
            sc_name = sc["name"]
            sc_med = str(sc.get("medical_map") or "")
            sc_univ = MEDICAL_TO_UNIVERSAL.get(sc_med, sc_med) if sc_med else ""
            sc_depts = set(src_depts_map.get(sc_name, _infer_component_departments(sc)))
            sc_prims = set(src_prims_map.get(sc_name, ()))

            best_score = 0.0
            best_tc: dict[str, Any] | None = None
            best_shared_depts: tuple[str, ...] = ()
            best_shared_univ: tuple[str, ...] = ()
            best_shared_prims: tuple[str, ...] = ()
            best_basis: list[str] = []

            for tc in target_template.components:
                tc_name = tc["name"]
                tc_med = str(tc.get("medical_map") or "")
                tc_univ = MEDICAL_TO_UNIVERSAL.get(tc_med, tc_med) if tc_med else ""
                tc_depts = set(tgt_depts_map.get(tc_name, ()))
                tc_prims = set(tgt_prims_map.get(tc_name, ()))

                score = 0.0
                basis: list[str] = []
                shared_univ: list[str] = []
                if sc_univ and tc_univ and sc_univ == tc_univ and sc_univ != "unknown":
                    score += 0.45
                    shared_univ.append(sc_univ)
                    basis.append("universal_function")

                shared_d = sorted(sc_depts & tc_depts)
                if shared_d:
                    union_d = sc_depts | tc_depts
                    score += 0.35 * (len(shared_d) / max(len(union_d), 1))
                    basis.append("department")

                shared_p = sorted(sc_prims & tc_prims)
                if shared_p:
                    union_p = sc_prims | tc_prims
                    score += 0.20 * (len(shared_p) / max(len(union_p), 1))
                    basis.append("primitive")

                if source_key == target_key and sc_name == tc_name:
                    score = 1.0
                    basis = ["exact_identity"]

                score = min(1.0, round(score, 4))
                if score > best_score:
                    best_score = score
                    best_tc = tc
                    best_shared_depts = tuple(shared_d)
                    best_shared_univ = tuple(shared_univ)
                    best_shared_prims = tuple(shared_p)
                    best_basis = basis

            if best_tc is not None and best_score >= 0.20:
                mapped_target_names.add(best_tc["name"])
                mappings.append(
                    ComponentMapping(
                        source_component=sc_name,
                        target_component=best_tc["name"],
                        shared_departments=best_shared_depts,
                        shared_universal_functions=best_shared_univ,
                        shared_primitives=best_shared_prims,
                        alignment_score=best_score,
                        mapping_basis="+".join(best_basis),
                    )
                )
            else:
                unmapped_source_names.append(sc_name)

        # Preserved invariants across source and target
        src_classes = set(self._domain_invariants_classes.get(source_key, ()))
        tgt_classes = set(self._domain_invariants_classes.get(target_key, ()))
        shared_classes = sorted(src_classes & tgt_classes)

        src_all_prims = {
            p for ps in src_prims_map.values() for p in ps
        } | set(source_ticket.primitive_hits)
        tgt_all_prims = {p for ps in tgt_prims_map.values() for p in ps}
        shared_primitives = [p for p in PRIMITIVE_GRAMMAR_KEYS if p in (src_all_prims & tgt_all_prims)]

        src_all_depts = {d for ds in src_depts_map.values() for d in ds}
        tgt_all_depts = {d for ds in tgt_depts_map.values() for d in ds}
        shared_departments = [d for d in CANONICAL_DEPARTMENTS if d in (src_all_depts & tgt_all_depts)]

        preserved_invariants: list[dict[str, Any]] = []
        for cls_name in shared_classes:
            preserved_invariants.append(
                {
                    "kind": "invariant_class",
                    "name": cls_name,
                    "required_primitives": list(
                        self._invariant_specs[cls_name]["required_primitives"]
                    ),
                }
            )
        if shared_primitives:
            preserved_invariants.append(
                {
                    "kind": "primitive_anchors",
                    "primitives": shared_primitives,
                }
            )
        if shared_departments:
            preserved_invariants.append(
                {
                    "kind": "functional_departments",
                    "departments": shared_departments,
                }
            )

        # Grounded transfer predictions via failure_modes -> target failure_modes / patterns
        transfer_predictions: list[str] = []
        target_fm_by_med: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for fm in target_template.failure_modes:
            target_fm_by_med[str(fm.get("medical_map") or "")].append(fm)
        target_ap_by_med: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for ap in target_template.architecture_patterns:
            target_ap_by_med[str(ap.get("medical_map") or "")].append(ap)

        for src_fm in self._domain_templates[source_key].failure_modes:
            med = str(src_fm.get("medical_map") or "")
            tgt_fms = target_fm_by_med.get(med, ())
            if tgt_fms:
                tgt_fm = tgt_fms[0]
                transfer_predictions.append(
                    f"Failure-mode transfer ({med}): '{source_key}.{src_fm['name']}' predicts "
                    f"counterpart hazard '{target_key}.{tgt_fm['name']}' — falsifiable by testing "
                    f"whether indicators {tgt_fm.get('indicators', [])[:2]} appear under equivalent stress."
                )
        for src_ap in self._domain_templates[source_key].architecture_patterns:
            med = str(src_ap.get("medical_map") or "")
            tgt_aps = target_ap_by_med.get(med, ())
            if tgt_aps:
                tgt_ap = tgt_aps[0]
                transfer_predictions.append(
                    f"Pattern transfer ({med}): '{source_key}.{src_ap['name']}' aligns with "
                    f"'{target_key}.{tgt_ap['name']}'."
                )
        if not transfer_predictions and mappings:
            top_m = mappings[0]
            transfer_predictions.append(
                f"Structural transfer via {top_m.mapping_basis}: perturbation of "
                f"'{source_key}.{top_m.source_component}' predicts corresponding load on "
                f"'{target_key}.{top_m.target_component}'."
            )

        # Honest residual mismatches
        if source_key != target_key:
            residuals.append(
                f"Substrate boundary: '{source_key}' -> '{target_key}' is a structural "
                "alignment via shared departments/primitives, not substrate identity "
                "(substrate_confusion_check=True)."
            )
        if unmapped_source_names:
            residuals.append(
                f"Unmapped source components in '{source_key}': {', '.join(unmapped_source_names)}"
            )
        unmapped_target_names = [
            tc["name"]
            for tc in target_template.components
            if tc["name"] not in mapped_target_names
        ]
        if unmapped_target_names:
            residuals.append(
                f"Unmapped target components in '{target_key}': {', '.join(unmapped_target_names)}"
            )
        source_only_depts = sorted(src_all_depts - tgt_all_depts)
        target_only_depts = sorted(tgt_all_depts - src_all_depts)
        if source_only_depts:
            residuals.append(
                f"Departments present in '{source_key}' but absent in '{target_key}': "
                + ", ".join(source_only_depts)
            )
        if target_only_depts:
            residuals.append(
                f"Departments present in '{target_key}' but absent in '{source_key}': "
                + ", ".join(target_only_depts)
            )
        source_only_prims = sorted(src_all_prims - tgt_all_prims)
        if source_only_prims:
            residuals.append(
                f"Primitives in '{source_key}' without direct anchor in '{target_key}': "
                + ", ".join(source_only_prims)
            )

        alignment_coverage = round(len(mappings) / max(len(src_components), 1), 4)

        return TurntableTranslation(
            source_domain=source_key,
            target_domain=target_key,
            source_ticket=source_ticket,
            component_mappings=tuple(mappings),
            preserved_invariants=tuple(preserved_invariants),
            transfer_predictions=tuple(transfer_predictions),
            residual_mismatches=tuple(residuals),
            alignment_coverage=alignment_coverage,
            substrate_confusion_check=True,
            positional_claims_permitted=True,
        )


# ---------------------------------------------------------------------------
# Process-wide singleton & convenience top-level API
# ---------------------------------------------------------------------------

_DEFAULT_ELEVATOR: DomainElevator | None = None
_DEFAULT_LOCK = threading.Lock()


def get_default_elevator() -> DomainElevator:
    """Return the lazily initialized default DomainElevator singleton."""
    global _DEFAULT_ELEVATOR
    if _DEFAULT_ELEVATOR is None:
        with _DEFAULT_LOCK:
            if _DEFAULT_ELEVATOR is None:
                _DEFAULT_ELEVATOR = DomainElevator()
    return _DEFAULT_ELEVATOR


def summon(
    query: str | SemanticPacket,
    *,
    top_k: int = 3,
    include_compiled_entries: bool = True,
    include_invariants: bool = True,
) -> BayDelivery:
    """Summon matched domains, compiled entries, invariants, and model to the bay."""
    return get_default_elevator().summon(
        query,
        top_k=top_k,
        include_compiled_entries=include_compiled_entries,
        include_invariants=include_invariants,
    )


def park(
    text_or_model: str | SemanticPacket | Mapping[str, Any] | Any,
    *,
    domain: str | None = None,
) -> SemanticTicket:
    """Compress a domain model or text into a compact deterministic SemanticTicket."""
    return get_default_elevator().park(text_or_model, domain=domain)


def retrieve(
    ticket: SemanticTicket | str | Mapping[str, Any],
) -> RehydratedDomain:
    """Rehydrate a SemanticTicket back into its full domain skeleton on demand."""
    return get_default_elevator().retrieve(ticket)


def rotate_to(
    source_text_or_ticket: str | SemanticTicket | SemanticPacket | Mapping[str, Any] | Any,
    target_domain: str,
) -> TurntableTranslation:
    """Translate a source domain/text/ticket directly onto target_domain on the turntable."""
    return get_default_elevator().rotate_to(source_text_or_ticket, target_domain)


__all__ = [
    "CANONICAL_DEPARTMENTS",
    "RackSlot",
    "DomainMatch",
    "CompiledEntryMatch",
    "InvariantMatch",
    "BayDelivery",
    "SemanticTicket",
    "RehydratedDomain",
    "ComponentMapping",
    "TurntableTranslation",
    "DomainElevator",
    "get_default_elevator",
    "summon",
    "park",
    "retrieve",
    "rotate_to",
]
