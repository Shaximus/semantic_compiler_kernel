# Android security domain review

**Review date:** 2026-11-06  
**Target:** \`expansion/templates/mobile_security.yaml\`  
**Result:** precision pass applied; expert certification not claimed.

## Changes made

- Split the generic boot root from bootloader state, verified boot, rollback protection, and verified-partition integrity.
- Added app signing identity, UID sandboxing, SELinux MAC, runtime permissions, and IPC authorization as separate controls.
- Added File-Based Encryption with Device Encrypted versus Credential Encrypted storage and Direct Boot implications.
- Added KeyMint/Keystore security levels, TEE/StrongBox distinction, user-authenticator throttling, and challenge-bound key attestation.
- Added optional protected VMs, MTE/memory-safety mitigations, Mainline modules, and separate patch-delivery channels.
- Removed generic claims that all Android devices have a Knox-style tamper fuse, automatic protected-storage wipe, or a higher-privilege kernel runtime monitor.
- Replaced blanket "exponential backoff" with timeout-based Gatekeeper throttling and optional Weaver support.
- Added tests for source-tag coverage, relationship integrity, medical-map separation, routing precedence, and false-positive vocabulary.

## Precision findings

| Previous modeling risk | Corrected treatment |
|---|---|
| Knox-specific fused/tamper behavior presented as Android-wide | Excluded from generic AOSP model; scope only to documented OEM implementations |
| Every Verified Boot failure modeled as immediate permanent boot stop | Separate boot-time and runtime verification/recovery behavior |
| Keystore keys assumed hardware-backed | Require attestation and inspect Software / TEE / StrongBox security level |
| Developer APK signature treated as centralized identity verification | Model signing as package/update lineage, not legal identity proof |
| Credential throttling described as universal exponential backoff | Model secure timeout throttling; Weaver is optional/device-dependent |
| pKVM and MTE treated as universal protections | Marked optional and configuration-dependent |
| Encryption represented as one undifferentiated store | Split DE and CE storage, with Direct Boot scope |
| OS update path represented as one channel | Separate Mainline modules from OEM/kernel/vendor patch lifecycle |

## Verification status

The source material supports the architectural capabilities and limitations listed in \`docs/DEEP_SYSTEM_INVARIANTS.md\`. It does not support a single universal Android security posture across all manufacturers and devices. A concrete device assessment still requires model/build fingerprint, Android release, bootloader and verified-boot state, security patch level, vendor patch level, KeyMint attestation, and enabled optional capabilities.

The local V3.0.0 review archive completed **350 pytest passes with 4 expected xfails** after package-path setup. This is a source-archive test result, not a GitHub Actions result and not proof that every handset implements every modeled capability.
