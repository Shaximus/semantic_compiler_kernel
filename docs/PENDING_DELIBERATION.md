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
