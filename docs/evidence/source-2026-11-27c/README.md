# Shax source, t611u (2026-11-27): SC-TOL-001 rc7 direction

| File | What it is | Bytes | SHA-256 |
|---|---|---|---|
| `t611u_message_body.txt` | Shax's t611u message, verbatim as relayed to the compiler. One header line was added. It reviews rc6 and sets the rc7 direction. | 3405 | `a3d3f45a75b2e3674be622dddf4e7a56ad12d15c28a8c08dc56e216ff5c9d8c0` |

**Attribution.** The direction is Shax's. The message does not say whether he wrote the wording himself or adapted it from an assistant conversation, so the wording is not attributed further.

**What it directs.**
- Keep the rc6 propagation rule; do not weaken it.
- Unverified substrate, speculative architecture and invalid architecture are not equivalent.
- Report a structural result, an epistemic result and a combined certification separately (example: PASS, SPECULATIVE / UNVERIFIED, QUALIFIED), so the compiler never implies that speculative means defective.
- rc7 investigation list: epistemic qualification propagates independently of structural failure; speculative generators can reach structural PASS without empirical certification; a child cannot silently upgrade a parent's qualification; the 963-prompt corpus stays a regression baseline.
- Do not chase the score or force GOLD.
- Protect the separation between what a structure is, what evidence supports claims about it, and who has authority to change it.
- Implemented as rc7 in `tests/reference/sc_tol_001/compiler.py` (tag `RC7`). See `docs/SC-TOL-001_TREE_OF_LIFE_STRUCTURAL_COMPILER.md` section 5b.

**This file is evidence.** The runtime does not load it.

**Personal data.** Before commit, the file was scanned for personal names and family names, birthdays, emails, phone numbers, addresses, URLs, and credentials. None were found, and **no redaction was made**.
