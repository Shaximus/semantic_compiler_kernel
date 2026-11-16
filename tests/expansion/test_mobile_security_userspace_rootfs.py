"""Regression checks for mobile_security userspace rootfs extension (v1.2)."""

from pathlib import Path

import yaml


TEMPLATE = Path(__file__).resolve().parents[2] / "expansion" / "templates" / "mobile_security.yaml"


def _load():
    return yaml.safe_load(TEMPLATE.read_text())


def test_version_at_least_1_2():
    data = _load()
    assert float(data["version"]) >= 1.2


def test_userspace_rootfs_components_present():
    names = {c["name"] for c in _load()["components"]}
    for required in {
        "userspace_rootfs_runtime",
        "path_translation_shim",
        "bootstrap_blob_loader",
        "selinux_exec_workaround",
        "renamed_native_loader_alias",
    }:
        assert required in names


def test_proot_not_equated_to_root_exploit_invariant():
    blob = "\n".join(_load()["invariants"]).lower()
    assert "not evidence of android kernel privilege escalation" in blob
    assert "content hashes" in blob or "content hash" in blob


def test_failure_modes_for_misread_and_keyword_overclaim():
    names = {f["name"] for f in _load()["failure_modes"]}
    assert "proot_misread_as_root_exploit" in names
    assert "dex_bypass_keyword_overclaim" in names
    assert "renamed_loader_identity_miss" in names
