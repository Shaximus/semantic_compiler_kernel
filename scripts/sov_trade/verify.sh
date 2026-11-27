#!/usr/bin/env bash
# SC-SOV-TRADE-001 one-command verification (`make verify`).
#
# Builds a fresh venv from the hash-locked requirements, initialises a
# SoftHSM2 TEST token (random per-run TEST PINs, never written to logs),
# then runs: environment record, full pytest -rs -v with
# SOV_TRADE_REQUIRE_FUNCTIONAL=1, unittest, validate_catalog, fuzz pass,
# HSM evidence, OpenSSL cross-checks, mutation check, static checks and the
# dogfood regression diff against the merge-base with origin/main.
# Every log is hashed into SHA256SUMS. Each step's exit code is recorded in
# steps.tsv; the script exits non-zero if any step failed. Nothing is
# worked around: a failing step is reported as FAIL.
#
# Needs: python3 (>=3.10, venv), git, openssl (3.5+ for the ML-DSA
# cross-check), softhsm2, opensc (pkcs11-tool).
# Env: OUT (default ./verify-out), PYTHON (default python3),
#      SOV_TRADE_FUZZ_EXAMPLES (default 5000), SKIP_MUTATION=1,
#      SOV_TRADE_CORPUS_HARNESS=/path/to/decision_diff.py (optional; the
#      963-prompt corpus harness is not part of the repo).
set -uo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${OUT:-$REPO/verify-out}"
PY="${PYTHON:-python3}"
export SOV_TRADE_FUZZ_EXAMPLES="${SOV_TRADE_FUZZ_EXAMPLES:-5000}"
rm -rf "$OUT"; mkdir -p "$OUT/logs"
L="$OUT/logs"
STEPS="$OUT/steps.tsv"; : > "$STEPS"

step() {  # step <name> <command...>   (output -> logs/<name>.log)
  local name="$1"; shift
  local t0=$SECONDS
  echo "== $name"
  "$@" > "$L/$name.log" 2>&1
  local rc=$?
  printf '%s\t%s\t%ss\n' "$name" "$rc" "$((SECONDS - t0))" >> "$STEPS"
  if [ "$rc" -eq 0 ]; then echo "   PASS"; else echo "   FAIL (rc=$rc, see $L/$name.log)"; tail -n 15 "$L/$name.log"; fi
  return 0
}

info() {  # info <name> <command...>: recorded and hashed, reported as INFO (not a gate)
  local name="$1"; shift
  echo "== $name (report only)"
  "$@" > "$L/$name.log" 2>&1
  printf '%s\tINFO(rc=%s)\t-\n' "$name" "$?" >> "$STEPS"
  return 0
}

# --- importable as `semantic_compiler` (the repository root is the package)
PP="$OUT/pp"; mkdir -p "$PP"; ln -s "$REPO" "$PP/semantic_compiler"
export PYTHONPATH="$PP"

# --- fresh venv from the locks
VENV="$OUT/venv"
step venv bash -c "'$PY' -m venv '$VENV' && '$VENV/bin/python' -m pip install -q --upgrade pip \
  && '$VENV/bin/python' -m pip install -q --require-hashes -r '$REPO/requirements/sov-trade-ci.lock' \
  && '$VENV/bin/python' -m pip install -q --require-hashes -r '$REPO/requirements/sov-trade-static.lock'"
VPY="$VENV/bin/python"

# --- SoftHSM2 TEST token
HSM="$OUT/softhsm"; mkdir -p "$HSM/tokens"
printf 'directories.tokendir = %s\nobjectstore.backend = file\nlog.level = ERROR\n' "$HSM/tokens" > "$HSM/softhsm2.conf"
export SOFTHSM2_CONF="$HSM/softhsm2.conf"
SOV_TRADE_PKCS11_USER_PIN="$(openssl rand -hex 16)"; export SOV_TRADE_PKCS11_USER_PIN   # TEST PIN
SO_PIN="$(openssl rand -hex 16)"                                                       # TEST SO PIN
export SOV_TRADE_PKCS11_TOKEN_LABEL="sov-verify-test"
for m in /usr/lib/softhsm/libsofthsm2.so /usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so /usr/local/lib/softhsm/libsofthsm2.so; do
  if [ -f "$m" ]; then export SOV_TRADE_PKCS11_LIBRARY="$m"; break; fi
done
step softhsm_init softhsm2-util --init-token --free --label "$SOV_TRADE_PKCS11_TOKEN_LABEL" --pin "$SOV_TRADE_PKCS11_USER_PIN" --so-pin "$SO_PIN"
unset SO_PIN

# --- environment record
{
  echo "date_local: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "host_kind: ${SOV_VERIFY_HOST_KIND:-unspecified}"
  echo "uname: $(uname -a)"
  grep -E '^(PRETTY_NAME|VERSION_ID)=' /etc/os-release 2>/dev/null
  echo "repo: $REPO"
  echo "git_head: $(git -C "$REPO" rev-parse HEAD)"
  echo "git_dirty_files: $(git -C "$REPO" status --porcelain | wc -l)"
  echo "python: $("$VPY" -VV | tr '\n' ' ')"
  echo "openssl_cli: $(openssl version)"
  "$VPY" -c "import cryptography; from cryptography.hazmat.backends.openssl.backend import backend as b; print('cryptography:', cryptography.__version__, '| linked:', b.openssl_version_text())"
  echo "softhsm2: $(softhsm2-util --version 2>&1)"
  echo "pkcs11_module: ${SOV_TRADE_PKCS11_LIBRARY:-NOT FOUND}"
  echo "pkcs11_tool: $(pkcs11-tool --version 2>&1 | head -n 1 || dpkg-query -W opensc 2>/dev/null)"
  dpkg-query -W softhsm2 opensc openssl 2>/dev/null | sed 's/^/dpkg: /'
  echo "SOV_TRADE_REQUIRE_FUNCTIONAL: 1"
  echo "SOV_TRADE_FUZZ_EXAMPLES: $SOV_TRADE_FUZZ_EXAMPLES"
  echo "--- pip freeze"
  "$VPY" -m pip freeze --all
} > "$L/environment.txt" 2>&1

cd "$REPO"
export SOV_TRADE_REQUIRE_FUNCTIONAL=1 PYTHONDONTWRITEBYTECODE=1

step pytest_full "$VPY" -m pytest tests -rsx -v -p no:cacheprovider
step pytest_sov_trade "$VPY" -m pytest tests -k sov_trade -rsx -v -p no:cacheprovider
step sov_trade_zero_skips bash -c "! grep -E ' SKIPPED|^SKIPPED' '$L/pytest_sov_trade.log' && ! grep -E '^SKIPPED.*sov_trade' '$L/pytest_full.log' && echo 'sov_trade skips: 0'"
step unittest "$VPY" -m unittest discover -v
step validate_catalog "$VPY" docs/invariant_catalog/validate_catalog.py
step fuzz "$VPY" -m pytest tests/test_sc_sov_trade_001_fuzz.py -v -p no:cacheprovider
step hsm_evidence "$VPY" scripts/sov_trade/hsm_evidence.py
step cross_check "$VPY" scripts/sov_trade/cross_check.py "$OUT/cross_check"
if [ "${SKIP_MUTATION:-0}" != "1" ]; then
  step mutation "$VPY" scripts/sov_trade/mutation_check.py --python "$VPY" --out "$OUT/mutation.json"
fi

# --- static checks
VB="$VENV/bin"
step ruff_errors "$VB/ruff" check sov_trade scripts/sov_trade --select E9,F
info ruff_full "$VB/ruff" check sov_trade --select E,F,W,B,UP,S,BLE --output-format concise
step mypy bash -c "cd '$PP' && '$VB/mypy' -p semantic_compiler.sov_trade --ignore-missing-imports --follow-imports=silent"
step bandit "$VB/bandit" -r sov_trade -f txt
info bandit_scripts "$VB/bandit" -r scripts/sov_trade -f txt
step pip_audit_ci "$VB/pip-audit" --strict -r requirements/sov-trade-ci.lock --require-hashes --disable-pip
step pip_audit_static "$VB/pip-audit" --strict -r requirements/sov-trade-static.lock --require-hashes --disable-pip
step static_audit "$VPY" scripts/sov_trade/static_audit.py

# --- regression: dogfood (27 prompts) base vs head; corpus (963) if the harness is supplied
BASE="$(git merge-base HEAD origin/main 2>/dev/null || true)"
if [ -n "$BASE" ]; then
  BT="$OUT/base"; mkdir -p "$BT"
  git archive "$BASE" | tar -x -C "$BT" && mkdir -p "$OUT/basepp" && ln -s "$BT" "$OUT/basepp/semantic_compiler"
  echo "base: $BASE" > "$L/regression_base.txt"
  step dogfood_base env PYTHONPATH="$OUT/basepp" "$VPY" scripts/sov_trade/regression/dogfood_27.py "$OUT/dogfood_base.json"
  step dogfood_head "$VPY" scripts/sov_trade/regression/dogfood_27.py "$OUT/dogfood_head.json"
  step dogfood_diff "$VPY" scripts/sov_trade/regression/json_diff.py "$OUT/dogfood_base.json" "$OUT/dogfood_head.json"
  if [ -n "${SOV_TRADE_CORPUS_HARNESS:-}" ]; then
    step corpus_base env PYTHONPATH="$OUT/basepp" "$VPY" "$SOV_TRADE_CORPUS_HARNESS" "$BT" "$OUT/corpus_base.json"
    step corpus_head "$VPY" "$SOV_TRADE_CORPUS_HARNESS" "$REPO" "$OUT/corpus_head.json"
    step corpus_diff "$VPY" scripts/sov_trade/regression/json_diff.py "$OUT/corpus_base.json" "$OUT/corpus_head.json"
  else
    printf 'corpus\tNOT_RUN\t(SOV_TRADE_CORPUS_HARNESS not set)\n' >> "$STEPS"
  fi
else
  printf 'dogfood\tNOT_RUN\t(no origin/main merge-base)\n' >> "$STEPS"
fi

# --- hashes
( cd "$OUT" && find logs cross_check -type f 2>/dev/null; ls *.json 2>/dev/null; echo steps.tsv ) \
  | sort | ( cd "$OUT" && xargs sha256sum ) > "$OUT/SHA256SUMS"
echo; cat "$STEPS"
if awk -F'\t' '$2 != "0" && $2 != "NOT_RUN" && $2 !~ /^INFO/ {bad=1} END {exit bad}' "$STEPS"; then
  echo "verify: ALL STEPS PASSED"; exit 0
else
  echo "verify: SOME STEPS FAILED"; exit 1
fi
