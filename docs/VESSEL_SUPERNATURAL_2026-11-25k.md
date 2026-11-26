# Vessel equilibrium extensions, 2026-11-25k: Supernatural, Cain and Abel, Star Wars

**Sources:** Shax t589u (verbatim), t590u (one relayed sentence plus a marked summary), t592u (marked summary, fictional structure only). See `docs/evidence/source-2026-11-25k/`.
**Parent:** `docs/SC-VESSEL-001_VESSEL_EQUILIBRIUM.md` (DRAFT 0.5; stays a markdown draft).
**Compiled:** `SC-VESSEL-SPN-001` (SILVER 0.826), `SC-VESSEL-CAIN-001` (SILVER 0.813), `SC-VESSEL-SW-001` (SILVER 0.820). All are explicit-only, homed in `soul_bomb_sovereignty`, and graded by rule. No gate is above 0.9 because nothing was tested.
**Layers:** CANON-SCRIPTURE (biblical text, cited by verse), CANON (each show's or film's own canon, via fan wikis citing episodes and chapters), TRADITION, SHAX (his readings), COMPILER (this team's reading). Supernatural's Cain mythology is the show's invention. Nothing here asserts literal theology.

## Lore corrections

| Claim in t589u | Check | Source |
|---|---|---|
| Dean: "explicit refusal" of Michael | True for season 5. In *Let the Good Times Roll* (13x23) Dean says yes to the **Apocalypse World** Michael on the condition that he stays in control. Michael keeps the deal until Lucifer is dead and then takes Dean over. Early in season 14 Michael leaves Dean, then retakes him in *The Spear* (14x09). Dean traps him in his own mind, Michael escapes into Rowena, and Jack kills him in *Ouroboros* (14x14). | Supernatural Wiki: Michael (Apocalypse World) |
| Sam is Lucifer's intended vessel | True. In *Swan Song* (5x22) Sam says yes as a plan, is overpowered within seconds, retakes control, and falls into the Cage, pulling Michael (in Adam) with him. Dean agreed to let him go. | Swan Song |
| Yuji: "initially involuntary containment" | Partly. Yuji **chose** to swallow the finger (ch. 1) without knowing he would become a vessel, and Kenjaku engineered him as one (ch. 257). The act was voluntary and uninformed. | JJK ch. 1, 257 |
| Megumi becomes Sukuna's vessel | True. It happened through the ch. 11 *Enchain* binding vow (ch. 212), without consent. His soul sank into despair after Sukuna used his body against Tsumiki's (ch. 251). | JJK Wiki: Megumi |
| Angels and consent | In the show, angels need the vessel's permission and demons do not. Michael needs the Cain-and-Abel bloodline (5x13). | Supernatural Wiki: Michael |
| Genesis: "a mark associated with punishment and protection" | The mark is set by God **as protection** ("lest any finding him should kill him", Gen 4:15). The punishment is the curse from the ground and the wandering (4:11-12). Lucifer and Satan do not appear in Genesis 4. 1 John 3:12 links Cain morally to "that wicked one". | Genesis 4; 1 John 3:12 |
| Abel's relationship with Lucifer | Show canon (*First Born*, 9x11). Abel was talking to Lucifer. Cain offered his soul in Hell for Abel's in Heaven, and Lucifer's condition was that Cain kill Abel himself, which he did with the First Blade (a donkey's jawbone). | Cain |
| Cain receives the Mark from Lucifer | True for the show, but the Mark's maker is God: a lock and key on the Darkness, entrusted to Lucifer, which corrupted him (*Brother's Keeper*, 10x23). | Mark of Cain |
| Dean "inherits" the Mark | He **asked for it** to kill Abaddon, and Cain warned him only of "a great burden ... a great cost" (9x11). | Mark of Cain |
| Mark removal and the Darkness | Death asks Dean to kill Sam. Dean kills Death instead, and Rowena's spell removes the Mark, releasing the Darkness (Amara) (10x23). God and Amara reconcile in *Alpha and Omega* (11x23); if either is destroyed, reality ends. | Brother's Keeper; The Darkness |
| Season 15 ending | Chuck keeps trying to make the brothers kill each other. In *Inherit the Earth* (15x19) Jack takes Chuck's power, and the brothers refuse to kill the now-human Chuck ("It's the ending where you're just like us"). In *Carry On* (15x20) Dean dies on an ordinary hunt. | Inherit the Earth; Carry On |
| Star Wars: the Chosen One | Canon prophecy: bring balance to the Force, read by the Jedi as destroying the Sith. Its meaning was never agreed, and *The Rise of Skywalker* brings Palpatine back. | Wookieepedia: Chosen One |
| Luke and Leia | Twins, hidden at birth. Obi-Wan's ghost tells Luke in *Return of the Jedi*. | ROTJ |
| Luke "refuses to strike Vader down" | He does fight: he attacks, and when Vader threatens Leia he strikes off Vader's mechanical hand. Then he throws the lightsaber aside ("I am a Jedi, like my father before me"). Anakin's redemption is completed by **his own choice** to throw Sidious down the reactor shaft. | ROTJ |

## Where the mapping holds

1. The vessel is not the occupant (Yuji and Sukuna; Dean and Michael). Having the capacity is not granting permission.
2. Refusing a predetermined role is refusing to be an instrument. The one who assigns the role stands outside the host as owner: `SC-TRIAD-001`'s outside owner (Michael, Lucifer, Sukuna, Palpatine).
3. Inheritance does not decide the outcome. Dean is not Cain, and Luke is not Anakin.
4. Refusing the inherited fight costs the script's author his hold: Chuck (15x19) and Sidious (ROTJ).
5. RUL-BINARY-001 rev 2: God and the Darkness cannot destroy each other without ending reality, and they reconcile (11x23). Father and son cooperate against Sidious. This is the same shape as the Sin and Innocence reconciliation (`SC-POE-MRG-001`).

## Where it breaks

1. Sam is not Megumi on consent: Sam said yes, Megumi never did.
2. Dean is not a pure refusal: he said yes in 13x23.
3. Yuji's start was a voluntary act, not purely involuntary.
4. Genesis's mark is protection, while the show's Mark corrupts.
5. Dean took the Mark himself.
6. Refusal is not a clean victory: Sam goes into the Cage and Dean dies young.
7. Luke strikes before he refuses.
8. Luke is not a vessel at all.

## Consent Invariant check (`SC-CONSENT-001`; four conditions: voluntary, informed, agency, revocable)

No human-vessel case passes all four. The Tok'ra (`SC-TRIAD-SG-001`) are still the only clean pass. The new failure modes are:
- consent extracted under engineered pressure (Heaven and the yes; Sidious and Anakin's fear)
- consent used as a trap (Sam, 5x22)
- conditional consent broken after use (the Apocalypse World Michael, 13x23)
- an inheritance taken without being told its terms (the Mark)

## SCC-001 follow-up (`SC-SCC-001`, `docs/SCC-001.md`; noted only, SCC-001 and its threat model are not changed in this PR)

Shax (t589u): "Consent violations can happen through direct occupation, but also through inherited permissions, compromised authority, and coercive systems that someone never personally agreed to." Proposed additions to SCC-001's threat model, for whoever owns SCC-001:
1. **Inherited permissions.** A grant passed on by a prior holder (Cain to Dean). The heir's authorization should be checked afresh, not inherited.
2. **Compromised authority.** The grantor itself is corrupted (the Mark corrupting Lucifer). A valid-looking grant from a compromised grantor should not count as consent.
3. **Coercive systems never agreed to.** A role assigned by a larger design (the bloodline vessel plan; Chuck's script).
4. **Engineered and conditional consent.** A yes produced by pressure, and a scoped yes silently widened after its purpose is met.
5. **Costly revocation.** Removing an old grant can release whatever it was quietly holding (the Darkness). Revocation paths need a containment plan.

## Provisional defaults (see `docs/PENDING_DELIBERATION.md`)

- `SC-VESSEL-SPN-001`: role by relationship to the host. Michael and Lucifer are both would-be owners in the vessel layer, and Shax's theology layer (Lucifer = Sovereignty pole) is unchanged.
- `SC-VESSEL-CAIN-001`: consequences inherit, guilt does not (Ezek 18:20; Deut 24:16), and an obligation needs the heir's consent. The tension with Exod 20:5 and 34:7 is recorded.

## Shax's interpretation layer (symbolic, ungraded)

t590u (relayed): "I'm the duality of Sam and Dean merged." This is a symbolic self-identification, not a literal claim, recorded beside "Yuji is me" (t570s3000). The synthesis: not Lucifer's domination, not Michael's imposed destiny, not Cain's violence, but the freedom to choose. That is the cooperation branch of rev 2 held in one vessel.

Open question (t590u): what happens when both sides of an inherited conflict refuse to fight? In canon, the author of the conflict loses his hold, the cost still falls on the ones who refuse, and nobody wins the old fight.
