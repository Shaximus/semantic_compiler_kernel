"""
Discriminative domain router over the DomainElevator index.

The elevator's ``summon()`` ranks every slot that shares any indexed token with
the query, so ordinary prompts were "routed" on words such as "because",
"new", "my" or "draft". This router reads the same inverted index but:

* suppresses filler words (pronouns, auxiliaries, chat verbs, vague
  adjectives), while never stripping negation or relational words
  (``PROTECTED_RELATIONAL_WORDS``): they stay in the phrase stream;
* ignores tokens that are not discriminative across domains (present in too
  many domain templates), on top of the index's per-kind IDF weights;
* is phrase-aware: multi-word index phrases score above loose tokens;
* recognizes analogy structure ("X is like Y"): the subject clause X is
  weighted above the analogy source Y;
* returns ranked candidates with a routing confidence, the top-1 vs top-2
  margin, and an explicit outcome: ROUTED, AMBIGUOUS or ABSTAIN.

Routing confidence is a separate threshold from compilation structural fit
(``core.scoring.STRUCTURAL_FIT_MIN``); this module never touches fit.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from semantic_compiler.expansion.elevator import (
    _STOPWORDS,
    _TOKEN_RE,
    DomainElevator,
    _extract_ngrams,
    _get_router_keywords,
    _normalize_singular,
    get_default_elevator,
)

ROUTED = "ROUTED"
AMBIGUOUS = "AMBIGUOUS"
ABSTAIN = "ABSTAIN"

# Negation and relational words carry meaning ("not a moral test", "before
# paperwork"). They are never removed from the phrase stream, and never count
# as standalone domain evidence.
PROTECTED_RELATIONAL_WORDS: frozenset[str] = frozenset(
    {"not", "without", "before", "after", "only", "never", "no", "unless", "except"}
)

# Words that say nothing about a domain. Query-side only: the index is unchanged.
FILLER_WORDS: frozenset[str] = frozenset(
    {
        # pronouns / determiners
        "i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself",
        "he", "him", "his", "she", "her", "hers", "we", "us", "our", "ours",
        "they", "them", "their", "theirs", "it", "its", "this", "that", "these",
        "those", "someone", "something", "anything", "everything", "nothing",
        "anyone", "everyone", "thing", "things", "stuff", "one", "ones",
        # auxiliaries / modals
        "am", "is", "are", "was", "were", "be", "been", "being", "do", "does",
        "did", "doing", "have", "has", "had", "can", "could", "would", "should",
        "will", "shall", "may", "might", "must", "ll", "ve", "re", "don", "doesn",
        "didn", "isn", "aren", "wasn", "won", "can't", "cannot",
        # chat / request verbs
        "please", "thanks", "thank", "hi", "hello", "hey", "ok", "okay", "yes",
        "yeah", "sure", "get", "gets", "got", "getting", "make", "makes", "made",
        "want", "wants", "need", "needs", "help", "tell", "know", "think", "say",
        "said", "go", "goes", "going", "come", "let", "put", "take", "give",
        "see", "look", "find", "show", "explain", "summarize", "remind", "ask",
        "write", "draft", "reply", "send", "call", "talk", "try", "keep", "seem",
        "seems", "happen", "happens", "mean", "means", "like", "likes",
        # vague modifiers / time words
        "just", "really", "very", "so", "too", "also", "still", "even", "much",
        "many", "lot", "lots", "some", "any", "all", "every", "because", "since",
        "why", "how", "what", "when", "where", "who", "which", "whether", "about",
        "new", "old", "last", "next", "first", "good", "bad", "best", "better",
        "worse", "big", "small", "little", "faster", "slower", "fast", "slow",
        "quick", "quickly", "today", "tomorrow", "yesterday", "tonight", "now",
        "here", "there", "again", "maybe", "always", "usually", "sometimes",
        "way", "ways", "kind", "sort", "pretty", "quite", "actually", "basically",
        "lately", "recently", "anyway", "else", "other", "another", "same",
        "different", "right", "wrong", "true", "false", "real", "whole",
        "turn", "off", "set", "use", "using", "able", "via", "per", "etc",
    }
) - PROTECTED_RELATIONAL_WORDS

# A token present in more than this share of domain templates is not
# discriminative and is ignored as standalone evidence.
MAX_DOMAIN_DF_SHARE = 0.25
# Multi-word phrase matches are stronger evidence than loose tokens.
PHRASE_BOOST = 1.5
# Analogy subject clause weight vs. the analogy source clause.
SUBJECT_CLAUSE_WEIGHT = 1.25
SOURCE_CLAUSE_WEIGHT = 0.8

# Routing thresholds (routing confidence, NOT compilation fit).
MIN_ROUTE_SCORE = 16.0          # top-1 raw score floor
MIN_EVIDENCE_UNITS = 2          # distinct matched terms, unless a phrase or a specific term matched
SPECIFIC_TERM_MAX_DF = 2        # a term found in <= this many domains is specific evidence on its own
SPECIFIC_SINGLE_MIN_SCORE = 20.0  # ...but only if it scores at least this much
MIN_CONFIDENCE = 0.35           # routing confidence floor for ROUTED
AMBIGUITY_MARGIN = 0.15         # (top1 - top2) / top1 below this => AMBIGUOUS
CONFIDENCE_SATURATION = 25.0    # score at which evidence strength saturates
# Context anchors: a curated, high-precision domain keyword (expansion._DOMAIN_KEYWORDS,
# e.g. "spirit bomb", "chain of trust") names the frame the text is set in, so the
# anchored domain's score is multiplied by this factor.
ANCHOR_BOOST = 2.0
_BUILDCRAFT_ANCHOR_WORDS = frozenset({
    "gem", "gems", "weapon", "weapons", "armor", "armour", "slot", "slots", "link",
    "mana", "mirror", "character", "doll", "build", "builds", "bow", "projectiles",
    "socket", "sockets", "race", "maps", "league", "kalandra",
})
# A literal compiled-entry ID in the text routes to the entry's home domain.
EXPLICIT_ENTRY_SCORE = 25.0
_SC_ID_RE = re.compile(r"\bSC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}\b", re.IGNORECASE)

_ANALOGY_MARKER = re.compile(
    r"(?:(?<!\bwould )(?<!\bshould )(?<!\bmight )(?<!'d )\b(?:is|are|works|behaves|acts)?\s*like\b"
    r"|\b(?:acts as|act as|as if|similar to|analogous to)\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DomainCandidate:
    domain: str
    score: float
    confidence: float
    matched_terms: tuple[str, ...]
    phrase_matches: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "score": self.score,
            "confidence": self.confidence,
            "matched_terms": list(self.matched_terms),
            "phrase_matches": list(self.phrase_matches),
        }


@dataclass(frozen=True)
class RoutingResult:
    outcome: str                      # ROUTED | AMBIGUOUS | ABSTAIN
    domain: str | None                # set only when ROUTED
    confidence: float
    margin: float
    candidates: tuple[DomainCandidate, ...] = field(default_factory=tuple)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "domain": self.domain,
            "confidence": self.confidence,
            "margin": self.margin,
            "candidates": [c.to_dict() for c in self.candidates],
            "reason": self.reason,
        }


def _confidence(score: float, top: float, second: float) -> float:
    """Evidence strength x separation from the nearest rival, in [0, 1]."""
    strength = min(1.0, score / CONFIDENCE_SATURATION)
    rival = second if score >= top else top
    separation = max(0.0, (score - rival) / score) if score > 0 else 0.0
    return round(strength * (0.5 + 0.5 * separation), 4)


def _is_filler(tok: str) -> bool:
    return tok in FILLER_WORDS or (tok in _STOPWORDS and tok not in PROTECTED_RELATIONAL_WORDS)


def _query_units(text: str) -> tuple[list[str], list[str]]:
    """Return (evidence tokens, phrase candidates) for one clause of the query."""
    raw = _TOKEN_RE.findall(text.lower())
    tokens: list[str] = []
    seen: set[str] = set()
    for tok in raw:
        if len(tok) < 2 or _is_filler(tok) or tok in PROTECTED_RELATIONAL_WORDS:
            continue
        for t in (tok, _normalize_singular(tok)):
            if t and t not in seen:
                seen.add(t)
                tokens.append(t)
        if "-" in tok or "_" in tok:
            for part in re.split(r"[-_]+", tok):
                if len(part) >= 2 and not _is_filler(part) and part not in seen:
                    seen.add(part)
                    tokens.append(part)
    # Phrase stream: drop filler, KEEP protected relational words.
    content = [t for t in raw if len(t) >= 2 and not _is_filler(t)]
    # Index-compatible content stream (index content streams drop all stopwords).
    index_content = [t for t in raw if len(t) >= 2 and t not in _STOPWORDS]
    phrases = list(dict.fromkeys((
        *_extract_ngrams(raw, max_n=5),
        *_extract_ngrams(content, max_n=3),
        *_extract_ngrams(index_content, max_n=3),
    )))
    return tokens, phrases


class DomainRouter:
    """Discriminative, abstaining router over a DomainElevator's index."""

    def __init__(self, elevator: DomainElevator | None = None) -> None:
        self._elevator = elevator if elevator is not None else get_default_elevator()
        self._df_cache_build: int | None = None
        self._domain_df: dict[str, int] = {}
        self._n_domains = 1
        self._anchor_patterns: list[tuple[str, str, re.Pattern[str]]] | None = None

    def _refresh_df(self) -> None:
        el = self._elevator
        el._ensure_ready()
        if self._df_cache_build == el.build_count:
            return
        domain_df: dict[str, int] = {}
        for tok, postings in el._token_index.items():
            domain_df[tok] = sum(1 for sid, _w in postings if sid.startswith("domain:"))
        self._domain_df = domain_df
        self._n_domains = max(1, sum(1 for s in el._slots.values() if s.kind == "domain"))
        self._df_cache_build = el.build_count

    def _anchors(self, text: str) -> dict[str, list[str]]:
        if self._anchor_patterns is None:
            pats = []
            for domain, kws in _get_router_keywords():
                for kw in kws:
                    kw_l = kw.lower()
                    if kw_l.startswith("sc-"):
                        continue
                    pats.append((domain, kw_l, re.compile(
                        r"(?<![a-z0-9])" + re.escape(kw_l).replace(r"\ ", r"[\s\-]+") + r"(?:s|es)?(?![a-z0-9])"
                    )))
            # Buildcraft (PoE -> compute) triggers anchor ci_build_invariants, the
            # domain derived from that ontology; only the PoE-specific ones.
            from semantic_compiler.registry.buildcraft import BUILDCRAFT_MAPPINGS

            for mapping in BUILDCRAFT_MAPPINGS:
                for trig in mapping.triggers:
                    t = trig.lower()
                    if " " in t and set(re.split(r"[\s\-]+", t)) & _BUILDCRAFT_ANCHOR_WORDS:
                        pats.append(("ci_build_invariants", t, re.compile(
                            r"(?<![a-z0-9])" + re.escape(t).replace(r"\ ", r"[\s\-]+") + r"(?![a-z0-9])"
                        )))
            self._anchor_patterns = pats
        lowered = text.lower()
        found: dict[str, list[str]] = defaultdict(list)
        for domain, kw, pat in self._anchor_patterns:
            if domain != "universal_generic" and pat.search(lowered):
                found[domain].append(kw)
        return found

    def _discriminative(self, tok: str) -> bool:
        df = self._domain_df.get(tok, 0)
        return 0 < df <= max(1, int(self._n_domains * MAX_DOMAIN_DF_SHARE))

    def _score_clause(
        self,
        text: str,
        weight: float,
        scores: dict[str, float],
        terms: dict[str, list[str]],
        phrases_hit: dict[str, list[str]],
        entry_scores: dict[str, float],
    ) -> None:
        el = self._elevator
        tokens, phrases = _query_units(text)
        for tok in tokens:
            if not self._discriminative(tok):
                continue
            for sid, w in el._token_index.get(tok, ()):
                if sid.startswith("domain:"):
                    key = sid[7:]
                    if key == "universal_generic":
                        continue
                    scores[key] += w * weight
                    if tok not in terms[key]:
                        terms[key].append(tok)
                elif sid.startswith("entry:"):
                    entry_scores[sid[6:]] += w * weight
        for ph in phrases:
            postings = el._phrase_index.get(ph)
            if not postings:
                continue
            words = [w for w in ph.split() if not _is_filler(w) and w not in PROTECTED_RELATIONAL_WORDS]
            # A phrase must carry at least one discriminative content word.
            if not any(self._discriminative(w) or self._discriminative(_normalize_singular(w) or w) for w in words):
                continue
            for sid, w in postings:
                if sid.startswith("domain:"):
                    key = sid[7:]
                    if key == "universal_generic":
                        continue
                    scores[key] += w * PHRASE_BOOST * weight
                    if ph not in phrases_hit[key]:
                        phrases_hit[key].append(ph)
                elif sid.startswith("entry:"):
                    entry_scores[sid[6:]] += w * PHRASE_BOOST * weight

    def route(self, text: str, *, top_k: int = 3) -> RoutingResult:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        self._refresh_df()
        el = self._elevator
        scores: dict[str, float] = defaultdict(float)
        terms: dict[str, list[str]] = defaultdict(list)
        phrases_hit: dict[str, list[str]] = defaultdict(list)
        entry_scores: dict[str, float] = defaultdict(float)

        marker = _ANALOGY_MARKER.search(text)
        if marker and marker.start() > 0:
            self._score_clause(text[: marker.start()], SUBJECT_CLAUSE_WEIGHT, scores, terms, phrases_hit, entry_scores)
            self._score_clause(text[marker.end():], SOURCE_CLAUSE_WEIGHT, scores, terms, phrases_hit, entry_scores)
        else:
            self._score_clause(text, 1.0, scores, terms, phrases_hit, entry_scores)

        # Relationship recognition: a strongly matched compiled entry lifts its home domain.
        entry_lift_terms: set[str] = set()
        if entry_scores:
            top_entry, top_entry_score = max(entry_scores.items(), key=lambda kv: (kv[1], kv[0]))
            hint = el._entry_to_domain_hint.get(top_entry)
            if hint and top_entry_score >= 8.0 and hint != "universal_generic":
                scores[hint] += min(top_entry_score * 0.65, 12.0)
                entry_lift_terms.add(top_entry)
                if top_entry not in terms[hint]:
                    terms[hint].append(top_entry)

        # Explicit compiled-entry IDs (e.g. "SC-OMNI-001") name their home domain.
        for m in _SC_ID_RE.finditer(text):
            entry_id = m.group(0).upper()
            hint = el._entry_to_domain_hint.get(entry_id)
            if entry_id in el._compiled_entries and hint and hint != "universal_generic":
                scores[hint] += EXPLICIT_ENTRY_SCORE
                if entry_id not in phrases_hit[hint]:
                    phrases_hit[hint].append(entry_id)

        # Context recognition: curated anchors name the frame of the whole text.
        anchored = self._anchors(text)
        for domain, kws in anchored.items():
            if domain in scores:
                scores[domain] *= ANCHOR_BOOST
                for kw in kws:
                    if kw not in phrases_hit[domain] and kw not in terms[domain]:
                        (phrases_hit[domain] if " " in kw else terms[domain]).append(kw)

        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        if not ranked:
            return RoutingResult(ABSTAIN, None, 0.0, 0.0, (), "no discriminative domain evidence")

        proper_nouns = {
            m.group(0).lower()
            for m in re.finditer(r"(?<=[a-z0-9,;:] )[A-Z][a-z]+", text)
        }

        def units(domain: str) -> int:
            """Distinct evidence units: one per lemma, hyphen parts fold into the
            compound, and a compiled-entry lift is not counted as a unit."""
            matched = [t for t in terms[domain] if t not in entry_lift_terms]
            compounds = [t for t in matched if "-" in t or "_" in t]
            parts = {p for c in compounds for p in re.split(r"[-_]+", c)}
            lemmas = {_normalize_singular(t) or t for t in matched if t not in parts}
            return len(lemmas) + len(phrases_hit[domain])

        def qualifies(domain: str, score: float) -> bool:
            """Enough evidence to route here, ignoring rivals."""
            if score < MIN_ROUTE_SCORE:
                return False
            if phrases_hit[domain] or units(domain) >= MIN_EVIDENCE_UNITS:
                return True
            # One specific term can carry a route, but not a mid-sentence proper
            # noun (product or person names such as "Honda Civic").
            return score >= SPECIFIC_SINGLE_MIN_SCORE and any(
                self._domain_df.get(t, 99) <= SPECIFIC_TERM_MAX_DF and t not in proper_nouns
                for t in terms[domain]
            )

        top_domain, top = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        margin = (top - second) / top if top > 0 else 0.0

        candidates = tuple(
            DomainCandidate(
                domain=d,
                score=round(s, 4),
                confidence=_confidence(s, top, second),
                matched_terms=tuple(terms[d]),
                phrase_matches=tuple(phrases_hit[d]),
            )
            for d, s in ranked[:top_k]
        )
        confidence = candidates[0].confidence
        m = round(margin, 4)

        if top < MIN_ROUTE_SCORE:
            return RoutingResult(ABSTAIN, None, confidence, m, candidates,
                                 f"top score {top:.1f} below routing floor {MIN_ROUTE_SCORE}")
        if not qualifies(top_domain, top):
            return RoutingResult(ABSTAIN, None, confidence, m, candidates,
                                 "not enough discriminative evidence")
        if len(ranked) > 1 and margin < AMBIGUITY_MARGIN and qualifies(*ranked[1]):
            return RoutingResult(AMBIGUOUS, None, confidence, m, candidates,
                                 f"top-2 domains within margin {AMBIGUITY_MARGIN}")
        if confidence < MIN_CONFIDENCE:
            return RoutingResult(ABSTAIN, None, confidence, m, candidates,
                                 f"routing confidence {confidence:.2f} below {MIN_CONFIDENCE}")
        return RoutingResult(ROUTED, top_domain, confidence, m, candidates, "routed")


def get_default_router() -> DomainRouter:
    """The router bound to the default elevator (shared with summon())."""
    el = get_default_elevator()
    router = el.__dict__.get("_router")
    if router is None:
        router = el.__dict__.setdefault("_router", DomainRouter(el))
    return router


def route_domains(text: str, *, top_k: int = 3) -> RoutingResult:
    """Route text to a domain, or abstain / flag ambiguity. See module docstring."""
    return get_default_router().route(text, top_k=top_k)


__all__ = [
    "ABSTAIN", "AMBIGUOUS", "ROUTED", "FILLER_WORDS", "PROTECTED_RELATIONAL_WORDS",
    "DomainCandidate", "DomainRouter", "RoutingResult", "get_default_router", "route_domains",
]
