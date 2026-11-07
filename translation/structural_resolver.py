"""Relation-aware structural ontology resolver.

This module replaces phrase-only trigger matching with a small, deterministic
intermediate representation. It extracts concepts and typed relations from text,
then scores ontology mappings against required concepts, relation evidence,
negative evidence, and ontology-wide structural coherence.

It intentionally does not depend on a model or external NLP runtime. The output
is auditable and can later accept richer parser evidence without changing the
ontology contract.

Resolution rules worth knowing (all covered by tests):

* **Maximal munch.** When several alias phrases match overlapping tokens, the
  longest phrase wins ("weapon slots" beats "weapon"; "body armour slot" beats
  "armour"; "accelerator slot" beats "accelerator"). Without this, a slot
  concept was silently replaced by the item concept it contains, and the
  resolver produced confident wrong mappings such as "CPU socket is the body
  armour slot" -> "CPU is armour". Phrases of equal length over the same span
  all survive (an alias shared by two concepts yields both).
* **Negation.** A relation whose connector is negated ("is not", "isn't",
  "never", "without") is emitted as ``not_<relation>``. It never counts as
  support for a rule, and ``negated_rule_ids`` lets callers report that the
  source text denies the mapping instead of asserting it.
* **Strict relation kinds.** A pattern matches only relations of its own kind.
  "The LLM uses an active skill" is a ``uses`` relation and is no longer
  accepted as ``equivalent_role`` evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable, Mapping, Sequence


_TOKEN_RE = re.compile(r"[a-z0-9+./_-]+")

# Tokens that negate a relation when they sit between the two related concepts.
# Contractions are tokenized without the apostrophe ("isn't" -> "isn", "t").
_NEGATION_TOKENS = frozenset({
    "not", "no", "never", "nor", "neither", "cannot", "without",
    "isn", "aren", "wasn", "weren", "doesn", "don", "didn",
})
# Negated copulas that carry no separate "is"/"are" token after tokenization.
_NEGATED_COPULAS = frozenset({"isn", "aren", "wasn", "weren"})

_CONNECTORS = {
    "is": "equivalent_role",
    "are": "equivalent_role",
    "as": "equivalent_role",
    "uses": "uses",
    "use": "uses",
    "holds": "hosts",
    "hold": "hosts",
    "hosts": "hosts",
    "host": "hosts",
    "consumes": "consumes",
    "consume": "consumes",
    "reserves": "consumes",
    "reserve": "consumes",
    "frees": "releases",
    "free": "releases",
    "supports": "supports",
    "support": "supports",
    "links": "links",
    "linked": "links",
}

# How many following concept positions a concept may relate to.
_RELATION_WINDOW = 3


@dataclass(frozen=True)
class RelationPattern:
    """A typed relation a rule looks for between two concept groups.

    ``connectors`` is retained for backward compatibility with callers that
    construct patterns positionally; matching uses ``relation`` only, because
    relation tuples record the relation kind, not the surface connector token.
    """

    relation: str
    left: frozenset[str]
    right: frozenset[str]
    connectors: tuple[str, ...] = ("is", "are", "as", "uses", "holds", "hosts", "consumes", "frees")


@dataclass(frozen=True)
class StructuralRule:
    rule_id: str
    concepts_any: tuple[frozenset[str], ...] = ()
    concepts_all: frozenset[str] = frozenset()
    relations_any: tuple[RelationPattern, ...] = ()
    negative_concepts: frozenset[str] = frozenset()
    minimum_score: float = 0.55


@dataclass(frozen=True)
class StructuralEvidence:
    concepts: frozenset[str]
    relations: tuple[tuple[str, str, str], ...]
    spans: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class StructuralMatch:
    rule_id: str
    score: float
    evidence: tuple[str, ...]
    rejected_by: tuple[str, ...] = ()


def normalize(text: str) -> str:
    text = text.casefold().replace("’", "'").replace("–", "-").replace("—", "-")
    return " ".join(_TOKEN_RE.findall(text))


def _index_aliases(
    aliases: Mapping[str, Iterable[str]],
) -> dict[str, list[tuple[str, tuple[str, ...]]]]:
    """Index alias phrases by first token so matching is not O(tokens x phrases)."""
    index: dict[str, list[tuple[str, tuple[str, ...]]]] = {}
    for concept, phrases in aliases.items():
        for phrase in phrases:
            phrase_tokens = tuple(normalize(phrase).split())
            if phrase_tokens:
                index.setdefault(phrase_tokens[0], []).append((concept, phrase_tokens))
    return index


def _clause_positions(
    tokens: list[str],
    alias_index: Mapping[str, list[tuple[str, tuple[str, ...]]]],
) -> list[tuple[int, int, frozenset[str]]]:
    """Return non-overlapping (start, end, concepts) spans using maximal munch."""
    candidates: list[tuple[int, int, str]] = []
    for start, token in enumerate(tokens):
        for concept, phrase_tokens in alias_index.get(token, ()):
            end = start + len(phrase_tokens)
            if tokens[start:end] == list(phrase_tokens):
                candidates.append((start, end, concept))

    # Longest phrase first; ties broken left-to-right for determinism.
    candidates.sort(key=lambda item: (-(item[1] - item[0]), item[0], item[2]))
    accepted: list[tuple[int, int, str]] = []
    for start, end, concept in candidates:
        overlaps_different_span = any(
            start < a_end and a_start < end and (a_start, a_end) != (start, end)
            for a_start, a_end, _ in accepted
        )
        if not overlaps_different_span:
            accepted.append((start, end, concept))

    grouped: dict[tuple[int, int], set[str]] = {}
    for start, end, concept in accepted:
        grouped.setdefault((start, end), set()).add(concept)
    return [
        (start, end, frozenset(concepts))
        for (start, end), concepts in sorted(grouped.items())
    ]


def _connector_between(between: Sequence[str]) -> tuple[str, bool] | None:
    """Return (relation, negated) for the first connector in ``between``."""
    negated = any(token in _NEGATION_TOKENS for token in between)
    for token in between:
        if token in _CONNECTORS:
            return _CONNECTORS[token], negated
    # "isn't"/"aren't" tokenize with no separate "is"/"are" token.
    if any(token in _NEGATED_COPULAS for token in between):
        return "equivalent_role", True
    return None


def extract_evidence(text: str, aliases: Mapping[str, Iterable[str]]) -> StructuralEvidence:
    normalized = normalize(text)
    concepts: set[str] = set()
    spans: dict[str, list[str]] = {}

    for concept, phrases in aliases.items():
        for phrase in phrases:
            candidate = normalize(phrase)
            if candidate and re.search(rf"(?<![a-z0-9]){re.escape(candidate)}(?![a-z0-9])", normalized):
                concepts.add(concept)
                spans.setdefault(concept, []).append(candidate)

    alias_index = _index_aliases(aliases)
    relations: list[tuple[str, str, str]] = []

    # Relations are extracted per clause. Splitting the raw text on clause
    # boundaries BEFORE normalizing fixes two defects: sentence-final tokens
    # kept their trailing "." ("reservation." never matched alias windows),
    # and pairs were formed across ";" boundaries, producing spurious
    # relations between unrelated clauses.
    for clause in re.split(r"[.!?;\n]+", text):
        tokens = normalize(clause).split()
        if not tokens:
            continue
        positions = _clause_positions(tokens, alias_index)
        for left_index, (_, left_end, left_concepts) in enumerate(positions):
            for right_start, _, right_concepts in positions[left_index + 1:left_index + 1 + _RELATION_WINDOW]:
                found = _connector_between(tokens[left_end:right_start])
                if found is None:
                    continue
                relation, negated = found
                kind = f"not_{relation}" if negated else relation
                for left_concept in sorted(left_concepts):
                    for right_concept in sorted(right_concepts):
                        if left_concept != right_concept:
                            relations.append((left_concept, kind, right_concept))

    return StructuralEvidence(
        concepts=frozenset(concepts),
        relations=tuple(dict.fromkeys(relations)),
        spans={key: tuple(values) for key, values in spans.items()},
    )


def _relation_matches(pattern: RelationPattern, relation: tuple[str, str, str]) -> bool:
    left, kind, right = relation
    if kind != pattern.relation:
        return False
    return left in pattern.left and right in pattern.right


def negated_rule_ids(rules: Sequence[StructuralRule], evidence: StructuralEvidence) -> frozenset[str]:
    """Rule ids whose relation the source text explicitly denies.

    A rule is reported only when a negated relation matches one of its
    patterns and no affirmative relation matches that same pattern.
    """
    denied: set[str] = set()
    for rule in rules:
        for pattern in rule.relations_any:
            negated_kind = f"not_{pattern.relation}"
            has_negated = any(
                kind == negated_kind and left in pattern.left and right in pattern.right
                for left, kind, right in evidence.relations
            )
            has_affirmed = any(_relation_matches(pattern, relation) for relation in evidence.relations)
            if has_negated and not has_affirmed:
                denied.add(rule.rule_id)
    return frozenset(denied)


def score_rule(rule: StructuralRule, evidence: StructuralEvidence) -> StructuralMatch:
    reasons: list[str] = []
    rejected: list[str] = []
    score = 0.0

    if rule.negative_concepts & evidence.concepts:
        rejected.extend(sorted(rule.negative_concepts & evidence.concepts))
        return StructuralMatch(rule.rule_id, 0.0, (), tuple(rejected))

    if rule.concepts_all:
        coverage = len(rule.concepts_all & evidence.concepts) / len(rule.concepts_all)
        score += 0.45 * coverage
        reasons.append(f"required_concept_coverage={coverage:.2f}")

    if rule.concepts_any:
        matched_groups = sum(bool(group & evidence.concepts) for group in rule.concepts_any)
        coverage = matched_groups / len(rule.concepts_any)
        score += 0.30 * coverage
        reasons.append(f"concept_group_coverage={coverage:.2f}")

    if rule.relations_any:
        # ``relations_any`` means ANY pattern suffices. Coverage used to be
        # averaged across patterns, so a rule with two alternative patterns
        # (BUILD_010) could never reach its threshold on one affirmative match.
        matched = sum(
            any(_relation_matches(pattern, relation) for relation in evidence.relations)
            for pattern in rule.relations_any
        )
        coverage = 1.0 if matched else 0.0
        score += 0.25 * coverage
        reasons.append(f"relation_coverage={coverage:.2f}")

    return StructuralMatch(rule.rule_id, round(min(score, 1.0), 4), tuple(reasons))


def resolve_rules(
    text: str,
    aliases: Mapping[str, Iterable[str]],
    rules: Sequence[StructuralRule],
) -> tuple[StructuralEvidence, list[StructuralMatch]]:
    evidence = extract_evidence(text, aliases)
    matches = [score_rule(rule, evidence) for rule in rules]
    accepted = [match for match, rule in zip(matches, rules) if match.score >= rule.minimum_score]
    accepted.sort(key=lambda match: (-match.score, match.rule_id))
    return evidence, accepted
