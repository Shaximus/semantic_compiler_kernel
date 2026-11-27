# Avengers × Diablo II × Path of Exile: an Archetypal Evolution Principle map (2026-11-26d)

Source: Shax t603u (26 Nov 2026). This is material Shax supplied: he pasted it from a ChatGPT conversation, so the analysis (the tables, the matches and the invariants as phrased) was authored by that assistant, not by Shax. Relayed verbatim by Chief of Staff with the inline image embed URLs omitted. Evidence: `docs/evidence/source-2026-11-26d/` (sha256 `9ee6ad562a66d86020686f29f14bec9fd95550ae7adebdd7320f175003d654ca`).

Method: `SC-AEP-001` (read for structure, not one-to-one identity). Compiled entries: `SC-AVG-001` (this map, SILVER 0.813) and `SC-WORTHY-001` (the worthiness invariant, SILVER 0.822). Both are `PROVISIONAL_DEFAULT` and explicit-only.

## 0. Layers

| Layer | What it holds | How it is marked |
|---|---|---|
| Canon | What Blizzard's games, Grinding Gear Games' game and Marvel say | `CANON_VERIFIED` (compiler checked a primary or official page), `SECONDARY_VERIFIED` (checked against a secondary guide), `UNVERIFIED_FROM_PASTE` (not checked) |
| Tradition | Norse Thor mythology as summarized in the paste | `TRADITION_UNVERIFIED_FROM_PASTE`; not relied on |
| Interpretation | Every Avenger-to-class mapping and the structural reading | `INTERPRETIVE` / `PASTED_ASSISTANT_INTERPRETATION`; compiler grading is `COMPILER` |

The paste's source markers ("DIABLO II +1", "Fandom +1", "PoE Source +1", "ftp.blizzard.com +1", "diablo2.blizzard.com +1", "PoeFriend +1", "Marvel +1") are citation stubs from the chat interface, not verified sources. A canon claim is marked unverified-from-paste unless the compiler checked it.

None of the class mappings is an official Marvel, Blizzard or GGG classification, and nothing here claims that one franchise was derived from another. The paste says so itself: "this is a structural comparison, not a claim that Marvel characters were literally derived from Diablo II."

## 1. Core invariants (structural)

### 1.1 Worthiness invariant: capability is not legitimate authority (`SC-WORTHY-001`)

"Thor's power is not supposed to be self-authorizing. The hammer's worthiness condition separates capability from legitimate authority."

- Mjölnir's worthiness enchantment (Marvel): `UNVERIFIED_FROM_PASTE` ("Fandom +1").
- Diablo II Blessed Hammer and the Hammer of Ghrab Thaar: `CANON_VERIFIED` against The Arreat Summit, Paladin Combat Skills (classic.battle.net), which matches the Diablo II manual. The nuns who kept the relic, besieged by the undead and with no defenders, took the hammer and plunged themselves into a fiery chasm to destroy it; a force of Light struck the undead down; a well-trained Paladin taps the remnants of that released energy.
- **Correction to the paste:** the nuns destroyed the relic. They did not merely keep it from the undead. The Paladin channels its remnant energy as a summoned spinning hammer; he does not wield the Hammer of Ghrab Thaar. Legitimacy runs through sacrifice and denial of capture, not through possession of an object.
- The same Arreat Summit page gives the Paladin skill Sacrifice as a way "that he may prove himself worthy of victory": Diablo II uses worthiness language for the Paladin directly (`CANON_VERIFIED`).
- **Engineering form:** SCC-001-AC path 1, the identity fix merged in PR #95 (`docs/SCC-001-AC_ANTI_CAPTURE.md`): `FOUNDER_OVERRIDE` needs an independently verified principal credential. Authority must be independently verified, not self-asserted. Being able to send the override is not authority to use it.
- **Related but distinct:**
  - `SC-SHARD-001` (Usurped-Shard) is captured authority: authority that was never granted.
  - `SC-GUARD-001` (Guardian's Fall) is protective authority turning coercive: authority that was legitimate and then failed.
  - Worthiness is whether the holder is entitled to wield the power at all, checked before it is wielded.
  - They can co-occur. They are not merged (provisional default).

### 1.2 Specialization-gate invariant (progression)

A broad attribute foundation passes a trial and emerges as a specialized identity. In Path of Exile 1, every class shares one passive tree; the class sets the starting point and the Ascendancy options, not the skill gems; completing the Labyrinth for the first time lets a character choose one of its class's three Ascendancies. `SECONDARY_VERIFIED`: PoeFriend, "Path of Exile Classes and All 21 Ascendancies Explained" (updated 16 Nov 2026, for 3.30).

Residuals: the Ascendancy can be changed later at the altar, within the same class; Bloodline classes (since 3.27) add a second, optional Ascendancy layer. The gate is real but not irreversible, and the class itself is the one choice the altar does not undo.

### 1.3 Party-composition invariant: capability is not function, and function is not authority

"Power is not the same thing as function. Function is not the same thing as authority. Thor can be the Hammerdin without being the party leader. Strange can have extraordinary magical capability without automatically having the authority to command everyone. Tony can control battlefield infrastructure without owning the people using it."

Three forms of a distributed build:

- Diablo II: a party of recognizable class identities.
- Path of Exile: a shared passive architecture, then specialization into Ascendancies.
- The Avengers: a collective whose members keep independent abilities while combining their capabilities.

This is the worthiness invariant at party scale. Tony's line also touches `SC-SHARD-001`'s ownership confusion.

## 2. Canon layer

| Claim | Status |
|---|---|
| Diablo II: Lord of Destruction has seven classes (Amazon, Assassin, Barbarian, Druid, Necromancer, Paladin, and Sorceress); the expansion added the Assassin and the Druid | `UNVERIFIED_FROM_PASTE` ("ftp.blizzard.com +1") |
| Blizzard's class descriptions stress Paladin auras, Assassin traps, Druid summons and transformations, Necromancer dominion over life and death; the per-class signature skill lists | `UNVERIFIED_FROM_PASTE` ("diablo2.blizzard.com +1"), except Blessed Hammer and Sacrifice |
| Blessed Hammer lore (Hammer of Ghrab Thaar); Sacrifice's "prove himself worthy" | `CANON_VERIFIED` (The Arreat Summit; Diablo II manual) |
| Mjölnir's worthiness enchantment | `UNVERIFIED_FROM_PASTE` ("Fandom +1") |
| Path of Exile 1: seven classes, three Ascendancies each (table below); class sets the tree start and Ascendancy options, not the gems; the Labyrinth unlocks the Ascendancy | `SECONDARY_VERIFIED` (PoeFriend, 3.30); not checked against GGG's own site |
| Marvel's Avengers roster spans these characters and others | `UNVERIFIED_FROM_PASTE` ("Marvel +1") |

| Starting class | Attribute foundation | Three Ascendancies | Status |
|---|---|---|---|
| Marauder | Strength | Juggernaut, Berserker, Chieftain | SECONDARY_VERIFIED (PoeFriend, checked 2026-11-26 for 3.30) |
| Duelist | Strength + Dexterity | Slayer, Gladiator, Champion | SECONDARY_VERIFIED (PoeFriend, checked 2026-11-26 for 3.30) |
| Ranger | Dexterity | Deadeye, Warden, Pathfinder | SECONDARY_VERIFIED (PoeFriend, checked 2026-11-26 for 3.30) |
| Shadow | Dexterity + Intelligence | Assassin, Trickster, Saboteur | SECONDARY_VERIFIED (PoeFriend, checked 2026-11-26 for 3.30) |
| Witch | Intelligence | Occultist, Elementalist, Necromancer | SECONDARY_VERIFIED (PoeFriend, checked 2026-11-26 for 3.30) |
| Templar | Strength + Intelligence | Inquisitor, Hierophant, Guardian | SECONDARY_VERIFIED (PoeFriend, checked 2026-11-26 for 3.30) |
| Scion | Strength + Dexterity + Intelligence | Ascendant, Reliquarian, Luminary | SECONDARY_VERIFIED (PoeFriend, checked 2026-11-26 for 3.30) |

## 3. Tradition layer

The paste's Thor bullets (hammer as protection and legitimacy; thunder defending the established order; "death, sacrifice, restoration, and the continuation of a cosmic cycle ... in the wider Thor mythology") are `TRADITION_UNVERIFIED_FROM_PASTE`. Not checked against Norse sources; nothing here depends on them.

## 4. Interpretation layer

### 4.1 Thor and the Diablo II Paladin (pasted)

| Structural attribute | Thor | Diablo II Paladin | Status |
|---|---|---|---|
| Divine power | Thunder and lightning | Holy energy | INTERPRETIVE |
| Weapon | Mjölnir | Blessed Hammer | INTERPRETIVE; Blessed Hammer is a summoned skill, not an inherited weapon |
| Legitimacy | Worthiness | Faith and discipline | INTERPRETIVE; the verified lore grounds it in sacrifice and protection |
| Protective function | Defender of realms | Defender against evil | INTERPRETIVE |
| Power relationship | Wielder and enchanted vessel | Paladin channels sacred energy | INTERPRETIVE |

### 4.2 Diablo II, per Avenger

INTERPRETIVE. The pasted assistant's builds; not official Marvel or Blizzard classifications; no claim of derivation.

| Marvel character | Primary Diablo II build | Secondary tree | Why it fits (pasted) | Status |
|---|---|---|---|---|
| Thor | Paladin: Hammerdin | Sorceress, Barbarian | Blessed Hammer-style orbit, lightning, protective weapon field, melee power | INTERPRETIVE |
| Captain America | Paladin: defensive aura build | Barbarian | Leadership buffs, protection, combat mastery, rallying the party | INTERPRETIVE |
| Iron Man | Assassin: Trapsin | Sorceress | Automated weapons, remote systems, energy projectiles, tactical battlefield control | INTERPRETIVE |
| Hulk | Barbarian: Berserker | Druid: Werebear | Escalating physical force, rage, durability, transformation | INTERPRETIVE |
| Black Widow | Assassin: Martial Arts | Amazon | Precision, stealth, infiltration, disciplined close combat | INTERPRETIVE |
| Hawkeye | Amazon: Bowazon | Assassin | Ranged precision, specialized ammunition, tactical positioning | INTERPRETIVE |
| Scarlet Witch | Sorceress | Necromancer | Reality-altering magic, curses, control, manipulation of life and death | INTERPRETIVE |
| Doctor Strange | Sorceress | Paladin | Elemental and dimensional magic, shields, protective wards, teleportation | INTERPRETIVE |
| Vision | Necromancer: construct specialist | Sorceress | Artificial body, energy projection, phasing, unusual relationship between life and constructed existence | INTERPRETIVE; constructed vessel with independent agency, not equipment or a summoned minion |
| Black Panther | Assassin | Paladin | Stealth, martial arts, advanced equipment, protective responsibility | INTERPRETIVE |
| Ant-Man | Druid: Summoner | Assassin | Ant allies, size transformation, infiltration, unconventional battlefield control | INTERPRETIVE |
| Wasp | Amazon | Assassin | Aerial mobility, precision attacks, small-target agility, tactical strikes | INTERPRETIVE |
| Falcon | Amazon | Assassin | Aerial ranged combat, reconnaissance, mobility and positioning | INTERPRETIVE |
| War Machine | Amazon | Assassin: Trapsin | Ranged weapons platform, automated targeting, explosive area coverage | INTERPRETIVE |
| Winter Soldier | Barbarian | Assassin | Superhuman physical combat, weapon mastery, infiltration, close-range lethality | INTERPRETIVE |
| Spider-Man | Assassin | Amazon | Martial arts, mobility, traps and restraints, web-based battlefield control | INTERPRETIVE |
| Captain Marvel | Sorceress | Paladin | Energy projection, flight, immense elemental-like output, protective presence | INTERPRETIVE |
| Quicksilver | Barbarian: Frenzy | Assassin | Extraordinary movement speed, rapid attacks, evasive positioning | INTERPRETIVE |
| Loki | Sorceress | Assassin, Necromancer | Illusions, magic, deception, curses, manipulation and duplication | INTERPRETIVE |
| Shang-Chi | Assassin: Martial Arts | Barbarian | Charge-up and finishing-move structure, disciplined combat, weapon integration | INTERPRETIVE |
| Groot | Druid: Summoning (from the class list and section 3; no row in the pasted table) | none given | Nature-based body, regeneration and growth, organic manipulation of the environment, defensive barriers | INTERPRETIVE |

Party architecture as pasted (INTERPRETIVE): Protection, Paladin (Thor, Captain America). Force, Barbarian (Hulk, Winter Soldier). Precision, Amazon (Hawkeye, Falcon, War Machine). Control, Assassin (Black Widow, Iron Man, Spider-Man). Nature, Druid (Groot, Hulk). Life and death, Necromancer (Wanda, Vision partial). Arcane power, Sorceress (Doctor Strange, Wanda, Loki, Captain Marvel).

### 4.3 Path of Exile, per Avenger

INTERPRETIVE. The pasted assistant's builds; not official Marvel or GGG classifications; no claim of derivation.

| Avenger | PoE build (pasted) | Archetypal reasoning (pasted) | Status |
|---|---|---|---|
| Thor | Templar → Guardian / Inquisitor | Divine power, protective auras, lightning and empowered weapon attacks | INTERPRETIVE |
| Captain America | Duelist → Champion | Defensive leadership, ally protection, fortification, disciplined physical combat | INTERPRETIVE |
| Iron Man | Shadow → Saboteur | Automated weapons, traps, remote deployment, battlefield engineering | INTERPRETIVE |
| Hulk | Marauder → Berserker / Juggernaut | Rage scaling, enormous physical output, resilience and unstoppable momentum | INTERPRETIVE |
| Black Widow | Shadow → Assassin | Precision, infiltration, critical strikes and close-combat execution | INTERPRETIVE |
| Hawkeye | Ranger → Deadeye | Projectile specialization, accuracy, targeting and ranged superiority | INTERPRETIVE |
| Scarlet Witch | Witch → Occultist / Elementalist | Hexes, chaos manipulation, destructive magical forces and debuffs | INTERPRETIVE |
| Doctor Strange | Templar → Hierophant | Arcane mastery, dimensional manipulation, spell specialization and protective magic | INTERPRETIVE |
| Vision | Scion → Ascendant | Hybrid architecture, unusual energy systems, multiple capabilities in one constructed vessel | INTERPRETIVE; constructed vessel with independent agency, not equipment |
| Black Panther | Shadow → Trickster / Assassin | Mobility, evasion, precision, infiltration and advanced combat technique | INTERPRETIVE |
| Ant-Man | Ranger → Pathfinder | Mobility, unconventional positioning, resource management and adaptable tactics | INTERPRETIVE |
| Wasp | Ranger → Deadeye | Precision, aerial mobility and rapid projectile attacks | INTERPRETIVE |
| Falcon | Ranger → Warden | Aerial combat, mobility, environmental awareness and ranged support | INTERPRETIVE |
| War Machine | Shadow → Saboteur | Explosives, automated weapons, area denial and weapons-platform control | INTERPRETIVE |
| Winter Soldier | Duelist → Slayer | Superhuman physical combat, weapon specialization and relentless close-range pressure | INTERPRETIVE |
| Spider-Man | Shadow → Trickster | Evasion, mobility, traps, web control and unconventional battlefield manipulation | INTERPRETIVE |
| Captain Marvel | Templar → Inquisitor | Cosmic energy, empowered attacks, high damage and resistance penetration | INTERPRETIVE |
| Quicksilver | Ranger → Warden | Speed, evasion, rapid movement and high-tempo attacks | INTERPRETIVE |
| Loki | Shadow → Trickster | Deception, illusions, manipulation, misdirection and escape | INTERPRETIVE |
| Groot | Witch → Necromancer (adapted) | Organic constructs, regeneration, growth and battlefield support through summoned entities | NO_FORCED_MATCH: PoE 1 has no Druid starting class; the pasted 'adapted' row is an approximation the paste itself declines to force |
| Shang-Chi | Duelist → Gladiator | Martial discipline, counterattacks, weapon mastery and technical combat | INTERPRETIVE |

Distributed-build roles as pasted (INTERPRETIVE):

| System function | Avenger | PoE role | Status |
|---|---|---|---|
| Defensive aura | Captain America | Champion | INTERPRETIVE |
| Offensive aura | Thor | Inquisitor | INTERPRETIVE |
| Automated infrastructure | Iron Man | Saboteur | INTERPRETIVE |
| Frontline durability | Hulk | Juggernaut | INTERPRETIVE |
| Precision targeting | Hawkeye | Deadeye | INTERPRETIVE |
| Information manipulation | Loki | Trickster | INTERPRETIVE |
| Magical control | Scarlet Witch | Occultist | INTERPRETIVE |
| Spatial and spell control | Doctor Strange | Hierophant | INTERPRETIVE |
| Hybrid integration | Vision | Ascendant | INTERPRETIVE |

Thor's two Ascendancy expressions as pasted: "Guardian Thor protects the realm; Inquisitor Thor destroys what threatens it."

### 4.4 Groot: an honest no-forced-match

PoE 1 has no Druid starting class; none of the seven classes in section 2 is a Druid. The paste says Groot's organic construction and regeneration "are not perfectly represented by Necromancer" and "I wouldn't force a perfect match where the game doesn't provide one," yet its own table lists "Witch → Necromancer (adapted)". The compiler records Groot as **NO_FORCED_MATCH** in the PoE layer and keeps the adapted row only as the paste's approximation of the summoned-entity side. His Diablo II Druid match ("one of the cleanest Druid matches") stands as interpretive.

### 4.5 Vision: a constructed vessel with independent agency

Vision is a constructed vessel with independent agency. He is not equipment and not a summoned minion: "a constructed being with independent agency is not merely equipment." He is a partial Necromancer construct parallel in Diablo II, and a Scion → Ascendant candidate in PoE because his build spans all three attributes. The Scion's central start on the tree is the analogy, not an identity claim. Residual: Necromancer golems are minions without agency; Vision is not.

## 5. Open extensions (not done)

- **Villain roster.** Thanos, Loki, Ultron, Hela, Dormammu, Kang and the Celestials against Diablo's corrupted classes, demons, bosses and Prime Evils. NOT DONE.
- **Nephilim collective structure.** How the seven class archetypes combine into a collective system (hybrids, summons, party buffs, shared resources, resurrection mechanics). NOT DONE. `SC-NEPH-001` is named in an earlier source and is not in this repository; it stays unresolved and is not stubbed.

## 6. Grade

Graded by rule: GOLD needs a composite of at least 0.9 and every gate at least 0.8. No gate is above 0.9, because nothing was prediction-tested.

| Entry | Tier | Composite | Min gate | Why not higher |
|---|---|---|---|---|
| `SC-AVG-001` | SILVER | 0.813 | 0.7 (corpus_completeness) | Heroes only; villain roster and Nephilim structure not done; Diablo II roster unverified; per-Avenger rows are interpretive and unscored |
| `SC-WORTHY-001` | SILVER | 0.822 | 0.72 (corpus_completeness) | One verified worked case (Ghrab Thaar); Mjölnir and the Norse tradition unverified; no wider survey |

## 7. Provisional defaults

See `docs/PENDING_DELIBERATION.md`, sections `SC-AVG-001` and `SC-WORTHY-001`.

- `SC-AVG-001`: Groot is NO_FORCED_MATCH in the PoE layer; the specialization-gate and party-composition invariants are readings under `SC-AEP-001`, not invariant classes.
- `SC-WORTHY-001`: worthiness is a separate reading under `SC-AEP-001`, related to but not merged into `SC-SHARD-001` or `SC-GUARD-001`, and not an invariant class.

## 8. Routing

Both IDs are in `EXPLICIT_ONLY_ENTRY_HINTS`. Everyday and gaming words ("Avengers", "hammer", "paladin", "class", "party", "worthy", "build") do not lift `soul_bomb_sovereignty`. Explicit IDs route home. Naming either ID sets `needs_review`.

## 9. Privacy

The source covers fiction, game systems and a design principle. It was checked for emails, phone numbers, addresses, financial details, credentials and family information; none were found. No personal details are recorded here or in the entries.
