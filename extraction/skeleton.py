"""
Reflexion Semantic Compiler v2.0.0 — Structural Skeleton Extraction

Extract actors, objects, boundaries, inputs, outputs, flows, authority,
and failure modes from the semantic IR.

v2.0.1: Rewrote _extract_actors and _extract_objects with dependency-free
noun-phrase heuristics so the structural skeleton is populated from actual
entities rather than crude keyword matching.

Citation: v1.0 Spec Section 4 — Semantic IR
Citation: v1.0 Spec Section 8 — Master Pipeline, step 4.2
"""

from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------------
# Lightweight lexical resources (dependency-free)
# ---------------------------------------------------------------------------

_STOP_WORDS: set[str] = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when",
    "where", "why", "how", "what", "who", "which", "this", "that", "these",
    "those", "my", "your", "its", "their", "our", "his", "her", "their",
    "to", "of", "in", "on", "at", "by", "for", "with", "about", "against",
    "between", "into", "through", "during", "before", "after", "above",
    "below", "from", "up", "down", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "can",
    "will", "just", "should", "now", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "may",
    "might", "must", "shall", "could", "would", "i", "you", "he", "she",
    "it", "we", "they", "them", "him", "her", "us", "me", "them",
}

# Nouns the compiler sees often across its target domains.
_DOMAIN_NOUNS: set[str] = {
    # Organizational / business
    "company", "organization", "team", "department", "system", "agent",
    "service", "process", "pipeline", "model", "ai", "user", "admin",
    "manager", "founder", "board", "committee", "role", "function",
    "resource", "data", "file", "message", "packet", "record", "token",
    "key", "config", "policy", "rule", "constraint", "requirement",
    "decision", "action", "output", "input", "flow", "loop", "feedback",
    "authority", "approval", "permission", "secret", "credential",
    "project", "product", "market", "customer", "revenue", "budget",
    # Security / immune
    "threat", "risk", "attack", "defense", "immunity", "memory",
    "firewall", "security", "intruder", "pathogen", "antibody",
    # Biology / body
    "brain", "body", "cell", "membrane", "organ", "organism", "ecosystem",
    "nervous system", "immune system", "kidney", "blood", "liver", "lung",
    "heart", "muscle", "neuron", "gene", "dna", "protein", "metabolism",
    "circulatory system", "oxygen", "tissue",
    # Technology / computing
    "network", "server", "database", "queue", "cache", "worker",
    "task", "job", "request", "response", "event", "log", "metric",
    "garbage collection", "algorithm", "program", "software", "hardware",
    "telecommunications", "signal", "packet", "buffer", "address",
    "api", "api gateway", "gateway", "transport", "access",
    # Logistics / social
    "supply chain", "material", "resource", "economy", "country", "government",
    "nation", "society", "culture", "population", "city", "infrastructure",
    # General physics / cosmology
    "universe", "cosmos", "galaxy", "star", "planet", "moon", "black hole",
    "energy", "matter", "information", "entropy", "gravity", "force",
    "magnet", "magnetism", "orbit", "mass", "space", "time",
}

# Nouns that are typically animate/role-bearing actors.
_ROLE_NOUNS: set[str] = {
    "agent", "system", "user", "admin", "manager", "department", "team",
    "service", "process", "company", "organization", "founder", "board",
    "committee", "ai", "model", "worker", "subagent", "manager",
    "human", "person", "individual", "employee", "operator",
    "firewall", "security team", "immune system", "nervous system",
    "supply chain", "kidney", "brain", "heart", "economy", "government",
    "country", "nation", "city", "api gateway", "gateway",
}

# Words that signal an action performed by the preceding noun (subject).
_ACTION_VERBS: set[str] = {
    "has", "have", "had", "is", "are", "was", "were", "be", "being", "been",
    "detects", "detect", "detecting", "remembers", "remember", "remembering",
    "reads", "read", "reading", "writes", "write", "writing",
    "controls", "control", "controlling", "manages", "manage", "managing",
    "runs", "run", "running", "processes", "process", "processing",
    "sends", "send", "sending", "receives", "receive", "receiving",
    "creates", "create", "creating", "destroys", "destroy", "destroying",
    "approves", "approve", "approving", "routes", "route", "routing",
    "monitors", "monitor", "monitoring", "gates", "gate", "gating",
    "forks", "fork", "forking", "accesses", "access", "accessing",
    "modifies", "modify", "modifying", "owns", "own", "owning",
    "uses", "use", "using", "requires", "require", "requiring",
    "logs", "log", "logging", "checks", "check", "checking",
    "stores", "store", "storing", "loads", "load", "loading",
    "notifies", "notify", "notifying", "updates", "update", "updating",
    "deletes", "delete", "deleting", "filters", "filter", "filtering",
    "delivers", "deliver", "delivering", "circulates", "circulate", "circulating",
    "consolidates", "consolidate", "consolidating",
    "attracts", "attract", "attracting", "holds", "hold", "holding",
    "navigates", "navigate", "navigating", "patrols", "patrol", "patrolling",
    "argues", "argue", "arguing", "explains", "explain", "explaining",
    "works", "work", "working", "performs", "perform", "performing",
    "protects", "protect", "protecting", "attacks", "attack", "attacking",
    "defends", "defend", "defending", "enters", "enter", "entering",
    "leaves", "leave", "leaving",
}

# Common prepositions and analogy markers; nouns following these are often objects/inputs.
_PREPOSITIONS: set[str] = {
    "of", "in", "on", "at", "by", "for", "with", "to", "from", "into",
    "through", "during", "before", "after", "above", "below", "about",
    "against", "between", "under", "over", "via", "like", "as",
}

# Suffixes that commonly indicate English nouns.
# Conservative list: avoids false positives from verbs ending in -er/-or.
_NOUN_SUFFIXES: tuple[str, ...] = (
    "tion", "sion", "ment", "ness", "ity", "ism", "ure", "age",
    "dom", "ship", "hood", "ence", "ance",
)

# Determiners that precede objects.
_DETERMINERS: set[str] = {"the", "a", "an", "this", "that", "these", "those"}

# Words that break noun-phrase continuity (conjunctions and phrase boundaries).
_CONJUNCTIONS: set[str] = {"and", "or", "but", "nor", "yet", "so", "for"}

# Combined set of words that cannot appear inside a noun phrase.
_PHRASE_BREAKERS: set[str] = _PREPOSITIONS | _CONJUNCTIONS | _ACTION_VERBS | _STOP_WORDS

# Determiners are allowed inside phrases (e.g. "the immune system"), but most
# other stop words, prepositions, conjunctions and verb forms break continuity.
_INTERNAL_BREAKERS: set[str] = _PHRASE_BREAKERS - _DETERMINERS

# A grammatical subject cannot begin with a preposition, conjunction, or
# non-determiner stop word.  Determiners are allowed so "the X" can resolve to X.
_SUBJECT_START_FORBIDDEN: set[str] = (
    _PREPOSITIONS | _CONJUNCTIONS | (_STOP_WORDS - _DETERMINERS)
)


# ---------------------------------------------------------------------------
# Tokenization helpers
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-]*")


def _tokenize(text: str) -> list[str]:
    """Extract alphabetic tokens, preserving hyphenated words and stripping possessives."""
    # Normalize possessives so "brain's memory" becomes "brain memory".
    text = re.sub(r"\b(\w+)'s\b", r"\1", text)
    return _WORD_RE.findall(text)


def _singular_form(word: str) -> str:
    """Simple rule-based singularization for common English plurals."""
    lower = word.lower()
    if lower.endswith("ies") and len(lower) > 3:
        return lower[:-3] + "y"
    if lower.endswith("s") and not lower.endswith("ss") and len(lower) > 2:
        return lower[:-1]
    return lower


def _is_likely_noun(word: str) -> bool:
    """Heuristic noun detector using domain lexicon and suffix rules."""
    lower = word.lower()
    if lower in _STOP_WORDS:
        return False
    singular = _singular_form(lower)
    if lower in _DOMAIN_NOUNS or singular in _DOMAIN_NOUNS:
        return True
    if lower in _ROLE_NOUNS or singular in _ROLE_NOUNS:
        return True
    if any(lower.endswith(suffix) or singular.endswith(suffix) for suffix in _NOUN_SUFFIXES):
        return True
    # Allow capitalized mid-sentence words to count as nouns (proper nouns).
    if word[0].isupper():
        return True
    return False


def _phrase_is_acceptable(words: list[str]) -> bool:
    """
    Accept a noun phrase if its final word is noun-like or if the whole
    joined phrase is a known multi-word domain/role noun (e.g. "supply chain").
    """
    if not words:
        return False
    final = words[-1]
    if _is_likely_noun(final):
        return True
    joined = " ".join(w.lower() for w in words)
    if joined in _DOMAIN_NOUNS or joined in _ROLE_NOUNS:
        return True
    singular_joined = " ".join(_singular_form(w) for w in words)
    if singular_joined in _DOMAIN_NOUNS or singular_joined in _ROLE_NOUNS:
        return True
    return False


def _extract_noun_phrases(tokens: list[str]) -> list[str]:
    """
    Extract candidate noun phrases up to trigrams.

    A phrase is kept when its final word looks like a noun. This avoids
    keeping stray adjectives while preserving simple compounds such as
    "immune system" or "threat detection".
    """
    phrases: list[str] = []
    seen: set[str] = set()
    n = len(tokens)

    for i in range(n):
        if tokens[i].lower() in _STOP_WORDS:
            continue

        phrase_words: list[str] = []
        for j in range(i, min(i + 3, n)):
            word = tokens[j]
            if word.lower() in _STOP_WORDS and j > i:
                break
            phrase_words.append(word)
            final_word = phrase_words[-1]
            if _is_likely_noun(final_word):
                phrase = " ".join(w.lower() for w in phrase_words)
                if phrase not in seen:
                    seen.add(phrase)
                    phrases.append(phrase)

    return phrases


def _strip_determiners(words: list[str]) -> list[str]:
    """Drop leading determiners from a token list."""
    idx = 0
    while idx < len(words) and words[idx].lower() in _DETERMINERS:
        idx += 1
    return words[idx:]


def _phrase_key(words: list[str]) -> str:
    """Canonical lower-case phrase string with determiners stripped."""
    stripped = _strip_determiners(words)
    if not stripped:
        return ""
    return " ".join(w.lower() for w in stripped)


def _extract_subject_phrases(tokens: list[str]) -> list[str]:
    """
    Find noun phrases that immediately precede action verbs.
    These are the grammatical subjects / actors of the sentence.
    """
    n = len(tokens)
    subjects: list[str] = []
    seen: set[str] = set()

    for start in range(n):
        if tokens[start].lower() in _SUBJECT_START_FORBIDDEN:
            continue
        for end in range(start + 1, min(start + 4, n + 1)):
            # A subject must immediately precede an action verb.
            if end >= n or tokens[end].lower() not in _ACTION_VERBS:
                continue
            # The phrase must be a recognizable noun phrase.
            candidate = tokens[start:end]
            if not _phrase_is_acceptable(candidate):
                continue
            # Internal continuity: do not let the phrase cross prepositions,
            # conjunctions, verb forms, or other non-determiner breakers.
            internal = candidate[:-1]
            if any(t.lower() in _INTERNAL_BREAKERS for t in internal):
                continue
            phrase = _phrase_key(candidate)
            if not phrase or phrase in seen:
                continue
            seen.add(phrase)
            subjects.append(phrase)

    return _prune_subsumed_unigrams(subjects)


def _extract_object_phrases(tokens: list[str]) -> list[str]:
    """
    Find noun phrases that immediately follow action verbs, prepositions,
    or determiners. These are the grammatical objects / things being acted
    upon. Phrases that are also subjects are excluded.
    """
    n = len(tokens)
    objects: list[str] = []
    seen: set[str] = set()
    subject_phrases = set(_extract_subject_phrases(tokens))

    for start in range(1, n):
        prev = tokens[start - 1].lower()
        if prev not in _ACTION_VERBS and prev not in _PREPOSITIONS and prev not in _DETERMINERS:
            continue

        for end in range(start + 1, min(start + 4, n + 1)):
            candidate = tokens[start:end]
            if not _phrase_is_acceptable(candidate):
                continue
            # Do not let a noun phrase cross prepositions, conjunctions,
            # verb forms, or other non-determiner phrase-breaking words.
            internal = candidate[:-1]
            if any(t.lower() in _INTERNAL_BREAKERS for t in internal):
                continue
            phrase = _phrase_key(candidate)
            if not phrase or phrase in seen:
                continue
            # Skip if any word of this phrase is already captured by a subject.
            if any(_is_subsumed(word, list(subject_phrases)) for word in phrase.split()):
                continue
            seen.add(phrase)
            objects.append(phrase)

    return _prune_subsumed_unigrams(objects)


def _is_subsumed(word: str, phrases: list[str]) -> bool:
    """Return True if word already appears as a standalone or compound phrase."""
    for phrase in phrases:
        words = phrase.split()
        if word.lower() in (w.lower() for w in words):
            return True
    return False


def _prune_subsumed_unigrams(phrases: list[str]) -> list[str]:
    """
    Remove unigram phrases that are fragments of longer phrases in the list.

    A unigram is kept only if it is not a substring of any longer phrase
    already in the list.  Proper nouns are preserved because they refer to
    distinct named entities, but generic role nouns (e.g. "system" inside
    "immune system") are dropped to avoid substring duplication.
    """
    phrase_words: set[str] = set()
    for phrase in phrases:
        words = phrase.split()
        if len(words) > 1:
            phrase_words.update(w.lower() for w in words)

    kept: list[str] = []
    for phrase in phrases:
        words = phrase.split()
        if len(words) == 1:
            lower = phrase.lower()
            # Proper nouns may refer to distinct entities; keep them even if
            # they happen to match a word inside a longer phrase.
            if phrase[0].isupper():
                kept.append(phrase)
                continue
            if lower in phrase_words:
                continue
        kept.append(phrase)
    return kept


def _extract_actors(packet: Any) -> list[str]:
    """
    Extract actor references from raw input.

    Actors are entities that perform actions. Primary signal is a noun phrase
    immediately preceding an action verb. Proper nouns and explicit role nouns
    that are not already captured as part of a phrase are added as fallbacks.
    """
    text = packet.raw_input or ""
    tokens = _tokenize(text)
    n = len(tokens)
    actors: list[str] = []
    seen: set[str] = set()

    # 1. Subject phrases are the strongest actor signal.
    subject_phrases = _extract_subject_phrases(tokens)
    object_phrases = _extract_object_phrases(tokens)
    all_phrases = subject_phrases + object_phrases
    for phrase in subject_phrases:
        seen.add(phrase)
        actors.append(phrase)

    # 2. Proper nouns and explicit role nouns as fallbacks.
    for i, token in enumerate(tokens):
        lower = token.lower()
        if lower in _STOP_WORDS:
            continue
        canonical = token if token[0].isupper() else lower
        if canonical in seen:
            continue

        is_actor = False
        if i > 0 and token[0].isupper():
            is_actor = True
        elif lower in _ROLE_NOUNS:
            is_actor = True

        # Avoid adding a standalone noun that is just a fragment of an
        # already-extracted phrase (e.g. "system" from "immune system" or
        # "Whis" from "mail from Whis").
        if is_actor and not _is_subsumed(lower, all_phrases):
            seen.add(canonical)
            actors.append(canonical)

    return actors


def _extract_objects(packet: Any) -> list[str]:
    """
    Extract object references from raw input.

    Objects are entities that are acted upon. Primary signal is a noun phrase
    immediately following an action verb or preposition.
    """
    text = packet.raw_input or ""
    tokens = _tokenize(text)
    objects: list[str] = []
    seen: set[str] = set()

    # Object phrases after verbs/prepositions.
    for phrase in _extract_object_phrases(tokens):
        seen.add(phrase)
        objects.append(phrase)

    return objects


# ---------------------------------------------------------------------------
# Public skeleton API
# ---------------------------------------------------------------------------

def extract_structural_skeleton(packet: Any) -> dict[str, Any]:
    """
    Extract the structural skeleton from the packet.

    The skeleton is the abstract structure of the system being described,
    independent of any particular domain vocabulary.

    Citation: v1.0 Spec Section 8 — Master Pipeline, step 4.2
    """
    sir = packet.semantic_ir

    return {
        "actors": list(sir.actors) if sir.actors else _extract_actors(packet),
        "objects": list(sir.objects) if sir.objects else _extract_objects(packet),
        "boundaries": list(sir.boundaries) if sir.boundaries else [],
        "inputs": list(sir.inputs) if sir.inputs else [],
        "outputs": list(sir.outputs) if sir.outputs else [],
        "flows": list(sir.flows) if sir.flows else [],
        "authority": [
            av for av in sir.authority_vectors
        ] if sir.authority_vectors else [],
        "failure_modes": list(sir.failure_modes) if sir.failure_modes else [],
        "control_loops": list(sir.control_loops) if sir.control_loops else [],
        "feedback_loops": list(sir.feedback_loops) if sir.feedback_loops else [],
        "resources": list(sir.resources) if sir.resources else [],
        "forces": list(sir.forces) if sir.forces else [],
    }


def build_semantic_ir(packet: Any) -> Any:
    """
    Build the Semantic Intermediate Representation from the packet.
    Citation: v1.0 Spec Section 8 — Master Pipeline, step 3.1
    """
    from semantic_compiler.core.semantic_ir import SemanticIR

    sir = packet.semantic_ir

    # Populate claims from claim_types (rebuild each call to stay idempotent).
    sir.claims = []
    for i, ct in enumerate(packet.claim_types):
        sir.claims.append({
            "claim_id": ct.get("claim_id") or f"claim-{i}",
            "content": ct.get("content", packet.raw_input or ""),
            "claim_type": ct.get("claim_type", "OBSERVATION"),
            "confidence": ct.get("confidence", 0.5),
        })

    # Populate evidence
    sir.evidence = list(packet.evidence_inventory)

    # Populate constraints and unknowns
    sir.constraints = list(packet.declared_constraints)
    sir.unknowns = list(packet.unknowns)
    sir.rejected_assumptions = list(packet.rejected_assumptions)

    # Populate source frames
    sir.source_frames = list(packet.source_frames)

    return sir
