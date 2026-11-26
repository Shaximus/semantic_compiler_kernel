# Shax source, t599u (2026-11-26): SCC-001-AC Anti-Capture Invariant

| File | What it is | Bytes | SHA-256 |
|---|---|---|---|
| `SCC-001-AC_original.md` | **The attached rc1 spec, verbatim** (`scc_001_anti_capture_invariant.md` in t599u). Sections: verification metadata, 1 core principle, 2 Authority Graph and strict role-edge constraints, 3 AC-1..AC-5, 4 Mafuba test oracle and TEST-AC-01..05, 5 audit contract (Python), 6 execution order and handoff directive for Hannah. Byte-identical to the attachment; no trailing newline, as delivered. | 14445 | `d834c16162df19dcde2a106322d002ce53eb6cfc9eeca9646774dd48e31e0737` |
| `t599u_message_body.txt` | The text of Shax's t599u message: the rc1 registry line, his note on the two Canvas files, and the review (five refinements, the section-5 identity ambiguity, TEST-AC-06, the implementation order, the classification recommendation). Zero-width spaces at the start of three lines were removed; nothing else was changed. One trailing newline. | 8075 | `f4bed4ff432a78b1bcf8713460a84ad651716d6d6809ff3a0b4a6e42f968a2ca` |

**Correction.** PR #89 recorded `3d9214009385261117e1a243329465e0347984b0f00dc7d8f9d51d529d0c35ad` as the spec hash. That was the attachment's filename, not its content hash. The real content hash is the one above, and the registry now carries it.

**Personal data.** Before it was committed, `SCC-001-AC_original.md` was scanned for family names (Kayla, Mike), birthdays and dates of birth, personal testimony, emails, phone numbers, addresses, financial details and credentials. None were found, and **no redaction was made** (`provenance.redactions: []`). The only person named is Hannah, as the recipient of the section 6 engineering handoff; the repository already credits her as a collaborator. The message text was checked the same way, with the same result.

**These files are evidence.** The runtime does not load them. They carry no grade. The refined rc2 spec is `docs/SCC-001-AC_ANTI_CAPTURE.md`, which quotes rc1 verbatim beside each refinement.
