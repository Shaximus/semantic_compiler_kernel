"""Multi-source gem ingestion, provenance, and wording-diff flagging.

Gem Forge treats every corpus as a pinned, hash-verified input. This module
generalizes the single pinned corpus to N independent sources:

- each source carries a :class:`SourceProvenance` receipt (source id, data
  era / league, retrieval time, SHA-256 of the snapshot, synthetic flag);
- each source snapshot is normalized through the existing record schema
  (:func:`~semantic_compiler.expansion.gem_forge.corpus.load_gem_corpus`);
- gems are merged across sources by gem id; a gem present in exactly one
  source is marked ``single_source``;
- wording differences between sources are FLAGGED per gem as side-by-side
  line pairs. Variants are never merged, averaged, or smoothed — both
  wordings are preserved verbatim, classified as ``VALUE_ONLY`` (numbers
  differ, words identical) or ``WORDING_CHANGE``.

No network access occurs here; fetching is a generation-time concern recorded
in each source's manifest.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from semantic_compiler.expansion.gem_forge.corpus import CorpusPinError, load_gem_corpus_file
from semantic_compiler.expansion.gem_forge.models import PoeGem


@dataclass(frozen=True)
class SourceProvenance:
    """Receipt identifying one pinned corpus source."""

    source_id: str
    data_era: str
    origin: str  # upstream repo / hosted export / fixture path
    retrieved_at: str
    sha256: str
    synthetic: bool = False
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProvenancedSource:
    provenance: SourceProvenance
    gems: tuple[PoeGem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"provenance": self.provenance.to_dict(), "gem_count": len(self.gems)}


@dataclass(frozen=True)
class WordingDiff:
    """One flagged wording difference between two sources. Side by side only."""

    gem_id: str
    section: str  # wording | quality_wording
    kind: str  # MODIFIED_PAIR | ONLY_IN_SOURCE
    primary_source: str
    secondary_source: str
    primary_line: str | None
    secondary_line: str | None
    classification: str  # VALUE_ONLY | WORDING_CHANGE | LINE_ADDED | LINE_REMOVED

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MergedGem:
    gem_id: str
    name: str
    kind: str
    sources: tuple[str, ...]
    single_source: bool
    per_source_wording: dict[str, dict[str, tuple[str, ...]]] = field(default_factory=dict)
    wording_diffs: tuple[WordingDiff, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "gem_id": self.gem_id,
            "name": self.name,
            "kind": self.kind,
            "sources": list(self.sources),
            "single_source": self.single_source,
            "wording_diff_count": len(self.wording_diffs),
            "wording_diffs": [d.to_dict() for d in self.wording_diffs],
        }


@dataclass(frozen=True)
class MergeResult:
    sources: tuple[SourceProvenance, ...]
    gems: tuple[MergedGem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sources": [s.to_dict() for s in self.sources],
            "gem_count": len(self.gems),
            "single_source_count": sum(1 for g in self.gems if g.single_source),
            "gems_with_diffs": sum(1 for g in self.gems if g.wording_diffs),
            "total_diffs": sum(len(g.wording_diffs) for g in self.gems),
        }


def load_provenanced_source(
    snapshot_path: str | Path,
    manifest_path: str | Path,
    *,
    source_id: str,
    synthetic: bool = False,
    verify_hash: bool = True,
) -> ProvenancedSource:
    """Load one source snapshot with hash verification, mirroring the pinned loader."""
    snapshot = Path(snapshot_path)
    manifest = Path(manifest_path)
    if not snapshot.exists():
        raise CorpusPinError(f"source snapshot missing: {snapshot}")
    if not manifest.exists():
        raise CorpusPinError(f"source manifest missing: {manifest}")
    with manifest.open("r", encoding="utf-8") as handle:
        pin = json.load(handle)
    actual = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    if verify_hash:
        expected = pin.get("snapshot_sha256")
        if not expected or actual != expected:
            raise CorpusPinError(
                f"source snapshot hash mismatch for {source_id!r}: manifest records "
                f"{expected!r}, file hashes to {actual!r} — refusing unverified corpus"
            )
    source = pin.get("source") or {}
    provenance = SourceProvenance(
        source_id=source_id,
        data_era=str(source.get("data_era") or "unknown"),
        origin=str(source.get("repo") or source.get("hosted_export") or str(snapshot)),
        retrieved_at=str(source.get("fetched_at") or "unknown"),
        sha256=actual,
        synthetic=bool(pin.get("synthetic", synthetic)),
        notes=tuple(pin.get("rendering_decisions") or ()),
    )
    gems = load_gem_corpus_file(snapshot, source=f"multi:{source_id}")
    return ProvenancedSource(provenance=provenance, gems=gems)


_NUMBER_RUN_RE = re.compile(r"\d+(?:\.\d+)?")


def _numbers_blanked(line: str) -> str:
    """Line shape with every numeric run replaced by '#'."""
    return _NUMBER_RUN_RE.sub("#", line)


def _classify_pair(primary_line: str, secondary_line: str) -> str:
    if _numbers_blanked(primary_line) == _numbers_blanked(secondary_line):
        return "VALUE_ONLY"
    return "WORDING_CHANGE"


def _diff_sections(
    gem_id: str,
    section: str,
    primary_source: str,
    secondary_source: str,
    primary_lines: tuple[str, ...],
    secondary_lines: tuple[str, ...],
) -> tuple[WordingDiff, ...]:
    """Deterministic side-by-side diff of two line lists.

    ``difflib.SequenceMatcher`` with ``autojunk=False`` is deterministic for a
    fixed input pair. ``replace`` blocks are paired positionally; unpaired
    leftovers become ONLY_IN_SOURCE records. No line is ever merged with or
    averaged into another.
    """
    matcher = difflib.SequenceMatcher(
        None, list(primary_lines), list(secondary_lines), autojunk=False
    )
    diffs: list[WordingDiff] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            span = min(i2 - i1, j2 - j1)
            for k in range(span):
                left, right = primary_lines[i1 + k], secondary_lines[j1 + k]
                diffs.append(WordingDiff(
                    gem_id=gem_id,
                    section=section,
                    kind="MODIFIED_PAIR",
                    primary_source=primary_source,
                    secondary_source=secondary_source,
                    primary_line=left,
                    secondary_line=right,
                    classification=_classify_pair(left, right),
                ))
            for k in range(i1 + span, i2):
                diffs.append(WordingDiff(
                    gem_id=gem_id, section=section, kind="ONLY_IN_SOURCE",
                    primary_source=primary_source, secondary_source=secondary_source,
                    primary_line=primary_lines[k], secondary_line=None,
                    classification="LINE_REMOVED",
                ))
            for k in range(j1 + span, j2):
                diffs.append(WordingDiff(
                    gem_id=gem_id, section=section, kind="ONLY_IN_SOURCE",
                    primary_source=primary_source, secondary_source=secondary_source,
                    primary_line=None, secondary_line=secondary_lines[k],
                    classification="LINE_ADDED",
                ))
        elif tag == "delete":
            for k in range(i1, i2):
                diffs.append(WordingDiff(
                    gem_id=gem_id, section=section, kind="ONLY_IN_SOURCE",
                    primary_source=primary_source, secondary_source=secondary_source,
                    primary_line=primary_lines[k], secondary_line=None,
                    classification="LINE_REMOVED",
                ))
        elif tag == "insert":
            for k in range(j1, j2):
                diffs.append(WordingDiff(
                    gem_id=gem_id, section=section, kind="ONLY_IN_SOURCE",
                    primary_source=primary_source, secondary_source=secondary_source,
                    primary_line=None, secondary_line=secondary_lines[k],
                    classification="LINE_ADDED",
                ))
    return tuple(diffs)


def merge_sources(sources: Iterable[ProvenancedSource]) -> MergeResult:
    """Merge N provenanced sources by gem id.

    The FIRST source supplied is the primary reference: diffs are computed
    between the primary wording and each later source, per gem, for both the
    ``wording`` and ``quality_wording`` sections. Gems absent from the primary
    are diffed against the earliest source that contains them.
    """
    sources = tuple(sources)
    if not sources:
        raise ValueError("merge_sources requires at least one source")
    primary_id = sources[0].provenance.source_id

    by_id: dict[str, dict[str, PoeGem]] = {}
    name_of: dict[str, str] = {}
    kind_of: dict[str, str] = {}
    for source in sources:
        sid = source.provenance.source_id
        for gem in source.gems:
            by_id.setdefault(gem.gem_id, {})[sid] = gem
            name_of.setdefault(gem.gem_id, gem.name)
            kind_of.setdefault(gem.gem_id, gem.kind)

    merged: list[MergedGem] = []
    for gem_id in sorted(by_id):
        present = by_id[gem_id]
        source_ids = tuple(s.provenance.source_id for s in sources if s.provenance.source_id in present)
        reference_id = primary_id if primary_id in present else source_ids[0]
        reference = present[reference_id]
        per_source = {
            sid: {"wording": present[sid].wording, "quality_wording": present[sid].quality_wording}
            for sid in source_ids
        }
        diffs: list[WordingDiff] = []
        for sid in source_ids:
            if sid == reference_id:
                continue
            other = present[sid]
            for section, left, right in (
                ("wording", reference.wording, other.wording),
                ("quality_wording", reference.quality_wording, other.quality_wording),
            ):
                diffs.extend(_diff_sections(gem_id, section, reference_id, sid, left, right))
        merged.append(MergedGem(
            gem_id=gem_id,
            name=name_of[gem_id],
            kind=kind_of[gem_id],
            sources=source_ids,
            single_source=len(source_ids) == 1,
            per_source_wording=per_source,
            wording_diffs=tuple(diffs),
        ))
    return MergeResult(
        sources=tuple(s.provenance for s in sources),
        gems=tuple(merged),
    )


def wording_diff_records(result: MergeResult) -> list[dict[str, Any]]:
    """One JSONL-ready record per gem that has at least one wording diff."""
    records = []
    for gem in result.gems:
        if not gem.wording_diffs:
            continue
        records.append({
            "gem_id": gem.gem_id,
            "name": gem.name,
            "sources": list(gem.sources),
            "diffs": [d.to_dict() for d in gem.wording_diffs],
        })
    return records


def provenance_report(result: MergeResult) -> dict[str, Any]:
    """Machine-readable multi-source provenance rollup."""
    per_source_gems: dict[str, int] = {s.source_id: 0 for s in result.sources}
    single_by_source: dict[str, int] = {s.source_id: 0 for s in result.sources}
    classification_counts: dict[str, int] = {}
    for gem in result.gems:
        for sid in gem.sources:
            per_source_gems[sid] += 1
        if gem.single_source:
            single_by_source[gem.sources[0]] += 1
        for diff in gem.wording_diffs:
            classification_counts[diff.classification] = classification_counts.get(diff.classification, 0) + 1
    return {
        "schema": "reflexion.gem_forge.multi_source_provenance.v1",
        "sources": [s.to_dict() for s in result.sources],
        "merged_gem_count": len(result.gems),
        "per_source_gem_counts": per_source_gems,
        "single_source_gem_counts": single_by_source,
        "shared_gem_count": sum(1 for g in result.gems if not g.single_source),
        "gems_with_wording_diffs": sum(1 for g in result.gems if g.wording_diffs),
        "total_wording_diffs": sum(len(g.wording_diffs) for g in result.gems),
        "diff_classification_counts": dict(sorted(classification_counts.items())),
        "policy": (
            "Wording variants are flagged side by side and never averaged. "
            "Gems present in exactly one source are marked single_source. "
            "The first source listed is the primary reference for diff direction."
        ),
    }
