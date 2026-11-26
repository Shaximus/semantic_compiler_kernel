# SCC-001-AC draft registry (not runtime-loaded)

- `scc_001_anti_capture.jsonl` holds one line, the `SCC-001-AC` entry (0.1.0-rc2). It is `PROPOSED_GOLD` with `gold_awarded: false`. Its verification axes are kept separate: `DRAFT_SPECIFIED_UNPROVEN`, `REFERENCE_ONLY` and `UNVALIDATED`. Shax's rc1 formal conditions are kept verbatim in `source_formal_conditions_rc1`, and the refined rc2 conditions are in `formal_conditions`.
- `provenance.spec_sha256` is the content hash of the verbatim rc1 spec, `docs/evidence/source-2026-11-26c/SCC-001-AC_original.md`. `refined_spec_sha256` pins `docs/SCC-001-AC_ANTI_CAPTURE.md`. `redactions` is empty, because the scan found no personal data.
- `manifest_pins` holds the SHA-256 of the three real SC-MAFUBA-001 manifests, which the oracle binds to (rc1 section 6 step 1).
- `live_interface_gaps` lists the eight strict xfails, which are the capture paths found in existing code and manifests. `tests/test_scc_001_ac_anti_capture.py` checks that this list matches the test markers exactly.
- `reproducibility.json` holds file hashes of the reference, tests, specs and manifests, plus a hash of the sorted per-test outcomes. Registry tests are excluded from that hash so it is not circular.

Nothing here is in `calibration_output/compiled_entries/` or the compiled manifest. Nothing here is compiled, validated or GOLD.
