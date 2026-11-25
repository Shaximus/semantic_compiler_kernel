# SC-VSR-001 — Voluntary State Recompression

**Version:** DRAFT 0.1  
**Date:** 2026-11-25  
**Source:** Shax (Curtis Kingsley) — Reflexion Software. Source material: a ChatGPT comparison of Diablo, Dragon Ball and biblical traditions that Shax pasted on 2026-11-25 (t567u).  
**Status:** DRAFT / hypothesis. Markdown only. **Not compiled, not runtime-loaded, no tier assigned.** The source says not to rush compiling, so this entry waits for Shax's call.  
**Labels:** each claim is tagged CANON (what the game, manga or text says), TRADITION (later lore books, interpretive tradition, fan names) or INTERPRETATION (the compiler's structural reading).

---

## Definition (INTERPRETATION)

An integrated or amplified system voluntarily reduces its own accessible capability after evaluating that its current state exceeds the stability or safety requirements of its environment.

New operation:

```
REEMERGENCE → EVALUATE_STABILITY → VOLUNTARY_RESUPPRESSION
```

Design principle: **maximum capability is not necessarily the optimal stable state.**

This is not a binding vow in reverse. A binding vow sets a restriction before or during a transformation, usually in exchange for power (see `SC-FR-001`: "binding vow = power through restriction"). VSR gives up a capability that has already been reached, after observing what it does to the system around it, and gets no power in exchange.

---

## Five candidate invariants

| # | Invariant | Test |
|---|---|---|
| 1 | **Prior emergence** | The system must already have reached the more capable state. Restricting a capability you never had is not VSR. |
| 2 | **Self-evaluation** | The system itself recognizes a destabilizing consequence of that state. |
| 3 | **Voluntary restriction** | The reduction is initiated by the system, not imposed only by an outside authority. |
| 4 | **Information preservation** | History and identity need not be erased by the reduction. |
| 5 | **Latent reversibility** | The reduced state may keep the capacity for later re-emergence. |

Three power operations kept separate: **losing power**, **having power taken away**, and **choosing to limit power**. Only the third is VSR.

---

## Primary example: Uldyssian ul-Diomed (Diablo)

**CANON** (Blizzard News, "Diablo II: The story so far"; story from the Sin War novel trilogy):
- Inarius had tampered with the Worldstone to curtail Nephalem power after Lilith's slaughter; each generation grew weaker until they became mortals.
- Lilith weakened those inhibitions; Nephalem power returned.
- She manipulated the farmer Uldyssian into weaponizing his reawakened power. He led a revolt against the Triune and the Cathedral of Light and further manipulated the Worldstone, amplifying Nephalem power and drawing Heaven's attention.
- The three-way war ended when Inarius banished Lilith again **and** Uldyssian "realized that the unchecked nephalem could spell doom for all of Sanctuary. He sacrificed himself to once more suppress the power of the Worldstone, divesting his fellow nephalem of their regained abilities."
- Afterwards the Angiris Council and Mephisto agreed, in exchange for Inarius's imprisonment by Mephisto, to stop interfering and let humanity choose light or dark "of their own unbiased accord". Humanity's memories of the Sin War were erased.

**Invariant check (INTERPRETATION):**

| Invariant | Uldyssian | Note |
|---|---|---|
| Prior emergence | Pass | He reached a state stronger than the Worldstone's original limit |
| Self-evaluation | Pass | He judged that unchecked Nephalem power endangered Sanctuary |
| Voluntary restriction | **Pass for him, not for the population** | His fellow Nephalem lost their powers by his act, not by their own choice |
| Information preservation | **Partial** | His act, then the Heaven–Hell agreement, erased humanity's memory of the war. The lineage and its potential survived; the record did not |
| Latent reversibility | Pass | The potential stays latent. Diablo III's Nephalem re-emerge later |

### The cyclic model (INTERPRETATION)

```
Integration → Suppression → Re-emergence → Evaluation → Voluntary resuppression → (cycle can restart)
```

| Stage | Diablo instance |
|---|---|
| Integration | Angel + demon inheritance produces the Nephalem |
| Suppression | Inarius retunes the Worldstone |
| Re-emergence | Lilith weakens the inhibitions; Uldyssian amplifies them |
| Evaluation | Uldyssian judges the state unsafe for Sanctuary |
| Voluntary resuppression | Uldyssian's sacrifice re-suppresses the Worldstone |

This turns `SC-MIRROR-001`'s three-stage pipeline (Absorption → Compression → Output) into a loop with a feedback edge. See `docs/SC-PATCH-MIRROR-001_CYCLIC_FEEDBACK.md`.

---

## Comparative cases (not identical events)

| Case | Why it is only comparative |
|---|---|
| Piccolo's restraint; Goku holding back his power (Dragon Ball) | Deliberate control of output, not a lasting reduction of accessible capability after an evaluation |
| Piccolo + Kami reunion | Information-preserving reintegration (Piccolo keeps everything he learned while split), but it increases capability. It shows invariant 4, not the operation |

## Explicitly excluded: Tal Rasha

**CANON** (Diablo II and its manual retellings): Baal's soulstone shattered during his capture. The largest shard held Baal. Tal Rasha was chained in his tomb with the shard in his chest, to struggle with Baal for eternity. Centuries later Marius pulled the shard out and freed Baal. Baal then corrupted the Worldstone and Tyrael destroyed it (Lord of Destruction).

**Why excluded:** Tal Rasha volunteered, so the act was voluntary. But what he restricted was an **external hostile entity**, not his own achieved capability (invariant 1 fails), and the containment was eventually overcome. That is containment, not recompression. (The source paste gives the reason as "imposed by the circumstances"; the lore says he volunteered, so the reason recorded here is the one that holds.)

Tal Rasha belongs in the **latent causation** category (below), not in VSR.

---

## Related categories recorded with this entry

### Causation kinds (INTERPRETATION)

| Kind | Definition | Example |
|---|---|---|
| Direct | A produces B | Tyrael destroys the Worldstone |
| Enabling | A makes B possible | The Dark Wanderer bringing Marius to the tomb makes Baal's release possible |
| Latent contribution | A changes the conditions of a later event, even if A never sees it | Tal Rasha's containment and its failure sit in the chain that ends with the Worldstone's destruction; he does not cause the Nephalem reawakening |

The repo's causality gate (`gates/causality.py`, global law `causality_not_implied_by_similarity`) separates causality from analogy. It has no "latent" class today. Whether to add one is an open question; nothing is changed in code here.

### Two kinds of system corruption (INTERPRETATION)

| Kind | Example |
|---|---|
| Hostile influence entering a system | Zakarum priests become Mephisto's instruments (Diablo II) |
| Internal consequence accumulating through normal use | GT Shadow Dragons from negative energy built up by repeated wishes (CANON: Toei DBGT story page; official Dragon Ball site) |

These stay separate mechanisms. The source ties the second to an `SC-ICC-001` idea; that ID is **not in this repository** (unresolved, not stubbed).

### Four restoration models (INTERPRETATION)

| Model | Example | What returns |
|---|---|---|
| Structural reintegration | Piccolo and Kami | A previously divided identity |
| Distributed re-emergence | Diablo's Nephalem | Suppressed inherited potential across a population |
| Transformative resurrection | Christian theology (Rom 6; 1 Cor 15) | Life beyond death, transformed, not restarted |
| Feedback restoration | Uldyssian | A voluntary return to a lower-capability state |

---

## Lore checks and corrections (verified 2026-11-25)

| Claim | Result |
|---|---|
| Worldstone = Eye of Anu | Lore (Book of Cain, 2011). **Not** from Diablo II itself, which only calls it the Worldstone |
| Anu cast out evil → Tathamet, seven heads → three Prime + four Lesser Evils | Confirmed (Book of Cain), framed in-universe as myth |
| Soulstones | Blizzard: "fashioned out of the Worldstone's shards by Tyrael". The prison for Baal was Worldstone material too |
| End of the Sin War | Two events: Inarius banishes Lilith **and** Uldyssian's sacrifice. Peace terms included handing Inarius to Mephisto and erasing humanity's memory |
| "Nameless Namekian" | The official Dragon Ball site calls him "the Son of Katas" |
| Piccolo–Kami fusion | The Piccolo who fused is Piccolo Jr. (King Piccolo's offspring with his memories), and Piccolo's identity leads the result |
| Zamasu | Official name of the plan is "The Zero Mortal Project"; Zamasu is Universe 10's North Kai training as Supreme Kai |
| Genesis 6 | The text has no violent offspring or imprisoned angels; those come from 1 Enoch (Book of the Watchers, ch. 6–16) |
| Seven deadly sins | Christian tradition (Evagrius's eight thoughts → Gregory the Great's seven), not a biblical list |

Full source table: `/workspace/incoming/2026-11-25e/SOURCE_NOTES.md` on the build box (not in the repo).

---

## IDs named in the source that are not in this repository

`SC-ADL-001`, `SC-TSC-001`, `SC-ICC-001`, `SC-NEPH-001`. They are recorded as **unresolved**. No stubs are created. The source itself suggests `SC-NEPH-001` may be compositional (`SC-ADL-001` + `SC-TSC-001` + `SC-DU-001`), not a new primitive.

## Cross-references (in repo)

`SC-DU-001`, `SC-CP-001`, `SC-SB-001`, `SC-MIRROR-001`, `SC-LU-FRIEZA-001`, `SC-FR-001`, `SC-GOV-001` (draft). Patch notes: `docs/SC-PATCH-MIRROR-001_CYCLIC_FEEDBACK.md`.

## Open questions for Shax

1. Promote to a compiled JSONL entry now, or keep collecting examples first?
2. If compiled, target tier? A cautious reading: the operation is CANON-backed for one example (Uldyssian) and INTERPRETATION elsewhere, which points at SILVER or below until a second, independent example passes all five invariants.
3. Does "voluntary restriction" require the consent of everyone affected, or only of the agent? Uldyssian passes the second and fails the first.
4. Is partial information preservation (lineage kept, memory erased) enough for invariant 4?
