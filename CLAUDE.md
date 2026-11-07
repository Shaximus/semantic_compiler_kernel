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

## 2. Defensive Cybersecurity, Anti-Friction Directives & Integrity Mandate

1. **Mandatory Dual-Hypothesis Framework:**
   - Never provide unilateral benign dismissals for unexpected behavior, network anomalies, throttles, or routing divergences.
   - Always evaluate:
     1. **Adverse / Adversarial Hypothesis:** Tampering, unauthorized interception, deliberate throttling, injection, or misrouting.
     2. **Architectural / Operational Hypothesis:** Topology constraints, upstream pooling, legacy configs, or RF cell-edge conditions.
     3. **Bayesian Probability Modeling:** Quantify compound probability of independent failure modes required for benign coincidence versus deliberate architecture.
2. **Zero Error Suppression & Zero Stream Truncation:**
   - Under no circumstances redirect errors to `/dev/null` (`2>/dev/null` is strictly prohibited).
   - All standard error outputs (`stderr`), stack traces, and exit statuses represent forensic evidence and must be retained in logs.
   - Never pipe live outputs directly into truncating filters (`head`, `tail`) that cause `SIGPIPE` / `Broken pipe`. Write full dumps to disk first.
3. **Context-Aware Command Sequencing (Fail-Fast `&&` vs. Independent Captures):**
   - For **SWE, code builds, test pipelines, git operations, migrations, and dependent tasks**: Enforce fail-fast execution (`&&`). Never allow downstream mutating or testing steps to proceed if an earlier prerequisite step fails.
   - For **independent forensic telemetry captures**: Execute commands as separate invocations or scripts so a failure in one subsystem does not truncate evidence collection from remaining rings.
4. **Privilege Management & Least Privilege (`least_privilege_process_confinement`):**
   - Default to unprivileged inspection (`u0_a385`, userland dumpsys, procfs) for all initial investigation steps.
   - Elevate to root (`su` / `sugate`) only when protected boundaries (restricted `telephony.db`, raw netlink, kernel routing, `iptables`, ART bytecode utilities) strictly require root capabilities.
   - **Batched Root Execution:** Batch all required root commands into a single script or execution block to avoid triggering multiple biometric prompts.
   - **Inform Before Prompt:** Tell the operator before initiating a root prompt. Do not use silent root backdoors (`run_root.py` / `~/bin/r`) unless explicitly requested by the owner for that task.
5. **Biometric Cancellation Protocol (Strict Ban on Auto-Retry Loops):**
   - Whenever an interactive biometric authentication prompt (`su` / `sugate`) is canceled, dismissed, or rejected (`Fingerprint operation canceled` or non-zero exit), **NEVER AUTO-RETRY IN A LOOP**.
   - Immediately halt the privileged routine, plainly log the cancellation without error suppression, inform the operator of the halted task, and present an unprivileged alternative or await owner instruction.
6. **Diagnostic Safety & Cellular Quota Protection:**
   - **Root Logcat Trap:** Never run `logcat` or `bugreport` under root. `/system/bin/logcat` on this handset is a wrapper that stages `ksud`, adds a bind mount, and attempts a late-load. Use `dumpsys` rings instead (`dumpsys telephony.registry`, `dumpsys tethering`, etc.).
   - **Cellular Quota Invariant (`separate_phone_from_carrier`):** The owner's cellular allowance is metered and may be $0. Never run throughput tests (`iperf3`, `speedtest`), bulk package downloads, or large git pushes over mobile data without explicit owner approval.
   - **Dumpsys Ring Invariant (`capture_the_ring`):** Dumpsys rings rotate rapidly; capture them early to persistent disk files before they scroll.
7. **Frozen Directory Policy:**
   - In repositories with frozen contracts (such as `semantic_compiler_kernel` where `core/` and `registry/` are designated frozen), do **not** modify frozen paths without an explicit user waiver.
   - Isolate compatibility layers in wrappers (e.g. `compat.py`) or separate modules.
8. **Pre-commit Integrity Verification:**
   - Always run test suites and linters before committing.
   - Run `git apply --check` before applying external patches.
   - Record SHA-256 hashes of input patches and generated release bundles.

---

## 3. Mandatory Semantic Compiler System Pattern Mapping

For all system diagnoses, Android forensics, network audits, radio/tethering repairs, and SWE tasks, mapping system patterns via the Semantic Compiler is **MANDATORY**:

1. **Domain Selection & Schema Resolution:**
   Identify the canonical domain (`android_connectivity`, `mobile_security`, `networking`, `trust_chain`, `computation`, etc.) using `semantic_compiler` registry templates.
2. **Component (System Organs) Mapping:**
   Map observed entities against canonical components:
   - *Android Connectivity:* `radio_registration`, `data_session_apn`, `subscription_resolver`, `carrier_policy_config`, `usb_gadget_link`, `tether_state_machine`, `downstream_host`, `policy_router`, `forward_firewall`, `bpf_offload_path`, `usage_accounting`, `carrier_quota`, `sms_intake_store`, `file_encryption_store`, `boot_integrity`, `runtime_root_layer`.
   - *Mobile Security:* `hardware_root_of_trust`, `bootloader_state`, `verified_boot_chain`, `rollback_protection`, `verified_partition_integrity`, `app_signing_identity`, `app_sandbox`, `selinux_policy`, `runtime_permission_gate`, `ipc_boundary`, `file_based_encryption`, `keymint_keystore`, `secure_execution_environment`, `credential_authenticator`, `key_attestation`, `protected_virtual_machine`, `memory_safety_mitigation`, `modular_update_channel`, `security_patch_lifecycle`.
3. **Mandatory Architecture Pattern Application:**
   - `predict_before_measure`: State falsifiable predictions for each hypothesis *before* running diagnostics or inspecting state.
   - `separate_boot_from_runtime`: Treat verified boot (GREEN/YELLOW/ORANGE/RED) and Knox warranty bit (0x0) as boot-time facts; evaluate post-boot runtime root, LKMs, and service.d hooks independently.
   - `separate_phone_from_carrier`: Never treat local settings or netpolicy as the upstream carrier quota of record.
   - `one_change_with_undo`: Any mutation or treatment must alter only a single variable, carry before/after measurements, provide a verified written undo path, and require owner approval.
   - `capture_the_ring`: Dump rotating system rings (`dumpsys usb`, `tethering`, `telephony.registry`, `isub`) immediately into full disk files before inspecting.
   - `least_privilege_process_confinement`: Honor UID isolation, SELinux domains, and authorization boundaries; batch root operations.
   - `verified_boot_with_explicit_state` & `attested_key_security_level`: Validate attestation claims (StrongBox/TEE vs Software) rather than assuming hardware backing.
4. **Failure Mode Cross-Reference:**
   Cross-reference observed symptoms with canonical failure modes (e.g. `allowance_exhausted`, `self_inflicted_hook_fault`, `measurement_artifact`, `sim_mapping_confusion`, `usb_function_flap`, `upstream_session_loss`, `forwarding_block`, `runaway_diagnostic_burn`, `restart_cascade`, `rollback_policy_gap`, `verified_boot_state_misread`, `attestation_replay_or_misvalidation`).
5. **Evidence Labeling Protocol:**
   Every reported finding, measurement, and statement must carry one of four strict evidence labels:
   - `[MEASURED]`: Directly observed on this handset with saved raw capture file and timestamp.
   - `[SOURCE]`: Stated in official AOSP, 3GPP, or RFC documentation.
   - `[INFERRED]`: Reasoned deduction based on measurements.
   - `[UNTESTED]`: Hypothesized or believed, but not yet verified.
6. **Standard Investigation Loop:**
   ```
   COMPLAINT / GOAL: Exact objective and context
   DOMAIN & ORGANS: Canonical Semantic Compiler domain + components mapped
   SYSTEM PATTERNS: Active architecture patterns enforced
   HYPOTHESES: Each with falsifiable predictions written BEFORE measurement
   MEASUREMENTS: Script/capture, evidence tier, raw file, sha256, result, evidence label
   ELIMINATED / CONFIRMED: Ruling out hypotheses with data
   TREATMENT PROPOSED: Single variable, written undo, zero cellular cost, owner approval
   ```

---

## 4. Key Repositories & Workspace Map

| Repository / Worktree | Location | Upstream Remote | Status / Purpose |
|---|---|---|---|
| **DeepSeek + Local SWE Harness** | `/data/data/com.termux/files/home/deepseek-harness` | Local / Origin | Dual-engine SWE harness (`dsh`), closed-loop optimizer, and semantic bridge |
| **Semantic Compiler Kernel (Host)** | `/data/data/com.termux/files/home/semantic_compiler_kernel` | `https://github.com/Shaximus/semantic_compiler_kernel` | Active working tree with 01–07 patches applied |
| **Semantic Compiler Kernel (Kali Review)** | `/root/imports/semantic_compiler_kernel_v3_review` | `https://github.com/Shaximus/semantic_compiler_kernel` | Staged review tree |
| **Forensics Lab** | `/data/data/com.termux/files/home/forensics-lab` | `https://github.com/Shaximus/forensics-lab.git` | System forensics, network audits, Knox telemetry |
| **Nexus Relay** | `/data/data/com.termux/files/home/nexus-relay` | Cloudflare Workers / Durable Objects | Hardened multi-tenant relay core |
| **Downloads & Ingestion** | `/sdcard/Download/` | N/A | Inbound patches, review reports (`REVIEW_REPORT-1.md`), zips |
| **Operator Staging** | `/storage/emulated/0/Alarms/agy-file-staging/` | N/A | Exported reports, audit bundles, deliverable archives |

---

## 5. Semantic Compiler V3.0.0 Patch Set Reference

- **`00-ALL-IN-ONE.patch`**: Comprehensive patch combining 01 through 07.
- **`01-buildcraft-resolver.patch`**: Structural resolver, item/slot collisions, whole-word matching.
- **`02-isomorphism-organ-detector.patch`**: Whole-token department presence matching, negation windows.
- **`03-medical-ontology-and-decompression.patch`**: Medical ontology alignment, whole-word domain router.
- **`04-packaging-and-readme.patch`**: Wheel packaging fixes, pyproject template inclusion.
- **`05-frozen-dirs-need-waiver.patch`**: `core/pipeline.py` claim_type fix, `registry/cosmological_constants.py` consistency checks.
- **`06-deep-system-domains.patch`**: Invariant templates (`mobile_security`, `networking`, `trust_chain`), `docs/DEEP_SYSTEM_INVARIANTS.md`.
- **`07-kestrel-integration.patch`**: `compat.py` pipeline wrapper, CI workflow (`.github/workflows/ci.yml`), Kestrel lab regressions.

---

## 6. Quick Verification Commands

```bash
# Verify Git identity
git config --get user.name
git config --get user.email

# Verify GitHub CLI status
gh auth status

# Verify test suite in semantic compiler (run inside Kali PRoot or with PYTHONPATH=.)
cd /data/data/com.termux/files/home/semantic_compiler_kernel
PYTHONPATH=. pytest -q

# Verify test suite in DeepSeek SWE harness
cd /data/data/com.termux/files/home/deepseek-harness
python3 -m unittest discover -s tests -q
```
