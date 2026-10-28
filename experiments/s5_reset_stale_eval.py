#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_reset_stale_eval.py — 清空倒挂 Convention 下的 stale 评测数据。

2026-10-27T01:3x：full_progress.json 的 108 行 eval_rows 与 verdict 块为掩码
Convention 倒挂（xin=xb*mask）下计算，全部作废。清空 eval_rows/verdict 使下一单元
重跑 `full_protocol.py all` 时按修正 Convention（xb*(1-mask)）全量重算；
runs/sanity 保留（sanity.verify_real_size 与 Convention 无关；runs 中 C 条目
将被重训后覆盖，A/B 条目仍有效）。原子写，kill 不留半截。
"""
import json
import os
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS = os.path.join(PROJECT, "results", "full_progress.json")

with open(PROGRESS, encoding="utf-8") as fh:
    p = json.load(fh)

n_rows = len(p.get("eval_rows", []))
had_verdict = p.get("verdict") is not None
p["eval_rows"] = []
p["verdict"] = None
p["convention_reset"] = {
    "at": "2026-10-27T01:3x",
    "reason": ("mask convention inverted (xin=xb*mask kept masked frames); "
               "stale rows computed under inverted convention, see "
               "results/full_threearm_CONVENTION_NOTE.md and "
               "experiments/s5_mask_convention_probe.py"),
    "cleared_eval_rows": n_rows,
    "cleared_verdict": had_verdict,
    "fix_applied": "pilot_threearm.py eval_arm_condition + train_one, "
                   "full_protocol.py train_one_full: xb*mask -> xb*(1-mask)",
    "regression": "experiments/s5_mask_fix_regression.py R1-R3 all PASS",
    "c_ckpts_moved_to": "experiments/ckpt/superseded_inverted_mask_20261027/",
}

tmp = PROGRESS + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(p, fh, ensure_ascii=False, indent=2)
os.replace(tmp, PROGRESS)
print(f"cleared eval_rows={n_rows} verdict={had_verdict}; "
      f"runs kept: {sorted(p.get('runs', {}).keys())}")
print("progress reset OK")
