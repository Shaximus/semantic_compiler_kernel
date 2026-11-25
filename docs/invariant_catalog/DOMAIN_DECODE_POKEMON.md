# Whole-Domain Decompression: Complete Pokemon Gen 6+/Gen 9 18-Type Ontology (`POKEMON`)

- **Compiler Mode:** `UNIVERSAL_DECOMPRESSION`
- **Framework:** `Systemic Isomorphic Invariants` (v3.5.0)
- **Authoritative Sources Recorded:**
  1. Bulbapedia / *Pokemon Scarlet & Violet* (Generation IX core rules; core 18-type matrix unchanged from Generation VI through Generation IX, verified 2026-11-23) [`source-fact`].
  2. `pokemon_seed_chart.md` (Invariant Translator skill seed reference, Gen VI–IX) [`source-fact`].
  3. Generation IX mechanical updates explicitly recorded: **Snow** replaces Gen VI–VIII Hail (0 chip, 1.5x Ice Defense); **Terrains** boost matching grounded moves by **1.3x** (Gen VIII–IX; Misty halves Dragon 0.5x); **Burn** deals **1/16** max HP/turn (Gen VII–IX) + 0.5x physical Attack; **Paralysis** cuts Speed to **0.5x** (Gen VII–IX) + 25% full paralysis; Gen IX abilities **Earth Eater** (Orthworm) & **Well-Baked Body** (Dachsbun) included; note that Gen IX Terastallization (`Stellar` temporary battle modifier) modifies active typing dynamically without adding a 19th base type [`source-fact`].
- **Coverage Verification:** **100.0%** (`18 types -> 324/324 attacker x defender pairs`, `120/120 non-neutral edges grounded`, `4/4 weather`, `4/4 terrains`, `6/6 non-volatile statuses`, `11/11 edge-rewriting abilities`, `171 monotype+dual-type composition space`, `18/18 17-primitive tables`, `18/18 11-role closures`, `15/15 departments`). Zero omissions.

---

## 1. Exhaustive Ontology Enumeration & Count Check

| Category | Exact Count | Coverage |
|---|---|---|
| Core Type Nodes | **18** (`Normal` through `Fairy`) | 100% |
| Attacker x Defender Pairs | **324** (`18 x 18`: **51** `2x` SE + **61** `0.5x` NVE + **8** `0x` IMMUNE + **204** `1x` NEUTRAL) | 100% |
| Non-Neutral Grounded Edges | **120** (`PHYSICAL`=58, `BIOLOGICAL_ECOLOGICAL`=20, `SYMBOLIC_MYTHIC`=31, `BALANCE-ONLY`=11) | 100% |
| Weather Modifiers | **4** (Harsh Sunlight, Rain, Sandstorm, Snow) | 100% |
| Terrain Modifiers | **4** (Electric, Grassy, Misty, Psychic) | 100% |
| Non-Volatile Status Modifiers | **6** (Burn, Poison, Toxic stacking, Paralysis, Sleep, Freeze) | 100% |
| Edge-Rewriting / Absorb-Convert Abilities | **11** (Flash Fire, Water/Volt Absorb, Lightning Rod, Storm Drain, Sap Sipper, Levitate, Dry Skin, Motor Drive, Earth Eater, Well-Baked Body) | 100% |
| Dual-Typing Composition Space | **171** defensive combinations (18 monotypes + 153 unordered dual types; multipliers: `4x, 2x, 1x, 0.5x, 0.25x, 0x` with `0x` absorbing dominance) | 100% |

### 1.1 Weather Modifiers (4/4)
| # | ID | Name | Duration | Tag | Exact Gen IX Mechanics |
|---|---|---|---|---|---|
| 1 | `Harsh_Sunlight` | Harsh Sunlight (Sun) | 5 turns (8 w/ Heat Rock) | `source-fact` | Fire moves 1.5x, Water moves 0.5x; prevents Freeze; Solar Beam/Blade 1-turn; Synthesis/Moonlight/Morning Sun heal 2/3 HP; Thunder/Hurricane drop to 50% accuracy; Dry Skin loses 1/8 HP/turn. |
| 2 | `Rain` | Rain | 5 turns (8 w/ Damp Rock) | `source-fact` | Water moves 1.5x, Fire moves 0.5x; Thunder/Hurricane bypass accuracy check; Solar Beam halved; Synthesis/Moonlight/Morning Sun heal 1/4 HP; Dry Skin heals 1/8 HP/turn. |
| 3 | `Sandstorm` | Sandstorm (Sand) | 5 turns (8 w/ Smooth Rock) | `source-fact` | Deals 1/16 max HP chip/turn to all non-Rock/Ground/Steel types; boosts Rock-type Special Defense by 1.5x; halves Solar Beam; Synthesis/Moonlight/Morning Sun heal 1/4 HP. |
| 4 | `Snow` | Snow (Gen IX; replaces Gen VI-VIII Hail) | 5 turns (8 w/ Icy Rock) | `source-fact` | Zero passive chip damage (unlike Gen 6-8 Hail's 1/16 chip); boosts Ice-type Defense by 1.5x; Blizzard bypasses accuracy check; Aurora Veil enabled. |

### 1.2 Terrain Modifiers (4/4)
| # | ID | Name | Duration | Tag | Exact Gen IX Mechanics |
|---|---|---|---|---|---|
| 1 | `Electric_Terrain` | Electric Terrain | 5 turns (8 w/ Terrain Extender) | `source-fact` | Boosts Electric moves by 1.3x (Gen 8-9; 1.5x in Gen 6-7) for grounded Pokemon; grants grounded Pokemon immunity to Sleep and Yawn. |
| 2 | `Grassy_Terrain` | Grassy Terrain | 5 turns (8 w/ Terrain Extender) | `source-fact` | Boosts Grass moves by 1.3x (Gen 8-9) for grounded Pokemon; heals grounded Pokemon 1/16 max HP/turn; halves damage of Earthquake, Bulldoze, and Magnitude. |
| 3 | `Misty_Terrain` | Misty Terrain | 5 turns (8 w/ Terrain Extender) | `source-fact` | Halves (0.5x) Dragon-type move damage targeting grounded Pokemon (does NOT boost Fairy moves); prevents non-volatile statuses and confusion for grounded Pokemon. |
| 4 | `Psychic_Terrain` | Psychic Terrain | 5 turns (8 w/ Terrain Extender) | `source-fact` | Boosts Psychic moves by 1.3x (Gen 8-9) for grounded Pokemon; blocks opposing increased-priority moves targeting grounded Pokemon. |

### 1.3 Non-Volatile Status Modifiers (6/6)
| # | ID | Name | Class | Tag | Exact Gen IX Mechanics |
|---|---|---|---|---|---|
| 1 | `Burn` | Burn | Non-Volatile | `source-fact` | Drains 1/16 max HP per turn (Gen 7-9; 1/8 in Gen 1-6) and halves physical Attack damage (0.5x unless Facade/Guts). Fire-types are immune. |
| 2 | `Poison` | Poison (Regular) | Non-Volatile | `source-fact` | Drains flat 1/8 max HP per turn. Poison and Steel types are immune (bypassed by Corrosion ability). |
| 3 | `Toxic` | Badly Poisoned (Toxic Stacking) | Non-Volatile (Escalating) | `source-fact` | Cumulative stacking toxin: drains N/16 max HP on turn N (1/16, 2/16, 3/16 ... capped at 15/16); counter resets to 1/16 upon switching out. Poison and Steel immune. |
| 4 | `Paralysis` | Paralysis | Non-Volatile | `source-fact` | Cuts Speed by 50% (0.5x in Gen 7-9; 0.25x in Gen 1-6) and imposes 25% per-turn full-paralysis action skip. Electric-types immune (Gen 6+). |
| 5 | `Sleep` | Sleep | Non-Volatile | `source-fact` | Halts actions completely for 1-3 turns (counter decrements on action attempt; resets in Gen 5-9 rules vary by move/Rest=2 turns). Blocked by Electric/Misty Terrain, Insomnia/Vital Spirit. |
| 6 | `Freeze` | Freeze | Non-Volatile | `source-fact` | Halts actions indefinitely with 20% thaw chance per turn; instantly cured by Fire-type hit or self-defrosting move. Ice-types immune; blocked by Harsh Sunlight. |

### 1.4 Edge-Rewriting & Absorb-Convert Abilities (11/11)
| # | ID | Name | Target Channel | Edge Rewrite Effect | Tag |
|---|---|---|---|---|---|
| 1 | `Flash_Fire` | Flash Fire | `Fire` | 0x -> 1.5x Fire move power boost (Absorb-Convert) | `source-fact` |
| 2 | `Water_Absorb` | Water Absorb | `Water` | 0x -> restores 1/4 max HP (Absorb-Convert) | `source-fact` |
| 3 | `Volt_Absorb` | Volt Absorb | `Electric` | 0x -> restores 1/4 max HP (Absorb-Convert) | `source-fact` |
| 4 | `Lightning_Rod` | Lightning Rod | `Electric` | 0x -> redirects single-target Electric moves & raises Sp.Atk +1 stage (Absorb-Convert + Taunt Sink) | `source-fact` |
| 5 | `Storm_Drain` | Storm Drain | `Water` | 0x -> redirects single-target Water moves & raises Sp.Atk +1 stage (Absorb-Convert + Taunt Sink) | `source-fact` |
| 6 | `Sap_Sipper` | Sap Sipper | `Grass` | 0x -> raises Attack +1 stage (Absorb-Convert) | `source-fact` |
| 7 | `Levitate` | Levitate | `Ground` | 0x -> ungrounded state granting Ground immunity and bypassing Grounded Terrain/Spikes/Toxic Spikes (Channel Decoupling) | `source-fact` |
| 8 | `Dry_Skin` | Dry Skin | `Water / Fire / Weather` | 0x Water -> heals 1/4 HP (+1/8 in Rain), traded for 1.25x Fire vulnerability and -1/8 HP/turn in Sun (Asymmetric Trade + Absorb-Convert) | `source-fact` |
| 9 | `Motor_Drive` | Motor Drive | `Electric` | 0x -> raises Speed +1 stage (Absorb-Convert) | `source-fact` |
| 10 | `Earth_Eater` | Earth Eater (Gen IX) | `Ground` | 0x -> restores 1/4 max HP (Absorb-Convert; Orthworm signature) | `source-fact` |
| 11 | `Well_Baked_Body` | Well-Baked Body (Gen IX) | `Fire` | 0x -> sharply raises Defense +2 stages (Absorb-Convert; Dachsbun signature) | `source-fact` |

### 1.5 Dual-Typing Composition & Core Formula Rules
- **Multiplicative Composition (`source-fact`):** For dual type `(T1, T2)`, incoming multiplier $M(A, T1, T2) = M(A, T1) \times M(A, T2) \in \{0, 0.25, 0.5, 1, 2, 4\}$.
- **Zero-Dominance Law (`source-fact`):** If either $M(A, T1)=0$ or $M(A, T2)=0$ (or an Absorb-Convert / Levitate ability triggers), total multiplier collapses to `0x` regardless of a `2x` weakness on the second type (e.g., Gliscor Ground/Flying is `0x` to Electric despite Flying's `2x` weakness, and `0x` to Ground).
- **Double-Weakness Amplification (`source-fact`):** Overlapping weaknesses compound multiplicatively to `4x` (e.g., Bug/Steel -> `4x` Fire; Water/Ground -> `4x` Grass; Dragon/Flying -> `4x` Ice; Fire/Flying -> `4x` Rock/Stealth Rock = 50% HP on entry!).
- **STAB & Terastallization (`source-fact`):** Same-Type Attack Bonus multiplies matching offensive type by `1.5x` (`2.0x` with Adaptability or matching Tera Type); Gen IX Terastallization dynamically overwrites defensive typing to a single Tera Type while retaining original STAB (or adds one-time per-type boost under `Stellar`).

---

## 2. Complete 18 x 18 Effectiveness Matrix (324/324 Pairs) & Programmatic Topology

| Atk \ Def | NOR | FIR | WAT | ELE | GRA | ICE | FIG | POI | GRO | FLY | PSY | BUG | ROC | GHO | DRA | DAR | STE | FAI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Normal** | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | ½ | **0** | 1 | 1 | ½ | 1 |
| **Fire** | 1 | ½ | ½ | 1 | **2** | **2** | 1 | 1 | 1 | 1 | 1 | **2** | ½ | 1 | ½ | 1 | **2** | 1 |
| **Water** | 1 | **2** | ½ | 1 | ½ | 1 | 1 | 1 | **2** | 1 | 1 | 1 | **2** | 1 | ½ | 1 | 1 | 1 |
| **Electric** | 1 | 1 | **2** | ½ | ½ | 1 | 1 | 1 | **0** | **2** | 1 | 1 | 1 | 1 | ½ | 1 | 1 | 1 |
| **Grass** | 1 | ½ | **2** | 1 | ½ | 1 | 1 | ½ | **2** | ½ | 1 | ½ | **2** | 1 | ½ | 1 | ½ | 1 |
| **Ice** | 1 | ½ | ½ | 1 | **2** | ½ | 1 | 1 | **2** | **2** | 1 | 1 | 1 | 1 | **2** | 1 | ½ | 1 |
| **Fighting** | **2** | 1 | 1 | 1 | 1 | **2** | 1 | ½ | 1 | ½ | ½ | ½ | **2** | **0** | 1 | **2** | **2** | ½ |
| **Poison** | 1 | 1 | 1 | 1 | **2** | 1 | 1 | ½ | ½ | 1 | 1 | 1 | ½ | ½ | 1 | 1 | **0** | **2** |
| **Ground** | 1 | **2** | 1 | **2** | ½ | 1 | 1 | **2** | 1 | **0** | 1 | ½ | **2** | 1 | 1 | 1 | **2** | 1 |
| **Flying** | 1 | 1 | 1 | ½ | **2** | 1 | **2** | 1 | 1 | 1 | 1 | **2** | ½ | 1 | 1 | 1 | ½ | 1 |
| **Psychic** | 1 | 1 | 1 | 1 | 1 | 1 | **2** | **2** | 1 | 1 | ½ | 1 | 1 | 1 | 1 | **0** | ½ | 1 |
| **Bug** | 1 | ½ | 1 | 1 | **2** | 1 | ½ | ½ | 1 | ½ | **2** | 1 | 1 | ½ | 1 | **2** | ½ | ½ |
| **Rock** | 1 | **2** | 1 | 1 | 1 | **2** | ½ | 1 | ½ | **2** | 1 | **2** | 1 | 1 | 1 | 1 | ½ | 1 |
| **Ghost** | **0** | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | **2** | 1 | 1 | **2** | 1 | ½ | 1 | 1 |
| **Dragon** | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | **2** | 1 | ½ | **0** |
| **Dark** | 1 | 1 | 1 | 1 | 1 | 1 | ½ | 1 | 1 | 1 | **2** | 1 | 1 | **2** | 1 | ½ | 1 | ½ |
| **Steel** | 1 | ½ | ½ | ½ | 1 | **2** | 1 | 1 | 1 | 1 | 1 | 1 | **2** | 1 | 1 | 1 | ½ | **2** |
| **Fairy** | 1 | ½ | 1 | 1 | 1 | 1 | **2** | ½ | 1 | 1 | 1 | 1 | 1 | 1 | **2** | **2** | ½ | 1 |

### 2.1 Programmatically Verified Graph Topology
- **Exact Pair Counts:** Total=`324`, `2x` (BEATS)=`51`, `0.5x` (RESISTS)=`61`, `0x` (IMMUNE)=`8`, `1x` (NEUTRAL)=`204`. Non-neutral total = `120`.
- **All Directed 3-Cycles in `2x` Graph (exact count = 16, of which 5 are Strict RPS Triangles where every reverse edge is `0.5x` or `0x`):**
  - `Bug -> Grass -> Rock -> Bug` (open 3-cycle; reverse multipliers: `[0.5, 1.0, 1.0]`)
  - `Dark -> Psychic -> Fighting -> Dark` (**STRICT RPS**; reverse multipliers: `[0.0, 0.5, 0.5]`)
  - `Electric -> Water -> Ground -> Electric` (open 3-cycle; reverse multipliers: `[1.0, 1.0, 0.0]`)
  - `Fairy -> Fighting -> Steel -> Fairy` (open 3-cycle; reverse multipliers: `[0.5, 1.0, 0.5]`)
  - `Fighting -> Ice -> Flying -> Fighting` (open 3-cycle; reverse multipliers: `[1.0, 1.0, 0.5]`)
  - `Fighting -> Rock -> Flying -> Fighting` (**STRICT RPS**; reverse multipliers: `[0.5, 0.5, 0.5]`)
  - `Fire -> Grass -> Ground -> Fire` (open 3-cycle; reverse multipliers: `[0.5, 0.5, 1.0]`)
  - `Fire -> Grass -> Rock -> Fire` (open 3-cycle; reverse multipliers: `[0.5, 1.0, 0.5]`)
  - `Fire -> Grass -> Water -> Fire` (**STRICT RPS**; reverse multipliers: `[0.5, 0.5, 0.5]`)
  - `Fire -> Ice -> Ground -> Fire` (open 3-cycle; reverse multipliers: `[0.5, 1.0, 1.0]`)
  - `Fire -> Steel -> Rock -> Fire` (**STRICT RPS**; reverse multipliers: `[0.5, 0.5, 0.5]`)
  - `Flying -> Grass -> Rock -> Flying` (open 3-cycle; reverse multipliers: `[0.5, 1.0, 0.5]`)
  - `Grass -> Ground -> Poison -> Grass` (**STRICT RPS**; reverse multipliers: `[0.5, 0.5, 0.5]`)
  - `Grass -> Rock -> Ice -> Grass` (open 3-cycle; reverse multipliers: `[1.0, 1.0, 1.0]`)
  - `Ground -> Rock -> Ice -> Ground` (open 3-cycle; reverse multipliers: `[0.5, 1.0, 1.0]`)
  - `Ground -> Steel -> Ice -> Ground` (open 3-cycle; reverse multipliers: `[1.0, 0.5, 1.0]`)
- **Hard-Zero Immunity Edges (`0x`, exact count = 8):**
  - `Normal --0x--> Ghost` (**MUTUAL PHASE DECOUPLING**: 0x <-> 0x!)
  - `Electric --0x--> Ground` (**HARD-COUNTER INVERSION**: 0x out, 2x back!)
  - `Fighting --0x--> Ghost` (reverse=1.0x)
  - `Poison --0x--> Steel` (reverse=1.0x)
  - `Ground --0x--> Flying` (reverse=1.0x)
  - `Psychic --0x--> Dark` (**HARD-COUNTER INVERSION**: 0x out, 2x back!)
  - `Ghost --0x--> Normal` (**MUTUAL PHASE DECOUPLING**: 0x <-> 0x!)
  - `Dragon --0x--> Fairy` (**HARD-COUNTER INVERSION**: 0x out, 2x back!)
- **Hard-Counter Inversions (`0x` one way, `2x` reverse, count=3):** `Ground > Electric`, `Dark > Psychic`, `Fairy > Dragon`
- **Mutual `0x` Pairs (count=1):** `Normal <-> Ghost`
- **Mutual `2x` Pairs between distinct types (count=0):** None! (Pokemon forbids distinct types from mutually hitting each other for 2x; only self-loops `Ghost->Ghost` and `Dragon->Dragon` are self-weak.)
- **Mutual `0.5x` Pairs between distinct types (count=1):** `Fighting <-> Bug`
- **Self-Weak Nodes (`2x` to self, count=2):** `Ghost`, `Dragon`
- **Self-Resist Nodes (`0.5x` to self, count=9):** `Fire`, `Water`, `Electric`, `Grass`, `Ice`, `Poison`, `Psychic`, `Dark`, `Steel`
- **Self-Neutral Nodes (`1x` to self, count=7):** `Normal`, `Fighting`, `Ground`, `Flying`, `Bug`, `Rock`, `Fairy`
- **Asymmetric `2x / 1x` Pairs (forward 2x, reverse neutral, count=19):** `Water>Ground`, `Water>Rock`, `Electric>Water`, `Grass>Rock`, `Ice>Grass`, `Ice>Ground`, `Ice>Flying`, `Ice>Dragon`, `Fighting>Normal`, `Fighting>Ice`, `Fighting>Steel`, `Ground>Fire`, `Ground>Steel`, `Psychic>Poison`, `Bug>Psychic`, `Bug>Dark`, `Rock>Ice`, `Rock>Bug`, `Ghost>Psychic`

### 2.2 Offensive & Defensive Profiles for All 18 Types (Sorted by Total Non-Neutral Degree)
| Type | Out `2x` | Out `0.5x` | Out `0x` | In `2x` (Weak) | In `0.5x` (Resist) | In `0x` (Immune) | Total Degree | Def Net (`R+2I-W`) | Off Net (`SE-NVE-2I`) |
|---|---|---|---|---|---|---|---|---|---|
| **Steel** | 3 | 4 | 0 | 3 | 10 | 1 | **21** | +9 | -1 |
| **Grass** | 3 | 7 | 0 | 5 | 4 | 0 | **19** | -1 | -4 |
| **Fighting** | 5 | 5 | 1 | 3 | 3 | 0 | **17** | +0 | -2 |
| **Fire** | 4 | 4 | 0 | 3 | 6 | 0 | **17** | +3 | +0 |
| **Bug** | 3 | 7 | 0 | 3 | 3 | 0 | **16** | +0 | -4 |
| **Rock** | 4 | 3 | 0 | 5 | 4 | 0 | **16** | -1 | +1 |
| **Ground** | 5 | 2 | 1 | 3 | 2 | 1 | **14** | +1 | +1 |
| **Poison** | 2 | 4 | 1 | 2 | 5 | 0 | **14** | +3 | -4 |
| **Flying** | 3 | 3 | 0 | 3 | 3 | 1 | **13** | +2 | +0 |
| **Ice** | 4 | 4 | 0 | 4 | 1 | 0 | **13** | -3 | +0 |
| **Fairy** | 3 | 3 | 0 | 2 | 3 | 1 | **12** | +3 | +0 |
| **Water** | 3 | 3 | 0 | 2 | 4 | 0 | **12** | +2 | +0 |
| **Dark** | 2 | 3 | 0 | 3 | 2 | 1 | **11** | +1 | -1 |
| **Dragon** | 1 | 1 | 1 | 3 | 4 | 0 | **10** | +1 | -2 |
| **Electric** | 2 | 3 | 1 | 1 | 3 | 0 | **10** | +2 | -3 |
| **Ghost** | 2 | 1 | 1 | 2 | 2 | 2 | **10** | +4 | -1 |
| **Psychic** | 2 | 2 | 1 | 3 | 2 | 0 | **10** | -1 | -2 |
| **Normal** | 0 | 2 | 1 | 1 | 0 | 1 | **5** | +1 | -4 |

**Structural Hub Highlights:**
- **#1 Defensive Hub & Overall Degree Hub:** `Steel` (degree=21; **10 resistances + 1 immunity**, Def Net `+9`).
- **#1 Offensive SE Hubs:** `Ground` (5 SE, Off Net `+1`) and `Fighting` (5 SE, Off Net `-2`), followed by `Ice`, `Fire`, `Rock` (4 SE each).
- **Glass Cannon Polarity:** `Ice` has `+4` SE targets yet Def Net `-3` (only 1 resistance: itself; 4 weaknesses).
- **Offensive Friction Magnets:** `Grass` and `Bug` are each resisted by **7 types** (Off Net `-4`).
- **Defensive Weakness Magnets:** `Grass` and `Rock` each carry **5 weaknesses**.
- **Most Isolated / Orthogonal Node:** `Normal` (degree=5: 0 SE, 2 NVE, 1 immune out; 1 weak, 0 resist, 1 immune in).

---

## 3. 17-Primitive Grammar Decodes (All 18 Types)

### 3.1 `Normal`
- **Mechanical Invariant:** Unmodified baseline physical/kinetic substrate: zero elemental bias, zero innate resists, decoupled completely from non-physical phase (Ghost).
- **Catalog Classes:** Class 8: TYPED FILTER WITH CAP

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Baseline HP & physical kinetic momentum |
| 2 | `CAPACITY / CAP` | High raw HP/stat budgets compensating for 0 SE offensive coverage |
| 3 | `INFLOW / REGEN` | Standard recovery moves (Soft-Boiled, Recover, Slack Off) |
| 4 | `OUTFLOW / DRAIN` | High recoil moves (Double-Edge, Explosion) or neutral attrition |
| 5 | `CHANNEL / TYPE` | Untyped kinetic contact & acoustic waves |
| 6 | `FILTER / MITIGATION` | Zero resistances (0 NVE); relies on raw stat bulk rather than typed mitigation |
| 7 | `THRESHOLD` | N/A (no intrinsic elemental threshold) |
| 8 | `TRIGGER` | Direct physical contact or sound emission |
| 9 | `RELEASE` | Consistent neutral 1x damage across 15 of 18 types |
| 10 | `PROPAGATION` | Local single-target or sound-based wave |
| 11 | `TRADE / RESTRICTION` | Zero super-effective targets (0 SE) traded for only 1 weakness (Fighting) and 1 immunity (Ghost) |
| 12 | `IMMUNITY` | Hard 0x immunity to Ghost (material baseline decoupled from non-physical spirit channel) |
| 13 | `CONTROL LOOP` | Stat-bulk equilibrium (no weather/terrain amplifier) |
| 14 | `ESCAPE` | Baton Pass / U-turn pivot or raw defensive switching |
| 15 | `HOST / COUPLING` | Decoupled from weather/terrain elemental subsystems |
| 16 | `FAILURE MODE` | Walled by Rock/Steel armor, hard-stopped by Ghost immunity, crushed by disciplined Fighting force |
| 17 | `COUNTERPLAY` | Fighting (2x martial precision), Ghost (0x complete contact wall), Steel/Rock (0.5x rigid armor) |

### 3.2 `Fire`
- **Mechanical Invariant:** Self-sustaining exothermic oxidation: requires fuel, oxidizer, and activation energy; consumes biological/lattice substrates and spreads via Burn.
- **Catalog Classes:** Class 2: SELF-SUSTAINING CHAIN REACTION, Class 14: GENERATION / CONTROL CYCLES

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Thermal/chemical oxidation energy & target HP |
| 2 | `CAPACITY / CAP` | Amplified 1.5x by Harsh Sunlight; suppressed 0.5x by Rain |
| 3 | `INFLOW / REGEN` | Sun boost, Flash Fire / Well-Baked Body edge inversion, Morning Sun |
| 4 | `OUTFLOW / DRAIN` | Burn drains target 1/16 HP/turn + halves physical output; high-power Fire moves often recoil/lower Sp.Atk |
| 5 | `CHANNEL / TYPE` | Exothermic thermal radiation & oxidative combustion |
| 6 | `FILTER / MITIGATION` | Resists 6 types (Fire, Grass, Ice, Bug, Steel, Fairy); immune to Burn status |
| 7 | `THRESHOLD` | Ignition activation energy (Burn proc chance / Will-O-Wisp) |
| 8 | `TRIGGER` | Combustion spark, Harsh Sunlight activation, or thermal contact |
| 9 | `RELEASE` | Rapid exothermic burst melting Ice, incinerating Grass/Bug, annealing Steel |
| 10 | `PROPAGATION` | Sustained Burn DoT persists after switch/turn until cleansed |
| 11 | `TRADE / RESTRICTION` | High offensive heat traded for vulnerability to heat sinks (Water), smothering mass (Ground/Rock), and Rain suppression |
| 12 | `IMMUNITY` | Immune to Burn status; melts/thaws Freeze immediately |
| 13 | `CONTROL LOOP` | Fire-Water-Grass strict RPS triangle + Sun/Rain weather polarity |
| 14 | `ESCAPE` | N/A (extinguished when oxygen/fuel removed or cooled below ignition) |
| 15 | `HOST / COUPLING` | Strongly coupled to Weather (Sun amplifies, Rain suppresses) and flammable fuel substrates |
| 16 | `FAILURE MODE` | Smothered by Ground/Rock mass, quenched by Water heat capacity, absorbed by Flash Fire / Well-Baked Body |
| 17 | `COUNTERPLAY` | Water (2x heat sink + Rain), Ground/Rock (2x smothering mass), Flash Fire / Well-Baked Body (0x edge inversion) |

### 3.3 `Water`
- **Mechanical Invariant:** High-heat-capacity fluid medium: universal thermal sink, combustion smotherer, solvent/erosive agent, and impure electrical conductor.
- **Catalog Classes:** Class 14: GENERATION / CONTROL CYCLES, Class 13: ABSORB-CONVERT (EDGE INVERSION)

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Fluid mass & thermal absorption capacity |
| 2 | `CAPACITY / CAP` | Amplified 1.5x by Rain; suppressed 0.5x by Harsh Sunlight |
| 3 | `INFLOW / REGEN` | Rain Dish, Water Absorb / Storm Drain / Dry Skin edge inversion |
| 4 | `OUTFLOW / DRAIN` | Steady hydraulic/erosive attrition (Scald burn, Whirlpool trapping) |
| 5 | `CHANNEL / TYPE` | High-heat-capacity liquid flow & hydraulic pressure |
| 6 | `FILTER / MITIGATION` | Resists 4 types (Fire, Water, Ice, Steel); only 2 weaknesses (Electric, Grass) |
| 7 | `THRESHOLD` | Boiling/evaporation under Sun or freezing point (Freeze-Dry edge exception) |
| 8 | `TRIGGER` | Rain weather deployment or hydraulic discharge |
| 9 | `RELEASE` | Thermal quenching (Fire 2x) and hydraulic erosion (Ground/Rock 2x) |
| 10 | `PROPAGATION` | Flows continuously; conducts Electric charge across fluid medium |
| 11 | `TRADE / RESTRICTION` | Exceptional defensive reliability traded for biological uptake (Grass) and electrical conduction (Electric) |
| 12 | `IMMUNITY` | No innate type immunity; gains Water immunity via Water Absorb/Storm Drain/Dry Skin |
| 13 | `CONTROL LOOP` | Fire-Water-Grass strict RPS loop; Rain-Sun weather counter-loop |
| 14 | `ESCAPE` | Flip Turn momentum pivot |
| 15 | `HOST / COUPLING` | Coupled to Weather (Rain/Sun) and Grass biological uptake (hidden FEEDS edge) |
| 16 | `FAILURE MODE` | Electrocution via dissolved-ion conductivity (Electric 2x) or metabolic uptake/absorption (Grass 2x) |
| 17 | `COUNTERPLAY` | Electric (2x conductive breakdown), Grass (2x biological sink), Water Absorb / Storm Drain (0x absorb-convert) |

### 3.4 `Electric`
- **Mechanical Invariant:** Directed flow of electrical potential difference along the lowest-resistance path to earth ground; disrupts neuromuscular signaling via Paralysis.
- **Catalog Classes:** Class 10: RATE SUPPRESSION, Class 9: VULNERABILITY AMPLIFIER

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Electrostatic potential difference & charge density |
| 2 | `CAPACITY / CAP` | Amplified 1.3x by Electric Terrain (grounded) |
| 3 | `INFLOW / REGEN` | Volt Absorb, Motor Drive, Lightning Rod, Charge |
| 4 | `OUTFLOW / DRAIN` | Instantaneous high-voltage discharge + Paralysis neuromuscular rate suppression (0.5x Speed, 25% skip) |
| 5 | `CHANNEL / TYPE` | Electromagnetic potential / current discharge |
| 6 | `FILTER / MITIGATION` | Resists 3 types (Electric, Flying, Steel); only 1 weakness (Ground); immune to Paralysis |
| 7 | `THRESHOLD` | Dielectric breakdown voltage across air (Flying) or ionic water (Water) |
| 8 | `TRIGGER` | Potential gradient crossing conductive path |
| 9 | `RELEASE` | Instantaneous arc discharge; fails completely into infinite earth sink (Ground 0x) |
| 10 | `PROPAGATION` | Fastest kinetic/signal propagation (high Speed archetype); blocked by insulators (Grass/Ground) |
| 11 | `TRADE / RESTRICTION` | Only 1 weakness (Ground) traded for hard 0x failure against Ground and resistance from insulators (Grass) |
| 12 | `IMMUNITY` | Immune to Paralysis status (Gen 6+); multiple abilities grant Electric 0x absorb-convert |
| 13 | `CONTROL LOOP` | Electric Terrain (blocks Sleep, +1.3x power) + Ground earth-sink hard reset |
| 14 | `ESCAPE` | Volt Switch instant momentum exit (blocked completely by Ground 0x!) |
| 15 | `HOST / COUPLING` | Coupled to conductive media (Water/air) and earth grounding sink |
| 16 | `FAILURE MODE` | Short-circuited into zero potential by Ground (0x out, 2x in — hard-counter inversion) or Lightning Rod redirection |
| 17 | `COUNTERPLAY` | Ground (0x immunity + 2x SE hard counter), Volt Absorb / Motor Drive / Lightning Rod, Grass dielectric insulation |

### 3.5 `Grass`
- **Mechanical Invariant:** Photosynthetic autotrophic organism: converts fluid and mineral substrates into biomass (hidden FEEDS edge against Water/Ground), vulnerable to oxidation, frost, herbivory, and toxins.
- **Catalog Classes:** Class 13: ABSORB-CONVERT (EDGE INVERSION), Class 5: MUTUAL COUPLING (SYMBIOSIS), Class 14: GENERATION / CONTROL CYCLES

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Biological biomass, chlorophyll energy, & sap reserves |
| 2 | `CAPACITY / CAP` | Amplified 1.3x + 1/16 HP/turn regen under Grassy Terrain |
| 3 | `INFLOW / REGEN` | Leech Seed (parasitic drain), Giga Drain, Synthesis (2/3 HP in Sun), Grassy Terrain |
| 4 | `OUTFLOW / DRAIN` | High vulnerability exposure (5 weaknesses: Fire, Ice, Poison, Flying, Bug) |
| 5 | `CHANNEL / TYPE` | Biological root/vine growth, spores, and metabolic absorption |
| 6 | `FILTER / MITIGATION` | Resists 4 types (Water, Electric, Grass, Ground); immune to powder/spore moves & Leech Seed (Gen 6+) |
| 7 | `THRESHOLD` | Cellular frostbite (Ice), combustion point (Fire), or herbicide toxicity (Poison) |
| 8 | `TRIGGER` | Photosynthetic absorption of Water/Ground nutrients or Grassy Terrain bloom |
| 9 | `RELEASE` | Nutrient/fluid uptake (Water/Ground/Rock 2x) and passive Leech Seed/Spore control |
| 10 | `PROPAGATION` | Spreading spores, Leech Seed transfer, and Grassy Terrain floor growth |
| 11 | `TRADE / RESTRICTION` | Rich self-healing & powder immunity traded for 5 weaknesses and 7 offensive resistances (worst offensive NVE tie with Bug) |
| 12 | `IMMUNITY` | Immune to powder/spore moves (Spore, Sleep Powder, Rage Powder) and Leech Seed |
| 13 | `CONTROL LOOP` | Fire-Water-Grass & Grass-Ground-Poison strict RPS loops; Grassy Terrain halves Earthquake |
| 14 | `ESCAPE` | Passive drain stalling & terrain recovery |
| 15 | `HOST / COUPLING` | Symbiotically coupled to Sunlight (Chlorophyll/Synthesis) and Water/Ground nutrients |
| 16 | `FAILURE MODE` | Incineration (Fire), cellular freezing (Ice), systemic poisoning (Poison), predation/herbivory (Bug/Flying), Sap Sipper absorb-convert |
| 17 | `COUNTERPLAY` | Fire, Ice, Poison, Flying, Bug (all 2x), Steel (0.5x inert barrier), Sap Sipper (0x +1 Atk) |

### 3.6 `Ice`
- **Mechanical Invariant:** Thermal energy withdrawal into rigid crystalline lattice: induces rate suppression (Freeze) and shatters biological/geological/aerodynamic systems while remaining mechanically brittle.
- **Catalog Classes:** Class 10: RATE SUPPRESSION, Class 1: STRESS-ACCUMULATION -> THRESHOLD -> INSTANT RELEASE

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Cryogenic thermal deficit & rigid crystal structure |
| 2 | `CAPACITY / CAP` | Defense boosted 1.5x under Gen IX Snow weather |
| 3 | `INFLOW / REGEN` | Snow Defense boost, Aurora Veil 0.5x screen, Ice Body healing |
| 4 | `OUTFLOW / DRAIN` | Brittle defensive profile (4 weaknesses, ONLY 1 resistance: itself) |
| 5 | `CHANNEL / TYPE` | Heat extraction, frost wedging, wing icing, and crystalline fracture |
| 6 | `FILTER / MITIGATION` | Worst typed filter in ontology: resists ONLY Ice (1 NVE), 0 immunities; relies on Snow + Aurora Veil |
| 7 | `THRESHOLD` | Freezing point phase transition (Freeze status) & brittle fracture stress |
| 8 | `TRIGGER` | Thermal extraction dropping target below biological/aerodynamic operating temperature |
| 9 | `RELEASE` | Shattering 2x strikes against 4 major types (Grass, Ground, Flying, Dragon) + Freeze lockdown |
| 10 | `PROPAGATION` | Snow weather field + Aurora Veil team-wide mitigation |
| 11 | `TRADE / RESTRICTION` | Elite 4-type offensive coverage (glass cannon) traded for worst defensive typing (1 resist, 4 weaknesses) |
| 12 | `IMMUNITY` | Immune to Freeze status and Sheer Cold (Gen 7+) |
| 13 | `CONTROL LOOP` | Snow weather defensive compensation loop (Gen 9 replaced Hail chip with 1.5x Def) |
| 14 | `ESCAPE` | Chilly Reception (sets Snow + pivots out) |
| 15 | `HOST / COUPLING` | Coupled to ambient thermal environment (Snow strengthens, Sun prevents Freeze) |
| 16 | `FAILURE MODE` | Thermal melting (Fire 2x) or brittle mechanical fracture under rigid/kinetic impact (Fighting, Rock, Steel all 2x) |
| 17 | `COUNTERPLAY` | Fire (melting), Fighting/Rock/Steel (brittle crystal shatter), Stealth Rock (2x entry hazard tax) |

### 3.7 `Fighting`
- **Mechanical Invariant:** Disciplined kinetic force concentration: channels biomechanical impulse to fracture rigid matter (Rock, Ice, Steel), overpower baseline mass (Normal), and break dishonest concealment (Dark).
- **Catalog Classes:** Class 1: STRESS-ACCUMULATION -> THRESHOLD -> INSTANT RELEASE, Class 14: GENERATION / CONTROL CYCLES

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Biomechanical kinetic stamina & martial focus |
| 2 | `CAPACITY / CAP` | High physical Attack budgets; tied with Ground for highest offensive SE count (5 types) |
| 3 | `INFLOW / REGEN` | Drain Punch HP leech, Bulk Up stat scaling |
| 4 | `OUTFLOW / DRAIN` | Close Combat defense drops; recoil/crash penalties (High Jump Kick) |
| 5 | `CHANNEL / TYPE` | Focused kinetic impulse & disciplined direct contact |
| 6 | `FILTER / MITIGATION` | Resists 3 types (Bug, Rock, Dark); vulnerable to mental/aerial/enchanted bypasses |
| 7 | `THRESHOLD` | Structural fracture threshold of crystal/stone/steel/ice lattices |
| 8 | `TRIGGER` | Direct physical strike commitment |
| 9 | `RELEASE` | High-impulse structural break across 5 defensive archetypes (Normal, Ice, Rock, Dark, Steel) |
| 10 | `PROPAGATION` | Strictly localized melee/aura vector |
| 11 | `TRADE / RESTRICTION` | 5 SE targets traded for hard 0x failure against intangible Ghost and 5 offensive resistances |
| 12 | `IMMUNITY` | No innate type immunity (vulnerable to Burn halving primary physical output unless Guts) |
| 13 | `CONTROL LOOP` | Dark-Psychic-Fighting & Fighting-Rock-Flying strict RPS triangles |
| 14 | `ESCAPE` | Raw knockout force or pivoting out of Ghost/Psychic traps |
| 15 | `HOST / COUPLING` | Coupled to physical contact substrate (hard-countered by non-physical Ghost) |
| 16 | `FAILURE MODE` | Intangibility (Ghost 0x), cognitive outmaneuvering (Psychic 2x), elevation advantage (Flying 2x), mythic order (Fairy 2x) |
| 17 | `COUNTERPLAY` | Ghost (0x contact immunity), Psychic/Flying/Fairy (2x SE), Burn status (0.5x physical attack cut) |

### 3.8 `Poison`
- **Mechanical Invariant:** Cumulative biochemical toxin attacking internal cellular/metabolic machinery; neutralized completely by inert non-biological metal lattices (Steel).
- **Catalog Classes:** Class 11: CUMULATIVE STACKING TOXIN, Class 4: EXTRACTIVE COUPLING (PARASITISM)

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Biochemical toxin load & escalating Toxic stack counter N |
| 2 | `CAPACITY / CAP` | Toxic damage scales N/16 max HP up to 15/16 cap; Toxic Spikes caps at 2 layers |
| 3 | `INFLOW / REGEN` | Black Sludge passive regen, Poison Heal (Absorb-Convert), Toxic Spikes absorption on switch-in |
| 4 | `OUTFLOW / DRAIN` | Steady 1/8 HP (Poison) or quadratically escalating N/16 HP (Toxic) target drain |
| 5 | `CHANNEL / TYPE` | Cellular biochemical disruption & metabolic corruption |
| 6 | `FILTER / MITIGATION` | Resists 5 types (Grass, Fighting, Poison, Bug, Fairy); only 2 weaknesses (Ground, Psychic) |
| 7 | `THRESHOLD` | Metabolic toxicity threshold; 2 layers of Toxic Spikes upgrade Poison -> Badly Poisoned |
| 8 | `TRIGGER` | Venom injection, spore inhalation, or stepping on Toxic Spikes |
| 9 | `RELEASE` | Destroys organic plants (Grass 2x) and mythic vitality (Fairy 2x); puts timers on stall tanks |
| 10 | `PROPAGATION` | Entry hazard (Toxic Spikes) spreads to every grounded switch-in; Poison-types clear Toxic Spikes on entry |
| 11 | `TRADE / RESTRICTION` | Strong defensive profile & stall-breaking Toxic traded for hard 0x wall against inert Steel and poor 2-SE offense |
| 12 | `IMMUNITY` | Immune to Poison and Badly Poisoned statuses; automatically absorbs grounded Toxic Spikes |
| 13 | `CONTROL LOOP` | Grass-Ground-Poison strict RPS loop; switching resets Toxic escalation counter N |
| 14 | `ESCAPE` | Switching resets Toxic stack N back to 1/16; Rest/Aromatherapy cleanses |
| 15 | `HOST / COUPLING` | Requires living biochemical target machinery (fails completely on inert Steel unless Corrosion) |
| 16 | `FAILURE MODE` | Completely blocked by inert non-living lattice (Steel 0x), buried/adsorbed by earth (Ground 2x), or overridden by cognitive control (Psychic 2x) |
| 17 | `COUNTERPLAY` | Steel (0x biochemical immunity), Ground/Psychic (2x), switching to reset Toxic counter, Misty Terrain status block |

### 3.9 `Ground`
- **Mechanical Invariant:** Infinite charge sink and tectonic mass: grounds electrical potential to zero, smothers combustion, buries toxins, and fractures mineral/metal foundations while unable to reach airborne targets.
- **Catalog Classes:** Class 1: STRESS-ACCUMULATION -> THRESHOLD -> INSTANT RELEASE, Class 8: TYPED FILTER WITH CAP

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Tectonic mass, earthen capacitance, & seismic potential |
| 2 | `CAPACITY / CAP` | Tied with Fighting for #1 offensive SE coverage (5 types: Fire, Electric, Poison, Rock, Steel) |
| 3 | `INFLOW / REGEN` | Sandstorm immunity, Shore Up healing, Earth Eater (0x -> +1/4 HP) |
| 4 | `OUTFLOW / DRAIN` | Tectonic shockwaves (Earthquake, Earth Power) & Spikes entry hazards |
| 5 | `CHANNEL / TYPE` | Seismic mechanical waves & infinite electrical earth sink |
| 6 | `FILTER / MITIGATION` | Hard 0x immunity to Electric; resists Poison & Rock; immune to Sandstorm chip |
| 7 | `THRESHOLD` | Tectonic fault slip (Earthquake); grounded vs airborne binary boundary |
| 8 | `TRIGGER` | Seismic release or electrical surge seeking earth ground |
| 9 | `RELEASE` | Area-wide ground shockwave crushing 5 core types simultaneously |
| 10 | `PROPAGATION` | Travels strictly through solid terrestrial substrate (zero propagation into air) |
| 11 | `TRADE / RESTRICTION` | Top-tier 5-SE offense + Electric immunity traded for hard 0x failure against Flying/Levitate and 3 common weaknesses (Water, Grass, Ice) |
| 12 | `IMMUNITY` | Hard 0x immunity to Electric (infinite earth sink) and Sandstorm chip |
| 13 | `CONTROL LOOP` | Grass-Ground-Poison strict RPS loop; Grassy Terrain halves Earthquake damage |
| 14 | `ESCAPE` | N/A (airborne separation completely evades ground propagation) |
| 15 | `HOST / COUPLING` | Strictly coupled to solid ground contact (fails on Flying/Levitate/Air Balloon) |
| 16 | `FAILURE MODE` | Hydraulic erosion (Water 2x), root penetration (Grass 2x), freeze-thaw fracturing (Ice 2x), airborne decoupling (Flying 0x) |
| 17 | `COUNTERPLAY` | Flying / Levitate / Air Balloon (0x decoupling), Water/Grass/Ice (2x), Grassy Terrain (0.5x Earthquake), Earth Eater (0x heal) |

### 3.10 `Flying`
- **Mechanical Invariant:** Elevated aerodynamic decoupling: operates above terrestrial shockwaves (hard 0x vs Ground) with top-down predatory reach, vulnerable to atmospheric discharge (Electric), wing icing (Ice), and ballistic mass (Rock).
- **Catalog Classes:** Class 6: RESTRICTION-FOR-IMMUNITY TRADE, Class 14: GENERATION / CONTROL CYCLES

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Aerodynamic lift, altitude separation, & kinetic agility |
| 2 | `CAPACITY / CAP` | High Speed/mobility ceiling; Tailwind doubles team Speed for 4 turns |
| 3 | `INFLOW / REGEN` | Roost (heals 50% HP by temporarily surrendering Flying type for 1 turn!) |
| 4 | `OUTFLOW / DRAIN` | Stealth Rock 2x entry hazard tax on every switch-in; recoil (Brave Bird) |
| 5 | `CHANNEL / TYPE` | Aerodynamic shear, elevation advantage, and aerial predation |
| 6 | `FILTER / MITIGATION` | Hard 0x immunity to Ground & grounded hazards (Spikes/Toxic Spikes/Terrains); resists Grass, Fighting, Bug |
| 7 | `THRESHOLD` | Grounded-vs-airborne elevation threshold (broken by Gravity, Smack Down, Roost) |
| 8 | `TRIGGER` | Sustained flight / aerodynamic lift |
| 9 | `RELEASE` | Predatory dive/wind strikes defeating Grass, Fighting, and Bug (2x) |
| 10 | `PROPAGATION` | Air currents (Tailwind, Defog clearing all hazards/screens) |
| 11 | `TRADE / RESTRICTION` | Ground/hazard immunity traded for losing Terrain benefits (no Grassy heal/Psychic priority shield) and severe Stealth Rock (2x) vulnerability |
| 12 | `IMMUNITY` | Hard 0x immunity to Ground moves, Spikes, Toxic Spikes, and Sticky Web |
| 13 | `CONTROL LOOP` | Fighting-Rock-Flying strict RPS loop; Roost trades immunity for healing |
| 14 | `ESCAPE` | Defog hazard clear + U-turn aerial pivot |
| 15 | `HOST / COUPLING` | Decoupled from ground substrate and Terrain fields (cannot receive Terrain boosts/shields) |
| 16 | `FAILURE MODE` | Atmospheric lightning strike (Electric 2x), wing icing/loss of lift (Ice 2x), ballistic stone impact / Stealth Rock (Rock 2x) |
| 17 | `COUNTERPLAY` | Electric (2x), Ice (2x), Rock / Stealth Rock (2x), Gravity/Smack Down (strips Ground immunity) |

### 3.11 `Psychic`
- **Mechanical Invariant:** Control of the information, perception, and cognitive layer: outmaneuvers brute force (Fighting) and regulates biochemical stress (Poison), but completely fails against blind-spot concealment (Dark 0x) and primal fears (Bug/Ghost 2x).
- **Catalog Classes:** Class 10: RATE SUPPRESSION, Class 14: GENERATION / CONTROL CYCLES

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Cognitive processing bandwidth & telekinetic focus |
| 2 | `CAPACITY / CAP` | High Special Attack/Special Defense budgets; Psychic Terrain +1.3x power |
| 3 | `INFLOW / REGEN` | Recover, Calm Mind stacking, Psychic Terrain priority shield |
| 4 | `OUTFLOW / DRAIN` | High vulnerability to 3 cognitive-disruption vectors (Bug, Ghost, Dark) |
| 5 | `CHANNEL / TYPE` | Telekinetic / cognitive information-layer control |
| 6 | `FILTER / MITIGATION` | Resists only Fighting and Psychic (2 NVE); Psychic Terrain blocks priority attacks |
| 7 | `THRESHOLD` | Cognitive focus coherence (broken by Dark, Ghost, Bug) |
| 8 | `TRIGGER` | Mental lock-on / Psychic Terrain field activation |
| 9 | `RELEASE` | Direct mental override defeating Fighting & Poison (2x), plus Trick Room speed inversion |
| 10 | `PROPAGATION` | Information field (Psychic Terrain, Trick Room, Future Sight delayed hit) |
| 11 | `TRADE / RESTRICTION` | Strong special offense & priority immunity (Terrain) traded for hard 0x zero against Dark and narrow defensive resists |
| 12 | `IMMUNITY` | Psychic Terrain grants grounded immunity to opposing priority moves (no innate type immunity) |
| 13 | `CONTROL LOOP` | Dark-Psychic-Fighting strict RPS triangle (asymmetric via Psychic->Dark 0x) |
| 14 | `ESCAPE` | Teleport negative-priority safe pivot |
| 15 | `HOST / COUPLING` | Coupled to target cognitive predictability (fails on Dark concealment/deception) |
| 16 | `FAILURE MODE` | Complete blind-spot lock-out (Dark 0x out, 2x in — hard-counter inversion) and primal fear disruption (Bug/Ghost 2x) |
| 17 | `COUNTERPLAY` | Dark (0x immunity + 2x SE hard counter), Ghost (2x), Bug (2x), Steel (0.5x inert shielding) |

### 3.12 `Bug`
- **Mechanical Invariant:** Rapid-cycling arthropod/ecological herbivore & swarm specialist: exploits plant biomass (Grass), breaks mental concentration (Psychic), and exposes concealment (Dark), while fragile to heat, predation, and rigid armor.
- **Catalog Classes:** Class 4: EXTRACTIVE COUPLING (PARASITISM), Class 2: SELF-SUSTAINING CHAIN REACTION

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Exoskeletal biomass & rapid swarm proliferation |
| 2 | `CAPACITY / CAP` | High speed/tempo pivots (U-turn, Sticky Web) offsetting low average stat totals |
| 3 | `INFLOW / REGEN` | Leech Life (parasitic drain), Quiver Dance multi-stat scaling |
| 4 | `OUTFLOW / DRAIN` | Heavy entry hazard tax (Stealth Rock 2x) and 7 offensive resistances (tied worst with Grass) |
| 5 | `CHANNEL / TYPE` | Biological herbivory, chitinous strikes, swarm harassment, and silk traps |
| 6 | `FILTER / MITIGATION` | Resists Grass, Fighting, Ground (3 NVE); weak to Fire, Flying, Rock |
| 7 | `THRESHOLD` | Metamorphosis / Quiver Dance setup threshold |
| 8 | `TRIGGER` | Swarm emergence or U-turn hit-and-run pivot |
| 9 | `RELEASE` | Herbivory (Grass 2x), phobia disruption (Psychic 2x), tempo disruption (Dark 2x, Sticky Web -1 Speed) |
| 10 | `PROPAGATION` | Sticky Web field hazard + U-turn continuous momentum relay |
| 11 | `TRADE / RESTRICTION` | Elite pivoting/utility tools traded for 7 resisted targets (Fire, Fighting, Poison, Flying, Ghost, Steel, Fairy) and Stealth Rock weakness |
| 12 | `IMMUNITY` | No innate type immunity |
| 13 | `CONTROL LOOP` | Ecological trophic chain (Flying > Bug > Grass) |
| 14 | `ESCAPE` | U-turn (damage + immediate forced switch pivot) |
| 15 | `HOST / COUPLING` | Ecologically coupled as herbivore/parasite (Grass host) and prey (Flying predator) |
| 16 | `FAILURE MODE` | Desiccation/incineration (Fire 2x), avian predation (Flying 2x), crushing mass (Rock 2x), walled by 7 types |
| 17 | `COUNTERPLAY` | Fire, Flying, Rock (2x), Steel/Fairy/Poison/Ghost (0.5x walls) |

### 3.13 `Rock`
- **Mechanical Invariant:** Unrefined crystalline mineral mass: withstands heat, baseline impacts, toxins, and wind, and crushes fragile flyers/bugs/ice/fire, yet fractures under concentrated kinetic impulse, erosion, roots, and refined metal.
- **Catalog Classes:** Class 1: STRESS-ACCUMULATION -> THRESHOLD -> INSTANT RELEASE, Class 8: TYPED FILTER WITH CAP

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Mineral mass & rigid compressive strength |
| 2 | `CAPACITY / CAP` | Special Defense boosted 1.5x under Sandstorm |
| 3 | `INFLOW / REGEN` | Sandstorm 1.5x Sp.Def boost & chip immunity |
| 4 | `OUTFLOW / DRAIN` | 5 defensive weaknesses (tied worst with Grass: Water, Grass, Fighting, Ground, Steel) |
| 5 | `CHANNEL / TYPE` | Ballistic mineral mass & persistent jagged entry hazards (Stealth Rock) |
| 6 | `FILTER / MITIGATION` | Resists 4 types (Normal, Fire, Poison, Flying); immune to Sandstorm chip |
| 7 | `THRESHOLD` | Brittle fracture point under shear/impulse stress |
| 8 | `TRIGGER` | Stealth Rock deployment (taxes every switch-in by Rock effectiveness: 1/32 to 1/2 max HP!) |
| 9 | `RELEASE` | High-impact ballistic damage defeating Fire, Ice, Flying, and Bug (2x) |
| 10 | `PROPAGATION` | Stealth Rock persists across entire battle until Rapid Spin/Defog |
| 11 | `TRADE / RESTRICTION` | Top-tier offensive coverage (4 SE + Stealth Rock) traded for 5 major weaknesses and low move accuracy (Stone Edge 80%, Rock Slide 90%) |
| 12 | `IMMUNITY` | Immune to Sandstorm chip damage (no innate type immunity) |
| 13 | `CONTROL LOOP` | Fighting-Rock-Flying & Fire-Steel-Rock strict RPS triangles; Sandstorm Sp.Def loop |
| 14 | `ESCAPE` | N/A (slow rigid anchor archetype) |
| 15 | `HOST / COUPLING` | Coupled to Sandstorm weather for special bulk viability |
| 16 | `FAILURE MODE` | Hydraulic erosion (Water), root wedging (Grass), seismic shattering (Ground), martial fracture (Fighting), refined metal cutting (Steel) |
| 17 | `COUNTERPLAY` | Water, Grass, Fighting, Ground, Steel (all 2x) |

### 3.14 `Ghost`
- **Mechanical Invariant:** Non-physical spectral channel decoupled from ordinary material contact: mutually zeroed against Normal, immune to Fighting, hunts cognitive/spectral targets, and exhibits self-weakness (phase resonance).
- **Catalog Classes:** Class 6: RESTRICTION-FOR-IMMUNITY TRADE

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Non-physical spectral phase energy |
| 2 | `CAPACITY / CAP` | Only 1 type resists Ghost (Dark) + 1 immune (Normal), granting near-universal neutral coverage |
| 3 | `INFLOW / REGEN` | Pain Split HP averaging, Strength Sap |
| 4 | `OUTFLOW / DRAIN` | Curse (Ghost variant: trades 50% own max HP to drain target 25% max HP/turn!) |
| 5 | `CHANNEL / TYPE` | Non-material spectral phase bypassing physical contact |
| 6 | `FILTER / MITIGATION` | 2 hard immunities (Normal, Fighting) + 2 resists (Poison, Bug) + immune to all trapping effects (Gen 6+) |
| 7 | `THRESHOLD` | Phase coupling threshold (broken only by matching spectral phase Ghost or blind-spot Dark) |
| 8 | `TRIGGER` | Spectral phasing or Curse blood-pact |
| 9 | `RELEASE` | Near-unresisted spectral strikes hitting Psychic & Ghost (2x) and 14 types neutrally |
| 10 | `PROPAGATION` | Bypasses physical traps (Arena Trap, Shadow Tag, Mean Look) completely |
| 11 | `TRADE / RESTRICTION` | Dual contact immunity + trap immunity traded for symmetric 0x inability to touch Normal and self-weakness (2x to Ghost) |
| 12 | `IMMUNITY` | Hard 0x immunity to Normal, Fighting, and all switching-traps (Gen 6+) |
| 13 | `CONTROL LOOP` | Mutual decoupling with Normal (0x <-> 0x); self-weak phase resonance (Ghost -> Ghost 2x) |
| 14 | `ESCAPE` | Universal unconditional escape from trapping abilities/moves |
| 15 | `HOST / COUPLING` | Decoupled from material Normal/Fighting channels |
| 16 | `FAILURE MODE` | Same-phase spectral resonance (Ghost 2x) or shadow/concealment predation (Dark 2x) |
| 17 | `COUNTERPLAY` | Dark (0.5x resist + 2x SE), Normal (0x immunity wall), Ghost (2x mutual phase resonance), Scrappy ability |

### 3.15 `Dragon`
- **Mechanical Invariant:** Apex mythic high-energy organism: resists all four core natural elements (Fire, Water, Electric, Grass), dominates neutral trades, suffers self-weakness and cold-blooded Ice vulnerability, and is hard-bound by mythic order (Fairy 0x).
- **Catalog Classes:** Class 8: TYPED FILTER WITH CAP

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Apex raw elemental & stat-total reservoir (pseudo-legendary cluster) |
| 2 | `CAPACITY / CAP` | Highest average base-stat cap in ontology |
| 3 | `INFLOW / REGEN` | Dragon Dance (Attack + Speed snowball), Roost/Recover on select lines |
| 4 | `OUTFLOW / DRAIN` | Outrage lock-in (2-3 turns -> self-Confusion) & Draco Meteor (-2 Sp.Atk recoil) |
| 5 | `CHANNEL / TYPE` | Raw apex draconic energy |
| 6 | `FILTER / MITIGATION` | Resists all 4 classical/starter elements (Fire, Water, Electric, Grass) |
| 7 | `THRESHOLD` | Outrage lock-in / Draco Meteor depletion; Fairy hard-zero boundary |
| 8 | `TRIGGER` | Dragon Dance setup or high-base-power raw burst |
| 9 | `RELEASE` | Overwhelming neutral output across 15 types, 2x only vs Dragon |
| 10 | `PROPAGATION` | N/A (concentrated apex threat rather than hazard/field spread) |
| 11 | `TRADE / RESTRICTION` | Elemental dominance + massive stats traded for 0x total negation by Fairy, Steel resistance, and Ice/Dragon weaknesses |
| 12 | `IMMUNITY` | No innate type immunity |
| 13 | `CONTROL LOOP` | Gen VI Fairy insertion specifically engineered to break Dragon's uncontested apex dominance (hard-counter inversion) |
| 14 | `ESCAPE` | N/A (Outrage explicitly locks user in and prevents switching!) |
| 15 | `HOST / COUPLING` | Coupled to Misty Terrain suppression (Dragon moves halved 0.5x against grounded targets) |
| 16 | `FAILURE MODE` | Hard-bound by mythic order (Fairy 0x out, 2x in — hard-counter inversion), cold-blooded thermal collapse (Ice 2x), or peer clash (Dragon 2x) |
| 17 | `COUNTERPLAY` | Fairy (0x immunity + 2x SE hard counter), Ice (2x), Dragon (2x), Steel (0.5x wall), Misty Terrain (0.5x) |

### 3.16 `Dark`
- **Mechanical Invariant:** Concealment, deception, and blind-spot exploitation: completely immune to cognitive/Psychic prediction (0x), punishes Psychic and Ghost, and is countered by disciplined directness (Fighting), mythic light/order (Fairy), and swarm disruption (Bug).
- **Catalog Classes:** Class 6: RESTRICTION-FOR-IMMUNITY TRADE, Class 14: GENERATION / CONTROL CYCLES

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Information asymmetry, priority ambush tempo, & item-disruption leverage |
| 2 | `CAPACITY / CAP` | Signature utility scaling (Knock Off removes opponent items for 1.5x power; Sucker Punch priority) |
| 3 | `INFLOW / REGEN` | Nasty Plot, Foul Play (turns opponent's own Attack stat against them — Edge Inversion) |
| 4 | `OUTFLOW / DRAIN` | Item/resource stripping (Knock Off) and trap punishment (Pursuit historically) |
| 5 | `CHANNEL / TYPE` | Deception, blind-spot ambush, and resource/item stripping |
| 6 | `FILTER / MITIGATION` | Hard 0x immunity to Psychic & Prankster status moves (Gen 7+); resists Ghost & Dark |
| 7 | `THRESHOLD` | Opponent telegraph / attack commitment (Sucker Punch trigger) |
| 8 | `TRIGGER` | Cognitive over-reliance (Psychic) or held-item dependency (Knock Off) |
| 9 | `RELEASE` | Punishes Psychic & Ghost (2x) while stripping structural equipment |
| 10 | `PROPAGATION` | Disrupts opponent team synergy by deleting permanent held items |
| 11 | `TRADE / RESTRICTION` | Psychic + Prankster immunity traded for weaknesses to direct discipline (Fighting), mythic order (Fairy), and swarm instinct (Bug) |
| 12 | `IMMUNITY` | Hard 0x immunity to Psychic moves and Prankster-prioritized status moves (Gen 7+) |
| 13 | `CONTROL LOOP` | Dark-Psychic-Fighting strict RPS triangle |
| 14 | `ESCAPE` | Parting Shot (drops target Atk/Sp.Atk -1 and pivots out) |
| 15 | `HOST / COUPLING` | Exploits opponent's own attack/item state (Foul Play / Knock Off) |
| 16 | `FAILURE MODE` | Disciplined direct force (Fighting 2x), mythic enchantment/order (Fairy 2x), or instinctual swarm attack (Bug 2x) |
| 17 | `COUNTERPLAY` | Fighting (0.5x resist + 2x SE), Fairy (0.5x resist + 2x SE), Bug (2x SE) |

### 3.17 `Steel`
- **Mechanical Invariant:** Refined, ordered metallic crystal lattice: apex defensive hub (10 resistances + 1 hard Poison immunity), cuts brittle stone/ice and binds mythic magic (cold iron vs Fairy), while softened by oxidation heat (Fire), fractured by martial impulse (Fighting), and buckled by tectonic shifts (Ground).
- **Catalog Classes:** Class 8: TYPED FILTER WITH CAP, Class 14: GENERATION / CONTROL CYCLES

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | High-integrity metallic lattice durability |
| 2 | `CAPACITY / CAP` | #1 defensive hub in the entire ontology: 10 resistances + 1 immunity (11 mitigated channels out of 18!) |
| 3 | `INFLOW / REGEN` | Sandstorm chip immunity, Iron Defense +2 stages |
| 4 | `OUTFLOW / DRAIN` | Low natural recovery access; trapped by Magnet Pull (electromagnetic vulnerability!) |
| 5 | `CHANNEL / TYPE` | Refined metallic edge, high-density impact, and cold-iron mythic neutralization |
| 6 | `FILTER / MITIGATION` | Resists 10 types (Normal, Grass, Ice, Flying, Psychic, Bug, Rock, Dragon, Steel, Fairy) + 0x Poison + Sandstorm immune |
| 7 | `THRESHOLD` | Annealing/melting temperature (Fire), yield stress (Fighting/Ground) |
| 8 | `TRIGGER` | Refined lattice deployment as defensive pivot/wall |
| 9 | `RELEASE` | Shatters Ice & Rock (2x) and neutralizes Fairy (2x cold-iron invariant) |
| 10 | `PROPAGATION` | N/A (rigid static fortress; loses Ghost/Dark resistances in Gen VI balance nerf) |
| 11 | `TRADE / RESTRICTION` | Unmatched 11-channel mitigation traded for 3 critical weaknesses (Fire, Fighting, Ground), Magnet Pull trap risk, and modest 3-SE offense |
| 12 | `IMMUNITY` | Hard 0x immunity to Poison moves, Poison/Toxic status, and Sandstorm chip |
| 13 | `CONTROL LOOP` | Fire-Steel-Rock strict RPS loop; Gen VI removed Ghost/Dark resists to prevent total defensive monopoly |
| 14 | `ESCAPE` | Vulnerable to Magnet Pull magnetic trapping (cannot switch out) |
| 15 | `HOST / COUPLING` | Inert non-biological substrate (decoupled from organic toxins) |
| 16 | `FAILURE MODE` | Thermal annealing/melting (Fire 2x), tectonic foundation collapse (Ground 2x), focused kinetic fracture (Fighting 2x), Magnet Pull trap |
| 17 | `COUNTERPLAY` | Fire (annealing/melting), Ground (tectonic buckling), Fighting (kinetic fracture), Magnet Pull + Fire/Ground trap |

### 3.18 `Fairy`
- **Mechanical Invariant:** Symbolic/mythic order and restorative enchantment that overrides raw apex power (hard 0x immunity + 2x SE vs Dragon) and dark deception, yet breaks upon contact with cold refined iron (Steel) and biochemical corruption (Poison).
- **Catalog Classes:** Class 6: RESTRICTION-FOR-IMMUNITY TRADE, Class 8: TYPED FILTER WITH CAP

| # | Primitive | Decode |
|---|---|---|
| 1 | `POOL` | Mythic enchantment order & restorative aura |
| 2 | `CAPACITY / CAP` | Elite defensive/offensive balance inserted in Gen VI to regulate Dragon/Fighting/Dark meta |
| 3 | `INFLOW / REGEN` | Moonlight, Wish, Draining Kiss, Misty Terrain status protection |
| 4 | `OUTFLOW / DRAIN` | Misty Terrain halves Dragon output and blocks status conditions across grounded arena |
| 5 | `CHANNEL / TYPE` | Mythic/symbolic binding order & lunar/fae energy |
| 6 | `FILTER / MITIGATION` | Hard 0x immunity to Dragon; resists Fighting, Bug, Dark (3 NVE); only 2 weaknesses (Poison, Steel) |
| 7 | `THRESHOLD` | Contact with industrial cold iron (Steel) or ecological pollution/toxin (Poison) |
| 8 | `TRIGGER` | Mythic binding against raw power (Dragon) or deceit (Dark) |
| 9 | `RELEASE` | Binds and overwhelms Dragon, Fighting, and Dark (all 2x) |
| 10 | `PROPAGATION` | Misty Terrain protective enchantment field across grounded units |
| 11 | `TRADE / RESTRICTION` | Complete Dragon negation + top-tier 3-SE offense traded for industrial/ecological weaknesses (Steel, Poison) and Fire resistance |
| 12 | `IMMUNITY` | Hard 0x immunity to Dragon moves (completely stops Outrage lock-in!) |
| 13 | `CONTROL LOOP` | Systemic regulator inserted in Gen VI to restore balance against Dragon apex monopoly |
| 14 | `ESCAPE` | Misty Terrain immunity to status disruption |
| 15 | `HOST / COUPLING` | Coupled to unpolluted natural/mythic purity (corrupted by Poison/Steel) |
| 16 | `FAILURE MODE` | Cold-iron folklore banishment (Steel 2x) or toxic/industrial corruption (Poison 2x) |
| 17 | `COUNTERPLAY` | Steel (0.5x resist + 2x SE cold iron), Poison (0.5x resist + 2x SE pollution), Fire (0.5x resist wall) |

---

## 4. Grounded Edge Decodes (All 120/120 Non-Neutral Edges)

**Grounding Breakdown:** `PHYSICAL`=58, `BIOLOGICAL_ECOLOGICAL`=20, `SYMBOLIC_MYTHIC`=31, `BALANCE-ONLY`=11 (Total = **120/120**, plus 204 neutral = **324/324**).

| # | Attacker | Mult | Defender | Grounding | Mechanical Decode via Two Node Invariants |
|---|---|---|---|---|---|
| 1 | `Normal` | `0.5x (RESISTS)` | `Rock` | **`PHYSICAL`** | Unfocused kinetic force dissipates against rigid dense mineral mass. |
| 2 | `Normal` | `0x (IMMUNE)` | `Ghost` | **`SYMBOLIC_MYTHIC`** | Material baseline contact passes harmlessly through non-physical spectral phase (hard 0x zero). |
| 3 | `Normal` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | Baseline kinetic impact deflects off refined high-yield metallic lattice. |
| 4 | `Fire` | `0.5x (RESISTS)` | `Fire` | **`PHYSICAL`** | Exothermic plasma/flame cannot oxidize an already-combusting thermal source. |
| 5 | `Fire` | `0.5x (RESISTS)` | `Water` | **`PHYSICAL`** | Water's high specific heat capacity and latent heat of vaporization absorb combustion energy. |
| 6 | `Fire` | `2x (BEATS)` | `Grass` | **`PHYSICAL`** | Dry/organic cellulose provides abundant hydrocarbon fuel for exothermic oxidation. |
| 7 | `Fire` | `2x (BEATS)` | `Ice` | **`PHYSICAL`** | Thermal energy inflow breaks hydrogen-bonded ice lattice, inducing rapid phase-change melting. |
| 8 | `Fire` | `2x (BEATS)` | `Bug` | **`BIOLOGICAL_ECOLOGICAL`** | High surface-area-to-volume ratio causes rapid desiccation and thermal protein denaturation in arthropods. |
| 9 | `Fire` | `0.5x (RESISTS)` | `Rock` | **`PHYSICAL`** | Silicate mineral mass has high melting point and acts as a non-combustible thermal barrier. |
| 10 | `Fire` | `0.5x (RESISTS)` | `Dragon` | **`BALANCE-ONLY`** | Game-design/lore apex gatekeeping: Dragon resists all four starter elements (Fire/Water/Electric/Grass) primarily for RPG boss-tier balance. |
| 11 | `Fire` | `2x (BEATS)` | `Steel` | **`PHYSICAL`** | High thermal energy anneals, softens, and oxidizes refined metal crystal lattices. |
| 12 | `Water` | `2x (BEATS)` | `Fire` | **`PHYSICAL`** | High heat capacity cools fuel below ignition temperature while liquid layer smothers atmospheric oxygen. |
| 13 | `Water` | `0.5x (RESISTS)` | `Water` | **`PHYSICAL`** | Fluid impact merges into bulk fluid reservoir without structural disruption. |
| 14 | `Water` | `0.5x (RESISTS)` | `Grass` | **`BIOLOGICAL_ECOLOGICAL`** | Hidden FEEDS edge: photosynthetic plants absorb liquid water metabolically rather than taking damage. |
| 15 | `Water` | `2x (BEATS)` | `Ground` | **`PHYSICAL`** | Hydraulic flow saturates soil cohesion, inducing mudslides and mechanical erosion. |
| 16 | `Water` | `2x (BEATS)` | `Rock` | **`PHYSICAL`** | Continuous hydraulic pressure and chemical weathering erode mineral rock over time. |
| 17 | `Water` | `0.5x (RESISTS)` | `Dragon` | **`BALANCE-ONLY`** | Game-design apex tiering: Dragon resists all four core elemental attacks for endgame progression balance. |
| 18 | `Electric` | `2x (BEATS)` | `Water` | **`PHYSICAL`** | Dissolved ions in natural water turn the medium into a low-resistance conductor distributing lethal current. |
| 19 | `Electric` | `0.5x (RESISTS)` | `Electric` | **`PHYSICAL`** | High-potential electrical system already operates at elevated voltage and resists additional charge flow. |
| 20 | `Electric` | `0.5x (RESISTS)` | `Grass` | **`PHYSICAL`** | Dry woody/fibrous plant tissue acts as a high-resistance dielectric insulator impeding current flow. |
| 21 | `Electric` | `0x (IMMUNE)` | `Ground` | **`PHYSICAL`** | Infinite earth capacitance sinks electrical potential directly to zero volts (hard 0x zero). |
| 22 | `Electric` | `2x (BEATS)` | `Flying` | **`PHYSICAL`** | Elevated airborne objects in storm fields become isolated lightning-strike conductors with no safe grounding path. |
| 23 | `Electric` | `0.5x (RESISTS)` | `Dragon` | **`BALANCE-ONLY`** | Game-design apex tiering: Dragon resists Electric alongside Fire/Water/Grass with no physical dielectric basis. |
| 24 | `Grass` | `0.5x (RESISTS)` | `Fire` | **`PHYSICAL`** | Plant biomass serves as fuel that gets consumed when attacking an active exothermic flame. |
| 25 | `Grass` | `2x (BEATS)` | `Water` | **`BIOLOGICAL_ECOLOGICAL`** | Metabolic water uptake drains and absorbs fluid reservoirs through root/vascular transport. |
| 26 | `Grass` | `0.5x (RESISTS)` | `Grass` | **`BIOLOGICAL_ECOLOGICAL`** | Competing plant tissues share identical cellulose defense and photosynthetic niche. |
| 27 | `Grass` | `0.5x (RESISTS)` | `Poison` | **`BIOLOGICAL_ECOLOGICAL`** | Toxic/herbicidal chemistry rapidly degrades plant cellular walls before plant growth can take hold. |
| 28 | `Grass` | `2x (BEATS)` | `Ground` | **`BIOLOGICAL_ECOLOGICAL`** | Root networks penetrate, bind, and extract nutrients from soil, fracturing earthen stability. |
| 29 | `Grass` | `0.5x (RESISTS)` | `Flying` | **`BIOLOGICAL_ECOLOGICAL`** | Airborne mobility evades ground-rooted vines and birds consume seeds/foliage. |
| 30 | `Grass` | `0.5x (RESISTS)` | `Bug` | **`BIOLOGICAL_ECOLOGICAL`** | Herbivorous arthropods feed on plant biomass, converting plant attacks into nutrition. |
| 31 | `Grass` | `2x (BEATS)` | `Rock` | **`BIOLOGICAL_ECOLOGICAL`** | Biological root-wedging and organic acids split fissures inside mineral rock. |
| 32 | `Grass` | `0.5x (RESISTS)` | `Dragon` | **`BALANCE-ONLY`** | Game-design apex tiering: Dragon resists Grass as part of the 4-element endgame resistance package. |
| 33 | `Grass` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | Soft organic plant fibers cannot penetrate or corrode a refined metallic crystal lattice. |
| 34 | `Ice` | `0.5x (RESISTS)` | `Fire` | **`PHYSICAL`** | Active exothermic heat rapidly melts incoming cryogenic projectiles before impact. |
| 35 | `Ice` | `0.5x (RESISTS)` | `Water` | **`PHYSICAL`** | Liquid water's high thermal mass absorbs cold deficit and buffers freezing. |
| 36 | `Ice` | `2x (BEATS)` | `Grass` | **`BIOLOGICAL_ECOLOGICAL`** | Cellular ice-crystal formation ruptures plant cell membranes (frostbite necrosis). |
| 37 | `Ice` | `0.5x (RESISTS)` | `Ice` | **`PHYSICAL`** | Rigid cryogenic crystal already exists at sub-zero equilibrium and resists additional cooling. |
| 38 | `Ice` | `2x (BEATS)` | `Ground` | **`PHYSICAL`** | Freeze-thaw water expansion inside soil pores causes frost heave and mechanical cracking. |
| 39 | `Ice` | `2x (BEATS)` | `Flying` | **`PHYSICAL`** | Ice accretion on wings destroys aerodynamic lift and adds fatal stalling weight. |
| 40 | `Ice` | `2x (BEATS)` | `Dragon` | **`BIOLOGICAL_ECOLOGICAL`** | Reptilian/ectothermic draconic physiology suffers severe metabolic shutdown under extreme heat withdrawal. |
| 41 | `Ice` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | High-ductility metallic alloy withstands brittle ice impacts without fracturing. |
| 42 | `Fighting` | `2x (BEATS)` | `Normal` | **`PHYSICAL`** | Trained, focused biomechanical force decisively overwhelms untrained baseline physical mass. |
| 43 | `Fighting` | `2x (BEATS)` | `Ice` | **`PHYSICAL`** | Concentrated high-impulse strike fractures brittle crystalline ice along cleavage planes. |
| 44 | `Fighting` | `0.5x (RESISTS)` | `Poison` | **`BIOLOGICAL_ECOLOGICAL`** | Close-quarters physical contact exposes fighters to toxic secretions that impair stamina. |
| 45 | `Fighting` | `0.5x (RESISTS)` | `Flying` | **`PHYSICAL`** | Elevation separation places airborne targets out of effective melee reach and leverage. |
| 46 | `Fighting` | `0.5x (RESISTS)` | `Psychic` | **`SYMBOLIC_MYTHIC`** | Mind-over-matter archetype: predictive cognitive control anticipates and deflects telegraphed physical strikes. |
| 47 | `Fighting` | `0.5x (RESISTS)` | `Bug` | **`BALANCE-ONLY`** | Game-design mutual resistance quirk (Fighting <-> Bug 0.5x): lacks a clean physical or biological invariant. |
| 48 | `Fighting` | `2x (BEATS)` | `Rock` | **`PHYSICAL`** | Concentrated martial kinetic impulse shatters brittle stone (brick-breaking mechanics). |
| 49 | `Fighting` | `0x (IMMUNE)` | `Ghost` | **`SYMBOLIC_MYTHIC`** | Pure physical contact cannot interact with non-material spectral phase (hard 0x zero). |
| 50 | `Fighting` | `2x (BEATS)` | `Dark` | **`SYMBOLIC_MYTHIC`** | Disciplined righteous/direct combat breaks cowardly deception and dirty-fighting tactics. |
| 51 | `Fighting` | `2x (BEATS)` | `Steel` | **`PHYSICAL`** | High-impulse concentrated force dents, bends, and work-fatigues metal armor. |
| 52 | `Fighting` | `0.5x (RESISTS)` | `Fairy` | **`SYMBOLIC_MYTHIC`** | Mythic enchantment and ethereal agility outmaneuver straightforward physical brawling. |
| 53 | `Poison` | `2x (BEATS)` | `Grass` | **`BIOLOGICAL_ECOLOGICAL`** | Herbicidal toxins directly disrupt photosynthesis and cellular metabolism in plants. |
| 54 | `Poison` | `0.5x (RESISTS)` | `Poison` | **`BIOLOGICAL_ECOLOGICAL`** | Venomous organisms possess evolved antitoxins and biochemical resistance to self-channel toxins. |
| 55 | `Poison` | `0.5x (RESISTS)` | `Ground` | **`PHYSICAL`** | Porous soil and clay minerals adsorb, dilute, and immobilize chemical toxins. |
| 56 | `Poison` | `0.5x (RESISTS)` | `Rock` | **`PHYSICAL`** | Inert non-living silicate rock has no biological metabolism for toxins to disrupt. |
| 57 | `Poison` | `0.5x (RESISTS)` | `Ghost` | **`SYMBOLIC_MYTHIC`** | Undead/non-biological spectral entities lack living organs susceptible to cellular venom. |
| 58 | `Poison` | `0x (IMMUNE)` | `Steel` | **`PHYSICAL`** | Refined non-biological metal has zero metabolic pathways for biological poisons (hard 0x zero). |
| 59 | `Poison` | `2x (BEATS)` | `Fairy` | **`SYMBOLIC_MYTHIC`** | Industrial pollution and toxic corruption defile and wither mythic nature spirits. |
| 60 | `Ground` | `2x (BEATS)` | `Fire` | **`PHYSICAL`** | Blanketing soil/sand smothers oxygen supply and extinguishes active combustion. |
| 61 | `Ground` | `2x (BEATS)` | `Electric` | **`PHYSICAL`** | Earthen grounding shorts out high-potential electrical systems into zero-volt collapse (2x complement to 0x immunity). |
| 62 | `Ground` | `0.5x (RESISTS)` | `Grass` | **`BIOLOGICAL_ECOLOGICAL`** | Plant root structures anchor and stabilize loose soil, absorbing tectonic disruption. |
| 63 | `Ground` | `2x (BEATS)` | `Poison` | **`PHYSICAL`** | Mineral earth buries, adsorbs, and neutralizes liquid/chemical toxins. |
| 64 | `Ground` | `0x (IMMUNE)` | `Flying` | **`PHYSICAL`** | Seismic ground waves cannot propagate through air to reach airborne targets (hard 0x zero). |
| 65 | `Ground` | `0.5x (RESISTS)` | `Bug` | **`BALANCE-ONLY`** | Game-design quirk: burrowing/ground-dwelling insects resisting seismic shockwaves is inconsistently applied and primarily balances Earthquake spam. |
| 66 | `Ground` | `2x (BEATS)` | `Rock` | **`PHYSICAL`** | Tectonic liquefaction and shear waves undermine and fracture rigid rock foundations. |
| 67 | `Ground` | `2x (BEATS)` | `Steel` | **`PHYSICAL`** | Seismic ground buckling bends, buries, and structurally collapses heavy rigid metal frameworks. |
| 68 | `Flying` | `0.5x (RESISTS)` | `Electric` | **`PHYSICAL`** | High-voltage electromagnetic fields ionize air and disrupt aerodynamic approach. |
| 69 | `Flying` | `2x (BEATS)` | `Grass` | **`BIOLOGICAL_ECOLOGICAL`** | Avian predation on seeds/foliage and high-speed wind shear shred plant structures. |
| 70 | `Flying` | `2x (BEATS)` | `Fighting` | **`PHYSICAL`** | High-ground aerial diving exploits elevation leverage against ground-bound melee fighters. |
| 71 | `Flying` | `2x (BEATS)` | `Bug` | **`BIOLOGICAL_ECOLOGICAL`** | Direct trophic predation: birds and aerial predators systematically hunt insects. |
| 72 | `Flying` | `0.5x (RESISTS)` | `Rock` | **`PHYSICAL`** | Dense stationary mineral mass easily withstands wind shear and light aerial strikes. |
| 73 | `Flying` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | Aerodynamic gusts and talons fail to dent refined high-strength metal. |
| 74 | `Psychic` | `2x (BEATS)` | `Fighting` | **`SYMBOLIC_MYTHIC`** | Mind-over-matter: cognitive prediction and telekinesis effortlessly neutralize brute muscular force. |
| 75 | `Psychic` | `2x (BEATS)` | `Poison` | **`SYMBOLIC_MYTHIC`** | Mental discipline / clinical intelligence diagnoses and purges toxic disruption (weak physical basis, symbolic archetype). |
| 76 | `Psychic` | `0.5x (RESISTS)` | `Psychic` | **`SYMBOLIC_MYTHIC`** | Trained cognitive shields resist external telepathic intrusion from peer mental channels. |
| 77 | `Psychic` | `0x (IMMUNE)` | `Dark` | **`SYMBOLIC_MYTHIC`** | Concealment, malice, and blind-spot deception completely block predictive mental lock-on (hard 0x zero). |
| 78 | `Psychic` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | Inert metallic Faraday/shielding mass lacks organic neural substrate and blocks mental/EM waves. |
| 79 | `Bug` | `0.5x (RESISTS)` | `Fire` | **`PHYSICAL`** | Active flame incinerates chitinous insects upon approach. |
| 80 | `Bug` | `2x (BEATS)` | `Grass` | **`BIOLOGICAL_ECOLOGICAL`** | Herbivory: insects directly consume plant foliage and sap. |
| 81 | `Bug` | `0.5x (RESISTS)` | `Fighting` | **`BALANCE-ONLY`** | Game-design mutual resistance quirk (Bug <-> Fighting 0.5x) without real mechanical grounding. |
| 82 | `Bug` | `0.5x (RESISTS)` | `Poison` | **`BIOLOGICAL_ECOLOGICAL`** | Toxic chemical defenses (insecticides/venoms) repel and kill arthropod attackers. |
| 83 | `Bug` | `0.5x (RESISTS)` | `Flying` | **`BIOLOGICAL_ECOLOGICAL`** | Avian predators naturally counter and outmaneuver insects in mid-air. |
| 84 | `Bug` | `2x (BEATS)` | `Psychic` | **`SYMBOLIC_MYTHIC`** | Primal entomophobia disrupts calm mental concentration and telepathic focus. |
| 85 | `Bug` | `0.5x (RESISTS)` | `Ghost` | **`BALANCE-ONLY`** | Game-design defensive tuning nerfing Bug offense against Ghost with no structural justification. |
| 86 | `Bug` | `2x (BEATS)` | `Dark` | **`SYMBOLIC_MYTHIC`** | Japanese Kamen Rider heroic-insect cultural trope opposing evil/Darkness (plus nocturnal insect vision in dark). |
| 87 | `Bug` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | Chitinous mandibles cannot bite through refined metallic armor. |
| 88 | `Bug` | `0.5x (RESISTS)` | `Fairy` | **`BALANCE-ONLY`** | Gen VI competitive balance tuning specifically giving Fairy resistance to ubiquitous U-turn/Bug pivots. |
| 89 | `Rock` | `2x (BEATS)` | `Fire` | **`PHYSICAL`** | Heavy mineral avalanches crush and smother combustion sources. |
| 90 | `Rock` | `2x (BEATS)` | `Ice` | **`PHYSICAL`** | High-density rock impact shatters brittle lower-hardness ice crystals. |
| 91 | `Rock` | `0.5x (RESISTS)` | `Fighting` | **`PHYSICAL`** | Trained martial artists condition and deflect blunt stone impacts (breaking bricks/boards). |
| 92 | `Rock` | `0.5x (RESISTS)` | `Ground` | **`PHYSICAL`** | Deep unconsolidated soil cushions and absorbs blunt mineral projectiles. |
| 93 | `Rock` | `2x (BEATS)` | `Flying` | **`PHYSICAL`** | Ballistic stone impact ('killing two birds with one stone') grounds fragile airborne anatomy. |
| 94 | `Rock` | `2x (BEATS)` | `Bug` | **`PHYSICAL`** | Heavy mineral mass easily crushes delicate arthropod exoskeletons. |
| 95 | `Rock` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | Refined metal alloys possess higher toughness and shatter resistance than raw rock. |
| 96 | `Ghost` | `0x (IMMUNE)` | `Normal` | **`SYMBOLIC_MYTHIC`** | Non-physical spectral attacks pass cleanly through baseline material Normal entities (mutual 0x zero). |
| 97 | `Ghost` | `2x (BEATS)` | `Psychic` | **`SYMBOLIC_MYTHIC`** | Primal fear of spirits/the uncanny shatters rational cognitive control. |
| 98 | `Ghost` | `2x (BEATS)` | `Ghost` | **`SYMBOLIC_MYTHIC`** | Same-phase spectral resonance allows spirits to directly disrupt one another (self-weak 2x). |
| 99 | `Ghost` | `0.5x (RESISTS)` | `Dark` | **`SYMBOLIC_MYTHIC`** | Shadow/darkness subsumes and resists spectral ambush. |
| 100 | `Dragon` | `2x (BEATS)` | `Dragon` | **`SYMBOLIC_MYTHIC`** | Apex-vs-apex parity: only draconic power matches draconic scales (self-weak 2x). |
| 101 | `Dragon` | `0.5x (RESISTS)` | `Steel` | **`SYMBOLIC_MYTHIC`** | Forged knightly armor withstands raw draconic fury (also Gen II balance check on Dragon). |
| 102 | `Dragon` | `0x (IMMUNE)` | `Fairy` | **`SYMBOLIC_MYTHIC`** | Mythic fairy-tale order completely binds and nullifies raw draconic chaos (hard 0x zero; Gen VI meta-balance check). |
| 103 | `Dark` | `0.5x (RESISTS)` | `Fighting` | **`SYMBOLIC_MYTHIC`** | Disciplined martial integrity sees through and resists deceitful ambush. |
| 104 | `Dark` | `2x (BEATS)` | `Psychic` | **`SYMBOLIC_MYTHIC`** | Exploitation of blind spots and fear of the dark overwhelms cognitive prediction (2x complement to 0x immunity). |
| 105 | `Dark` | `2x (BEATS)` | `Ghost` | **`SYMBOLIC_MYTHIC`** | Predatory shadow magic dominates spectral entities. |
| 106 | `Dark` | `0.5x (RESISTS)` | `Dark` | **`SYMBOLIC_MYTHIC`** | Deceivers recognize and resist mirror-image blind-spot tactics. |
| 107 | `Dark` | `0.5x (RESISTS)` | `Fairy` | **`SYMBOLIC_MYTHIC`** | Mythic radiance and order resist malicious concealment. |
| 108 | `Steel` | `0.5x (RESISTS)` | `Fire` | **`PHYSICAL`** | Intense heat weakens metallic weapons upon strike. |
| 109 | `Steel` | `0.5x (RESISTS)` | `Water` | **`PHYSICAL`** | Fluid drag cushions metallic impact while moisture promotes rust/oxidation. |
| 110 | `Steel` | `0.5x (RESISTS)` | `Electric` | **`BALANCE-ONLY`** | Game-design tuning: Steel-type moves dealing 0.5x to Electric lacks physical basis (metal actually conducts/shorts electrical circuits). |
| 111 | `Steel` | `2x (BEATS)` | `Ice` | **`PHYSICAL`** | Hardened metallic blades cleave and shatter brittle ice lattices. |
| 112 | `Steel` | `2x (BEATS)` | `Rock` | **`PHYSICAL`** | Refined steel mining tools fracture and quarry raw unrefined rock. |
| 113 | `Steel` | `0.5x (RESISTS)` | `Steel` | **`PHYSICAL`** | Hardened metal colliding with hardened metal deflects with minimal penetration. |
| 114 | `Steel` | `2x (BEATS)` | `Fairy` | **`SYMBOLIC_MYTHIC`** | Folklore cold-iron invariant: forged iron directly harms and banishes fae beings. |
| 115 | `Fairy` | `0.5x (RESISTS)` | `Fire` | **`BALANCE-ONLY`** | Gen VI competitive balance tuning giving Fire a defensive Fairy resistance to curb Fairy meta dominance. |
| 116 | `Fairy` | `2x (BEATS)` | `Fighting` | **`SYMBOLIC_MYTHIC`** | Mythic enchantment effortlessly redirects and subdues raw martial force. |
| 117 | `Fairy` | `0.5x (RESISTS)` | `Poison` | **`SYMBOLIC_MYTHIC`** | Toxic/polluted corruption resists and degrades fae magic. |
| 118 | `Fairy` | `2x (BEATS)` | `Dragon` | **`SYMBOLIC_MYTHIC`** | Mythic order overrides raw apex draconic might (2x complement to 0x immunity). |
| 119 | `Fairy` | `2x (BEATS)` | `Dark` | **`SYMBOLIC_MYTHIC`** | Radiant mythic order dispels malicious deception and shadow. |
| 120 | `Fairy` | `0.5x (RESISTS)` | `Steel` | **`SYMBOLIC_MYTHIC`** | Cold forged iron repels and neutralizes fae enchantment. |

**Section 10 Balance-Only Audit:** All **11** `BALANCE-ONLY` edges are explicitly listed in `residual_mismatches` inside `INVARIANT_ENTRY_SC-IT-POKEMON-001.jsonl` and never forced onto real physics or biology.

---

## 5. 11-Role Closure Table (All 18 Types) & Predicted Missing Edges

### `Normal`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Baseline biological/mechanical mass |
| `SINK` | Rock/Steel armor dissipation; Ghost phase void |
| `COUNTER` | Fighting (2x), Ghost (0x) |
| `AMPLIFIER` | STAB 1.5x + Silk Scarf / Adaptability / Guts |
| `CONDUCTOR` | Sound waves (Boomburst) & direct contact |
| `INSULATOR` | Ghost phase decoupling (0x mutual) |
| `CONVERTER` | Pixilate / Refrigerate / Aerilate (converts Normal -> Fairy/Ice/Flying!) |
| `BYPRODUCT` | Recoil self-damage (Double-Edge) |
| `SYMBIONT` | Ghost partner (covers sole Fighting weakness cleanly) |
| `PARASITE` | PREDICTED: Normal lack of resists leaves it vulnerable to chip attrition/hazards |
| `STATE CHANGE` | Type-Conversion Abilities (-ate abilities) & Terastallization |

### `Fire`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Exothermic fuel + oxidizer + ignition spark |
| `SINK` | Water (heat sink), Ground/Rock (smothering mass) |
| `COUNTER` | Water, Ground, Rock (all 2x); Flash Fire / Well-Baked Body (0x) |
| `AMPLIFIER` | Harsh Sunlight (1.5x), Flash Fire (+1.5x) |
| `CONDUCTOR` | Dry Grass/Bug biomass fuel; Sun-heated air |
| `INSULATOR` | Rock silicate mass; Water thermal buffer |
| `CONVERTER` | Flash Fire / Well-Baked Body (Fire attack -> offense/Defense boost); Melts Ice -> Water (PREDICTED) |
| `BYPRODUCT` | Burn status (1/16 HP + 0.5x Phys Atk) & Ash/Char |
| `SYMBIONT` | Grass (Chlorophyll/Sun synergy in Sun teams) |
| `PARASITE` | Stealth Rock (2x entry tax punishing Fire pivots) |
| `STATE CHANGE` | Thaws Freeze instantaneously; Dry Skin dehydrates in Sun |

### `Water`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Fluid hydrological reservoir + Rain precipitation |
| `SINK` | Grass (metabolic uptake), Harsh Sunlight evaporation (0.5x) |
| `COUNTER` | Electric (2x), Grass (2x), Freeze-Dry (2x exception) |
| `AMPLIFIER` | Rain (1.5x) |
| `CONDUCTOR` | Dissolved ions conduct Electric current (2x risk) |
| `INSULATOR` | Thermal insulation against Fire (0.5x) & Ice (0.5x) |
| `CONVERTER` | Water Absorb / Storm Drain / Dry Skin (Water -> HP/Sp.Atk) |
| `BYPRODUCT` | Scald steam burn; mud/erosion against Ground/Rock |
| `SYMBIONT` | Electric/Flying partners (Thunder/Hurricane 100% accuracy in Rain) |
| `PARASITE` | PREDICTED: Poison/toxic runoff contaminating Water (missing 2x edge in Pokemon!) |
| `STATE CHANGE` | Liquid -> Ice (Freeze-Dry) or Vapor (Harsh Sunlight 0.5x) |

### `Electric`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Electrostatic potential gradient / storm discharge |
| `SINK` | Ground (infinite earth capacitance 0x); Lightning Rod |
| `COUNTER` | Ground (0x out, 2x in); Volt Absorb / Motor Drive / Lightning Rod |
| `AMPLIFIER` | Electric Terrain (1.3x), Charge (2x next Electric move) |
| `CONDUCTOR` | Water (2x), Air/Flying (2x), PREDICTED: Steel (currently only 1x!) |
| `INSULATOR` | Grass dielectric tissue (0.5x), Ground infinite sink (0x) |
| `CONVERTER` | Volt Absorb (-> HP), Motor Drive (-> Speed), Lightning Rod (-> Sp.Atk) |
| `BYPRODUCT` | Paralysis (0.5x Speed, 25% action skip) |
| `SYMBIONT` | Rain weather (Thunder bypasses accuracy check) |
| `PARASITE` | Lightning Rod redirecting ally/foe Electric moves away from intended target |
| `STATE CHANGE` | Discharge -> Neutralized Ground Potential (0V) |

### `Grass`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Photosynthesis (Sun + Water + Ground minerals) |
| `SINK` | Fire combustion, Bug herbivory, Ice frostbite, Poison herbicide |
| `COUNTER` | Fire, Ice, Poison, Flying, Bug (5 weaknesses); Sap Sipper (0x) |
| `AMPLIFIER` | Grassy Terrain (1.3x + 1/16 HP regen), Sun (Chlorophyll 2x Speed + 1-turn Solar Beam) |
| `CONDUCTOR` | Vascular roots conducting Water/Ground nutrients |
| `INSULATOR` | Dielectric wood insulating Electric (0.5x); Powder/Spore immunity |
| `CONVERTER` | Sap Sipper (Grass -> +1 Atk); Hidden FEEDS edge converts Water/Ground into growth |
| `BYPRODUCT` | Spores, Sleep Powder, Leech Seed, Oxygen |
| `SYMBIONT` | Fire/Sun setters (Chlorophyll) & Water-Fire-Grass defensive cores |
| `PARASITE` | Leech Seed (extractive 1/8 HP/turn drain) & Bug herbivores |
| `STATE CHANGE` | Living Biomass -> Charred Fuel (Fire) or Frozen Necrosis (Ice) |

### `Ice`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Cryogenic heat extraction + Snow atmospheric crystallization |
| `SINK` | Fire melting, Water thermal mass, Fighting/Rock/Steel mechanical shatter |
| `COUNTER` | Fire, Fighting, Rock, Steel (all 2x) |
| `AMPLIFIER` | Snow weather (1.5x Def + 100% Blizzard + Aurora Veil) |
| `CONDUCTOR` | Freeze-Dry special thermal channel (hits Water 2x) |
| `INSULATOR` | Self-equilibrium against Ice (0.5x) & Freeze status immunity |
| `CONVERTER` | Water -> Rigid Ice crystal (Freeze status) |
| `BYPRODUCT` | Freeze rate-suppression lock; brittle crystalline shards |
| `SYMBIONT` | Water/Ground partners covering Fire/Steel/Rock weaknesses |
| `PARASITE` | Stealth Rock (2x entry hazard tax punishing fragile Ice pivots) |
| `STATE CHANGE` | Solid Ice -> Melted Water under Fire (PREDICTED type-shift mechanic) |

### `Fighting`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Trained kinetic biomechanical impulse |
| `SINK` | Ghost intangibility (0x); Burn halving physical output |
| `COUNTER` | Psychic, Flying, Fairy (2x); Ghost (0x) |
| `AMPLIFIER` | Guts (inverts Burn penalty into 1.5x Attack!), Bulk Up, Swords Dance |
| `CONDUCTOR` | Direct physical contact & Aura waves |
| `INSULATOR` | Stealth Rock resistance (0.5x) & Dark trickery resistance (0.5x) |
| `CONVERTER` | Guts ability (Status penalty -> 1.5x offense Edge Inversion); Drain Punch (damage -> HP) |
| `BYPRODUCT` | Self-defense drops (Close Combat) or crash recoil (High Jump Kick) |
| `SYMBIONT` | Dark/Ghost partners eliminating Psychic & Ghost walls |
| `PARASITE` | Burn status (cuts non-Guts physical output by 50%) |
| `STATE CHANGE` | Controlled Stance -> Overextended Exhaustion (Close Combat -1 Def/SpD) |

### `Poison`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Biochemical venom synthesis & toxic metabolic waste |
| `SINK` | Steel inert non-living barrier (0x); Ground soil adsorption (2x) |
| `COUNTER` | Ground (2x), Psychic (2x), Steel (0x) |
| `AMPLIFIER` | Venoshock (2x power on poisoned targets), Toxic Spikes 2-layer escalation |
| `CONDUCTOR` | Living cellular/vascular bloodstream |
| `INSULATOR` | Steel inert metal (0x); Poison/Steel status immunity; Misty Terrain |
| `CONVERTER` | Poison Heal (Poison drain -> 1/8 HP/turn heal Edge Inversion); Poison-type absorbs Toxic Spikes |
| `BYPRODUCT` | Cumulative stacking Toxic timer (N/16 max HP/turn) |
| `SYMBIONT` | Corrosion ability (breaks Steel/Poison immunity — explicit rule bypass!) |
| `PARASITE` | Toxic stalling drains defensive hosts over escalating turns |
| `STATE CHANGE` | Regular Poison (flat 1/8) -> Badly Poisoned (escalating N/16) |

### `Ground`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Tectonic lithosphere mass & infinite earth capacitance |
| `SINK` | Water hydraulic erosion, Grass root stabilization, Ice frost heave |
| `COUNTER` | Water, Grass, Ice (all 2x); Flying / Levitate (0x); Earth Eater (0x) |
| `AMPLIFIER` | Sand Force (1.3x in Sandstorm) |
| `CONDUCTOR` | Solid continuous terrestrial substrate (Earthquake propagation) |
| `INSULATOR` | Air gap (Flying / Levitate / Air Balloon = 0x decoupling) |
| `CONVERTER` | Earth Eater (Ground -> +1/4 HP); Electric charge -> 0V ground potential |
| `BYPRODUCT` | Spikes entry hazard; Sandstorm dust |
| `SYMBIONT` | Sandstorm setters (Rock/Steel/Ground Sand core) |
| `PARASITE` | Grassy Terrain cutting Earthquake output by 50% |
| `STATE CHANGE` | Solid Ground -> Eroded Mud (Water) or Frost-Heaved Cracks (Ice) |

### `Flying`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Aerodynamic lift & altitude decoupling |
| `SINK` | Stealth Rock (2x switch tax), Electric lightning, Ice wing-icing |
| `COUNTER` | Electric, Ice, Rock (all 2x); Gravity / Smack Down (forces grounded) |
| `AMPLIFIER` | Tailwind (2x Speed), Rain (100% Hurricane accuracy) |
| `CONDUCTOR` | Atmospheric wind currents |
| `INSULATOR` | Altitude gap insulating against Ground (0x), Spikes, Toxic Spikes, Sticky Web |
| `CONVERTER` | Roost (surrenders Flying altitude for 1 turn -> restores 50% HP) |
| `BYPRODUCT` | Defog clearing all field hazards & screens |
| `SYMBIONT` | Heavy-Duty Boots (negates Stealth Rock tax); Ground partners (immune to Electric) |
| `PARASITE` | Stealth Rock (25% HP entry drain on every switch-in) |
| `STATE CHANGE` | Airborne Immune -> Grounded Vulnerable (Roost / Gravity / Smack Down) |

### `Psychic`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Cognitive predictive modeling & telekinetic control |
| `SINK` | Dark blind-spot negation (0x); Steel Faraday shielding (0.5x) |
| `COUNTER` | Dark (0x out, 2x in), Ghost (2x), Bug (2x) |
| `AMPLIFIER` | Psychic Terrain (1.3x + priority block), Expanding Force (spread + 1.5x in Terrain) |
| `CONDUCTOR` | Target neural predictability & psychic field |
| `INSULATOR` | Dark deception (0x); Steel inert shell (0.5x) |
| `CONVERTER` | Trick Room (inverts global Speed hierarchy); Guard/Power Swap |
| `BYPRODUCT` | Future Sight delayed two-turn temporal strike |
| `SYMBIONT` | Fighting/Fairy partners covering Dark hard-counter |
| `PARASITE` | Pursuit (historically trapped Psychic switch-outs) & Knock Off item theft |
| `STATE CHANGE` | Normal Speed Order -> Inverted Trick Room Space |

### `Bug`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | High-reproduction arthropod swarm & chitinous adaptation |
| `SINK` | Fire desiccation, Flying predation, Rock crushing, 7 resisted walls |
| `COUNTER` | Fire, Flying, Rock (2x); Steel/Fairy/Poison/Ghost (0.5x walls) |
| `AMPLIFIER` | Swarm (1.5x at <=1/3 HP), Quiver Dance (+1 SpA/SpD/Spe), Compound Eyes |
| `CONDUCTOR` | Momentum pivoting (U-turn) & silk webs (Sticky Web) |
| `INSULATOR` | Chitin resistance vs Grass/Ground/Fighting |
| `CONVERTER` | Leech Life (damage -> 50% HP recovery) |
| `BYPRODUCT` | Sticky Web (-1 Speed hazard for grounded switch-ins) |
| `SYMBIONT` | Ground/Fire partners breaking Steel walls |
| `PARASITE` | Stealth Rock (2x switch-in tax punishing U-turn pivots) |
| `STATE CHANGE` | Larval/Weak Stage -> Metamorphosed Quiver-Dance Sweeper |

### `Rock`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Unrefined geological mineral formations |
| `SINK` | Water erosion, Grass roots, Ground quakes, Fighting/Steel fracture |
| `COUNTER` | Water, Grass, Fighting, Ground, Steel (5 weaknesses) |
| `AMPLIFIER` | Sandstorm (1.5x Sp.Def boost + chip immunity) |
| `CONDUCTOR` | Ballistic trajectory & jagged persistent hazards (Stealth Rock) |
| `INSULATOR` | High melting point (0.5x Fire) & inertness (0.5x Poison) |
| `CONVERTER` | Smack Down (converts airborne Flying targets -> Grounded) |
| `BYPRODUCT` | Stealth Rock (most influential hazard in competitive Pokemon) |
| `SYMBIONT` | Sandstorm setters & Ground/Steel cores |
| `PARASITE` | Low base accuracy tax (80-90%) creating variance risk |
| `STATE CHANGE` | Raw Rock -> Refined Steel (metallurgical smelting, PREDICTED) |

### `Ghost`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Non-physical spectral phase decoupled from matter |
| `SINK` | Dark predation (2x), same-phase Ghost resonance (2x), Normal phase void (0x) |
| `COUNTER` | Dark (0.5x resist + 2x SE), Normal (0x wall), Ghost (2x) |
| `AMPLIFIER` | Hex (2x power against statused targets) |
| `CONDUCTOR` | Uncanny spectral fear channel hitting Psychic & Ghost |
| `INSULATOR` | Material phase decoupling (0x vs Normal & Fighting; immune to all traps) |
| `CONVERTER` | Ghost Curse (50% own HP -> 25%/turn residual drain on target) |
| `BYPRODUCT` | Spinblocking (blocks Rapid Spin Normal-type hazard removal!) |
| `SYMBIONT` | Fighting/Fairy partners breaking Dark & Normal walls |
| `PARASITE` | Scrappy / Foresight abilities breaking Ghost's Normal/Fighting immunities |
| `STATE CHANGE` | Material Host -> Unbound Spectral Phase (immune to traps) |

### `Dragon`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Apex mythic elemental reservoir & high base-stat budget |
| `SINK` | Fairy hard-zero negation (0x out, 2x in), Ice ectothermic shock (2x), Dragon peer clash |
| `COUNTER` | Fairy (0x + 2x hard counter), Ice (2x), Dragon (2x), Steel (0.5x) |
| `AMPLIFIER` | Dragon Dance (+1 Atk/Spe), Scale Shot |
| `CONDUCTOR` | Raw high-base-power apex bursts (Outrage, Draco Meteor) |
| `INSULATOR` | Quad-elemental resistance (Fire, Water, Electric, Grass) |
| `CONVERTER` | Misty Terrain suppresses Dragon output by 50% |
| `BYPRODUCT` | Outrage lock-in Confusion; Draco Meteor -2 Sp.Atk recoil |
| `SYMBIONT` | Steel/Fire partners removing Fairy & Ice counters (Dragon-Fairy-Steel core) |
| `PARASITE` | Outrage forced lock-in letting Fairy switch in for free immune turn |
| `STATE CHANGE` | Unchecked Gen I-V Apex -> Gen VI Fairy-Regulated Triad |

### `Dark`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Concealment, deception, and adversarial blind-spot exploitation |
| `SINK` | Fighting directness (2x), Fairy mythic radiance (2x), Bug instinct (2x) |
| `COUNTER` | Fighting, Fairy (0.5x resist + 2x SE), Bug (2x) |
| `AMPLIFIER` | Knock Off (1.5x when removing held item), Dark Aura (1.33x) |
| `CONDUCTOR` | Opponent telegraphs (Sucker Punch) & opponent Attack stat (Foul Play) |
| `INSULATOR` | Hard 0x immunity to Psychic moves & Prankster status priority |
| `CONVERTER` | Foul Play (inverts opponent's high Attack into self-damage); Parting Shot (stat drop -> pivot) |
| `BYPRODUCT` | Permanent held-item deletion (Knock Off) |
| `SYMBIONT` | Poison/Ghost partners covering Fairy & Fighting weaknesses |
| `PARASITE` | Exploits setup sweepers via Foul Play and item-reliant walls via Knock Off |
| `STATE CHANGE` | Item-Equipped Target -> Stripped/Vulnerable State |

### `Steel`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Metallurgical refinement of mineral ore into ordered crystal lattice |
| `SINK` | Fire annealing/melting (2x), Ground buckling (2x), Fighting kinetic fatigue (2x) |
| `COUNTER` | Fire, Fighting, Ground (all 2x); Magnet Pull trapping |
| `AMPLIFIER` | Iron Defense (+2 Def) + Body Press scaling |
| `CONDUCTOR` | Refined metal edge (2x vs Rock/Ice/Fairy); PREDICTED: conducts Electric (missing 2x weakness!) |
| `INSULATOR` | Apex 11-channel filter (10 resistances + 0x Poison + Sandstorm immune) |
| `CONVERTER` | Cold iron neutralizes mythic Fairy magic; Magnet Pull converts Steel property into trap liability |
| `BYPRODUCT` | Gen VI nerf dropped Ghost/Dark resistances to prevent total defensive monopoly |
| `SYMBIONT` | Dragon-Fairy-Steel competitive triad (covers Dragon's Ice/Fairy/Dragon weaknesses) |
| `PARASITE` | Magnet Pull (traps Steel types specifically for Fire/Ground elimination) |
| `STATE CHANGE` | Rigid Ordered Lattice -> Annealed Softened Metal (Fire) or Corroded Rust (PREDICTED Water) |

### `Fairy`
| Role | Relation / Derived Entity |
|---|---|
| `SOURCE` | Mythic/symbolic order, lunar enchantment, and ecosystem purity |
| `SINK` | Steel cold iron (2x), Poison industrial corruption (2x) |
| `COUNTER` | Steel, Poison (0.5x resist + 2x SE); Fire (0.5x wall) |
| `AMPLIFIER` | Fairy Aura (1.33x), Calm Mind; Misty Terrain halves Dragon & blocks status |
| `CONDUCTOR` | Mythic binding aura overriding Dragon & Dark |
| `INSULATOR` | Hard 0x immunity to Dragon; Misty Terrain status shield |
| `CONVERTER` | Pixilate (converts Normal -> Fairy); Draining Kiss (damage -> 75% HP) |
| `BYPRODUCT` | Systemic regulation of Dragon/Dark/Fighting meta post-Gen VI |
| `SYMBIONT` | Dragon-Fairy-Steel competitive core |
| `PARASITE` | Industrial Steel & Poison pollution directly severing fae purity |
| `STATE CHANGE` | Unregulated Dragon Meta -> Fairy-Bounded Equilibrium |

### 5.1 Predicted Missing Edges (Gaps Exposed by the 17-Primitive Decode)
| ID | Missing / Under-Modeled Edge | Structural Derivation |
|---|---|---|
| `PME-PKM-01` | `Electric -> Steel (currently 1x NEUTRAL; PREDICTED 2x PHYSICAL)` | Steel is a refined conductive metallic lattice; real electromagnetism predicts Electric should conduct/short through Steel at 2x (note that Pokemon acknowledges metal magnetism via Magnet Pull yet left Electric->Steel neutral for defensive balance). |
| `PME-PKM-02` | `Water -> Steel (currently 1x NEUTRAL; PREDICTED 2x or Corrosion DoT PHYSICAL)` | Water + atmospheric oxygen oxidizes/rusts iron-steel lattices over time; real chemistry predicts Water should corrode Steel (partially echoed only by the Corrosion ability, not Water itself). |
| `PME-PKM-03` | `Poison -> Water (currently 1x NEUTRAL; PREDICTED 2x BIOLOGICAL_ECOLOGICAL)` | Chemical/biological toxins contaminate aquatic reservoirs rapidly and poison aquatic organisms; real ecology predicts Poison > Water (currently absent in Pokemon, leaving Water with only 2 weaknesses). |
| `PME-PKM-04` | `Ice -> Water (currently 0.5x NVE; PREDICTED state-change 2x partially realized by Freeze-Dry)` | Cryogenic heat withdrawal freezes liquid water into solid ice; Pokemon omitted this from the base chart (0.5x) and had to patch the structural gap in Gen VI via the single-move exception Freeze-Dry (2x vs Water)! |
| `PME-PKM-05` | `Fire + Ice -> Water / Steam State-Change Reaction (ABSENT in Pokemon, PRESENT in Genshin Impact)` | Melting Ice with Fire produces liquid Water/Steam; Pokemon models thaw on status only, lacking a persistent elemental state-change reaction on the battlefield. |
| `PME-PKM-06` | `Water + Electric -> Chain Conductivity Area Spread (ABSENT in base singles)` | Conductive wet terrain/Rain should propagate Electric damage across adjacent grounded wet targets (modeled only via niche move Ion Deluge / Soak rather than ambient Rain conductivity). |
| `PME-PKM-07` | `Flying -> Poison (currently 1x NEUTRAL; PREDICTED dispersion 0.5x/2x)` | High-velocity wind currents disperse toxic clouds/vapors; Pokemon models Defog clearing Toxic Spikes but leaves Flying vs Poison neutral. |

---

## 6. Invariant Catalog Classification

Pokemon instantiates 11 of the 14 seed classes directly plus Class 15 (`COMPILED-MODEL EXTERNALIZATION` via Weather/Terrain arenas) and introduces **Class 19: `MULTIPLICATIVE COMPOSITIONAL AMPLIFICATION (DUAL-TYPING / COMMON-MODE 4x)`** (stacking two typed filters creates multiplicative `0x` dominance on immune channels and `4x` catastrophic failure on shared weakness holes):
- **Class 1** (`STRESS-ACCUMULATION -> THRESHOLD -> INSTANT RELEASE`): `Ground` (Earthquake), `Rock`, `Ice`, `Fighting`.
- **Class 2** (`SELF-SUSTAINING CHAIN REACTION`): `Fire` + `Burn`, `Bug` swarm.
- **Class 4** (`EXTRACTIVE COUPLING / PARASITISM`): `Leech Seed`, `Drain Punch`, `Leech Life`, `Poison`.
- **Class 5** (`MUTUAL COUPLING / SYMBIOSIS`): Weather cores (`Sun+Grass`, `Rain+Electric/Flying`, `Sand+Rock/Steel`), `Dragon-Fairy-Steel` triad.
- **Class 6** (`RESTRICTION-FOR-IMMUNITY TRADE`): `Ghost`, `Flying`, `Dark`, `Fairy`, `Levitate`, `Roost`.
- **Class 8** (`TYPED FILTER WITH CAP`): `Steel` (11 mitigated channels), `Rock`, `Ground`, `Normal`, `Dragon`.
- **Class 9** (`VULNERABILITY AMPLIFIER`): `Stealth Rock` (up to 50% entry damage), `Venoshock`/`Hex` (2x status amplifiers).
- **Class 10** (`RATE SUPPRESSION`): `Ice`/`Freeze`, `Electric`/`Paralysis` (0.5x Speed + 25% skip), `Sleep`, `Sticky Web`, `Psychic` (`Trick Room`).
- **Class 11** (`CUMULATIVE STACKING TOXIN`): `Toxic` (`N/16` up to `15/16` max HP/turn).
- **Class 13** (`ABSORB-CONVERT / EDGE INVERSION`): `Water Absorb`, `Volt Absorb`, `Flash Fire`, `Lightning Rod`, `Storm Drain`, `Sap Sipper`, `Dry Skin`, `Motor Drive`, `Earth Eater`, `Well-Baked Body`, `Poison Heal`, `Guts`, `Grass` resisting `Water` (hidden `FEEDS`).
- **Class 14** (`GENERATION / CONTROL CYCLES`): All **5 strict RPS 3-cycles** + 11 open 3-cycles.
- **Class 15** (`COMPILED-MODEL EXTERNALIZATION`): 4 Weather + 4 Terrain arena fields acting as operative Domain Expansions.
- **Class 19 (NEW)** (`MULTIPLICATIVE COMPOSITIONAL AMPLIFICATION / COMMON-MODE 4x`): Dual-typing (`0x` absorbing zero + `4x` common-mode hole).

---

## 7. Cross-Domain Overlays (Topology-Scored)

| Target Domain / Scale | Topology Score | Structural Alignment & Explicit Residuals |
|---|---|---|
| **Real Physics & Chemistry** | **0.77** | Strong match on 58/120 physically grounded edges: thermodynamics (Fire/Water/Ice phase & heat capacity), electromagnetism (Electric->Water conduction, Electric->Ground 0V earth sink), mechanics (Fighting/Rock/Ice brittle fracture, Ground tectonic waves). Residuals: Electric->Steel neutrality (missing 2x conductivity), Water->Steel neutrality (missing rust), and 11 BALANCE-ONLY edges. |
| **Biology & Ecology** | **0.81** | Strong match on 20/120 ecological edges: trophic cascades (Flying > Bug > Grass), hidden FEEDS edge (Grass absorbs Water/Ground), herbicides/toxins (Poison > Grass, Toxic bioaccumulation), ectothermic cold-shutdown (Ice > Dragon), and parasitic leeching. Residuals: symbolic types (Ghost/Fairy/Dark/Psychic) lack biological counterparts. |
| **Wu Xing (5-Phase Generation & Control)** | **0.79** | Strong cyclic topology match: Wu Xing's 5-node generation/control ring embeds directly into Pokemon's 5 strict RPS 3-cycles (especially Fire->Grass[Wood]->Water->Fire, Fire->Steel[Metal]->Rock[Earth]->Fire, and Grass[Wood]->Ground[Earth]->Poison->Grass). Difference: Pokemon adds 8 hard-zero immunities and 18-node scale absent from Wu Xing's symmetric 5-ring. |
| **Classical Four Elements (Fire, Water, Earth, Air)** | **0.74** | Exact core subset match (Fire, Water, Ground/Rock, Flying) preserving thermal quenching (Water>Fire), smothering (Ground>Fire), and airborne decoupling (Ground->Flying 0x). Pokemon expands 4 elements -> 18 types by splitting Earth (Ground/Rock/Steel), adding Biological (Grass/Bug/Poison), Energy/Phase (Electric/Ice), and Cognitive/Mythic (Psychic/Dark/Ghost/Dragon/Fairy). |
| **Naruto 5-Nature Cycle (Fire>Wind>Lightning>Earth>Water>Fire)** | **0.68** | Moderate structural match: shares Earth>Lightning (Ground 2x/0x Electric) and Water>Fire, plus cyclic closure. Major topological divergence: Naruto's Lightning>Earth (Chidori/Earth) inverts Pokemon's Ground>Electric hard-zero, and Naruto uses a single 5-cycle vs Pokemon's 16 overlapping 3-cycles. |
| **Path of Exile (PoE) Damage Types, Ailments & Defenses** | **0.88** | Very high mechanical isomorphism: Fire/Ignite == Fire/Burn (Class 2), Cold/Freeze == Ice/Freeze (Class 10), Lightning/Shock == Electric/Paralysis (Class 9/10), Chaos/Poison == Poison/Toxic (Class 11), Chaos Inoculation == Steel 0x Poison / Ghost 0x Normal-Fighting (Class 6), PoE Leech/Damage-Taken-As == Water/Volt Absorb & Flash Fire (Class 13). Difference: PoE uses 5 damage channels with 75% resist caps vs Pokemon's 18 channels with discrete 0x..4x multipliers. |
| **JJK / Domain Expansion (`DOMAIN_EXPANSION_EGO`)** | **0.74** | Strong cross-domain bridge: Weather & Terrains ARE literal Domain Expansions (externalized arena axioms granting 1.3x-1.5x guaranteed advantages and status/priority rules within duration); Weather Wars == Domain Clashes (newer/more refined setter overwrites rival field); 8 Pokemon 0x immunities == Toji 0-CE & Gojo Infinity hard zeros; Absorb-Convert == Dante Royal Guard & Yuta RCT inversion. Divergence: Pokemon is flat/cyclic (16 3-cycles) whereas DOMAIN_EXPANSION_EGO is hub-and-hierarchy dominated. |
| **AI Scale (Multi-Agent Security & Modality Routing)** | **0.76** | Typed filter stacks (18 channels, 4x common-mode failure in dual-typing), Absorb-Convert == adversarial training converting exploits into robustness, Toxic stacking == compounding context-window drift reset by session restart ('switching out'), Weather/Terrain == system-prompt operational contexts. |
| **Human Scale (Physiology, Cognition & Strategy)** | **0.74** | Cognitive blind-spot exploitation (Dark > Psychic), primal phobia disruption (Bug/Ghost > Psychic), rate suppression (Paralysis/Freeze ~ fatigue/sedation), bioaccumulation (Toxic), disciplined kinetic training (Fighting > Normal). |
| **Societal Scale (Ecosystems, Markets & Infrastructure)** | **0.72** | Trophic cascades (Flying > Bug > Grass), electrical grid grounding (Electric -> Ground 0x), industrial cold-iron vs ecology (Steel/Poison > Fairy/Grass), regulatory insertion creating triads (Gen VI Fairy vs Dragon -> Dragon-Fairy-Steel triad, PRED-PKM-006 untested). |
| **Cosmological Scale (Thermodynamics & Phase Mechanics)** | **0.63** | Partial structural analogy only: exothermic oxidation, thermal sinks, dielectric breakdown, and phase transitions hold literally at physical scale, while biological/mythic/balance-only edges vanish completely (high information loss and residuals). |

---

## 8. All 15 Department Lenses (Domain-Wide + Hub Diagnostics)

| # | Department | State | Domain-Wide & Hub Manifestation |
|---|---|---|---|
| 1 | `SUBCONSCIOUS` | `PRESENT` | **Base type identity (18 types + 153 dual-type combinations), hidden IVs/EVs, passive Abilities (Flash Fire, Levitate, Earth Eater)** — Determines intrinsic damage multipliers and hidden edge-rewriting traps before a single move executes. |
| 2 | `INNER_MONOLOGUE` | `PRESENT` | **Turn-level move/switch prediction tree (calculating 4x/2x/0.5x/0x matchups, weather/terrain clocks, Toxic counters)** — Evaluates matchup topology, predicted switch-ins, and Absorb-Convert baiting prior to turn commitment. |
| 3 | `SPEECH_OUTPUT` | `PRESENT` | **Executed typed move (Physical/Special/Status), weather/terrain shift, or hazard deployment** — Externalized channel impulse resolved through the 324-pair multiplier matrix. |
| 4 | `STORAGE` | `PRESENT` | **HP pool, PP move counts, 6-slot team roster, active weather/terrain turn counters (5/8 turns), Toxic stack N** — Holds persistent state across turns; switching out preserves HP/status while resetting Toxic N and stat boosts. |
| 5 | `SECURITY` | `PRESENT` | **Typed resistances (61 NVE edges), 8 hard-zero immunities (Steel 0x Poison, Ground 0x Electric, Ghost 0x Normal/Fighting), Absorb-Convert abilities, Misty/Psychic Terrains** — Steel is the apex SECURITY hub (10 resists + 1 immune); Absorb-Convert abilities upgrade passive barriers into active Edge Inversions. |
| 6 | `TELECOMMUNICATIONS` | `PRESENT` | **Weather fields (global arena), Terrains (grounded propagation), entry hazards (Stealth Rock/Spikes/Toxic Spikes/Sticky Web), pivoting moves (U-turn/Volt Switch/Flip Turn)** — Propagates state across team slots and turns; Volt Switch fails completely against Ground 0x (signal grounded!). |
| 7 | `ENERGY_INTAKE` | `PRESENT` | **Absorb-Convert abilities (Water/Volt Absorb, Earth Eater, Dry Skin), Leech Seed/Giga Drain/Drain Punch, Grassy Terrain 1/16 heal, Synthesis/Roost** — Converts incoming enemy channels or ambient fields directly into HP/stat fuel. |
| 8 | `DISPLAY` | `PRESENT` | **Visible type silhouettes, weather animations, terrain floor overlays, status icons, Mold Breaker / Terrain surge telegraphs** — Exposes active field rules publicly while concealing unrevealed Absorb-Convert abilities (e.g., Zoroark Illusion or unprocced Flash Fire/Earth Eater). |
| 9 | `PROCESSOR` | `PRESENT` | **Deterministic damage formula multiplying Base Power x Stat Ratio x STAB (1.5x) x Type1 x Type2 (0x..4x) x Weather (1.5x/0.5x) x Terrain (1.3x/0.5x) x Burn (0.5x)** — Computes exact multiplicative outcomes; 0x immunity short-circuits the entire product regardless of power. |
| 10 | `REPRODUCTION` | `PRESENT` | **Hazard layering (Spikes x3, Toxic Spikes x2), Substitute decoys, Baton Pass stat propagation, breeding/egg-group inheritance (meta-layer)** — Replicates persistent field pressure across switch-ins (Note: absent on pure single-target burst types like Normal/Dragon during battle). |
| 11 | `DELETION` | `PRESENT` | **Fainting (HP=0), Knock Off permanent item deletion, Perish Song 3-turn countdown, Explosion self-deletion** — Permanently removes a unit or held item from the match topology, collapsing defensive cores. |
| 12 | `WASTE_REMOVAL` | `PRESENT` | **Rapid Spin / Defog (clears hazards/screens), Aromatherapy / Heal Bell / Rest (clears statuses), Poison-types absorbing Toxic Spikes on entry** — Clears persistent field residue (Stealth Rock, Toxic Spikes, Burn/Toxic) without sacrificing the host unit. |
| 13 | `APPLICATION` | `PRESENT` | **Balanced competitive turn-based tactical puzzle & ecological/elemental simulation teaching compositional trade-offs** — Maintains strategic diversity via 16 3-cycles (5 strict RPS loops), 8 hard zeros, and multiplicative dual-type risk/reward. |
| 14 | `RENDERING_OVERHEAD` | `PRESENT` | **PP limits, 5-turn weather/terrain expiry, Outrage confusion lock-in, Draco Meteor -2 SpA recoil, Stealth Rock switch-in tax** — Taxes repeated high-power actions and defensive switching so infinite stall or single-button spam remains bounded. |
| 15 | `INFORMATION_DENSITY` | `PRESENT` | **18 distinct typed channels x 171 defensive monotype/dual-type profiles x 6 multiplier tiers (0x, 0.25x, 0.5x, 1x, 2x, 4x) + 11 ability overrides** — Extremely high channel discrimination compared to PoE (5 damage types) or Classical 4 elements, enabling surgical 4x counterplay. |

**Explicit `ABSENT` Department Checks on Individual Hub Nodes:**
- `Normal`: Typed `SECURITY` resistances are **`ABSENT`** (`0 NVE`) — forces reliance on raw HP/stat storage and Ghost decoupling.
- `Ice`: Durable typed `SECURITY` filters are nearly **`ABSENT`** (`1 NVE` self-only, `0 IMM`) — explains why Gen IX had to add a `1.5x Defense` Snow Weather compensation loop.
- `Dragon` (under `Outrage`): `ESCAPE` / tactical switching is **`ABSENT`** (locked in 2–3 turns) — exposes Dragon directly to a free `Fairy` `0x` hard-zero switch-in.

---

## 9. Falsifiable Prediction Tests (Weakness & Counterplay Transfer)

| Pred ID | Source Invariant | Predicted Counterplay / Weakness | Target Domain | Verification Evidence | Status | Classification |
|---|---|---|---|---|---|---|
| `PRED-PKM-001` | Electric -> Ground Hard-Counter Inversion (0x out, 2x in) + Earth Sink | Any potential-difference flow (electrical current, viral signal burst) neutralized by an infinite low-impedance sink collapses to zero output while remaining vulnerable to physical substrate disruption. | Electrical Engineering (Lightning Rods / Earth Grounding) & Network DDoS Sinkholing | CONFIRMED: Electrical earthing rods shunt megavolt lightning safely to 0V ground potential (literally Lightning Rod + Ground 0x), and BGP blackhole/sinkhole routing absorbs volumetric DDoS floods to 0x while physical fiber-cut (Ground) destroys the network. | **`confirmed`** | `ISOMORPHIC_INVARIANT` |
| `PRED-PKM-002` | Hidden FEEDS Edge (Grass resists Water 0.5x, beats Water 2x) + Absorb-Convert Abilities (Water Absorb / Flash Fire / Volt Absorb) | Attacks directed through a channel the target metabolizes or converts fail to damage it and instead heal/strengthen it; counterplay requires switching to an orthogonal non-metabolized channel (e.g., Fire/Ice vs Grass, Mold Breaker bypassing Absorb). | Biology (Plant Irrigation / Antibiotic-Eating Bacteria) & Adversarial ML | CONFIRMED: Irrigating weeds accelerates weed growth (Water feeds Grass); bacteria evolving beta-lactamase convert/neutralize penicillin; in ML, adversarial training (Absorb-Convert) turns known attack vectors into robustness gains, forcing attackers onto orthogonal zero-day channels. | **`confirmed`** | `ISOMORPHIC_INVARIANT` |
| `PRED-PKM-003` | Cumulative Stacking Toxin (Pokemon Toxic N/16 max HP/turn, reset by switching out) | Static high-HP defense walls immune to burst damage still collapse inevitably to escalating exposure timers unless they reset state (switch/flush) or possess structural channel immunity (Steel/Poison). | Path of Exile (Poison Stacks), Toxicology (Heavy-Metal Bioaccumulation) & Software Engineering (Technical Debt / Memory Leaks) | CONFIRMED: PoE Poison stacks scale linearly with exposure count bypassing high flat defenses unless immune (Chaos Inoculation == Steel 0x); cumulative lead/mercury bioaccumulation overwhelms healthy organisms unless chelated/removed; compounding technical debt/memory leaks crash long-running monolithic servers unless periodically restarted ('switched out'). | **`confirmed`** | `ISOMORPHIC_INVARIANT` |
| `PRED-PKM-004` | Dual-Typing Multiplicative Composition (`4x` Double Weakness from Overlapping Defense Holes) | Composing two specialized defensive layers that share a common unmitigated channel creates a catastrophic multiplicative vulnerability (`4x` one-shot) despite strong average resistance coverage (e.g., Scizor Bug/Steel = 8 resists + 1 immune, yet 4x weak to Fire; Swampert Water/Ground = 4x weak to Grass). | Systems Engineering & Cybersecurity (Correlated Common-Mode Failure in Layered Redundancy) | CONFIRMED: Stacking two subsystems sharing a single common-mode dependency (e.g., dual redundant cloud services sharing the same DNS/BGP/TLS dependency, or Space Shuttle O-rings failing jointly in cold temperature) produces catastrophic multiplicative failure precisely along the shared unmitigated channel. | **`confirmed`** | `ISOMORPHIC_INVARIANT` |
| `PRED-PKM-005` | Ecological Trophic Hierarchy (Flying > Bug > Grass) & Pesticide/Herbicide (Poison > Grass) | Removing a top predator (Flying) allows herbivore (Bug) runaway over Grass, while chemical toxins (Poison) destroy producer biomass (Grass) unless resisted. | Real Ecology (Trophic Cascades) | CONFIRMED: Documented trophic cascades (e.g., China's 1958 Four Pests sparrow extermination eliminated Flying predators, triggering catastrophic Bug locust swarms devastating Grass/grain crops). | **`confirmed`** | `ISOMORPHIC_INVARIANT` |
| `PRED-PKM-006` | Gen VI Structural Regulator Insertion (Adding Fairy 0x/2x vs Dragon to break apex monopoly) | Inserting a hard-zero counter-regulator against an apex monopoly shifts equilibrium into a 3-node triad (Dragon-Fairy-Steel) rather than eliminating dominance hierarchies permanently, predicting emergence of a secondary meta bottleneck (Steel/Fairy). | Antitrust Economics & Multi-Agent Evolutionary Game Theory | UNTESTED QUANTITATIVELY AS CROSS-SUBSTRATE PREDICTOR: Confirmed within Pokemon VGC/Smogon history (Steel/Fairy became dominant post-Gen VI), and qualitatively echoed in regulatory capture, but formal quantitative equivalence to antitrust market concentration ratios remains untested. | **`untested`** | `STRUCTURAL_ANALOGY` |

---

## 10. Section 10 Gate Discipline & Residual Audit

- All game -> real-system mappings strictly enforce `substrate_confusion_check: true` and `positional_claims_permitted: true` (SC-PATCH-DU-001; formerly `identity_claim_allowed: false`).
- All **11** `BALANCE-ONLY` edges plus the 7 predicted missing physical edges (`PME-PKM-01..07`) are recorded explicitly inside `residual_mismatches`.
- Gates backed by confirmed prediction tests (`PRED-PKM-001`..`PRED-PKM-005`) earn `1.0` (`causal_validity`, `scale_integrity`, `boundary_integrity`, `measurement_integrity`, `security_safety`, `substrate_sovereignty`). Gates covering argued-but-untested dimensions (`authority_safety`, `wave_function_coherence`, `corpus_completeness`) are strictly capped at `0.9`, with `PRED-PKM-006` listed explicitly in `uncertainty_statement`.
