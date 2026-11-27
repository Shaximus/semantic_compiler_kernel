# SC-SOV-TRADE-001 — Root ceremony runbook (software rehearsal)

This runbook describes the scripted 3-of-5 Shamir split of national-root
signing material implemented in `sov_trade/ceremony.py`. It is a **software
rehearsal** for tests and dry runs. It is **not** a witnessed national root
ceremony, it does not satisfy a certified-HSM requirement, and it does not
answer the section 16 questions about who the custodians are or which
jurisdiction governs the root.

Use a certified hardware security module, air-gapped hosts, independent
witnesses and a legal procedure before any real root is generated. The
PKCS#11 signer (`sov_trade/pkcs11.py`) is the interface that a certified
module can back, by configuration, with no code changes.

## Roles

- **Custodians:** five officers. Any three can reconstruct. Two or fewer cannot.
- **Ceremony officer / clerk:** runs the scripted procedure, never holds a
  reconstructed root after the split, and does not keep a share.
- **Witnesses (real ceremony only):** independent observers who attest that
  the published root public key and the commitment were produced in front of
  them. This rehearsal has no witnesses.

No single officer may hold SIGN, APPROVE and DEPLOY (see `sov_trade/custody.py`).

## Prerequisites

- `cryptography>=50.0.2` (hard requirement of `sov_trade`).
- For token-resident keys: a PKCS#11 module (SoftHSM2 in tests; a certified
  HSM in a real ceremony) and a PIN that is never committed or logged.
- An air-gapped host for a real ceremony. This rehearsal may run on a
  development machine with ephemeral secrets only.

## Procedure

1. **Prepare.** Confirm five custodians are present (or five test officers).
   Confirm the threshold is 3 of 5. Confirm no recording of secret material
   other than the published public key and the SHA-256 commitment.
2. **Generate.** Call `run_root_ceremony(n=5, k=3)` (or the equivalent CLI
   wrapper). The implementation draws a 32-byte Ed25519 seed, splits it with
   GF(256) Shamir (AES polynomial), and drops the unsplit secret from the
   result object.
3. **Publish.** Record the root **public** key and the SHA-256 **commitment**
   of the secret. These are not secret. They are the values later used to
   detect a tampered share.
4. **Distribute.** Give share *i* to custodian *i* only, out of band. Shares
   must not be committed to the repository, copied to a ticket, or written
   into logs. In tests, shares live in a temporary object and are discarded
   when the test process exits.
5. **Quorum check (rehearsal).** Any three shares reconstruct the seed,
   recover the same public key, and can sign. Two or fewer shares raise
   `CeremonyError` (`quorum not met`). A share whose bytes have been altered
   fails the commitment check (and, when more than three shares are offered,
   fails subset consistency).
6. **Use.** The reconstructed root may sign issuer certificates and
   delegations. It must never sign a trade assertion (enforced by
   `sign_sae`). After the signature is produced, wipe the reconstructed seed
   from the process.
7. **Compromise drill.** If a share is lost or suspected, generate a new
   root, re-run the ceremony, and re-issue issuer recognition as in R-11.
   Do not lower the threshold to recover a missing quorum.

## What this rehearsal does not do

- It does not generate the root inside a certified HSM (SoftHSM2 is a
  software token; keys there are still software, even if they are
  non-extractable through the PKCS#11 API).
- It does not provide legal evidence, a witnessed transcript, or a
  jurisdictional policy.
- It does not implement a hardware threshold signature (the 3-of-5 split
  reconstructs the seed, then signs). A production design may prefer a
  native threshold scheme so the seed is never reassembled in software.
- Independent assurance (R-16) is still not met.

## Recovery

If reconstruction fails with a commitment mismatch, treat the offered
shares as tainted. Repeat with a different custodian trio. If every trio
fails, the root is unrecoverable; begin a new ceremony and re-recognize
issuers under the new public key.
