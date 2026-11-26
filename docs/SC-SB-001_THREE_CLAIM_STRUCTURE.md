# SC-SB-001 Patch — Spirit Bomb Three-Claim Structure

**Version:** DRAFT 0.4 (0.1 → 0.2 on 2026-11-25: child invariant written out from the SC-MIRROR-001 spec §4.3 / §6.2; 0.2 → 0.3 the same day: Shax ruled that GT and the films count as evidence, so the Spirit Bomb kill list covers the whole franchise; 0.3 → 0.4 the same day: Shax's standalone source `SC-SIT-001` Structural Integrity Test (t573u upload) folded in, see the section below)  
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

**Evidence base (Shax, 2026-11-25): GT and the films count.** With them counted, Kid Buu is not "the ONLY Spirit Bomb fatality in the franchise" (spec §4.3, §6.2). The full record:

| Target | Source | Outcome | Structural reading (hypothesis) |
|---|---|---|---|
| Dr. Wheelo | Film, *The World's Strongest* | Destroyed | A brain running a built body: power not grown in its own architecture |
| Turles | Film, *The Tree of Might* | Destroyed | Power from the Tree of Might's fruit: consumed, not built (the bomb is charged from the Tree's own energy) |
| Lord Slug | Film, *Lord Slug* | Destroyed | Youth restored by a Dragon Ball wish. Weakest fit: a native Super Namekian with his own architecture |
| Kid Buu | *Dragon Ball Z* | Destroyed | Zero structure, pure chaos |
| Omega Shenron | *Dragon Ball GT* (Universal Spirit Bomb) | Destroyed | Accumulated negative energy from Dragon Ball wishes |
| Vegeta | *Dragon Ball Z*, Saiyan saga | Survives | Own architecture |
| Frieza | *Dragon Ball Z*, Namek | Survives | Own architecture, external substrate (`SC-LU-FRIEZA-001`) |
| Jiren | *Dragon Ball Super*, Tournament of Power | Survives (pushes it back) | Own architecture |

Edge cases, not counted either way: Super Android 13 (film; Goku absorbs the gathered Spirit Bomb energy and strikes directly, no bomb is thrown) and Hatchiyack (OVA *Plan to Eradicate the Saiyans*).

Reading (hypothesis): the destroyed targets run on borrowed, consumed or accumulated power; the survivors run on their own load-bearing architecture. Lord Slug fits worst. The magnitude confound (Claim 3) is stronger with the films included, because several film bombs were scaled up for the climax.

**The outside layer is part of the Frieza row.** Frieza's survival is read through the outsider invariant in `SC-LU-FRIEZA-001`: a lineage from a black-hole domain outside this universe, that domain owned by another entity, entering by stealth (an outside invasion). Those three layers are OPEN_HYPOTHESIS there; they are carried, not dropped, and are not reduced to a hard-work metaphor.

**Where the invariant is used.**

- `SC-MIRROR-001` (Dragon Ball evidence map): the calibration dot survives compression because it has structure; pure chaos does not.
- `SC-LU-FRIEZA-001` CLM-LU-FRZ-05: Frieza's survival as structural response.
- Router: the `soul_bomb_sovereignty` template carries this invariant tagged `[SC-SB-001][SC-LU-FRIEZA-001]`.

**Reconciliation with DRAFT 0.1.** The spec's phrasing ("discriminates by architecture, not magnitude or morality") is stronger than Claim 3 here. This patch keeps Claim 3: the encounters do not separate architecture from energy or circumstance, so "not magnitude" stays a hypothesis. Claim 1's tension with SC-OMNI-001 CLM-OM-002 ("spares the pure-hearted") also stays open.

---

## Counterpoint to record

- Kid Buu's regeneration is itself an internal mechanism.
- Frieza's empire versus body durability are different variables.

These cut against treating the three outcomes as a clean architecture-only result, and they sit with the magnitude confound.

---

## SC-SIT-001 Structural Integrity Test (Shax source, t573u): folded into this patch

**Source:** `docs/evidence/source-2026-11-25g/10_SC-SIT-001_structural_integrity_test.jsonl` (verbatim). **Status:** source material for this patch. `SC-SIT-001` is not a compiled entry and is not loaded by the runtime. Most of it restates the child invariant above, so no separate entry is created.

**What SIT adds.**
- The "structural integrity test" framing: uniform stress reveals architecture, and "the crisis didn't break anything, it revealed what was already broken" (CLM-SIT-005).
- A three-outcome classification:
  1. binding-vow architecture **absorbs** (Vegeta);
  2. alien substrate **deflects** (Frieza);
  3. zero structure is **destroyed** (Kid Buu).
- Substrate activation (Black Frieza) as a third power mechanism (CLM-SIT-003). It is already recorded as SC-LU-FRIEZA-001 layer E.
- A cosmological reading: the CMB as a uniform test that separates bound structure, dark matter and plasma (CLM-SIT-004).

**Canon corrections (recorded; the source wording stays in the evidence file).**
- **Frieza did not deflect the Namek Spirit Bomb.** He took it directly, was driven down into the planet, and survived badly injured. The only deflection in canon is Gohan bouncing the Saiyan-saga bomb back onto Vegeta, and Vegeta then took it directly (DB ch. 238; SC-LU-VEGETA-001 CLM-LU-VEG-04). The "deflects" outcome has no canon instance. Both survivors were **hit and survived**. Outcome classes 1 and 2 are therefore one class, survival under a direct hit. They differ only in the architecture reading.
- **"Kid Buu is the ONLY fatality"** was already corrected in DRAFT 0.3. With films and GT counted, Dr. Wheelo, Turles, Lord Slug and Omega Shenron are also destroyed.
- **"Frieza has never trained"** is true only until *Resurrection 'F'* (2015 film; *Dragon Ball Super*). There he trains for about four months and reaches Golden Frieza. So Black Frieza (DBS manga ch. 87, ten years of training) is **not** his "first compatible input". Golden Frieza came first.
- **"Survival is determined by architecture, not raw power"** is stronger than Claim 3 (magnitude confound), which this patch keeps. It is recorded as Shax's reading (SHAX_INTERPRETATION), not as a result.

**Grades (SIT's self-grade vs this patch).**

| Claim | Self-grade | Here |
|---|---|---|
| CLM-SIT-001 uniform input, architecture decides | ISOMORPHIC_INVARIANT 0.9 | Hypothesis, as Claim 2; magnitude confound open (Claim 3) |
| CLM-SIT-002 three outcomes (absorb / deflect / destroyed) | ISOMORPHIC_INVARIANT 0.85 | ANALOGOUS 0.6; "deflect" has no canon instance |
| CLM-SIT-003 substrate activation (Black Frieza) | ANALOGOUS 0.8 | ANALOGOUS 0.7, with Golden Frieza as the earlier activation (SC-LU-FRIEZA-001 layer E) |
| CLM-SIT-004 CMB as a cosmological integrity test | ANALOGOUS 0.75 | ANALOGOUS 0.5. CMB anisotropies trace primordial density perturbations; dark matter is not "deflected" by the CMB, it simply does not couple to photons. |
| CLM-SIT-005 "the crisis revealed what was broken" | ISOMORPHIC_INVARIANT 0.85 | ANALOGOUS 0.75 (stress testing in engineering is an anchor for the method, not for the cross-scale claim) |

**Unchanged.** The tension between Claim 1 (moral neutrality) and SC-OMNI-001 CLM-OM-002 ("spares the pure-hearted") stays open for Shax. SIT sides with moral neutrality.

---

## Cross-references

| ID | In this repository |
|---|---|
| SC-SB-001 | Yes — compiled V5 Sovereignty Patch JSONL, which this draft patches and does not replace |
| SC-OMNI-001 | Yes — compiled Spirit Bomb Reflection entry; see the tension noted under Claim 1 |
| SC-LU-FRIEZA-001 | Yes — compiled lineup entry (2026-11-25); Frieza row of the child invariant |
| SC-MIRROR-001 | Yes — compiled capstone (2026-11-25); uses the child invariant in its evidence map |
| SC-LU-BUU-001 | No — named in the SC-MIRROR-001 spec; no such entry exists; not stubbed |
| SC-CP-001 | Yes — compiled 2026-11-25 as a reconstruction (GOLD 0.926) |
| SC-SIT-001 | Source draft only (verbatim in `docs/evidence/source-2026-11-25g/`); folded into this patch in DRAFT 0.4, not compiled |
