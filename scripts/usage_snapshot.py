#!/usr/bin/env python3
"""Fetch GitHub traffic and popularity snapshots for this repository.

GitHub retains clone, view, referrer, and popular-path traffic for only
14 days. This script writes an accumulating history *outside* the
repository so older days are not lost. It performs no hidden telemetry:
the only network calls are to the GitHub REST API, and only from the
machine that runs the script.

Default history directory: ``/workspace/repos/sc-usage/``. Override with
``--out`` or the ``SC_USAGE_DIR`` environment variable. The script
refuses to write inside this git work tree.

Authentication: set ``GITHUB_TOKEN`` or ``GH_TOKEN``. Traffic endpoints
require a token with push access to the repository (or a fine-grained
token with Administration: Read). The token is never printed.

Usage::

    python scripts/usage_snapshot.py
    python scripts/usage_snapshot.py --out /workspace/repos/sc-usage
    python scripts/usage_snapshot.py --repo Shaximus/semantic_compiler_kernel
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_REPO = "Shaximus/semantic_compiler_kernel"
DEFAULT_OUT = Path("/workspace/repos/sc-usage")
API_ROOT = "https://api.github.com"
USER_AGENT = "semantic-compiler-kernel-usage-snapshot"

JsonGetter = Callable[[str, str], Any]

CSV_FIELDS = [
    "snapshot_at",
    "repo",
    "visibility",
    "clones_count",
    "clones_uniques",
    "views_count",
    "views_uniques",
    "clone_window_start",
    "clone_window_end",
    "stars",
    "forks",
    "subscribers",
    "open_issues_count",
    "referrer_count",
    "path_count",
]


class GithubError(RuntimeError):
    """A GitHub API call failed or required configuration is missing."""


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def token_from_env(env: dict[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    token = source.get("GITHUB_TOKEN") or source.get("GH_TOKEN")
    if not token:
        raise GithubError(
            "Set GITHUB_TOKEN or GH_TOKEN to a token that can read "
            "repository traffic (typically push access on the repo)."
        )
    return token


def github_get(path: str, token: str, timeout: float = 30.0) -> Any:
    url = f"{API_ROOT}/{path.lstrip('/')}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GithubError(
            f"GET {path} failed: HTTP {exc.code}: {body[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise GithubError(f"GET {path} failed: {exc.reason}") from exc


def _window_bounds(daily: list[dict[str, Any]] | None) -> tuple[str, str]:
    if not daily:
        return "", ""
    start = str(daily[0].get("timestamp") or "")
    end = str(daily[-1].get("timestamp") or "")
    return start, end


def fetch_snapshot(
    repo: str,
    getter: JsonGetter,
    token: str,
    *,
    snapshot_at: str | None = None,
) -> dict[str, Any]:
    clones = getter(f"repos/{repo}/traffic/clones", token)
    views = getter(f"repos/{repo}/traffic/views", token)
    referrers = getter(f"repos/{repo}/traffic/popular/referrers", token)
    paths = getter(f"repos/{repo}/traffic/popular/paths", token)
    meta = getter(f"repos/{repo}", token)
    when = snapshot_at or datetime.now(timezone.utc).isoformat()
    visibility = meta.get("visibility")
    if not visibility:
        visibility = "private" if meta.get("private") else "public"
    return {
        "snapshot_at": when,
        "repo": repo,
        "visibility": visibility,
        "stars": meta.get("stargazers_count"),
        "forks": meta.get("forks_count"),
        "subscribers": meta.get("subscribers_count"),
        "open_issues_count": meta.get("open_issues_count"),
        "clones": clones,
        "views": views,
        "referrers": referrers,
        "popular_paths": paths,
    }


def csv_row(snapshot: dict[str, Any]) -> dict[str, Any]:
    clones = snapshot.get("clones") or {}
    views = snapshot.get("views") or {}
    start, end = _window_bounds(clones.get("clones") or [])
    return {
        "snapshot_at": snapshot.get("snapshot_at", ""),
        "repo": snapshot.get("repo", ""),
        "visibility": snapshot.get("visibility", ""),
        "clones_count": clones.get("count", ""),
        "clones_uniques": clones.get("uniques", ""),
        "views_count": views.get("count", ""),
        "views_uniques": views.get("uniques", ""),
        "clone_window_start": start,
        "clone_window_end": end,
        "stars": snapshot.get("stars", ""),
        "forks": snapshot.get("forks", ""),
        "subscribers": snapshot.get("subscribers", ""),
        "open_issues_count": snapshot.get("open_issues_count", ""),
        "referrer_count": len(snapshot.get("referrers") or []),
        "path_count": len(snapshot.get("popular_paths") or []),
    }


def resolve_out_dir(out: Path, root: Path | None = None) -> Path:
    """Return a resolved history directory that is not inside the repo."""
    out = out.expanduser().resolve()
    root = (root or repo_root()).resolve()
    try:
        out.relative_to(root)
    except ValueError:
        return out
    raise GithubError(
        f"Refusing to write usage history inside the repository ({out}). "
        "Pass --out or set SC_USAGE_DIR to a path outside the repo."
    )


def append_history(out_dir: Path, snapshot: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "history.jsonl"
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(snapshot, sort_keys=True) + "\n")
    latest_path = out_dir / "latest.json"
    latest_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    csv_path = out_dir / "history.csv"
    row = csv_row(snapshot)
    new_file = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def format_summary(snapshot: dict[str, Any]) -> str:
    row = csv_row(snapshot)
    clones = snapshot.get("clones") or {}
    views = snapshot.get("views") or {}
    referrers = snapshot.get("referrers") or []
    paths = snapshot.get("popular_paths") or []
    window = ""
    if row["clone_window_start"] or row["clone_window_end"]:
        window = f" (UTC daily buckets {row['clone_window_start']} .. {row['clone_window_end']})"
    lines = [
        f"Snapshot at {row['snapshot_at']} for {row['repo']} ({row['visibility']})",
        f"Clones (14-day window{window}): {row['clones_count']} total, {row['clones_uniques']} unique cloners",
        f"Views (14-day window): {row['views_count']} total, {row['views_uniques']} unique visitors",
        f"Stars: {row['stars']}  Forks: {row['forks']}  Subscribers (watchers): {row['subscribers']}",
        f"open_issues_count (includes pull requests): {row['open_issues_count']}",
    ]
    if referrers:
        lines.append("Referrers:")
        for item in referrers:
            lines.append(
                f"  - {item.get('referrer')}: {item.get('count')} views / {item.get('uniques')} uniques"
            )
    if paths:
        lines.append("Popular paths:")
        for item in paths:
            lines.append(
                f"  - {item.get('path')}: {item.get('count')} views / {item.get('uniques')} uniques"
            )
    daily = clones.get("clones") or []
    if daily:
        lines.append("Clone days (UTC):")
        for item in daily:
            lines.append(
                f"  - {item.get('timestamp')}: {item.get('count')} clones / {item.get('uniques')} uniques"
            )
    daily_views = views.get("views") or []
    if daily_views:
        lines.append("View days (UTC):")
        for item in daily_views:
            if not item.get("count"):
                continue
            lines.append(
                f"  - {item.get('timestamp')}: {item.get('count')} views / {item.get('uniques')} uniques"
            )
    lines.append(
        "Note: GitHub clone totals include CI, mirrors, and crawlers. "
        "uniques are unique cloners/visitors, not unique IPs or billed users."
    )
    return "\n".join(lines)


def default_out_dir() -> Path:
    override = os.environ.get("SC_USAGE_DIR")
    return Path(override) if override else DEFAULT_OUT


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Snapshot GitHub traffic and stars/forks to a local history directory."
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"owner/name (default: {DEFAULT_REPO})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"history directory outside the repo (default: {DEFAULT_OUT} or SC_USAGE_DIR)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        token = token_from_env()
        out_dir = resolve_out_dir(args.out if args.out is not None else default_out_dir())
        snapshot = fetch_snapshot(args.repo, github_get, token)
        append_history(out_dir, snapshot)
    except GithubError as exc:
        print(f"usage_snapshot: {exc}", file=sys.stderr)
        return 1
    print(format_summary(snapshot))
    print(f"Wrote {out_dir / 'latest.json'}, appended {out_dir / 'history.jsonl'} and {out_dir / 'history.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
