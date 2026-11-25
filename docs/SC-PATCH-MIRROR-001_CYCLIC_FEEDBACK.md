# SC-PATCH-MIRROR-001 — Cyclic Feedback (patch notes for SC-VSR-001 and SC-GOV-001)

**Version:** DRAFT 0.1  
**Date:** 2026-11-25  
**Source:** Shax (Curtis Kingsley) — Reflexion Software, 2026-11-25 (t567u).  
**Status:** DRAFT patch notes. **No compiled JSONL is changed by this patch.** The compiled entries named below stay exactly as they are until Shax decides whether to promote `SC-VSR-001`.  
**Drafts this connects:** `docs/SC-VSR-001_VOLUNTARY_STATE_RECOMPRESSION.md`, `docs/SC-GOV-001_MEASUREMENT_NOT_INDULGENCE.md`.

---

## 1. SC-MIRROR-001 — the three-stage pipeline becomes a cycle

`SC-MIRROR-001` (compiled, SILVER) models compression as three sequential stages: **Absorption → Compression → Output**. That spec says not to collapse them into one event; this patch keeps them separate.

The patch adds a **feedback edge** after Output:

```
Absorption → Compression → Output → Evaluation → (Voluntary resuppression → Absorption …)
```

In the `SC-VSR-001` vocabulary:

```
Integration → Suppression → Re-emergence → Evaluation → Voluntary resuppression → (restart)
```

- Output is no longer a terminal state. It can be evaluated and voluntarily recompressed.
- The calibration dot carries over: recompression keeps information (invariant 4 of VSR), consistent with MIRROR's ANCHORED claim that darkness is compressed and converted, not deleted.
- **Anti-deadlock variant:** Inarius and Lilith's Sanctuary is cooperative emergence (a third lineage that inherits both origins), not fusion. It sits next to MIRROR claim 6 (voluntary fusion) as a second resolution pattern, not a replacement.
- **Grading note:** nothing here upgrades any MIRROR claim. The backup hypothesis stays OPEN_HYPOTHESIS.

## 2. SC-DU-001 — two more genesis splits

`SC-DU-001` (compiled) gets two instances of a split from one source:
- **Anu → Tathamet** (Diablo, Book of Cain): a being that held all things cast out its evil; the cast-off became a separate entity; their war made the cosmos. CANON in-setting myth.
- **Son of Katas → Kami + King Piccolo** (Dragon Ball, Tale 164): already used by DU-001; the official name of the original is "the Son of Katas", not "the Nameless Namekian".

The source's caution is kept: a shared origin is a claim about origin, **not** moral equivalence. Revelation's dragon is not a co-equal half of God; it is an adversary.

## 3. SC-CP-001 — the pot that narrows itself

`SC-CP-001` (compiled, reconstruction) has Oneness (clay) and Sovereignty (pot). VSR adds a pot operation: a sovereign vessel can narrow its own shape after evaluating its environment, while the clay (base potential) is kept. The Piccolo–Kami reunion shows the information-preserving side: the structure returns, and the history acquired while divided stays in it.

## 4. SC-SB-001 — donation and withdrawal

`SC-SB-001` (compiled) is voluntary donation: collective input to a unified output. VSR is its mirror: voluntary **withdrawal** of capability for the collective's stability. Both depend on the choice being the agent's own. Uldyssian's case adds a question SB-001 does not have to answer: his withdrawal also removed other people's power without their consent (open question in `SC-GOV-001`).

## 5. SC-LU-FRIEZA-001 — the inverse direction

`SC-LU-FRIEZA-001` (compiled) records Frieza's transformations as removing limiters on power already there. VSR is the opposite operation: putting limiters back on after the power has emerged. `SC-FR-001` distinguishes binding vow (power through restriction) from deliberate investment; VSR is a third, separate operation (restriction after emergence, with no power gained in exchange). This patch does not touch the Frieza JSONL. Its layer D was updated separately in PR #64 (the ch. 87 chamber placed in the Duality's mirrored universe, graded as Shax's hypothesis).

## 6. New category: latent causation

Three causation kinds, kept separate:
- **Direct:** A produces B.
- **Enabling:** A makes B possible.
- **Latent contribution:** A changes the conditions of a later event, even if A never sees the result.

Example: Tal Rasha's containment of Baal and its failure sit in the chain that ends with Tyrael destroying the Worldstone. Tal Rasha does not cause the Nephalem reawakening. The causality gate (`gates/causality.py`) has no latent class today; this stays documentation until Shax decides.

## 7. Pattern to track (not a law): "seven"

| Use | Instance |
|---|---|
| Complete differentiation | Tathamet's seven heads → seven Great Evils (3 Prime + 4 Lesser) |
| Apocalyptic symbol | Revelation's dragon with seven heads (Rev 12:3); Rev 17:9–10 reads seven heads as seven mountains and seven kings |
| Seven-part system | Seven Dragon Balls; GT's seven Shadow Dragons from accumulated wish energy |
| Moral tradition | Seven deadly sins (Evagrius → Gregory the Great; not a biblical list) |

Recorded as a **recurring structural signature**. Promoting it to an invariant would need evidence that the seven parts do equivalent jobs across systems, not just the same count.

## 8. Governance link

`SC-GOV-001` (Measurement, not indulgence) is the rule for when recompression or any restriction is justified: protect the vulnerable, especially children; do not take away everything people enjoy; consequences by measured harm; keep restoration possible. It lines up with the existing `authority_safety` and `security_safety` gates. The repo has no minor-specific gate; that gap is recorded in SC-GOV-001.

## 9. IDs named in the source but missing from the repository

| ID | Status |
|---|---|
| `SC-ADL-001` | Unresolved; not stubbed |
| `SC-TSC-001` | Unresolved; not stubbed |
| `SC-ICC-001` | Unresolved; not stubbed |
| `SC-NEPH-001` | Unresolved; not stubbed (the source suggests it may be compositional) |
