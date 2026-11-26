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
