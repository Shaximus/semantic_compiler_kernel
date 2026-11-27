#!/usr/bin/env python3
"""usage: json_diff.py base.json head.json -> prints changed keys; exit 1 if any differ."""
import json
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))
keys = sorted(set(a) | set(b))
diffs = [k for k in keys if a.get(k) != b.get(k)]
print(f"{len(keys)} items, {len(diffs)} diffs")
for k in diffs[:50]:
    print("DIFF", k, json.dumps(a.get(k))[:200], "->", json.dumps(b.get(k))[:200])
sys.exit(1 if diffs else 0)
