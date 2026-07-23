# Kestrel Lab — Three-Cycle Hardening Report

Baseline: `main@4110edc110336b40c07968499ebc2fac662e9e63`
Experiment: `kestrel/lab-3cycle`

## Executive result

Three bounded defects were identified and repaired on the isolated branch. The canonical `main` branch remains unchanged.

Runtime verification is **pending** because no GitHub Actions run was created for the branch/PR and the external execution container returned `ClientResponseError` before extraction. No passing-test claim is made for the experiment branch.

## Cycle 1 — Decision-derivative consistency

### Test

Inspect ordering in `core/pipeline.py` and assert that exported routing and executive translations equal the final packet decision.

### Baseline finding

The pipeline built `routing_packet`, `literal_translation`, `public_translation`, and `executive_translation` before Stage 9 calculated the final decision. These derivatives could retain `PENDING` or stale routing state.

### Repair

Added `compat.compile_semantic_packet`, which recompiles all decision-dependent derivatives after the core pipeline returns.

### Score

- Static invariant before: 0/2 decision-dependent surfaces guaranteed current.
- Static invariant after: 2/2 rebuilt from final decision.
- Runtime result: pending.

## Cycle 2 — Sensitive SFT prompt leakage

### Test

Compile a packet with `privacy_sensitivity=SENSITIVE` and assert the raw input does not appear in the Qwen user message.

### Baseline finding

`build_qwen_sft_output` labeled content as redacted but concatenated the unredacted raw input:

```python
user_content = "Compile (redacted): " + raw
```

### Repair

The package wrapper replaces sensitive/critical user content with a SHA-256 provenance marker and preserves the default-deny training disposition.

### Score

- Raw sensitive text echoed before: yes.
- Raw sensitive text echoed after wrapper: no.
- Provenance retained after: SHA-256 only.
- Runtime result: pending.

## Cycle 3 — Release-version provenance

### Test

Assert `semantic_compiler.__version__ == "2.1.3"`.

### Baseline finding

The repository README and manifest declared V2.1.3 while the package exported `2.0.0-draft`; packet metadata and manifest also retain older version identifiers.

### Repair

Aligned the public package version and module heading to V2.1.3. Packet/manifest migration is intentionally not changed in this bounded experiment because it affects generated-artifact compatibility and should be handled as a dedicated release-metadata migration.

### Score

- Public package/release alignment before: fail.
- Public package/release alignment after: pass by source inspection.
- Full metadata alignment: partial; packet and generated manifest remain documented follow-up work.
- Runtime result: pending.

## Files changed

- `compat.py`
- `__init__.py`
- `tests/test_kestrel_lab_regressions.py`
- `.github/workflows/kestrel-lab.yml`

## Acceptance gate

Do not merge until:

1. The canonical 67-test suite passes.
2. All three new regression tests pass.
3. Calibration and freeze artifacts are regenerated and compared.
4. Logos reviews whether the wrapper should become core pipeline reordering instead.

## Kestrel recommendation

The privacy defect is merge-worthy once tested. The stale derivative defect is real, but the preferred long-term implementation is to reorder Stage 7/8 derivatives after Stage 9 inside `core/pipeline.py`, not retain a permanent compatibility wrapper. Version metadata should receive a separate, comprehensive migration covering package, packet, manifest, and generated artifacts.
