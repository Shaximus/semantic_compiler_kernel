# StarCraft ability catalogue: evidence

Evidence for `docs/STARCRAFT_ABILITY_THEOLOGY_MAP.md` (Shax t587u, 2026-11-25).

| File | Contents | SHA-256 |
| --- | --- | --- |
| `abilities.jsonl` | One record per catalogued ability (151 records): mechanic, counterpart, citation, invariant, grade, residual, MAFUBA note, flags, source keys. | `b3ce20031d4e7f523392d8960021d0e26fd55638b229e42e5fb9dac80d2a8b43` |
| `sources.jsonl` | One record per wiki page used (133 pages: 83 Liquipedia StarCraft II, 37 Liquipedia Brood War, 13 StarCraft Wiki). Title, revision ID and timestamp at time of check, URL, permalink, and SHA-256 of the fetched wikitext. | `05978d723f0169f08a94f3567aae381885b48feb8dbcfb5ec882cd8fbdd4c8f1` |

## How the pages were read

- Liquipedia pages and their `SCSpell/*` and `SCAbility/*` templates were fetched through the MediaWiki API (`action=query&prop=revisions`) on 2026-11-25 (America/Toronto). Ability names were extracted from the templates each unit page transcludes, and from `{{Ability|name=...}}` blocks on Brood War pages. Abilities listed only under "Removed" sections are excluded (for example the Infestor's Infested Terran and the Raven's Seeker Missile).
- Campaign-only abilities come from the StarCraft Wiki (Fandom). They are flagged `CAMPAIGN_ONLY` and kept in a separate section.
- Wiki text is not copied into the repository (Liquipedia and Fandom text is CC BY-SA). Only titles, revision IDs, permalinks and hashes are kept, so a reader can open the exact revision that was checked.
- Liquipedia's StarCraft II pages were being edited on the day of the check. A revision ID is the one current when the metadata was read; the hash is of the text that was fetched.
- Scripture references are to chapter and verse. Short phrases in the map follow common English translations (ESV wording where quoted).
