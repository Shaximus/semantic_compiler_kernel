"""Compile NUMEROLOGY_ASTROLOGY_AGENT_GUIDE.md into Logos Semantic Training Sample V3.5.0 rows."""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))

from semantic_compiler.core.dataset import validate_dataset_row
from semantic_compiler.core.pipeline import build_dataset_row, compile_semantic_packet

SOURCE_FILE = Path("/storage/emulated/0/Download/NUMEROLOGY_ASTROLOGY_AGENT_GUIDE.md")
OUTPUT_JSONL = REPO_DIR / "calibration_output" / "numerology_astrology_corpus_v3_5_0.jsonl"
OUTPUT_DOWNLOAD = Path("/storage/emulated/0/Download/NUMEROLOGY_ASTROLOGY_V3_5_0_CORPUS.jsonl")


def extract_semantic_blocks(raw_text: str) -> list[dict]:
    """Parse markdown document into cohesive semantic units."""
    # Split on markdown headers (# or ## or ###)
    chunks = re.split(r"\n(?=#{1,3} )", raw_text)
    blocks = []

    current_part = "GENERAL"
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        header = lines[0].strip()
        body = "\n".join(lines[1:]).strip()

        if header.startswith("# PART 1: NUMEROLOGY"):
            current_part = "NUMEROLOGY"
            continue
        elif header.startswith("# PART 2: ASTROLOGY"):
            current_part = "ASTROLOGY"
            continue
        elif header.startswith("# PART 3: APPENDICES"):
            current_part = "APPENDICES"
            continue

        if "Version 1.0" in header or "Quick-reference" in header or header == "# NUMEROLOGY & ASTROLOGY — AGENT DECODE REFERENCE":
            continue

        # If it's a super-header with negligible body, skip
        if len(chunk) < 60 and not body:
            continue

        # Determine domain
        if current_part == "NUMEROLOGY":
            domain = "numerology"
        elif current_part == "ASTROLOGY":
            domain = "astrology"
        else:
            domain = "numerology" if "number" in header.lower() or "month" in header.lower() else "astrology"

        # Clean text for compiler ingestion
        clean_text = f"{header}\n{body}" if body else header

        blocks.append({
            "header": header,
            "part": current_part,
            "domain": domain,
            "text": clean_text,
            "char_count": len(clean_text),
        })

    return blocks


def main():
    if not SOURCE_FILE.exists():
        print(f"Error: Source file {SOURCE_FILE} does not exist.")
        sys.exit(1)

    print(f"Reading source guide: {SOURCE_FILE}")
    raw_content = SOURCE_FILE.read_text(encoding="utf-8")
    raw_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

    blocks = extract_semantic_blocks(raw_content)
    print(f"Extracted {len(blocks)} semantic blocks from guide.")

    compiled_rows = []
    start_time = time.time()
    validation_failures = 0

    for idx, block in enumerate(blocks, 1):
        context = {
            "source": "NUMEROLOGY_ASTROLOGY_AGENT_GUIDE.md",
            "section_header": block["header"],
            "part": block["part"],
            "target_domain": block["domain"],
        }

        # Compile through V3.5.0 pipeline
        packet = compile_semantic_packet(block["text"], context=context)
        row = build_dataset_row(packet)

        # Enforce V3.5.0 schema properties & provenance
        row["schema_version"] = "3.5.0"
        row["provenance"]["source_type"] = "document"
        row["provenance"]["origin"] = "Hannah (Claude) for Reflexion Software Agent Team"
        row["provenance"]["source_path"] = str(SOURCE_FILE)
        row["provenance"]["raw_hash"] = raw_hash
        row["provenance"]["trust_level"] = "DIRECT"
        row["provenance"]["mutation_state"] = "ORIGINAL"
        row["provenance"]["license_or_consent"] = "OWNED"

        # Validate against Logos Semantic Training Sample V3.5.0 schema
        validation = validate_dataset_row(row)
        if not validation["valid"]:
            print(f"[{idx}/{len(blocks)}] Validation error on '{block['header']}': {validation['errors']}")
            validation_failures += 1
        else:
            compiled_rows.append(row)

        if idx % 10 == 0 or idx == len(blocks):
            print(f"Processed {idx}/{len(blocks)} blocks (Valid: {len(compiled_rows)}, Failed: {validation_failures})")

    elapsed = time.time() - start_time
    print(f"\nCompilation finished in {elapsed:.2f}s. Valid rows: {len(compiled_rows)}/{len(blocks)}")

    if validation_failures > 0:
        print(f"WARNING: {validation_failures} rows failed schema validation.")
        sys.exit(1)

    # Write output JSONL
    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSONL.open("w", encoding="utf-8") as f:
        for r in compiled_rows:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(compiled_rows)} rows to {OUTPUT_JSONL}")

    # Mirror to Downloads for easy access
    try:
        with OUTPUT_DOWNLOAD.open("w", encoding="utf-8") as f:
            for r in compiled_rows:
                f.write(json.dumps(r) + "\n")
        print(f"Mirrored {len(compiled_rows)} rows to {OUTPUT_DOWNLOAD}")
    except Exception as e:
        print(f"Notice: Could not mirror to Downloads: {e}")

    print("Success: Numerology and Astrology guide fully mapped into Semantic Compiler V3.5.0!")


if __name__ == "__main__":
    main()
