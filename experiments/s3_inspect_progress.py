#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inspect_progress.py — 盘点 eval progress 行数/缺口（S3 三补单元只读盘点）。"""
import glob
import json
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEEDS = [0, 1, 2]
ARMS = ["A", "B", "C"]
# 从 pilot_threearm 常量读，避免手抄
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pilot_threearm", os.path.join(PROJECT, "experiments", "pilot_threearm.py"))
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
print("EVAL_TOTAL =", P.EVAL_TOTAL, "| CONDITIONS =", P.CONDITIONS,
      "| N_PATTERNS =", P.N_PATTERNS, "| SEEDS =", P.SEEDS)

sources = [("main", os.path.join(PROJECT, "results", "pilot_progress.json"))]
for f in sorted(glob.glob(os.path.join(PROJECT, "results", "pilot_progress.shard*.json"))):
    sources.append((os.path.basename(f), f))

rows_by_key = {}
for name, path in sources:
    if not os.path.exists(path):
        print(f"[{name}] missing")
        continue
    with open(path, encoding="utf-8") as fh:
        p = json.load(fh)
    n_new = 0
    for r in p.get("eval_rows", []):
        key = (r.get("dataset"), r.get("seed"), r.get("arm"), r.get("condition"), r.get("pattern"))
        if key not in rows_by_key:
            rows_by_key[key] = r
            n_new += 1
    print(f"[{name}] +{n_new} rows (union so far {len(rows_by_key)})")

have = {(k[1], k[2], k[3], k[4]) for k in rows_by_key}
missing = [(s, a, c, pt) for s in SEEDS for a in ARMS
           for c in P.CONDITIONS for pt in range(P.N_PATTERNS)
           if (s, a, c, pt) not in have]
print(f"UNION = {len(rows_by_key)} / {P.EVAL_TOTAL}  MISSING = {len(missing)}")
for m in missing:
    print("  missing:", m)
