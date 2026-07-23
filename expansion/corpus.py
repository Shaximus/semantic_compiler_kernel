"""
Corpus orchestration layer (V2.2 expansion).

``compile_semantic_packet`` compiles exactly one string. This module runs it
over a multi-document corpus and aggregates the per-chunk packets into a
deterministic corpus-level report with a cross-document **invariant
registry** — the structure the 20-document corpus-mapping mission consumes.

Everything here is deterministic: no LLM calls, no randomness. The invariant
signature is a documented structural fingerprint (claim types + relationship
types + populated skeleton dimensions + source frames); recurrence of the
same fingerprint across documents is what "recurring structure" means at this
layer. Finer-grained semantic judgment is deliberately left to downstream
(human or model) review.

Verdicts use the :mod:`semantic_compiler.expansion.verdicts` vocabulary:

- ``HOLDS`` — fingerprint recurs in >= 2 distinct documents with no
  counterexample disconfirmation on record.
- ``UNRESOLVED`` — observed in exactly one document so far (not yet
  cross-confirmed), or timestamps insufficient for a derivation-order call.
- ``STRAINS`` — at least one recorded disconfirmation carries a real
  counterexample (``FAILED``/``WEAKENED``).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence

from semantic_compiler.core.pipeline import compile_semantic_packet
from semantic_compiler.expansion.counter_mapping import (
    Disconfirmation,
    searched_but_not_found,
)
from semantic_compiler.expansion.derivation_order import (
    attach_derivation_event,
    make_event,
)
from semantic_compiler.expansion.evidence_tiers import (
    EvidenceTier,
    strongest_tier,
)
from semantic_compiler.expansion.verdicts import CorpusVerdict

DEFAULT_MAX_CHUNK_CHARS = 4000

# Skeleton dimensions used in the structural fingerprint.
_SKELETON_DIMENSIONS = (
    "actors", "objects", "boundaries", "inputs", "outputs", "flows",
    "authority", "failure_modes", "control_loops", "feedback_loops",
    "resources", "forces",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Document inputs
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DocumentMetadata:
    """Metadata every corpus document must carry."""

    doc_id: str
    source_path: Optional[str]
    captured_at: str
    evidence_tier: str = EvidenceTier.SELF_ASSESSED_ESTIMATE.value
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source_path": self.source_path,
            "captured_at": self.captured_at,
            "evidence_tier": self.evidence_tier,
            "extra": dict(self.extra),
        }


@dataclass(frozen=True)
class CorpusDocument:
    metadata: DocumentMetadata
    text: str


def load_documents(
    inputs: Iterable[Any],
    *,
    default_evidence_tier: str = EvidenceTier.SELF_ASSESSED_ESTIMATE.value,
) -> list[CorpusDocument]:
    """
    Normalize corpus inputs into :class:`CorpusDocument` objects.

    Accepted input forms:

    - ``str``/``Path`` path to a UTF-8 text file (doc_id defaults to the file
      stem, captured_at to the file mtime);
    - ``(doc_id, text)`` or ``(doc_id, text, metadata_dict)`` tuples —
      ``metadata_dict`` may carry ``source_path``, ``captured_at``,
      ``evidence_tier`` plus arbitrary extras;
    - ``{"doc_id": ..., "text": ..., ...}`` dicts (same metadata keys).
    """
    documents: list[CorpusDocument] = []
    for item in inputs:
        if isinstance(item, (str, Path)):
            documents.append(_load_from_path(Path(item), default_evidence_tier))
        elif isinstance(item, tuple):
            if len(item) == 2:
                doc_id, text = item
                meta: dict[str, Any] = {}
            elif len(item) == 3:
                doc_id, text, meta = item
                meta = dict(meta or {})
            else:
                raise ValueError(f"Document tuple must have 2 or 3 items: {item!r}")
            documents.append(_from_parts(str(doc_id), str(text), meta, default_evidence_tier))
        elif isinstance(item, dict):
            data = dict(item)
            doc_id = str(data.pop("doc_id"))
            text = str(data.pop("text"))
            documents.append(_from_parts(doc_id, text, data, default_evidence_tier))
        else:
            raise TypeError(f"Unsupported document input: {type(item).__name__}")
    return documents


def _load_from_path(path: Path, default_tier: str) -> CorpusDocument:
    text = path.read_text(encoding="utf-8")
    captured_at = datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc
    ).isoformat()
    metadata = DocumentMetadata(
        doc_id=path.stem,
        source_path=str(path),
        captured_at=captured_at,
        evidence_tier=default_tier,
    )
    return CorpusDocument(metadata=metadata, text=text)


def _from_parts(
    doc_id: str,
    text: str,
    meta: dict[str, Any],
    default_tier: str,
) -> CorpusDocument:
    known = {}
    for key in ("source_path", "captured_at", "evidence_tier"):
        if key in meta:
            known[key] = meta.pop(key)
    metadata = DocumentMetadata(
        doc_id=doc_id,
        source_path=known.get("source_path"),
        captured_at=known.get("captured_at") or _now(),
        evidence_tier=known.get("evidence_tier") or default_tier,
        extra=meta,
    )
    return CorpusDocument(metadata=metadata, text=text)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Chunk:
    index: int
    text: str
    start: int
    end: int


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHUNK_CHARS) -> list[Chunk]:
    """
    Split text into chunks of at most ``max_chars`` characters.

    Paragraph/section-aware: splits on blank-line boundaries first, keeps a
    Markdown heading attached to the block that follows it, falls back to
    single newlines for oversized paragraphs, and hard-splits only when a
    single line still exceeds the limit. Character offsets are preserved so
    every chunk can be located in its source document.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if not text:
        return []

    # Paragraph blocks with their offsets (blank-line separated).
    blocks: list[tuple[str, int, int]] = []
    pos = 0
    for part in text.split("\n\n"):
        start = text.index(part, pos) if part else pos
        blocks.append((part, start, start + len(part)))
        pos = start + len(part) + 2

    # Attach Markdown headings to the following block (section awareness).
    merged: list[tuple[str, int, int]] = []
    pending: Optional[tuple[str, int, int]] = None
    for block in blocks:
        stripped = block[0].strip()
        if stripped.startswith("#") and pending is None and len(blocks) > 1:
            pending = block
            continue
        if pending is not None:
            block = (pending[0] + "\n\n" + block[0], pending[1], block[2])
            pending = None
        merged.append(block)
    if pending is not None:
        merged.append(pending)

    # Accumulate blocks up to the size limit.
    pieces: list[tuple[str, int, int]] = []
    current: Optional[tuple[str, int, int]] = None
    for block in merged:
        candidate = (
            block if current is None
            else (current[0] + "\n\n" + block[0], current[1], block[2])
        )
        if current is not None and len(candidate[0]) > max_chars:
            pieces.append(current)
            current = block
        else:
            current = candidate
    if current is not None:
        pieces.append(current)

    # Split oversized pieces on newlines, then hard-split long lines.
    chunks: list[Chunk] = []
    for piece_text, piece_start, _ in pieces:
        for sub_text, sub_start in _split_oversized(piece_text, piece_start, max_chars):
            chunks.append(Chunk(
                index=len(chunks),
                text=sub_text,
                start=sub_start,
                end=sub_start + len(sub_text),
            ))
    return [c for c in chunks if c.text.strip()]


def _split_oversized(
    text: str, offset: int, max_chars: int
) -> list[tuple[str, int]]:
    if len(text) <= max_chars:
        return [(text, offset)]

    # Flatten to segments with exact offsets; `sep` is the length of the
    # joiner that precedes the segment when merging (1 = newline, 0 = none,
    # i.e. the segment comes from a hard-split line).
    segments: list[tuple[str, int, int]] = []
    cursor = offset
    for line in text.split("\n"):
        line_start = cursor
        if len(line) <= max_chars:
            segments.append((line, line_start, 1))
        else:
            for i in range(0, len(line), max_chars):
                segments.append((line[i:i + max_chars], line_start + i, 1 if i == 0 else 0))
        cursor = line_start + len(line) + 1

    out: list[tuple[str, int]] = []
    current: Optional[str] = None
    current_start = offset
    for seg_text, seg_start, sep in segments:
        if current is None:
            current, current_start = seg_text, seg_start
            continue
        joiner = "\n" if sep else ""
        if len(current) + len(joiner) + len(seg_text) > max_chars:
            out.append((current, current_start))
            current, current_start = seg_text, seg_start
        else:
            current += joiner + seg_text
    if current is not None:
        out.append((current, current_start))
    return out


# ---------------------------------------------------------------------------
# Structural fingerprint
# ---------------------------------------------------------------------------

def structural_signature(packet: Any) -> dict[str, Any]:
    """
    Extract the deterministic structural fingerprint of one compiled packet.

    Components (all sorted, deduplicated):

    - ``claim_types`` — claim type labels from stage-1 classification;
    - ``relationship_types`` — relationship types in the Semantic IR;
    - ``populated_structure`` — skeleton dimensions with non-empty content;
    - ``source_frames`` — detected source frames.
    """
    claim_types = sorted({
        str(c.get("claim_type"))
        for c in (packet.claim_types or [])
        if isinstance(c, dict) and c.get("claim_type")
    })
    ir = packet.semantic_ir
    relationships = getattr(ir, "relationships", None) or []
    relationship_types = sorted({
        str(r.get("relationship_type"))
        for r in relationships
        if isinstance(r, dict) and r.get("relationship_type")
    })
    skeleton = packet.structural_skeleton or {}
    populated = sorted(
        dim for dim in _SKELETON_DIMENSIONS if skeleton.get(dim)
    )
    frames = sorted(str(f) for f in (packet.source_frames or []))
    return {
        "claim_types": claim_types,
        "relationship_types": relationship_types,
        "populated_structure": populated,
        "source_frames": frames,
    }


def signature_key(signature: dict[str, Any]) -> str:
    """Stable string key for a signature (JSON, sorted keys)."""
    return json.dumps(signature, sort_keys=True)


# ---------------------------------------------------------------------------
# Corpus compilation and aggregation
# ---------------------------------------------------------------------------

def compile_corpus(
    documents: Iterable[Any],
    *,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    compile_fn: Callable[..., Any] = compile_semantic_packet,
    parallel_exposure_at: Optional[str] = None,
) -> dict[str, Any]:
    """
    Compile a corpus and build the aggregated report + invariant registry.

    Parameters
    ----------
    documents:
        Anything :func:`load_documents` accepts.
    max_chunk_chars:
        Chunk size limit for :func:`chunk_text`.
    compile_fn:
        Per-chunk compile callable (injectable for tests); must accept
        ``(text, context=...)`` and return a SemanticPacket-like object.
    parallel_exposure_at:
        Optional ISO timestamp of exposure to a parallel account; when given,
        every invariant's ``derivation_event_log`` records whether its first
        derivation preceded that exposure.
    """
    docs = load_documents(documents)
    generated_at = _now()

    doc_reports: dict[str, Any] = {}
    observations: dict[str, dict[str, Any]] = {}  # signature_key -> accumulator

    for doc in docs:
        meta = doc.metadata
        chunks = chunk_text(doc.text, max_chunk_chars)
        chunk_results: list[dict[str, Any]] = []
        seen_in_doc: set[str] = set()

        for chunk in chunks:
            context = {
                "document_metadata": meta.to_dict(),
                "chunk": {
                    "index": chunk.index,
                    "start": chunk.start,
                    "end": chunk.end,
                    "chunk_count": len(chunks),
                },
            }
            packet = compile_fn(chunk.text, context=context)
            signature = structural_signature(packet)
            key = signature_key(signature)
            decision = getattr(packet, "decision", None)
            chunk_results.append({
                "chunk_index": chunk.index,
                "start": chunk.start,
                "end": chunk.end,
                "decision": getattr(decision, "name", str(decision)),
                "signature": signature,
                "signature_key": key,
            })

            acc = observations.setdefault(key, {
                "signature": signature,
                "supporting": [],
                "doc_ids": set(),
                "first_seen_at": meta.captured_at,
                "last_seen_at": meta.captured_at,
                "derived_at": generated_at,
                "evidence_tiers": [],
            })
            acc["supporting"].append({
                "doc_id": meta.doc_id,
                "chunk_index": chunk.index,
                "start": chunk.start,
                "end": chunk.end,
            })
            acc["doc_ids"].add(meta.doc_id)
            acc["evidence_tiers"].append(meta.evidence_tier)
            acc["first_seen_at"] = min(acc["first_seen_at"], meta.captured_at)
            acc["last_seen_at"] = max(acc["last_seen_at"], meta.captured_at)
            seen_in_doc.add(key)

        doc_reports[meta.doc_id] = {
            "metadata": meta.to_dict(),
            "chunk_count": len(chunks),
            "chunk_results": chunk_results,
            "distinct_signatures": sorted(seen_in_doc),
        }

    registry = _build_registry(
        observations,
        searched_doc_ids=[d.metadata.doc_id for d in docs],
        generated_at=generated_at,
        parallel_exposure_at=parallel_exposure_at,
    )

    return {
        "schema": "reflexion.corpus.report.v1",
        "generated_at": generated_at,
        "corpus": {
            "document_count": len(docs),
            "chunk_count": sum(r["chunk_count"] for r in doc_reports.values()),
            "documents": [d.metadata.to_dict() for d in docs],
        },
        "documents": doc_reports,
        "invariant_registry": registry,
    }


def _build_registry(
    observations: dict[str, dict[str, Any]],
    *,
    searched_doc_ids: Sequence[str],
    generated_at: str,
    parallel_exposure_at: Optional[str],
) -> list[dict[str, Any]]:
    registry: list[dict[str, Any]] = []
    for i, (key, acc) in enumerate(sorted(observations.items())):
        doc_ids = sorted(acc["doc_ids"])
        signature = acc["signature"]

        # Honest disconfirmation records: every searched document where this
        # fingerprint was not observed is NOT_FOUND_WITHIN_SEARCH_SCOPE.
        absent_docs = [d for d in searched_doc_ids if d not in acc["doc_ids"]]
        disconfirmations: list[dict[str, Any]] = []
        if absent_docs:
            disc: Disconfirmation = searched_but_not_found(
                attack=f"structural fingerprint absent from {len(absent_docs)} searched document(s)",
                queries_used=[key],
                documents_searched=absent_docs,
                searched_at=generated_at,
                impact="bounds cross-document generality of the invariant",
            )
            disconfirmations.append(disc.to_negative_test(test_id="nt-corpus-0"))

        if len(doc_ids) >= 2:
            verdict = CorpusVerdict.HOLDS.value
        else:
            verdict = CorpusVerdict.UNRESOLVED.value

        tier = strongest_tier([
            EvidenceTier(t) for t in acc["evidence_tiers"]
        ]) or EvidenceTier.MARKED_SPECULATION

        entry: dict[str, Any] = {
            "invariant_id": f"INV-{i:04d}",
            "description": _describe(signature),
            "signature": signature,
            "supporting": acc["supporting"],
            "supporting_documents": doc_ids,
            "confirmations": len(acc["supporting"]),
            "disconfirmations": disconfirmations,
            "evidence_tier": tier.value,
            "verdict": verdict,
            "first_seen_at": acc["first_seen_at"],
            "last_seen_at": acc["last_seen_at"],
            "registered_at": generated_at,
            "derivation_event_log": [],
        }
        if parallel_exposure_at is not None:
            entry = attach_derivation_event(entry, make_event(
                subject_id=entry["invariant_id"],
                derived_at=generated_at,
                exposed_to_parallel_at=parallel_exposure_at,
                note="corpus invariant first derived during compile_corpus run",
            ))
        registry.append(entry)
    return registry


def _describe(signature: dict[str, Any]) -> str:
    parts = []
    if signature["claim_types"]:
        parts.append("claims: " + ", ".join(signature["claim_types"]))
    if signature["relationship_types"]:
        parts.append("relationships: " + ", ".join(signature["relationship_types"]))
    if signature["populated_structure"]:
        parts.append("structure: " + ", ".join(signature["populated_structure"]))
    if signature["source_frames"]:
        parts.append("frames: " + ", ".join(signature["source_frames"]))
    return "Recurring structural fingerprint (" + "; ".join(parts) + ")"
