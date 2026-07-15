"""
Quarantine the three residual disputed cases from Kestrel's V2.1.3 final review.

Applies to:
    - calibration_corpus_v2_1_3.jsonl
    - release_candidate_corpus_v2_1_3.jsonl

Fields set on quarantined rows:
    - decision.status = "NEEDS_REVISION"
    - quality.training_ready = false
    - quality.dataset_utility_tier = "DIAGNOSTIC"
    - quality.dataset_tier = "DIAGNOSTIC"
    - review.consensus.status = "QUARANTINED_PENDING_ADJUDICATION"
    - review.consensus.notes = explanatory note
    - status = "QUARANTINED"

Outputs:
    - Updated JSONL corpora (in-place)
    - QUARANTINE_REPORT_V2_1_3.md
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from semantic_compiler.core.dataset import validate_dataset_row


OUTPUT_DIR = Path("/home/shax/Apps/semantic_compiler/calibration_output")
DISPUTED_PATH = OUTPUT_DIR / "FIRST_PASS_DISPUTED_CASES_V2_1_3.json"


def load_disputed_ids(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for item in data:
        ids.add(item["sample_id"])
        ids.update(item.get("duplicate_sample_ids", []))
    return ids


def quarantine_row(row: dict[str, Any]) -> dict[str, Any]:
    row["decision"]["status"] = "NEEDS_REVISION"
    row["status"] = "QUARANTINED"
    row["quality"]["training_ready"] = False
    row["quality"]["dataset_utility_tier"] = "DIAGNOSTIC"
    row["quality"]["dataset_tier"] = "DIAGNOSTIC"
    row["quality"]["tier_reasons"].append("Quarantined pending adjudication")

    consensus = row["review"]["consensus"]
    consensus["status"] = "QUARANTINED_PENDING_ADJUDICATION"
    consensus["notes"] = (
        "Quarantined per Kestrel V2.1.3 final review. "
        "Residual disputed case excluded from SFT positives, DPO chosen records, "
        "Gold candidates, and release acceptance statistics."
    )
    return row


def process_corpus(path: Path, disputed_ids: set[str]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    invalid: list[tuple[str, list[str]]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("sample_id") in disputed_ids:
                row = quarantine_row(row)
                quarantined.append(
                    {
                        "sample_id": row["sample_id"],
                        "text": row["input"]["raw_input"][:200],
                        "category": row.get("metadata", {}).get("category", "unknown"),
                    }
                )
            rows.append(row)

    # Validate after mutation.
    for row in rows:
        validation = validate_dataset_row(row)
        if not validation["valid"]:
            invalid.append((row.get("sample_id", "?"), validation["errors"]))

    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows),
        encoding="utf-8",
    )

    return {
        "path": str(path),
        "total_rows": len(rows),
        "quarantined_count": len(quarantined),
        "quarantined": quarantined,
        "invalid_count": len(invalid),
        "invalid": invalid,
    }


def main() -> None:
    disputed_ids = load_disputed_ids(DISPUTED_PATH)

    results: list[dict[str, Any]] = []
    for name in ("calibration_corpus_v2_1_3.jsonl", "release_candidate_corpus_v2_1_3.jsonl"):
        corpus_path = OUTPUT_DIR / name
        result = process_corpus(corpus_path, disputed_ids)
        results.append(result)

    report_lines = [
        "# Quarantine Report V2.1.3",
        "",
        f"Disputed case IDs (including duplicates): {len(disputed_ids)}",
        "",
        "## Per-corpus quarantine summary",
        "",
        "| Corpus | Total rows | Quarantined | Invalid after quarantine |",
        "|---|---|---:|---:|",
    ]
    for r in results:
        report_lines.append(
            f"| {Path(r['path']).name} | {r['total_rows']} | {r['quarantined_count']} | {r['invalid_count']} |"
        )

    report_lines.extend(["", "## Quarantined rows", ""])
    for r in results:
        report_lines.append(f"### {Path(r['path']).name}")
        if not r["quarantined"]:
            report_lines.append("- none")
        for q in r["quarantined"]:
            report_lines.append(f"- `{q['sample_id']}` ({q['category']}): {q['text']}")
        report_lines.append("")

    if any(r["invalid"] for r in results):
        report_lines.extend(["", "## Validation errors", ""])
        for r in results:
            for sample_id, errors in r["invalid"]:
                report_lines.append(f"- `{sample_id}`: {'; '.join(errors[:3])}")

    report_path = OUTPUT_DIR / "QUARANTINE_REPORT_V2_1_3.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Quarantined {sum(r['quarantined_count'] for r in results)} rows across {len(results)} corpora.")
    print(f"Report: {report_path}")
    if any(r["invalid_count"] for r in results):
        print("WARNING: schema validation errors present after quarantine.")


if __name__ == "__main__":
    main()
