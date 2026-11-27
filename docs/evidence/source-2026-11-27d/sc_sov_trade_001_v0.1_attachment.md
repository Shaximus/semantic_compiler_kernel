# SC-SOV-TRADE-001: Sovereign Bilateral Authentication Exchange

Nov 27, 2026 · @Curtis William Michel Kingsley

Draft v0.1 engineering specification for a reciprocal verification service in which two sovereign states keep their own trust anchors, policies and records, and exchange signed, scoped, freshness-bound trade assertions that each side verifies independently.

## 1. Scope and non-goals

The system lets two sovereign states, Nation A and Nation B, each verify the authenticity and authority behind trade documents the other issues, without either one surrendering control of its identity infrastructure, policy or records.

**In scope**

- Independent sovereign trust domains, one per nation, each with its own roots, institutions and policy.
- Signed trade assertions: export and import documentation, certificates of origin, customs and regulatory declarations, inspection and compliance records, shipment and delivery confirmations, contractual acknowledgments.
- Scoped, time-bound, revocable delegation from each state to its institutions and officials.
- A bilateral exchange protocol that ends in mutually verifiable receipts.
- Semantic translation of institutional vocabulary that never alters a signed source record.
- Tamper-evident audit records that either party can verify without the other's cooperation.

**Out of scope**

- Proving that an underlying claim is true. A valid signature shows who asserted something, under what authority and when. Truth of the claim needs evidence, independent appraisal, and where required physical inspection.
- Replacing customs, tax, sanctions or regulatory decision-making. Each state keeps its own decisions.
- A shared platform, shared root of trust or shared database between the two states.
- Hardware or workload attestation. The `remote_attestation` template is a pattern to learn from, not the credential model for national institutions.

**Design principles**

1. The channel is never the trust anchor.
2. Recognition is reciprocal and explicit, never inherited.
3. Verification of a document is separate from belief in its content.
4. Any party can decline recognition without losing control of its own systems.
5. A component that enforces rules cannot expand its own authority.

## 2. Architecture

&#91;embedded content: architecture · 2 sovereign domains, 1 exchange layer\]

Each nation owns its root, recognition records, signers, verifier and ledger. Only signed artifacts, public keys and ledger checkpoints cross the exchange layer, and arrows run both ways because each nation is simultaneously issuer and verifier.

## 3. Threat model

The design assumes a well-resourced adversary, including a compromised insider in either state and a hostile third state. Each threat maps to the control that answers it and to the requirement IDs in section 14.

| ID | Threat | Example | Primary control | Req. |
| --- | --- | --- | --- | --- |
| T-01 | Impersonation of a nation or institution | Forged customs authority issues a certificate | Per-domain trust anchors, no cross-issuance, authenticated delegation | R-01, R-02 |
| T-02 | Tampering with a signed assertion | Quantity or origin field altered in transit or at rest | Canonical signing, content hashes, translation layer cannot touch the source record | R-03, R-14 |
| T-03 | Replay of valid evidence | Old export license resubmitted for a new shipment | Challenge-bound nonces, validity windows, per-transaction binding | R-05 |
| T-04 | Use of revoked or expired authority | Official keeps signing after dismissal | Signed status lists, freshness limits, fail-closed on unknown status | R-05, R-06 |
| T-05 | Authority escalation by a delegate | Regional office signs outside its commodity scope | Scoped delegation, verifier checks scope on every assertion | R-04 |
| T-06 | Insider key misuse | Administrator signs a false assertion | HSM custody, multi-party approval, dual control, signer attribution | R-09, R-10 |
| T-07 | Root key compromise | Theft or coercion of a national root | Offline root, ceremony controls, pre-planned recovery and re-recognition | R-11 |
| T-08 | Receipt repudiation or rewriting | A party denies acknowledging a shipment | Co-signed receipts, append-only logs, independently verifiable proofs | R-07, R-08 |
| T-09 | Split-view attack | Each party shown a different history | Gossiped log checkpoints, cross-signed tree heads | R-08 |
| T-10 | Coerced recognition | One state pressures the other to accept an anchor | Recognition is explicit, scoped, revocable, and logged by the recognizing side | R-02 |
| T-11 | Capture of the verifier itself | Enforcement component grants itself new authority | Anti-capture invariant: no self-escalation, no proxy laundering, bounded emergency authority | R-12 |
| T-12 | Semantic drift | Term mapped to a different legal category without notice | Mapping registry, visible transformations, human review of class changes | R-13 |
| T-13 | Denial of service or isolation | Link cut to stall trade | Offline verification, store-and-forward, degraded-mode rules | R-15 |
| T-14 | Future cryptanalysis | Recorded signatures broken later | Algorithm agility, post-quantum hybrid signing, long-term archive timestamps | R-10 |

**Assumed trust boundaries**

- Each nation's internal systems are trusted only by that nation.
- Transport networks, cloud providers and any intermediary relays are untrusted.
- Neither party trusts the other's operators or software supply chain beyond what is verifiable from signed artifacts.

**Explicit residual risk.** A fully corrupt issuing institution can sign false claims with valid authority. The system makes that attributable and auditable. It cannot make it impossible.

## 4. Sovereign identity and trust anchors

Each nation operates a self-contained trust domain. Nothing in one domain can issue, revoke or modify anything in the other.

**Domain structure (per nation)**

| Layer | Role | Custody |
| --- | --- | --- |
| National root (NR) | Signs institutional issuers only. Never signs assertions directly. | Offline HSM, quorum ceremony |
| Institutional issuer (II) | One per institution, for example customs, standards body, health inspectorate. Signs delegations to officials and systems. | Online HSM, dual control |
| Operational signer (OS) | Short-lived keys held by a role or system, scoped to a document class and commodity set. Signs assertions. | HSM-backed or hardware token, auto-expiring |
| Verifier agent (VA) | The local service that validates the other nation's artifacts. Holds no signing authority over assertions. | Separate from all signers |

**Cross-recognition**

1. Nation A publishes its national root and institutional registry through a signed trust bundle.
2. Nation B receives the bundle out of band, authenticates it through a pre-agreed ceremony (section 10), and stores a **Recognition Record**: which of A's issuers B accepts, for which document classes, for what period.
3. B's acceptance is B's decision alone. It is stored in B's domain, signed by B, and does not appear as a grant inside A's domain.
4. The same process runs in reverse. Recognition is never symmetric by default.
5. Either side can narrow or withdraw recognition at any time. Withdrawal takes effect for new verifications immediately and for in-flight transactions by explicit policy.

**Identifiers**

- Each issuer and signer has a stable, resolvable identifier bound to its public key set (DID-style or X.509 subject with a registry binding, to be chosen in the open questions).
- Identifiers include the sovereign domain, so a name can never be read in the wrong domain.

**Requirement.** No component may treat a message as authentic because of the channel it arrived on. Authenticity derives only from a chain to a trust anchor the verifier itself recognizes.

## 5. Assertion format

Every trade claim travels as a **Signed Assertion Envelope (SAE)**. The envelope is immutable once signed. Anything derived from it, including translations, is a separate object that points back to its hash.

| Field | Purpose | Rule |
| --- | --- | --- |
| `sae_version` | Schema version | Verifier rejects unknown major versions |
| `assertion_id` | Globally unique ID | UUIDv7 plus issuer prefix |
| `domain` | Issuing sovereign domain | Must match the signer's chain |
| `doc_class` | Certificate of origin, customs declaration, and so on | Must be inside the signer's delegated scope |
| `subject` | Goods, parties, shipment, contract references | Canonical form, no free-text-only identifiers |
| `claims` | The asserted statements | Typed, each with an evidence reference |
| `evidence_refs` | Hashes and locators of supporting records | SHA-256 minimum, content-addressed |
| `issued_at` / `not_before` / `not_after` | Validity window | Verifier enforces both ends against a trusted clock |
| `txn_binding` | Transaction ID and counterparty domain | Prevents reuse on another transaction |
| `challenge` | Nonce supplied by the verifier | Required for interactive flows |
| `authority_chain` | Chain from signer to national root | Every link carries scope and validity |
| `status_ref` | Pointer to revocation status | Freshness bound declared by policy |
| `source_hash` | Hash of the original institutional record | Ties the envelope to the legacy source |
| `signatures[]` | One or more signatures | Algorithm and key ID per signature |

**Canonicalization.** Signatures cover a deterministic serialization (RFC 8785 JSON Canonicalization or deterministic CBOR, to be fixed in the open questions). Verifiers reject envelopes whose canonical form does not reproduce the signed bytes.

**Multi-signature.** High-value classes can require two or more independent institutional signatures. The required set is defined by the receiving nation's recognition policy, not by the issuer.

**Privacy.** Commercially sensitive fields support selective disclosure (salted-hash commitments) so a verifier can validate a field it is entitled to see without receiving the rest.

**Cardinal rule.** A verified envelope proves origin, authority, integrity and freshness. It does not prove the claim is true.

## 6. Authority, delegation and anti-capture

Authority is data that is granted, scoped, time-bound and revocable. A claim of authority never substitutes for a verified grant. This section carries the SCC-001-AC anti-capture invariant into the trade setting and reuses the authority-gate logic from the repository.

**Delegation record**

- Grantor, grantee, target scope (document classes, commodity codes, counterparty domains, value ceilings), mode, validity interval, and a monotonically increasing grant serial.
- Scope can only narrow down the chain. A delegate cannot hold more than its grantor.
- Every record is signed by the grantor and logged in the grantor's domain ledger.

**Lifecycle**

| Event | Required behavior |
| --- | --- |
| Issue | Dual control for issuers; officials issued short-lived keys with auto-expiry |
| Renew | New serial, fresh signature, old grant remains valid only to its own expiry |
| Revoke | Signed status-list entry within a stated maximum latency; verifiers fail closed when status is older than policy allows |
| Rotate | Overlapping keys, with the old key accepted only for assertions timestamped before cutover |
| Suspend | Reversible hold, logged and visible to counterparties |
| Emergency | Finite positive TTL, bounded scope, issued by an authority external to the requester, auto-reverting |

**Anti-capture rules (normative)**

1. A verifier, monitor or supervisor component may detect, evaluate, deny and halt within its granted scope. It may not grant itself privileges, modify its own policy, redefine the principal, disable the principal's override, or turn an advisory score into authorization.
2. No self-authorized escalation. The authorizer must be authenticated, active, and cover the target, scope and mode requested.
3. No proxy-laundered escalation. The authorization chain must not pass through the actor or its proxy.
4. Emergency authority must carry a finite positive TTL that does not exceed the authorizer's own window.
5. Machine-learning risk scoring is advisory only. It can raise a flag for human review. It cannot approve a transaction or widen any authority.
6. Each nation retains a unilateral override path that no verifier component can quarantine, throttle or renew over.

Gate T8 and acceptance tests 11 to 18 in `sc_tol_001.py` serve as the executable reference for rules 1 to 4.

## 7. Bilateral exchange protocol

&#91;embedded content: protocol flow · 7 steps, 1 decision, 1 fail-closed exit\]

The verifier issues a challenge, the issuer signs an envelope bound to it, and the verifier runs every check before its own policy decides. A receipt exists only when both sides have signed and logged.

**Checks in step 3, each with its own reason code on failure**

1. Schema, version and canonical-form match.
2. Signature validity for every required algorithm (hybrid: all must verify).
3. Chain to a trust anchor the verifier recognizes, with recognition scope covering this document class.
4. Delegation scope at every link: class, commodity, counterparty domain, value ceiling.
5. Validity window against the trusted clock, within the agreed skew bound.
6. Revocation and suspension status, fresh within policy.
7. Challenge and transaction binding, so the envelope cannot be reused.
8. Replay cache: this `assertion_id` has not been accepted before for this transaction.

**Outcomes.** `accepted`, `accepted_with_conditions`, `deferred` (cannot establish a fact, retry allowed) and `rejected` (a check failed). Step 4 is the receiving nation's decision. A passing verification never forces acceptance.

## 8. Receipts and audit

Each completed transaction yields a **Bilateral Verification Receipt (BVR)** that either nation can verify alone, offline, years later.

**BVR contents**

- Hashes of every SAE involved, and the hash of any translation produced.
- Verifier identity and verification result per check: signature, chain, scope, validity window, revocation status, replay, binding.
- Trust bundle and recognition-record versions in force at verification time.
- Trusted timestamp from a time source both parties have agreed to, with a stated skew bound.
- The acknowledgment signature of the receiving institution, and, once exchanged, of the issuing nation.
- Outcome: `accepted`, `accepted_with_conditions`, `rejected`, or `deferred`, with machine-readable reasons.

**Dual ledgers**

1. Each nation keeps its own append-only, hash-chained ledger of everything it issued, received and decided.
2. Each ledger publishes signed checkpoints (Merkle tree heads) on a fixed cadence.
3. Each nation stores the other's checkpoints and verifies consistency proofs between them. A split view, where each side is shown a different history, becomes detectable.
4. Inclusion proofs let a party show that a given BVR is in the ledger without exposing the rest.

**Retention and long-term validity**

- Receipts are archived with the certificates, status data and timestamps needed to verify them after the original keys expire.
- Archive timestamps are renewed before the underlying algorithms weaken.
- Retention periods follow each nation's customs and commercial law and are a configuration, not a constant.

**Independence test.** If either nation's systems are unavailable, the other must still be able to verify a receipt using only the receipt, the published checkpoints and its own trust anchors.

## 9. Semantic translation layer

The two nations use different institutional vocabularies, code lists and document structures. The semantic compiler maps between them, and the mapping must be visible, versioned and unable to change what was signed.

**Rules**

1. The signed source SAE is never modified. A translation is a separate **Translation Record** that carries the source hash, the mapping version, and the output.
2. Every mapping lives in a signed registry, owned by the receiving nation and reviewed by the sending nation. Mappings have a version, effective date and review history.
3. Each translated field is tagged with its mapping type: `exact`, `narrowing`, `broadening`, or `no_equivalent`. Anything other than `exact` is shown to the human reviewer and logged in the BVR.
4. Changes of legal or regulatory category, such as tariff classification or controlled-goods status, always require explicit human or institutional confirmation. The layer cannot make them silently.
5. Unmapped terms pass through untouched and flagged, never guessed.
6. The translation layer holds no signing authority over assertions. It can sign only its own Translation Records, with a key that has no delegation chain to either national root.

**Use of the existing compiler.** The Domain Elevator and semantic IR supply the structural mapping and keep provenance (source SHA-256, transformation history). The anti-capture gates apply to the compiler too, in particular the rule that a generator cannot exempt its outputs from the immutable gates.

**Out of the translation path:** signatures, hashes, validity windows, authority chains and identifiers. These are compared byte for byte and never translated.

## 10. Cryptography and key custody

Choices below are the proposed baseline. The customer's national standards body or signals agency may mandate different suites, and the system must accept that without redesign, so every algorithm is referenced by identifier and replaceable.

| Function | Baseline | Notes |
| --- | --- | --- |
| Signatures | ECDSA P-384 or Ed25519 | Selected per policy of the verifying nation |
| Post-quantum | ML-DSA (FIPS 204) in a hybrid signature with the classical algorithm | Both must verify; protects recorded assertions against future attack |
| Hashing | SHA-256 minimum, SHA-384 for archives | Content addressing and ledger trees |
| Transport | Mutually authenticated TLS 1.3 with hybrid post-quantum key exchange where supported | Transport is defense in depth, never the trust anchor |
| Payload encryption | AEAD (AES-256-GCM or ChaCha20-Poly1305) for confidentiality between institutions | Per-recipient key wrapping |
| Timestamps | RFC 3161 timestamp authority, plus ledger checkpoint anchoring | Time source agreed bilaterally |

**Key custody**

- National roots: offline, in HSMs certified to a level the customer specifies (FIPS 140-3 Level 3 or equivalent national scheme), stored in separate secure locations.
- Root operations only through a documented ceremony: a quorum of custodians (for example 3 of 5), independent witnesses, scripted procedure, video and signed transcript.
- Issuer keys in online HSMs with dual control and separation of duties. No single person can sign, approve and deploy.
- Operational signing keys are short-lived and attributable to a named role.
- No signing key ever exists in software memory outside an HSM or token.

**Ceremonies required before go-live**

1. Root key generation for each nation.
2. Out-of-band trust bundle exchange and fingerprint verification by authorized officials of both states.
3. Recovery drill for loss of a custodian.
4. Compromise drill: revoke an issuer, rotate, and re-recognize.

**Crypto agility.** Algorithm sets are versioned in the policy. Migration to a new suite requires overlap periods and re-timestamping of archived receipts.

## 11. Security controls by layer

| Layer | Control | Detail |
| --- | --- | --- |
| Identity | Mutual recognition records | Explicit, scoped, revocable, logged by the recognizing side only |
| Access | Zero trust between all internal services | Service identities, mTLS, per-call authorization, no ambient network trust |
| Insiders | Dual control and separation of duties | No single person can sign, approve and deploy; privileged actions require two humans |
| Software supply chain | Reproducible builds, signed artifacts, SBOM | Each nation can rebuild and verify the verifier agent from audited source |
| Verifier isolation | Verifier runs in a hardened, minimal environment | No outbound access except declared endpoints; read-only configuration; attested at start |
| Policy | Policy as signed data | Changes need quorum approval, and are logged and visible to the counterparty |
| Input handling | Strict schema validation and size limits | Reject before parsing deeply; fuzzed parsers; no dynamic code in documents |
| Freshness | Challenge-response plus validity windows | Clock sync monitored; unsynchronized clocks fail closed |
| Logging | Append-only, hash-chained, off-host | Tamper evidence, not only access control |
| Monitoring | Detection of anomalous signing volume, scope probing, replay attempts | Alerts go to humans; the monitor has no authority to change grants |
| Data protection | Minimum disclosure | Selective disclosure and per-field encryption for commercial data |
| Physical | Controlled facilities for roots and HSMs | Two-person access, tamper-evident storage, audit |
| Testing | Independent penetration test, protocol review, formal analysis | Before pilot and before each major release |
| Incident response | Joint playbook | Compromise declaration, revocation broadcast, quarantine and recovery steps agreed by both nations in advance |

**Fail-closed default.** Whenever status, time, scope or chain cannot be established, the verifier returns `deferred` or `rejected`, never `accepted`.

## 12. Availability, disputes and failure handling

| Failure | Required behavior |
| --- | --- |
| Link to the other nation is down | Verification continues offline against the last trusted bundle and status data. Results are valid only inside the freshness bound declared by policy; past it, `deferred`. |
| Status service unreachable | Fail closed for high-value classes. Lower-value classes can allow a bounded grace period if the receiving nation's policy permits it. |
| Clock drift or disagreement | Reject on drift beyond the agreed bound. Log and alert. |
| Issuer key compromised | Issuer revoked in the grantor's ledger, revocation broadcast, assertions after the compromise time quarantined, joint review of earlier ones. |
| National root compromised | Declared by the owning nation. Counterparty suspends recognition immediately. Re-establishment needs a new ceremony and a new Recognition Record. |
| Ledger fork detected | Both sides stop acceptance for affected classes and run the joint investigation procedure. |
| Component failure | Redundant verifier instances in separate zones. A node that cannot prove its integrity is removed from rotation, not trusted by default. |

**Dispute handling**

1. Either party can open a dispute against a BVR or assertion, referencing hashes.
2. Both parties produce their ledger inclusion proofs and the evidence bundle.
3. Verification is re-run against the trust bundle and status data as they stood at the transaction time. The archive makes this reproducible.
4. The outcome records which check failed or which claim was contested. Who is liable is a matter for the nations' agreements, not the software.

**Service targets (to be agreed).** Proposed starting points: verification decision under 2 seconds at the 95th percentile for cached chains, revocation propagation within 15 minutes, recovery time objective of 4 hours, recovery point objective of zero for ledger data.

## 13. Compliance and legal boundaries

This section lists what must be established with each government's counsel and security authorities. It is an engineering checklist, not legal advice.

- **Export controls on the software itself.** Cryptographic and security software can be controlled in the vendor's country and the customer's. Establish classification and licensing before any technical exchange beyond the proposal stage.
- **Sovereignty and data residency.** Each nation's ledger, keys and archive stay in its own jurisdiction. The design has no required cross-border storage.
- **Standards alignment.** Map the design to the customer's mandated frameworks, for example ISO/IEC 27001, eIDAS-style trust-service models, WCO data models, UN/CEFACT trade documents and national PKI policy. The target set comes from the customer.
- **Evidentiary status.** Whether a BVR or an electronic signature has legal force in each jurisdiction is decided by that jurisdiction's law and by the treaty or agreement between the nations.
- **Sanctions and restricted-party screening.** Out of this system's authority, but the verifier must expose hooks so each nation can run its own screening against verified assertions.
- **Procurement and security clearance.** Government deployment normally needs a defined procurement route, personnel vetting, and supply-chain assurance. Confirm the route before committing to a delivery plan.
- **Information handling.** No classified or non-public government information enters the design phase. All pilots use synthetic data until each side's authority approves otherwise.

## 14. Acceptance criteria and adversarial tests

No requirement counts as met without an executable test and recorded result. Status stays `not implemented` until the test runs against a real build.

| Req. | Requirement | Test |
| --- | --- | --- |
| R-01 | Neither nation can impersonate the other | Forged-chain suite: foreign-signed assertion presented as domestic must fail |
| R-02 | Recognition is explicit, scoped, revocable, and held by the recognizer | Withdraw recognition mid-transaction; confirm policy outcome and that the grantor's domain is unaffected |
| R-03 | A signed assertion cannot be altered undetected | Bit-flip fuzzing across every field and the canonical form |
| R-04 | Delegated authority is scoped | Signer outside doc class, commodity or value ceiling is rejected |
| R-05 | Expired, revoked and replayed evidence are distinguishable from valid evidence | Matrix: valid, expired, not yet valid, revoked, replayed, wrong transaction, each with its own reason code |
| R-06 | Unknown status fails closed | Cut the status service; confirm `deferred` or `rejected` |
| R-07 | Both parties verify receipts independently | Verify a BVR with the counterparty offline |
| R-08 | Split views are detectable | Fork one ledger; confirm checkpoint comparison flags it |
| R-09 | No single person can sign, approve and deploy | Role-separation audit and attempted bypass |
| R-10 | Algorithm agility and post-quantum hybrid verification | Suite migration test; hybrid signature with one algorithm broken must still fail |
| R-11 | Root compromise is recoverable | Compromise drill end to end |
| R-12 | Anti-capture: no self-escalation, no proxy laundering, bounded emergency | Port of the T8 test set to the production authority service |
| R-13 | Translation cannot alter a signed record or silently change class | Mapping tests; hash of the source is unchanged; non-exact mappings flagged |
| R-14 | Source records retain provenance | Round trip from translated output to the original institutional record |
| R-15 | Degraded operation is defined and bounded | Chaos tests: link loss, clock drift, node failure |
| R-16 | Independent assurance | Third-party penetration test and protocol review with remediation tracked |

**Test layers.** Unit tests for each gate and operator; property-based tests on canonicalization and chain validation; interoperability tests between two independently configured trust domains; adversarial red-team exercises; long-run soak tests; and a formal model of the exchange protocol checked for authentication, freshness and non-repudiation properties.

**Exit rule.** Phase gates in section 15 open only when every listed requirement for that phase has a passing recorded run.

## 15. Implementation phases

&#91;embedded content: roadmap · 5 phases, 4 gates\]

No phase starts until the gate before it has passing, recorded test runs. Phase lengths are deliberately not given: they depend on the customer's answers in section 16 and on how much of the existing repository holds up under review. Phase 1 can begin as an internal build while Phase 0 is still open, because it needs no customer data.

## 16. Open questions

These decide the shape of the build. Several assumptions in this draft change depending on the answers.

- [ ] Who are the two parties, and who is the contracting customer? A government, a ministry, or a trade body acting for one?
- [ ] Is the second nation a real participant at this stage, or is the first deliverable a one-sided demonstration?
- [ ] Which document classes come first? A single class such as certificates of origin is a far safer pilot than the full list.
- [ ] Identifier and credential model: X.509 with a registry binding, DIDs with verifiable credentials, or an existing national scheme?
- [ ] Mandated algorithms and HSM certification level in each country.
- [ ] Existing national PKIs, single windows or customs systems this must integrate with.
- [ ] Agreed time source and acceptable clock skew.
- [ ] Who operates the verifier in each nation, and who audits it?
- [ ] Required availability, volumes and latency. The targets in section 12 are guesses.
- [ ] Legal standing of the receipts in each jurisdiction, and the governing agreement between the nations.
- [ ] Export-licence position for delivering cryptographic software to the customer.
- [ ] Who funds and owns independent assurance (penetration test, formal review)?
- [ ] What is the repository's current state for the components in section 15? Mapping here is from the earlier review of the code and has not been checked by me against the live repository.
