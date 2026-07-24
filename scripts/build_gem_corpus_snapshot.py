#!/usr/bin/env python3
"""Build the pinned, normalized PoE gem corpus snapshot for gem_forge.

One-time GENERATION-TIME tool. The compiler never fetches anything: this
script converts a local RePoE checkout (gems.json + stat_translations.json)
into the normalized snapshot vendored at
``expansion/gem_forge/data/gem_corpus_snapshot.json`` plus a provenance
manifest (``CORPUS_MANIFEST.json``) recording the upstream pin and SHA-256
hashes of the raw inputs and the generated snapshot.

Rendering decisions (deterministic, documented):
- Stat wording lines are rendered at the gem's maximum level from
  ``per_level`` values positionally aligned to ``static.stats`` ids
  (null entries fall back to the static base value).
- RePoE stat-translation entries are applied verbatim: English variant
  chosen by condition match on the raw value, ``ignore`` formats skipped,
  index_handlers applied to numeric substitutions.
- Quality-stat values are per-mille in RePoE (1000 = 1%); they are divided
  by 1000 before translation rendering.
- Support-gem stat lines starting with "Skills " are prefixed with
  "Supported " to match in-game tooltip phrasing.

Usage:
    python scripts/build_gem_corpus_snapshot.py /path/to/RePoE-checkout
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_PATH = Path("expansion/gem_forge/data/gem_corpus_snapshot.json")
MANIFEST_PATH = Path("expansion/gem_forge/data/CORPUS_MANIFEST.json")

UPSTREAM_REPO = "https://github.com/brather1ng/RePoE"
UPSTREAM_GEMS_COMMIT = "157d1f33a1b32acaf6e552e714a28ee4610c4678"  # gems.json, 2022-08-23
UPSTREAM_DATA_ERA = "RePoE master snapshot (last gems.json update 2022-08-23; approx. PoE 3.19/3.20-era data)"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _apply_handler(value, handler: str):
    if value is None:
        return None
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
    elif handler == "divide_by_ten_1dp_if_required":
        v = v / 10
    elif handler == "divide_by_ten_0dp":
        v = v / 10
    elif handler == "divide_by_two_0dp":
        v = v / 2
    elif handler == "divide_by_five":
        v = v / 5
    elif handler == "milliseconds_to_seconds":
        v = v / 1000
    elif handler.startswith("milliseconds_to_seconds_2dp"):
        v = v / 1000
    elif handler == "per_minute_to_per_second":
        v = v / 60
    elif handler.startswith("per_minute_to_per_second_"):
        v = v / 60
    elif handler == "old_leech_percent":
        v = v / 5
    elif handler == "old_leech_permyriad":
        v = v / 100
    # Unhandled handlers (canonical_stat, affliction_reward_type, ...):
    # fall through with the raw value — never invent semantics.
    if v == int(v):
        return int(v)
    return round(v, 2)


def _condition_matches(condition: list, value) -> bool:
    for cond in condition:
        if not isinstance(cond, dict):
            continue
        if value is None:
            return False
        if "min" in cond and value < cond["min"]:
            return False
        if "max" in cond and value > cond["max"]:
            return False
    return True


def _build_translation_index(translations: list) -> dict:
    index: dict[str, list] = {}
    for entry in translations:
        for stat_id in entry.get("ids", []):
            index.setdefault(stat_id, []).append(entry)
    return index


def _render_stat(stat_id: str, value, indexes: list, is_support: bool, condition_value=None) -> str | None:
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


def _gem_stats_at_max_level(gem: dict) -> list[tuple[str, object]]:
    static = gem.get("static") or {}
    static_stats = static.get("stats") or []
    per_level = gem.get("per_level") or {}
    if per_level:
        max_level = max(per_level.keys(), key=lambda k: int(k))
        level_stats = (per_level[max_level] or {}).get("stats") or []
    else:
        level_stats = []
    out: list[tuple[str, object]] = []
    for i, stat in enumerate(static_stats):
        if not isinstance(stat, dict) or "id" not in stat:
            continue
        value = stat.get("value")
        if i < len(level_stats) and isinstance(level_stats[i], dict) and level_stats[i].get("value") is not None:
            value = level_stats[i]["value"]
        out.append((stat["id"], value))
    return out


def build_snapshot(repoe_dir: Path) -> list[dict]:
    gems_raw = json.loads((repoe_dir / "gems.json").read_text(encoding="utf-8"))
    translations = json.loads((repoe_dir / "stat_translations.json").read_text(encoding="utf-8"))
    aggregate_index = _build_translation_index(translations)
    # Per-file translation indexes (gem-specific files take priority over the
    # aggregate, which omits many *_final stat entries).
    per_file_indexes: dict[str, dict] = {}
    translations_dir = repoe_dir / "stat_translations"
    if translations_dir.is_dir():
        for path in sorted(translations_dir.glob("*.json")):
            if path.name.endswith(".min.json"):
                continue
            per_file_indexes[f"stat_translations/{path.stem}"] = _build_translation_index(
                json.loads(path.read_text(encoding="utf-8"))
            )

    gems: list[dict] = []
    for gem_id, gem in sorted(gems_raw.items()):
        base_item = gem.get("base_item") or {}
        name = base_item.get("display_name") or gem_id
        is_support = bool(gem.get("is_support"))
        active_skill = gem.get("active_skill") or {}
        description = str(active_skill.get("description") or "").strip()
        gem_indexes = [
            per_file_indexes[gem["stat_translation_file"]],
            aggregate_index,
        ] if gem.get("stat_translation_file") in per_file_indexes else [aggregate_index]

        wording: list[str] = []
        if description:
            wording.append(description)
        for stat_id, value in _gem_stats_at_max_level(gem):
            line = _render_stat(stat_id, value, gem_indexes, is_support)
            if line:
                wording.append(line)

        quality_wording: list[str] = []
        for qstat in (gem.get("static") or {}).get("quality_stats") or []:
            if not isinstance(qstat, dict) or "id" not in qstat:
                continue
            raw = qstat.get("value")
            value = raw / 1000 if isinstance(raw, (int, float)) else raw  # RePoE quality values are per-mille
            line = _render_stat(qstat["id"], value, gem_indexes, is_support, condition_value=raw)
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
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    repoe_dir = Path(sys.argv[1])
    gems_path = repoe_dir / "gems.json"
    translations_path = repoe_dir / "stat_translations.json"
    for path in (gems_path, translations_path):
        if not path.exists():
            raise SystemExit(f"missing RePoE input: {path}")

    gems = build_snapshot(repoe_dir)
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"gems": gems}
    SNAPSHOT_PATH.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema": "reflexion.gem_forge.corpus_manifest.v1",
        "snapshot": str(SNAPSHOT_PATH),
        "snapshot_sha256": _sha256(SNAPSHOT_PATH),
        "gem_count": len(gems),
        "source": {
            "repo": UPSTREAM_REPO,
            "data_era": UPSTREAM_DATA_ERA,
            "gems_json_commit": UPSTREAM_GEMS_COMMIT,
            "raw_inputs": {
                "gems.json": _sha256(gems_path),
                "stat_translations.json": _sha256(translations_path),
            },
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "fetch_policy": "one-time generation-time fetch; the compiler NEVER fetches at run time",
        },
        "rendering_decisions": [
            "stat wording rendered at gem max level (per_level values aligned to static.stats ids)",
            "RePoE stat-translation entries applied verbatim; 'ignore' formats skipped",
            "quality stat values divided by 1000 (RePoE per-mille convention)",
            "support-gem lines starting with 'Skills ' prefixed with 'Supported '",
        ],
        "generator": "scripts/build_gem_corpus_snapshot.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"snapshot: {SNAPSHOT_PATH} ({len(gems)} gems, sha256 {manifest['snapshot_sha256'][:16]}…)")
    print(f"manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
