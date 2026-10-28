#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""per_seed_numbers.py — 从最终 CSV 实算逐种子×臂×条件 mean（pp），供状态文件引用。"""
import csv
import os
import statistics as st

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(PROJECT, "results", "pilot_threearm.csv"), encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
assert len(rows) == 108, len(rows)

for cond in ["clean", "uniform30", "block5-30", "block15-30"]:
    line = [cond]
    for arm in ["A", "B", "C"]:
        vals = [float(r["acc_meanpool"]) for r in rows if r["arm"] == arm and r["condition"] == cond]
        seeds = {}
        for r in rows:
            if r["arm"] == arm and r["condition"] == cond:
                seeds.setdefault(int(r["seed"]), []).append(float(r["acc_meanpool"]))
        sm = {s: st.mean(v) for s, v in sorted(seeds.items())}
        line.append(f"{arm}={st.mean(vals)*100:.2f}pp(seed0/1/2="
                    f"{sm[0]*100:.2f}/{sm[1]*100:.2f}/{sm[2]*100:.2f})")
    # B-A / C-A per seed
    for arm in ["B", "C"]:
        d = []
        for s in [0, 1, 2]:
            a = st.mean([float(r["acc_meanpool"]) for r in rows
                         if r["arm"] == "A" and r["condition"] == cond and int(r["seed"]) == s])
            x = st.mean([float(r["acc_meanpool"]) for r in rows
                         if r["arm"] == arm and r["condition"] == cond and int(r["seed"]) == s])
            d.append((x - a) * 100)
        line.append(f"{arm}-A/seed={d[0]:+.2f}/{d[1]:+.2f}/{d[2]:+.2f}pp(mean={st.mean(d):+.2f})")
    print(" | ".join(line))
