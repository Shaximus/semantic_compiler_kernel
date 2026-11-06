# CLAUDE.md — Kali Linux Environment, Tooling & GitHub Access Directives

> [!IMPORTANT]
> **OPERATIONAL SECURITY & DEVICE INTEGRITY DIRECTIVE:**
> - **Device:** Samsung Galaxy S26 Ultra (`SM-S948W`), Android 17, Kernel 6.12.69 (aarch64).
> - **Knox Warranty Bit: `0x0`** (Strictly preserved; locked bootloader, zero partition writes, zero boot image flashing).
> - **Execution Mode:** Kali Linux Rolling PRoot container under Termux. Privileged operations bridge through `su` / `sugate`.
> - **Anti-Manipulation Squad Protocol:** Enforce strict forensic neutrality, zero error suppression, fail-closed validation, and git cryptographic integrity.

---

## 1. GitHub Access, Identity & Workflow Configuration

### Identity Profile
- **GitHub Username:** `Shaximus`
- **Committer Email:** `shaximusoverride6@gmail.com`
- **Primary Org / User Profile:** `https://github.com/Shaximus/`

### Global Git Configuration (Pre-configured)
Both `/root/.gitconfig` and `/home/claude/.gitconfig` are configured with:
```gitconfig
[user]
    name = Shaximus
    email = shaximusoverride6@gmail.com
[safe]
    directory = *
[core]
    pager = cat
[credential]
    helper = store
```

### GitHub CLI (`gh`) Integration
- **Binary Location:** `/usr/bin/gh` (v2.103.3 ARM64)
- **Authentication Options:**
  1. **Token Authentication via Environment Variable (Recommended for CLI agents):**
     ```bash
     export GH_TOKEN="<YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>"
     export GITHUB_TOKEN="$GH_TOKEN"
     ```
  2. **Non-Interactive Login via Token:**
     ```bash
     echo "$GH_TOKEN" | gh auth login --with-token
     ```
  3. **Credential Store for Standard Git:**
     ```bash
     echo "https://Shaximus:${GH_TOKEN}@github.com" >> ~/.git-credentials
     chmod 600 ~/.git-credentials
     ```
  4. **SSH Key Pair Generation & Upload:**
     ```bash
     ssh-keygen -t ed25519 -C "shaximusoverride6@gmail.com" -f ~/.ssh/id_ed25519 -N ""
     gh ssh-key add ~/.ssh/id_ed25519.pub --title "SM-S948W-Kali-PRoot"
     ```

### Critical Git Execution Rules in PRoot / Termux
1. **Zero Pager Hanging:** Never invoke git commands with interactive pagers (`less`). Always use `--no-pager` or ensure `GIT_PAGER=cat` is set.
2. **Safe Directory Exemption:** Always maintain `git config --global --add safe.directory '*'` across all users to prevent `fatal: detected dubious ownership` across PRoot UID boundaries.
3. **Clean Commits & Branch Conventions:**
   - Default branch: `main`
   - Atomic commits with semantic prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.

---

## 2. Defensive Cybersecurity & Anti-Manipulation Mandate

1. **Mandatory Dual-Hypothesis Framework:**
   - Never provide unilateral benign dismissals for unexpected behavior, network anomalies, throttles, or routing divergences.
   - Always evaluate:
     1. **Adverse / Adversarial Hypothesis:** Tampering, unauthorized interception, deliberate throttling, injection, or misrouting.
     2. **Architectural / Operational Hypothesis:** Legitimate platform design, carrier policy, OEM behavior, or expected failure modes versus deliberate architecture.
2. **Zero Error Suppression:**
   - Under no circumstances redirect errors to `/dev/null` (`2>/dev/null` is strictly prohibited).
   - All standard error outputs (`stderr`), stack traces, and exit statuses represent forensic evidence and must be retained in logs.
3. **Frozen Directory Policy:**
   - In repositories with frozen contracts (such as `semantic_compiler_kernel` where `core/` and `registry/` are designated frozen), do **not** modify frozen paths without an explicit user waiver.
   - Isolate compatibility layers in wrappers (e.g. `compat.py`) or separate modules.
4. **Pre-commit Integrity Verification:**
   - Always run test suites and linters before committing.
   - Run `git apply --check` before applying external patches.
   - Record SHA-256 hashes of input patches and generated release bundles.

---

## 3. Key Repositories & Workspace Map

| Repository / Worktree | Location | Upstream Remote | Status / Purpose |
|---|---|---|---|
| **Semantic Compiler Kernel (Host)** | `/data/data/com.termux/files/home/semantic_compiler_kernel` | `https://github.com/Shaximus/semantic_compiler_kernel` | Active working tree with 01–07 patches applied |
| **Semantic Compiler Kernel (Kali Review)** | `/root/imports/semantic_compiler_kernel_v3_review` | `https://github.com/Shaximus/semantic_compiler_kernel` | Staged review tree |
| **Forensics Lab** | `/data/data/com.termux/files/home/forensics-lab` | `https://github.com/Shaximus/forensics-lab.git` | System forensics, network audits, Knox telemetry |
| **Nexus Relay** | `/data/data/com.termux/files/home/nexus-relay` | Cloudflare Workers / Durable Objects | Hardened multi-tenant relay core |
| **Downloads & Ingestion** | `/sdcard/Download/` | N/A | Inbound patches, review reports (`REVIEW_REPORT-1.md`), zips |
| **Operator Staging** | `/storage/emulated/0/Alarms/agy-file-staging/` | N/A | Exported reports, audit bundles, deliverable archives |

---

## 4. Semantic Compiler V3.0.0 Patch Set Reference

- **`00-ALL-IN-ONE.patch`**: Comprehensive patch combining 01 through 07.
- **`01-buildcraft-resolver.patch`**: Structural resolver, item/slot collisions, whole-word matching.
- **`02-isomorphism-organ-detector.patch`**: Whole-token department presence matching, negation windows.
- **`03-medical-ontology-and-decompression.patch`**: Medical ontology alignment, whole-word domain router.
- **`04-packaging-and-readme.patch`**: Wheel packaging fixes, pyproject template inclusion.
- **`05-frozen-dirs-need-waiver.patch`**: `core/pipeline.py` claim_type fix, `registry/cosmological_constants.py` consistency checks.
- **`06-deep-system-domains.patch`**: Invariant templates (`mobile_security`, `networking`, `trust_chain`), `docs/DEEP_SYSTEM_INVARIANTS.md`.
- **`07-kestrel-integration.patch`**: `compat.py` pipeline wrapper, CI workflow (`.github/workflows/ci.yml`), Kestrel lab regressions.

---

## 5. Quick Verification Commands

```bash
# Verify Git identity
git config --get user.name
git config --get user.email

# Verify GitHub CLI status
gh auth status

# Verify test suite in semantic compiler
cd /data/data/com.termux/files/home/semantic_compiler_kernel
python3 -m unittest discover -s tests -q
```
