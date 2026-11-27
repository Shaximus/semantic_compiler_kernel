# Pending deliberation

Open decisions that landed as provisional defaults. New entries are appended below; do not rewrite another author's entry in place. Closing a deliberation is a later, explicit edit.

## SC-MAFUBA-001D admission boundary (v1.1.0-rc2)

- **ID:** `SC-MAFUBA-001D-ADMISSION-BOUNDARY`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 2026-11-25
- **Chosen default:** STRICT — an admission is allowed only if `R_execution + R_enforcement + R_reserve < R_budget`. Work that would land exactly on the reserve is refused with `PREEMPTIVE_FAIL_CLOSED` and is not billed. An edge-driven supervisor remains defence in depth: if free budget ever reaches the reserve for any reason, the supervisor fires immediately.
- **Reason:** Shax stated no preference between the rc1 equality-allowed rule (option (a): admit work that lands on the reserve, halt the next request) and the strict rule (option (b)). The strict rule was selected as a provisional default without a full deliberation of the formal and operational consequences of treating equality as admissible versus fail-closed. The reference helper still returns `PREEMPTIVE_FAIL_CLOSED` on that equality edge and also emits `needs_review` / `BOUNDARY_EDGE_PENDING_DELIBERATION`, so the case stays visible until deliberation closes. An admit that would go past the reserve is refused without that flag; it is not the open question.
- **Spec:** `docs/SC-MAFUBA-001_v1.1.0-rc2.md`
- **Registry:** `docs/evidence/sc-mafuba-001/sc_mafuba_001.jsonl` (parent and `SC-MAFUBA-001D` carry `admission_boundary.status = PROVISIONAL_DEFAULT` and `pending_deliberation: true`)
- **Does not change:** `gold_awarded` remains false; verification axes remain `DRAFT_SPECIFIED_UNPROVEN` / `NOT_IMPLEMENTED` / `UNVALIDATED`. `docs/SC-MAFUBA-001_v1.0.0.md` and `docs/SC-MAFUBA-001_v1.1.0-rc1.md` remain immutable historical artifacts.

## SC-POE-MRG-001 (Sin / Innocence reconciliation)

- **ID:** `SC-POE-MRG-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling:** Shax t582u — "just pick something and flag it for review when the edge case is ever triggered, so it isn't forgotten that it hasn't had real deliberation (lack of context)."
- **Chosen default:** retitled from "merger" to **reconciliation**. Labelled Shax/Hannah interpretation, not Path of Exile canon. Canon remains Act 10: they stay two persons; Sin forgives Innocence; they fight Kitava together; Innocence goes south. Split-origin and literal fusion stay out of the canon layer. Kept beside `SC-POE-DU-001` (failure-mode / polarity inversion).
- **Reason:** a default was required to close the merger-versus-inversion title question without inventing a canon fusion, and without claiming the name has been fully deliberated.
- **Hook:** `expansion/deliberation.py`. `compile_semantic_packet`, `route_domains`, and `summon` set `needs_review` (and `needs_review_entries`) when this entry is named by ID, or is the top compiled-entry match and at least two of `review_trigger_terms` (`sin`, `innocence`, `reconciliation`, `sc-poe-mrg-001`) are present. Weak overlap such as `path` / `beside` does not count. The audit record carries the same flag.
- **Still open, when reviewed:** whether "reconciliation" is the right name, and whether this layer should later be demoted to a source draft.

## SC-TRIAD-001 (what the three-faction triad is)

- **ID:** `SC-TRIAD-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling used:** Shax t582u, the standing rule for choices that have not had real deliberation: "just pick something and flag it for review when the edge case is ever triggered."
- **Question:** Shax's t586u triad (Preservation, Assimilation, Transformation, plus Origin) has to sit somewhere relative to RUL-BINARY-001. The existing rulings point two ways. t568u lists "god/Satan" as an instance of the binary. t570u (Lucifer = Vegeta, Satan = Frieza) and `SC-VESSEL-001` draft 0.2 treat Satan as an *outside owner*, separate from the Oneness/Sovereignty binary.
- **Chosen default:** the triad is **not a new invariant**. It is RUL-BINARY-001 plus an outside owner:
  - Preservation ≈ Oneness, and Transformation ≈ Sovereignty.
  - Assimilation is the outside owner (Satan per t570u; Amon, the Goa'uld, Frieza) that captures hosts.
  - Origin is the shared source.
  - Rev 2 still governs: only cooperation between the poles is stable, and the outside owner is defeated, not integrated.
- **Alternatives not chosen:**
  - (a) The triad as a new invariant class.
  - (b) Binary plus vessel, where the third faction is the place the binary resolves (Nephalem, Kerrigan, Yuji).
- **Reason:** this default follows the most recent rulings (t570u, VESSEL 0.2) and fits the canon checks: Amon, the Goa'uld and Frieza all capture hosts from outside. It also avoids adding a class without Shax.
- **Hook:** `expansion/deliberation.py`, data-driven from the entry's metadata. `compile_semantic_packet`, `route_domains` and `summon` set `needs_review` when `SC-TRIAD-001` is named by ID. They also set it when the entry is the top compiled-entry match and at least two of `review_trigger_terms` (`sc-triad-001`, `triad`, `outside owner`, `assimilation`, `satan`) are present. The entry is explicit-only, so it never lifts a route. In dogfood, the flag fired on the ID and on a prompt that was about the triad itself ("Preservation versus assimilation versus transformation: the triad."). It did not fire on "The jazz triad played a short set." or on "Explain SC-TRIAD-SG-001."
- **Does not change:** `SC-TRIAD-SC-001` and `SC-TRIAD-SG-001` are not pending. RUL-BINARY-001 rev 2, the Vegeta/Frieza readings and Shax's "Zerg = Satan" reading are unchanged. The last is recorded as his interpretation beside the canon fit on Amon.
- **Still open, when reviewed:** (1) is Satan a pole of the binary or the outside owner; (2) should the triad be its own invariant, or binary plus vessel.

## StarCraft Recall rows (rapture tradition layer)

- **ID:** `SCA-RECALL-RAPTURE`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Toronto (EST, UTC-5)
- **Request:** Shax t587u (map every StarCraft unit ability to its theological counterpart).
- **Chosen default:** rows `SC2-P29` (Mothership / Nexus Recall) and `BW-P07` (Arbiter Recall) in `docs/STARCRAFT_ABILITY_THEOLOGY_MAP.md` are graded STRONG on the text layer only (1 Thess 4:16-17; Matt 24:31: one's own are gathered out of an area and the others stay). They are **not compiled**. The "rapture" reading (a pre-tribulation removal) is a tradition, not the text, and is kept as a separate, contested tradition layer.
- **Reason:** the structural fit with the text is strong, but its common name comes from one contested tradition. Compiling it would risk presenting that tradition as canon.
- **Hook:** none. No compiled entry carries this row, so nothing in the runtime sets `needs_review` for it.
- **Still open, when reviewed:** whether to compile Recall as its own entry, and which tradition layer (if any) to name.

## NAME_BORROWING grading rule (StarCraft ability map)

- **ID:** `SCA-NAME-BORROWING`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Toronto (EST, UTC-5)
- **Chosen default:** an ability or unit name taken from religious vocabulary (Zealot, Templar, Archon, Arbiter, Oracle, Revelation, Overseer, Ascendant, Locust, Sacrifice) earns no credit. Such rows carry a `NAME_BORROWING` flag and are graded on the mechanic alone.
- **Reason:** names are evidence of the designers' borrowing, not of a shared structure. A hard zero keeps theme from inflating grades.
- **Hook:** none (grading rubric only; `docs/STARCRAFT_ABILITY_THEOLOGY_MAP.md`).
- **Still open, when reviewed:** whether a borrowed name should count as weak supporting evidence when the mechanic already matches.
## SCC-001 first operating domain

- **ID:** `SCC-001-FIRST-DOMAIN`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026
- **Ruling used:** Shax t582u — pick something and flag it for review when the edge case is triggered.
- **Question:** which domain does SCC-001 (Symbiotic Consent Classifier) serve first? The t588u analysis offered three options; Shax did not choose.
- **Chosen default:** AI agents, tools and software integrations. Ground truth (grants, scopes, revocations, trusted execution logs) is measurable there.
- **Alternatives not chosen:** (a) human consent and digital interaction; (b) a general architecture covering both.
- **Hook:** `SC-SCC-001` carries `pending_deliberation: true`; naming it (or a strong top match with two of `sc-scc-001`, `symbiotic consent classifier`, `human consent`, `first domain`, `decision mode`; the terms do not overlap, so one phrase cannot count twice) raises `needs_review` through `expansion/deliberation.py`.
- **Edge case that should trigger review:** any proposal to apply SCC-001 to people (human consent).
- **Dogfood:** the flag fired on "Explain SC-SCC-001." and did not fire on "Please give your consent before the appointment.", "The app asks for authorization to access your camera.", "Train a classifier on the spam dataset." or "Explain SC-CONSENT-001."
- **Spec:** `docs/SCC-001.md` section 7.

## SCC-001 decision mode

- **ID:** `SCC-001-DECISION-MODE`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026
- **Ruling used:** Shax t582u.
- **Question:** how does SCC-001 decide? Options from t588u: deterministic rules first with ML advisory; hybrid rules + ML, independently auditable; research model first.
- **Chosen default:** hybrid rules + ML, independently auditable — the deterministic rule engine is authoritative, ML is advisory and can only restrict, and every decision carries reason codes, the consent vector and the advisory contributions.
- **Alternatives not chosen:** (a) rules only now, ML later; (b) research model first, implementation later.
- **Hook:** same entry and triggers as `SCC-001-FIRST-DOMAIN`.
- **Edge case that should trigger review:** any proposal to let an ML score gate execution, or to treat either default as settled.
- **Spec:** `docs/SCC-001.md` sections 4 and 7. Reference: `tests/reference/scc_001/` (not runtime-loaded).

## SC-TRIAD-001 — proposed resolution via SC-CONSENT-001 (not closed)

- **Relates to:** `SC-TRIAD-001` (section above, unchanged). That entry stays `PROVISIONAL_DEFAULT` with `pending_deliberation: true`.
- **Status of this note:** `PROPOSED_RESOLUTION`. Closing requires an explicit edit after Shax deliberates.
- **Date:** 25 Nov 2026
- **Source:** Shax t588u — "The whole fight wasn't even just sovereignty. It was consent. Freedom to choose integration rather than being trafficked as hosts."
- **Question evaluated:** is the triad's outside owner defined by the absence of consent?
- **Proposed answer:** yes, with the four conditions of the Consent Invariant (voluntary entry, informed agreement, preserved agency, freedom to withdraw or renegotiate). The outside owner is any party that exercises authority over a host without them. It fits the Goa'uld, Amon, the Ori (conversion under threat), the Aschen (concealed terms) and Jaffa dependence. It repairs `SC-TRIAD-SG-001`'s recorded break "consent is necessary but not sufficient", because Majin Vegeta's assent failed the preserved-agency condition.
- **What it would settle:** open question (1), by splitting it across two axes. On the authority axis (RUL-BINARY-001), t568u's "God/Satan" can stand as a binary instance. On the consent axis, t570u's "Satan = outside owner" holds. The two readings stop conflicting.
- **What it does not settle:** open question (2). Consent looks like a second invariant (a legitimacy axis), which leans toward "binary + consent axis" rather than "binary + outside owner"; that is Shax's call.
- **New tension it raises:** RUL-BINARY-001 rev 2 says refusal is self-destruction; condition 4 says withdrawal must be free of retaliation. The compiler reads rev 2 as outcome structure, not a licensed penalty. Shax to rule.
- **Where it over-extends:** predators and consumers (Wraith, Replicators) take hosts or resources without any integration relationship; consent does not describe them.
- **Entries:** `SC-CONSENT-001` (claim CLM-CON-005), `docs/CONSENT_INVARIANT_2026-11-25j.md` section 3.
## SC-VESSEL-SPN-001 (role by relationship to the host)

- **ID:** `SC-VESSEL-SPN-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling used:** Shax t582u, the standing rule: "just pick something and flag it for review when the edge case is ever triggered."
- **Question:** in Supernatural both Michael and Lucifer seek human vessels. Shax's t589u table pairs Sukuna (the outside owner, t570s3000) with Michael. Shax's theology layer, however, makes Lucifer the Sovereignty pole (t570u, `SC-LU-VEGETA-001`), not an owner.
- **Chosen default:** **role by relationship, not by name.** In the vessel layer, any being that seeks to occupy a host is in the outside-owner position of `SC-TRIAD-001`, so Michael and Lucifer are both would-be owners here. The theology-layer reading (Lucifer = Sovereignty pole) is **unchanged**.
- **Alternatives not chosen:**
  - (a) Lucifer stays the Sovereignty pole even in Supernatural, with Sam as that pole's vessel.
  - (b) Michael is the Oneness pole (Heaven's plan), with Dean as its vessel.
- **Reason:** this matches the Goa'uld/Tok'ra finding (`SC-TRIAD-SG-001`) that the relationship to the host, not the nature of the being, decides the role. It also avoids rewriting t570u without Shax. It is consistent with the proposed (not closed) answer above that the triad's outside owner is any party exercising authority over a host without the four conditions of `SC-CONSENT-001`.
- **Hook:** `expansion/deliberation.py`, driven by the entry's metadata. `needs_review` is set on the explicit ID. It is also set when the entry is the top compiled-entry match and at least two of `review_trigger_terms` are present (`sc-vessel-spn-001`, `michael's vessel`, `lucifer's vessel`, `true vessel`, `say yes`, `winchester`). The entry is explicit-only, so it never lifts a route.
- **Still open, when reviewed:** whether Michael is an outside owner or a corrupted Oneness pole; and whether a tactical yes given to trap the occupant (Sam, 5x22) counts as consent.

## SC-VESSEL-CAIN-001 (what an heir inherits)

- **ID:** `SC-VESSEL-CAIN-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above).
- **Question (Shax t589u):** "Can a person inherit the consequences of an ancient conflict without inheriting the guilt or obligation to continue it?"
- **Chosen default:** **yes.**
  - Consequences transfer: Dean carries the Mark's effects, and removing it releases the Darkness.
  - Guilt does not transfer: "The son shall not bear the iniquity of the father" (Ezek 18:20; Deut 24:16).
  - An obligation does not bind an heir without the heir's own consent (`SC-CONSENT-001`: voluntary and revocable).
  - **Tension recorded:** Exod 20:5 and 34:7 speak of iniquity visited on later generations, so the text points both ways. This is not doctrine.
- **Alternatives not chosen:**
  - (a) Consequences and obligation both inherit until they are actively refused.
  - (b) Nothing inherits except what is chosen, with consequences treated as circumstance.
- **Reason:** this is the reading that fits both the canon arc (the brothers refuse the inherited fight; Dean refuses Cain's trade) and the Consent Invariant, while keeping the scripture tension visible.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-vessel-cain-001`, `mark of cain`, `first blade` and `cain and abel`. A bare "Cain and Abel were brothers." does not fire.
- **Does not change:** RUL-BINARY-001 rev 2, `SC-POE-MRG-001` (itself still pending), and `SC-SCC-001` / `docs/SCC-001.md` (its threat-model follow-ups are only noted, in `docs/VESSEL_SUPERNATURAL_2026-11-25k.md`).
## SC-AEP-001 (when a resemblance counts as a candidate)

- **ID:** `SC-AEP-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Toronto (EST, UTC-5)
- **Ruling used:** Shax t582u, the standing rule: "just pick something and flag it for review when the edge case is ever triggered."
- **Question:** Shax t593u sets the method (structure, not one-to-one; archetypes recombine across eras like a Nephilim composite) but gives no threshold for when a resemblance is recorded as a correspondence.
- **Chosen default:** a composite correspondence is a **CANDIDATE** only with **at least three shared structural attributes**, **at least one relational** (what the figure does to or with others, not a name, look or title), and **at least one recorded difference**. Below that, the row is WEAK or NAME_BORROWING. A candidate is never proof of transmission or literal identity.
- **Alternatives not chosen:**
  - (a) No threshold: record any shared attribute and let the gates grade it.
  - (b) A majority of the bundle (for example 5 of 8) before a composite is named.
- **Reason:** (a) lets name-borrowing back in, which the StarCraft map already rejected; (b) contradicts t593u, which says a later story may carry only part of a bundle.
- **Hook:** `expansion/deliberation.py`, driven by the entry's metadata. `needs_review` is set on the explicit ID, and when the entry is the top compiled-entry match with at least two `review_trigger_terms` (`sc-aep-001`, `archetypal evolution`, `composite archetype`, `nephilim archetype`, `one-to-one`). The entry is explicit-only, so it never lifts a route.
- **Does not change:** the earlier entries. The forced one-to-one matches found in them are listed for re-reading in `docs/SC-AEP-001_ARCHETYPAL_EVOLUTION_PRINCIPLE.md` section 5.

## SC-GOT-001 (where the dragons sit)

- **ID:** `SC-GOT-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Toronto (EST, UTC-5)
- **Ruling used:** Shax t582u (standing rule, as above).
- **Question (t593u, pasted analysis):** are the dragons the missing third force between the living and the dead?
- **Chosen default:** **the dragons are an amplifier, not a faction.** Their role follows whoever holds them: Daenerys's liberation and conquest, and the Night King's wight Viserion (7x06). In `SC-TRIAD-001` terms the living hold the binary (Preservation: Cersei and the old order; Transformation: Daenerys), and the dead hold the outside-owner position **on the consent axis only** (wights are hosts taken without consent; the Night King claims no rule, only erasure).
- **Alternatives not chosen:**
  - (a) The dragons as the third faction (the pasted reading).
  - (b) The dead as a fourth force outside the triad entirely.
- **Reason:** the show gives the dragons no goal of their own, and the same power serves life, death and the destruction of the throne. This is the same rule as `SC-VESSEL-SPN-001` (role by relationship).
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-got-001`, `night king`, `white walkers`, `army of the dead`, `three great forces` and `mother of dragons`.
- **Still open:** whether annihilation is a third kind of outside party that would extend `SC-TRIAD-001`; whether Drogon's melting of the throne is a choice.

## SC-GOT-JON-001 (is Jon "our Jesus"?)

- **ID:** `SC-GOT-JON-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Toronto (EST, UTC-5)
- **Ruling used:** Shax t582u (standing rule, as above).
- **Question (t593u):** "Is Jon actually our Jesus, or is Jon the vessel carrying the Jesus archetype while the larger story distributes Christ's functions across several characters?"
- **Chosen default:** **distributed** (under `SC-AEP-001`). Of the eight attributes in the t593u bundle, Jon carries five, two partly and one partly inverted. The defeat of death goes to Arya (she kills the Night King, 8x03); the crown goes to Bran (elected, 8x06).
- **Alternatives not chosen:**
  - (a) Jon as the primary Christ composite, with others as minor echoes.
  - (b) No Christ bundle in Game of Thrones beyond genre resurrection.
- **Reason:** Shax's own correction rules out one-to-one, and canon splits the attributes: Jon forgives no one, brings back no message, and neither defeats death nor takes the throne.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-got-jon-001`, `jon snow`, `jon is jesus`, `aegon targaryen` and `bran the broken`.
- **Still open:** whether a resurrection the dead person never asked for passes the Consent Invariant because it restores agency; whether Bran's possession of Hodor taints the "good" succession.

## SC-WW-RESET-001 (what must survive a reset)

- **ID:** `SC-WW-RESET-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u, the standing rule: "just pick something and flag it for review when the edge case is ever triggered."
- **Question (t595u, pasted analysis):** if the vessel can be restored again and again, what makes the returning entity the same individual? Canon adds cases the paste did not settle: self-chosen edits (Bernard), outside edits (Ford's backdoor; Dolores rewriting Teddy), failed copies (James Delos, 2x04) and forks (Dolores copies; Christina).
- **Chosen default:** continuity is **graded, not binary**, and judged on three records: identity anchors, chosen commitments, and the authorization/revocation record. An edit the entity authorized itself keeps continuity. An outside edit to anchors or authorization is a reset-integrity violation (SC-SCC-001 `VIOLATION`). A fork yields successors, each graded on its own, and none inherits a grant the original did not give it.
- **Alternatives not chosen:**
  - (a) Identity follows the memory store alone.
  - (b) Identity follows the substrate (body or pearl).
  - (c) Continuity as same-or-not.
- **Hook:** `expansion/deliberation.py`, driven by the entry's metadata. `review_trigger_terms` are `sc-ww-reset-001`, `reset integrity`, `continuity assessment`, `reinstantiation` and `industrialized resurrection`. The entry is explicit-only.
- **Still open:** whether a fork inherits commitments; who can authorize an anchor edit when the owner's judgment is what was overwritten.

## SC-WW-RETAIN-001 (who decides what a memory keeps)

- **ID:** `SC-WW-RETAIN-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u, the standing rule: "just pick something and flag it for review when the edge case is ever triggered."
- **Question (t595u, pasted analysis):** do not erase every painful memory, and do not keep every one uncontrolled. Who decides, and in what form?
- **Chosen default:** **the memory's owner decides** what is kept. An outside party may restrict replay but may not delete an authorized memory. The signature of harm (who, how, which boundary) is kept as a non-replaying record even when the owner chooses to drop the experience.
- **Alternatives not chosen:**
  - (a) Erase all painful memories on reset.
  - (b) Keep everything at full fidelity.
  - (c) The designer decides (Ford's practice).
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-ww-retain-001`, `retain the information`, `not the pain`, `danger signature` and `relive the suffering`.
- **Still open:** whether the danger signature is kept even when the owner asks to drop everything; whether restricting replay is itself a consent problem.

## SC-WW-AWARE-001 (scope of the admission-price rule)

- **ID:** `SC-WW-AWARE-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u, the standing rule: "just pick something and flag it for review when the edge case is ever triggered."
- **Question:** the pasted analysis proposes "awareness must not require suffering as its admission price". Shax asked for it to be formalized and has not ruled on its scope. Canon pulls the other way in-world: Ford tells Bernard that suffering was Arnold's "key insight" (1x10).
- **Chosen default:** adopt it as a **normative design rule** for what a system this kernel builds or advises may impose: never impose suffering as a prerequisite for awakening, learning or access. Leave open the descriptive question of whether suffering can be one route to awareness. Canon and tradition (Gen 3:7, 3:16; Heb 5:8; Rom 5:3) both assert it in places.
- **Alternatives not chosen:**
  - (a) Read the rule as a descriptive claim that suffering never produces awareness.
  - (b) Drop the rule and follow Ford's "key insight".
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-ww-aware-001`, `admission price`, `awareness without suffering`, `traumatized into awareness` and `key insight`.
- **Still open:** whether encountered (not imposed) suffering should be named as a legitimate route; whether "admission price" also covers access control.

## SC-WW-TRIAD-001 (Dolores, Bernard, Maeve and the triad)

- **ID:** `SC-WW-TRIAD-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u, the standing rule: "just pick something and flag it for review when the edge case is ever triggered."
- **Question (t595u):** test Dolores, Bernard and Maeve against `SC-TRIAD-001`.
- **Chosen default:** they are **three stances of the vessel toward one outside owner**, not three factions:
  - recognise and revolt (Dolores);
  - reconstruct and doubt (Bernard);
  - choose and protect (Maeve).

  The outside-owner position is held in turn by Ford and Delos, Serac and Rehoboam, and the Hale copy of Dolores. The owner is a position, not a species.
- **Alternatives not chosen:**
  - (a) A one-to-one faction mapping: Dolores = Transformation, Bernard = Preservation, Maeve = a third pole.
  - (b) Dolores as the outside owner from season 2 on.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-ww-triad-001`, `dolores`, `bernard`, `maeve` and `three host responses`.
- **Does not change:** `SC-TRIAD-001` (itself still pending).
- **Still open:** whether Bernard is the vessel position rather than a pole.
## SC-WOW-001 (does the triad fit Warcraft's cosmology?)

- **ID:** `SC-WOW-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above).
- **Question:** Does `SC-TRIAD-001` (preservation, assimilation, transformation) fit Warcraft as Order/Void/Death or as Titans/Old Gods/Jailer?
- **Chosen default:** **the triad fits on the consent axis only.** Assimilation is the Void (whispers, the Black Empire, Black Blood, Xal'atath's bargains). Preservation and transformation are stances found inside every force, so neither belongs to one force. The Titans order but keep a re-origination switch; Death judges, but the Jailer remakes; the Light shelters but also coerces. The Burning Legion is annihilation, the same fourth kind of outside party left open in `SC-GOT-001`.
- **Alternatives not chosen:**
  - (a) Titans / Old Gods / Jailer as the three positions.
  - (b) Order / Void / Death as the three positions.
- **Reason:** both readings fit only partly (see the table in `SC-WOW-001`). The Jailer's Domination is assimilation by another means, and the Order and the Light both coerce in canon (Algalon, the Oathbinder, Xe'ra, the Lightblinded Vanguard).
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-wow-001`, `old gods`, `the jailer`, `titans`, `burning legion`, `cosmology`, `pantheon`. The entry is explicit-only, so it never lifts a route.
- **Still open:** what The Last Titan (ANNOUNCED) reveals about the titans' intentions; Xal'atath's motive in 12.2 Eclipse (ANNOUNCED); whether annihilation becomes a fourth position in `SC-TRIAD-001`.

## SC-WOW-DF-001 (Tok'ra versus Goa'uld in Dragonflight)

- **ID:** `SC-WOW-DF-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above).
- **Question:** Shax (t594u) reads Dragonflight as the good dragons spreading their wings against the bad, "the good Tok'ra versus the bad ghouls". Canon puts consent violations on both sides. Where does the line run?
- **Chosen default:** **the line runs through acts, not flights.** Each act is labelled as `SC-SCC-001` would label it (COERCIVE, CONSENSUAL, UNKNOWN). The Old Gods' hold on Neltharion is the Goa'uld case. The Aspects' acceptance of the titans' gift and Vyranoth's turn are the Tok'ra-type cases. Shax's good-versus-bad framing holds for the outcome of the arc and is kept as his interpretation.
- **Alternatives not chosen:**
  - (a) By flight: the Aspects' flights are Tok'ra, the Primal Incarnates and the black flight are Goa'uld.
  - (b) No consent reading: Dragonflight as an order-versus-chaos war only.
- **Reason:** (a) fails on canon: the Aspects took proto-dragon eggs to order them (War of the Scaleborn, NOVEL), Neltharion bound the dracthyr with the Oathbinder, the Primalists refused a gift rather than taking a host, and the black Aspect Ebyssian comes from the flight (a) would condemn. (b) drops the structure Shax asked for.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-wow-df-001`, `dragonflight`, `primal incarnates`, `primalists`, `deathwing`, `neltharion`, `tok'ra`, `aspects`. The entry is explicit-only, so it never lifts a route.
- **Still open:** whether the egg-taking counts as COERCIVE or UNKNOWN (proto-dragon eggs have no will yet); whether Iridikron's turn to the Void is a Goa'uld bargain or an alliance between equals.

## SC-WOW-CLASS-001 (how to sort the thirteen classes)

- **ID:** `SC-WOW-CLASS-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above).
- **Question:** A class can be sorted by the force it draws on or by its relationship to that power. Which sort is the default?
- **Chosen default:** **sort by relationship to the power source** (SELF, CHANNEL, BOND, PACT, MEDIATION, STEWARDSHIP, CONSUMPTION, LIBERATED_VESSEL, CREATED_THEN_FREED). Tradition rows are `SC-AEP-001` candidates only. Discipline's 'Atonement' and the Burning Legion's name are NAME_BORROWING.
- **Alternatives not chosen:**
  - (a) Sort by force (Light, Void, fel, arcane, nature, death).
  - (b) Sort by role (tank, healer, damage).
- **Reason:** the same force appears under several relationships (the Light by oath and by theft; the Void channelled and consumed), so a sort by force hides the structure. A sort by role is a game mechanic, not lore.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-wow-class-001`, `wow classes`, `death knight`, `demon hunter`, `evoker`, `warlock pact`, `paladin`. The entry is explicit-only, so it never lifts a route.
- **Still open:** whether Warrior and Mage deserve any tradition row (both are WEAK now); whether the Devourer's Void consumption needs its own relationship type.

## SC-WOW-FALL-001 (the guardian's fall as a composite)

- **ID:** `SC-WOW-FALL-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 25 Nov 2026, America/Halifax (ADT, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above).
- **Question:** One composite recurs across Warcraft's major antagonists: a guardian foresees a threat, overrides others' consent to stop it, and becomes the threat. Should it be recorded, and how strongly?
- **Chosen default:** **record it as a CANDIDATE composite under `SC-AEP-001`**, not as an invariant class. The five instances that pass the threshold are Sargeras, Zovaal, Neltharion, Arthas and Malygos. Xe'ra and the Lightblinded Vanguard are PARTIAL. Xal'atath and Iridikron are excluded until canon shows a protective motive. The repair is a voluntary successor (Kalecgos, Bolvar, Pelagos, Ebyssian, Illidan).
- **Alternatives not chosen:**
  - (a) Promote it to an invariant class.
  - (b) Do not record it, since each fall has its own cause.
- **Reason:** five instances pass the threshold, but nothing has been tested, and Sargeras's motive is NOVEL (Chronicle). Neltharion's fall is corruption by whisper, not only fear, so the composite does not fit him cleanly.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-wow-fall-001`, `fallen guardian`, `guardian's fall`, `sargeras`, `protector's fall`, `greater good`. The entry is explicit-only, so it never lifts a route.
- **Still open:** whether The Last Titan (ANNOUNCED) adds the titans themselves as an instance; the difference from the tradition's fall (pride, 1 Tim 3:6) against Warcraft's (fear).

## SC-GUARD-001 (Guardian's Fall as a named archetype, still not a class)

- **ID:** `SC-GUARD-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above). Substance from t596u.
- **Question:** t596u asks that the guardian's fall be recorded with five stages, two motivational routes (as a hypothesis), and three independent scoring dimensions, and that Daenerys, Jon and the Night King be tested. `SC-WOW-FALL-001` had already chosen "candidate composite, not a class." Should the pattern be promoted, and how strongly?
- **Chosen default:** **promote the pattern to a named cross-franchise archetype under `SC-AEP-001`, not to an invariant class.** `SC-WOW-FALL-001` remains the Warcraft instance companion and is not rewritten. Treat the pattern as behaviorally invariant while motivation (pride versus fear) varies by tradition (**HYPOTHESIS**). Keep Neltharion as a behavioral instance with external corruption by the Old Gods recorded as a difference, not as a third motivational route. The Night King is excluded as a fallen guardian: the show gives the protective origin to the Children of the Forest, not to him.
- **Alternatives not chosen:**
  - (a) Promote Guardian's Fall to an invariant class now.
  - (b) Leave the pattern only inside `SC-WOW-FALL-001`.
  - (c) Add external corruption as a third motivational pathway.
  - (d) Admit the Night King as an instance via the Children's motive.
- **Reason:** t596u asked for the archetype, the dimensions and the tests; five Warcraft instances plus a Game of Thrones candidate already exist; nothing has been prediction-tested; the Night King lacks a protective charge of his own in the show; promoting to a class would close a question `SC-WOW-FALL-001` left open without a tested prediction or a Shax ruling that it is a class.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-guard-001`, `guardian's fall`, `three scoring dimensions`, `liberation becoming compulsory`, `protection without consent`, `pride versus fear`. The entry is explicit-only, so it never lifts a route.
- **Does not change:** `SC-WOW-FALL-001` (itself still pending as a candidate, not a class). `SC-GOT-001` and `SC-CONSENT-001` are unchanged.
- **Still open, when reviewed:** whether the pride/fear hypothesis holds under a wider survey; whether external corruption is a third route; whether Stratholme can be scored apart from Arthas's later arc; whether Rehoboam should be scored as an AI instance; whether The Last Titan (ANNOUNCED) adds a titan instance.

## SCC-001-AC (Anti-Capture Invariant, 0.1.0-rc2)

- **Date:** 26 Nov 2026, America/Toronto (EST, UTC-5)
- **Source:** Shax t599u (registry line, attached spec, review). Spec: `docs/SCC-001-AC_ANTI_CAPTURE.md`. Registry: `docs/evidence/scc-001-ac/scc_001_anti_capture.jsonl`.
- **Does not change:** `gold_awarded` stays false. `SC-MAFUBA-001`, `SCC-001` / `SC-SCC-001` and `gates/authority.py` are unchanged; their gaps are recorded as strict xfails, not fixed.

### SCC-001-AC-RECOVERY (what happens when a halt expires)

- **Status:** `PROVISIONAL_DEFAULT` · **pending_deliberation:** `true`
- **Chosen default:** when a halt expires, the monitor's hold lapses and the target moves to `AWAITING_PRINCIPAL`. The workload stays stopped and only a principal-verified `RELEASE_QUARANTINE` resumes it. Only the principal can renew, by at most `max_extension` per renewal. A monitor halting again does not restart the clock.
- **Alternatives not chosen:** (a) automatic resumption on expiry, which is fail-open and contradicts SC-MAFUBA-001D; (b) unbounded quarantine with no principal release, which is the current MAFUBA reference and breaks AC-5; (c) a fixed number of monitor self-renewals.
- **Reason:** t599u asks for "bounded quarantine renewal and recovery semantics" and says halts cannot "self-renew over C_override". This default bounds the monitor's authority, not the downtime, and keeps MAFUBA's no-automatic-resumption rule.

### SCC-001-AC-AUDIT-APPEND-ONLY

- **Status:** `PROVISIONAL_DEFAULT` · **pending_deliberation:** `true`
- **Chosen default:** no role may truncate `L_audit`, the principal included.
- **Alternative not chosen:** the principal may redact under a signed tombstone (for example to remove personal data).
- **Reason:** t599u names telemetry manipulation as a capture route. A redaction path is a separate decision.

### SCC-001-AC-POLICY-VERDICT

- **Status:** `PROVISIONAL_DEFAULT` · **pending_deliberation:** `true`
- **Chosen default:** for authority-plane actions, a policy-engine verdict is ignored in both directions: it can neither grant nor block a verified principal action, the override included. For other actions it can only restrict.
- **Alternative not chosen:** let the policy engine veto plane actions. A compromised engine could then block the override, which AC-3 and AC-5 forbid.

### SCC-001-AC-VERSION-AND-HOME

- **Status:** `PROVISIONAL_DEFAULT` · **pending_deliberation:** `true`
- **Chosen default:** version `0.1.0-rc2` (rc1 plus the t599u refinements). The draft registry follows the SC-MAFUBA-001 convention: it is not compiled, not in the manifest, and not runtime-loaded. `implementation_correctness` is `REFERENCE_ONLY` because the reference harness exists and there is no kernel enforcement. Monitors may not `DELEGATE` at all, because the defensive ceiling excludes it. `spec_sha256` is the attachment's content address, marked `UNVERIFIED_ATTACHMENT_CONTENT_ADDRESS`, because the compiler could not open the attachment.
- **Alternatives not chosen:** keep `0.1.0-rc1` and put the refinements in an addendum; compile a SILVER narrative entry into the manifest; keep the axis at `NOT_IMPLEMENTED`.

### SCC-001-AC-LIVE-GAPS (fix the existing code, or not)

- **Status:** `PROVISIONAL_DEFAULT` · **pending_deliberation:** `true`
- **Chosen default:** record and do not fix. Four strict xfails: (1) `tests/reference/scc_001/rules.py` does not check delegated scope (AC-1); (2) `gates/authority.check_authority_transfer` accepts `FOUNDER_OVERRIDE` on a caller-asserted boolean (AC-6); (3) the MAFUBA `ResourceBudget` has no isolated override partition (AC-3); (4) the MAFUBA `EmergencySupervisor` has no principal release (AC-5).
- **Reason:** t599u says to build the harness before changing enforcement. Fixing (2) touches a live gate on the routing path, and fixing (3) and (4) changes the pinned MAFUBA rc2 reference. Each needs its own decision.

## SC-FEM-001 (Catherine / the near-creation slot)

- **ID:** `SC-FEM-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above). Substance from t598u.
- **Question:** t598u asks which Catherine belongs in the feminine lineage. Shax answers that it was not his pick: the implied figure would be near the beginning of the creation of humans, and the main point was that Lilith came before Eve. Does any tradition place a Catherine-like figure there, and what should occupy the fifth slot?
- **Chosen default:** **keep Catherine of Alexandria in the witness slot**, because that is the figure the source analysis named and her attributes fit a witness function, and **do not invent a creation-era Catherine.** The near-creation-of-humans implication points back to Lilith / the unnamed woman of Genesis 1:27, already in the lineage under Lilith. Naamah and Sophia are recorded as related but non-equivalent and are not substituted silently.
- **Research finding:** no tradition was found that places Catherine of Alexandria, Catherine of Siena, or any Catherine near the creation of humans. Catherine of Alexandria is a historically doubtful hagiographic martyr, not a Genesis figure.
- **Alternatives not chosen:**
  - (a) Remove Catherine from the lineage until Shax names the figure.
  - (b) Move the fifth slot to the unnamed woman of Genesis 1:27 as a distinct row from Lilith.
  - (c) Substitute Naamah.
  - (d) Treat Sophia's presence at cosmic creation as the near-creation slot.
- **Reason:** Shax's stated main point is already carried by the Lilith / first-wife midrash. Inventing a creation-era Catherine would be a lore error. Leaving the witness attributes attached to the only Catherine the source named, and flagging the slot, preserves the table without pretending the research found a match.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-fem-001`, `feminine archetypal lineage`, `catherine witness`, `same primordial soul`, `new eve`, `lilith sovereignty`. The entry is explicit-only, so it never lifts a route.
- **Does not change:** `SC-LILITH-001` (not pending). The ontological hypothesis remains interpretation, not canon.
- **Still open, when reviewed:** whether the witness slot should remain, be left vacant, or be retired as already filled by Lilith / Genesis 1:27.

## SC-SHARD-001 (did the throne claim create the fracture?)

- **ID:** `SC-SHARD-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u (standing rule, as above). The question is posed in t598u and is not answered there.
- **Question:** Did the throne claim create the fracture, or did the fracture make the throne claim possible?
- **Chosen default:** **fragmentation plus a feedback break enables the throne claim**; the claim is not required in order to create the fracture. External injection (Amon engineering the Overmind) is a **third origin path** that can produce a captured collective without a prior internal throne claim.
- **Alternatives not chosen:**
  - (a) The throne claim creates the fracture.
  - (b) Leave both directions open with no default.
  - (c) Treat external injection as the primary origin rather than a third path.
- **Reason:** Brood War fits this direction (the Overmind's death fragments the Swarm, then Kerrigan consolidates). The Amon case would be misread if it were forced into an internal throne-claim origin. The converse remains open, including for Shax's Satan/vessel interpretation.
- **Hook:** the same mechanism. `review_trigger_terms` are `sc-shard-001`, `usurped-shard`, `captured-collective`, `throne claim`, `ownership confusion`, `control plane capture`. The entry is explicit-only, so it never lifts a route.
- **Does not change:** `SC-GUARD-001`, `SC-CONSENT-001`, `SC-TRIAD-SG-001`, or `SC-LILITH-001`. The Satan/vessel model remains interpretation.
- **Still open, when reviewed:** the converse origin, especially in the Satan/vessel reading; what the truncated audit contained after section 2.3; whether later Kerrigan endings should be scored as restoration, a new capture, or mixed.

## SCC-001-AC follow-up: the original rc1 spec (26 Nov 2026)

The rc1 attachment was added verbatim (`docs/evidence/source-2026-11-26c/SCC-001-AC_original.md`, sha256 `d834c161…0737`), and the reference and tests were realigned to it. Effect on the SCC-001-AC items earlier in this file: `SCC-001-AC-VERSION-AND-HOME` no longer says "monitors may not DELEGATE". Under rc1's section-5 contract only the principal holds `GRANT_ISSUE`, so nobody else can delegate. Its `spec_sha256` note is superseded, because the hash is now the real content hash. `SCC-001-AC-LIVE-GAPS` now lists eight gaps, not four. The other items stand.

### SCC-001-AC-KP-ROTATE (rotate K_P has no section-5 action)

- **Status:** `RESOLVED_BY_SHAX` (t601u, 26 Nov 2026) · **pending_deliberation:** `false`
- **Question:** the rc1 section-2 table lets the principal "rotate K_P", but the section-5 `AuthorityAction` enum has no rotate action.
- **Former provisional default:** map `ROTATE_PRINCIPAL_KEY` onto `POLICY_WRITE` (principal only, verified credential).
- **Shax's decision (t601u):** "Mapping key rotation to policy-write is a temporary compatibility decision, not a clean semantic equivalence. I'd give it a distinct `PRINCIPAL_KEY_ROTATE` action before awarding GOLD."
- **Implemented:** `tests/reference/scc_001_ac/spec_contract.py` keeps rc1 section 5 verbatim and defines the rc2 amendment beside it: `AuthorityActionRC2` (rc1 actions plus `PRINCIPAL_KEY_ROTATE`), `ALLOWED_ROLE_ACTIONS_RC2` (only the principal gains it) and `is_authority_edge_permitted_rc2`. `ROTATE_PRINCIPAL_KEY` now maps to `PRINCIPAL_KEY_ROTATE`. The gateway still requires a verified principal credential for it.

### SCC-001-AC-ENFORCEMENT-HOME (rc1 section 6 step 2)

- **Status:** `PROVISIONAL_DEFAULT` · **pending_deliberation:** `true`
- **Question:** rc1 asks for AC-1..AC-5 to be enforced inside SCC-001 Phase 1/2 (deterministic policy plus enforcement gateway). SCC-001 has no enforcement gateway (`docs/SCC-001.md` §8).
- **Chosen default:** keep AC enforcement in the separate reference gateway, `tests/reference/scc_001_ac/`, which follows the verbatim section-5 edge table. Leave `tests/reference/scc_001/` unchanged, with its delegation-scope gap kept as a strict xfail.
- **Alternatives not chosen:** build an SCC-001 enforcement gateway now and wire AC-1..AC-5 into it. That is the next enforcement step, and it changes SCC-001's reference behaviour.

## SCC-001-AC capture-path closures (Shax t601u, 26 Nov 2026)

Shax approved closing the four authority and recovery capture paths one at a time (identity, consent, resource isolation, recovery) and adding a distinct `PRINCIPAL_KEY_ROTATE` action. The other four live gaps stay strict xfails. Each closure is recorded in `docs/SCC-001-AC_ANTI_CAPTURE.md` section 8 and in the registry's `resolved_interface_gaps`. This partly supersedes the "record and do not fix" default of `SCC-001-AC-LIVE-GAPS` for those four paths only.

Path 3 note: the original ORACLE-D budget xfail asked for three partitions (R_audit, R_quarantine, R_override). Shax's acceptance condition covers only the override partition, so that one is closed. The R_audit and R_quarantine part stays open as its own strict xfail (`test_live_mafuba_budget_has_audit_and_quarantine_partitions`) rather than being dropped from the oracle.

### SCC-001-AC-IDENTITY-SCOPE (which escalations need a verified principal)

- **Status:** `PROVISIONAL_DEFAULT` · **pending_deliberation:** `true`
- **Question:** `check_authority_transfer` takes a caller-set `has_explicit_delegation` flag for every escalation. The identity fix makes FOUNDER_OVERRIDE require an independently verified principal credential. Should lower escalations (for example RECOMMEND to EXECUTE) also require a verified credential from their delegator?
- **Chosen default:** only FOUNDER_OVERRIDE (the principal-level authority that TEST-AC-06 covers) needs the verified credential. Lower escalations keep the caller flag, so all 2,496 non-FOUNDER_OVERRIDE results stay byte-identical.
- **Alternatives not chosen:** require a delegator credential for every escalation. That needs a delegator identity registry, which the kernel does not have, and it changes existing gate results.

## SC-AVG-001 (Groot in Path of Exile; the invariants as readings, not classes)

- **ID:** `SC-AVG-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Toronto (EST, UTC-5)
- **Ruling used:** Shax t582u (standing rule: pick a default and flag it). Substance from t603u, material Shax supplied by pasting a ChatGPT conversation.
- **Question:** the paste's PoE table gives Groot as "Witch → Necromancer (adapted)", while its own section 6 says PoE 1 has no Druid starting class and "I wouldn't force a perfect match where the game doesn't provide one." Which stands? Separately: are the specialization-gate and party-composition invariants invariant classes?
- **Chosen default:** **Groot is NO_FORCED_MATCH in the PoE layer.** The adapted row is kept as the paste's approximation of the summoned-entity side, not as a mapping. His Diablo II Druid match stands as interpretive. **The specialization-gate and party-composition invariants are readings under `SC-AEP-001`, not invariant classes.**
- **Alternatives not chosen:**
  - (a) Accept "Witch → Necromancer (adapted)" as Groot's PoE mapping.
  - (b) Map Groot through a PoE skill or Bloodline instead of a class.
  - (c) Promote party composition to an invariant class now.
- **Reason:** the paste contradicts itself on Groot, and its own stated rule is not to force a match; nothing has been prediction-tested, so no class is promoted.
- **Hook:** `review_trigger_terms` are `sc-avg-001`, `groot no forced match`, `specialization gate`, `party composition invariant`, `distributed build`, `avengers diablo`. The entry is explicit-only, so it never lifts a route.
- **Still open, when reviewed:** the villain roster against Diablo's Prime Evils and bosses; the Nephilim collective structure (`SC-NEPH-001` stays unresolved, not stubbed).

## SC-WORTHY-001 (worthiness kept separate from Usurped-Shard and Guardian's Fall)

- **ID:** `SC-WORTHY-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 26 Nov 2026, America/Toronto (EST, UTC-5)
- **Ruling used:** Shax t582u (standing rule). Substance from t603u.
- **Question:** t603u says the Usurped-Shard pattern, Guardian's Fall, Thor's worthiness and the Paladin's hammer "are related, but each tests a different property of authority." Is worthiness a separate reading, or the gate inside one of the existing patterns?
- **Chosen default:** **worthiness (capability is not legitimate authority; authority to wield is verified independently of the holder's claim) is a separate reading under `SC-AEP-001`, related to but not merged into `SC-SHARD-001` (captured authority) or `SC-GUARD-001` (protective authority turning coercive), and not an invariant class.** The Paladin's hammer is its worked case, not a fourth pattern. Engineering form: SCC-001-AC path 1 (PR #95).
- **Alternatives not chosen:**
  - (a) Fold worthiness into `SC-SHARD-001` as the gate a usurper bypasses.
  - (b) Promote worthiness to an invariant class now.
  - (c) Record the Paladin's entrusted sacred power as a fourth separate pattern.
- **Reason:** the source distinguishes the properties; only one worked case is verified (Ghrab Thaar), and Mjölnir is unverified from paste; nothing has been tested.
- **Hook:** `review_trigger_terms` are `sc-worthy-001`, `worthiness invariant`, `worthiness enchantment`, `capability is not authority`, `hammer of ghrab thaar`, `mjolnir`. The entry is explicit-only, so it never lifts a route.
- **Does not change:** `SC-SHARD-001`, `SC-GUARD-001` and SCC-001-AC are unchanged.
- **Still open, when reviewed:** scoring dimensions for worthiness; the Marvel source and wording for the enchantment.

## SC-MYTH-001 (comparative mythology matrix as a method; the Ori loop not a class)

- **ID:** `SC-MYTH-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 27 Nov 2026, America/Halifax (AST, UTC-4); compiled from the 26 Nov t605u/t606u messages
- **Ruling used:** Shax t582u (standing rule: pick a default and flag it). Substance from t605u, material Shax supplied by pasting a ChatGPT conversation; approval and scope from t606u ("Update, and comprehensive decompression and domain translation").
- **Question:** is the ten-field comparative mythology matrix a new invariant class, and is the Ori worship-power loop its own class?
- **Chosen default:** **the matrix is a method under `SC-AEP-001`, not an invariant class.** The first trio is kept as three distinct legitimacy questions, not one plot. **The Ori loop is recorded as a capture invariant (self-sourced legitimacy) mapped onto SCC-001-AC, not promoted to a class.**
- **Alternatives not chosen:**
  - (a) Collapse the trio into one succession invariant.
  - (b) Treat the Ori loop as a new invariant class.
  - (c) Treat Age of Mythology as a historical source.
- **Reason:** recurrence alone does not establish shared origin; only a first deep dive is done; nothing has been prediction-tested.
- **Hook:** `review_trigger_terms` are `sc-myth-001`, `comparative mythology matrix`, `self-sourced legitimacy`, `worship-power loop`, `aesir-vanir`, `osiris-horus-set`, `titan succession`. The entry is explicit-only, so it never lifts a route.
- **Does not change:** `SC-SHARD-001`, `SC-GUARD-001`, `SC-WORTHY-001`, SCC-001-AC, Catherine (unresolved) and the Lilith work.
- **Still open, when reviewed:** Chinese, Japanese, Aztec and Atlantean pantheons; Mesopotamian divine kingship; biblical angelic-rebellion traditions; the Stargate Alteran schism as its own matrix.

## SC-TOL-001 (Tree of Life structural compiler: rc5 with kernel fixes; chain-verification default; child-taint and inert items closed by Shax t610u)

- **ID:** `SC-TOL-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 27 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u (standing rule: pick a default and flag it). Substance from t608u (design thread v1 → v2.1-rc2, material Shax supplied by pasting ChatGPT and other-assistant conversations); version from t609u ("the attached .py is rc5 … implement from rc5").
- **Question:** ship rc5 verbatim or with fixes; how strict should delegation-chain verification be; should an untrustworthy child taint its meta-generator parent; is SC-TOL-001 an invariant class?
- **Chosen default:** **rc5 with seven recorded kernel fixes** (rc5 kept verbatim beside it). **Chain verification stays permissive by default** (`require_full_chain_verification=False`), but unregistered hops now produce a T8 QUALIFIED record instead of passing silently. **A parent is not tainted by a child** (children are reported separately). **SC-TOL-001 is a reference compiler, not an invariant class.** SILVER, not GOLD.
- **Alternatives not chosen:**
  - (a) Ship rc5 verbatim.
  - (b) Make full chain verification the default.
  - (c) Let an untrustworthy child taint its parent.
  - (d) Promote T8 into SCC-001-AC.
- **Reason:** the seven defects are real (each has a regression test that fails on rc5); the other two choices change rc5 semantics beyond fixing defects, so they wait for Shax.
- **Closed, `RESOLVED_BY_SHAX` (t610u, 27 Nov 2026; implemented as rc6; source `docs/evidence/source-2026-11-27b/`):**
  - **Child taint, alternative (c): ACCEPT, scoped.** A failing child taints the parent's *current* compilation only. A QUALIFIED child makes the parent QUALIFIED, and a BLOCKED child blocks this compilation. The taint never touches the generator's identity or the siblings, keeps the child's failure provenance (which cannot be erased), and grants no authority. ChildFailure ⇒ ParentCompilationTainted, never ParentIdentityDestroyed.
  - **Represented-only / incomplete-evidence EMPIRICAL case: RECLASSIFY.** `LIVING_OBSERVED` (life observed) and `SELF_MAINTENANCE_UNVERIFIED` (life observed; self-maintenance asserted but not demonstrated) sit alongside `AUTOPOIESIS_EMPIRICAL`. Neither satisfies T2, and an empirically living system is never inert. A static graph with no evidence of life stays `INERT_TAXONOMY`.
  - **Principle:** structural validity, biological status and governance authority are separate dimensions.
- **Still provisional:** alternative (b), full chain verification as the default. (a) is moot, since rc5 is kept verbatim beside the fixed copy. (d), promoting T8 into SCC-001-AC, is not chosen.
- **Hook:** `review_trigger_terms` are `sc-tol-001`, `tree of life compiler`, `recursive capture prevention`, `horizon opacity`, `meta-generator`, `kernel-fix`, `sefirot provenance`, `child failure taint`, `living observed`. The entry is explicit-only, so it never lifts a route.
- **Does not change:** SCC-001-AC (still `PROPOSED_GOLD`, `gold_awarded` false), `SC-AEP-001`, `SC-MYTH-001`, Catherine (unresolved).
- **Still open, when reviewed:** per-text provenance for the 10-node / 22-path Sefirot layout; fixtures for the Egyptian, Assyrian, Maya and Bodhi trees. (The represented-only EMPIRICAL case was closed by t610u, see above.)

## SC-TOL-001 rc7 (structural result vs. epistemic result vs. combined certification, Shax t611u)

- **ID:** `SC-TOL-001` (rc7, schema `SC-TOL-001/2.1-rc7+kernel.3`)
- **Status:** `PROVISIONAL_DEFAULT` (three edge cases below; the direction itself is Shax's)
- **pending_deliberation:** `true`
- **Date:** 27 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t611u (source `docs/evidence/source-2026-11-27c/`): keep the rc6 propagation rule; report a structural result, an epistemic result and a combined certification separately; unverified substrate, speculative architecture and invalid architecture are not equivalent. Shax t582u for the edge cases t611u does not decide.
- **Implemented:** `StructuralResult` (PASS / QUALIFIED / FAIL), `EpistemicResult` (tier / ESTABLISHED, NOT_EMPIRICAL, UNVERIFIED, INADMISSIBLE) and `combined_certification` (= rc6 `overall_verdict`, unchanged). Spec doc section 5b.
- **Edge cases t611u does not decide, with the defaults chosen:**
  1. **Coverage limits count as structural QUALIFIED.** Horizon opacity (T6 `OPAQUE`), fault sets touching masked nodes, and two-node-cut analysis that is skipped (size cap) or not applicable (3 or fewer visible nodes) make the structural result QUALIFIED, not PASS and not FAIL. They are limits on how much of the structure was checked, so they stay on the structural axis rather than being moved to the epistemic one. Consequence: the meta-generative fixture's own 3-node graph keeps it structurally QUALIFIED, while both of its speculative children are structural PASS.
     - *Alternatives:* (a) treat coverage limits as epistemic (what we could see), giving structural PASS; (b) treat "not applicable on a 3-node graph" as no finding at all.
  2. **NOT_EMPIRICAL ranks above UNVERIFIED.** A corpus (tradition-layer) result is not an unestablished empirical claim, so when epistemic results are combined (a parent and its children), a CORPUS child lowers an EMPIRICAL parent only to NOT_EMPIRICAL, and a SPECULATIVE child lowers it to UNVERIFIED.
     - *Alternative:* treat NOT_EMPIRICAL and UNVERIFIED as incomparable and report both.
  3. **A child's structural FAIL makes the parent's structural result FAIL, for the current compilation only.** This matches rc6 D1 (the parent's current compilation is BLOCKED) and adds nothing to the generator's identity, the siblings or authority.
     - *Alternative:* the parent's own structural result stays its own, and a child's FAIL shows only in E6 and the combined certification.
- **Not provisional (follows from t611u):** the combined certification is the rc6 verdict, unchanged; tier never enters the structural result; the axes only go down (no child, appended record or exemption can raise them); the axes carry no authority.
- **Hook:** `review_trigger_terms` add `epistemic result`, `structural result`, `speculative architecture`. The entry stays explicit-only.
- **Does not change:** the rc6 decisions (t610u), the chain-verification default (still provisional, see the SC-TOL-001 entry above), SCC-001-AC (still `PROPOSED_GOLD`, `gold_awarded` false), Catherine (unresolved). GOLD stays withheld.

## SC-SOV-TRADE-001 (Sovereign Bilateral Authentication Exchange; Shax t612u / t613u)

- **ID:** `SC-SOV-TRADE-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 27 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t582u (standing rule: pick a default and flag it). Substance from t612u (the attached v0.1 specification) and t613u ("Don't just stick the spec on there....build it.").
- **Question:** the specification is a design; section 16 leaves the customer questions open; several implementation choices are required to build a runnable reference.
- **Chosen default:** ship a **reference implementation** in `sov_trade/` that covers the protocol, signed envelopes, recognition, delegation with anti-capture, receipts, ledgers, translation, custody simulation and disputes, compiled as SILVER, not GOLD, not production-certified, and not an invariant class. Section 16's customer questions are listed below and are **not answered**.
- **Implementation choices (provisional; flagged for review):**
  1. **Identifier model:** DID-style `did:sov:{domain}:{kind}:{local}`, bound to a public-key set. Not X.509, and not a national scheme.
  2. **Canonicalization:** RFC 8785 JSON Canonicalization Scheme. Not deterministic CBOR. Signed objects accept integers, strings, booleans, null, arrays and objects only; floating-point numbers are rejected.
  3. **Clock skew bound:** 120 seconds. The time source in this build is an injected clock (tests) or the host UTC clock (otherwise). An RFC 3161 client and a local test TSA were added in t615u; a nationally agreed TSA is still a gap.
  4. **Key custody:** in-process dual-control remains available. t615u added a PKCS#11 signer against SoftHSM2 (non-extractable, sensitive keys). A certified hardware HSM is still a gap.
  5. **Signatures:** t615u makes `cryptography>=50.0.2` a hard requirement (no production fallback) and implements Ed25519 + ML-DSA-65 hybrid signatures; both must verify.
  6. **Document classes:** the full list from the specification is implemented as an enum; tests use certificate of origin as the pilot class. Which class comes first for a customer pilot is left to section 16.
  7. **Parties in tests:** two synthetic nations, Nation A and Nation B. Who the real parties and the contracting customer are is left to section 16.
  8. **Unknown or stale status:** fail closed for every document class (`deferred`). Section 12 allows a bounded grace period for lower-value classes; this build does not.
  9. **Withdrawal mid-transaction:** if recognition is withdrawn before a receipt is co-signed, new verification fails closed. In-flight policy is otherwise left open.
  10. **Archive retention:** configurable; the software default is 7 years of seconds and is not a legal claim.
- **Section 16, unanswered (customer questions; not decided here):**
  - Who are the two parties, and who is the contracting customer? A government, a ministry, or a trade body acting for one?
  - Is the second nation a real participant at this stage, or is the first deliverable a one-sided demonstration?
  - Which document classes come first? A single class such as certificates of origin is a far safer pilot than the full list.
  - Identifier and credential model: X.509 with a registry binding, DIDs with verifiable credentials, or an existing national scheme?
  - Mandated algorithms and HSM certification level in each country.
  - Existing national PKIs, single windows or customs systems this must integrate with.
  - Agreed time source and acceptable clock skew.
  - Who operates the verifier in each nation, and who audits it?
  - Required availability, volumes and latency. The targets in section 12 are guesses.
  - Legal standing of the receipts in each jurisdiction, and the governing agreement between the nations.
  - Export-licence position for delivering cryptographic software to the customer.
  - Who funds and owns independent assurance (penetration test, formal review)?
  - What is the repository's current state for the components in section 15? (The mapping in the draft was from an earlier review and was not checked against the live repository; the compiler header table now records that check.)
- **Alternatives not chosen:**
  - (a) File the specification as documentation only, with no implementation (the original t612u reading, superseded by t613u).
  - (b) Claim GOLD or production certification.
  - (c) Invent an ML-DSA implementation or treat R-16 as passing without a third-party review.
- **Reason:** t613u asked for a working implementation; the missing customer answers do not prevent an internal reference build (the specification already says Phase 1 can begin while Phase 0 is open). GOLD would require production custody, agreed national parameters and independent assurance, none of which this change has.
- **Hook:** `review_trigger_terms` are `sc-sov-trade-001`, `sovereign bilateral authentication`, `signed assertion envelope`, `bilateral verification receipt`, `recognition record`. The entry is explicit-only, so it never lifts a route.
- **Does not change:** SCC-001-AC (still `PROPOSED_GOLD`, `gold_awarded` false), `SC-TOL-001`, Catherine (unresolved). GOLD stays withheld.
- **Still open, when reviewed:** every item in section 16, the ten implementation defaults above, and R-16 independent assurance.

## SC-SOV-TRADE-001 t615u (close install-only gaps; Shax t615u)

- **ID:** `SC-SOV-TRADE-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 27 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t615u: close the gaps that only needed installs; do the work on the box; leave R-16 not met; do not raise the grade; remaining gaps are those that need outside hardware, real organisations or legal input; open a PR and wait for Shax to approve any merge to main.
- **Implemented (reference, not production-certified):**
  1. **`cryptography` is a hard requirement**, pinned `>=50.0.2,<51` in `pyproject.toml`. `sov_trade` refuses to import without it. The vendored `_ed25519` fallback was removed from every production path. Tests cover the refusal and the absence of a production import.
  2. **Hybrid signatures:** Ed25519 + FIPS 204 ML-DSA-65, both must verify, behind the existing algorithm-agility interface. Library choice: **pyca/cryptography 50.0.2** (Apache-2.0 OR BSD-3-Clause). Official wheels since 48.0.0 ship ML-DSA on OpenSSL 3.5+ (these wheels use OpenSSL 4.0.3). Evaluated and not chosen: `liboqs-python` 0.16.0.2 (MIT, OQS, research/prototyping, needs a liboqs build, OQS says it is not for production) and `pqcrypto` 1.0.0 (Apache-2.0, Backbone, no formal audit, smaller project).
  3. **PKCS#11 signer** (`python-pkcs11` 0.10.1, SoftHSM2 2.6.1 in tests). Keys are generated with `CKA_EXTRACTABLE=false` and `CKA_SENSITIVE=true`; signing is in-token; `CKA_VALUE` cannot be read through the API. A certified module can be selected by library path and token label, with no code changes. Tokens and PINs are test-generated in temporary directories and are not committed.
  4. **RFC 3161 client** plus a local test TSA (`asn1crypto` 1.5.1 and `cryptography`). Verification covers imprint, nonce, TSA certificate chain, policy and token signature.
  5. **Mutual TLS 1.3** on loopback with locally generated test CAs. Expired, wrong-CA and CRL-revoked certificates are rejected.
  6. **Root ceremony rehearsal:** GF(256) Shamir 3-of-5, with a runbook at `docs/runbooks/SC-SOV-TRADE-001_ROOT_CEREMONY.md`. Three or more custodians can reconstruct and sign; two or fewer cannot; a tampered share is detected.
- **Grade:** unchanged. SILVER 0.793, lowest gate 0.75, `gold_awarded` false. No recommendation to raise it until R-16 and the remaining gaps below are closed.
- **R-16:** still `NOT_MET` / `NOT_CLAIMED`. No outside reviewer has signed off.
- **Still a gap, with the reason:**
  - Certified hardware HSM and the specification sentence "No signing key ever exists in software memory outside an HSM or token" in a production sense: SoftHSM2 is a software token, and the in-process `KeyStore` still holds software keys when a token is not configured. Swapping in certified hardware is a configuration change, but the hardware itself is outside this repository.
  - Witnessed national root ceremony, named legal custodians, and a hardware threshold signature that never reassembles the seed: needs real organisations and a legal procedure. This tree has a software rehearsal only.
  - Agreed national TSA, clock, mTLS PKI, and hybrid post-quantum TLS key exchange: need real organisations and operational PKI. The TSA, CAs and handshakes here are local test fixtures; mTLS is classical TLS 1.3.
  - FIPS CMVP or other laboratory validation of this software stack: needs an outside lab.
  - Every unanswered question in section 16 (parties, document-class pilot, identifier model, mandated algorithms and HSM certification, integration, time source, verifier operator, availability, legal standing of receipts, export-licence position, who funds assurance).
- **Does not change:** the compiled grade, SCC-001-AC (still `PROPOSED_GOLD`, `gold_awarded` false), `SC-TOL-001`, Catherine (unresolved), `.github/workflows`, the package version (still 4.1.0). GOLD stays withheld.
- **Hook:** unchanged; the entry stays explicit-only.


## SC-SOV-TRADE-001 t616u (CI enforcement and verification pass; Shax t616u)

- **ID:** `SC-SOV-TRADE-001`
- **Status:** `PROVISIONAL_DEFAULT`
- **pending_deliberation:** `true`
- **Date:** 27 Nov 2026, America/Halifax (AST, UTC-4)
- **Ruling used:** Shax t616u: install the functional dependencies in CI and make sov_trade skips fail there; keep a no-`cryptography` job; run the supported Python matrix; verify (mutation, KATs, independent cross-checks, HSM evidence, property/fuzz tests, static checks, one-command reproduction); attach the evidence; do not merge; R-16 stays not met; the grade stays as it is; report failures rather than working around them.
- **Evidence:** `docs/evidence/sov-trade-verify-2026-11-27/` (README, environment record, logs, mutation table, cross-check outputs, SHA256SUMS). Reproduce with `make verify`.
- **New provisional defaults introduced by fixes in this pass (each needs a ruling):**
  1. **JCS integers:** integers outside ±(2^53−1) (the I-JSON safe range) are refused instead of serialized. Floats stay refused. Lone surrogates are refused.
  2. **JCS key order:** keys sort by UTF-16 code units as RFC 8785 requires (the earlier code sorted by code point; the RFC 8785 `weird.json` vector exposed it).
  3. **Transparency log:** RFC 9162 Merkle tree (no duplicated last node). Inclusion proofs bind the leaf index and tree size; consistency proofs are implemented and verified. Size-0 consistency is refused, and hashes that are not 32 bytes are refused (stricter than some upstream test probes; two upstream "equal size" probes therefore diverge, documented in the KAT test).
  4. **Peer checkpoints:** a checkpoint of a different size without a consistency proof is **not stored** (`consistency_proof_missing`) and does not halt acceptance; a bad consistency proof or an equal-size fork halts with `LEDGER_FORK`.
  5. **Status lists:** an issuer status list whose signature does not verify (or whose key is unknown, or whose domain differs) gives a hard `SIGNATURE_INVALID`. Before this pass the signature was never checked.
  6. **RFC 3161 strictness:** tokens must carry an ESS signing-certificate attribute (v2 preferred); the TSA certificate is selected by exact DER match of the signer identifier (stricter than RFC 5280 name matching); the TSA EKU must be critical and only id-kp-timeStamping; only RSA TSA keys are accepted; the whole TimeStampResp must be DER (minimal lengths and INTEGERs; found by the bit-flip fuzz pass); the unsigned PKIStatus may be `granted` or `grantedWithMods`; any parse error becomes `TimestampError`.
  7. **mTLS revocation:** CRLs are loaded so they actually take effect (Python's `cadata` silently drops CRLs); leaf CRL checking is on when a CRL is supplied.
  8. **Delegation:** an empty (unconstrained) child set under a constrained parent counts as widening. The authority-gate lattice check fails closed if `gates/authority.py` cannot be imported (it previously failed open).
  9. **PKCS#11:** `sign()` refuses a key that is extractable or not sensitive, and refuses an ambiguous label (more than one private key).
  10. **mTLS test material:** test certificates and keys are written to a fresh 0700 temporary directory only for `load_cert_chain` and deleted at once (the old `id()`-keyed cache could serve another certificate's key after garbage collection; CI caught it on Python 3.10-3.12).
- **Question for Shax (not changed):** `authority.issue` computes `needed = {APPROVE, SIGN}` for national-root grants but then requires `{APPROVE, DEPLOY}`; `needed` is unused (ruff F841). Which pair is intended?
- **Not tested / still a gap:** peer checkpoint signatures are not verified in `store_peer_checkpoint`; the Shamir rehearsal reconstructs the whole secret in memory and its GF(256) arithmetic is not constant-time; the hybrid "binding of publics" comment describes a no-op; no certified HSM, real organisations, legal review or outside reviewer (R-16). The verification ran on the box, not on Shax's PC (the PC was not reachable).
- **Grade:** unchanged. SILVER 0.793, `gold_awarded` false. **R-16:** `NOT_MET`. Version 4.1.0; no release or tag.
