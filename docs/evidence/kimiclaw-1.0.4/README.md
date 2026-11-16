# KimiClaw 1.0.4 static text excerpts

Text only. This folder does not contain an APK, XAPK, or native library.

These files support `docs/KIMICLAW_USERSACE_ROOTFS_EVIDENCE.md`. Paths in that note (`evidence/native/…`, `acquisition-logs/…`) name the original study tree. The copies here are:

- `SO_INVENTORY.txt` — arm64-v8a library sizes and sha256 (no binaries)
- `HASHES.txt` — base split and XAPK sha256
- `disasm_libcompat_execve.txt` — bounded `libcompat-v2.so` `execve` listing
- `disasm_proot_entry.txt` — bounded `bin/proot` entry listing
- `APKPURE_ACQUISITION.md` — third-party mirror acquisition log

`disasm_bootstrap_getZip.txt` is cited in the evidence note and was not in this text bundle. Provenance is an APKPure mirror of `com.moonshot.kimiclaw` 1.0.4, XAPK sha256 `b7a97c56de16820a50eb03ab48b167275396d3267a77bef63316ad666a9ca44b`.
