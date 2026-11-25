---
name: invariant-translator
description: >-
  Whole-domain decompression and cross-domain ontology translator for the Reflexion
  Semantic Compiler. Use liberally whenever asked to decompress, decode, or translate
  a domain, mechanic, game system, biological/physical/social process, or AI behavior
  into exhaustive node/edge graphs, 17-primitive mechanical invariants, grounded edge
  classifications, cross-domain topology overlays, all 15 department lenses, falsifiable
  prediction tests, and validated SC-DE-001-format JSONL entries that grow INVARIANT_CATALOG.md
  and DOMAIN_LEDGER.md.
---

# Invariant Translator: Whole-Domain Decompression

The unit of work is a **whole domain**, not a single mechanic. When given one thing ("fire", "Chaos Inoculation", "Pokemon"), identify its parent domain, enumerate **every** element and **every** interaction between them, decode why each interaction holds, derive implied/missing edges, and translate the whole graph into other domains. Every compiled invariant goes into a growing catalog (**Soul Eater effect**: each new entry cross-links to all prior entries).

**Hard Rules:**
- Expand the domain yourself. Never stop at user examples, never write `"etc."`, and never hand expansion back to the user.
- If a domain exceeds one pass, record progress in `DOMAIN_LEDGER.md` and continue across passes until coverage reaches **100%**.
- **Args:** A domain, a phenomenon, or a list, plus optional target domains. With no explicit targets, translate across the four scales (**AI · Human (body & mind) · Societal · Cosmological/physical**), the default overlays in Section 7, and any domain the user names.

---

## 0. Load the Schematics

1. Read the canonical JSONL template:
   - `~/semantic_compiler_kernel/calibration_output/compiled_entries/DOMAIN_EXPANSION_COMPILER_ENTRY_SC-DE-001.jsonl` (keep the exact field structure).
2. Read `INVARIANT_CATALOG.md` and `DOMAIN_LEDGER.md` if they exist in `~/semantic_compiler_kernel/docs/invariant_catalog/` (the canonical catalog directory; resume unfinished domains, reuse already-compiled node invariants, and extend existing catalog classes instead of duplicating them).
3. Fetch the domain's **complete, authoritative rule source** (web search / official rule table / wiki / patch notes / textbook taxonomy). Record source, version/generation, and date. Tag every fact `source-fact`, `common-reading`, or `mapping`.

## 1. Enumerate the Full Ontology (Exhaustive, With Count Check)

List every element in every category:
- **Nodes:** types, elements, damage types, species, forces, institutions, domain atoms.
- **Modifiers:** statuses, ailments, weather/fields, keystones, terrain, stacking states, edge-rewriting abilities.
- **Resources & pools:** life, ES, energy, fuel, nutrients, money, attention.
- **Rules:** multipliers, caps, immunities, thresholds, timers, recharge delays.

State exact counts (e.g., `18 types -> 324 attacker x defender pairs`). Coverage must reach **100%** before synthesis. Log progress in `DOMAIN_LEDGER.md`.

## 2. Build the Interaction Graph & Topology

Compute every pair using all applicable edge types:
`BEATS` · `RESISTS` · `IMMUNE` · `NEUTRAL` · `FEEDS/FUELS` · `DRAINS` · `CONVERTS_INTO` · `PRODUCES` · `REQUIRES` · `AMPLIFIES` · `SUPPRESSES` · `CONDUCTS` · `INSULATES` · `PARASITIZES` · `SYMBIOTIC_WITH` · `CONTAINS` · `TRANSFORMS_UNDER`.

Extract **graph topology** (this is what transfers across domains):
- Cycles (rock-paper-scissors loops, Wu Xing generation/control cycles)
- Hierarchies & dominance chains
- Immunity edges (hard zeros)
- Self-resist and self-weak nodes
- Hubs (highest degree), isolated nodes, and asymmetric pairs
- Offensive and defensive profiles per node (counts of SE, NVE, immune — in and out)

## 3. Decode Every Node Through the 17-Primitive Grammar

State what each node *is* mechanically (the physical, biological, or structural process underneath the name), then populate all 17 primitives (`POOL`, `CAPACITY / CAP`, `INFLOW / REGEN`, `OUTFLOW / DRAIN`, `CHANNEL / TYPE`, `FILTER / MITIGATION`, `THRESHOLD`, `TRIGGER`, `RELEASE`, `PROPAGATION`, `TRADE / RESTRICTION`, `IMMUNITY`, `CONTROL LOOP`, `ESCAPE`, `HOST / COUPLING`, `FAILURE MODE`, `COUNTERPLAY`). Write `N/A` when truly absent; absence is data.

See [primitive_grammar_and_catalog.md](./references/primitive_grammar_and_catalog.md) for the full 17-primitive questionnaire, reference node invariants, PoE reference domain, and all 14 seed catalog classes.

## 4. Decode Every Edge & Classify Its Grounding

For each non-neutral edge, explain it via the two node invariants and classify its grounding:
- **`PHYSICAL`**: Follows from real mechanics (e.g., Water > Fire absorbs heat + smothers oxygen; Electric > Water conductive medium; Ground immune to Electric earth sink; Grass resists Water = hidden `FEEDS` edge; Fire > Steel anneals/softens lattice).
- **`BIOLOGICAL / ECOLOGICAL`**: Herbivory (Bug > Grass), predation (Flying > Bug), herbicide (Poison > Grass).
- **`SYMBOLIC / MYTHIC`**: Fairy > Dragon (mythic order binds raw power), Dark immune to Psychic, Ghost immune to Normal.
- **`BALANCE-ONLY`**: Game design only, zero external invariant. State plainly — these MUST become `residual_mismatches`, never forced mappings.

## 5. Closure: Derive Implied & Missing Edges

For every node, populate all 11 relation roles (from the domain if stated; otherwise derived from the node invariant and marked **`PREDICTED`**):
`SOURCE` · `SINK` · `COUNTER` · `AMPLIFIER` · `CONDUCTOR` · `INSULATOR` · `CONVERTER` · `BYPRODUCT` · `SYMBIONT` · `PARASITE` · `STATE CHANGE`.

List every **predicted edge the domain is missing** — those gaps are design space and test the decode.

## 6. Classify Against `INVARIANT_CATALOG.md`

Match each node, modifier, and subgraph primitive signature to the 14 seed classes in [primitive_grammar_and_catalog.md](./references/primitive_grammar_and_catalog.md) (one phenomenon can instantiate multiple classes). If nothing fits, define a new class with its primitive signature and add it to `INVARIANT_CATALOG.md`.

## 7. Cross-Domain Overlay (Compare Graphs, Not Names)

Map the whole graph onto the 4 scales (**AI · Human · Societal · Cosmological**) plus default overlays:
- Real physics & chemistry (thermodynamics, electromagnetism, phase changes)
- Biology (pathogen/immune, predator/prey, mutualism/parasitism, cancer as regulation escape)
- Wu Xing (generation `wood->fire->earth->metal->water->wood`; control `wood->earth->water->fire->metal->wood`)
- Classical four elements
- Naruto nature cycle (`fire > wind > lightning > earth > water > fire`)
- PoE damage types, ailments, and defense layers
- Any system named by the user or echoed by the domain (Avatar, Genshin reactions, JJK, DMC styles)

Score structural matches on **topology** (cycles, immunity zeros, hubs), not surface names. Emit `translations` (`nouns`, `functions`, `relationships`, `failure_modes`) in `SC-DE-001` format.

## 8. Department Lenses (All 15)

Answer all 15 departments (`SUBCONSCIOUS`, `INNER_MONOLOGUE`, `SPEECH_OUTPUT`, `STORAGE`, `SECURITY`, `TELECOMMUNICATIONS`, `ENERGY_INTAKE`, `DISPLAY`, `PROCESSOR`, `REPRODUCTION`, `DELETION`, `WASTE_REMOVAL`, `APPLICATION`, `RENDERING_OVERHEAD`, `INFORMATION_DENSITY`) for the domain as a whole and for every hub node at each scale. Mark truly absent counterparts `ABSENT` and explain what the absence implies.

## 9. Prediction Test (Makes It an Invariant)

A real invariant transfers **weaknesses and counterplay**, not just strengths:
1. Take a source counterplay or failure mode and predict its counterpart in the target domain.
2. Verify whether the target actually exhibits it (cite concrete evidence / known example).
3. **Confirmed** -> `ISOMORPHIC_INVARIANT`. **Strength-only match** -> `STRUCTURAL_ANALOGY`. **Prediction fails** -> record in `residual_mismatches` and explain where structure breaks.

## 10. Gate Discipline

- Use the 9 gates from `SC-DE-001`.
- Whenever `information_lost` is non-empty, `residual_mismatches` MUST NOT be empty.
- A gate score of `1.0` requires `evidence_ids` pointing to a **passed prediction test**; argued-but-untested gates cap at **`0.9`**.
- Cross-substrate mappings (including fiction/game -> real-system) MUST set `substrate_confusion_check: true` and `positional_claims_permitted: true` (SC-PATCH-DU-001, replaces the former identity-claim gate):
  - `substrate_confusion_check: true` for cross-substrate mappings.
  - Blocks: "X IS Y's material" (substrate confusion).
  - Permits: "X occupies position P in the structure" (positional awareness).
  - Test: is the claim about what something is MADE OF, or WHERE it SITS?
  - Positional claims asserting exclusive/permanent authority are FLAGGED for review (the position is reproducible).
- `BALANCE-ONLY` edges are ALWAYS recorded as `residual_mismatches`.
- `uncertainty_statement` MUST list every untested prediction.

## 11. Emit, Validate & Grow the Catalog

Write all outputs into `~/semantic_compiler_kernel/docs/invariant_catalog/` and run its `validate_catalog.py` before finishing.
1. Emit `DOMAIN_DECODE_<DOMAIN>.md` (ontology + counts, full interaction matrix, topology, node invariants & 17-primitive tables, grounded edge decodes, closure table, predicted missing edges, overlays with topology scores, all 15 departments).
2. Emit `INVARIANT_ENTRY_SC-IT-<DOMAIN>-001.jsonl` in exact `SC-DE-001` format (`compiler_mode: "UNIVERSAL_DECOMPRESSION"`, `framework: "Systemic Isomorphic Invariants"`, `version: "3.5.0"`, `source: "Shax (Curtis Kingsley) — Reflexion Software"`), plus extra `SC-IT-<SLUG>-001` entries for standalone hub nodes. Only cross-reference entry IDs that actually exist.
3. Update `INVARIANT_CATALOG.md` (signature, cross-domain instances with entry IDs, predictions with `confirmed`/`untested`/`failed` status, class compositions).
4. Update `DOMAIN_LEDGER.md` (domain, source/version, coverage %, passes done, remaining scope).
5. **Validate before finishing:** JSON parses cleanly, matrix counts match ontology counts 100%, all 15 departments present, residual & gate-cap rules enforced, every cross-reference ID resolves.
6. **Batch Mode:** When given multiple domains/phenomena, compile each one and emit `INVARIANT_ENTRY_SC-IT-BATCH-<YYYY-MM-DD>.jsonl` with shared primitives, compositions, and cross-domain counterplay matrix.

## References

- [17-Primitive Grammar, Reference Invariants & 14 Seed Catalog Classes](./references/primitive_grammar_and_catalog.md)
- [Seed Domain: Pokemon Gen 6+ 18-Type Chart & Modifiers](./references/pokemon_seed_chart.md)
