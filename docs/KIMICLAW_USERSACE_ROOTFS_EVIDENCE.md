# KimiClaw mechanism findings (static, offline)

**Updated:** 2026-11-06 ~23:30 ADT (America/Halifax)  
**Owner auth:** t456u / t457u / t460u (CoS relay)  
**Constraint compliance:** no APK/native payload execution; no redistribute; box scratch only.

## Artifact provenance

| Field | Value |
|---|---|
| Package | `com.moonshot.kimiclaw` |
| Version | 1.0.4 (versionCode 1007) |
| Acquisition | APKPure public HTML CDN (`d.apkpure.com` → `data.winudf.com`) |
| File | `apks/KimiClaw_1.0.4_APKPure.xapk` |
| XAPK SHA-256 | `b7a97c56de16820a50eb03ab48b167275396d3267a77bef63316ad666a9ca44b` (matches APKPure listing) |
| Base split SHA-256 | `a23a20629a0ef64293bf48f26cb134e1cdc5776b92299776839e8bd3b5eec608` |
| arm64 config SHA-256 | `ef674400f436fab4b9bd13ebc82974c607d05fd52578e0d8c93e41cb5a2ba149` |
| Label | **Third-party mirror — not vendor-official CDN.** Package name + version match Xiaomi store listing (1.0.4 / ~193MB). Does **not** match preserved Ark base hash `f4a36f16…` (different packaging: split XAPK vs single base). |
| Official direct APK | Still none on kimi.com (QR/login / store / in-app). |
| Signing note | Parsed APK Sig Block candidate cert presents as Google Inc / Android (likely Play App Signing lineage or parse ambiguity). **Moonshot upload-key identity not independently confirmed this stream.** |

Acquisition logs: `acquisition-logs/APKPURE_ACQUISITION.md`.

## Spelling / label resolution (evidence-indexed)

Owner labels "P root bypass.so" (t456u) and "peer bypass" (t457u) are **not** filenames in the APK.

| Owner label | Best-supported mapping | Evidence |
|---|---|---|
| "P root bypass.so" | **PRoot** userspace syscall translator (`bin/proot` inside Termux bootstrap) + SELinux **exec bypass** script markers — **not** a top-level `libproot.so` / `*bypass*.so` | Bootstrap ZIP lists `bin/proot`, `libexec/proot/loader{,32}`; DEX strings `# SELinux exec bypass`, `selinux-exec-bypass.sh`, `__selinux_exec_bypass_{begin,end}__` |
| "peer bypass" | **Do not conflate** with PeerCred (`Lcom/termux/shared/net/socket/local/PeerCred;`, `getPeerCredNative`) — local-socket peer credential plumbing. No `*peer*bypass*.so` | DEX string inventory |
| Obfuscated `.so` remapping | (1) `libruntime-init.so` **byte-identical** to `libexec/proot/loader` (sha256 `44ef39c1…`); (2) `libcompat-v2.so` exports remapped libc path ops via `dlsym`; (3) bootstrap embeds full Termux usr tree as ZIP blob | Hash match + ELF exports |

**Verdict class:** capability observed = userspace rootfs / path translation for OpenClaw-on-Android. **Not** evidence of Android kernel root exploit or UID privilege escalation.

## Native inventory (arm64-v8a only)

15 libraries in `config.arm64_v8a.apk`. Mechanism-relevant:

| Library | Size | Role (observed) |
|---|---:|---|
| `libtermux-bootstrap.so` | 47 188 920 | ELF64 DYN AArch64; exports `blob`, `blob_size`, `Java_com_termux_app_TermuxInstaller_getZip` — embeds Termux bootstrap ZIP |
| `libtermux.so` | 13 736 | JNI_OnLoad; PTY/fork helpers for Termux session |
| `libruntime-init.so` | 18 136 | **Identical** to `libexec/proot/loader` (PRoot loader remapped into `lib/`) |
| `libcompat-v2.so` | 9 400 | Exports `execve`/`execv`/`stat`/`access`/`chmod`/…; imports `dlsym` — path-translation shim |
| `libEncryptorP.so` | 83 928 | Separate JNI encryptor (name ≠ PRoot); not the bypass mechanism |
| `libflipped.so` | 7 384 | ByteDance Mira flipped compat (Hidden API related; DEX refs `FlippedV2Impl`) |
| Others | — | mmkv, rive, apminsight, volc_log, local-socket, c++_shared, backup-crypto, androidx path — not PRoot path |

Full hashes: `evidence/native/SO_INVENTORY.txt`.

## Source → loader → native call graph (static)

```
App DEX (classes*.dex)
  ├─ TermuxInstaller / onInstallBootstrap / install_bootstrap_*
  │     └─ System.loadLibrary("termux-bootstrap")
  │           └─ libtermux-bootstrap.so
  │                 └─ Java_com_termux_app_TermuxInstaller_getZip
  │                       └─ returns embedded ZIP blob (offset 0x520, ~47 185 835 B)
  │                             └─ extract → /data/data/com.moonshot.kimiclaw/files/usr
  │                                   ├─ bin/proot  (ELF64 DYN; ptrace/syscall/mmap/mprotect/mremap strings)
  │                                   ├─ libexec/proot/loader{,32}
  │                                   ├─ bin/proot-distro (+ debian rootfs scripts)
  │                                   ├─ bin/termux-chroot, bin/unshare, bin/ischroot
  │                                   └─ lib/libtermux-exec-*-ld-preload.so (path rewrite LD_PRELOAD family)
  ├─ Shell / OpenClaw launch paths (DEX strings)
  │     └─ `proot-distro login debian -- /bin/bash` / `exec proot-distro login debian -- /bin/bash`
  │           └─ OpenClaw under installed-rootfs/debian/root/.openclaw
  ├─ SELinux exec bypass markers (script fragments in DEX)
  │     └─ `# SELinux exec bypass` / `__selinux_exec_bypass_{begin,end}__` / `selinux-exec-bypass.sh`
  ├─ HiddenApiBypass / flipped (DEX) — reflection restriction bypass, not root
  └─ libcompat-v2.so (APK lib/)
        └─ exported execve @0xe78: resolves real libc symbol via dlsym, optional path rewrite, then `br x3`
              (bounded disasm: evidence/native/disasm_libcompat_execve.txt)

Also shipped: libruntime-init.so ≡ proot loader (same bytes as bootstrap libexec/proot/loader).
```

## PRoot vs privilege escalation vs "peer bypass" (no conflation)

| Concept | Present? | Meaning here |
|---|---|---|
| PRoot namespace/path translation | **Yes** | Userspace intercepts syscalls (ptrace/seccomp-style family per strings) to fake chroot / path map for a Linux userland **without** changing Android UID to 0 |
| Kernel privilege escalation / Magisk-style root | **Not observed** in static APK | No su binary claim as root exploit; no evidence of breaking UID/SELinux into other apps' private data as a rootkit |
| SELinux **exec** bypass | **Yes (script markers)** | Termux-family workaround for SELinux restrictions on executing from app data paths — **not** "disable SELinux globally" |
| PeerCred / peer certificates | **Yes (unrelated label)** | Local socket peer UID/cred checks and TLS peer certs — **not** a bypass library |
| Accessibility automation | Documented vendor capability | Separate threat surface (cross-app UI) — out of this remapping focus unless tied to loader |

## Bounded disassembly anchors

- `libcompat-v2.so` `execve` @ `0xe78`: prologue → lazy `dlsym` resolve → conditional path rewrite → `br x3` to real libc (`evidence/native/disasm_libcompat_execve.txt`)
- `bin/proot` entry @ `0x1372c`: PAC/BTI entry into main (`evidence/native/disasm_proot_entry.txt`)
- `libtermux-bootstrap.so` `Java_com_termux_app_TermuxInstaller_getZip` (`evidence/native/disasm_bootstrap_getZip.txt`)
- Host `objdump` cannot target AArch64; Capstone used. Full ptrace handler bodies in `proot` not exhaustively walked (quota bound) — string counts: ptrace=32, PTRACE=41, syscall=31, mprotect=2, mremap=1.

## Threat boundaries / tests (for domain expansion)

1. **Invariant:** Presence of PRoot/Termux bootstrap ≠ proof of Android root exploit.  
2. **Invariant:** `libruntime-init.so` may be a renamed PRoot loader — always hash-compare to known loader.  
3. **Invariant:** Path-translation shims (`libcompat-v2` / termux-exec LD_PRELOAD) stay inside app UID sandbox unless paired with a separate escalation.  
4. **Test:** Static APK must list whether `bin/proot` exists inside bootstrap blob before labeling "root bypass".  
5. **Test:** Distinguish DEX "bypass" hits (SELinux exec / HiddenApi / ads) via exact string match, not keyword alone.

## Limitations

- No runtime / emulator execution (per owner constraint).  
- Mirror provenance; Ark optional corroboration still offline.  
- AArch64 disassembly bounded; no full CFG of every ptrace case in proot.  
- Accessibility / network / credential surfaces not re-audited in this remapping pass.
