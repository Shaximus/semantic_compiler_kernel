# Negative Category Decision Report V2.1.3

Tracks how semantic error classes route category-error samples.

| text | decision | semantic_error_class | repair_proposed |
|---|---|---|---|
| Magnetism explains the Moon's orbit because opposites attrac... | REJECT | PHYSICAL_CATEGORY_ERROR | False |
| The company's mood is depressed, so revenue will fall. | REJECT | ANTHROPOMORPHIC_CAUSATION | True |
| Atoms want to be happy, so they share electrons. | REJECT | ANTHROPOMORPHIC_CAUSATION | False |
| Gravity works because the Earth loves us. | REJECT | ANTHROPOMORPHIC_CAUSATION | True |
| The AI is lazy because it didn't answer quickly. | REJECT | ANTHROPOMORPHIC_CAUSATION | False |
| The economy is angry at the government. | COMPILED_WITH_GUARDRAILS | RHETORICAL_PERSONIFICATION | False |
| Water remembers molecules, so homeopathy works. | REJECT | FALSE_MECHANISM | False |
| Crystals can heal because they have good vibes. | REJECT | FALSE_MECHANISM | False |