# Kestrel Lab — Three-Cycle Hardening Report

Baseline: \`main@4110edc110336b40c07968499ebc2fac662e9e63\`
Experiment: \`kestrel/lab-3cycle\`

## Executive result

Three bounded defects were identified and repaired on the isolated branch. The canonical
\`main\` branch remained unchanged during the original experiment.

The original report's runtime verification was pending. The fixes were subsequently
reproduced and executed against V3.0.0 on 2026-11-06. This addendum preserves the
original findings and records the later verification.

## Cycle 1 — Decision-derivative consistency

The core pipeline built the routing packet and literal, public, and executive translations
before Stage 9 calculated the final decision. Those derivatives could retain \`PENDING\`
or stale routing state.

The V3 package-entry wrapper, \`compat.compile_semantic_packet\`, rebuilds the routing
packet and translations from the final decision, then rebuilds the dataset tier, SFT
export, dataset row, and audit record in dependency order.

The wrapper does not change scoring, the decision, or any gate. Early-exit packets that
never built derivatives remain unchanged.

**Remaining architectural limitation:** callers importing
\`semantic_compiler.core.pipeline.compile_semantic_packet\` directly bypass the wrapper.
This includes corpus scripts and \`expansion.corpus\`. The preferred long-term repair is
to reorder derivative construction inside \`core/pipeline.py\` after the V3 freeze permits it.

## Cycle 2 — Sensitive SFT prompt leakage

The core SFT builder labels sensitive prompts as redacted but appends the original text.
The wrapper replaces user messages for \`SENSITIVE\` and \`CRITICAL\` packets with a
SHA-256 provenance marker, and rebuilds the dataset row so its embedded SFT copy is
also redacted. The default-deny \`qwen_sft_ready\` disposition is unchanged.

**Important known gap:** the wrapper does not redact every raw-text-bearing field in the
dataset row. The row can still carry sensitive text in \`input.normalized_input\`,
\`input.claims[].content\`, and \`semantic_compilation.semantic_ir.claims[].content\`,
while declaring \`privacy.redactions_required: ["raw_input"]\` and
\`export_disposition: PROHIBITED\`. The row remains not training-ready. This is a
separate privacy/export-boundary decision and must not be mistaken for full-row
redaction. Tests retain this as an expected failure until the owner defines the
downstream redaction contract.

## Cycle 3 — Release-version provenance

The package version, \`pyproject.toml\`, and V3.0.0 release manifest agree on
\`3.0.0\`. The packet metadata version remains \`2.0.0\` and is copied into audit
records and dataset rows as \`compiler_version\`.

Changing packet metadata affects generated artifacts and compatibility. It remains a
dedicated migration rather than being silently changed in this pass.

## Acceptance gate

- Full pytest suite: 350 passed, 4 documented expected failures.
- Unittest discovery: 151 tests passed, 4 documented expected failures.
- The three-cycle regression tests execute against V3.0.0.
- Calibration and freeze artifacts were compared in memory for the 76-input calibration
  set; release artifacts were not regenerated.
- Moving the wrapper logic into the frozen core pipeline remains an owner decision.

## Provenance

The original lab report was written on 2026-07-15 against V2.1.3. The V3.0.0
addendum was prepared on 2026-11-06 after reproducing the stale-derivative and
SFT-prompt defects against the released package. This report distinguishes the
original experiment from later verification; it does not claim that GitHub Actions
has run unless a workflow run is recorded.
