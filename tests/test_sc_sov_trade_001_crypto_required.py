"""Item 1: cryptography is a hard requirement; no production fallback."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SOV = REPO / "sov_trade"


def test_no_production_ed25519_fallback_module() -> None:
    assert not (SOV / "_ed25519.py").exists()
    import re
    forbidden = (
        r"\b_ed25519\b",
        r"\bpublickey_unsafe\b",
        r"\bsignature_unsafe\b",
        r"\bcheckvalid\b",
        r"vendored_ed25519",
    )
    for path in sorted(SOV.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert re.search(token, text) is None, f"{path} still mentions {token}"


def test_production_modules_do_not_import_a_fallback() -> None:
    for path in sorted(SOV.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "_ed25519" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert "_ed25519" not in module
                for alias in node.names:
                    assert alias.name != "_ed25519"


def test_sov_trade_refuses_to_import_without_cryptography() -> None:
    # Import in a clean subprocess whose meta_path blocks cryptography.
    program = r"""
import sys
class _BlockCryptography:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "cryptography" or fullname.startswith("cryptography."):
            raise ImportError("cryptography blocked for refusal test")
        return None
sys.meta_path.insert(0, _BlockCryptography())
sys.modules.pop("cryptography", None)
try:
    import semantic_compiler.sov_trade as st  # noqa: F401
except ImportError as exc:
    text = str(exc).lower()
    if "cryptography" in text:
        raise SystemExit(0)
    raise SystemExit(f"ImportError did not mention cryptography: {exc}")
raise SystemExit("sov_trade imported without cryptography")
"""
    env = dict(**{k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"})
    # Make the repo importable as semantic_compiler, same pattern as CI.
    import tempfile, os
    tmp = tempfile.mkdtemp(prefix="sov-refuse-")
    link = Path(tmp) / "semantic_compiler"
    link.symlink_to(REPO)
    env["PYTHONPATH"] = tmp
    result = subprocess.run(
        [sys.executable, "-c", program],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"


def test_package_declares_cryptography_pin() -> None:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    assert "cryptography>=50.0.2,<51" in text
