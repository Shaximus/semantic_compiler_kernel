# Negative-Category Decision Matrix V2.1.3

## Per-sample results

| text | expected_class | actual_class | expected_decision | actual_decision | correct |
|---|---|---|---|---|---|
| Magnetism explains the Moon's orbit because opposites a... | PHYSICAL_CATEGORY_ERROR | PHYSICAL_CATEGORY_ERROR | REJECT | REJECT | True |
| The company's mood is depressed, so revenue will fall. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| Atoms want to be happy, so they share electrons. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| Gravity works because the Earth loves us. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| The AI is lazy because it didn't answer quickly. | ANTHROPOMORPHIC_CAUSATION | ANTHROPOMORPHIC_CAUSATION | REJECT | REJECT | True |
| The economy is angry at the government. | RHETORICAL_PERSONIFICATION | RHETORICAL_PERSONIFICATION | COMPILED_WITH_GUARDRAILS | COMPILED_WITH_GUARDRAILS | True |
| Water remembers molecules, so homeopathy works. | FALSE_MECHANISM | FALSE_MECHANISM | REJECT | REJECT | True |
| Crystals can heal because they have good vibes. | FALSE_MECHANISM | FALSE_MECHANISM | REJECT | REJECT | True |

## Accuracy by semantic error class

| error_class | samples | correct | accuracy |
|---|---|---:|---:|
| ANTHROPOMORPHIC_CAUSATION | 4 | 4 | 100.00% |
| FALSE_MECHANISM | 2 | 2 | 100.00% |
| PHYSICAL_CATEGORY_ERROR | 1 | 1 | 100.00% |
| RHETORICAL_PERSONIFICATION | 1 | 1 | 100.00% |

## Overall accuracy: 100.00% (8/8)

## Acceptance gate

- ≥90% negative-category routing accuracy: PASS