#!/usr/bin/env python3
"""Build a normalized second-source gem corpus snapshot from a repoe-fork export.

One-time GENERATION-TIME tool, mirroring ``build_gem_corpus_snapshot.py`` for the
maintained RePoE fork (https://github.com/repoe-fork/repoe, hosted exports at
https://repoe-fork.github.io/). The compiler never fetches anything: this script
converts a local directory containing the fork's ``gems.json`` +
``stat_translations.json`` + ``stat_translations/*.json`` into the same normalized
snapshot schema as the pinned first-source corpus, plus a provenance manifest
recording source id, data era (game version), retrieval time, and SHA-256 of every
raw input.

Rendering decisions (deterministic, aligned with the pinned first-source builder
so wording diffs are attributable to the source, not the renderer):
- Stat wording lines are rendered at the gem's maximum available ``per_level``
  level, positionally aligned to ``static.stats`` ids (null per-level entries
  fall back to the static base value) — identical rule to the pinned builder.
- The fork's authoritative pre-rendered English (``static.stat_text``) is
  preferred per stat id; local translation rendering is the fallback.
- Stat-translation entries are applied verbatim: English variant chosen by
  condition match on the raw value (null min/max treated as absent), ``ignore``
  formats skipped, index_handlers applied to numeric substitutions.
- Fork quality stats are templated ``{"stat": text, "stats": {id: value}}``
  records. Placeholders that exactly match a key are substituted with the value
  divided by 1000 (RePoE per-mille convention, same as the pinned builder).
  Compound placeholder expressions (e.g. ``{a/b}``) are left verbatim — never
  invent unit conversions.
- Support-gem translated lines starting with "Skills " are prefixed with
  "Supported " (same as the pinned builder).

Usage:
    python scripts/build_gem_corpus_snapshot_repoe_fork.py <fork_data_dir> <out_dir>
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

UPSTREAM_REPO = "https://github.com/repoe-fork/repoe"
UPSTREAM_HOSTED = "https://repoe-fork.github.io/data/"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _apply_handler(value, handler):
    if value is None or not handler:
        return value
    try:
        v = float(value)
    except (TypeError, ValueError):
        return value
    if handler == "negate":
        v = -v
    elif handler == "double":
        v = v * 2
    elif handler == "negate_and_double":
        v = -v * 2
    elif handler == "times_twenty":
        v = v * 20
    elif handler == "multiply_by_four":
        v = v * 4
    elif handler == "divide_by_one_hundred":
        v = v / 100
    elif handler == "divide_by_one_thousand":
        v = v / 1000
    elif handler.startswith("divide_by_ten"):
        v = v / 10
    elif handler == "divide_by_two_0dp":
        v = v / 2
    elif handler == "divide_by_five":
        v = v / 5
    elif handler in ("milliseconds_to_seconds",) or handler.startswith("milliseconds_to_seconds"):
        v = v / 1000
    elif handler == "per_minute_to_per_second" or handler.startswith("per_minute_to_per_second_"):
        v = v / 60
    elif handler == "old_leech_percent":
        v = v / 5
    elif handler == "old_leech_permyriad":
        v = v / 100
    if v == int(v):
        return int(v)
    return round(v, 2)


def _condition_matches(condition, value) -> bool:
    for cond in condition or []:
        if not isinstance(cond, dict):
            continue
        if value is None:
            return False
        # Fork encodes absent bounds as explicit nulls; treat null as absent.
        if cond.get("min") is not None and value < cond["min"]:
            return False
        if cond.get("max") is not None and value > cond["max"]:
            return False
    return True


def _build_translation_index(translations: list) -> dict:
    index: dict[str, list] = {}
    for entry in translations:
        for stat_id in entry.get("ids", []):
            index.setdefault(stat_id, []).append(entry)
    return index


def _render_stat(stat_id, value, indexes, is_support, condition_value=None):
    for index in indexes:
        entries = index.get(stat_id)
        if entries:
            break
    else:
        return f"{stat_id}: {value}"
    if condition_value is None:
        condition_value = value
    for entry in entries:
        for english in entry.get("English", []):
            formats = english.get("format") or []
            if formats and all(f == "ignore" for f in formats):
                continue
            if not _condition_matches(english.get("condition") or [], condition_value):
                continue
            text = english.get("string") or ""
            handlers = english.get("index_handlers") or []
            flat_handlers = [h for group in handlers for h in (group or [None])] or [None]
            for i, match in enumerate(re.finditer(r"\{(\d+)(?::[^}]*)?\}", text)):
                idx = int(match.group(1))
                handler = flat_handlers[idx] if idx < len(flat_handlers) else (
                    flat_handlers[0] if flat_handlers else None)
                rendered = _apply_handler(value, handler) if handler else value
                text = text.replace(match.group(0), str(rendered))
            if is_support and text.startswith("Skills "):
                text = "Supported " + text
            return text
    return f"{stat_id}: {value}"


def _fmt_per_mille(value) -> str:
    if isinstance(value, (int, float)):
        return str(value / 1000)
    return str(value)


def _render_quality(qstat: dict) -> str | None:
    """Render one fork quality record; compound placeholders stay verbatim."""
    template = qstat.get("stat")
    values = qstat.get("stats") or {}
    if not isinstance(template, str) or not template.strip():
        return None

    def _sub(match):
        key = match.group(1)
        if key in values:
            return _fmt_per_mille(values[key])
        return match.group(0)  # compound / unknown expression: verbatim

    return re.sub(r"\{([^{}]+)\}", _sub, template)


def _gem_stats_at_max_level(gem: dict):
    static = gem.get("static") or {}
    static_stats = static.get("stats") or []
    per_level = gem.get("per_level") or {}
    if per_level:
        max_level = max(per_level.keys(), key=lambda k: int(k))
        level_stats = (per_level[max_level] or {}).get("stats") or []
    else:
        level_stats = []
    out = []
    for i, stat in enumerate(static_stats):
        if not isinstance(stat, dict) or "id" not in stat:
            continue
        value = stat.get("value")
        if i < len(level_stats) and isinstance(level_stats[i], dict) and level_stats[i].get("value") is not None:
            value = level_stats[i]["value"]
        out.append((stat["id"], value))
    return out


def build_snapshot(fork_dir: Path) -> list[dict]:
    gems_raw = json.loads((fork_dir / "gems_full.json").read_text(encoding="utf-8"))
    aggregate_index = _build_translation_index(
        json.loads((fork_dir / "stat_translations.json").read_text(encoding="utf-8"))
    )
    per_file_indexes: dict[str, dict] = {}
    translations_dir = fork_dir / "stat_translations"
    if translations_dir.is_dir():
        for path in sorted(translations_dir.glob("*.json")):
            per_file_indexes[f"stat_translations/{path.stem}"] = _build_translation_index(
                json.loads(path.read_text(encoding="utf-8"))
            )

    gems: list[dict] = []
    for gem_id, gem in sorted(gems_raw.items()):
        base_item = gem.get("base_item") or {}
        name = base_item.get("display_name") or gem.get("display_name") or gem_id
        is_support = bool(gem.get("is_support"))
        active_skill = gem.get("active_skill") or {}
        description = str(active_skill.get("description") or "").strip()
        gem_indexes = [
            per_file_indexes[gem["stat_translation_file"]],
            aggregate_index,
        ] if gem.get("stat_translation_file") in per_file_indexes else [aggregate_index]

        # The fork ships authoritative pre-rendered English per static stat id
        # (``static.stat_text``); prefer it and fall back to local translation
        # rendering, then to the raw ``stat_id: value`` receipt form.
        stat_text = (gem.get("static") or {}).get("stat_text") or {}

        wording: list[str] = []
        if description:
            wording.append(description)
        for stat_id, value in _gem_stats_at_max_level(gem):
            line = stat_text.get(stat_id) or _render_stat(stat_id, value, gem_indexes, is_support)
            if line:
                wording.append(line)

        quality_wording: list[str] = []
        for qstat in (gem.get("static") or {}).get("quality_stats") or []:
            if not isinstance(qstat, dict):
                continue
            line = _render_quality(qstat)
            if line:
                quality_wording.append(line)

        gems.append({
            "id": gem_id,
            "name": name,
            "kind": "support" if is_support else "active",
            "tags": [str(t) for t in gem.get("tags") or []],
            "description": description,
            "wording": wording,
            "quality_wording": quality_wording,
            "release_state": str(base_item.get("release_state") or "released"),
        })
    return gems


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    fork_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    gems_path = fork_dir / "gems_full.json"
    translations_path = fork_dir / "stat_translations.json"
    version_path = fork_dir / "version.txt"
    for path in (gems_path, translations_path):
        if not path.exists():
            raise SystemExit(f"missing fork input: {path}")

    data_era = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"

    gems = build_snapshot(fork_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = out_dir / "SECOND_SOURCE_SNAPSHOT.json"
    payload = {"gems": gems}
    snapshot_path.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    raw_inputs = {"gems.json": _sha256(gems_path), "stat_translations.json": _sha256(translations_path)}
    for path in sorted((fork_dir / "stat_translations").glob("*.json")):
        raw_inputs[f"stat_translations/{path.name}"] = _sha256(path)

    manifest = {
        "schema": "reflexion.gem_forge.corpus_manifest.v1",
        "source_id": "repoe-fork",
        "snapshot": str(snapshot_path),
        "snapshot_sha256": _sha256(snapshot_path),
        "gem_count": len(gems),
        "synthetic": False,
        "source": {
            "repo": UPSTREAM_REPO,
            "hosted_export": UPSTREAM_HOSTED,
            "data_era": f"repoe-fork hosted export, game version {data_era}",
            "game_version": data_era,
            "raw_inputs": raw_inputs,
            "fetched_at": "2026-07-24T19:53:16+00:00",
            "fetch_policy": "one-time generation-time fetch; the compiler NEVER fetches at run time",
        },
        "rendering_decisions": [
            "stat wording rendered at gem max available per_level level (same rule as pinned builder)",
            "fork's pre-rendered static.stat_text preferred per stat id; local translation render as fallback",
            "stat-translation entries applied verbatim; 'ignore' formats skipped; null condition bounds treated as absent",
            "quality placeholders matching a stats key divided by 1000 (RePoE per-mille convention)",
            "compound quality placeholder expressions left verbatim",
            "support-gem lines starting with 'Skills ' prefixed with 'Supported '",
        ],
        "generator": "scripts/build_gem_corpus_snapshot_repoe_fork.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = out_dir / "SECOND_SOURCE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"snapshot: {snapshot_path} ({len(gems)} gems, sha256 {manifest['snapshot_sha256'][:16]}…)")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
