# Missing Organ Precision Report V2.1.2

## Scope-aware changes
- Missing-organ detection now runs only when the mode is structural-reconstruction,
  the input claims completeness, or the user explicitly requests it.
- `expected_at_scale: Unknown` findings are no longer counted as confirmed absence.
- Fragmentary one-sentence analogies cannot support `ABSENT_CONFIRMED`.

## Unit-test evidence
- `test_fragmentary_analogy_marks_unobserved` — passing
- `test_unknown_scale_does_not_confirm_absence` — passing
- `test_whole_system_mode_allows_absent_confirmed` — passing
- `test_default_mode_does_not_emit_missing` — passing
- `test_structural_reconstruction_does_not_use_unobserved` — passing

## Calibration corpus observation
Ground-truth missing-organ labels are not yet annotated, so precision/recall
numbers require a seeded evaluation set. The scope gate is in place and covered
by tests; the next step is a 40-case hand-labeled evaluation.
