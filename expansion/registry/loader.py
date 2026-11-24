"""Load and validate domain templates."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from semantic_compiler.expansion.schema import (
    DOMAIN_TEMPLATE_SCHEMA_PATH,
    validate_domain_template,
)


@dataclass(frozen=True)
class DomainTemplate:
    domain: str
    version: float
    description: str
    components: list[dict]
    relationships: list[dict]
    invariants: list[str]
    failure_modes: list[dict]
    architecture_patterns: list[dict]


TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

_CACHE_FORMAT_VERSION = 1
_MEM_CACHE_LOCK = threading.Lock()
_MEM_CACHE: dict[str, tuple[tuple[Any, ...], dict[str, DomainTemplate]]] = {}


def _compute_dir_signature(template_dir: Path) -> tuple[list[Path], list[list[Any]]]:
    """Return (sorted_yaml_paths, [[name, mtime_ns, size], ...]) including schema stat."""
    yaml_paths = sorted(template_dir.glob("*.yaml"))
    sig: list[list[Any]] = []
    for path in yaml_paths:
        st = path.stat()
        sig.append([path.name, st.st_mtime_ns, st.st_size])
    try:
        schema_st = DOMAIN_TEMPLATE_SCHEMA_PATH.stat()
        sig.append(["__schema__", schema_st.st_mtime_ns, schema_st.st_size])
    except OSError:
        pass
    return yaml_paths, sig


def _sidecar_cache_path(resolved_dir: Path) -> Path:
    digest = hashlib.sha256(str(resolved_dir).encode("utf-8")).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"semantic_compiler_templates_v{_CACHE_FORMAT_VERSION}_{digest}.json"


def _read_sidecar_cache(
    cache_path: Path,
    expected_sig: list[list[Any]],
) -> dict[str, DomainTemplate] | None:
    try:
        raw = cache_path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return None
        if payload.get("cache_version") != _CACHE_FORMAT_VERSION:
            return None
        if payload.get("signature") != expected_sig:
            return None
        items = payload.get("templates")
        if not isinstance(items, dict):
            return None
        templates: dict[str, DomainTemplate] = {}
        for domain, data in items.items():
            if not isinstance(data, dict):
                return None
            templates[domain] = DomainTemplate(**data)
        return templates
    except (OSError, ValueError, TypeError, KeyError):
        return None


def _write_sidecar_cache(
    cache_path: Path,
    signature: list[list[Any]],
    templates: dict[str, DomainTemplate],
) -> None:
    tmp_path: Path | None = None
    try:
        cache_dir = cache_path.parent
        payload = {
            "cache_version": _CACHE_FORMAT_VERSION,
            "signature": signature,
            "templates": {domain: asdict(tmpl) for domain, tmpl in templates.items()},
        }
        serialized = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        fd, tmp_name = tempfile.mkstemp(
            prefix=".sc_tmpl_",
            suffix=".tmp",
            dir=str(cache_dir),
        )
        tmp_path = Path(tmp_name)
        fd_owned = False
        try:
            fh = os.fdopen(fd, "w", encoding="utf-8")
            fd_owned = True
            with fh:
                fh.write(serialized)
        except Exception:
            if not fd_owned:
                try:
                    os.close(fd)
                except OSError:
                    pass
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            return
        os.replace(tmp_path, cache_path)
    except OSError:
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


def load_templates(template_dir: Path | None = None) -> dict[str, DomainTemplate]:
    """Load and validate all *.yaml domain templates from template_dir, keyed by domain."""
    template_dir = Path(template_dir) if template_dir is not None else TEMPLATE_DIR
    resolved_dir = template_dir.resolve()
    resolved_key = str(resolved_dir)

    yaml_paths, sig = _compute_dir_signature(template_dir)
    sig_key = tuple((row[0], row[1], row[2]) for row in sig)

    # 1. Process-local in-memory cache (avoids double YAML/JSON parsing across index + elevator)
    with _MEM_CACHE_LOCK:
        cached = _MEM_CACHE.get(resolved_key)
        if cached is not None and cached[0] == sig_key:
            return dict(cached[1])

    # 2. Persistent mtime+size-validated JSON sidecar cache in tempfile.gettempdir()
    try:
        cache_path: Path | None = _sidecar_cache_path(resolved_dir)
    except OSError:
        cache_path = None

    if cache_path is not None:
        templates = _read_sidecar_cache(cache_path, sig)
        if templates is not None:
            with _MEM_CACHE_LOCK:
                _MEM_CACHE[resolved_key] = (sig_key, templates)
            return dict(templates)

    # 3. Cold parse + schema validation from YAML, then write sidecar cache
    templates = {}
    for path in yaml_paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        errors = validate_domain_template(data)
        if errors:
            raise ValueError(f"Invalid template {path}: {errors}")
        tmpl = DomainTemplate(**data)
        templates[tmpl.domain] = tmpl

    if cache_path is not None:
        _write_sidecar_cache(cache_path, sig, templates)
    with _MEM_CACHE_LOCK:
        _MEM_CACHE[resolved_key] = (sig_key, templates)
    return dict(templates)
