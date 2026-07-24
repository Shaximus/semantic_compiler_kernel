"""Tests for the pinned gem corpus snapshot (gate: provenance + hash)."""

import hashlib
import json

import pytest

from semantic_compiler.expansion.gem_forge.corpus import (
    CorpusPinError,
    PINNED_MANIFEST_PATH,
    PINNED_SNAPSHOT_PATH,
    load_pinned_corpus,
)


def test_pinned_corpus_loads_and_hash_matches_manifest():
    gems = load_pinned_corpus()
    with PINNED_MANIFEST_PATH.open() as f:
        manifest = json.load(f)
    assert len(gems) == manifest["gem_count"]
    actual = hashlib.sha256(PINNED_SNAPSHOT_PATH.read_bytes()).hexdigest()
    assert actual == manifest["snapshot_sha256"]


def test_manifest_records_league_pin_provenance_and_fetch_policy():
    with PINNED_MANIFEST_PATH.open() as f:
        manifest = json.load(f)
    source = manifest["source"]
    assert source["repo"] == "https://github.com/brather1ng/RePoE"
    assert source["gems_json_commit"]  # upstream commit pin
    assert "2022-08-23" in source["data_era"]  # league/version era pin
    assert source["raw_inputs"]["gems.json"]  # raw input hash recorded
    assert "NEVER fetches at run time" in source["fetch_policy"]


def test_tampered_snapshot_fails_closed(tmp_path):
    payload = json.loads(PINNED_SNAPSHOT_PATH.read_text())
    payload["gems"][0]["name"] = "Tampered Gem"
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(payload))
    with pytest.raises(CorpusPinError):
        load_pinned_corpus(snapshot_path=tampered)


def test_missing_manifest_fails_closed(tmp_path):
    with pytest.raises(CorpusPinError):
        load_pinned_corpus(manifest_path=tmp_path / "nope.json")


def test_pinned_gems_have_wording_and_kinds():
    gems = load_pinned_corpus()
    assert len(gems) > 900  # full RePoE gem set
    kinds = {gem.kind for gem in gems}
    assert "support" in kinds and "active" in kinds
    with_wording = [gem for gem in gems if gem.wording]
    assert len(with_wording) / len(gems) > 0.8
    gmp = next(g for g in gems if "Greater Multiple Projectiles" in g.name)
    assert any("additional Projectiles" in line for line in gmp.wording)
