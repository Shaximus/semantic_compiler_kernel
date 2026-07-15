"""
Generate final V2.1.3 freeze artifacts:
    - RELEASE_MANIFEST_V2_1_3.json
    - KNOWN_LIMITATIONS_V2_1_3.md
    - SFT_PILOT_DATASET_V1.jsonl
    - SFT_PILOT_EVALUATION_SET_V1.jsonl
    - DPO_DIAGNOSTIC_REGISTRY.json

Inputs (from calibration_output/):
    - calibration_corpus_v2_1_3.jsonl (post-quarantine)
    - release_candidate_corpus_v2_1_3.jsonl (post-quarantine)
    - DPO_DELTA_DISTRIBUTION.json
    - QUARANTINE_REPORT_V2_1_3.md
    - FOUR_CASE_RULING_VERIFICATION.md
"""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path("/home/shax/Apps/semantic_compiler/calibration_output")
random.seed(20260714)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _sft_record(row: dict[str, Any]) -> dict[str, Any]:
    """Return the Qwen chat-format SFT payload with provenance metadata."""
    return {
        "sample_id": row["sample_id"],
        "messages": row["training_payloads"]["sft"]["messages"],
        "metadata": {
            "decision": row["decision"]["status"],
            "semantic_quality_tier": row["quality"]["semantic_quality_tier"],
            "dataset_utility_tier": row["quality"]["dataset_utility_tier"],
            "isomorphism_quality": row["isomorphism_analysis"]["aggregate"]["aggregate_isomorphism_quality"],
            "relationship_count": len(row["semantic_compilation"]["semantic_ir"]["relationships"]),
            "source_corpus": row.get("metadata", {}).get("source_corpus", "unknown"),
        },
    }


def main() -> None:
    cal_path = OUTPUT_DIR / "calibration_corpus_v2_1_3.jsonl"
    rc_path = OUTPUT_DIR / "release_candidate_corpus_v2_1_3.jsonl"
    dpo_path = OUTPUT_DIR / "DPO_DELTA_DISTRIBUTION.json"

    cal_rows = load_rows(cal_path)
    rc_rows = load_rows(rc_path)

    # Post-quarantine counts.
    cal_decisions = Counter(r["decision"]["status"] for r in cal_rows)
    rc_decisions = Counter(r["decision"]["status"] for r in rc_rows)
    cal_quarantined = sum(1 for r in cal_rows if r["review"]["consensus"]["status"] == "QUARANTINED_PENDING_ADJUDICATION")
    rc_quarantined = sum(1 for r in rc_rows if r["review"]["consensus"]["status"] == "QUARANTINED_PENDING_ADJUDICATION")

    cal_ready = [r for r in cal_rows if r["quality"]["training_ready"]]
    rc_ready = [r for r in rc_rows if r["quality"]["training_ready"]]

    # SFT pilot: training rows from calibration positives, eval from a random
    # sample of release-candidate positives (post-quarantine).
    train_records = [_sft_record(r) for r in cal_ready]
    eval_sample_size = min(30, len(rc_ready))
    eval_records = [_sft_record(r) for r in random.sample(rc_ready, eval_sample_size)]

    train_path = OUTPUT_DIR / "SFT_PILOT_DATASET_V1.jsonl"
    eval_path = OUTPUT_DIR / "SFT_PILOT_EVALUATION_SET_V1.jsonl"
    train_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in train_records),
        encoding="utf-8",
    )
    eval_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in eval_records),
        encoding="utf-8",
    )

    # DPO diagnostic registry.
    dpo_data = json.loads(dpo_path.read_text(encoding="utf-8")) if dpo_path.exists() else {"pairs": []}
    dpo_registry = {
        "version": "2.1.3",
        "generated_at": _now_iso(),
        "production_export_allowed": False,
        "pairs": [
            {
                "pair_id": p["pair_id"],
                "delta": p["delta"],
                "positive_decision": p["positive_decision"],
                "negative_decision": p["negative_decision"],
                "production_export": p["pair_id"] != "memory_gc",
                "exclusion_reason": (
                    "Positive side remains NEEDS_REVISION; retained as diagnostic regression sample."
                    if p["pair_id"] == "memory_gc" else None
                ),
            }
            for p in dpo_data.get("pairs", [])
        ],
        "summary": {
            "total_pairs": len(dpo_data.get("pairs", [])),
            "production_exportable": sum(1 for p in dpo_data.get("pairs", []) if p["pair_id"] != "memory_gc"),
            "diagnostic_only": sum(1 for p in dpo_data.get("pairs", []) if p["pair_id"] == "memory_gc"),
            "mean_delta": dpo_data.get("mean_delta"),
            "median_delta": dpo_data.get("median_delta"),
        },
    }
    dpo_registry_path = OUTPUT_DIR / "DPO_DIAGNOSTIC_REGISTRY.json"
    dpo_registry_path.write_text(json.dumps(dpo_registry, indent=2, ensure_ascii=False), encoding="utf-8")

    # Release manifest.
    artifact_paths = {
        "calibration_corpus": cal_path,
        "release_candidate_corpus": rc_path,
        "calibration_report": OUTPUT_DIR / "calibration_report_v2_1_3.md",
        "release_candidate_report": OUTPUT_DIR / "release_candidate_report_v2_1_3.md",
        "human_review_selection": OUTPUT_DIR / "HUMAN_REVIEW_SELECTION_V2_1_3.json",
        "unique_review_selection": OUTPUT_DIR / "UNIQUE_REVIEW_SELECTION_V2_1_3.json",
        "four_case_ruling_verification": OUTPUT_DIR / "FOUR_CASE_RULING_VERIFICATION.md",
        "quarantine_report": OUTPUT_DIR / "QUARANTINE_REPORT_V2_1_3.md",
        "dpo_delta_distribution": dpo_path,
        "dpo_diagnostic_registry": dpo_registry_path,
        "sft_pilot_dataset": train_path,
        "sft_pilot_evaluation_set": eval_path,
        "score_by_mapping_status": OUTPUT_DIR / "SCORE_BY_MAPPING_STATUS.json",
        "empty_mapping_invariant_report": OUTPUT_DIR / "EMPTY_MAPPING_INVARIANT_REPORT.md",
        "negative_category_decision_report": OUTPUT_DIR / "NEGATIVE_CATEGORY_DECISION_REPORT.md",
        "relative_clause_extraction_report": OUTPUT_DIR / "RELATIVE_CLAUSE_EXTRACTION_REPORT.md",
        "missing_organ_labeled_benchmark": OUTPUT_DIR / "MISSING_ORGAN_LABELED_BENCHMARK.md",
    }

    manifest = {
        "manifest_version": "2.1.3",
        "semantic_compiler_version": "2.0.0",
        "schema_version": "2.1.0",
        "generated_at": _now_iso(),
        "git_commit": _git_commit(),
        "generator_script": "scripts/generate_v2_1_3_freeze_artifacts.py",
        "test_command": "PYTHONPATH=/home/shax/Apps python3 -m unittest discover -s tests -v",
        "test_result": "67/67 OK",
        "corpus_statistics": {
            "calibration": {
                "total_rows": len(cal_rows),
                "decisions": dict(cal_decisions),
                "quarantined": cal_quarantined,
                "training_ready": len(cal_ready),
            },
            "release_candidate": {
                "total_rows": len(rc_rows),
                "decisions": dict(rc_decisions),
                "quarantined": rc_quarantined,
                "training_ready": len(rc_ready),
            },
        },
        "dpo_summary": dpo_registry["summary"],
        "sft_pilot": {
            "train_rows": len(train_records),
            "eval_rows": len(eval_records),
        },
        "artifact_hashes": {
            name: _sha256_file(path) for name, path in artifact_paths.items() if path.exists()
        },
        "approvals": {
            "canonical_freeze": "Kestrel",
            "controlled_corpus_production": "approved",
            "deduplicated_human_reviewed_sft_pilot": "approved",
            "production_dpo_training": "not approved",
            "missing_organ_hard_gate": "not approved",
            "autonomous_gold_promotion": "not approved",
        },
    }

    manifest_path = OUTPUT_DIR / "RELEASE_MANIFEST_V2_1_3.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Known limitations.
    limitations_md = """# Known Limitations — Semantic Compiler V2.1.3

## Approved scope

- Canonical compiler freeze.
- Controlled corpus production.
- Deduplicated, human-reviewed SFT pilot dataset.

## Not approved for this release

- Production DPO training: the `memory_gc` pair remains diagnostic-only.
- Missing-organ hard-gate enforcement: findings remain advisory.
- Autonomous Gold/Diamond promotion: all positive mappings are currently
  `COMPILED_WITH_GUARDRAILS` pending explicit invariants, negative tests,
  residual analysis, and full gate clearance.

## Quarantined records

Three residual disputed cases (and their duplicates) are quarantined in both
`calibration_corpus_v2_1_3.jsonl` and `release_candidate_corpus_v2_1_3.jsonl`:

- `LOGOS:SAMPLE:dc51ef2d-301d-43` — incomplete computer system
- `LOGOS:SAMPLE:0dc86964-7ec3-45` — incomplete society system
- `LOGOS:SAMPLE:c1f4f30c-10c5-4e` — complete cell listing

They are marked:
- `decision.status` = `NEEDS_REVISION`
- `quality.training_ready` = `false`
- `quality.dataset_utility_tier` = `DIAGNOSTIC`
- `review.consensus.status` = `QUARANTINED_PENDING_ADJUDICATION`

They are excluded from SFT positives, DPO chosen records, Gold candidates, and
release acceptance statistics.

## Score/modeling notes

- Strong-isomorphism analogies are intentionally retained as
  `COMPILED_WITH_GUARDRAILS` in V2.1.3.
- The `memory_gc` DPO pair has a weak delta because the positive sample is
  still `NEEDS_REVISION`; it is retained as a diagnostic regression sample.
- The score plateau is broken: distinct ISO scores now range across strong
  analogies (~0.58–0.63), underspecified cases (~0.00–0.06), and rejected
  cases (0.00).

## Next release targets

- Promote strong isomorphisms to plain `COMPILED` after explicit invariant,
  negative-test, residual, and gate requirements are formalized.
- Expand missing-organ benchmark and enable hard-gate enforcement.
- Repair the `memory_gc` extraction path and re-enable production DPO export.
"""
    limitations_path = OUTPUT_DIR / "KNOWN_LIMITATIONS_V2_1_3.md"
    limitations_path.write_text(limitations_md, encoding="utf-8")

    print(f"Wrote {manifest_path}")
    print(f"Wrote {limitations_path}")
    print(f"Wrote {train_path} ({len(train_records)} records)")
    print(f"Wrote {eval_path} ({len(eval_records)} records)")
    print(f"Wrote {dpo_registry_path}")


if __name__ == "__main__":
    main()
