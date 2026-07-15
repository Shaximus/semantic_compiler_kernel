"""
Reflexion Semantic Compiler v2.0.0 — Relationship Extraction

Extract subject-verb-object triples and analogy edges from raw input.
This is intentionally dependency-free: no spaCy, no NLTK, only the same
lightweight lexical resources used by the skeleton extractor.

v2.1.2: Added to close the skeleton/relationship extraction gap identified
by Kestrel in the V2.1.1 calibration review.
"""

from __future__ import annotations

from typing import Any

from semantic_compiler.extraction.skeleton import (
    _tokenize,
    _phrase_key,
    _phrase_is_acceptable,
    _is_likely_noun,
    _ACTION_VERBS,
    _INTERNAL_BREAKERS,
    _PREPOSITIONS,
    _DETERMINERS,
)


# Analogy markers and a small set of copula/auxiliary verbs that can sit
# between a noun phrase and the marker (e.g. "is like", "was as").
_ANALOGY_MARKERS: set[str] = {"like", "as"}
_COPULA: set[str] = {"is", "are", "was", "were", "be", "being", "been", "seems", "appears"}

# Relative pronouns that introduce a clause modifying a noun phrase.
_RELATIVE_PRONOUNS: set[str] = {"that", "which", "who"}

# Object pronouns that may need antecedent resolution.
_OBJECT_PRONOUNS: set[str] = {"it", "them", "they", "him", "her", "us", "me"}

# Coordinating conjunctions that can link parallel verbs.
_COORDINATORS: set[str] = {"and", "or", "nor"}


def _extract_noun_phrase_before(
    tokens: list[str],
    end_index: int,
    max_len: int = 3,
) -> str | None:
    """
    Find the best noun phrase ending immediately before ``end_index``.

    The phrase may be up to ``max_len`` words long and must not cross an
    internal breaker.  Determiners are stripped by ``_phrase_key``.
    """
    best: str | None = None
    for start in range(max(0, end_index - max_len), end_index):
        candidate = tokens[start:end_index]
        if not _phrase_is_acceptable(candidate):
            continue
        internal = candidate[:-1]
        if any(t.lower() in _INTERNAL_BREAKERS for t in internal):
            continue
        phrase = _phrase_key(candidate)
        if phrase:
            best = phrase
    return best


def _extract_noun_phrase_after(
    tokens: list[str],
    start_index: int,
    max_len: int = 3,
) -> str | None:
    """
    Find the best noun phrase starting immediately after ``start_index``.
    """
    best: str | None = None
    for end in range(start_index + 1, min(start_index + 1 + max_len, len(tokens) + 1)):
        candidate = tokens[start_index:end]
        if not _phrase_is_acceptable(candidate):
            continue
        internal = candidate[:-1]
        if any(t.lower() in _INTERNAL_BREAKERS for t in internal):
            continue
        phrase = _phrase_key(candidate)
        if phrase:
            best = phrase
    return best


def _find_closest_phrase_before(
    phrase: str | None,
    tokens: list[str],
    index: int,
    candidates: list[str],
) -> str | None:
    """Return the nearest known phrase from ``candidates`` ending before ``index``."""
    if phrase and phrase.lower() in {c.lower() for c in candidates}:
        return phrase
    lower_tokens = [t.lower() for t in tokens]
    for i in range(index - 1, -1, -1):
        for cand in candidates:
            words = cand.lower().split()
            if lower_tokens[i] == words[-1]:
                start = i - len(words) + 1
                if start >= 0 and lower_tokens[start:i + 1] == words:
                    return cand
    return None


def _find_closest_phrase_after(
    phrase: str | None,
    tokens: list[str],
    index: int,
    candidates: list[str],
) -> str | None:
    """Return the nearest known phrase from ``candidates`` starting at/after ``index``."""
    if phrase and phrase.lower() in {c.lower() for c in candidates}:
        return phrase
    lower_tokens = [t.lower() for t in tokens]
    for i in range(index, len(tokens)):
        for cand in candidates:
            words = cand.lower().split()
            if lower_tokens[i] == words[0]:
                end = i + len(words)
                if end <= len(tokens) and lower_tokens[i:end] == words:
                    return cand
    return None


def _classify_predicate(verb: str, object_phrase: str | None) -> str:
    """Map a verb to a coarse relationship_type enum used by the schema."""
    verb_lower = verb.lower()
    if verb_lower in {"controls", "control", "controlling", "gates", "gate", "gating"}:
        return "CONTROLS"
    if verb_lower in {"routes", "route", "routing", "sends", "send", "sending", "delivers", "deliver", "delivering"}:
        return "ROUTES_TO"
    if verb_lower in {"detects", "detect", "detecting", "observes", "observe", "monitoring", "monitors", "monitor"}:
        return "OBSERVES"
    if verb_lower in {"filters", "filter", "filtering"}:
        return "CONSTRAINS"
    if verb_lower in {"remembers", "remember", "remembering", "stores", "store", "storing", "consolidates", "consolidate", "consolidating"}:
        return "CONTAINS"
    if verb_lower in {"requires", "require", "requiring", "depends", "depend", "depending"}:
        return "DEPENDS_ON"
    if verb_lower in {"enables", "enable", "enabling", "allows", "allow", "allowing"}:
        return "ENABLES"
    if verb_lower in {"causes", "cause", "causing", "makes", "make", "making"}:
        return "CAUSES"
    if verb_lower in {"precedes", "precede", "preceding", "comes", "come"}:
        return "PRECEDES"
    if verb_lower in {"updates", "update", "updating", "changes", "change", "changing", "modifies", "modify", "modifying"}:
        return "UPDATES"
    if verb_lower in {"fails", "fail", "failing", "breaks", "break", "breaking"}:
        return "FAILS_AS"
    if verb_lower in {"protects", "protect", "protecting", "defends", "defend", "defending"}:
        return "CONSTRAINS"
    if verb_lower in {"attacks", "attack", "attacking"}:
        return "COMPETES_WITH"
    return "ENABLES"


def _resolve_relative_pronoun_subject(
    tokens: list[str],
    verb_index: int,
    actors: list[str],
    objects: list[str],
) -> str | None:
    """
    If the verb at ``verb_index`` is introduced by a relative pronoun
    ("that", "which", "who"), find the antecedent noun phrase immediately
    before the relative pronoun.
    """
    if verb_index == 0:
        return None
    if tokens[verb_index - 1].lower() not in _RELATIVE_PRONOUNS:
        return None

    pronoun_index = verb_index - 1

    # The antecedent is the noun phrase ending immediately before the pronoun.
    # Gather all acceptable phrases up to 3 tokens back.
    acceptable: list[str] = []
    for start in range(max(0, pronoun_index - 3), pronoun_index):
        candidate = tokens[start:pronoun_index]
        if not _phrase_is_acceptable(candidate):
            continue
        internal = candidate[:-1]
        if any(t.lower() in _INTERNAL_BREAKERS for t in internal):
            continue
        phrase = _phrase_key(candidate)
        if phrase:
            acceptable.append(phrase)

    if acceptable:
        # Prefer the longest phrase; if there are ties, prefer known domain
        # or role nouns (e.g. "immune system" over "system").
        def _score(phrase: str) -> tuple[int, bool]:
            from semantic_compiler.extraction.skeleton import _DOMAIN_NOUNS, _ROLE_NOUNS
            known = phrase.lower() in _DOMAIN_NOUNS or phrase.lower() in _ROLE_NOUNS
            return (len(phrase.split()), known)

        acceptable.sort(key=_score, reverse=True)
        return acceptable[0]

    # Fallback: nearest known actor/object before the pronoun.
    subject = _find_closest_phrase_before(None, tokens, pronoun_index, actors)
    if not subject:
        subject = _find_closest_phrase_before(None, tokens, pronoun_index, objects)
    return subject


def _resolve_pronoun_object(
    pronoun: str,
    relationships: list[dict[str, Any]],
    actors: list[str],
    objects: list[str],
) -> str | None:
    """
    Resolve a pronoun object to the most recent non-pronoun antecedent.
    Prefers objects from already-extracted relationships, then the object list,
    then the actor list.
    """
    candidates: list[str] = []
    for rel in relationships:
        target = rel.get("target_entity_id", "")
        if target and target.lower() not in _OBJECT_PRONOUNS:
            candidates.append(target)
    candidates.extend(o for o in objects if o.lower() not in _OBJECT_PRONOUNS)
    candidates.extend(a for a in actors if a.lower() not in _OBJECT_PRONOUNS)

    # Pick the most recent candidate that matches the pronoun in number.
    pronoun_lower = pronoun.lower()
    for cand in reversed(candidates):
        if pronoun_lower in {"them", "they"}:
            # Plural antecedent preferred but not required.
            return cand
        if pronoun_lower in {"it"}:
            return cand
        # Fallback for other pronouns.
        return cand
    return None


def _extract_svo_relationships(
    text: str,
    actors: list[str],
    objects: list[str],
) -> list[dict[str, Any]]:
    """
    Extract subject-verb-object triples for explicit action verbs.

    v2.1.3 additions:
      - Relative-clause subjects ("immune system that detects threats")
      - Coordinated verbs ("detects and remembers")
      - Pronoun antecedent resolution ("remembers them" -> "remembers threats")
    """
    tokens = _tokenize(text)
    n = len(tokens)
    relationships: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    i = 0
    while i < n:
        token = tokens[i]
        i += 1
        if token.lower() not in _ACTION_VERBS:
            continue
        # Skip the copula/auxiliary verbs that do not carry semantic action.
        if token.lower() in {"is", "are", "was", "were", "be", "being", "been", "has", "have", "had"}:
            continue

        verb_index = i - 1

        # If a word that can be a verb is actually functioning as the object of
        # the immediately preceding verb, skip it (e.g., "controls access").
        if verb_index > 0 and tokens[verb_index - 1].lower() in _ACTION_VERBS:
            if _is_likely_noun(token):
                continue

        # If the verb is introduced by a relative pronoun, the subject is the
        # antecedent noun phrase, not the closest actor before the verb.
        if verb_index > 0 and tokens[verb_index - 1].lower() in _RELATIVE_PRONOUNS:
            subject = _resolve_relative_pronoun_subject(tokens, verb_index, actors, objects)
        else:
            subject = _extract_noun_phrase_before(tokens, verb_index)
            subject = _find_closest_phrase_before(subject, tokens, verb_index, actors)
        if not subject:
            continue

        # Look for object after the verb, skipping a leading determiner or
        # preposition if present (e.g. "delivers [the] materials").
        obj_start = verb_index + 1
        if obj_start < n and tokens[obj_start].lower() in _DETERMINERS | _PREPOSITIONS:
            obj_start += 1
        object_phrase = _extract_noun_phrase_after(tokens, obj_start)
        if object_phrase:
            object_phrase = _find_closest_phrase_after(object_phrase, tokens, obj_start, objects) or object_phrase

        # If the verb is followed by an analogy marker, this is an analogy
        # edge rather than a normal SVO; handled separately below.
        if obj_start < n and tokens[obj_start].lower() in _ANALOGY_MARKERS:
            continue

        if not object_phrase:
            continue

        def _add_rel(verb: str, obj: str) -> None:
            key = (subject.lower(), verb.lower(), obj.lower())
            if key in seen:
                return
            seen.add(key)
            rel_type = _classify_predicate(verb, obj)
            relationships.append({
                "relationship_id": f"rel-svo-{len(relationships):03d}",
                "source_entity_id": subject,
                "target_entity_id": obj,
                "relationship_type": rel_type,
                "confidence": 0.85,
                "mapping_class": "CAUSAL_MAPPING" if rel_type == "CAUSES" else "STRUCTURAL_ANALOGY",
                "source_span": " ".join(tokens[max(0, verb_index - 1):verb_index + 2]),
                "predicate": verb.lower(),
            })

        _add_rel(token, object_phrase)

        # Coordinated verb: "X detects and remembers Y" -> also extract
        # "X remembers Y". Require the coordinator and second verb to follow
        # immediately, with the object already captured.
        coord_index = obj_start
        if coord_index < n and tokens[coord_index].lower() in _DETERMINERS | _PREPOSITIONS:
            coord_index += 1
        # If the object phrase was consumed, the next token may be the coordinator.
        obj_end = obj_start + len(object_phrase.split())
        # Recompute object span from actual tokens to find the position after it.
        obj_tokens = _tokenize(object_phrase)
        after_obj = obj_start + len(obj_tokens)
        if after_obj < n and tokens[after_obj].lower() in _COORDINATORS:
            second_verb_index = after_obj + 1
            if second_verb_index < n and tokens[second_verb_index].lower() in _ACTION_VERBS:
                second_verb = tokens[second_verb_index]
                # Object is the same as for the first verb; no re-scan needed.
                _add_rel(second_verb, object_phrase)

    # Resolve pronoun objects to concrete antecedents.
    for rel in relationships:
        target = rel.get("target_entity_id", "")
        if target.lower() in _OBJECT_PRONOUNS:
            resolved = _resolve_pronoun_object(target, relationships, actors, objects)
            if resolved:
                rel["target_entity_id"] = resolved
                rel["source_span"] = rel.get("source_span", "").replace(target, resolved)

    return relationships


def _extract_analogy_edges(
    text: str,
    actors: list[str],
    objects: list[str],
) -> list[dict[str, Any]]:
    """
    Extract IS_STRUCTURALLY_LIKE / ANALOGOUS_TO edges from markers
    such as "is like", "like", "as", and "just as".
    """
    tokens = _tokenize(text)
    n = len(tokens)
    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for i, token in enumerate(tokens):
        if token.lower() not in _ANALOGY_MARKERS:
            continue

        # Determine the end of the source side. Allow a copula immediately
        # before the marker: "X is like Y" -> source ends at i-2.
        source_end = i
        if i > 0 and tokens[i - 1].lower() in _COPULA:
            source_end = i - 1

        source = _extract_noun_phrase_before(tokens, source_end)
        source = _find_closest_phrase_before(source, tokens, source_end, actors)

        # Target starts after the marker, skipping determiners/prepositions.
        target_start = i + 1
        if target_start < n and tokens[target_start].lower() in _DETERMINERS | _PREPOSITIONS:
            target_start += 1

        target = _extract_noun_phrase_after(tokens, target_start)
        if not target:
            target = _find_closest_phrase_after(None, tokens, target_start, objects)

        if not source or not target:
            continue
        if source.lower() == target.lower():
            continue

        key = (source.lower(), target.lower())
        if key in seen:
            continue
        seen.add(key)

        edges.append({
            "relationship_id": f"rel-analogy-{len(edges):03d}",
            "source_entity_id": source,
            "target_entity_id": target,
            "relationship_type": "ANALOGOUS_TO",
            "confidence": 0.8,
            "mapping_class": "STRUCTURAL_ANALOGY",
            "source_span": " ".join(tokens[max(0, source_end - 2):target_start + 2]),
            "predicate": "is_structurally_like",
        })

    return edges


def extract_relationships(packet: Any) -> list[dict[str, Any]]:
    """
    Populate ``packet.semantic_ir.relationships`` from extracted actors,
    objects, and raw input.

    Returns a list of relationship dictionaries compatible with the V2.1
    dataset schema (source_entity_id, target_entity_id, relationship_type,
    confidence, mapping_class).
    """
    text = packet.raw_input or ""
    skeleton = packet.structural_skeleton or {}
    actors = [str(a) for a in skeleton.get("actors", [])]
    objects = [str(o) for o in skeleton.get("objects", [])]

    if not text or (not actors and not objects):
        return []

    svo = _extract_svo_relationships(text, actors, objects)
    analogies = _extract_analogy_edges(text, actors, objects)

    # Combine and renumber IDs so they are unique.
    combined = svo + analogies
    for idx, rel in enumerate(combined):
        rel["relationship_id"] = f"rel-{idx:03d}"

    return combined
