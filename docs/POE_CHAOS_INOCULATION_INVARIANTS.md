# Single-buffer defense: the Path of Exile Chaos Inoculation invariant

Added 2026-11-06 as one domain template in `expansion/templates/`, and expanded the same day
in a second pass (see "Changelog" at the end):

| Domain | File | What it models |
|---|---|---|
| `poe_chaos_inoculation` | `poe_chaos_inoculation.yaml` | The Chaos Inoculation keystone (maximum life becomes 1, immune to chaos damage) and the defense built on top of it: an energy shield buffer, a delay-then-refill recharge, converted recovery, a closed bypass channel, and the mechanics the trade switches off. Second pass adds resource costs paid from the buffer and conditional item-granted bypass clauses. |

## The invariant in one paragraph

Chaos Inoculation (CI) is one indivisible trade. The lethal pool (life) is reduced to the
constant 1, so any damage that reaches it is fatal. The only thing between the character and
that pool is the energy shield buffer, and the one damage type that ignores the buffer in
PoE 1 (chaos) is made harmless by the immunity that comes with the keystone. Everything else in
the build is then a statement about that buffer: how big it is, how it refills, what recovery
is converted into it, which mechanics still scale off the *old* life value, and which
mechanics are lost because they need a life pool. A second pass adds that costs can be paid
from the buffer itself and that item clauses can open additional bypass channels that switch
on when the buffer is low.

## How to read the provenance

* Every **invariant** ends with one or more source tags, e.g. `[POEDB-CI]`, and names the game
  version it was sourced for (PoE 1, PoE 2, or both). The tags are defined in the table
  below. `tests/expansion/test_deep_system_templates.py` fails if an invariant has no tag or
  uses an undefined one.
* **Failure modes and architecture patterns are the template author's mappings**
  onto the medical ontology. They are derived from the invariants (what breaks if the
  invariant is violated), not quoted from the sources.
* Provenance is **page level**. A tag says the claim is stated by that document, not
  which paragraph.
* This is **research-derived and has not been reviewed by an expert player**. Treat it as a
  sourced first draft.

## Sources

| Tag | Source | URL |
|---|---|---|
| `POEDB-CI` | poedb (PoE 1), Chaos Inoculation keystone page | https://poedb.tw/us/Chaos_Inoculation |
| `FANDOM-EB` | Path of Exile fandom wiki, Eldritch Battery | https://pathofexile.fandom.com/wiki/Eldritch_Battery |
| `FANDOM-ES` | Path of Exile fandom wiki, Energy shield (revision 94370, a 2014 revision: structure only, its numbers are not used) | https://pathofexile.fandom.com/wiki/Energy_shield?diff=94370 |
| `MOBA-ES` | Mobalytics, Path of Exile 2 energy shield guide (January 4, 2025, early access) | https://mobalytics.gg/poe-2/guides/energy-shield |
| `SKEEDA-CI` | Sportskeeda, Path of Exile 2 Chaos Inoculation explained (undated, early access) | https://www.sportskeeda.com/mmo/path-exile-2-chaos-inoculation-explained |
| `POE2-PATCH-0-5-0` | Mobalytics, Path of Exile 2 patch 0.5.0 notes (dated 2026-06-08) | https://mobalytics.gg/poe-2/guides/0-5-patch-notes |
| `POE-FORUM-ES` | pathofexile.com forum thread on energy shield and life flasks (January 28-30, 2025) | https://www.pathofexile.com/forum/view-thread/3711951/page/2 |
| `FANDOM-CI` | Path of Exile fandom wiki (PoE 1), Chaos Inoculation keystone page: keystone text, mechanics notes and version history (read 2026-11-06; the page shows no last-edited date) | https://pathofexile.fandom.com/wiki/Chaos_Inoculation |
| `FEXTRA-POE2-050` | Fextralife Path of Exile 2 wiki, Patch Notes 0.5.x (0.5.0 through 0.5.5; page last edited 2026-09-22, read 2026-11-06) | https://pathofexile2.wiki.fextralife.com/Patch_Notes_050 |

## Structure versus literal mechanics (the guardrail)

The repository already states that its PoE layer preserves *structure*, not literal mechanics:
PoE rules are designed, deterministic and versioned by patch, and a mapping between a PoE
build and another system is only as good as the structural property that transfers. This
template follows the same rule from the other side.

* **What the template asserts as invariant** is the delay-rate-interrupt shape of recharge,
  the buffer-first routing with a bypass exception, the floor-and-convert design of CI, and
  the list of mechanics that need a life pool. These persisted across the versions read.
* **What the template treats as a patch-dependent parameter, not an invariant:** recharge
  delay, recharge rate, the factor by which chaos damages the buffer in PoE 2, any modifier
  value. The sources disagree across versions (PoE 1 halved the recharge rate in 3.5.0; PoE 2
  0.5.0 lowered many recharge modifiers), and one source (`FANDOM-ES`) is a 2014 revision.
  The invariant that mentions numbers is worded as "numbers are patch-dependent while the
  structure persists".
* **PoE 1 and PoE 2 differ in the bypass channel.** PoE 1: chaos damage ignores the buffer.
  PoE 2 (January 2025 guide): chaos damage removes twice as much buffer, and poison and
  bleeding skip the buffer. The invariants say which version each claim was sourced for. A
  consumer should not read a PoE 1 invariant as a PoE 2 rule or the reverse.

### What transfers to other systems, and what does not

| Structural property | Transfers to | Does not transfer |
|---|---|---|
| Reduce the fatal pool to a constant and put all defense into one buffer | Any system with a single "death" resource and a layered absorber (a circuit breaker on one fuse, a quota that kills a job at zero) | The specific value 1: it is a design number |
| Close the one channel that bypasses the buffer, then concentrate | Defense in depth: eliminate the unfiltered path first, then invest in the filter | That the bypass is a *damage type*: in other systems it is a path, a privilege or an interface |
| Refill only after a quiet period; any new damage restarts the clock | Rate limiters with a cool-down, health checks with a backoff | The delay and rate values, which differ by patch and by modifier |
| Convert every recovery mechanism into the buffer because the original pool cannot use it | Migrations where the old resource is capped and everything is routed to the new one | That the converters are specific items and keystones |
| Thresholds read the pre-override base while the lethal value stays at its floor | Systems where a display or safety value is overridden but derived limits should keep the original basis | That the PoE 2 0.5.0 note is a bug fix: a feature in one version, a defect in another |
| State the lost subsystems up front | Any irreversible trade-off decision | The exact list, which changes with each patch |

## Specification and derived properties (author reasoning, not sourced)

The section above is what the pages state. This section is the template author's
decompression of it: a small specification and the properties that follow from it. None of
it is a source claim, so none of it is in the template's `invariants` list. It is checked by
an executable toy model, `tests/expansion/test_poe_ci_reference_model.py`.

### The condition changes type

A life build survives on margins: over time, recovery keeps up with damage. With life fixed
at 1, survival becomes **for every damage event, damage to life is zero**. That is a rule
about every event, not an average, which is why the whole build becomes a buffer.

```
State:   L = 1 (constant)   E in [0, E_max]   t_quiet = time since damage was last taken
Event:   damage d of type τ
route(d, τ):
  τ ∈ Immune          → nothing happens; t_quiet is not reset
  τ ∈ Bypass \ Immune → straight to L → death
  otherwise           → E -= d · k(τ); any overflow below 0 → L → death
  any damage taken    → t_quiet = 0

Safety 1 (paths):    Bypass \ Immune = ∅
Safety 2 (capacity): for every event, d · k(τ) < E just before it (current, not maximum)
Refill:              E rises when t_quiet ≥ delay, or by converted recovery at any time
Patch-dependent:     delay, rate, k(τ), E_max
```

### What follows

1. **Safety 1 is the reference-monitor property.** Nothing reaches the protected pool
   without passing the buffer, the same structure as the `trust_chain` domain. Chaos
   immunity exists to close the PoE 1 bypass.
2. **In PoE 2 (January 2025 rules) the bypass set is effectively empty under CI.** Poison is
   chaos damage, so the immunity covers it. Bleeding is inflicted only by a hit that damages
   life, and at life 1 that hit is already lethal, so bleeding is never the first cause of
   death. The model checks this exhaustively over short sequences, and checks that it fails
   if that one bleeding rule is removed. **That rule is the one to re-verify against PoE 2
   0.5.x**; it rests on the January 2025 guide.
3. **The real killer is a race, not a single event** (`spike_after_chip`). Chip damage keeps
   resetting the delay, so the buffer stays below its maximum, then a hit the full buffer
   would absorb overflows. In the model the same three hits kill with no gaps and are
   survived with quiet gaps, and a thousand-fold faster recharge does not help.
4. **Refill is measured by gaps between hits, not by rate.** Recharge runs only in quiet
   time. Converted recovery (Ghost Reaver, Zealot's Oath, Eternal Youth) works during
   combat, so it removes the quiet-time requirement rather than only adding recovery. The
   model shows the chip-then-spike sequence survived with converted recovery alone.
5. **Fixing a value turns every condition on it into a constant**
   (`audit_predicates_on_fixed_value`). Low life is always false and full life always true:
   some of these are dead code, some are permanent effects.
6. **The threshold leak is a basis-versus-override bug.** Every calculation that reads the
   overridden value must say whether it wants the override (1) or the original basis. The
   PoE 2 0.5.0 note calls the leak a fix, so the designers treat it as a defect.
7. **Immunity closes a channel, not every channel** (`conditional_bypass_clause`). The
   pre-0.5.x Runemastered Revered Vestments clause shows that an item can open a bypass that
   has nothing to do with damage type. Because it switched on only below half buffer, it
   opened exactly when the margin was smallest. In the model, a hit the remaining buffer
   would absorb kills through the clause, and Safety 1 fails for CI under both rule sets once
   the clause is equipped. Safety 1 is therefore a property of the whole equipment set, not
   of the keystone.
8. **A cost paid from the buffer is damage the build chose to take**
   (`buffer_spent_as_cost`). Safety 2 reads the *current* buffer, so a cost paid just before a
   spike turns an absorbed hit into overflow. The model shows this whether or not paying the
   cost restarts the recharge delay; that rule was not found in any source read, and the model
   shows it only matters once there is quiet time to refill.
9. **The floor is applied last** (`apply_the_floor_last`). `FANDOM-CI` states that life
   reductions apply before the reset to 1. The failure mode `post_override_reduction` is
   the author's statement of what that ordering prevents; it is not a reported bug.

### The medical mapping is approximate here

The keystone component maps to `vaccination`. That is the nearest of the 17 canonical
concepts, but it is a poor fit: vaccination trains a learned response, while CI removes
the target the damage acts on, closer to a receptor knockout, and pays a large structural
price for it. The ontology has no concept for immunity by removing the target. Adding one
would change the ontology every template draws on, so it is left as an open decision.

## What was not read or not established

* **The wikis could not be fetched.** poewiki.net and poe2wiki.net answer automated clients
  with an access-denied page; poedb's energy shield page, poe2db and the fandom Chaos
  Inoculation page are not reachable from this environment. The sources above are the pages
  that could be read.
* **`FANDOM-ES` is a stale revision** (2014: a 6-second delay and a one-third-per-second rate
  are on that page). It is used for the structure (buffer first, delay, interrupt) and for
  nothing numeric.
* **Current PoE 1 recharge numbers were not verified.** The 3.5.0 halving is cited via
  `FANDOM-EB`; the resulting values were not read.
* **PoE 2 mechanics rest on a January 2025 guide** (early access). The 0.5.0 patch notes
  (June 2026) were read for the recharge-modifier change and the threshold fix only. The
  January 2025 claims about chaos, poison and bleeding were not re-verified against 0.5.x.
  **Second pass:** the full Fextralife 0.5.x page (0.5.0 through 0.5.5, the current patch,
  which that wiki dates to September 4, 2026) was read for Chaos Inoculation, chaos, poison
  and bleeding interactions with energy shield, the life override, Eternal Youth and
  Eldritch Battery. None of those rules is changed in those notes. That is the *absence of a
  change in patch notes*, not a positive confirmation of the January 2025 rules, so the
  bleeding derivation in property 2 still rests on `MOBA-ES`. An official-forum thread from
  December 2024 (https://www.pathofexile.com/forum/view-thread/3643766) has players
  disagreeing about exactly these rules and no developer reply; it is not cited.
* **Release-date disagreement.** `POE2-PATCH-0-5-0` is dated 2026-06-08 on Mobalytics, while
  the Fextralife patch-notes index gives the 0.5.0 release as May 29, 2026. The tag keeps the
  date of the page it cites.
* **PoE 1 currency (second pass).** The official 3.27.0 content update notes (October 23,
  2025) mention none of Chaos Inoculation, energy shield recharge, Ghost Reaver, Zealot's
  Oath or Eldritch Battery. The poedb 3.28.0 page was read up to its last 1,469 characters
  and contained none of them either. No 3.28.x hotfix notes were read, so the PoE 1
  invariants are current as of those pages, not verified against the latest hotfix.
* **Version coverage per tag:** `POEDB-CI` is PoE 1 only. `MOBA-ES`, `SKEEDA-CI` and
  `POE2-PATCH-0-5-0` are PoE 2. `FANDOM-ES` and `FANDOM-EB` are PoE 1. The Sportskeeda page
  states the Eldritch Battery anti-synergy for PoE 2, and says a life flask can still restore
  energy shield under Chaos Inoculation in PoE 2; it names the Ghostwraithe chestpiece, not
  Ghost Reaver, so the Sportskeeda page does not support the PoE 1 Ghost Reaver and Zealot's
  Oath clause; that clause is carried by `POEDB-CI`.
* **The Eternal Youth change is player-reported** in a forum thread, not stated by the
  developers in anything read. The template only says, for PoE 2 early access, that
  Eternal Youth lets life flasks restore energy shield.
* **The 0.5.0 threshold note is directionally ambiguous.** It says the override of maximum
  life to one was incorrectly affecting stun and ailment thresholds and was fixed. Whether
  that makes a CI character more or less stunnable was not established, so no such claim is
  made. The PoE 1 invariant (thresholds use pre-override life) comes from `POEDB-CI`.
* **"Chaos bypasses the buffer, therefore CI" is the author's inference.** The sources
  state the facts (chaos ignores the buffer in PoE 1; CI grants chaos immunity); they do not
  state that this is why the keystone exists. The pattern name
  `close_the_bypass_then_concentrate` is a mapping, not a quotation.
* **`decompress` does not read the input's meaning.** Pathology detection compares the
  template's own component names and concepts with the template's own failure-mode text
  (`expansion/pathology/profiles.py`), so the five PoE calibration samples all produce the
  same ten of the eleven failure modes at confidence 0.6, whatever the sample says (measured
  after the second pass; it was seven of eight before). The one left out,
  `self_inflicted_life_drain`, is still not surfaced even with the new `resource_costs`
  component; the component text was not reworded to force a match. The toy model in `tests/expansion/test_poe_ci_reference_model.py` is the part
  that does reason about specific damage sequences; it is a test, not wired into `decompress`.
  This is the existing engine behavior for every template; the template was not reworded to
  change it.
* No PoE 1 interaction testing was done; every claim is what a page states.

## Engine changes that ship with the template

* `expansion/__init__.py`: `_DOMAIN_KEYWORDS` has one new group, after `trust_chain` and ahead
  of `computation`: `chaos inoculation`, `energy shield`, `eldritch battery`, `ghost reaver`.
  Bare `path of exile` is deliberately **not** a keyword: the Buildcraft and gem-decode
  layers use PoE shorthand to describe *computation* builds (Ice Nova, Cospri's Malice,
  Dying Sun), and those texts must keep routing as before. The test suite pins that for every
  pre-existing calibration sample and for the gem-decode PoE spec. The remaining risk is the
  reverse one: `energy shield` also appears in other games and in fiction, and a text using it
  that way routes here. Routing is vocabulary-based, as for every other domain; narrow it
  further (for example to require a second PoE term) if that proves noisy.
* No schema change: the optional `medical_map` field on components was added with the
  deep-system templates and is reused here.
* Component concepts (`vaccination`, `immune_system`, `homeostasis`, `treatment`,
  `prognosis`, `quarantine`) are disjoint from failure-mode concepts (`acute`, `pathogen`,
  `chronic`, `sepsis`, `metastasis`, `autoimmune`, `inflammation`). `detect_pathologies`
  treats a shared concept as direct evidence (0.75), so an overlap would raise a failure
  mode's confidence for reasons unrelated to the input. A test enforces the separation.

## Changelog

* **2026-11-06, first version.** Template, this note, contract tests and the toy reference
  model.
* **2026-11-06, second pass (expansion).**
  * Sources: added `FANDOM-CI` (PoE 1 keystone page) and `FEXTRA-POE2-050` (PoE 2 0.5.x notes).
  * Invariants: seven added (15 to 22): the stable keystone text and the removed energy shield
    bonus, life reductions before the override, Blood Magic as an excluded subsystem,
    Valyrium moving stun threshold to energy shield, an item-granted bypass clause, delay and
    rate as separately tuned parameters, and energy shield as a skill cost.
  * Components: `resource_costs` and `bypass_clauses`, with edges `draws_down` and
    `adds_exception_to`. Neither has a `medical_map`, so both decompress as `unknown`.
  * Failure modes: `conditional_bypass_clause`, `buffer_spent_as_cost`,
    `post_override_reduction`; `unclosed_bypass_channel` gained the indicator
    `item_granted_bypass`.
  * Patterns: `apply_the_floor_last`, `audit_bypass_clauses_not_only_damage_types`,
    `budget_buffer_spending_against_spikes`.
  * Reference model: an item bypass clause and an `es_cost` event, with six new tests;
    derived properties 7 to 9 above.
  * Not changed: router keywords, schema, ontology, frozen paths (`core/`, `registry/`).
  * Deliberately not added: analogies from fiction. The template is sourced game rules; a
    cross-domain analogy belongs in a separate note, not in `invariants`.
