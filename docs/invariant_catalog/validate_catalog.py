#!/usr/bin/env python3
"""
Automated Verification Suite for Invariant Translator Catalog (2026-11-23).
Independently parses and validates all emitted .jsonl and .md files against:
  1. Exact SC-DE-001 top-level & nested schema structure
  2. Exact 324/324 Pokemon pairs & 120/120 non-neutral grounded edges (independently parsed from MD & JSONL)
  3. Exact 225/225 DOMAIN_EXPANSION_EGO pairs & 110/110 non-neutral grounded edges
  4. All 15 functional departments present in every JSONL and MD decode
  5. Strict Section 10 gate discipline (residual_mismatches non-empty when information_lost set,
     substrate_confusion_check == True & positional_claims_permitted == True per SC-PATCH-DU-001,
     BALANCE-ONLY edges in residuals, 0.9 cap on untested gates,
     uncertainty_statement lists all untested predictions)
  6. Zero dangling cross-reference IDs across all JSONL and MD catalog/ledger files
  7. Zero "etc." elisions across all emitted artifacts
  8. All 19 catalog classes & 17-primitive grammar coverage
"""

import glob
import json
import os
import re
import sys

CAT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CAT_DIR, "..", ".."))
COMPILED_DIR = os.path.join(REPO_ROOT, "calibration_output", "compiled_entries")
TEMPLATE_PATH = os.path.join(COMPILED_DIR, "DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl")
MANIFEST_PATH = os.path.join(COMPILED_DIR, "manifest.json")

# Upstream session entry IDs formally tracked in DOMAIN_LEDGER.md Section 3
# awaiting standalone JSONL drops (never silently ignored as accidental typos).
EXTERNAL_UPSTREAM_IDS = {
    "SC-CP-001",
    "SC-IT-POE-SOUL-EATER-001",
    "SC-IT-GOJO-KIT-001",
    # 2026-11-25 drops tracked as markdown patch/source docs (not compiled JSONL):
    "SC-PATCH-DU-001",  # docs/SC-PATCH-DU-001_IDENTITY_GATE_CORRECTION.md
    "SC-THEO-002",      # docs/SC-THEO-002_OMNI_STATE.md (entry patch, awaiting JSONL compile)
    "SC-BRM-001",       # docs/SC-BRM-001_BIOMEDICAL_MICROPLASTIC_DOSSIER.md (feasibility dossier)
}


def substrate_gate_ok(mp):
    """SC-PATCH-DU-001 mapping-object gate fields (old identity_claim_allowed removed)."""
    return (
        mp.get("substrate_confusion_check") is True
        and mp.get("positional_claims_permitted") is True
        and "identity_claim_allowed" not in mp
    )

REQUIRED_DEPTS = {
    "SUBCONSCIOUS", "INNER_MONOLOGUE", "SPEECH_OUTPUT", "STORAGE", "SECURITY",
    "TELECOMMUNICATIONS", "ENERGY_INTAKE", "DISPLAY", "PROCESSOR", "REPRODUCTION",
    "DELETION", "WASTE_REMOVAL", "APPLICATION", "RENDERING_OVERHEAD", "INFORMATION_DENSITY",
}

REQUIRED_PRIMITIVES = [
    "POOL", "CAPACITY / CAP", "INFLOW / REGEN", "OUTFLOW / DRAIN", "CHANNEL / TYPE",
    "FILTER / MITIGATION", "THRESHOLD", "TRIGGER", "RELEASE", "PROPAGATION",
    "TRADE / RESTRICTION", "IMMUNITY", "CONTROL LOOP", "ESCAPE", "HOST / COUPLING",
    "FAILURE MODE", "COUNTERPLAY",
]

CONFIRMED_PREDS = {
    "PRED-DEE-001", "PRED-DEE-002", "PRED-DEE-003", "PRED-DEE-004",
    "PRED-PKM-001", "PRED-PKM-002", "PRED-PKM-003", "PRED-PKM-004", "PRED-PKM-005",
    "PRED-BATCH-001", "PRED-BATCH-002", "PRED-BATCH-003", "PRED-BATCH-004",
}
UNTESTED_PREDS_BY_ENTRY = {
    "SC-IT-DOMAIN-EXPANSION-EGO-001": ["PRED-DEE-005", "PRED-DEE-006"],
    "SC-IT-POKEMON-001": ["PRED-PKM-006"],
    "SC-IT-BATCH-2026-11-23": ["PRED-DEE-005", "PRED-DEE-006", "PRED-PKM-006"],
}

errors = []
checks_passed = []


def check(cond, msg):
    if cond:
        checks_passed.append(msg)
    else:
        errors.append(msg)


# Load template SC-DE-001
with open(TEMPLATE_PATH, encoding="utf-8") as f:
    template = json.loads(f.readline())

# Build authoritative ground-truth entry ID registry on disk
valid_entry_ids = {template["metadata"]["entry_id"]}
with open(MANIFEST_PATH, encoding="utf-8") as f:
    manifest = json.load(f)
for item in manifest["entries"]:
    valid_entry_ids.add(item["entry_id"])

jsonl_files = sorted(glob.glob(os.path.join(CAT_DIR, "INVARIANT_ENTRY_*.jsonl")))
check(len(jsonl_files) == 3, f"Expected 3 INVARIANT_ENTRY_*.jsonl files, found {len(jsonl_files)}")

loaded_entries = {}
for jp in jsonl_files:
    fname = os.path.basename(jp)
    with open(jp, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    check(len(lines) == 1, f"{fname}: valid single-record JSONL (lines={len(lines)})")
    try:
        obj = json.loads(lines[0])
    except Exception as exc:
        errors.append(f"{fname}: JSON parse error: {exc}")
        continue
    eid = obj["metadata"]["entry_id"]
    loaded_entries[eid] = (fname, obj)
    valid_entry_ids.add(eid)

check(len(valid_entry_ids) == 21, f"Authoritative local compiled entry registry size == 21 (found {len(valid_entry_ids)}: {sorted(valid_entry_ids)})")

# 1. Exact SC-DE-001 Schema Parity & Section 10 Gate Discipline
for eid, (fname, obj) in loaded_entries.items():
    check(set(obj.keys()) == set(template.keys()), f"{fname}: exact top-level key match with SC-DE-001 ({len(obj.keys())} keys)")
    for subk in ["metadata", "analysis", "structural_skeleton", "translations", "gates",
                 "isomorphism_quality", "dataset_value", "isomorphism_analysis",
                 "v2_extensions", "outputs", "training_payloads"]:
        check(set(obj[subk].keys()) == set(template[subk].keys()),
              f"{fname}: exact nested key match for `{subk}`")
    check(set(obj["structural_skeleton"]["metrics"].keys()) == set(template["structural_skeleton"]["metrics"].keys()),
          f"{fname}: exact nested key match for `structural_skeleton.metrics`")

    # Metadata invariants
    meta = obj["metadata"]
    check(meta["compiler_mode"] == "UNIVERSAL_DECOMPRESSION", f"{fname}: compiler_mode == UNIVERSAL_DECOMPRESSION")
    check(meta["framework"] == "Systemic Isomorphic Invariants", f"{fname}: framework matches canonical")
    check(meta["version"] == "3.5.0", f"{fname}: version == 3.5.0")
    check(meta["source"] == "Shax (Curtis Kingsley) — Reflexion Software", f"{fname}: source matches canonical")

    # Cross-references check (zero dangling IDs)
    xrefs = meta["cross_references"]
    dangling = [x for x in xrefs if x not in valid_entry_ids]
    check(len(dangling) == 0, f"{fname}: zero dangling cross_references (checked {len(xrefs)}, dangling={dangling})")

    # 15 functional departments check
    depts = [d["department"] for d in obj["functional_departments"]]
    check(len(depts) == 15 and set(depts) == REQUIRED_DEPTS,
          f"{fname}: exact 15/15 functional departments present")

    # Section 10 Gate Discipline
    gates = obj["gates"]
    for gname, gval in gates.items():
        check(set(gval.keys()) == {"applicable", "passed", "score", "reason", "evidence_ids"},
              f"{fname}: gate `{gname}` exact keys")
        ev_ids = gval["evidence_ids"]
        has_confirmed_pred = any(ev in CONFIRMED_PREDS for ev in ev_ids)
        if gval["score"] == 1.0:
            check(has_confirmed_pred,
                  f"{fname}: gate `{gname}` score=1.0 backed by confirmed prediction evidence_ids={ev_ids}")
        else:
            check(gval["score"] <= 0.9,
                  f"{fname}: gate `{gname}` non-1.0 score <= 0.9 (actual={gval['score']})")

    # Isomorphism mappings: non-empty residual_mismatches when information_lost set; SC-PATCH-DU-001 gate fields
    mappings = obj["isomorphism_analysis"]["mappings"]
    check(len(mappings) >= 1, f"{fname}: has >=1 isomorphism mappings ({len(mappings)})")
    all_residuals_text = []
    for mp in mappings:
        check(substrate_gate_ok(mp),
              f"{fname} / {mp['mapping_id']}: substrate_confusion_check & positional_claims_permitted == True")
        info_lost = mp["scale_transform"]["information_lost"]
        res = mp["residual_mismatches"]
        if info_lost and str(info_lost).strip():
            check(isinstance(res, list) and len(res) > 0,
                  f"{fname} / {mp['mapping_id']}: non-empty residual_mismatches when information_lost is set (count={len(res)})")
        all_residuals_text.extend(res)

    # Check uncertainty_statement lists every untested prediction
    unc = obj["outputs"]["uncertainty_statement"]
    for up in UNTESTED_PREDS_BY_ENTRY[eid]:
        check(up in unc, f"{fname}: uncertainty_statement explicitly lists untested prediction `{up}`")

# 2. Independently verify Pokemon 324/324 matrix & 120/120 grounded edges from DOMAIN_DECODE_POKEMON.md
pkm_md_path = os.path.join(CAT_DIR, "DOMAIN_DECODE_POKEMON.md")
with open(pkm_md_path, encoding="utf-8") as f:
    pkm_md = f.read()

# Parse the 18x18 effectiveness table directly from Markdown
pkm_matrix_rows = re.findall(r"^\|\s*\*\*([A-Za-z]+)\*\*\s*\|((?:\s*[^|]+\|){18})\s*$", pkm_md, re.MULTILINE)
check(len(pkm_matrix_rows) == 18, f"DOMAIN_DECODE_POKEMON.md: parsed 18x18 matrix rows == 18 (found {len(pkm_matrix_rows)})")
pkm_cell_counts = {"2": 0, "½": 0, "0": 0, "1": 0}
total_pkm_cells = 0
for atk, cells_str in pkm_matrix_rows:
    cells = [c.strip().replace("*", "") for c in cells_str.strip().strip("|").split("|")]
    assert len(cells) == 18
    for c in cells:
        total_pkm_cells += 1
        pkm_cell_counts[c] += 1
check(total_pkm_cells == 324, f"DOMAIN_DECODE_POKEMON.md: exact 324/324 attacker x defender pairs parsed")
check(pkm_cell_counts == {"2": 51, "½": 61, "0": 8, "1": 204},
      f"DOMAIN_DECODE_POKEMON.md: exact cell counts 51 SE / 61 NVE / 8 IMM / 204 NEU (got {pkm_cell_counts})")

# Parse grounded edge rows in Section 4 of DOMAIN_DECODE_POKEMON.md
pkm_edge_rows = re.findall(
    r"^\|\s*(\d+)\s*\|\s*`([A-Za-z]+)`\s*\|\s*`([^`]+)`\s*\|\s*`([A-Za-z]+)`\s*\|\s*\*\*`(PHYSICAL|BIOLOGICAL_ECOLOGICAL|SYMBOLIC_MYTHIC|BALANCE-ONLY)`\*\*\s*\|",
    pkm_md, re.MULTILINE
)
check(len(pkm_edge_rows) == 120, f"DOMAIN_DECODE_POKEMON.md: exact 120/120 non-neutral grounded edges parsed (found {len(pkm_edge_rows)})")
pkm_jsonl = loaded_entries["SC-IT-POKEMON-001"][1]
check(len(pkm_jsonl["analysis"]["relationships"]) == 120,
      f"INVARIANT_ENTRY_SC-IT-POKEMON-001.jsonl: exact 120/120 non-neutral relationships")

# Verify EVERY Pokemon BALANCE-ONLY edge appears in residual_mismatches
pkm_bal_edges = [(a, d) for (_, a, _, d, g) in pkm_edge_rows if g == "BALANCE-ONLY"]
pkm_all_res = "\n".join(
    r for mp in pkm_jsonl["isomorphism_analysis"]["mappings"] for r in mp["residual_mismatches"]
)
missing_pkm_bal = [f"{a}->{d}" for (a, d) in pkm_bal_edges if f"{a}->{d}" not in pkm_all_res]
check(len(missing_pkm_bal) == 0,
      f"SC-IT-POKEMON-001: all {len(pkm_bal_edges)} BALANCE-ONLY edges present in residual_mismatches (missing={missing_pkm_bal})")

# Check all 15 departments and 17 primitives appear in DOMAIN_DECODE_POKEMON.md
check(all(d in pkm_md for d in REQUIRED_DEPTS), "DOMAIN_DECODE_POKEMON.md: all 15 departments present")
check(all(f"`{p}`" in pkm_md for p in REQUIRED_PRIMITIVES), "DOMAIN_DECODE_POKEMON.md: all 17 primitives present")

# 3. Independently verify DOMAIN_EXPANSION_EGO 225/225 matrix & 110/110 grounded edges
dee_md_path = os.path.join(CAT_DIR, "DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md")
with open(dee_md_path, encoding="utf-8") as f:
    dee_md = f.read()

dee_matrix_rows = re.findall(r"^\|\s*\*\*[A-Z]+\*\*\s*\(`([^`]+)`\)\s*\|((?:\s*[^|]+\|){15})\s*$", dee_md, re.MULTILINE)
check(len(dee_matrix_rows) == 15, f"DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md: parsed 15x15 matrix rows == 15 (found {len(dee_matrix_rows)})")
dee_non_neutral = 0
dee_total = 0
for src, cells_str in dee_matrix_rows:
    cells = [c.strip() for c in cells_str.strip().strip("|").split("|")]
    assert len(cells) == 15
    for c in cells:
        dee_total += 1
        if c != ".":
            dee_non_neutral += 1
check(dee_total == 225, f"DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md: exact 225/225 ordered pairs parsed")

dee_edge_rows = re.findall(
    r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*\*\*`(PHYSICAL|BIOLOGICAL_ECOLOGICAL|SYMBOLIC_MYTHIC|BALANCE-ONLY)`\*\*\s*\|",
    dee_md, re.MULTILINE
)
check(len(dee_edge_rows) == dee_non_neutral == 110,
      f"DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md: exact 110/110 non-neutral edges match matrix ({len(dee_edge_rows)} vs {dee_non_neutral})")
dee_jsonl = loaded_entries["SC-IT-DOMAIN-EXPANSION-EGO-001"][1]
check(len(dee_jsonl["analysis"]["relationships"]) == 110,
      f"INVARIANT_ENTRY_SC-IT-DOMAIN-EXPANSION-EGO-001.jsonl: exact 110/110 non-neutral relationships")

dee_bal_edges = [(s, t) for (_, s, _, t, g) in dee_edge_rows if g == "BALANCE-ONLY"]
dee_all_res = "\n".join(
    r for mp in dee_jsonl["isomorphism_analysis"]["mappings"] for r in mp["residual_mismatches"]
)
missing_dee_bal = [f"{s}->{t}" for (s, t) in dee_bal_edges if f"{s}->{t}" not in dee_all_res]
check(len(missing_dee_bal) == 0,
      f"SC-IT-DOMAIN-EXPANSION-EGO-001: all {len(dee_bal_edges)} BALANCE-ONLY edges present in residual_mismatches (missing={missing_dee_bal})")

check(all(d in dee_md for d in REQUIRED_DEPTS), "DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md: all 15 departments present")
check(all(f"`{p}`" in dee_md for p in REQUIRED_PRIMITIVES), "DOMAIN_DECODE_DOMAIN_EXPANSION_EGO.md: all 17 primitives present")

# 4. Verify SC-IT-OCTO-RNA-EDIT-001 and SC-HS-001 (v1.1.0) & their companion Markdown documents
octo_jsonl_path = os.path.join(COMPILED_DIR, "INVARIANT_ENTRY_SC-IT-OCTO-RNA-EDIT-001.jsonl")
octo_md_path = os.path.join(CAT_DIR, "DOMAIN_DECODE_OCTOPUS_RNA_EDITING.md")
check(os.path.exists(octo_jsonl_path), "INVARIANT_ENTRY_SC-IT-OCTO-RNA-EDIT-001.jsonl exists in compiled_entries")
check(os.path.exists(octo_md_path), "DOMAIN_DECODE_OCTOPUS_RNA_EDITING.md exists in docs/invariant_catalog")
with open(octo_jsonl_path, encoding="utf-8") as f:
    octo_obj = json.loads(f.readline())
check(octo_obj["metadata"]["entry_id"] == "SC-IT-OCTO-RNA-EDIT-001", "SC-IT-OCTO-RNA-EDIT-001: entry_id matches")
check(len(octo_obj["analysis"]["entities"]) == 12, "SC-IT-OCTO-RNA-EDIT-001: exact 12 entities")
check(len(octo_obj["analysis"]["relationships"]) == 20, "SC-IT-OCTO-RNA-EDIT-001: exact 20 non-neutral relationships")
check(octo_obj["structural_skeleton"]["metrics"] == {"nodes": 12, "ordered_pairs": 132, "non_neutral_edges": 20},
      "SC-IT-OCTO-RNA-EDIT-001: structural metrics 12/132/20 match")
octo_depts = [d["department"] for d in octo_obj["functional_departments"]]
check(len(octo_depts) == 15 and set(octo_depts) == REQUIRED_DEPTS, "SC-IT-OCTO-RNA-EDIT-001: exact 15/15 departments")
check(len(octo_obj["gates"]) == 9 and all(g["passed"] for g in octo_obj["gates"].values()),
      "SC-IT-OCTO-RNA-EDIT-001: 9/9 gates passed")
check(octo_obj["isomorphism_quality"]["score"] == 0.953 and octo_obj["dataset_tier"] == "GOLD",
      "SC-IT-OCTO-RNA-EDIT-001: GOLD score 0.953")
check(len(octo_obj["prediction_tests"]) == 4, "SC-IT-OCTO-RNA-EDIT-001: 4 prediction tests (P1..P4)")
for mp in octo_obj["isomorphism_analysis"]["mappings"]:
    check(substrate_gate_ok(mp) and len(mp["residual_mismatches"]) > 0,
          f"SC-IT-OCTO-RNA-EDIT-001 / {mp['mapping_id']}: substrate_confusion_check=True & non-empty residuals")
with open(octo_md_path, encoding="utf-8") as f:
    octo_md = f.read()
check(all(d in octo_md for d in REQUIRED_DEPTS), "DOMAIN_DECODE_OCTOPUS_RNA_EDITING.md: all 15 departments present")

hs_jsonl_path = os.path.join(COMPILED_DIR, "SC-HS-001_FLAT_FLRW_HUBBLE_SCHWARZSCHILD_PATCH.jsonl")
hs_md_path = os.path.join(REPO_ROOT, "docs", "FLAT_FLRW_HUBBLE_SCHWARZSCHILD_CORRESPONDENCE.md")
check(os.path.exists(hs_jsonl_path), "SC-HS-001_FLAT_FLRW_HUBBLE_SCHWARZSCHILD_PATCH.jsonl exists in compiled_entries")
check(os.path.exists(hs_md_path), "docs/FLAT_FLRW_HUBBLE_SCHWARZSCHILD_CORRESPONDENCE.md exists")
with open(hs_jsonl_path, encoding="utf-8") as f:
    hs_obj = json.loads(f.readline())
check(hs_obj["metadata"]["entry_id"] == "SC-HS-001" and hs_obj["metadata"]["entry_revision"] == "1.1.0",
      "SC-HS-001: entry_id and revision 1.1.0 match")
hs_claim_ids = [c["claim_id"] for c in hs_obj["analysis"]["claims"]]
check(hs_claim_ids == ["CLM-HS-001", "CLM-HS-002A", "CLM-HS-002B", "CLM-HS-003", "CLM-HS-004", "CLM-HS-005", "CLM-HS-006"],
      f"SC-HS-001: exact 7 v1.1.0 claims present ({hs_claim_ids})")
check(len(hs_obj["gates"]) == 9 and all(g["passed"] for g in hs_obj["gates"].values()),
      "SC-HS-001: 9/9 gates passed")
check(hs_obj["isomorphism_quality"]["score"] == 0.954 and hs_obj["dataset_tier"] == "GOLD",
      "SC-HS-001: GOLD score 0.954")
hs_map = hs_obj["isomorphism_analysis"]["mappings"][0]
check(substrate_gate_ok(hs_map) and len(hs_map["residual_mismatches"]) == 3,
      "SC-HS-001 / MAP:HS-001: substrate_confusion_check=True & 3 residual_mismatches")

omni_jsonl_path = os.path.join(COMPILED_DIR, "SC-OMNI-001_SPIRIT_BOMB_OMNI_STATE.jsonl")
reld_md_path = os.path.join(REPO_ROOT, "docs", "RELD_V3.md")
v7_md_path = os.path.join(REPO_ROOT, "docs", "CURTIS_THEOLOGICAL_MAP_UNIFIED_V7.md")
check(os.path.exists(omni_jsonl_path), "SC-OMNI-001_SPIRIT_BOMB_OMNI_STATE.jsonl exists in compiled_entries")
check(os.path.exists(reld_md_path), "docs/RELD_V3.md exists")
check(os.path.exists(v7_md_path), "docs/CURTIS_THEOLOGICAL_MAP_UNIFIED_V7.md exists")
with open(omni_jsonl_path, encoding="utf-8") as f:
    omni_obj = json.loads(f.readline())
check(omni_obj["metadata"]["entry_id"] == "SC-OMNI-001" and omni_obj["metadata"]["entry_revision"] == "2.0.0",
      "SC-OMNI-001: entry_id and revision 2.0.0 match")
check(len(omni_obj["analysis"]["claims"]) == 11, "SC-OMNI-001: exact 11 claims present")
omni_depts = [d["department"] for d in omni_obj["functional_departments"]]
check(len(omni_depts) == 15 and set(omni_depts) == REQUIRED_DEPTS, "SC-OMNI-001: exact 15/15 departments")
check(len(omni_obj["gates"]) == 9 and all(g["passed"] for g in omni_obj["gates"].values()),
      "SC-OMNI-001: 9/9 gates passed")
check(omni_obj["isomorphism_quality"]["score"] == 0.937 and omni_obj["dataset_tier"] == "GOLD",
      "SC-OMNI-001: GOLD score 0.937")
check(set(omni_obj["attenuation_protocol"].keys()) == {"time", "support", "intent"},
      "SC-OMNI-001: Attenuation Protocol has time/support/intent")
for mp in omni_obj["isomorphism_analysis"]["mappings"]:
    check(substrate_gate_ok(mp) and len(mp["residual_mismatches"]) > 0,
          f"SC-OMNI-001 / {mp['mapping_id']}: substrate_confusion_check=True & non-empty residuals")

# SC-DU-001 (The Duality) — post SC-PATCH-DU-001 revision
du_jsonl_path = os.path.join(COMPILED_DIR, "SC-DU-001_THE_DUALITY.jsonl")
check(os.path.exists(du_jsonl_path), "SC-DU-001_THE_DUALITY.jsonl exists in compiled_entries")
with open(du_jsonl_path, encoding="utf-8") as f:
    du_obj = json.loads(f.readline())
check(du_obj["metadata"]["entry_id"] == "SC-DU-001", "SC-DU-001: entry_id matches")
du_maps = du_obj["isomorphism_analysis"]["mappings"]
check(len(du_maps) == 4 and all(substrate_gate_ok(mp) for mp in du_maps),
      "SC-DU-001: 4/4 mappings carry substrate_confusion_check & positional_claims_permitted")
check(len(du_obj["gates"]) == 9 and all(g["passed"] for g in du_obj["gates"].values()),
      "SC-DU-001: 9/9 gates passed")
check("substrate confusion" in du_obj["gates"]["authority_safety"]["reason"].lower(),
      "SC-DU-001: authority_safety reason references substrate confusion")
check("substrate confusion" in du_obj["outputs"]["guardrails"][0].lower(),
      "SC-DU-001: guardrails reference substrate confusion")

# SC-PATCH-DU-001 checklist: no compiled or catalog entry carries the old gate field
for fp in sorted(glob.glob(os.path.join(COMPILED_DIR, "*.jsonl")) + glob.glob(os.path.join(CAT_DIR, "*.jsonl"))):
    with open(fp, encoding="utf-8") as f:
        raw = f.read()
    check("identity_claim_allowed" not in raw,
          f"{os.path.basename(fp)}: no `identity_claim_allowed` (SC-PATCH-DU-001)")
    for ln in raw.splitlines():
        if ln.strip():
            json.loads(ln)

# 5. Verify INVARIANT_CATALOG.md and DOMAIN_LEDGER.md cross-references and 25 classes
allowed_doc_ids = valid_entry_ids | EXTERNAL_UPSTREAM_IDS
for md_name in ["INVARIANT_CATALOG.md", "DOMAIN_LEDGER.md"]:
    mp = os.path.join(CAT_DIR, md_name)
    with open(mp, encoding="utf-8") as f:
        txt = f.read()
    found_ids = set(re.findall(r"(?<![A-Za-z0-9_-])SC-[A-Z0-9]+(?:-[A-Z0-9]+)*(?![A-Za-z0-9-])", txt))
    dangling_md = sorted(found_ids - allowed_doc_ids)
    check(len(dangling_md) == 0,
          f"{md_name}: zero dangling SC-* IDs (found {len(found_ids)} IDs, dangling={dangling_md})")

with open(os.path.join(CAT_DIR, "INVARIANT_CATALOG.md"), encoding="utf-8") as f:
    cat_txt = f.read()
class_headers = re.findall(r"^### Class (\d+):", cat_txt, re.MULTILINE)
check([int(x) for x in class_headers] == list(range(1, 26)),
      f"INVARIANT_CATALOG.md: exact Classes 1..25 present (found {len(class_headers)})")

# 6. Zero "etc." elisions across ALL emitted .md and .jsonl files
for fp in sorted(glob.glob(os.path.join(CAT_DIR, "*.md")) + glob.glob(os.path.join(CAT_DIR, "*.jsonl"))):
    with open(fp, encoding="utf-8") as f:
        txt = f.read()
    hits = re.findall(r"\betc\.", txt, re.IGNORECASE)
    check(len(hits) == 0, f"{os.path.basename(fp)}: zero 'etc.' occurrences (found {len(hits)})")

# Summary Report
print("=" * 72)
print(f"INVARIANT TRANSLATOR CATALOG VALIDATION SUMMARY")
print("=" * 72)
print(f"Checks PASSED: {len(checks_passed)}")
print(f"Checks FAILED: {len(errors)}")
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(f"  [FAIL] {e}")
    sys.exit(1)
else:
    print("\nALL CHECKS PASSED 100%:")
    for c in checks_passed:
        print(f"  [PASS] {c}")
    sys.exit(0)
