"""Offline tests for scripts/usage_snapshot.py (no network, no token required)."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "usage_snapshot", REPO / "scripts" / "usage_snapshot.py"
)
assert SPEC is not None and SPEC.loader is not None
usage_snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(usage_snapshot)


def _payloads() -> dict[str, object]:
    return {
        "repos/acme/demo/traffic/clones": {
            "count": 10,
            "uniques": 4,
            "clones": [
                {"timestamp": "2026-11-11T00:00:00Z", "count": 3, "uniques": 2},
                {"timestamp": "2026-11-12T00:00:00Z", "count": 7, "uniques": 3},
            ],
        },
        "repos/acme/demo/traffic/views": {
            "count": 5,
            "uniques": 2,
            "views": [
                {"timestamp": "2026-11-11T00:00:00Z", "count": 5, "uniques": 2},
            ],
        },
        "repos/acme/demo/traffic/popular/referrers": [
            {"referrer": "github.com", "count": 5, "uniques": 2},
        ],
        "repos/acme/demo/traffic/popular/paths": [
            {"path": "/acme/demo", "title": "Overview", "count": 5, "uniques": 2},
        ],
        "repos/acme/demo": {
            "private": False,
            "visibility": "public",
            "stargazers_count": 3,
            "forks_count": 1,
            "subscribers_count": 2,
            "open_issues_count": 4,
        },
    }


class UsageSnapshotTests(unittest.TestCase):
    def test_token_from_env_requires_a_token(self) -> None:
        with self.assertRaises(usage_snapshot.GithubError):
            usage_snapshot.token_from_env(env={})
        self.assertEqual(usage_snapshot.token_from_env(env={"GITHUB_TOKEN": "abc"}), "abc")
        self.assertEqual(usage_snapshot.token_from_env(env={"GH_TOKEN": "xyz"}), "xyz")

    def test_fetch_snapshot_composes_api_payloads(self) -> None:
        payloads = _payloads()
        called: list[str] = []

        def getter(path: str, token: str) -> object:
            called.append(path)
            self.assertEqual(token, "unused")
            return payloads[path]

        snapshot = usage_snapshot.fetch_snapshot(
            "acme/demo", getter, "unused", snapshot_at="2026-11-25T15:00:00+00:00"
        )
        self.assertEqual(snapshot["repo"], "acme/demo")
        self.assertEqual(snapshot["visibility"], "public")
        self.assertEqual(snapshot["stars"], 3)
        self.assertEqual(snapshot["forks"], 1)
        self.assertEqual(snapshot["subscribers"], 2)
        self.assertEqual(snapshot["clones"]["count"], 10)
        self.assertEqual(snapshot["views"]["uniques"], 2)
        self.assertEqual(len(called), 5)

    def test_csv_row_flattens_window_totals(self) -> None:
        payloads = _payloads()
        snapshot = usage_snapshot.fetch_snapshot(
            "acme/demo",
            lambda path, token: payloads[path],
            "unused",
            snapshot_at="2026-11-25T15:00:00+00:00",
        )
        row = usage_snapshot.csv_row(snapshot)
        self.assertEqual(row["clones_count"], 10)
        self.assertEqual(row["clones_uniques"], 4)
        self.assertEqual(row["views_count"], 5)
        self.assertEqual(row["clone_window_start"], "2026-11-11T00:00:00Z")
        self.assertEqual(row["clone_window_end"], "2026-11-12T00:00:00Z")
        self.assertEqual(row["referrer_count"], 1)
        self.assertEqual(row["path_count"], 1)

    def test_append_history_writes_jsonl_csv_and_latest(self) -> None:
        payloads = _payloads()
        snapshot = usage_snapshot.fetch_snapshot(
            "acme/demo",
            lambda path, token: payloads[path],
            "unused",
            snapshot_at="2026-11-25T15:00:00+00:00",
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "history"
            usage_snapshot.append_history(out, snapshot)
            usage_snapshot.append_history(out, snapshot)
            lines = (out / "history.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            latest = usage_snapshot.json.loads((out / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(latest["stars"], 3)
            csv_text = (out / "history.csv").read_text(encoding="utf-8")
            self.assertEqual(csv_text.count("\n"), 3)  # header + two rows

    def test_resolve_out_dir_rejects_paths_inside_the_repo(self) -> None:
        with self.assertRaises(usage_snapshot.GithubError):
            usage_snapshot.resolve_out_dir(REPO / "docs" / "usage", root=REPO)
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "sc-usage"
            resolved = usage_snapshot.resolve_out_dir(outside, root=REPO)
            self.assertEqual(resolved, outside.resolve())


if __name__ == "__main__":
    unittest.main()
