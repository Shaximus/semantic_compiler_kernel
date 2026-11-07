# V3.0.0 review patch set (2026-11-06)

Source: project folder artifacts after local review. Apply in order on pristine main.

- `00-ALL-IN-ONE.patch` — combined 01–07
- `07-kestrel-integration.patch` — Kestrel lab branch integration

See `docs/REVIEW_REPORT.md` and `docs/REVIEW_REPORT-1.md` for the written review.

Companion expansion added in the same session:
- `expansion/templates/android_connectivity.yaml` (pattern-lock / Ark diagnosis domain)
- `expansion/templates/bluetooth.yaml` (Bluetooth/BLE domain)

## Incoming 2026-11-06 bundle

`incoming-20261106/` keeps the later review delivery (patches 01–09, not only 01–07). The stub files above stay as pointers to the earlier project-folder copies. SHA-256 sums of the preserved bytes are in `incoming-20261106/SHA256SUMS.txt`. The full narrative, including sections H and I, is `docs/REVIEW_REPORT_20261106_FULL.md`. `docs/REVIEW_REPORT.md` and `docs/REVIEW_REPORT-1.md` remain the shorter notes that already mention the handset domains.

Applied on top of current `main`, without replaying hunks that would overwrite newer files:

- Translation repairs in `translation/structural_resolver.py`, `translation/buildcraft.py`, and `translation/fractal.py`, with their regression tests.
- `expansion/templates/poe_chaos_inoculation.yaml`, `docs/POE_CHAOS_INOCULATION_INVARIANTS.md`, routing keywords, calibration samples, and the reference-model test. The single-buffer note in the delivery is byte-identical to that provenance document.
- Optional `medical_map` on domain-template components, which the shipped templates already use.

Left in place because `main` is newer:

- `expansion/templates/mobile_security.yaml`, `networking.yaml`, `trust_chain.yaml`, and `docs/DEEP_SYSTEM_INVARIANTS.md` (precision pass; Knox is not modeled as generic Android).
- `docs/kestrel/Kestrel_Lab_3_Cycle_Report.md` and `.github/workflows/ci.yml` (later verification note and `kestrel/v3` branch).
- `android_connectivity` and `bluetooth` templates, `CLAUDE.md`, and the review summaries.

Not applied, because `core/` and `registry/` stay frozen without a separate waiver. The change is still inside `00-ALL-IN-ONE-01-through-09.patch` (one `claim_type` read in `core/pipeline.py`, plus consistency checks in `registry/cosmological_constants.py` and their tests). The review itself marks that patch as needing a decision.
