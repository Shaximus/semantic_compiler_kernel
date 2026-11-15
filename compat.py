"""Backwards-compatible entry-point module.

Historically held post-hoc fixes for ``core/pipeline.py`` while ``core/`` was
under the V3.0.0 freeze. As of V3.1.1, those fixes (decision-dependent
derivative refresh, sensitive SFT prompt redaction, and dataset-row redaction)
live directly in ``core/pipeline.py`` and ``core/dataset.py``, so this module
is a thin re-export.
"""
from __future__ import annotations

from semantic_compiler.core.pipeline import compile_semantic_packet

__all__ = ["compile_semantic_packet"]
