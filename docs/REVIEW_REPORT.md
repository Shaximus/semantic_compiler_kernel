# Semantic Compiler Kernel V3.0.0 — review, repair and upgrade

Date: 2026-11-06. Reviewed: `github.com/Shaximus/semantic_compiler_kernel` (HEAD as cloned this session), in a local clone only.

**Authoritative full text:** project folder `REVIEW_REPORT.md` (23 096 bytes). Large narrative sections remain in the project folder; this file holds the measured results and patch map.

## Result in numbers

| | Before (pristine HEAD) | After |
|---|---|---|
| `pytest tests` | 223 passed (README claimed 211) | 336 passed (305 after patches 01-05, plus 31 for patch 06) |
| `unittest discover` | 82 tests | 133 tests |
| Missing-organ benchmark, absent-confirmed recall | 0.805 (66 TP / 16 FN) | 1.000 (82 TP / 0 FN) |
| Missing-organ benchmark, absent-confirmed precision | 0.985 (1 FP) | 0.921 (7 FP) |
| Installed wheel: `import semantic_compiler.expansion` | `ModuleNotFoundError` | works, medical decompress runs |

## Patch files (apply in order; 05 needs waiver; 06 is domain expansion)

| File | Touches | Notes |
|---|---|---|
| `01-buildcraft-resolver.patch` | `translation/structural_resolver.py`, `translation/buildcraft.py`, 2 test files | |
| `02-isomorphism-organ-detector.patch` | `translation/fractal.py`, new `tests/test_department_presence.py` | |
| `03-medical-ontology-and-decompression.patch` | `expansion/{__init__,advisor,ontology,pathology}`, new test | |
| `04-packaging-and-readme.patch` | `pyproject.toml`, `README.md`, new packaging test | |
| `05-frozen-dirs-need-waiver.patch` | `core/pipeline.py` (one line), `registry/cosmological_constants.py`, 2 new test files | README says `core/` and `registry/` are frozen |
| `06-deep-system-domains.patch` | templates + `docs/DEEP_SYSTEM_INVARIANTS.md` | mobile_security, networking, trust_chain |
| `07-kestrel-integration.patch` | `compat.py`, CI workflow | Kestrel lab branch |
| `00-ALL-IN-ONE.patch` | combined | Prefer for single apply |

## Expansion added in the same session (2026-11-06)

- `expansion/templates/android_connectivity.yaml` — Ark pattern-lock / connectivity diagnosis domain
- `expansion/templates/bluetooth.yaml` — Bluetooth/BLE domain (adapter, classic/LE, bonding, GATT, audio, permissions, HAL/firmware, coexistence)

## Known limitation (still open)

`decompress()` does not read the input for component extraction; it copies from the domain template. Cross-domain missing-organ reconstruction therefore does not happen inside `decompress` today. See project-folder report section D for the design note and pinned test.
