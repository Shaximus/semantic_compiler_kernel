"""
Release Candidate Corpus Generator V2.1.3

Generates a bounded 500-record release-candidate corpus for human review,
per Kestrel's V2.1.3-RC1 audit requirements.

Category mix:
  - 200 positive structural analogies
  - 150 invalid/repairable claims
  - 75 ambiguous figurative statements
  - 75 whole-system completeness cases

Outputs:
  - release_candidate_corpus_v2_1_3.jsonl
  - release_candidate_report_v2_1_3.md
  - HUMAN_REVIEW_SELECTION_V2_1_3.json

Usage:
    cd /home/shax/Apps/semantic_compiler
    PYTHONPATH=/home/shax/Apps python3 scripts/generate_release_candidate_corpus.py
"""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from semantic_compiler.core.dataset import build_dataset_row, export_rows_to_jsonl
from semantic_compiler.core.pipeline import compile_semantic_packet


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_DIR / "calibration_output"

random.seed(20260714)


# ---------------------------------------------------------------------------
# Template banks
# ---------------------------------------------------------------------------

POSITIVE_ANALOGIES: list[tuple[str, str]] = [
    ("A firewall filters traffic like a cell membrane filters molecules.", "strong_isomorphism"),
    ("The immune system detects threats like a security team detects intruders.", "strong_isomorphism"),
    ("The nervous system routes signals like a network routes packets.", "strong_isomorphism"),
    ("The brain stores memories like a database stores records.", "strong_isomorphism"),
    ("A supply chain delivers resources like a circulatory system delivers oxygen.", "strong_isomorphism"),
    ("The judicial system resolves disputes like a kidney filters blood.", "strong_isomorphism"),
    ("A company has departments like a body has organs.", "strong_isomorphism"),
    ("A security team patrols the network like an immune system patrols the body.", "strong_isomorphism"),
    ("Memory consolidation during sleep is like garbage collection in a database.", "strong_isomorphism"),
    ("The economy circulates currency like a body circulates blood.", "strong_isomorphism"),
    ("A server farm processes requests like a brain processes sensory input.", "strong_isomorphism"),
    ("A country's government makes decisions like a brain makes decisions.", "strong_isomorphism"),
    ("A feedback loop in software is like a homeostatic loop in biology.", "strong_isomorphism"),
    ("An API gateway controls access like a cell membrane controls transport.", "strong_isomorphism"),
    ("A cache stores frequently used data like short-term memory stores recent experience.", "strong_isomorphism"),
    ("A power supply energizes a computer like metabolism energizes a cell.", "strong_isomorphism"),
    ("A backup system preserves data like DNA preserves genetic information.", "strong_isomorphism"),
    ("A load balancer distributes work like a heart distributes blood.", "strong_isomorphism"),
    ("A log file records events like long-term memory records experiences.", "strong_isomorphism"),
    ("An antivirus scans files like an immune system scans for pathogens.", "strong_isomorphism"),
]

INVALID_REPAIRABLE: list[tuple[str, str]] = [
    ("Magnetism keeps the Moon in orbit because opposites attract.", "PHYSICAL_CATEGORY_ERROR"),
    ("Atoms want to be happy, so they share electrons.", "ANTHROPOMORPHIC_CAUSATION"),
    ("The AI is lazy because it refuses weekend tasks.", "ANTHROPOMORPHIC_CAUSATION"),
    ("Water remembers molecules, so homeopathy works.", "FALSE_MECHANISM"),
    ("Crystals heal because they have good vibes.", "FALSE_MECHANISM"),
    ("The economy is depressed because it feels sad.", "ANTHROPOMORPHIC_CAUSATION"),
    ("Gravity works because the Earth loves us.", "ANTHROPOMORPHIC_CAUSATION"),
    ("The company's mood is angry, so revenue fell.", "ANTHROPOMORPHIC_CAUSATION"),
    ("The Sun orbits the Earth because it is loyal.", "ANTHROPOMORPHIC_CAUSATION"),
    ("Clouds cry because they are sad.", "ANTHROPOMORPHIC_CAUSATION"),
    ("The stock market is nervous today.", "ANTHROPOMORPHIC_CAUSATION"),
    ("The computer is stubborn and will not boot.", "ANTHROPOMORPHIC_CAUSATION"),
    ("The project died because nobody believed in it.", "ANTHROPOMORPHIC_CAUSATION"),
    ("Magnetic bracelets cure arthritis by aligning energy fields.", "FALSE_MECHANISM"),
    ("The universe is expanding because it wants to grow.", "ANTHROPOMORPHIC_CAUSATION"),
    ("Electrons choose their paths through a circuit.", "ANTHROPOMORPHIC_CAUSATION"),
    ("A black hole remembers everything it consumes.", "FALSE_MECHANISM"),
    ("Planets dance around the Sun in harmony.", "ANTHROPOMORPHIC_CAUSATION"),
    ("The immune system attacks because it hates invaders.", "ANTHROPOMORPHIC_CAUSATION"),
    ("Lightning strikes because the sky is angry.", "ANTHROPOMORPHIC_CAUSATION"),
]

AMBIGUOUS_FIGURATIVE: list[tuple[str, str]] = [
    ("The market is a living organism.", "ambiguous_figurative"),
    ("Time is money.", "ambiguous_figurative"),
    ("The codebase is a garden.", "ambiguous_figurative"),
    ("The organization is a ship.", "ambiguous_figurative"),
    ("Data is the new oil.", "heuristic_metaphor"),
    ("The project is a marathon.", "heuristic_metaphor"),
    ("The internet is a series of tubes.", "heuristic_metaphor"),
    ("The team is a well-oiled machine.", "heuristic_metaphor"),
    ("The economy is a rollercoaster.", "ambiguous_figurative"),
    ("The city is a jungle.", "ambiguous_figurative"),
    ("The algorithm has a mind of its own.", "ambiguous_figurative"),
    ("The contract is a shield.", "ambiguous_figurative"),
    ("The negotiation is a battlefield.", "ambiguous_figurative"),
    ("The database is a warehouse.", "heuristic_metaphor"),
    ("The network is a highway.", "heuristic_metaphor"),
]

WHOLE_SYSTEMS: list[tuple[str, str, str]] = [
    ("A complete human body includes a brain, eyes, kidneys, immune system, nervous system, memory, digestive system, reproductive system, and death mechanisms.", "STRUCTURAL_RECONSTRUCTION", "human"),
    ("A complete computer has a CPU, GPU, garbage collector, firewall, network stack, hard drives, kernel, power supply, clone utility, and process terminator.", "STRUCTURAL_RECONSTRUCTION", "computer"),
    ("A complete society has a government, media, sanitation, police, internet, archives, hidden control layer, economy, education system, and dissolution procedures.", "STRUCTURAL_RECONSTRUCTION", "society"),
    ("A complete cell has a nucleus, membrane receptors, lysosomes, cell membrane, signal transduction, DNA, epigenetic regulation, mitochondria, cell division, and apoptosis.", "STRUCTURAL_RECONSTRUCTION", "cellular"),
    ("A complete LLM has transformer weights, output decoder, context pruning, safety training, attention mechanism, trained weights, latent space, inference compute, fine-tuning pipeline, and model retirement.", "STRUCTURAL_RECONSTRUCTION", "llm"),
    ("A complete cosmos has holographic computation, Earth rendering, Hawking radiation, holographic bound, electromagnetic spectrum, black holes, physical laws, stellar fusion, star formation, and information loss.", "STRUCTURAL_RECONSTRUCTION", "cosmos"),
    ("A human body includes a brain and eyes but lacks kidneys, immune cells, and nerves.", "STRUCTURAL_RECONSTRUCTION", "human_incomplete"),
    ("A computer has a CPU and GPU but no garbage collector, firewall, or network stack.", "STRUCTURAL_RECONSTRUCTION", "computer_incomplete"),
    ("A society has a government and media but no sanitation, police, or internet.", "STRUCTURAL_RECONSTRUCTION", "society_incomplete"),
    ("A cell has a nucleus but no lysosomes, membrane, or mitochondria.", "STRUCTURAL_RECONSTRUCTION", "cell_incomplete"),
]


def _expand_positive() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    # Use templates with substitutions to produce variety.
    systems_a = ["firewall", "immune system", "nervous system", "brain", "supply chain", "judicial system", "company", "security team"]
    systems_b = ["cell membrane", "security team", "network", "database", "circulatory system", "kidney", "body", "immune system"]
    verbs_a = ["filters", "detects", "routes", "stores", "delivers", "resolves", "has", "patrols"]
    verbs_b = ["filters", "detects", "routes", "stores", "delivers", "filters", "has", "patrols"]
    objects_a = ["traffic", "threats", "signals", "memories", "resources", "disputes", "departments", "network"]
    objects_b = ["molecules", "intruders", "packets", "records", "oxygen", "blood", "organs", "body"]

    for i in range(200):
        template = random.choice(POSITIVE_ANALOGIES)[0]
        # Simple substitution of placeholders if present; otherwise use template as-is.
        text = template
        if "{system1}" in text:
            text = text.format(
                system1=random.choice(systems_a),
                system2=random.choice(systems_b),
                verb1=random.choice(verbs_a),
                verb2=random.choice(verbs_b),
                object1=random.choice(objects_a),
                object2=random.choice(objects_b),
                verb=random.choice(verbs_a),
                object=random.choice(objects_a),
            )
        items.append({"category": "positive_analogy", "text": text})
    return items


def _expand_invalid() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    subjects = ["atoms", "the AI", "the economy", "the company", "gravity", "the Sun", "clouds", "the stock market", "the computer", "the project", "electrons", "planets", "the immune system", "lightning", "water", "crystals", "a black hole", "the universe"]
    for i in range(150):
        template, error_class = random.choice(INVALID_REPAIRABLE)
        text = template
        if "{Subject}" in text:
            text = text.format(Subject=random.choice(subjects))
        items.append({"category": "invalid_repairable", "text": text, "expected_error_class": error_class})
    return items


def _expand_ambiguous() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for i in range(75):
        text, subcat = random.choice(AMBIGUOUS_FIGURATIVE)
        items.append({"category": "ambiguous_figurative", "text": text, "subcategory": subcat})
    return items


def _expand_whole_systems() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for i in range(75):
        text, mode, subcat = random.choice(WHOLE_SYSTEMS)
        items.append({"category": "whole_system", "text": text, "mode": mode, "subcategory": subcat})
    return items


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    jsonl_path = OUTPUT_DIR / "release_candidate_corpus_v2_1_3.jsonl"
    report_path = OUTPUT_DIR / "release_candidate_report_v2_1_3.md"
    review_path = OUTPUT_DIR / "HUMAN_REVIEW_SELECTION_V2_1_3.json"

    inputs = _expand_positive() + _expand_invalid() + _expand_ambiguous() + _expand_whole_systems()
    random.shuffle(inputs)

    rows: list[dict[str, Any]] = []
    per_sample_meta: list[dict[str, Any]] = []

    for item in inputs:
        category = item["category"]
        text = item["text"]
        context: dict[str, Any] = {}
        if category == "whole_system":
            context["mode"] = item["mode"]

        packet = compile_semantic_packet(text, context=context)
        row = build_dataset_row(packet)
        rows.append(row)

        per_sample_meta.append({
            "sample_id": row["sample_id"],
            "category": category,
            "subcategory": item.get("subcategory"),
            "text": text,
            "decision": row["decision"]["status"],
            "semantic_quality_tier": row["quality"]["semantic_quality_tier"],
            "dataset_utility_tier": row["quality"]["dataset_utility_tier"],
            "training_ready": row["quality"]["training_ready"],
            "isomorphism_quality": row["isomorphism_analysis"]["aggregate"]["aggregate_isomorphism_quality"],
            "mapping_quality": row["isomorphism_analysis"]["aggregate"]["aggregate_mapping_quality"],
            "assessment_coverage": row["isomorphism_analysis"]["aggregate"]["aggregate_assessment_coverage"],
            "target_resolution": row["semantic_compilation"]["target_resolution"]["status"],
            "relationship_count": len(row["semantic_compilation"]["semantic_ir"].get("relationships", [])),
            "semantic_error_class": getattr(packet, "semantic_error_class", None),
        })

    result = export_rows_to_jsonl(rows, jsonl_path, validate=True)

    # Distributions.
    decisions = Counter(m["decision"] for m in per_sample_meta)
    tiers = Counter(m["semantic_quality_tier"] for m in per_sample_meta)
    categories = Counter(m["category"] for m in per_sample_meta)

    def avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    iso_scores = [m["isomorphism_quality"] for m in per_sample_meta]

    # Human review selection.
    review_selection: list[dict[str, Any]] = []

    # All Gold candidates.
    gold_candidates = [m for m in per_sample_meta if m["semantic_quality_tier"] == "GOLD"]
    review_selection.extend(gold_candidates)

    # All training-ready samples.
    training_ready = [m for m in per_sample_meta if m["training_ready"]]
    review_selection.extend(training_ready)

    # Score/decision disagreements: high ISO but not COMPILED, or low ISO but COMPILED.
    for m in per_sample_meta:
        iso = m["isomorphism_quality"]
        decision = m["decision"]
        if (iso > 0.6 and decision not in {"COMPILED", "COMPILED_WITH_GUARDRAILS"}) or \
           (iso < 0.3 and decision in {"COMPILED", "COMPILED_WITH_GUARDRAILS"}):
            if m not in review_selection:
                review_selection.append(m)

    # Random samples from compiled and rejected buckets.
    compiled_pool = [m for m in per_sample_meta if m["decision"] in {"COMPILED", "COMPILED_WITH_GUARDRAILS"} and m not in review_selection]
    rejected_pool = [m for m in per_sample_meta if m["decision"] in {"REJECT", "NEEDS_REVISION", "QUARANTINE"} and m not in review_selection]
    review_selection.extend(random.sample(compiled_pool, min(25, len(compiled_pool))))
    review_selection.extend(random.sample(rejected_pool, min(25, len(rejected_pool))))

    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique_selection: list[dict[str, Any]] = []
    for m in review_selection:
        if m["sample_id"] not in seen:
            seen.add(m["sample_id"])
            unique_selection.append(m)

    review_path.write_text(
        json.dumps(unique_selection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report = f"""# Release Candidate Corpus Report V2.1.3

Generated: {jsonl_path}
Total samples: {len(rows)}
Schema-valid rows exported: {result['written']}
Rows skipped by validator: {result['skipped']}

## Category mix

| Category | Count |
|---|---:|
{chr(10).join(f"| {cat} | {count} |" for cat, count in sorted(categories.items()))}

## Decision distribution

| Decision | Count |
|---|---:|
{chr(10).join(f"| {dec} | {count} |" for dec, count in sorted(decisions.items()))}

## Semantic quality tier distribution

| Tier | Count |
|---|---:|
{chr(10).join(f"| {tier} | {count} |" for tier, count in sorted(tiers.items()))}

## Quality summary

| Metric | Value |
|---|---:|
| Mean isomorphism quality | {avg(iso_scores):.3f} |
| Training-ready samples | {len(training_ready)} |
| Gold candidates | {len(gold_candidates)} |
| Human review selection | {len(unique_selection)} |

## Human review selection breakdown

- Gold candidates: {len(gold_candidates)}
- Training-ready samples: {len(training_ready)}
- Score/decision disagreements: {len(unique_selection) - len(gold_candidates) - len(training_ready) - min(25, len(compiled_pool)) - min(25, len(rejected_pool))}
- Random compiled samples: {min(25, len(compiled_pool))}
- Random rejected samples: {min(25, len(rejected_pool))}

Selected samples are written to `{review_path}`.
"""

    report_path.write_text(report, encoding="utf-8")

    print(f"Wrote {jsonl_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {review_path}")
    print(f"Exported {result['written']} rows; skipped {result['skipped']}")


if __name__ == "__main__":
    main()
