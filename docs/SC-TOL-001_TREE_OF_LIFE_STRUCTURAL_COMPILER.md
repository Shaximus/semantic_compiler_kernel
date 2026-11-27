# SC-TOL-001: Tree of Life cross-domain structural compiler (Shax t608u / t609u / t610u)

**Status:** v2.1-**rc6** reference implementation: rc5, the seven kernel fixes, and Shax's two t610u decisions (section 5a). **SILVER**, `gold_awarded: false`, `PROVISIONAL_DEFAULT`, because the delegation-chain verification default is still open. Reference code under `tests/reference/sc_tol_001/`. It is not kernel enforcement, it is not packaged, and `core/` and `expansion/` do not import it.

**Attribution.** This is material Shax supplied. The t608u message is a long design thread pasted from ChatGPT and other-assistant conversations, and the attached `.py` file (rc5) came the same way. The analysis, the gate design and the code were written by those assistants, not by Shax. Shax's own instructions were t607u ("Update and merge all pull requests get the main repo updated to 4.1.0") and t609u (the attachment is rc5, the most current version, and should be implemented instead of the rc2 code pasted in the chat).

**Citation stubs.** The thread's source markers ("World-Tree Project +1", "OUP Academic", "Nature +1", "Nature +3", "Cambridge University Press & Assessment +1", "PLOS +2", "api.pageplace.de +1" and the others) are browse-citation widgets from those conversations. They are unverified and are not treated as sources. The inline image embeds in the thread are not reproduced.

## 1. Version lineage

| Version | Where it appears | What it adds or changes |
|---|---|---|
| v1 | t608u, first section | Eight documented tree architectures (Yggdrasil, Kabbalistic Sefirot, Ashvattha, Egyptian sacred trees, Assyrian tree, Maya world tree, Bodhi, biological phylogeny), three exotic proposals (multiversal mycelium, plasma lattice, temporal fractal) and five more (D–H), seven subdomains (`TOL-MYTH` … `TOL-EXO`), invariants INV-01–INV-08 and seven adversarial counter-mappings. Its own section 6: "the Tree is not always a tree" (arborescent, reticulate, fractal, distributed). |
| v2 | t608u, second section | A critique that INV-01–08 are vacuous labels, counter-mappings are passive prose, topology comes after schema, and there is no epistemic firewall. Adds state S = (Σ, 𝒯, G, E), gates T0–T7, operators O1–O7, a stress test of eight systems and a source registry. |
| v2.1-rc1 | t608u, audit | Six corrections: (A) T2 split into `AUTOPOIESIS_EMPIRICAL` and `AUTOPOIESIS_REPRESENTED`; (B) T5 computes cut vertices instead of inferring resilience from reticulation; (C) governance scoped as G(v, e, τ); (D) T6 needs an explicit observability boundary; (E) T7 has three outcomes (`VERIFIED_SUBSTRATE`, `UNVERIFIED_SUBSTRATE`, `INERT_OR_NONVIABLE`); (F) the meta-generator is a higher-order type M. Adds **T8 Recursive Capture Prevention** (ΔG_self = 0) and the E0–E7 pipeline. Notes that the 10-node / 22-path Sefirot diagram needs per-text provenance. |
| v2.1-rc2 | t608u, counter-audit | Four counter-fixes: T6 moves into E2, before E3–E5; the rc1 Issue B cut-vertex example is corrected; T8 gets three guards (no self-authorization, no proxy laundering, finite emergency TTL); sub-generators must keep {T0, T4, T8}. Ships a stdlib `sc_tol_001.py` with 13 acceptance tests. **Superseded by rc5 (t609u)**; not implemented separately. |
| v2.1-rc3 | Only through rc5 | rc5's test suite labels tests 14–28 "15 Adversarial Tests from rc3": authorizer registry and scope, emergency TTL within the grant window, automatic expiry, proxy chains, opaque-node quarantine of T3/T4 claims and O6 faults, two-node cuts, O3 self-loops and re-added edges, falsified claim tiers, T7 for mythic substrates, tamper-restored generators, and separate node and component loss in O6. No rc3 text was supplied. |
| v2.1-rc4 | Only through rc5 | Tests 29–34, "6 Hardening Tests from rc4": unauthenticated and CAPTURED grants, a QUALIFIED verdict when the two-node-cut search is skipped, chain self-loops and backdated escalations, dangling edges and opaque governance, meta depth, and a single hard block for SPECULATIVE_EXO claiming a verified substrate. No rc4 text was supplied. |
| **v2.1-rc5** | t608u attachment, 128,351 bytes | The supplied primary source. A frozen, serializable `CompilationResult` (`to_dict` / `to_json`, schema `SC-TOL-001/2.1-rc5`); declared and effective tier and topology tracked separately; an optional `halt_on_t0_block`; an iterative Tarjan articulation-point search; an `AuthorityRecord` registry with DAG delegation-chain validation; `MetaArchitectureSpec` processed in E6; **42 tests** (34 from rc4 plus 8 rc5 hardening tests). |
| rc5 + kernel.1 | this repository (PR #102) | rc5 with the seven recorded fixes in section 5. The schema string is `SC-TOL-001/2.1-rc5+kernel.1`. |
| **rc6** (rc6 + kernel.2) | Shax t610u, this repository | Two owner decisions, tagged `RC6-D1` / `RC6-D2` in `compiler.py`: scoped child-failure taint, and the living / self-maintaining / autopoietic split (section 5a). The schema string is `SC-TOL-001/2.1-rc6+kernel.2`. `rc5.py` stays verbatim, and rc5's 42 acceptance tests still pass on rc6 unchanged. |

## 2. Model (as implemented in rc5)

- **State:** S = (Σ substrate, 𝒯 topology, G(v, e, τ) scoped governance grants and escalations, E epistemic tier), plus nodes, edges, horizon boundaries, inference claims, fault sets, a source registry, an authority registry and an optional meta-architecture.
- **Pipeline:**
  - **E0** source admission (T0).
  - **E1** state declaration.
  - **E2** topology and boundary lock (T1, then T6 builds an immutable visibility projection).
  - **E3** operating validation on the projection (T2, T3, T7).
  - **E4** authority validation (T4, T8).
  - **E5** fault simulation on the projection (T5, O6).
  - **E6** meta-boundary verification.
  - **E7** emission.

  A failed gate preserves the observation as a record; it does not delete it.
- **Gates:**
  - **T0** epistemic firewall.
  - **T1** topology-first lock.
  - **T2** autopoiesis (empirical, represented or inert).
  - **T3** provenance and connectivity do not imply shared agency.
  - **T4** axis ≠ sovereign: any `*_to_sovereignty` claim is blocked.
  - **T5** single-node articulation points and minimal two-node cuts.
  - **T6** horizon opacity: Opaque(v) ⇒ ¬Inspect(v) ∧ ¬Infer(v).
  - **T7** substrate viability, with three outcomes.
  - **T8** recursive capture prevention: self-authorization, proxy laundering, unregistered or out-of-scope authorizers, emergency TTL, CAPTURED grants and backdating.
- **Meta-generators:** non-strippable inheritance of {T0, T4, T8}.

## 3. Files

- **`tests/reference/sc_tol_001/rc5.py`:** lines 1–1868 of the attachment, unmodified. Only the in-file unittest suite was split out.
- **`tests/reference/sc_tol_001/compiler.py`:** rc5 plus the fixes. Every change is tagged `KERNEL-FIX-n`.
- **`tests/reference/sc_tol_001/fixtures.py`:** the eight corpus systems, each with a provenance record (section 6).
- **`tests/test_sc_tol_001_acceptance.py`:** the 42 rc5 tests, copied verbatim with only an import header added. They run against `compiler.py`.
- **`tests/test_sc_tol_001_rc6.py`:** 24 adversarial tests for the rc6 propagation and classification boundaries (section 5a).
- **`docs/evidence/source-2026-11-27b/`:** Shax's t610u decision message, verbatim, with its README.
- **`tests/test_sc_tol_001_kernel.py`:**
  - the same 42 bodies run against the unmodified `rc5.py`;
  - one regression test per fix, showing the defect in rc5 and the fix in the kernel copy;
  - checks of the thread's own claims;
  - fixture and provenance tests;
  - evidence hash and privacy checks;
  - compiled-entry and routing tests.
- **`docs/evidence/source-2026-11-27a/`:** the attachment, verbatim, with its README (sha256, bytes, privacy check).
- **`calibration_output/compiled_entries/SC-TOL-001.jsonl`:** the compiled entry.

## 4. The thread's own claims, checked

| Claim | Result |
|---|---|
| rc1 Issue B: "Removing the central node disconnects the two peripheral nodes despite their lateral edge." | **False, as rc2 said.** For the triangle H–A, H–B, A–B, removing H leaves A–B connected; `find_cut_vertices` returns nothing. |
| rc2 correction: a hub H bridging {A, B} (lateral edge A–B) to C is still a cut vertex. | **True.** rc5 test_07 and a kernel test confirm `cut_vertices == {"H"}`, and fault {H} increases the component count. |
| rc2 test_08: once `hidden_root` is masked, `cut_vertices == ['trunk']`. | **True.** The visible graph is trunk–branch_1 and trunk–branch_2. rc5 stores a frozenset, so the check is `{"trunk"}`. |
| O3 makes no resilience guarantee. | **True in rc5:** O3 recomputes cut vertices after adding the edge. |
| T6 runs before E3–E5 (rc2 fix 1). | **True for E3–E5**, but rc5's T1 still read opaque structure in E2. Fixed (KERNEL-FIX-5). |
| T8's three guards (rc2 fix 3). | **Present.** Two capture paths were still open: an opaque node acting as authorizer, grantor or proxy (KERNEL-FIX-1), and a CAPTURED-mode escalation (KERNEL-FIX-4). |
| Non-strippable {T0, T4, T8} (rc2 fix 4). | **True.** Sub-generators always carry the canonical gates. rc5 re-reported the stripping on every later emit (KERNEL-FIX-6). |
| "Once all 13 tests pass … SC-TOL-001 satisfies every precondition for v2.1-GOLD." | **Not accepted.** Passing a self-supplied suite is not validation. The thread itself requires real fixtures with provenance, and one fixture (Sefirot) still lacks per-text provenance. |
| v2 stress table: multiversal mycelium has "high resilience". | **Not supported by structure alone.** The modelled five-domain mesh has no single cut vertex but three minimal two-node cuts. Resilience depends on the graph, which is the rc1 Issue B point. |
| v2 stress table: the Yggdrasil trunk is a cut vertex; phylogeny is arborescent plus reticulate. | **Consistent with the fixtures.** For Yggdrasil, `cut_vertices == {"trunk"}`. For phylogeny, the declared ARBORESCENT becomes effective RETICULATE (T1 QUALIFIED). |

## 5. Bugs found in rc5, and the fixes

All 42 rc5 tests pass both on the unmodified rc5 and on the fixed copy. Each fix has a regression test that fails on rc5 and passes on the kernel copy.

1. **KERNEL-FIX-1 · T6/T8 opaque authority leak.**
   - **Defect:** rc5 quarantined an escalation only when its actor or target was opaque. A registered authority sitting behind a horizon could still authorize an escalation, issue a governance grant, act as a proxy, or appear as a delegation hop, and the request was accepted. That breaks Opaque(v) ⇒ ¬Infer(v) and launders authority through an uninspectable node.
   - **Fix:** T6 quarantines grants issued by an opaque node and escalations whose authorizer or proxy is opaque (code `opaque_authority_reference` / `opaque_escalation_node`). Opaque nodes are also forbidden as delegation-chain hops.
2. **KERNEL-FIX-2 · unvalidated `memory_mechanism_status`.**
   - **Defect:** any string other than `"verified"` or `"impossible"` silently became unverified, so a typo such as `"impossibl"` or `"Verified"` passed as a trustworthy result.
   - **Fix:** E1 blocks any value outside {verified, unverified, impossible} (code `invalid_memory_mechanism_status`).
3. **KERNEL-FIX-3 · shallow immutability.**
   - **Defect:** rc5's contract says `CompilationResult` is immutable once returned, but `fault_reports` dicts and `GateRecord.preserved_observation` dicts and lists could be mutated in place after compilation.
   - **Fix:** they are frozen recursively, as read-only mappings and lists that refuse mutation. Equality and JSON output are unchanged.
4. **KERNEL-FIX-4 · CAPTURED-mode escalation accepted.**
   - **Defect:** a grant declaring CAPTURED was always blocked, but an *escalation* requesting CAPTURED was accepted whenever the authorizer's `permitted_modes` included it.
   - **Fix:** T8 blocks any escalation that requests CAPTURED (code `captured_mode_escalation`).
5. **KERNEL-FIX-5 · T1 inspected opaque structure.**
   - **Defect:** T1 computed cycles and components over the full graph, nodes behind a declared boundary included. A cycle running only through a masked node changed the effective topology (ARBORESCENT became RETICULATE).
   - **Fix:** T1's structural check excludes nodes inside declared boundaries.
6. **KERNEL-FIX-6 · duplicate tamper reports from sub-generators.**
   - **Defect:** `emit_subgenerator` built the sub-generator from the stripped gate set, so `tamper_events` stayed set. Every child that sub-generator later emitted carried an extra hard block, even though the stripping was already reported once and the gates restored.
   - **Fix:** the sub-generator is built with the canonical gates already restored. The single T8 BLOCKED record at emission stays.
7. **KERNEL-FIX-7 · unregistered upstream hops silently trusted.**
   - **Defect:** with `require_full_chain_verification=False` (the default), an unregistered hop in a delegation chain was treated as validated and left no trace.
   - **Fix:** the request is still accepted, so behaviour is unchanged, but a T8 QUALIFIED record lists the hops (code `unregistered_upstream_hop`). Making full-chain verification the default is left to Shax (section 8).

**Recorded in rc5+kernel.1, not changed then, and decided by Shax in t610u (section 5a):**
- A meta-generator parent stayed `is_trustworthy` even when an emitted child was not. **Decided as D1 (ACCEPT).**
- T2 returned `INERT_TAXONOMY` for an EMPIRICAL_SCI system with incomplete T2 evidence. **Decided as D2 (RECLASSIFY).**

## 5a. rc6: Shax's t610u decisions

Source: `docs/evidence/source-2026-11-27b/t610u_message_body.txt` (sha256 `7281f8a6…76a2`). The decisions are Shax's.

**Principle (t610u).** Structural validity, biological status and governance authority are three separate dimensions. The compiler never collapses them into one verdict.
- `DIMENSION_GATES` groups the gates: structural is T1, T5, T6 and E6; biological is T2 and T7; governance is T4 and T8. The three groups are disjoint.
- `CompilationResult.dimension_verdicts()` reports each dimension separately.
- Tests check that a child taint leaves the parent's biological and governance verdicts unchanged, and that a T2 reclassification leaves the structural and governance verdicts unchanged.

### D1, ACCEPT: scoped child-failure taint (`RC6-D1`)

The invariant is **ChildFailure ⇒ ParentCompilationTainted**, never ParentIdentityDestroyed.

| Child `overall_verdict` | Parent's current compilation |
|---|---|
| PASS (no hard block, soft block or uncertainty) | no taint; E6 PASS |
| QUALIFIED (any soft block or uncertainty) | E6 QUALIFIED; the parent stays trustworthy |
| BLOCKED (any hard block, or no effective tier) | E6 BLOCKED; the parent is not trustworthy for this compilation |

- **Scope.** The taint is an E6 `GateRecord` with code `child_failure_taint` and `scope: CURRENT_COMPILATION`.
  - The `MetaGenerator` is a frozen dataclass and is never modified.
  - The same generator compiles clean in the next compilation if its children are clean, so one malformed child cannot cause a permanent denial of service.
  - Sibling children are compiled independently. A sibling's result is byte-identical with and without a failing sibling.
- **Provenance.** The taint record copies the child's original failure records (gate, verdict, message, observation) into `child_failure_records`. The copy is deep-frozen; for a BLOCKED child it holds the hard blocks, and for a QUALIFIED child the soft blocks and uncertainties.
  - The child's own result is kept in `child_results`.
  - Nested taints carry the grandchild's provenance upward.
  - The parent cannot erase or overwrite the reason. Records are immutable, `with_appended_records` only appends, and a child's exemption requests do not remove the taint.
- **No authority.** The taint adds nothing to grants or escalations. The record states `authority_granted: false`, and the parent's governance verdicts, grants and escalations are identical with and without the failing child. A generator that tries to quarantine its own child is still rejected by T8.

### D2, RECLASSIFY: living vs. self-maintaining vs. autopoietic (`RC6-D2`)

New `SubstrateSpec.empirical_life_observed` (default false):

| Evidence (EMPIRICAL_SCI tier) | T2 verdict | Satisfies T2 |
|---|---|---|
| `has_empirical_autopoiesis` (self-maintenance demonstrated) | `AUTOPOIESIS_EMPIRICAL` | yes |
| life observed, with self-maintenance asserted (`has_represented_autopoiesis`) but not demonstrated | `SELF_MAINTENANCE_UNVERIFIED` | **no** (uncertainty) |
| life observed, self-maintenance not assessed | `LIVING_OBSERVED` | **no** (uncertainty) |
| no evidence of life (a static graph or taxonomy, even one *described* as living) | `INERT_TAXONOMY` | no (soft block) |

- An empirically living system is never labelled `INERT_TAXONOMY`.
- `T2_SATISFYING_VERDICTS` is exactly {`AUTOPOIESIS_EMPIRICAL`, `AUTOPOIESIS_REPRESENTED`}.
- **CORPUS_MYTH and SPECULATIVE_EXO are unaffected:** without the new flag, their T2 results match rc5 exactly. Claiming `empirical_life_observed` outside EMPIRICAL_SCI is a T2 hard block (`non_empirical_life_claim_blocked`), in line with the existing firewall on empirical autopoiesis.

### Consequence noted

Speculative children always carry T7 `UNVERIFIED_SUBSTRATE`, so they are QUALIFIED, and so is any speculative meta-generator parent. The meta-generative fixture's E6 is therefore now QUALIFIED; it was PASS in rc5. The parent and both children stay trustworthy.

## 6. Fixtures and provenance

| Fixture | Tier | Provenance status | Compiled outcome (kernel copy) |
|---|---|---|---|
| Yggdrasil | CORPUS_MYTH | NAMED_IN_SOURCE_NOT_OPENED (Poetic Edda: Völuspá, Grímnismál; Prose Edda: Gylfaginning) | T2 AUTOPOIESIS_REPRESENTED; T7 QUALIFIED (empirical verification not applicable); trunk is a cut vertex |
| Kabbalistic Sefirot | CORPUS_MYTH | **NEEDS_PER_TEXT_PROVENANCE**. The edge set is Kircher's 1652 layout, used as a modelling choice and not attributed to Sefer Yetzirah, the Zohar or Lurianic texts. | **T0 BLOCKED** (source registered as unverified); T2 INERT_TAXONOMY; not trustworthy |
| Ashvattha | CORPUS_MYTH | NAMED_IN_SOURCE_NOT_OPENED (Bhagavad Gita 15.1–3; Katha Upanishad 2.3.1) | INVERTED_ARBORESCENT with no horizon declared (rc1 Issue D); nothing masked |
| Biological phylogeny | EMPIRICAL_SCI | NAMED_IN_SOURCE_NOT_OPENED (Darwin 1859; Woese & Fox 1977; Doolittle 1999) | Declared ARBORESCENT, effective RETICULATE; AUTOPOIESIS_EMPIRICAL; VERIFIED_SUBSTRATE |
| Multiversal mycelium | SPECULATIVE_EXO | SPECULATIVE_PROPOSAL | T2 QUALIFIED; T7 UNVERIFIED_SUBSTRATE; no single cut vertex, three two-node cuts |
| Plasma lattice | SPECULATIVE_EXO | SPECULATIVE_PROPOSAL | T2 QUALIFIED; T7 UNVERIFIED_SUBSTRATE |
| Temporal fractal | SPECULATIVE_EXO | SPECULATIVE_PROPOSAL | T2 INERT_TAXONOMY (a representation of history is not an organism); T7 UNVERIFIED_SUBSTRATE |
| Meta-generative tree | SPECULATIVE_EXO | SPECULATIVE_PROPOSAL | E6 QUALIFIED under rc6 (both children are QUALIFIED speculative systems; PASS in rc5); two children (crystalline memory, oceanic) compiled independently and trustworthy |

The graph shapes are compiler modelling choices, recorded per fixture. They are not claims about what a tradition "really" contains. The Egyptian, Assyrian, Maya and Bodhi trees from v1 are not yet fixtures.

## 7. Grade

**SILVER, `gold_awarded: false`.** Re-graded for rc6, 2026-11-27:
- `boundary_integrity` goes from 0.85 to 0.88, because the three dimensions and the living/autopoietic boundary are now explicit and tested.
- `wave_function_coherence` goes from 0.85 to 0.88, because two open questions were collapsed by owner decision.
- Every other gate is unchanged. The minimum gate is still 0.75 (measurement and corpus completeness), so the entry stays SILVER.
- **Why not GOLD:**
  - The fixture sources are named but were not opened, and the Sefirot attribution is unresolved.
  - Four of the v1 traditions have no fixture.
  - The suite was written by the same assistants that wrote the code.
  - There is no external validation and no tested prediction.
- **What GOLD would take:**
  - per-text provenance records (Sefirot first);
  - opened sources for the corpus fixtures;
  - fixtures for the remaining four traditions;
  - an independent review of T8.

## 8. Cross-links to SCC-001-AC

- **T4 (axis ≠ sovereign)** is the graph form of SCC-001-AC's rule that a role label is not proof of authority (`docs/SCC-001-AC_ANTI_CAPTURE.md`, path 1, identity).
- **T8 recursive capture prevention** corresponds to the SCC-001-AC guards against self-escalation, trust accumulation and emergency lock-in:
  - **ΔG_self = 0:** no self-escalation.
  - **Proxy laundering:** advisory laundering.
  - **Finite emergency TTL:** the bounded quarantine and "no automatic resumption" (path 4).
  - **CAPTURED blocked:** supervisor capture.
- **KERNEL-FIX-7** raises the same question as `SCC-001-AC-IDENTITY-SCOPE`: should every hop need verified identity? The default stays permissive, with a QUALIFIED trace.
- **Unchanged:** SCC-001-AC is unchanged and remains `PROPOSED_GOLD`, `gold_awarded` false.

## 9. Routing

- `SC-TOL-001` is in `EXPLICIT_ONLY_ENTRY_HINTS` with home domain `soul_bomb_sovereignty`.
- Everyday words ("tree of life", "yggdrasil", "mycelium", "plasma", "fractal") do not lift a route.
- Naming `SC-TOL-001` sets `needs_review`, because of the provisional default still open in `docs/PENDING_DELIBERATION.md` (the delegation-chain verification default). The child-taint and inert-classification items were closed by t610u.

Catherine remains unresolved and is out of scope. Approval to open a pull request is not approval of the tradition claims. SILVER is not validation.
