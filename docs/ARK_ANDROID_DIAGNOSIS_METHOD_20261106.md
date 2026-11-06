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

## 2. The loop

This follows the kernel's predict-then-measure discipline. For each hypothesis, write the prediction first. Then capture the ring. Then label the result. Do not browse the phone hoping a pattern will appear.

(The complete method body — organs table, vitals, failure patterns with predict/falsify, worked case 2026-11-06 timeline, and report format — is the authoritative text from the project folder artifact ARK_ANDROID_DIAGNOSIS_METHOD_20261106.md. Companion expansion templates on this branch: `expansion/templates/android_connectivity.yaml` and `expansion/templates/bluetooth.yaml`.)

## 8. How to use the Semantic Compiler here

- **Use it as a checklist and vocabulary.** `android_connectivity.yaml` gives you the organs, invariants and failure patterns.
- **Do not cite its output as a diagnosis.** Per the kernel's own review report, `decompress()` copies components from the template whatever the input says, and `reconstruct_missing()` compares the template with itself. Two different inputs in a domain give identical models. A label such as `pathogen` or `autoimmune` is a filing category, and the evidence must come from the phone.
- **Enter evidence honestly.** Use the kernel's tiers: `PRIMARY_RECORD` for raw dumps and carrier texts, `AI_GENERATED_ASSESSMENT` for agent reports including this file, and `MARKED_SPECULATION` for hypotheses.
- **Record what you looked for and did not find, with its scope.** Say "not found in these files", never "does not exist".

## 9. Report format

```
COMPLAINT: owner's words, time
TRIAGE: what is getting worse, what was stopped
ORGAN: where the symptom lives
HYPOTHESES: each with its prediction, written before testing
TESTS: command, tier, raw file, sha256, result, label
ELIMINATED / STILL OPEN
TREATMENT PROPOSED: one variable, undo, cost, needs owner approval
UNKNOWN: and what would change this conclusion
```
