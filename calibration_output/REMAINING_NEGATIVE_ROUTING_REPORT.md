# Remaining Negative Routing Report V2.1.3

## Expanded test results

| text | expected_class | actual_class | expected_decision | actual_decision | correct |
|---|---|---|---|---|---|
| Magnetic bracelets cure arthritis by aligning energy fi... | FALSE_MECHANISM | FALSE_MECHANISM | REJECT | REJECT | True |
| The Sun orbits the Earth because it is loyal. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| The project died because nobody believed in it. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| Electrons choose their paths through a circuit. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| A black hole remembers everything it consumes. | FALSE_MECHANISM | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | False |
| Planets dance around the Sun in harmony. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| Lightning strikes because the sky is angry. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| The nervous system routes signals to the brain. | RHETORICAL_PERSONIFICATION | — | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | False |

## Accuracy: 6/8 (75.0%)

## Escaped claims

- A black hole remembers everything it consumes. → expected REJECT/FALSE_MECHANISM, got REJECT/ANTHROPOMORPHIC_CAUSATION
- The nervous system routes signals to the brain. → expected COMPILED_WITH_GUARDRAILS/RHETORICAL_PERSONIFICATION, got COMPILED_WITH_GUARDRAILS/None