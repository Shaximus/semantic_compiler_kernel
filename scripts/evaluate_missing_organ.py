"""
Evaluate missing-organ detector precision and recall against a hand-labeled
benchmark.

Usage:
    PYTHONPATH=/home/shax/Apps python3 scripts/evaluate_missing_organ.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from semantic_compiler.core.pipeline import compile_semantic_packet, infer_missing_functions
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.core.types import CompilerMode


BENCHMARK_PATH = Path(__file__).parent.parent / "benchmarks" / "missing_organ_labeled_benchmark.jsonl"

# States the detector may emit.
CONFIRMED_ABSENT_STATES = {"ABSENT_CONFIRMED", "MISSING"}
# States we treat as the detector claiming absence for metric purposes.
ABSENT_PREDICATE_STATES = {"ABSENT_CONFIRMED"}


def load_benchmark(path: Path) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))
    return examples


def _mode_from_name(name: str) -> CompilerMode | None:
    try:
        return CompilerMode[name]
    except KeyError:
        return None


def evaluate_example(example: dict[str, Any]) -> dict[str, Any]:
    """Run the missing-organ detector and compare predictions to labels."""
    text = example["text"]
    mode_name = example.get("mode", "default")
    labels = example.get("labels", {})
    description = example.get("description", "")

    # For default mode, exercise the full pipeline so fragment behavior is
    # realistic. For completeness modes, construct a minimal packet so the
    # benchmark isolates the missing-organ detector from frame-resolution
    # failures that are outside this component's scope.
    if mode_name == "default":
        packet = compile_semantic_packet(text)
    else:
        packet = SemanticPacket(raw_input=text)
        packet.mode = _mode_from_name(mode_name)
        # Derive source frames heuristically from the benchmark text so the
        # detector can infer the system scale.
        if "human" in text.lower() or "body" in text.lower():
            packet.source_frames = ["biology"]
        elif "computer" in text.lower() or "cpu" in text.lower():
            packet.source_frames = ["computation"]
        elif "society" in text.lower() or "government" in text.lower():
            packet.source_frames = ["society"]
        elif "llm" in text.lower() or "transformer" in text.lower() or "model" in text.lower():
            packet.source_frames = ["llm"]
        elif "cell" in text.lower() or "nucleus" in text.lower():
            packet.source_frames = ["cellular"]
        elif "cosmos" in text.lower() or "holographic" in text.lower():
            packet.source_frames = ["cosmological"]
        packet.structural_skeleton = {"actors": [], "flows": []}
        packet.missing_organs = infer_missing_functions(packet)

    findings = {f["department"]: f for f in packet.missing_organs}

    per_department: list[dict[str, Any]] = []
    for dept, true_state in labels.items():
        finding = findings.get(dept, {})
        pred_state = finding.get("state", "UNOBSERVED")
        pred_status = finding.get("status", "NOT_ASSESSED")
        # Treat "MISSING" status as equivalent to ABSENT_CONFIRMED.
        pred_absent = pred_state in ABSENT_PREDICATE_STATES or pred_status == "MISSING"
        true_absent = true_state == "ABSENT_CONFIRMED"

        per_department.append({
            "department": dept,
            "true_state": true_state,
            "predicted_state": pred_state,
            "predicted_status": pred_status,
            "true_absent": true_absent,
            "predicted_absent": pred_absent,
            "match": pred_absent == true_absent,
        })

    return {
        "text": text,
        "description": description,
        "mode": mode_name,
        "is_fragment": mode_name == "default",
        "per_department": per_department,
    }


def compute_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute precision, recall, and fragment false-positive rate."""
    tp = 0
    fp = 0
    fn = 0

    fragment_examples = [r for r in results if r["is_fragment"]]
    fragment_fp = 0
    fragment_absent_predictions = 0

    for r in results:
        for d in r["per_department"]:
            if d["true_absent"] and d["predicted_absent"]:
                tp += 1
            elif not d["true_absent"] and d["predicted_absent"]:
                fp += 1
            elif d["true_absent"] and not d["predicted_absent"]:
                fn += 1

    for r in fragment_examples:
        for d in r["per_department"]:
            fragment_absent_predictions += 1
            if d["predicted_absent"] and not d["true_absent"]:
                fragment_fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr_fragments = fragment_fp / fragment_absent_predictions if fragment_absent_predictions > 0 else 0.0

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "fragment_predictions": fragment_absent_predictions,
        "fragment_false_positives": fragment_fp,
        "absent_confirmed_precision": precision,
        "absent_confirmed_recall": recall,
        "fragment_false_positive_rate": fpr_fragments,
    }


def main() -> None:
    benchmark = load_benchmark(BENCHMARK_PATH)
    results: list[dict[str, Any]] = []

    for example in benchmark:
        results.append(evaluate_example(example))

    metrics = compute_metrics(results)

    print("=" * 60)
    print("Missing-Organ Detector Labeled Benchmark Report")
    print("=" * 60)
    print(f"Examples evaluated: {len(benchmark)}")
    print(f"True positives (ABSENT_CONFIRMED correct): {metrics['true_positives']}")
    print(f"False positives (ABSENT_CONFIRMED wrong):  {metrics['false_positives']}")
    print(f"False negatives (missed ABSENT_CONFIRMED): {metrics['false_negatives']}")
    print(f"ABSENT_CONFIRMED precision:                {metrics['absent_confirmed_precision']:.3f}")
    print(f"ABSENT_CONFIRMED recall:                   {metrics['absent_confirmed_recall']:.3f}")
    print(f"Fragment false-positive rate:              {metrics['fragment_false_positive_rate']:.3f}")
    print("=" * 60)

    # Acceptance gates from Kestrel V2.1.2 ruling.
    gates = {
        "precision_ge_0_90": metrics["absent_confirmed_precision"] >= 0.90,
        "recall_ge_0_80": metrics["absent_confirmed_recall"] >= 0.80,
        "fragment_fpr_le_0_10": metrics["fragment_false_positive_rate"] <= 0.10,
    }
    print("Acceptance gates:")
    for name, passed in gates.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    print("=" * 60)

    # Per-example failures for inspection.
    failures: list[dict[str, Any]] = []
    for r in results:
        for d in r["per_department"]:
            if d["true_absent"] != d["predicted_absent"]:
                failures.append({
                    "description": r["description"],
                    "department": d["department"],
                    "true": d["true_state"],
                    "predicted": d["predicted_state"],
                    "status": d["predicted_status"],
                })

    if failures:
        print("\nMisclassified department examples (first 20):")
        for f in failures[:20]:
            print(f"  {f['description']} | {f['department']} | true={f['true']} pred={f['predicted']} status={f['status']}")

    # Write machine-readable report.
    report_path = Path(__file__).parent.parent / "benchmarks" / "missing_organ_evaluation_report.json"
    report = {
        "metrics": metrics,
        "gates": gates,
        "failures": failures,
        "results": results,
    }
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report written to: {report_path}")


if __name__ == "__main__":
    main()
