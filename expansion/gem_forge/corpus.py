"""PoE gem corpus ingestion.

The loader accepts either a normalized Gem Forge record list or RePoE-style JSON.
No network access occurs inside the compiler: source snapshots are explicit inputs
with provenance, so a league update cannot silently rewrite prior translations.

The pinned corpus (``data/gem_corpus_snapshot.json`` +
``data/CORPUS_MANIFEST.json``) is loaded via :func:`load_pinned_corpus`, which
verifies the snapshot's SHA-256 against the manifest before parsing — a
tampered or drifting snapshot fails closed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from semantic_compiler.expansion.gem_forge.models import PoeGem

DATA_DIR = Path(__file__).parent / "data"
PINNED_SNAPSHOT_PATH = DATA_DIR / "gem_corpus_snapshot.json"
PINNED_MANIFEST_PATH = DATA_DIR / "CORPUS_MANIFEST.json"


class CorpusPinError(ValueError):
    """The pinned snapshot is missing or fails hash verification."""


def _as_text_lines(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, dict):
        lines: list[str] = []
        for item in value.values():
            lines.extend(_as_text_lines(item))
        return tuple(lines)
    if isinstance(value, (list, tuple)):
        lines: list[str] = []
        for item in value:
            lines.extend(_as_text_lines(item))
        return tuple(lines)
    return (str(value),)


def _normal_record(item: dict[str, Any], source: str) -> PoeGem:
    name = str(item.get("name") or item.get("display_name") or item.get("id") or "").strip()
    if not name:
        raise ValueError("gem record missing name")
    gem_id = str(item.get("gem_id") or item.get("id") or name.casefold().replace(" ", "_"))
    kind = str(item.get("kind") or item.get("type") or "active").casefold()
    if "support" in kind or item.get("is_support") is True:
        kind = "support"
    elif "meta" in kind:
        kind = "meta"
    else:
        kind = "active"
    return PoeGem(
        gem_id=gem_id,
        name=name,
        kind=kind,
        tags=tuple(str(tag) for tag in item.get("tags", ()) if tag),
        description=str(item.get("description") or ""),
        wording=_as_text_lines(item.get("wording") or item.get("stat_text") or item.get("stats")),
        quality_wording=_as_text_lines(item.get("quality_wording") or item.get("quality_stats")),
        release_state=str(item.get("release_state") or item.get("release_state_name") or "released"),
        source=source,
        metadata={key: value for key, value in item.items() if key not in {
            "gem_id", "id", "name", "display_name", "kind", "type", "is_support",
            "tags", "description", "wording", "stat_text", "stats", "quality_wording",
            "quality_stats", "release_state", "release_state_name",
        }},
    )


def _repoe_record(gem_id: str, item: dict[str, Any], source: str) -> PoeGem:
    name = str(item.get("display_name") or item.get("name") or gem_id)
    tags_raw = item.get("tags") or item.get("gem_tags") or ()
    tags = tuple(tags_raw.keys()) if isinstance(tags_raw, dict) else tuple(str(tag) for tag in tags_raw)
    base_item = item.get("base_item") if isinstance(item.get("base_item"), dict) else {}
    is_support = bool(item.get("is_support") or base_item.get("is_support_gem"))
    static = item.get("static") if isinstance(item.get("static"), dict) else {}
    description = str(item.get("description") or static.get("description") or "")

    wording = _as_text_lines(
        item.get("wording")
        or item.get("stat_text")
        or item.get("stats")
        or item.get("level_stats")
        or static.get("stats")
    )
    quality = _as_text_lines(item.get("quality_stats") or static.get("quality_stats"))

    return PoeGem(
        gem_id=gem_id,
        name=name,
        kind="support" if is_support else "active",
        tags=tags,
        description=description,
        wording=wording,
        quality_wording=quality,
        release_state=str(item.get("release_state") or "released"),
        source=source,
        metadata={"raw_shape": "repoe", "base_item": base_item},
    )


def load_gem_corpus(data: Any, *, source: str = "provided_snapshot") -> tuple[PoeGem, ...]:
    """Load a deterministic gem corpus from parsed JSON-compatible data."""
    if isinstance(data, list):
        gems = [_normal_record(item, source) for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        if isinstance(data.get("gems"), list):
            gems = [_normal_record(item, source) for item in data["gems"] if isinstance(item, dict)]
        else:
            gems = [
                _repoe_record(str(gem_id), item, source)
                for gem_id, item in data.items()
                if isinstance(item, dict)
            ]
    else:
        raise TypeError("gem corpus must be a list or mapping")

    unique: dict[str, PoeGem] = {}
    for gem in gems:
        unique[gem.gem_id] = gem
    return tuple(sorted(unique.values(), key=lambda gem: (gem.kind, gem.name.casefold(), gem.gem_id)))


def load_gem_corpus_file(path: str | Path, *, source: str | None = None) -> tuple[PoeGem, ...]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return load_gem_corpus(data, source=source or str(file_path))


def dump_normalized_corpus(gems: Iterable[PoeGem]) -> list[dict[str, Any]]:
    return [gem.to_dict() for gem in gems]


def load_pinned_corpus(
    snapshot_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    *,
    verify_hash: bool = True,
) -> tuple[PoeGem, ...]:
    """Load the vendored pinned corpus, verifying provenance first.

    The manifest records the league/version pin, upstream source, and the
    SHA-256 of the snapshot. With ``verify_hash`` (default), a snapshot
    whose hash does not match the manifest fails closed with
    :class:`CorpusPinError`. No network access ever occurs here.
    """
    snapshot = Path(snapshot_path) if snapshot_path else PINNED_SNAPSHOT_PATH
    manifest = Path(manifest_path) if manifest_path else PINNED_MANIFEST_PATH
    if not snapshot.exists():
        raise CorpusPinError(f"pinned snapshot missing: {snapshot}")
    if not manifest.exists():
        raise CorpusPinError(f"corpus manifest missing: {manifest}")
    with manifest.open("r", encoding="utf-8") as handle:
        pin = json.load(handle)
    if verify_hash:
        expected = pin.get("snapshot_sha256")
        actual = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        if not expected or actual != expected:
            raise CorpusPinError(
                f"snapshot hash mismatch: manifest records {expected!r}, "
                f"file hashes to {actual!r} — refusing unverified corpus"
            )
    return load_gem_corpus_file(snapshot, source=f"pinned:{pin.get('source', {}).get('data_era', 'unknown')}")
