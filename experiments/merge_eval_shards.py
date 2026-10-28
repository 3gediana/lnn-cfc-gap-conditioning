#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_eval_shards.py — 合并主 progress + 各分片 progress 的 eval_rows（2026-10-26 S3 续跑单元）。

背景：评测矩阵按 (seed, arm) 分片多进程并行跑（eval_shard_runner.py），每片写独立
progress 文件；本脚本按键 (dataset,seed,arm,condition,pattern) 去重合并，108 行齐全
才写 CSV/MD/timing（与 pilot_threearm.py eval 分支的落盘契约一致）。幂等可重跑。

竞争处理：主评测进程（seed1 段）可能仍在逐行原子写主 progress——故合并结果默认写
results/pilot_progress.merged.json，不覆盖主文件；确认主进程已结束后加 --canonical
再写一份到规范位置（results/pilot_progress.json）。

用法：
  G:/ai/python11/python.exe experiments/merge_eval_shards.py            # 合并+校验+出表
  G:/ai/python11/python.exe experiments/merge_eval_shards.py --canonical # 主进程结束后同写规范位
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "pilot_threearm", os.path.join(HERE, "pilot_threearm.py"))
    assert spec is not None and spec.loader is not None
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    return P


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="quickdraw")
    ap.add_argument("--canonical", action="store_true",
                    help="同时把合并结果写到规范位 results/pilot_progress.json"
                         "（仅主评测进程已结束时使用）")
    args = ap.parse_args()

    P = load_module()
    shard_files = sorted(glob.glob(os.path.join(PROJECT, "results", "pilot_progress.shard*.json")))
    sources = [("main", P.PROGRESS)] + [(os.path.basename(f), f) for f in shard_files]

    rows_by_key: dict = {}
    sanity, runs = {}, {}
    for name, path in sources:
        if not os.path.exists(path):
            print(f"[merge] skip {name} (missing)")
            continue
        with open(path, encoding="utf-8") as fh:
            p = json.load(fh)
        n_new = 0
        for r in p.get("eval_rows", []):
            key = (r.get("dataset"), r.get("seed"), r.get("arm"), r.get("condition"), r.get("pattern"))
            if key not in rows_by_key:
                rows_by_key[key] = r
                n_new += 1
        if p.get("sanity"):
            sanity = {**p["sanity"], **sanity}          # 主进程的 sanity 优先
        if p.get("runs"):
            runs = {**p["runs"], **runs}
        print(f"[merge] {name}: +{n_new} rows (total unique {len(rows_by_key)})")

    rows = sorted(rows_by_key.values(),
                  key=lambda r: (r["seed"], r["arm"], P.CONDITIONS.index(r["condition"]), r["pattern"]))
    print(f"[merge] union rows = {len(rows)} / {P.EVAL_TOTAL}")
    if len(rows) < P.EVAL_TOTAL:
        have = {(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows}
        missing = [(s, a, c, pt) for s in P.SEEDS for a in ["A", "B", "C"]
                   for c in P.CONDITIONS for pt in range(P.N_PATTERNS)
                   if (s, a, c, pt) not in have]
        print(f"[merge] INCOMPLETE: {len(missing)} cells missing, e.g. {missing[:6]}")
        print("[merge] no CSV/MD written (contract: 108 rows only)")
        return 2

    summary = P.summarize(rows, args.dataset)
    timing = {"merged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
              "shard_timing": {}, "note": "S3 分片并行（eval_shard_runner）+ 主进程 seed1 段合并"}
    # 2026-10-26T03:3x 三补单元：canonical eval 续跑（pilot_threearm.py eval）在合并前
    # 已写出带真实计时的 pilot_timing.json；合并时原样携带该快照，不用空壳计时覆盖真实数字。
    tpath = os.path.join(PROJECT, "results", "pilot_timing.json")
    if "resume_eval_run" not in timing and os.path.exists(tpath):
        with open(tpath, encoding="utf-8") as fh:
            timing["resume_eval_run"] = json.load(fh).get("u5_runtime")
    for f in shard_files:
        tf = f.replace(".json", ".timing.json")
        if os.path.exists(tf):
            with open(tf, encoding="utf-8") as fh:
                timing["shard_timing"][os.path.basename(f)] = json.load(fh).get("u5_runtime")

    merged = {"runs": runs, "eval": [], "sanity": sanity,
              "verdict": summary["verdict"], "eval_rows": rows}
    P.PROGRESS = os.path.join(PROJECT, "results", "pilot_progress.merged.json")
    P.save_progress(merged)
    P.write_csv_md(rows, summary, args.dataset, sanity.get("verify_real_size", {}), timing)
    P.save_timing(merged, timing)
    print(f"[merge] CSV/MD/timing written; verdict={json.dumps(summary['verdict'], ensure_ascii=False)}")
    print("[merge] SANITY:", json.dumps(summary["sanity"], ensure_ascii=False))

    if args.canonical:
        P.PROGRESS = os.path.join(PROJECT, "results", "pilot_progress.json")
        P.save_progress(merged)
        print("[merge] canonical pilot_progress.json written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
