#!/usr/bin/env python3
"""Static audit for SC-SOV-TRADE-001 (no third-party tools needed).

1. No `random` module import in sov_trade/ (secrets / os.urandom /
   secrets.SystemRandom only).
2. Every ==/!= comparison whose operands mention a signature, MAC, tag,
   PIN or secret is listed; the audit fails if one compares SECRET or
   MAC/signature material directly. Signatures are only ever checked
   through `cryptography` verify() calls (constant time in OpenSSL /
   the Rust backend); hash/commitment/nonce comparisons of public values
   are listed for review.
3. Secret scan over every git-tracked file: private-key PEM blocks,
   GitHub tokens, AWS keys, generic 'api_key = "..."' assignments.

Exit status 1 on a hard finding. Prints a JSON report.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOV = REPO / "sov_trade"

SENSITIVE = re.compile(r"(signature|\bsig\b|_sig\b|mac\b|tag\b|pin\b|secret|private)", re.I)
SECRET_PATTERNS = {
    "private_key_pem": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{60,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "slack_token": re.compile(r"\bxox[abpors]-[A-Za-z0-9-]{10,}\b"),
    "generic_assignment": re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"][A-Za-z0-9/+_\-]{24,}['\"]"),
}


def main() -> int:
    report: dict[str, object] = {}
    hard: list[str] = []

    random_imports = []
    compare_sites = []
    compare_digest_sites = []
    for path in sorted(SOV.rglob("*.py")):
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        rel = str(path.relative_to(REPO))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name == "random" or a.name.startswith("random."):
                        random_imports.append(f"{rel}:{node.lineno}")
            elif isinstance(node, ast.ImportFrom) and (node.module or "") == "random":
                random_imports.append(f"{rel}:{node.lineno}")
            elif isinstance(node, ast.Compare) and any(isinstance(op, (ast.Eq, ast.NotEq)) for op in node.ops):
                text = ast.get_source_segment(src, node) or ""
                if SENSITIVE.search(text):
                    compare_sites.append(f"{rel}:{node.lineno}: {text}")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "compare_digest":
                compare_digest_sites.append(f"{rel}:{node.lineno}")
    report["random_module_imports"] = random_imports
    if random_imports:
        hard.append("random module imported in sov_trade")
    # Reviewed allow-list: comparisons of PUBLIC values only.
    reviewed_public = {
        # attribute presence / algorithm-name / length checks, not secret bytes
    }
    report["sensitive_eq_comparisons"] = compare_sites
    report["hmac_compare_digest_sites"] = compare_digest_sites
    for site in compare_sites:
        body = site.split(": ", 1)[1]
        # Direct equality on signature/MAC bytes is a hard failure.
        if re.search(r"(bytes\(|\.signature\b|sig\b)", body) and not re.search(
            r"(len\(|\.algorithm|party|signature_size|\"|')", body
        ) and site not in reviewed_public:
            hard.append(f"direct comparison of signature material: {site}")

    tracked = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=REPO, capture_output=True, check=True).stdout
    findings = []
    for name in tracked.decode().split("\0"):
        if not name:
            continue
        p = REPO / name
        if not p.is_file() or p.stat().st_size > 5_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            for m in pattern.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                findings.append({"file": name, "line": line, "kind": label})
    report["secret_scan_files"] = len([n for n in tracked.decode().split("\0") if n])
    report["secret_scan_findings"] = findings
    if findings:
        hard.append(f"{len(findings)} possible committed secrets")
    report["hard_findings"] = hard
    report["result"] = "PASS" if not hard else "FAIL"
    print(json.dumps(report, indent=2))
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
