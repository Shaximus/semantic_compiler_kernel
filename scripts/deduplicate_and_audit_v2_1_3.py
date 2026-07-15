"""
Deduplicate and audit the V2.1.3 release-candidate corpus.

Produces:
  - UNIQUE_REVIEW_SELECTION_V2_1_3.json
  - DUPLICATE_COLLAPSE_REPORT.md
  - SCORE_PLATEAU_ROOT_CAUSE.md
  - TRAINING_READINESS_INVARIANT_REPORT.md
  - REMAINING_NEGATIVE_ROUTING_REPORT.md

Usage:
    cd /home/shax/Apps/semantic_compiler
    PYTHONPATH=/home/shax/Apps python3 scripts/deduplicate_and_audit_v2_1_3.py
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from semantic_compiler.core.pipeline import compile_semantic_packet
from semantic_compiler.core.types import Decision


OUTPUT_DIR = Path("/home/shax/Apps/semantic_compiler/calibration_output")


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(the|a|an|is|are|was|were|has|have|had|like|as)\b", "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def semantic_signature(s: dict[str, Any]) -> str:
    return " | ".join([
        normalize_text(s["text"]),
        s["category"],
        s.get("subcategory") or "none",
        s["decision"],
        s.get("semantic_quality_tier") or s["decision"],
        s.get("semantic_error_class") or "none",
        str(s["relationship_count"]),
    ])


def load_corpus(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_selection_from_corpus(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract the same metadata the generator wrote to HUMAN_REVIEW_SELECTION."""
    selection = []
    for row in rows:
        packet_meta = row["semantic_compilation"]
        iso = row["isomorphism_analysis"]["aggregate"]
        selection.append({
            "sample_id": row["sample_id"],
            "text": row["input"]["raw_input"],
            "category": row.get("metadata", {}).get("category", "unknown"),
            "subcategory": row.get("metadata", {}).get("subcategory"),
            "decision": row["decision"]["status"],
            "semantic_quality_tier": row["quality"]["semantic_quality_tier"],
            "dataset_utility_tier": row["quality"]["dataset_utility_tier"],
            "training_ready": row["quality"]["training_ready"],
            "isomorphism_quality": iso["aggregate_isomorphism_quality"],
            "mapping_quality": iso["aggregate_mapping_quality"],
            "assessment_coverage": iso["aggregate_assessment_coverage"],
            "target_resolution": packet_meta["target_resolution"]["status"],
            "relationship_count": len(packet_meta["semantic_ir"].get("relationships", [])),
            "semantic_error_class": row["semantic_compilation"].get("semantic_error_class"),
        })
    return selection


def deduplicate(selection: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    by_sig: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for s in selection:
        by_sig[semantic_signature(s)].append(s)

    representatives: list[dict[str, Any]] = []
    for sig, rows in by_sig.items():
        rep = rows[0].copy()
        rep["duplicate_count"] = len(rows)
        rep["duplicate_sample_ids"] = [r["sample_id"] for r in rows]
        representatives.append(rep)

    return representatives, dict(by_sig)


def produce_duplicate_report(
    selection: list[dict[str, Any]],
    unique: list[dict[str, Any]],
    groups: dict[str, list[dict[str, Any]]],
) -> str:
    lines = [
        "# Duplicate Collapse Report V2.1.3",
        "",
        f"Original review selection rows: {len(selection)}",
        f"Unique semantic signatures: {len(unique)}",
        f"Duplicate reduction: {len(selection) - len(unique)} rows ({(len(selection) - len(unique)) / len(selection) * 100:.1f}%)",
        "",
        "## Largest duplicate groups",
        "",
        "| count | representative_text |",
        "|---:|---|",
    ]
    for sig, rows in sorted(groups.items(), key=lambda x: -len(x[1]))[:20]:
        text = rows[0]["text"]
        lines.append(f"| {len(rows)} | {text[:90]}{'...' if len(text) > 90 else ''} |")

    lines += [
        "",
        "## Unique representatives by category",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for cat, count in sorted(Counter(u["category"] for u in unique).items()):
        lines.append(f"| {cat} | {count} |")

    lines += [
        "",
        "## Deduplication method",
        "",
        "Grouped by normalized text + category + subcategory + decision + semantic_quality_tier + semantic_error_class + relationship_count.",
    ]
    return "\n".join(lines)


def produce_plateau_report(unique: list[dict[str, Any]]) -> str:
    scores = [u["isomorphism_quality"] for u in unique]
    coverages = [u["assessment_coverage"] for u in unique]
    score_counts = Counter(round(s, 4) for s in scores)
    coverage_counts = Counter(round(c, 4) for c in coverages)

    lines = [
        "# Score Plateau Root-Cause Report V2.1.3",
        "",
        "## Distribution summary",
        "",
        f"- Unique samples: {len(unique)}",
        f"- Distinct ISO scores: {len(score_counts)}",
        f"- Distinct coverage values: {len(coverage_counts)}",
        f"- Most common ISO score: {score_counts.most_common(1)[0][0]} ({score_counts.most_common(1)[0][1]} samples)",
        f"- Most common coverage: {coverage_counts.most_common(1)[0][0]} ({coverage_counts.most_common(1)[0][1]} samples)",
        "",
        "## Top ISO score values",
        "",
        "| iso_score | count |",
        "|---:|---:|",
    ]
    for score, count in score_counts.most_common(10):
        lines.append(f"| {score} | {count} |")

    lines += [
        "",
        "## Top coverage values",
        "",
        "| coverage | count |",
        "|---:|---:|",
    ]
    for cov, count in coverage_counts.most_common(10):
        lines.append(f"| {cov} | {count} |")

    lines += [
        "",
        "## Likely root cause",
        "",
        "The geometric mean of assessment dimensions collapses many samples to the same value because:",
        "1. Most samples use the same set of populated dimensions (relationships, scale, contradictions).",
        "2. The weighting does not strongly differentiate clear analogies from weak metaphors.",
        "3. Several dimensions return default or near-default values for the majority of inputs.",
        "",
        "## Recommended fix",
        "",
        "Introduce a discriminative signal that depends on relationship quality and semantic error class, not only coverage count.",
    ]
    return "\n".join(lines)


def produce_training_readiness_report(unique: list[dict[str, Any]]) -> str:
    ready = [u for u in unique if u["training_ready"]]
    ready_zero_rels = [u for u in ready if u["relationship_count"] == 0]
    ambiguous_ready = [u for u in ready if u["category"] in {"ambiguous_figurative"}]

    lines = [
        "# Training Readiness Invariant Report V2.1.3",
        "",
        f"- Unique samples: {len(unique)}",
        f"- training_ready=true: {len(ready)}",
        f"- training_ready=true with relationship_count=0: {len(ready_zero_rels)}",
        f"- training_ready=true in ambiguous_figurative category: {len(ambiguous_ready)}",
        "",
        "## training_ready=true with zero relationships",
        "",
        "| text | decision | category | iso_quality |",
        "|---|---|---|---:|",
    ]
    for u in ready_zero_rels:
        text = u["text"]
        lines.append(
            f"| {text[:80]}{'...' if len(text) > 80 else ''} | {u['decision']} | {u['category']} | {u['isomorphism_quality']:.4f} |"
        )

    lines += [
        "",
        "## Invariant violation",
        "",
        "A record should not be training-ready when no relationships were extracted from an explicit analogy or causal claim.",
        f"Violations found: {len(ready_zero_rels)}",
        "",
        "## Recommended fix",
        "",
        "Add a hard gate: `training_ready` requires `relationship_count > 0` for ANALOGY/CAUSAL/METAPHOR inputs, unless the input is explicitly non-relational.",
    ]
    return "\n".join(lines)


def produce_negative_routing_report() -> str:
    """Test additional negative-category claims that may escape rejection."""
    test_cases = [
        ("Magnetic bracelets cure arthritis by aligning energy fields.", "FALSE_MECHANISM"),
        ("The Sun orbits the Earth because it is loyal.", "ANTHROPOMORPHIC_CAUSATION"),
        ("The project died because nobody believed in it.", "ANTHROPOMORPHIC_CAUSATION"),
        ("Electrons choose their paths through a circuit.", "ANTHROPOMORPHIC_CAUSATION"),
        ("A black hole remembers everything it consumes.", "FALSE_MECHANISM"),
        ("Planets dance around the Sun in harmony.", "ANTHROPOMORPHIC_CAUSATION"),
        ("Lightning strikes because the sky is angry.", "ANTHROPOMORPHIC_CAUSATION"),
        ("The nervous system routes signals to the brain.", "RHETORICAL_PERSONIFICATION"),
    ]

    results = []
    for text, expected in test_cases:
        packet = compile_semantic_packet(text)
        actual = getattr(packet, "semantic_error_class", None)
        decision = packet.decision.name if packet.decision else "PENDING"
        reject_classes = {
            "ANTHROPOMORPHIC_CAUSATION",
            "PHYSICAL_CATEGORY_ERROR",
            "FALSE_MECHANISM",
            "UNSUPPORTED_CAUSAL_TRANSFER",
            "IDENTITY_ANALOGY_CONFUSION",
        }
        expected_decision = "REJECT" if expected in reject_classes else "COMPILED_WITH_GUARDRAILS"
        results.append({
            "text": text,
            "expected_class": expected,
            "actual_class": actual,
            "expected_decision": expected_decision,
            "actual_decision": decision,
            "correct": actual == expected and decision == expected_decision,
        })

    lines = [
        "# Remaining Negative Routing Report V2.1.3",
        "",
        "## Expanded test results",
        "",
        "| text | expected_class | actual_class | expected_decision | actual_decision | correct |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        text = r["text"]
        lines.append(
            f"| {text[:55]}{'...' if len(text) > 55 else ''} | {r['expected_class']} | "
            f"{r['actual_class'] or '—'} | {r['expected_decision']} | {r['actual_decision']} | {r['correct']} |"
        )

    correct = sum(1 for r in results if r["correct"])
    lines += [
        "",
        f"## Accuracy: {correct}/{len(results)} ({correct / len(results) * 100:.1f}%)",
        "",
        "## Escaped claims",
        "",
    ]
    escaped = [r for r in results if not r["correct"]]
    if escaped:
        for r in escaped:
            lines.append(f"- {r['text']} → expected {r['expected_decision']}/{r['expected_class']}, got {r['actual_decision']}/{r['actual_class'] or 'None'}")
    else:
        lines.append("- None in this expanded set.")

    return "\n".join(lines)


def perform_first_pass_review(unique: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Apply deterministic first-pass rules to flag cases that need founder judgment.
    """
    disputed: list[dict[str, Any]] = []

    for u in unique:
        reasons: list[str] = []

        # Invariant: training_ready with zero relationships on an analogy/figurative input.
        if u["training_ready"] and u["relationship_count"] == 0 and u["category"] in {"positive_analogy", "ambiguous_figurative", "invalid_repairable"}:
            reasons.append("TRAINING_READY_ZERO_RELATIONSHIPS")

        # Invariant: ambiguous figurative marked training-ready.
        if u["training_ready"] and u["category"] == "ambiguous_figurative":
            reasons.append("AMBIGUOUS_TRAINING_READY")

        # Invariant: explicitly incomplete whole systems should not be compiled/training-ready.
        if u["training_ready"] and u["category"] == "whole_system" and "lacks" in u["text"].lower():
            reasons.append("INCOMPLETE_SYSTEM_TRAINING_READY")

        # Decision/score mismatch: high ISO but not compiled, or low ISO but compiled.
        if u["isomorphism_quality"] > 0.6 and u["decision"] not in {"COMPILED", "COMPILED_WITH_GUARDRAILS"}:
            reasons.append("HIGH_ISO_NON_COMPILED")
        if u["isomorphism_quality"] < 0.3 and u["decision"] in {"COMPILED", "COMPILED_WITH_GUARDRAILS"}:
            reasons.append("LOW_ISO_COMPILED")

        # Rhetorical personification on non-figurative inputs.
        if u["semantic_error_class"] == "RHETORICAL_PERSONIFICATION" and u["category"] == "positive_analogy":
            reasons.append("FALSE_PERSONIFICATION_ON_ANALOGY")

        if reasons:
            u = u.copy()
            u["first_pass_reasons"] = reasons
            disputed.append(u)

    return disputed


def main() -> None:
    selection_path = OUTPUT_DIR / "HUMAN_REVIEW_SELECTION_V2_1_3.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))

    unique, groups = deduplicate(selection)

    # Write unique review selection.
    unique_path = OUTPUT_DIR / "UNIQUE_REVIEW_SELECTION_V2_1_3.json"
    unique_path.write_text(json.dumps(unique, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write reports.
    reports = {
        "DUPLICATE_COLLAPSE_REPORT.md": produce_duplicate_report(selection, unique, groups),
        "SCORE_PLATEAU_ROOT_CAUSE.md": produce_plateau_report(unique),
        "TRAINING_READINESS_INVARIANT_REPORT.md": produce_training_readiness_report(unique),
        "REMAINING_NEGATIVE_ROUTING_REPORT.md": produce_negative_routing_report(),
    }
    for filename, content in reports.items():
        (OUTPUT_DIR / filename).write_text(content, encoding="utf-8")

    # First-pass review.
    disputed = perform_first_pass_review(unique)
    disputed_path = OUTPUT_DIR / "FIRST_PASS_DISPUTED_CASES_V2_1_3.json"
    disputed_path.write_text(json.dumps(disputed, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {unique_path} ({len(unique)} unique from {len(selection)} selected)")
    for filename in reports:
        print(f"Wrote {OUTPUT_DIR / filename}")
    print(f"Wrote {disputed_path} ({len(disputed)} disputed cases)")


if __name__ == "__main__":
    main()
