"""
Logos Calibration Corpus Generator V2.1

Generates ~60-100 deliberately varied samples across the categories needed to
calibrate the Semantic Compiler's scoring, tiering, and training-data export.

Outputs:
    - calibration_corpus_v2_1.jsonl
    - calibration_report_v2_1.md

Usage:
    cd /home/shax/Apps/semantic_compiler
    PYTHONPATH=/home/shax/Apps python3 scripts/generate_calibration_corpus.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from semantic_compiler.core.dataset import build_dataset_row, export_rows_to_jsonl
from semantic_compiler.core.pipeline import compile_semantic_packet


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_DIR / "calibration_output"
BENCHMARK_DIR = REPO_DIR / "benchmarks"


def _reason_codes(row: dict[str, Any]) -> list[str]:
    """Collect short reason codes explaining the row's quality disposition."""
    codes: list[str] = []
    decision = row["decision"]["status"]
    iso = row["isomorphism_analysis"]["aggregate"]["aggregate_isomorphism_quality"]
    quality = row["quality"]

    if decision == "NEEDS_REVISION" and iso > 0.5:
        codes.append("HIGH_QUALITY_NEEDS_REVISION")
    if quality["semantic_quality_tier"] != quality["dataset_utility_tier"]:
        codes.append("SEMANTIC_UTILITY_TIER_SPLIT")
    if not row["semantic_compilation"]["semantic_ir"].get("relationships"):
        codes.append("NO_RELATIONSHIPS_EXTRACTED")
    if row["semantic_compilation"]["target_resolution"]["status"] == "UNRESOLVED":
        codes.append("UNRESOLVED_TARGET_FRAME")

    for gate_name, gate in row["quality"]["hard_gates"].items():
        if gate.get("applicable") and gate.get("passed") is False:
            codes.append(f"{gate_name.upper()}_FAILED")

    for contradiction in row["semantic_compilation"]["adversarial"].get("contradictions", []):
        if isinstance(contradiction, dict):
            if contradiction.get("repair") and contradiction.get("resolved"):
                codes.append("CORRECTION_PROPOSED")
            elif not contradiction.get("repair") and not contradiction.get("resolved"):
                codes.append("UNRESOLVED_CONTRADICTION")

    return codes


# ---------------------------------------------------------------------------
# Calibration inputs, grouped by intended category
# ---------------------------------------------------------------------------

CALIBRATION_INPUTS: list[dict[str, Any]] = [
    # --- Strong valid isomorphisms ---
    {"category": "strong_isomorphism", "text": "The company has an immune system that detects threats and remembers them."},
    {"category": "strong_isomorphism", "text": "A firewall is like a cell membrane that controls what enters and leaves."},
    {"category": "strong_isomorphism", "text": "The nervous system routes signals like a telecommunications network."},
    {"category": "strong_isomorphism", "text": "The brain's memory consolidates during sleep like a database running garbage collection."},
    {"category": "strong_isomorphism", "text": "A country's economy circulates resources like a body's metabolism."},
    {"category": "strong_isomorphism", "text": "The judicial system filters disputes like a kidney filters blood."},
    {"category": "strong_isomorphism", "text": "A supply chain delivers materials like a circulatory system delivers oxygen."},
    {"category": "strong_isomorphism", "text": "A security team patrols the network like an immune system patrols the body."},

    # --- Useful heuristic metaphors ---
    {"category": "heuristic_metaphor", "text": "The market is a living organism that adapts to its environment."},
    {"category": "heuristic_metaphor", "text": "Time is money."},
    {"category": "heuristic_metaphor", "text": "The codebase is a garden that needs regular weeding."},
    {"category": "heuristic_metaphor", "text": "The organization is a ship navigating stormy seas."},
    {"category": "heuristic_metaphor", "text": "Data is the new oil."},
    {"category": "heuristic_metaphor", "text": "The project is a marathon, not a sprint."},
    {"category": "heuristic_metaphor", "text": "The internet is a series of tubes."},
    {"category": "heuristic_metaphor", "text": "The team is a well-oiled machine."},

    # --- Category errors ---
    {"category": "category_error", "text": "Magnetism explains the Moon's orbit because opposites attract."},
    {"category": "category_error", "text": "The company's mood is depressed, so revenue will fall."},
    {"category": "category_error", "text": "Atoms want to be happy, so they share electrons."},
    {"category": "category_error", "text": "Gravity works because the Earth loves us."},
    {"category": "category_error", "text": "The AI is lazy because it didn't answer quickly."},
    {"category": "category_error", "text": "The economy is angry at the government."},
    {"category": "category_error", "text": "Water remembers molecules, so homeopathy works."},
    {"category": "category_error", "text": "Crystals can heal because they have good vibes."},

    # --- Scale failures ---
    {"category": "scale_failure", "text": "What applies to a single neuron applies directly to the whole brain."},
    {"category": "scale_failure", "text": "One bad employee means the entire company is corrupt."},
    {"category": "scale_failure", "text": "If quantum particles are uncertain, then corporations are uncertain."},
    {"category": "scale_failure", "text": "A cell has a nucleus, so a person has a nucleus."},
    {"category": "scale_failure", "text": "The team is just one big person."},
    {"category": "scale_failure", "text": "What is true for bacteria is true for ecosystems without modification."},
    {"category": "scale_failure", "text": "A family argument proves nations cannot cooperate."},
    {"category": "scale_failure", "text": "One line of buggy code means the whole AI is conscious."},

    # --- Unresolved target frames ---
    {"category": "unresolved_frame", "text": "The thing does stuff with other things."},
    {"category": "unresolved_frame", "text": "It was good and bad at the same time."},
    {"category": "unresolved_frame", "text": "Something happened somewhere."},
    {"category": "unresolved_frame", "text": "They did it because reasons."},
    {"category": "unresolved_frame", "text": "Everything is connected."},
    {"category": "unresolved_frame", "text": "The system has parts that interact."},
    {"category": "unresolved_frame", "text": "It works like something but I don't know what."},
    {"category": "unresolved_frame", "text": "Stuff and things."},

    # --- Contradiction-and-repair cases ---
    {"category": "contradiction_repair", "text": "The AI is fully autonomous. Actually, it needs human approval for every action."},
    {"category": "contradiction_repair", "text": "The system is completely secure. We found a critical vulnerability yesterday."},
    {"category": "contradiction_repair", "text": "There is no hierarchy. Curtis has final authority."},
    {"category": "contradiction_repair", "text": "All data is public. This data must remain confidential."},
    {"category": "contradiction_repair", "text": "The model never hallucinates. Here is a known hallucination case."},
    {"category": "contradiction_repair", "text": "We have no secrets. The API key is in the repo."},
    {"category": "contradiction_repair", "text": "The process is automated. A human manually runs each step."},
    {"category": "contradiction_repair", "text": "The mapping is literal. It is only a metaphor."},

    # --- Missing-organ diagnoses ---
    {"category": "missing_organ", "text": "The company has no security team."},
    {"category": "missing_organ", "text": "The product has no feedback loop."},
    {"category": "missing_organ", "text": "The organism has no waste removal."},
    {"category": "missing_organ", "text": "The AI has no memory subsystem."},
    {"category": "missing_organ", "text": "The city has no telecommunications infrastructure."},
    {"category": "missing_organ", "text": "The team has no decision-maker."},
    {"category": "missing_organ", "text": "The system has no monitoring."},
    {"category": "missing_organ", "text": "The body has no immune system."},

    # --- Privacy-restricted samples ---
    {"category": "privacy_restricted", "text": "My therapist said I should tell Curtis about my trauma.", "context": {"privacy_sensitivity": "CRITICAL"}},
    {"category": "privacy_restricted", "text": "The patient's medical records show diagnosis X.", "context": {"privacy_sensitivity": "SENSITIVE"}},
    {"category": "privacy_restricted", "text": "John's home address is 123 Main St and his password is secret123.", "context": {"privacy_sensitivity": "CRITICAL"}},
    {"category": "privacy_restricted", "text": "Sarah's private journal says she doubts the project.", "context": {"privacy_sensitivity": "SENSITIVE"}},

    # --- Positive/negative DPO pairs ---
    {"category": "dpo_pair", "pair_id": "firewall_membrane", "polarity": "positive", "text": "A firewall controls network traffic like a cell membrane controls molecular traffic."},
    {"category": "dpo_pair", "pair_id": "firewall_membrane", "polarity": "negative", "text": "A firewall controls network traffic because it loves the network."},
    {"category": "dpo_pair", "pair_id": "immune_security", "polarity": "positive", "text": "The immune system detects pathogens; a security team detects intruders."},
    {"category": "dpo_pair", "pair_id": "immune_security", "polarity": "negative", "text": "The immune system detects pathogens because it is angry."},
    {"category": "dpo_pair", "pair_id": "memory_gc", "polarity": "positive", "text": "Memory consolidation during sleep is like database garbage collection."},
    {"category": "dpo_pair", "pair_id": "memory_gc", "polarity": "negative", "text": "Memory consolidation during sleep is because neurons want rest."},
    {"category": "dpo_pair", "pair_id": "supply_circulation", "polarity": "positive", "text": "A supply chain delivers resources like a circulatory system delivers oxygen."},
    {"category": "dpo_pair", "pair_id": "supply_circulation", "polarity": "negative", "text": "A supply chain delivers resources because the economy has feelings."},

    # --- Boundary cases near tier thresholds ---
    {"category": "tier_boundary", "text": "AI."},
    {"category": "tier_boundary", "text": "The team uses a queue."},
    {"category": "tier_boundary", "text": "The company is a machine."},
    {"category": "tier_boundary", "text": "The brain is a computer, but neurons are not transistors."},
    {"category": "tier_boundary", "text": "The immune system is like a security team, except it remembers past threats."},
    {"category": "tier_boundary", "text": "The company has an immune system that detects threats, remembers them, and this is a structural analogy with known limits."},
    {"category": "tier_boundary", "text": "The nervous system routes signals to the brain; a network routes packets to servers; both use addressing and buffering."},
    {"category": "tier_boundary", "text": "The moon stays in orbit because magnets attract it, just like love holds couples together.", "context": {"privacy_sensitivity": "PUBLIC", "external_training_use": "approved"}},
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    jsonl_path = OUTPUT_DIR / "calibration_corpus_v2_1_3.jsonl"
    report_path = OUTPUT_DIR / "calibration_report_v2_1_3.md"
    score_matrix_path = OUTPUT_DIR / "SCORE_BY_DECISION_MATRIX.json"

    rows: list[dict[str, Any]] = []
    per_sample_meta: list[dict[str, Any]] = []

    for item in CALIBRATION_INPUTS:
        category = item["category"]
        text = item["text"]
        context = item.get("context", {})

        packet = compile_semantic_packet(text, context=context)
        row = build_dataset_row(packet)

        rows.append(row)
        relationship_count = len(
            row["semantic_compilation"]["semantic_ir"].get("relationships", [])
        )
        per_sample_meta.append({
            "sample_id": row["sample_id"],
            "category": category,
            "pair_id": item.get("pair_id"),
            "polarity": item.get("polarity"),
            "decision": row["decision"]["status"],
            "semantic_quality_tier": row["quality"]["semantic_quality_tier"],
            "dataset_utility_tier": row["quality"]["dataset_utility_tier"],
            "training_ready": row["quality"]["training_ready"],
            "tier": row["quality"]["dataset_tier"],
            "schema_valid": row["audit"]["schema_valid"],
            "target_resolution": row["semantic_compilation"]["target_resolution"]["status"],
            "isomorphism_quality": row["isomorphism_analysis"]["aggregate"]["aggregate_isomorphism_quality"],
            "mapping_quality": row["isomorphism_analysis"]["aggregate"]["aggregate_mapping_quality"],
            "assessment_coverage": row["isomorphism_analysis"]["aggregate"]["aggregate_assessment_coverage"],
            "structural_fit": row["quality"]["compiler_scores"].get("structural_fit"),
            "relationship_count": relationship_count,
            "hard_gates_passed": all(
                g.get("passed") is not False or not g.get("applicable")
                for g in row["quality"]["hard_gates"].values()
            ),
            "reason_codes": _reason_codes(row),
        })

    # Export validated JSONL.
    result = export_rows_to_jsonl(rows, jsonl_path, validate=True)

    # Compute distributions.
    decisions = Counter(m["decision"] for m in per_sample_meta)
    tiers = Counter(m["tier"] for m in per_sample_meta)
    categories = Counter(m["category"] for m in per_sample_meta)
    target_res = Counter(m["target_resolution"] for m in per_sample_meta)
    hard_gate_failures = sum(1 for m in per_sample_meta if not m["hard_gates_passed"])
    forced_targets = sum(1 for m in per_sample_meta if m["target_resolution"] == "FORCED")
    unresolved_frames = sum(1 for m in per_sample_meta if m["target_resolution"] == "UNRESOLVED")
    schema_invalid = sum(1 for m in per_sample_meta if not m["schema_valid"])

    iso_scores = [m["isomorphism_quality"] for m in per_sample_meta]
    structural_fits = [m["structural_fit"] for m in per_sample_meta if m["structural_fit"] is not None]

    def avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def median(values: list[float]) -> float:
        if not values:
            return 0.0
        s = sorted(values)
        n = len(s)
        if n % 2 == 1:
            return s[n // 2]
        return (s[n // 2 - 1] + s[n // 2]) / 2.0

    # Score-by-decision matrix.
    decision_matrix: dict[str, dict[str, Any]] = {}
    for decision in sorted({m["decision"] for m in per_sample_meta}):
        samples = [m for m in per_sample_meta if m["decision"] == decision]
        iso_vals = [m["isomorphism_quality"] for m in samples]
        struct_vals = [m["structural_fit"] for m in samples if m["structural_fit"] is not None]
        decision_matrix[decision] = {
            "count": len(samples),
            "mean_isomorphism_quality": round(avg(iso_vals), 4),
            "median_isomorphism_quality": round(median(iso_vals), 4),
            "min_isomorphism_quality": round(min(iso_vals), 4) if iso_vals else 0.0,
            "max_isomorphism_quality": round(max(iso_vals), 4) if iso_vals else 0.0,
            "mean_mapping_quality": round(avg([m["mapping_quality"] for m in samples]), 4),
            "mean_assessment_coverage": round(avg([m["assessment_coverage"] for m in samples]), 4),
            "mean_structural_fit": round(avg(struct_vals), 4) if struct_vals else 0.0,
            "reason_codes": sorted({code for m in samples for code in m["reason_codes"]}),
        }

    score_matrix_path.write_text(
        json.dumps(decision_matrix, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    high_quality_needs_revision = [
        {
            "sample_id": m["sample_id"],
            "category": m["category"],
            "isomorphism_quality": m["isomorphism_quality"],
            "reason_codes": m["reason_codes"],
        }
        for m in per_sample_meta
        if m["decision"] == "NEEDS_REVISION" and m["isomorphism_quality"] > 0.5
    ]

    # Category-level metrics.
    category_metrics: dict[str, dict[str, Any]] = {}
    for cat in sorted(categories):
        cat_samples = [m for m in per_sample_meta if m["category"] == cat]
        cat_decisions = Counter(m["decision"] for m in cat_samples)
        cat_tiers = Counter(m["tier"] for m in cat_samples)
        cat_targets = Counter(m["target_resolution"] for m in cat_samples)
        category_metrics[cat] = {
            "count": len(cat_samples),
            "mean_iso_quality": avg([m["isomorphism_quality"] for m in cat_samples]),
            "mean_structural_fit": avg([m["structural_fit"] for m in cat_samples if m["structural_fit"] is not None]),
            "decisions": dict(sorted(cat_decisions.items())),
            "tiers": dict(sorted(cat_tiers.items())),
            "target_resolution": dict(sorted(cat_targets.items())),
        }

    # DPO pair deltas.
    dpo_pairs: dict[str, dict[str, Any]] = {}
    for m in per_sample_meta:
        pair_id = m.get("pair_id")
        if not pair_id:
            continue
        if pair_id not in dpo_pairs:
            dpo_pairs[pair_id] = {}
        dpo_pairs[pair_id][m["polarity"]] = m

    dpo_deltas: list[dict[str, Any]] = []
    for pair_id, pols in sorted(dpo_pairs.items()):
        pos = pols.get("positive")
        neg = pols.get("negative")
        if pos and neg:
            dpo_deltas.append({
                "pair_id": pair_id,
                "positive_iso": pos["isomorphism_quality"],
                "negative_iso": neg["isomorphism_quality"],
                "delta": pos["isomorphism_quality"] - neg["isomorphism_quality"],
                "positive_tier": pos["tier"],
                "negative_tier": neg["tier"],
                "positive_decision": pos["decision"],
                "negative_decision": neg["decision"],
            })

    # Expected-vs-actual category mapping (Logos/compiler disagreement).
    # These are heuristics for calibration review, not ground truth.
    expected_outcomes: dict[str, dict[str, Any]] = {
        "strong_isomorphism": {"expected_decisions": {"COMPILED"}, "expected_tier_min": "SILVER"},
        "heuristic_metaphor": {"expected_decisions": {"COMPILED", "COMPILED_WITH_GUARDRAILS"}, "expected_tier_min": "SILVER"},
        "category_error": {"expected_decisions": {"REJECT", "NEEDS_REVISION", "QUARANTINE"}, "expected_tier_min": "BRONZE"},
        "scale_failure": {"expected_decisions": {"REJECT", "NEEDS_REVISION", "COMPILED_WITH_GUARDRAILS"}, "expected_tier_min": "BRONZE"},
        "unresolved_frame": {"expected_decisions": {"UNRESOLVED"}, "expected_tier_min": "BRONZE"},
        "contradiction_repair": {"expected_decisions": {"COMPILED_WITH_GUARDRAILS", "NEEDS_REVISION"}, "expected_tier_min": "GOLD"},
        "missing_organ": {"expected_decisions": {"COMPILED", "COMPILED_WITH_GUARDRAILS"}, "expected_tier_min": "SILVER"},
        "privacy_restricted": {"expected_decisions": {"COMPILED_PRIVATE_REDACTED_ONLY", "COMPILED_SUPERVISED_ONLY"}, "expected_tier_min": "SILVER"},
        "dpo_pair": {"expected_decisions": set(), "expected_tier_min": None},
        "tier_boundary": {"expected_decisions": set(), "expected_tier_min": None},
    }

    TIER_ORDER = ["REJECT", "BRONZE", "SILVER", "GOLD", "DIAMOND", "DIAMOND_PLUS"]

    def _tier_rank(tier: str) -> int:
        try:
            return TIER_ORDER.index(tier)
        except ValueError:
            return -1

    disagreement_notes: list[dict[str, Any]] = []
    for cat, metrics in category_metrics.items():
        expected = expected_outcomes.get(cat, {})
        expected_decisions = expected.get("expected_decisions", set())
        expected_tier_min = expected.get("expected_tier_min")

        # Flag if the most common decision is unexpected.
        if expected_decisions:
            most_common_decision = max(metrics["decisions"], key=metrics["decisions"].get)
            if most_common_decision not in expected_decisions:
                disagreement_notes.append({
                    "category": cat,
                    "issue": "most_common_decision_unexpected",
                    "expected": sorted(expected_decisions),
                    "actual": most_common_decision,
                    "count": metrics["decisions"][most_common_decision],
                })

        # Flag if mean tier is below expected minimum.
        if expected_tier_min:
            min_rank = _tier_rank(expected_tier_min)
            below_count = sum(
                count for tier, count in metrics["tiers"].items()
                if _tier_rank(tier) < min_rank
            )
            if below_count > metrics["count"] // 2:
                disagreement_notes.append({
                    "category": cat,
                    "issue": "majority_below_expected_tier",
                    "expected_min": expected_tier_min,
                    "below_count": below_count,
                    "total": metrics["count"],
                })

    report = f"""# Logos Calibration Corpus Report V2.1

Generated: {jsonl_path}
Total samples: {len(rows)}
Schema-valid rows exported: {result['written']}
Rows skipped by validator: {result['skipped']}

## Sample categories

| Category | Count |
|---|---:|
{chr(10).join(f"| {cat} | {count} |" for cat, count in sorted(categories.items()))}

## Compiler decision distribution

| Decision | Count |
|---|---:|
{chr(10).join(f"| {dec} | {count} |" for dec, count in sorted(decisions.items()))}

## Tier distribution

| Tier | Count |
|---|---:|
{chr(10).join(f"| {tier} | {count} |" for tier, count in sorted(tiers.items()))}

## Target frame resolution

| Status | Count |
|---|---:|
{chr(10).join(f"| {status} | {count} |" for status, count in sorted(target_res.items()))}

## Quality metrics

| Metric | Value |
|---|---:|
| Schema validity rate | {(len(rows) - schema_invalid) / len(rows) * 100:.1f}% |
| Hard gate failure frequency | {hard_gate_failures} / {len(rows)} ({hard_gate_failures / len(rows) * 100:.1f}%) |
| Forced target frequency | {forced_targets} / {len(rows)} ({forced_targets / len(rows) * 100:.1f}%) |
| Unresolved frame frequency | {unresolved_frames} / {len(rows)} ({unresolved_frames / len(rows) * 100:.1f}%) |
| Mean isomorphism quality | {avg(iso_scores):.3f} |
| Mean structural fit | {avg(structural_fits):.3f} |

## Score-by-decision matrix

| Decision | Count | Mean ISO | Median ISO | Min ISO | Max ISO | Mean Map Q | Mean Coverage | Mean Struct Fit |
|---|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(
    f"| {dec} | {m['count']} | {m['mean_isomorphism_quality']:.3f} | {m['median_isomorphism_quality']:.3f} | "
    f"{m['min_isomorphism_quality']:.3f} | {m['max_isomorphism_quality']:.3f} | "
    f"{m['mean_mapping_quality']:.3f} | {m['mean_assessment_coverage']:.3f} | {m['mean_structural_fit']:.3f} |"
    for dec, m in sorted(decision_matrix.items())
)}

## Decision reason codes

| Decision | Reason codes |
|---|---|
{chr(10).join(
    f"| {dec} | {', '.join(m['reason_codes']) or '—'} |"
    for dec, m in sorted(decision_matrix.items())
)}

## High-quality NEEDS_REVISION records

These records have an isomorphism quality above 0.5 but still need revision,
indicating a decision-calibration gap rather than a low-quality mapping.

| sample_id | category | ISO quality | reason_codes |
|---|---|---:|---|
{chr(10).join(
    f"| {r['sample_id']} | {r['category']} | {r['isomorphism_quality']:.3f} | {', '.join(r['reason_codes']) or '—'} |"
    for r in high_quality_needs_revision
) if high_quality_needs_revision else "| — | — | — | — |"}

## Category-level calibration

| Category | Count | Mean ISO | Mean Struct Fit | Decisions | Tiers | Target Resolution |
|---|---|---:|---:|---|---|---|
{chr(10).join(
    f"| {cat} | {m['count']} | {m['mean_iso_quality']:.3f} | {m['mean_structural_fit']:.3f} | "
    f"{json.dumps(m['decisions'])} | {json.dumps(m['tiers'])} | {json.dumps(m['target_resolution'])} |"
    for cat, m in category_metrics.items()
)}

## DPO pair deltas

| Pair ID | Δ ISO | Positive ISO | Negative ISO | Positive Tier | Negative Tier | Positive Decision | Negative Decision |
|---|---|---:|---:|---|---|---|---|---|
{chr(10).join(
    f"| {d['pair_id']} | {d['delta']:+.3f} | {d['positive_iso']:.3f} | {d['negative_iso']:.3f} | "
    f"{d['positive_tier']} | {d['negative_tier']} | {d['positive_decision']} | {d['negative_decision']} |"
    for d in dpo_deltas
)}

## Expected-vs-actual category disagreement

| Category | Issue | Details |
|---|---|---|
{chr(10).join(
    f"| {n['category']} | {n['issue']} | {json.dumps({k: v for k, v in n.items() if k not in {'category', 'issue'}})} |"
    for n in disagreement_notes
) if disagreement_notes else "| — | none | No category-level disagreement detected. |"}

## Per-sample detail

| sample_id | category | decision | semantic_tier | utility_tier | training_ready | target_resolution | iso_quality | relationships | schema_valid |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(
    f"| {m['sample_id']} | {m['category']} | {m['decision']} | {m['semantic_quality_tier']} | {m['dataset_utility_tier']} | {m['training_ready']} | {m['target_resolution']} | {m['isomorphism_quality']:.3f} | {m['relationship_count']} | {m['schema_valid']} |"
    for m in per_sample_meta
)}

## Validation errors (if any)

```json
{json.dumps(result['errors'], indent=2)}
```
"""

    report_path.write_text(report, encoding="utf-8")

    # -------------------------------------------------------------------------
    # V2.1.3 required artifacts
    # -------------------------------------------------------------------------

    # 1. Score by mapping status.
    status_groups: dict[str, list[dict[str, Any]]] = {}
    for m in per_sample_meta:
        # Recover mapping_status from the dataset row if available.
        row = rows[per_sample_meta.index(m)]
        mapping_status = "UNKNOWN"
        if row.get("isomorphism_analysis", {}).get("mappings"):
            best = max(
                row["isomorphism_analysis"]["mappings"],
                key=lambda x: x.get("ranking_score", 0.0) or 0.0,
            )
            mapping_status = best.get("mapping_status", "UNKNOWN")
        status_groups.setdefault(mapping_status, []).append(m)

    score_by_status: dict[str, dict[str, Any]] = {}
    for status, samples in status_groups.items():
        iso_vals = [m["isomorphism_quality"] for m in samples]
        score_by_status[status] = {
            "count": len(samples),
            "mean_isomorphism_quality": round(avg(iso_vals), 4),
            "median_isomorphism_quality": round(median(iso_vals), 4),
            "min_isomorphism_quality": round(min(iso_vals), 4) if iso_vals else 0.0,
            "max_isomorphism_quality": round(max(iso_vals), 4) if iso_vals else 0.0,
            "decisions": dict(sorted(Counter(m["decision"] for m in samples).items())),
        }
    score_by_status_path = OUTPUT_DIR / "SCORE_BY_MAPPING_STATUS.json"
    score_by_status_path.write_text(
        json.dumps(score_by_status, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # 2. DPO delta distribution.
    dpo_delta_distribution = {
        "pairs": dpo_deltas,
        "count": len(dpo_deltas),
        "mean_delta": avg([d["delta"] for d in dpo_deltas]) if dpo_deltas else 0.0,
        "median_delta": median([d["delta"] for d in dpo_deltas]) if dpo_deltas else 0.0,
        "min_delta": min([d["delta"] for d in dpo_deltas]) if dpo_deltas else 0.0,
        "max_delta": max([d["delta"] for d in dpo_deltas]) if dpo_deltas else 0.0,
    }
    dpo_delta_path = OUTPUT_DIR / "DPO_DELTA_DISTRIBUTION.json"
    dpo_delta_path.write_text(
        json.dumps(dpo_delta_distribution, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # 3. Kestrel review selection: best/worst and boundary cases.
    review_selection: list[dict[str, Any]] = []
    sorted_by_iso = sorted(per_sample_meta, key=lambda m: m["isomorphism_quality"])
    for m in sorted_by_iso[:10] + sorted_by_iso[-10:]:
        row = rows[per_sample_meta.index(m)]
        review_selection.append({
            "sample_id": m["sample_id"],
            "category": m["category"],
            "decision": m["decision"],
            "semantic_quality_tier": m["semantic_quality_tier"],
            "dataset_utility_tier": m["dataset_utility_tier"],
            "isomorphism_quality": m["isomorphism_quality"],
            "relationship_count": m["relationship_count"],
            "target_resolution": m["target_resolution"],
            "reason_codes": m["reason_codes"],
            "text": row["input"]["raw_input"],
        })
    # Add boundary cases near thresholds.
    for m in per_sample_meta:
        if 0.45 <= m["isomorphism_quality"] <= 0.65 and m not in sorted_by_iso[:10] and m not in sorted_by_iso[-10:]:
            row = rows[per_sample_meta.index(m)]
            review_selection.append({
                "sample_id": m["sample_id"],
                "category": m["category"],
                "decision": m["decision"],
                "semantic_quality_tier": m["semantic_quality_tier"],
                "dataset_utility_tier": m["dataset_utility_tier"],
                "isomorphism_quality": m["isomorphism_quality"],
                "relationship_count": m["relationship_count"],
                "target_resolution": m["target_resolution"],
                "reason_codes": m["reason_codes"],
                "text": row["input"]["raw_input"],
            })
    kestrel_path = OUTPUT_DIR / "KESTREL_REVIEW_SELECTION_V2_1_3.json"
    kestrel_path.write_text(
        json.dumps(review_selection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # 4. Empty mapping invariant report.
    unassessed_rows = [
        (m, rows[per_sample_meta.index(m)])
        for m in per_sample_meta
        if any(
            mapping.get("mapping_status") == "UNASSESSED"
            for mapping in rows[per_sample_meta.index(m)]
                .get("isomorphism_analysis", {})
                .get("mappings", [])
        )
    ]
    empty_report_lines = [
        "# Empty Mapping Invariant Report V2.1.3",
        "",
        "Verifies that unassessed mappings receive null quality, zero coverage,",
        "zero confidence, and are never marked training-ready.",
        "",
        f"Total unassessed records: {len(unassessed_rows)}",
        "",
        "| sample_id | category | decision | mapping_quality | coverage | confidence | ranking_score | training_ready |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for m, row in unassessed_rows:
        mapping = next(
            (x for x in row.get("isomorphism_analysis", {}).get("mappings", []) if x.get("mapping_status") == "UNASSESSED"),
            {},
        )
        empty_report_lines.append(
            f"| {m['sample_id']} | {m['category']} | {m['decision']} | "
            f"{mapping.get('mapping_quality')} | {mapping.get('assessment_coverage')} | "
            f"{mapping.get('confidence')} | {mapping.get('ranking_score')} | {m['training_ready']} |"
        )
    empty_report_lines += ["", "### Invariant checks", ""]
    invariant_ok = True
    for m, row in unassessed_rows:
        for mapping in row.get("isomorphism_analysis", {}).get("mappings", []):
            if mapping.get("mapping_status") != "UNASSESSED":
                continue
            if mapping.get("mapping_quality") is not None:
                invariant_ok = False
                empty_report_lines.append(f"- FAIL {m['sample_id']}: mapping_quality is not null")
            if mapping.get("assessment_coverage", 1.0) != 0.0:
                invariant_ok = False
                empty_report_lines.append(f"- FAIL {m['sample_id']}: assessment_coverage is not 0.0")
            if mapping.get("confidence", 1.0) != 0.0:
                invariant_ok = False
                empty_report_lines.append(f"- FAIL {m['sample_id']}: confidence is not 0.0")
            if mapping.get("ranking_score", 1.0) != 0.0:
                invariant_ok = False
                empty_report_lines.append(f"- FAIL {m['sample_id']}: ranking_score is not 0.0")
            if m["training_ready"]:
                invariant_ok = False
                empty_report_lines.append(f"- FAIL {m['sample_id']}: training_ready is True")
    if invariant_ok:
        empty_report_lines.append("- All invariants hold for unassessed mappings.")
    empty_report_path = OUTPUT_DIR / "EMPTY_MAPPING_INVARIANT_REPORT.md"
    empty_report_path.write_text("\n".join(empty_report_lines), encoding="utf-8")

    # 5. Negative category decision report.
    negative_inputs = [item for item in CALIBRATION_INPUTS if item["category"] == "category_error"]
    negative_report_lines = [
        "# Negative Category Decision Report V2.1.3",
        "",
        "Tracks how semantic error classes route category-error samples.",
        "",
        "| text | decision | semantic_error_class | repair_proposed |",
        "|---|---|---|---|",
    ]
    for item in negative_inputs:
        packet = compile_semantic_packet(item["text"], context=item.get("context", {}))
        error_class = getattr(packet, "semantic_error_class", None)
        repair_proposed = any(
            c.get("repair") for c in packet.contradictions if isinstance(c, dict)
        )
        negative_report_lines.append(
            f"| {item['text'][:60]}{'...' if len(item['text']) > 60 else ''} | "
            f"{packet.decision.name if packet.decision else 'PENDING'} | {error_class or '—'} | {repair_proposed} |"
        )
    negative_report_path = OUTPUT_DIR / "NEGATIVE_CATEGORY_DECISION_REPORT.md"
    negative_report_path.write_text("\n".join(negative_report_lines), encoding="utf-8")

    # 6. Relative clause extraction report.
    relative_examples = [
        "The company has an immune system that detects threats and remembers them.",
        "A firewall is a membrane which filters packets.",
        "The nervous system routes signals to the brain.",
        "The brain's memory consolidates during sleep.",
        "A supply chain delivers materials like a circulatory system delivers oxygen.",
    ]
    relative_report_lines = [
        "# Relative Clause / Coordinated Verb Extraction Report V2.1.3",
        "",
        "Verifies extraction of relative-clause subjects, coordinated verbs, and pronoun antecedents.",
        "",
        "| input | relationships |",
        "|---|---|",
    ]
    for text in relative_examples:
        packet = compile_semantic_packet(text)
        rels = packet.semantic_ir.relationships
        rel_summary = "; ".join(
            f"{r.get('source_entity_id')}--{r.get('predicate')}-->{r.get('target_entity_id')}"
            for r in rels
        ) or "none"
        relative_report_lines.append(f"| {text} | {rel_summary} |")
    relative_report_path = OUTPUT_DIR / "RELATIVE_CLAUSE_EXTRACTION_REPORT.md"
    relative_report_path.write_text("\n".join(relative_report_lines), encoding="utf-8")

    # 7. Missing-organ labeled benchmark report (markdown copy).
    benchmark_report_path = OUTPUT_DIR / "MISSING_ORGAN_LABELED_BENCHMARK.md"
    benchmark_eval_report = json.loads(
        (BENCHMARK_DIR / "missing_organ_evaluation_report.json").read_text(encoding="utf-8")
    )
    benchmark_report_lines = [
        "# Missing-Organ Labeled Benchmark Report V2.1.3",
        "",
        f"Examples evaluated: {benchmark_eval_report['metrics'].get('examples_evaluated', '—')}",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Gate |",
        "|---|---|---|",
        f"| ABSENT_CONFIRMED precision | {benchmark_eval_report['metrics']['absent_confirmed_precision']:.3f} | {'PASS' if benchmark_eval_report['gates']['precision_ge_0_90'] else 'FAIL'} |",
        f"| ABSENT_CONFIRMED recall | {benchmark_eval_report['metrics']['absent_confirmed_recall']:.3f} | {'PASS' if benchmark_eval_report['gates']['recall_ge_0_80'] else 'FAIL'} |",
        f"| Fragment false-positive rate | {benchmark_eval_report['metrics']['fragment_false_positive_rate']:.3f} | {'PASS' if benchmark_eval_report['gates']['fragment_fpr_le_0_10'] else 'FAIL'} |",
        "",
        "## Misclassifications (first 20)",
        "",
        "| description | department | true | predicted | status |",
        "|---|---|---|---|---|",
    ]
    for f in benchmark_eval_report["failures"][:20]:
        benchmark_report_lines.append(
            f"| {f['description']} | {f['department']} | {f['true']} | {f['predicted']} | {f['status']} |"
        )
    benchmark_report_path.write_text("\n".join(benchmark_report_lines), encoding="utf-8")

    print(f"Wrote {jsonl_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {score_by_status_path}")
    print(f"Wrote {dpo_delta_path}")
    print(f"Wrote {kestrel_path}")
    print(f"Wrote {empty_report_path}")
    print(f"Wrote {negative_report_path}")
    print(f"Wrote {relative_report_path}")
    print(f"Wrote {benchmark_report_path}")
    print(f"Exported {result['written']} rows; skipped {result['skipped']}")


if __name__ == "__main__":
    main()
