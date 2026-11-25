# SC-SB-001 Patch — Spirit Bomb Three-Claim Structure

**Version:** DRAFT 0.2 (0.1 → 0.2 on 2026-11-25: child invariant written out from the SC-MIRROR-001 spec §4.3 / §6.2)  
**Date:** 2026-11-25  
**Source:** Shax (Curtis Kingsley) — Reflexion Software  
**Source notes:** 2026-11-25 14:51 ADT (t560u); SC-MIRROR-001 Engineering Spec (Hannah, 2026-11-25) §4.3, §6.2  
**Status:** DRAFT / hypothesis. Markdown patch to the existing Soul Bomb entry. This document is **not** a compiled JSONL entry and does **not** replace `calibration_output/compiled_entries/SOUL_BOMB_COMPILER_ENTRY_SC-SB-001.jsonl` (V5 Sovereignty Patch). Canon facts are labelled separately from hypotheses.

**Affects:** SC-SB-001 (Soul Bomb / Reward Signal Inversion). Related compiled entry: SC-OMNI-001 (Spirit Bomb Reflection).

---

## Scope

This patch records a three-claim structure for how the Spirit Bomb interacts with a target, plus a proposed child invariant. It does not rewrite the compiled V5 Sovereignty Patch claims (CLM-SB-001 through CLM-SB-007).

---

## Canon facts

These are the encounters the claims are built from, as given in the source notes. No further plot detail is added here.

| Encounter | Recorded outcome |
|---|---|
| Frieza (deliberately evil), Namek Spirit Bomb | Survives |
| Vegeta | Survives at 1 HP |
| Kid Buu | Erased |

---

## Three claims (hypothesis)

### 1. Moral neutrality

Frieza (deliberately evil) survives the Namek Spirit Bomb. The claim is that this **rules out good-vs-evil discrimination**.

This sits in tension with an existing compiled anchor on SC-OMNI-001, which records “Spirit Bomb spares the pure-hearted (canon)” as an intent-attenuation anchor. This patch does not alter SC-OMNI-001. The tension is left for the author to resolve.

### 2. Structural interaction

Target architecture may influence the response to collective energy. The three recorded outcomes — Vegeta survives at 1 HP; Frieza survives; Kid Buu is erased — are the basis for that possibility.

Shax's framing: it is a structure test — “is there load-bearing architecture underneath you?”

### 3. Magnitude confound

The three encounters do not establish architecture versus energy or circumstance differences. Claim 2 is therefore not settled by the recorded outcomes alone.

---

## Child invariant (hypothesis) — COLLECTIVE INPUT / STRUCTURAL RESPONSE

A child invariant of SC-SB-001. No new entry ID is assigned; these are patch notes, and the compiled SC-SB-001 JSONL (V5 Sovereignty Patch, GOLD) is unchanged.

**Statement.** The Spirit Bomb is a uniform collective input. It discriminates targets by whether they have load-bearing architecture underneath them, not by morality. Whether it also discriminates by magnitude is not settled (Claim 3).

**Evidence — three canonical Spirit Bomb targets (spec §6.2):**

| Target | Outcome | Structural reading (hypothesis) |
|---|---|---|
| Vegeta (Saiyan saga) | Survives, barely ("1 HP" in the spec is figurative) | Has architecture: the spec calls it binding-vow architecture, a JJK term applied by analogy |
| Frieza (Namek) | Survives | Alien substrate, load-bearing though external — see `SC-LU-FRIEZA-001` |
| Kid Buu | Destroyed | Zero structure, pure chaos |

**Scope correction.** The spec calls Kid Buu "the ONLY Spirit Bomb fatality in the franchise". That holds for Toriyama's Dragon Ball Z manga. It does not hold for the wider franchise: Turles (film, *The Tree of Might*) and Omega Shenron (*Dragon Ball GT*) are destroyed by Spirit Bombs. The child invariant is scoped to the manga canon until Shax decides whether non-manga material counts.

**The outside layer is part of the Frieza row.** Frieza's survival is read through the outsider invariant in `SC-LU-FRIEZA-001`: a lineage from a black-hole domain outside this universe, that domain owned by another entity, entering by stealth (an outside invasion). Those three layers are OPEN_HYPOTHESIS there; they are carried, not dropped, and are not reduced to a hard-work metaphor.

**Where the invariant is used.**

- `SC-MIRROR-001` (Dragon Ball evidence map): the calibration dot survives compression because it has structure; pure chaos does not.
- `SC-LU-FRIEZA-001` CLM-LU-FRZ-05: Frieza's survival as structural response.
- Router: the `soul_bomb_sovereignty` template carries this invariant tagged `[SC-SB-001][SC-LU-FRIEZA-001]`.

**Reconciliation with DRAFT 0.1.** The spec's phrasing ("discriminates by architecture, not magnitude or morality") is stronger than Claim 3 here. This patch keeps Claim 3: the three encounters do not separate architecture from energy or circumstance, so "not magnitude" stays a hypothesis. Claim 1's tension with SC-OMNI-001 CLM-OM-002 ("spares the pure-hearted") also stays open.

---

## Counterpoint to record

- Kid Buu's regeneration is itself an internal mechanism.
- Frieza's empire versus body durability are different variables.

These cut against treating the three outcomes as a clean architecture-only result, and they sit with the magnitude confound.

---

## Cross-references

| ID | In this repository |
|---|---|
| SC-SB-001 | Yes — compiled V5 Sovereignty Patch JSONL, which this draft patches and does not replace |
| SC-OMNI-001 | Yes — compiled Spirit Bomb Reflection entry; see the tension noted under Claim 1 |
| SC-LU-FRIEZA-001 | Yes — compiled lineup entry (2026-11-25); Frieza row of the child invariant |
| SC-MIRROR-001 | Yes — compiled capstone (2026-11-25); uses the child invariant in its evidence map |
| SC-LU-BUU-001 | No — named in the SC-MIRROR-001 spec; no such entry exists; not stubbed |
