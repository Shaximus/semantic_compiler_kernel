# SCC-001-AC draft registry (not runtime-loaded)

- `scc_001_anti_capture.jsonl` holds one line, the `SCC-001-AC` entry (0.1.0-rc2). It is `PROPOSED_GOLD` with `gold_awarded: false`. Its verification axes are kept separate: `DRAFT_SPECIFIED_UNPROVEN`, `REFERENCE_ONLY` and `UNVALIDATED`. The rc1 formal conditions from Shax's t599u registry line are kept verbatim in `source_formal_conditions_rc1`. The refined rc2 conditions are in `formal_conditions`.
- `live_interface_gaps` lists the four strict xfails against code that already existed. `tests/test_scc_001_ac_anti_capture.py` checks that this list matches the test markers exactly.
- `provenance.spec_sha256` is the attachment's content address as delivered. It has status `UNVERIFIED_ATTACHMENT_CONTENT_ADDRESS` because the compiler did not recompute it. `reconstructed_spec_sha256` pins `docs/SCC-001-AC_ANTI_CAPTURE.md`.

This file is **not** in `calibration_output/compiled_entries/` and is **not** in the compiled manifest. Nothing here is compiled, validated, or GOLD.
