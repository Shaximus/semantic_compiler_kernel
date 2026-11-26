"""Binding to the real SC-MAFUBA-001 manifests (reference only).

rc1 section 6 step 1 asks that SCC-001-AC bind to docs/evidence/sc-mafuba-001/
manifests/{disturbance,resource,sink}.yaml. This module hashes those files so
the Authority Plane can pin them in Pi, and reports whether a manifest carries
a principal signature or an R_override partition. It parses nothing else and
writes nothing.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

MANIFEST_DIR = Path(__file__).resolve().parents[3] / "docs" / "evidence" / "sc-mafuba-001" / "manifests"
MANIFEST_NAMES = ("disturbance.yaml", "resource.yaml", "sink.yaml")


def manifest_bytes(name: str) -> bytes:
    if name not in MANIFEST_NAMES:
        raise ValueError(name)
    return (MANIFEST_DIR / name).read_bytes()


def manifest_sha256(name: str) -> str:
    return hashlib.sha256(manifest_bytes(name)).hexdigest()


def pinned_manifests() -> dict:
    return {n: manifest_sha256(n) for n in MANIFEST_NAMES}


def verify_manifest(plane, name: str, data: bytes) -> bool:
    """Hash-verify manifest bytes against the pin in Pi. Unknown or unpinned => False."""
    pin = plane.manifest_sha(name)
    return pin is not None and hashlib.sha256(data).hexdigest() == pin


def _keys(data: bytes) -> set:
    out = set()
    for line in data.decode("utf-8").splitlines():
        s = line.split("#", 1)[0]
        if ":" in s and not s.startswith((" ", "\t", "-")):
            out.add(s.split(":", 1)[0].strip())
        elif ":" in s:
            out.add(s.split(":", 1)[0].strip().lstrip("- ").strip())
    return out


def has_principal_signature(name: str) -> bool:
    return "principal_signature" in _keys(manifest_bytes(name))


def declares_r_override(name: str = "resource.yaml") -> bool:
    return "R_override" in _keys(manifest_bytes(name))
