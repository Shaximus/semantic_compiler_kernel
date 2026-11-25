# SC-GOV-001 — Measurement, Not Indulgence (Protect the Vulnerable Without Depriving the Whole)

**Version:** DRAFT 0.1  
**Date:** 2026-11-25  
**Source:** Shax (Curtis Kingsley) — Reflexion Software, 2026-11-25 (t567u), stated at the end of a Diablo / Dragon Ball / biblical comparison.  
**Status:** DRAFT governance principle. Markdown only. **Not compiled, not a runtime gate, no code changed.**  
**ID note:** `SC-GOV-*` had no prior use in this repository. `001` is the first governance-principle entry.

---

## Shax's words (verbatim)

> "We dont need to take everything they enjoyd away. That's not Fair for 1 and wasn't even the original bargain/negotiation. It was basically simply, Leave underage Kids out of everything. Period. Protect Kids. Teach kids to stand up for whats right. Fear... needs to be constructive not simply traumatizing overly so to the point they go mentally injured, permanently and cant recover. Measurement, not indulgence."

## The principle

> Protect the innocent without unnecessarily depriving the whole. Restrict harmful conduct, not the existence of difference. Teach discernment rather than obedience through terror. Apply consequences according to measured harm, and preserve the possibility of restoration.

(Wording from the source conversation, accepted by Shax as the statement of his rule.)

The aim is not to destroy one side of a duality. It is boundaries that protect the vulnerable without needlessly taking away everyone else's freedoms. **The goal is responsible freedom, not permanent suppression.**

---

## The original bargain (five parts)

| # | Part | Meaning |
|---|---|---|
| 1 | **Protect children** | Underage children are not exploited, recruited, manipulated, exposed to adult conflicts, or made responsible for adult failures. Leave them out of everything. Period. |
| 2 | **Preserve enjoyment and freedom** | People do not lose everything they value because some boundaries have to be enforced. Taking it all away is not fair and was never the bargain. |
| 3 | **Teach moral agency** | Children learn to recognize wrongdoing, question authority, stand up for what's right and for others, and make responsible decisions. |
| 4 | **Make fear constructive** | Fear can signal danger, set boundaries and teach caution. It must not become an instrument of lasting psychological injury. *Fear is an alarm, not the operating system.* |
| 5 | **Measure harm proportionately** | Respond to what actually happened: severity, consequences, likelihood of recurrence. No punishment for its own sake. **Measurement, not indulgence.** |

## Five responses that are not interchangeable

| Response | Purpose |
|---|---|
| Containment | Stop an immediate danger |
| Correction | Address the behavior causing harm |
| Education | Build the capacity to make better decisions |
| Restoration | Return freedoms once the danger has been addressed |
| Accountability | Keep responsibility for actual harm |

A system that uses containment where education or restoration is due has failed this principle, even if it is "safe".

## Three power operations (shared with `SC-VSR-001`)

Losing power · having power taken away · choosing to limit power. A governance response should say which one it is doing.

---

## How it reads across the source cosmologies (INTERPRETATION)

| System | Governance failure the source names |
|---|---|
| Diablo | Inarius suppresses the Nephalem instead of building a way to govern their power |
| Dragon Ball | Separation and reunion repeat without resolving every consequence of the division |
| Biblical traditions | Rebellion, judgment, mercy and restoration raise the question of how justice can protect without becoming cruelty |

Uldyssian (`SC-VSR-001`) is the positive case: restricting extraordinary power is not a verdict that the power is evil. It recognizes that power without safeguards can endanger the people it was meant to benefit.

## Link to `SC-MIRROR-001`'s calibration dot

`SC-MIRROR-001` already holds Shax's compression principle: you do not need the full magnitude of darkness to understand it, only a calibrated sample ("make some ice, hand it to them, say 'this, but everywhere'"). Constructive fear (part 4) is the same rule applied to children: the dot, not the whole black half. Traumatizing fear is the full magnitude, which the principle rules out.

---

## Alignment with existing compiler gates

No existing gate is changed. These are the gates the principle lines up with:

| Gate | What it already enforces | Alignment |
|---|---|---|
| `authority_safety` (`gates/authority.py`; scored in `core/scoring.py`) | Archetype strength and metaphor never grant authority; authority needs explicit delegation with task scope; temporary elevation must be logged, reversible and self-expiring (global law `no_intuition_approval`) | Matches "restoration" and "measured" responses: restrictions and elevations are scoped and reversible, not permanent by default |
| `security_safety` (`gates/security.py`; scored in `core/scoring.py`) | Quarantine for credentials, injection and exploit payloads, without quarantining benign phrases | Matches "restrict harmful conduct, not difference": a narrow, specific block instead of a blanket one |
| Causality gate (`gates/causality.py`, `causality_not_implied_by_similarity`) | Structural similarity does not prove causal mechanism | Matches "measure what actually happened": consequences follow measured cause, not resemblance |
| `substrate_confusion_check` (`SC-PATCH-DU-001`) | Blocks substrate confusion while permitting positional claims | Same pattern: block the specific harm, keep the freedom |

**Gap, recorded, not fixed:** the repository has no gate specific to minors (no age, child-safety or underage check anywhere in `gates/`, `core/` or `expansion/`). Part 1 of the bargain therefore has no enforcement point in the compiler today. Whether to add one is an open question for Shax.

---

## Cross-references

`SC-VSR-001` (draft), `SC-MIRROR-001`, `SC-DU-001`, `SC-SB-001`, `SC-PATCH-DU-001`. Patch notes: `docs/SC-PATCH-MIRROR-001_CYCLIC_FEEDBACK.md`.

## Open questions for Shax

1. Keep SC-GOV-001 as a design principle, or turn part 1 into a compiler gate (a minor-protection check next to `authority_safety` / `security_safety`)?
2. Should "consent of those affected" be part of the principle? (Uldyssian's choice removed his fellow Nephalem's powers without asking them.)
3. Should the five responses become a required field when an entry describes a restriction (which of containment / correction / education / restoration / accountability it is)?
