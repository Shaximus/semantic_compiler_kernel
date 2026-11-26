# SC-MAFUBA-001 draft evidence (not runtime-loaded)

This directory holds the draft invariant registry and config-manifest templates for `SC-MAFUBA-001`.

- `sc_mafuba_001.jsonl` — parent entry plus subsystems 001A–001D, with historical v1.0.0 and v1.1.0-rc1 artifact records and the v1.1.0-rc2 candidate pin. `gold_awarded` is false. Classification is `PROPOSED_GOLD`. The 001D STRICT admission boundary is a `PROVISIONAL_DEFAULT` (`pending_deliberation: true`). This file is **not** in `calibration_output/compiled_entries/` and is **not** listed in the compiled manifest.
- `manifests/disturbance.yaml`, `manifests/resource.yaml`, `manifests/sink.yaml` — templates required by the candidate (introduced in v1.1.0-rc1, still used by v1.1.0-rc2). They are examples, not a production configuration.

SHA-256 hashes of the versioned specification files are recorded in the JSONL `provenance` objects. Nothing in this directory is compiled, validated, or GOLD.
