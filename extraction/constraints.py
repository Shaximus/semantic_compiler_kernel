"""
Reflexion Semantic Compiler v2.0.0 — Constraint Extraction

Citation: v1.0 Spec Section 8 — Master Pipeline
"""

from __future__ import annotations
from typing import Any

# Re-export from evidence module for backwards compatibility
from semantic_compiler.extraction.evidence import (
    extract_declared_constraints,
    extract_unknowns,
)

__all__ = ["extract_declared_constraints", "extract_unknowns"]
