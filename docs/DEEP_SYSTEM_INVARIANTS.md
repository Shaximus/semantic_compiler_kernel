# Deep-system invariants: Android security, networking, and trust chains

Added 2026-11-06. This is a research-derived architecture map, not a claim that every Android device implements every optional control.

## Domain map

| Domain | Template | Coverage |
|---|---|---|
| `mobile_security` | `expansion/templates/mobile_security.yaml` | Android Verified Boot, rollback and partition integrity, app signing and sandboxing, SELinux, permissions/IPC, FBE, KeyMint/TEE/StrongBox, authentication, attestation, optional pKVM/MTE, update channels, and v1.2 userspace rootfs / path-translation / renamed-loader / SELinux-exec-workaround surfaces (observation tag only; not kernel root) |
| `networking` | `expansion/templates/networking.yaml` | Endpoint principle, routing, RPKI resource authorization, DNSSEC validation |
| `trust_chain` | `expansion/templates/trust_chain.yaml` | Shared anchor, delegation, freshness, verifier, failure semantics, rollover, and scope pattern |

## Provenance rules

- Every invariant in the templates ends with one or more source tags.
- Tags map to the primary public document in the table below. This is page/document-level provenance, not paragraph-level proof.
- Failure modes and architecture patterns are model mappings derived from the invariants. They are not quotations from Android or IETF documentation.
- A source describing a capability does not prove that every OEM, SoC, Android release, or device enables it.
- A missing source statement means "not established by the reviewed material", not "the property is absent".

## Sources

| Tag | Source | URL |
|---|---|---|
| `AOSP-VB` | Android Open Source Project, Verified Boot | https://source.android.com/docs/security/features/verifiedboot and https://source.android.com/docs/security/features/verifiedboot/verified-boot |
| `AOSP-APP` | AOSP, Application Sandbox and App Signing | https://source.android.com/docs/security/features and https://source.android.com/docs/security/overview/app-security |
| `AOSP-SEC` | AOSP, Security overview and kernel security | https://source.android.com/docs/security/overview and https://source.android.com/docs/security/overview/kernel-security |
| `AOSP-SELINUX` | AOSP, Security-Enhanced Linux in Android | https://source.android.com/docs/security/features/selinux |
| `AOSP-FBE` | AOSP, File-based encryption | https://source.android.com/docs/security/features/encryption/file-based |
| `AOSP-KEYMINT` | AOSP, Hardware-backed Keystore | https://source.android.com/docs/security/features/keystore |
| `AOSP-ATTEST` | AOSP, Key and ID attestation | https://source.android.com/docs/security/features/keystore/attestation |
| `AOSP-AUTH` | AOSP, Gatekeeper and Weaver authentication | https://source.android.com/docs/security/features/authentication/gatekeeper and https://source.android.com/docs/security/features/authentication/weaver and https://source.android.com/docs/security/features/authentication/rate-limiting |
| `AOSP-AVF` | AOSP, Android Virtualization Framework security | https://source.android.com/docs/core/virtualization/security |
| `AOSP-MTE` | AOSP, Arm Memory Tagging Extension configuration | https://source.android.com/docs/security/test/memory-safety/mte-configuration |
| `AOSP-MAINLINE` | AOSP, Mainline modular system updates | https://source.android.com/docs/core/ota/modular-system |
| `RFC1958` | RFC 1958, Architectural Principles of the Internet | https://www.rfc-editor.org/rfc/rfc1958 |
| `RFC4033` | RFC 4033, DNS Security Introduction and Requirements | https://datatracker.ietf.org/doc/html/rfc4033 |
| `RFC6480` | RFC 6480, An Infrastructure to Support Secure Internet Routing | https://datatracker.ietf.org/doc/html/rfc6480 |
| `UCSB-176C` | UCSB CS176C, The Four Invariants | https://sites.cs.ucsb.edu/~arpitgupta/cs176c/spring26/assets/slides/week01_lecture02_four_invariants.html |
| `KNOX-WP` | Samsung Knox security white paper, revision 1 | https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/assets/Knox-security-white-paper-r1.pdf |
| `KW-2016` | Kanonov and Wool, Secure Containers in Android: the Samsung KNOX Case Study | https://arxiv.org/abs/1605.08567 |
| `OBS-KIMICLAW-1.0.4` | Static offline study of package `com.moonshot.kimiclaw` 1.0.4 (versionCode 1007), written up in `docs/KIMICLAW_USERSACE_ROOTFS_EVIDENCE.md`. Artifact provenance is a third-party APKPure mirror (XAPK sha256 `b7a97c56de16820a50eb03ab48b167275396d3267a77bef63316ad666a9ca44b`), not a vendor CDN. Text excerpts only; the APK is not in this repo. Mechanism class is Termux/PRoot userspace path translation. | https://apkpure.com/kimi-claw/com.moonshot.kimiclaw and https://github.com/termux/proot |

## Android precision corrections

1. **Preserve Verified Boot state semantics.** GREEN is OEM-root verified and locked; YELLOW is verified against a user-configured root; ORANGE is unlocked and unverified; RED indicates verification failure. A policy must not treat these states as interchangeable.
2. **Do not universalize Samsung Knox behavior.** The Knox warranty bit, device-specific fused state, Knox container behavior, and any key-gating consequences are OEM/product-specific. They are not generic Android components.
3. **Do not universalize a kernel runtime monitor.** The cited 2016 Knox study describes a particular implementation and historical threat model. It is not proof that current AOSP devices all have a higher-privilege monitor.
4. **Do not claim every verification failure has one consequence.** Verified Boot distinguishes boot-time failures from runtime dm-verity failures and defines recovery behavior. Device state and implementation policy matter.
5. **Do not assume every Keystore key is hardware-backed.** Attestation distinguishes Software, TrustedEnvironment, and StrongBox security levels. A relying party must validate the challenge, certificate chain, boot state, and relevant authorization fields.
6. **Do not overstate lock-screen throttling.** Gatekeeper exposes timeout-based throttling; Weaver can supply hardware-backed rate limiting where implemented. "Exponential backoff" is not a universal Android invariant.
7. **Do not confuse APK signing with identity proof.** Signing binds package/update lineage to a key; it does not mean Android centrally validates the developer's legal identity.
8. **Do not assume optional mitigations are active.** pKVM, StrongBox, MTE, and OEM-specific capabilities vary by hardware, Android release, and build configuration.
9. **Do not collapse storage classes.** File-based encryption distinguishes Device Encrypted and Credential Encrypted storage; Direct Boot changes which data is available before user unlock.
10. **Do not conflate update channels.** Mainline updates selected modules; OEM firmware, kernel, vendor, and full-platform patches remain separate coverage questions.
11. **Do not treat a userspace rootfs as kernel root.** PRoot/Termux-style path translation, bootstrap ZIP loaders, renamed native loaders, and SELinux exec workarounds for binaries under an app's private data stay inside the app UID and the device SELinux policy. In the KimiClaw 1.0.4 static study, owner label "P root bypass" maps to PRoot plus SELinux exec bypass, and "peer bypass" maps to PeerCred (local-socket peer credentials), not to one `.so` filename and not to UID 0. `libruntime-init.so` was hash-identical to the PRoot loader; identity checks use content hashes. The studied XAPK came from an APKPure mirror and is not redistributed here.

## Deliberate scope limits

- The model does not claim a single Android security posture for all devices. Device launch version, current release, OEM policy, SoC capabilities, bootloader state, patch level, and runtime configuration must be supplied to assess a concrete handset.
- Cellular/baseband security, SIM/eSIM lifecycle, Bluetooth/Wi-Fi protocol attack surfaces, biometric sensor/TEE specifics, exploit-chain telemetry, Verified Boot implementation details for individual OEMs, and the full Android Compatibility Definition Document remain follow-up research areas.
- The Knox white paper and 2016 Knox study are not used to generalize proprietary Knox mechanisms to AOSP.
- This document is a technical synthesis, not a vendor security certification or domain-expert sign-off.
