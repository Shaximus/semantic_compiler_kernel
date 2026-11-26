#!/usr/bin/env python3
"""Latency, RSS, and payload-size baseline for the Semantic Compiler.

Measures import, cold/warm compile, and first decompress (median and p95),
peak RSS via /proc/self/status VmHWM, and summary_v1 vs to_dict() JSON sizes.

Default inputs are tests/fixtures/kernel_mobile_prompts/ (the six Kernel Mobile
characterization prompts). JSON is written to stdout, or to --output.

This script is read-only against the compiler. It does not mutate the repo.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = REPO_ROOT / "tests" / "fixtures" / "kernel_mobile_prompts"


def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return float("nan")
    ys = sorted(xs)
    if len(ys) == 1:
        return ys[0]
    k = (len(ys) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(ys) - 1)
    frac = k - lo
    return ys[lo] * (1.0 - frac) + ys[hi] * frac


def summarize_ms(samples_s: list[float]) -> dict:
    if not samples_s:
        return {"n": 0}
    return {
        "n": len(samples_s),
        "unit": "ms",
        "min": min(samples_s) * 1000.0,
        "median": statistics.median(samples_s) * 1000.0,
        "p95": percentile(samples_s, 95) * 1000.0,
        "mean": statistics.fmean(samples_s) * 1000.0,
        "max": max(samples_s) * 1000.0,
    }


def summarize_kib(samples: list[int]) -> dict:
    if not samples:
        return {"n": 0}
    vals = [float(x) for x in samples]
    return {
        "n": len(vals),
        "unit": "KiB",
        "min": min(vals),
        "median": statistics.median(vals),
        "p95": percentile(vals, 95),
        "mean": statistics.fmean(vals),
        "max": max(vals),
    }


def proc_vmhwm_kib() -> int | None:
    path = Path("/proc/self/status")
    if not path.is_file():
        return None
    for line in path.read_text().splitlines():
        if line.startswith("VmHWM:"):
            parts = line.split()
            return int(parts[1])
    return None


def load_inputs(input_dir: Path) -> list[dict]:
    items = []
    for path in sorted(input_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        items.append(
            {
                "id": path.stem,
                "path": str(path),
                "text": text,
                "chars": len(text),
            }
        )
    if not items:
        raise SystemExit(f"no *.txt inputs in {input_dir}")
    return items


def run_isolated(code: str, args: list[str] | None = None, env: dict | None = None) -> dict:
    command = [sys.executable, "-c", code, *(args or [])]
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"isolated run failed rc={proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return json.loads(proc.stdout.strip().splitlines()[-1])


IMPORT_CORE = r"""
import json, time
from pathlib import Path

def vmhwm():
    p = Path("/proc/self/status")
    if p.is_file():
        for line in p.read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return None

t0 = time.perf_counter()
import semantic_compiler
t1 = time.perf_counter()
print(json.dumps({
    "import_s": t1 - t0,
    "version": getattr(semantic_compiler, "__version__", None),
    "vmhwm_kib": vmhwm(),
}))
"""

IMPORT_EXPANSION = r"""
import json, time
from pathlib import Path

def vmhwm():
    p = Path("/proc/self/status")
    if p.is_file():
        for line in p.read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return None

t0 = time.perf_counter()
import semantic_compiler
t1 = time.perf_counter()
import semantic_compiler.expansion
t2 = time.perf_counter()
print(json.dumps({
    "import_core_s": t1 - t0,
    "import_expansion_s": t2 - t1,
    "import_total_s": t2 - t0,
    "vmhwm_kib": vmhwm(),
}))
"""

COLD_COMPILE = r"""
import json, sys, time
from pathlib import Path

def vmhwm():
    p = Path("/proc/self/status")
    if p.is_file():
        for line in p.read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return None

text = sys.argv[1]
t0 = time.perf_counter()
from semantic_compiler import compile_semantic_packet
t1 = time.perf_counter()
pkt = compile_semantic_packet(text)
t2 = time.perf_counter()
full = json.dumps(pkt.to_dict(), default=str, separators=(",", ":"))
summary = None
summary_bytes = None
t3 = t2
try:
    from semantic_compiler.api import summary_v1
    summary = summary_v1(pkt)
    t3 = time.perf_counter()
    summary_bytes = len(json.dumps(summary, default=str, separators=(",", ":")).encode())
except ImportError:
    pass
print(json.dumps({
    "import_s": t1 - t0,
    "compile_s": t2 - t1,
    "summary_s": (t3 - t2) if summary_bytes is not None else None,
    "decision": pkt.decision.name if pkt.decision else None,
    "to_dict_bytes": len(full.encode()),
    "summary_v1_bytes": summary_bytes,
    "vmhwm_kib": vmhwm(),
}))
"""

COLD_TEMPLATES = r"""
import json, time
from pathlib import Path

def vmhwm():
    p = Path("/proc/self/status")
    if p.is_file():
        for line in p.read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return None

from semantic_compiler.expansion.registry.loader import _MEM_CACHE, load_templates
_MEM_CACHE.clear()
t0 = time.perf_counter()
templates = load_templates()
t1 = time.perf_counter()
print(json.dumps({
    "load_templates_s": t1 - t0,
    "n_templates": len(templates),
    "vmhwm_kib": vmhwm(),
}))
"""

COLD_DECOMPRESS = r"""
import json, sys, time
from pathlib import Path

def vmhwm():
    p = Path("/proc/self/status")
    if p.is_file():
        for line in p.read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return None

text = sys.argv[1]
from semantic_compiler import compile_semantic_packet
import semantic_compiler.expansion as expansion
pkt = compile_semantic_packet(text)
t0 = time.perf_counter()
model = expansion.decompress(pkt)
t1 = time.perf_counter()
print(json.dumps({
    "decompress_s": t1 - t0,
    "domain": model.get("domain"),
    "model_bytes": len(json.dumps(model, default=str, separators=(",", ":")).encode()),
    "vmhwm_kib": vmhwm(),
}))
"""


def machine_spec() -> dict:
    spec = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": sys.platform,
    }
    try:
        uname = os.uname()
        spec["uname"] = {
            "sysname": uname.sysname,
            "nodename": uname.nodename,
            "release": uname.release,
            "machine": uname.machine,
        }
    except AttributeError:
        pass
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        model = None
        mhz = None
        cpus = 0
        for line in cpuinfo.read_text().splitlines():
            if line.startswith("model name") and model is None:
                model = line.split(":", 1)[1].strip()
            elif line.startswith("cpu MHz") and mhz is None:
                mhz = line.split(":", 1)[1].strip()
            elif line.startswith("processor"):
                cpus += 1
        spec["cpu"] = {"model": model, "mhz": mhz, "logical_cpus": cpus}
    meminfo = Path("/proc/meminfo")
    if meminfo.is_file():
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemTotal:"):
                spec["mem_total_kib"] = int(line.split()[1])
                break
    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--import-n", type=int, default=15)
    parser.add_argument("--cold-n", type=int, default=15)
    parser.add_argument("--warm-n", type=int, default=50)
    parser.add_argument("--warmup-n", type=int, default=5)
    parser.add_argument("--decompress-n", type=int, default=8)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    inputs = load_inputs(args.input_dir)
    report: dict = {
        "machine": machine_spec(),
        "input_dir": str(args.input_dir),
        "counts": {
            "import_n": args.import_n,
            "cold_n": args.cold_n,
            "warm_n": args.warm_n,
            "warmup_n": args.warmup_n,
            "decompress_n": args.decompress_n,
        },
    }

    core_s, core_rss = [], []
    for _ in range(args.import_n):
        row = run_isolated(IMPORT_CORE)
        core_s.append(row["import_s"])
        if row.get("vmhwm_kib") is not None:
            core_rss.append(row["vmhwm_kib"])
        report["compiler_version"] = row.get("version")
    report["import_core"] = {**summarize_ms(core_s), "vmhwm_kib": summarize_kib(core_rss)}

    exp_core, exp_only, exp_total, exp_rss = [], [], [], []
    for _ in range(args.import_n):
        row = run_isolated(IMPORT_EXPANSION)
        exp_core.append(row["import_core_s"])
        exp_only.append(row["import_expansion_s"])
        exp_total.append(row["import_total_s"])
        if row.get("vmhwm_kib") is not None:
            exp_rss.append(row["vmhwm_kib"])
    report["import_expansion"] = {
        "core": summarize_ms(exp_core),
        "expansion_only": summarize_ms(exp_only),
        "total": summarize_ms(exp_total),
        "vmhwm_kib": summarize_kib(exp_rss),
    }

    # Warm compile in this process after the isolated import measurements.
    from semantic_compiler import compile_semantic_packet

    has_api = False
    try:
        from semantic_compiler.api import summary_v1 as summary_fn
        has_api = True
    except ImportError:
        summary_fn = None  # type: ignore[assignment]
    report["has_summary_v1"] = has_api

    report["inputs"] = {}
    for item in inputs:
        cold_rows = [run_isolated(COLD_COMPILE, [item["text"]]) for _ in range(args.cold_n)]
        for _ in range(args.warmup_n):
            compile_semantic_packet(item["text"])
        warm = []
        last_pkt = None
        for _ in range(args.warm_n):
            t0 = time.perf_counter()
            last_pkt = compile_semantic_packet(item["text"])
            warm.append(time.perf_counter() - t0)
        to_dict_bytes = len(
            json.dumps(last_pkt.to_dict(), default=str, separators=(",", ":")).encode()
        )
        summary_bytes = None
        if has_api and last_pkt is not None:
            summary_bytes = len(
                json.dumps(
                    summary_fn(last_pkt), default=str, separators=(",", ":")
                ).encode()
            )
        report["inputs"][item["id"]] = {
            "chars": item["chars"],
            "decision": last_pkt.decision.name if last_pkt and last_pkt.decision else None,
            "cold_import": summarize_ms([r["import_s"] for r in cold_rows]),
            "cold_compile": summarize_ms([r["compile_s"] for r in cold_rows]),
            "warm_compile": summarize_ms(warm),
            "to_dict_bytes": to_dict_bytes,
            "summary_v1_bytes": summary_bytes,
            "vmhwm_kib": summarize_kib(
                [r["vmhwm_kib"] for r in cold_rows if r.get("vmhwm_kib") is not None]
            ),
        }

    # First decompress: fresh TMPDIR so the sidecar is not reused across trials.
    report["first_decompress"] = {}
    decomp_ids = [item["id"] for item in inputs]
    # Keep this light: first-decompress is dominated by template load, so two
    # representative inputs (short compile path + a decompress-friendly domain).
    prefer = [i for i in decomp_ids if i in {"03_kv_cache", "06_long_multi_domain"}]
    chosen = prefer or decomp_ids[:2]
    for item in inputs:
        if item["id"] not in chosen:
            continue
        rows = []
        for _ in range(args.decompress_n):
            with tempfile.TemporaryDirectory(prefix="sck-bench-") as tmp:
                env = {"TMPDIR": tmp, "TMP": tmp, "TEMP": tmp}
                # Also isolate the sidecar from a user-set cache dir.
                env["SEMANTIC_COMPILER_CACHE_DIR"] = tmp
                rows.append(run_isolated(COLD_DECOMPRESS, [item["text"]], env=env))
        report["first_decompress"][item["id"]] = {
            "decompress": summarize_ms([r["decompress_s"] for r in rows]),
            "domain": rows[-1].get("domain"),
            "model_bytes": rows[-1].get("model_bytes"),
            "vmhwm_kib": summarize_kib(
                [r["vmhwm_kib"] for r in rows if r.get("vmhwm_kib") is not None]
            ),
        }

    # First load_templates() in a fresh cache dir (compile now warms templates,
    # so decompress-after-compile is not a template-cold measurement).
    tmpl_rows = []
    for _ in range(args.decompress_n):
        with tempfile.TemporaryDirectory(prefix="sck-tmpl-") as tmp:
            env = {"TMPDIR": tmp, "TMP": tmp, "TEMP": tmp, "SEMANTIC_COMPILER_CACHE_DIR": tmp}
            tmpl_rows.append(run_isolated(COLD_TEMPLATES, env=env))
    report["first_load_templates"] = {
        "load_templates": summarize_ms([r["load_templates_s"] for r in tmpl_rows]),
        "n_templates": tmpl_rows[-1].get("n_templates"),
        "vmhwm_kib": summarize_kib(
            [r["vmhwm_kib"] for r in tmpl_rows if r.get("vmhwm_kib") is not None]
        ),
    }

    report["this_process_vmhwm_kib"] = proc_vmhwm_kib()
    report["this_process_ru_maxrss_kib"] = int(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    )

    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
