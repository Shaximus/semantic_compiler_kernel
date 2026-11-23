# 17-Primitive Grammar, Reference Node Invariants & Seed Catalog Classes

## The 17-Primitive Grammar

Write `N/A` when a primitive is genuinely absent; absence is structural data.

| # | Primitive | Diagnostic Question |
|---|---|---|
| 1 | `POOL` | What quantities exist (life, ES, stress, fuel, cell count, trust, energy)? |
| 2 | `CAPACITY / CAP` | What is the maximum of each pool, and what sets it? |
| 3 | `INFLOW / REGEN` | How do pools refill, at what rate, and what delays or interrupts refill? |
| 4 | `OUTFLOW / DRAIN` | How do pools empty (hits, degen, leaks, consumption)? |
| 5 | `CHANNEL / TYPE` | Which kind of pressure is involved? Does it bypass any layer? |
| 6 | `FILTER / MITIGATION` | Which layers reduce incoming pressure (typed resists vs. general armour)? Is there a cap? |
| 7 | `THRESHOLD` | Where does behavior change discontinuously (failure, ignition, freeze, metastasis)? |
| 8 | `TRIGGER` | What crosses the threshold? |
| 9 | `RELEASE` | What happens at the crossing (instant or gradual, local or propagating)? |
| 10 | `PROPAGATION` | Does the effect spread? Through what medium? What stops it? |
| 11 | `TRADE / RESTRICTION` | What is given up for what (binding vow / keystone shape)? |
| 12 | `IMMUNITY` | What can the system not be touched by, and what does that immunity cost? |
| 13 | `CONTROL LOOP` | What regulates it (apoptosis, recharge delay, central bank, thermostat)? |
| 14 | `ESCAPE` | How does the regulated entity evade regulation? |
| 15 | `HOST / COUPLING` | Is it dependent on another system? Extractive, neutral, or mutual? |
| 16 | `FAILURE MODE` | How does the whole thing die? |
| 17 | `COUNTERPLAY` | What beats it, and through which primitive? |

---

## Reference Node Invariants

- **Fire:** Self-sustaining exothermic oxidation (fuel + oxidizer + activation energy; consumes substrate; spreads).
- **Water:** High-heat-capacity fluid: energy sink, smotherer, solvent, conductor when impure, erosive over time.
- **Electric:** Flow of potential difference along the lowest-resistance path to ground.
- **Ground:** Charge sink and mass; absorbs, buries, grounds.
- **Ice:** Energy withdrawal into rigid crystal (rate suppression, brittle).
- **Steel:** Refined, ordered lattice: high integrity, inert, but corrodes and conducts.
- **Poison:** Cumulative toxin attacking internal machinery.
- **Psychic:** Control of the information or perception layer.
- **Ghost:** Non-physical channel that bypasses contact.
- **Dark:** Concealment and exploitation of blind spots.
- **Fairy:** Symbolic or mythic order that overrides raw power.

---

## Reference Domain: Path of Exile (PoE) Damage Types & Defenses

*(Verify patch-specific numbers before citing.)*
- **Physical:** Structural force, integrity loss.
- **Fire:** Oxidation and energy release (`ignite` = self-sustaining chain reaction over time).
- **Cold:** Energy withdrawal (`chill` and `freeze` = rate suppression).
- **Lightning:** Sudden high-potential discharge (`shock` = vulnerability amplifier).
- **Chaos:** Corruption that skips the outer buffer (ES) and hits the core (life); `poison` = cumulative stacking toxin.
- **Bleed:** Load-coupled leak (amplified damage while moving).
- **Defense layers:** Armour, evasion, Energy Shield (ES), life, typed resists (capped at 75% base), block, leech, and regeneration.

---

## 14 Seed Invariant Catalog Classes

1. **STRESS-ACCUMULATION -> THRESHOLD -> INSTANT RELEASE**
   - *Signature:* Slow loading of a locked boundary -> failure -> instant energy dump -> aftershocks.
   - *Examples:* Earthquake (fault lock -> rupture), PoE Earthquake (hit + delayed aftershock), avalanche, market crash, burnout, gradient explosion, revolution.
   - *Prediction:* Frequent small releases lower catastrophic failure risk (controlled burns, small corrections).
2. **SELF-SUSTAINING CHAIN REACTION**
   - *Signature:* Requires fuel + oxidizer + activation energy; consumes substrate; spreads to adjacent fuel; dies when any leg of the triangle is removed.
   - *Examples:* Fire, ignite, nuclear fission, viral spread, riots, runaway agent feedback loops.
3. **REGULATION ESCAPE / UNBOUNDED REPLICATION**
   - *Signature:* Unit stops obeying system stop signal, hides from surveillance, captures supply lines, colonizes remote sites.
   - *Examples:* Cancer (apoptosis lost, immune evasion, angiogenesis, metastasis), fork bomb, misaligned subagent, monopoly / regulatory capture.
4. **EXTRACTIVE COUPLING (PARASITISM)**
   - *Signature:* Draws resources from host, evades detection, often manipulates host behavior, tuned below host-kill threshold.
   - *Examples:* Parasites, Toxoplasma behavior hijack, malware, rent-seeking, leech mechanics.
5. **MUTUAL COUPLING (SYMBIOSIS)**
   - *Signature:* Each system supplies what the other lacks; both strengthen; uncoupling harms both.
   - *Examples:* Mycorrhizae, gut flora, mitochondria (absorbed symbiosis), human-AI pairing, trade.
6. **RESTRICTION-FOR-IMMUNITY TRADE**
   - *Signature:* Delete an entire vulnerability surface/pool to gain immunity, shifting all defense into a different buffer.
   - *Examples:* Chaos Inoculation (life=1, chaos immune, ES defense), Toji's Heavenly Restriction, air-gapped system, monastic vows.
   - *Prediction (shared weakness):* Anything bypassing the new buffer or halting its recharge is immediately lethal (no backup pool; confirmed by USB/insider Stuxnet defeating air gaps).
7. **BUFFER WITH RECHARGE DELAY**
   - *Signature:* Refillable shield regenerating only after a damage-free window; sustained pressure prevents recharge start.
   - *Examples:* PoE ES recharge, sleep/recovery, cash reserves, post-rate-limit cooldown.
8. **TYPED FILTER WITH CAP**
   - *Signature:* Channel-specific mitigation with a hard ceiling (e.g., PoE 75% resist cap).
   - *Examples:* Adaptive immune specificity, firewalls, specialized statutes, armour vs. evasion filter dichotomy.
9. **VULNERABILITY AMPLIFIER**
   - *Signature:* State that multiplies all incoming pressure/damage.
   - *Examples:* PoE Shock, compromised immune system, market panic, poisoned context preceding jailbreak.
10. **RATE SUPPRESSION**
    - *Signature:* Cuts action speed rather than directly draining pool.
    - *Examples:* Chill/freeze, central-bank rate braking, sedation, API throttling.
11. **CUMULATIVE STACKING TOXIN**
    - *Signature:* Independent stacks with individual timers; drain scales with exposure count.
    - *Examples:* PoE poison stacks, Pokemon Toxic, heavy-metal bioaccumulation, technical debt.
12. **LOAD-COUPLED LEAK**
    - *Signature:* Drain accelerates while the system is active/moving.
    - *Examples:* PoE Bleed (higher damage while moving), hemorrhage under exertion, memory leak under load, attrition during expansion.
13. **ABSORB-CONVERT (EDGE INVERSION)**
    - *Signature:* Incoming attack channel is rewired to feed/heal the target instead of damaging it.
    - *Examples:* Water Absorb / Volt Absorb / Flash Fire / Sap Sipper, plants absorbing water, PoE leech & "damage taken as", adversarial attack turned into training signal.
14. **GENERATION / CONTROL CYCLES**
    - *Signature:* Closed loops where each node feeds one node and suppresses another.
    - *Examples:* Wu Xing, Fire/Water/Grass triangles, predator-prey oscillation, boom-bust cycles.

---

## All 15 Department Lenses

| # | Department | Question |
|---|---|---|
| 1 | `SUBCONSCIOUS` | What latent state or hidden accumulation exists before visible effect? |
| 2 | `INNER_MONOLOGUE` | Where is the decision point or threshold evaluation? |
| 3 | `SPEECH_OUTPUT` | What is the externally visible release or effect? |
| 4 | `STORAGE` | Which pools hold the state? |
| 5 | `SECURITY` | Which filters, barriers, and immunities exist, and what bypasses them? |
| 6 | `TELECOMMUNICATIONS` | How does the effect propagate, and through what medium? |
| 7 | `ENERGY_INTAKE` | What fuels it? What starves it? |
| 8 | `DISPLAY` | How does it appear to an observer (tells, symptoms, telegraphs)? |
| 9 | `PROCESSOR` | What computes the outcome (damage formula, causal mechanism)? |
| 10 | `REPRODUCTION` | Does it replicate or spawn copies (metastasis, spreading ignite)? |
| 11 | `DELETION` | How is it terminated (apoptosis, extinguishing, cleansing)? |
| 12 | `WASTE_REMOVAL` | What clears residue without killing the host? |
| 13 | `APPLICATION` | What function does it serve for the hosting system? |
| 14 | `RENDERING_OVERHEAD` | What does sustaining it cost (mana reservation, metabolic/regulatory overhead)? |
| 15 | `INFORMATION_DENSITY` | How finely does it discriminate targets (typed vs. untyped, targeted vs. chemo)? |
