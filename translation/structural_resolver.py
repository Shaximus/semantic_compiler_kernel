"""Relation-aware structural ontology resolver.

This module replaces phrase-only trigger matching with a small, deterministic
intermediate representation. It extracts concepts and typed relations from text,
then scores ontology mappings against required concepts, relation evidence,
negative evidence, and ontology-wide structural coherence.

It intentionally does not depend on a model or external NLP runtime. The output
is auditable and can later accept richer parser evidence without changing the
ontology contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable, Mapping, Sequence


_TOKEN_RE = re.compile(r"[a-z0-9+./_-]+")


@dataclass(frozen=True)
class RelationPattern:
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

    relations: list[tuple[str, str, str]] = []
    connectors = {
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

    # Relations are extracted per clause. Splitting the raw text on clause
    # boundaries BEFORE normalizing fixes two defects: sentence-final tokens
    # kept their trailing "." ("reservation." never matched alias windows),
    # and pairs were formed across ";" boundaries, producing spurious
    # relations between unrelated clauses.
    for clause in re.split(r"[.!?;\n]+", text):
        tokens = normalize(clause).split()
        if not tokens:
            continue
        concept_positions: dict[int, str] = {}
        for index in range(len(tokens)):
            for concept, phrases in aliases.items():
                for phrase in phrases:
                    phrase_tokens = normalize(phrase).split()
                    if phrase_tokens and tokens[index:index + len(phrase_tokens)] == phrase_tokens:
                        concept_positions[index] = concept

        ordered = sorted(concept_positions.items())
        for left_index, (left_pos, left_concept) in enumerate(ordered):
            for right_pos, right_concept in ordered[left_index + 1:left_index + 4]:
                between = tokens[left_pos + 1:right_pos]
                relation = next((connectors[token] for token in between if token in connectors), None)
                if relation:
                    relations.append((left_concept, relation, right_concept))

    return StructuralEvidence(
        concepts=frozenset(concepts),
        relations=tuple(dict.fromkeys(relations)),
        spans={key: tuple(values) for key, values in spans.items()},
    )


def _relation_matches(pattern: RelationPattern, relation: tuple[str, str, str]) -> bool:
    left, kind, right = relation
    if kind != pattern.relation and kind not in pattern.connectors:
        return False
    return left in pattern.left and right in pattern.right


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
        matched = sum(
            any(_relation_matches(pattern, relation) for relation in evidence.relations)
            for pattern in rule.relations_any
        )
        coverage = matched / len(rule.relations_any)
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
