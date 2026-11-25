# Mobile Add-on Roadmap — Semantic Compiler Kernel as a Bolt-in for AI Mobile Apps

**Status:** Assessment / proposal (no code changes in this document's PR).
**Baseline:** `main` @ `7e63996` (V3.8.0), assessed 2026-11-25.
**Goal (Shax):** ship the kernel as a bolt-in add-on for any/all AI mobile apps.

Every statement below is tagged:

- **[Measured]** — observed on this commit (box: x86_64, 8 cores, CPython 3.13.5).
- **[Code]** — read directly from the source at this commit (file cited).
- **[Assumption]** — not verified here; needs a spike or Shax's decision.

---

## 1. What the kernel is today (facts that drive the packaging choice)

| Property | Finding | Tag |
|---|---|---|
| Language / runtime | Pure Python, `requires-python >=3.10`. No C extensions in the repo itself. | [Code] `pyproject.toml` |
| Runtime deps | `jsonschema>=4.0`, `PyYAML>=6.0`. `jsonschema` pulls `referencing`, `attrs`, `jsonschema-specifications` and **`rpds-py` (a Rust native extension)**. | [Measured] venv `pip list` |
| Where deps are used | `jsonschema` validates templates/schemas (`expansion/schema/*`, `expansion/gem_decode/schema.py`, `core/dataset.py`). `PyYAML` loads the 46 domain templates (`expansion/templates/*.yaml`). | [Code] |
| Network / process I/O | No `requests`/`urllib`/`socket`/`subprocess` use in library code. Fully offline-capable. | [Code] grep over non-test `.py` |
| Models / ML | None. The pipeline is deterministic rule/regex/graph logic — no weights, no GPU, no LLM calls. | [Code] `core/pipeline.py`, `extraction/*` |
| Public entry point | `semantic_compiler.compile_semantic_packet(input_text, registry=None, context=None, mode="AUTO") -> SemanticPacket`; `SemanticPacket.to_dict()`; `semantic_compiler.expansion.decompress(packet)`. | [Code] `__init__.py`, `core/pipeline.py:1101`, `core/packet.py:186` |
| Code size | ~12.6k LOC in `core/ gates/ extraction/ translation/ modes/`, ~15.4k LOC in `expansion/`. Repo (minus `.git` and `calibration_output/`) ~9.9 MB; `calibration_output/` (14 MB) is not in the wheel (`MANIFEST.in`). | [Measured] |
| Language coverage | Extraction heuristics are English-specific (e.g. English plural suffix rules in `extraction/skeleton.py`). | [Code] |
| Tests | 555 pytest + 103 subtests pass; 247 unittest pass. | [Measured] |

### Performance baseline [Measured, x86_64 desktop-class CPU]

| Step | Time |
|---|---|
| `import semantic_compiler` (core only) | ~0.06 s |
| First `compile_semantic_packet` in a process | ~0.045 s |
| Warm `compile_semantic_packet` (avg of 30) | ~12–14 ms |
| `import semantic_compiler.expansion` | ~0.20 s |
| First `decompress()` with **no** template cache (YAML parse + schema validation of 46 templates) | ~0.33 s |
| `decompress()` after the sidecar cache exists | ~12 ms (compile + decompress) |
| Peak traced Python allocation for the benchmark run | ~14 MB (RSS ~44 MB incl. interpreter) |
| `SemanticPacket.to_dict()` as JSON for a one-sentence input | ~33 KB |

**[Assumption]** Mid/high-end phone CPUs running CPython are roughly 2–4× slower than this box per core, so expect ~30–60 ms per warm compile and ~0.5–1.5 s cold start on-device. This must be measured on the S26 Ultra (Termux CPython is the cheapest first measurement).

---

## 2. Packaging options

| # | Option | How the host AI app uses it | Pros | Cons / risks | Fit |
|---|---|---|---|---|---|
| A | **Local/remote HTTP API** (thin FastAPI/stdlib server around `compile_semantic_packet`) | App POSTs text, gets packet JSON | Zero port of the Python code; works for every app/platform immediately; easiest to version | Remote = latency, hosting cost, user text leaves device (privacy); AGPL §13 applies to anyone running it as a network service | **Best first step (weeks, not months)** |
| B | **MCP server** (stdio + streamable HTTP) exposing `compile`, `decompress`, `route_domain`, `list_invariants` tools | Any MCP-capable assistant (desktop and increasingly mobile clients) calls it as a tool | Same code as A; matches how AI apps already add capabilities; discoverable | Mobile MCP client support varies by app [Assumption]; still a server process | **Ship alongside A** |
| C | **Embedded Python on Android** (Chaquopy or CPython's official Android support, PEP 738) wrapped in a Kotlin `.aar` SDK | Kotlin call `SemanticCompiler.compile(text)` returning JSON | Runs fully on-device/offline; reuses code unchanged | Adds ~10–20 MB of interpreter to the APK [Assumption]; `rpds-py` needs an Android wheel or must be removed (see §4) | **Main on-device path for Android** |
| D | **Embedded Python on iOS** (CPython official iOS support, PEP 730, via BeeWare/Briefcase-style XCFramework) wrapped in a Swift package | Swift call returning JSON | On-device/offline | Same interpreter-size and native-wheel issues as C; App Store review of embedded interpreters is fine if no code is downloaded at runtime [Assumption] | Second on-device path |
| E | **Native port** (Rust core → Kotlin/Swift bindings, or Kotlin Multiplatform) | Tiny native library | Smallest/fastest; no interpreter | Rewrites ~28k LOC; doubles the maintenance surface; high drift risk from the Python canon | Long-term only, after the API stabilises |
| F | **WASM** (Pyodide in a WebView, or a later Rust→WASM build) | Hybrid/React-Native/web-view apps | One artifact for web + mobile WebViews | Pyodide payload is large (multi-MB) and cold start is slow [Assumption] | Niche |
| G | **Keyboard (IME) or Accessibility-service layer** | Intercepts text in *any* app, compiles it before it reaches an AI app | Truly "bolt into any app" without each vendor integrating | Android Accessibility and IME are heavily policy-restricted (Play policy on Accessibility API use; sensitive-input exposure); iOS keyboards are sandboxed and no network by default; very high trust/privacy bar | Only as an opt-in power-user tool; not the primary channel |

**Recommendation [Assumption, needs Shax's decision]:** A + B first (one server codebase, usable this month by any app that can call an API or an MCP tool), then C (Android SDK) because the founder device and current users are Android/Termux, then D. Treat E as a v5 decision once the API surface is frozen. Treat G as experimental.

---

## 3. Integration points for a host AI app

Grounded in the current pipeline stages (`core/pipeline.py`):

1. **Pre-prompt compiler** — run `compile_semantic_packet(user_text)` before the LLM call; inject a compact summary (decision, selected target domain, contradictions, unknowns, category errors) into the system prompt or as a tool result.
2. **Post-response audit** — compile the model's answer and surface the gate results (`testimony_integrity_gate`, `causal_analysis`, `contradictions`, `category_errors`) as a "reasoning check" badge.
3. **Domain router** — `expansion.decompress()` / the Domain Elevator (`expansion/elevator.py`) picks one of 46 domain templates; host apps can use that to pick prompts, tools, or specialist models.
4. **Dataset tap** — `core/dataset.py` already emits SFT/DPO rows with redaction; an opt-in "export my compiled sessions" feature for fine-tuning.

**Required API work before any SDK [Code-grounded]:**

- A **stable, versioned, compact output contract** (e.g. `packet.summary_v1()`): the full `to_dict()` is ~33 KB and includes `raw_input` and `normalized_input`, which is too heavy for per-message mobile use and carries user text verbatim.
- A **JSON-in/JSON-out facade** (`semantic_compiler.api.compile_json(str) -> str`) so Kotlin/Swift/JS bindings only marshal strings.
- **Explicit cache location**: the template sidecar cache is written to `tempfile.gettempdir()` (`expansion/registry/loader.py:_sidecar_cache_path`). On mobile it must be configurable (app cache dir) or replaced by a pre-built cache shipped inside the package.
- **Thread-safety review**: several modules hold module-level caches (`functools.lru_cache` in `translation/buildcraft.py`, `translation/structural_resolver.py`, `core/dataset.py`) and module-level state in `expansion/` (e.g. `expansion/elevator.py`, `expansion/consciousness/*`). Not yet audited for concurrent calls from multiple app threads [Assumption: likely safe for read-only lookups, unverified].

---

## 4. Performance and size work (ordered by payoff)

1. **Precompile templates at build time** [Code + Assumption]: ship the 46 templates as one validated JSON blob (the sidecar format already exists). Then on-device runtime needs neither PyYAML nor `jsonschema` → drops the `rpds-py` native wheel problem entirely and removes the ~0.3 s cold parse.
2. **Lazy-import `expansion`** [Measured]: core import is ~0.06 s, `expansion` adds ~0.2 s; only import the expansion subpackages a call actually needs (e.g. `consciousness.domain_expansion` alone is ~30 ms of import time).
3. **Slim profile** [Assumption]: a `semantic-compiler-kernel[mobile]` build that excludes `gem_forge/data` (~850 KB), scripts, benchmarks, and docs.
4. **Compact output** (see §3) to cut serialization and bridge-marshalling cost.
5. **On-device benchmark harness**: add `scripts/bench_mobile.py` reproducing the §1 table so every release reports phone numbers (Termux on the S26 Ultra first).

---

## 5. Licensing (AGPL-3.0 + Commercial dual license)

- **[Code]** The repo is `AGPL-3.0-or-later` with a separate `COMMERCIAL_LICENSE.md`.
- **Closed-source mobile apps** that embed the kernel (options C/D/E/G) would have to release their app source under AGPL — in practice that means almost every commercial app vendor needs the commercial license. This is the revenue lever for the add-on.
- **Hosted API/MCP (A/B)**: AGPL §13 obliges whoever operates a modified network service to offer its source to users. If Reflexion Software runs the API itself, it is the copyright holder and is not bound the same way [Assumption — get legal confirmation]. Third parties self-hosting need AGPL compliance or a commercial license.
- **Contributor rights**: dual licensing only works cleanly if Reflexion holds rights to all contributions. Commit history includes AI-tool co-author trailers (Claude, Cursor Agent) and imported patch sets (`patches/`); a CLA/DCO policy should be in place before selling commercial licenses for the add-on [Assumption — needs legal review].
- **Wording to check**: `COMMERCIAL_LICENSE.md` §1 describes the AGPL grant as for "open-source, non-commercial, academic, and research environments". The AGPL itself does not restrict commercial use; it requires source disclosure. Shax may want that wording reviewed so the terms are not contestable.
- **Third-party deps**: `jsonschema` (MIT), `PyYAML` (MIT), `rpds-py` (MIT), `referencing`/`attrs` (MIT); compatible with both license tracks [Assumption — verify at the pinned versions]. Embedded-Python runtimes (CPython PSF license; Chaquopy MIT since 2022 [Assumption]) are permissive.

---

## 6. Proposed phased plan

| Phase | Deliverable | Exit criteria |
|---|---|---|
| 0 | `api.compile_json` facade + `summary_v1` contract + configurable cache dir + precompiled templates | Existing tests green; new contract tests; core runs without PyYAML/jsonschema installed |
| 1 | HTTP API + MCP server (`semantic_compiler.server`) | Termux-on-phone and box both serve it; latency table recorded |
| 2 | Android `.aar` (embedded CPython) + sample app | Offline compile on the S26 Ultra; APK size delta recorded |
| 3 | iOS Swift package | Same on an iPhone simulator/device |
| 4 | Decide on native port (Rust/KMP) using phase 1–3 numbers | Written go/no-go |

---

## 7. Open questions for Shax

1. Is on-device/offline a hard requirement (privacy pitch), or is a hosted API acceptable for v1?
2. Who are the first target host apps (own apps such as ReflexionShell, or third-party assistants via MCP)?
3. Commercial pricing for SDK embedding versus hosted API usage?
4. Should non-English input be in scope for v1? Extraction is English-only today.
5. CLA/DCO policy for contributions before selling commercial licenses?
