# Seed Domain: Pokemon Type Chart (Gen 6+ — Verify Against Current Authoritative Source)

**Ontology Count Check:** 18 types -> **324** `attacker x defender` pairs.

## Type Effectiveness Chart (Attacker -> Super Effective (2x) / Not Very Effective (0.5x) / No Effect (0x))

| Attacker | Super Effective (`2x`) | Not Very Effective (`0.5x`) | No Effect (`0x` IMMUNE) |
|---|---|---|---|
| **Normal** | — | Rock, Steel | Ghost |
| **Fire** | Grass, Ice, Bug, Steel | Fire, Water, Rock, Dragon | — |
| **Water** | Fire, Ground, Rock | Water, Grass, Dragon | — |
| **Electric** | Water, Flying | Electric, Grass, Dragon | Ground |
| **Grass** | Water, Ground, Rock | Fire, Grass, Poison, Flying, Bug, Dragon, Steel | — |
| **Ice** | Grass, Ground, Flying, Dragon | Fire, Water, Ice, Steel | — |
| **Fighting** | Normal, Ice, Rock, Dark, Steel | Poison, Flying, Psychic, Bug, Fairy | Ghost |
| **Poison** | Grass, Fairy | Poison, Ground, Rock, Ghost | Steel |
| **Ground** | Fire, Electric, Poison, Rock, Steel | Grass, Bug | Flying |
| **Flying** | Grass, Fighting, Bug | Electric, Rock, Steel | — |
| **Psychic** | Fighting, Poison | Psychic, Steel | Dark |
| **Bug** | Grass, Psychic, Dark | Fire, Fighting, Poison, Flying, Ghost, Steel, Fairy | — |
| **Rock** | Fire, Ice, Flying, Bug | Fighting, Ground, Steel | — |
| **Ghost** | Psychic, Ghost | Dark | Normal |
| **Dragon** | Dragon | Steel | Fairy |
| **Dark** | Psychic, Ghost | Fighting, Dark, Fairy | — |
| **Steel** | Ice, Rock, Fairy | Fire, Water, Electric, Steel | — |
| **Fairy** | Fighting, Dragon, Dark | Fire, Poison, Steel | — |

## Modifiers Required for 100% Domain Coverage

- **Weather:** Harsh Sunlight (Sun), Rain, Sandstorm (Sand), Snow (Gen 9; Hail in Gen 6–8).
- **Terrain:** Electric Terrain, Grassy Terrain, Misty Terrain, Psychic Terrain.
- **Non-Volatile Statuses:** Burn, Poison, Badly Poisoned (Toxic stacking), Paralysis, Sleep, Freeze.
- **Edge-Rewriting / Absorb-Convert Abilities:** Flash Fire, Water Absorb, Volt Absorb, Lightning Rod, Storm Drain, Sap Sipper, Levitate (plus Dry Skin, Motor Drive, Earth Eater, Well-Baked Body where verified in Gen 9).
- **Dual-Typing:** Multiplicative node composition (`4x`, `2x`, `1x`, `0.5x`, `0.25x`, `0x` dominance).
