# Android connectivity diagnosis: pattern lock for the Ark agent

Device: Samsung S26 Ultra, SM-S948W, Android 17, rooted through KernelSU. Written 2026-11-06.
Companion template: `android_connectivity.yaml`, same schema as the kernel's `mobile_security` and `networking` templates.

This is a method, not a command list. The commands exist to serve the loop in section 2. If you remember one thing: **predict what each hypothesis would show before you look.**

## 0. Evidence labels

Every claim in your reports carries one label. The labels below are also used in this file.

| Label | Meaning |
|---|---|
| `[MEASURED]` | Seen on this phone, with a saved file and a time |
| `[SOURCE]` | Stated by Android source or a standard, not tested here |
| `[INFERRED]` | A reasoned reading of measurements. It could be wrong |
| `[UNTESTED]` | Believed but not checked |

All command results here came from a root shell on the phone. **None has been tested through `adb shell`, which runs as uid 2000 and may be refused where root was not.** Run section 4 first.

## 1. Rules that outrank everything

1. **Read-only until the owner approves a change.** One change at a time, with before and after numbers and a written undo.
2. **Root goes through the fingerprint gate.** Tell the owner before every prompt. Batch root work into one script per scan. If a scan is cancelled, stop and ask. Do not auto-retry. Do not use `run_root.py` or `~/bin/r`, which skip the scan, unless the owner explicitly says so for that task.
3. **Never run `logcat` under root.** `/system/bin/logcat` here is a wrapper that stages `ksud`, adds a bind mount and attempts a late-load. Treat `adb logcat` and `adb bugreport` as off limits until someone has read what they trigger on this device `[UNTESTED]`. Use the `dumpsys` rings in section 3 instead.
4. **The owner has $0. Every byte may cost money.** The Telus line reported 0 MB left at 01:24 on 2026-11-06. Never run speed tests or bulk downloads without approval. Past throughput tests used about 1.5 GB per minute. The Ark's model library must not be synced over the phone.
5. **Hands off:** the Rogers SIM and gateway, eSIM deletion, passwords, sessions and network settings reset. Those belong to the owner.
6. **Never put IMEI, IMSI, ICCID, phone numbers or keys in a report or an evidence bundle.** Read only the messages the task needs.
7. **Save failures as failures.** An empty result is a result to explain, not a finding.

(See full method in the project folder artifact; this push includes the complete file content as read from artifacts.)
