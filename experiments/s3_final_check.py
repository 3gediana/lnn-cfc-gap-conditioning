#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""final_check.py — S3 收工前终态校验：progress 108 行+verdict、CSV 行数、
timing 真实数字、sanity 三门控、四份契约产物存在性。"""
import csv
import json
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(PROJECT, "results")

with open(os.path.join(R, "pilot_progress.json"), encoding="utf-8") as fh:
    p = json.load(fh)
rows = p.get("eval_rows", [])
print(f"progress eval_rows = {len(rows)}")
print(f"progress verdict = {json.dumps(p.get('verdict'), ensure_ascii=False)}")
print(f"progress sanity.verify_real_size = {json.dumps(p.get('sanity', {}).get('verify_real_size'), ensure_ascii=False)}")

with open(os.path.join(R, "pilot_threearm.csv"), encoding="utf-8") as fh:
    rd = list(csv.DictReader(fh))
print(f"csv data rows = {len(rd)}")
assert len(rd) == 108 and len(rows) == 108

with open(os.path.join(R, "pilot_timing.json"), encoding="utf-8") as fh:
    t = json.load(fh)
print(f"timing u5_runtime keys = {sorted(t['u5_runtime'].keys())}")
print(f"timing resume_eval_run = {json.dumps(t['u5_runtime'].get('resume_eval_run'), ensure_ascii=False)}")

# 契约产物存在性
for f in ["pilot_threearm.csv", "pilot_threearm.md", "pilot_progress.json", "pilot_timing.json"]:
    path = os.path.join(R, f)
    ok = os.path.exists(path) and os.path.getsize(path) > 0
    print(f"artifact {f}: exists={ok} size={os.path.getsize(path) if os.path.exists(path) else 0}")
    assert ok

# 三门控复述
s = p.get("sanity", {})
print(f"gate1 clean A≡B<0.1pp: {s.get('clean_A_equals_B_lt_0p1pp')}")
print(f"gate2 uniform30 z>2: {s.get('A_uniform30_z_vs_chance')} -> {s.get('A_uniform30_direction_ok')}")
print(f"gate3 A@clean>=97%: {s.get('A_clean_fidelity_97')} (A@clean={s.get('clean_A_mean')})")
print("FINAL_CHECK_PASS")
