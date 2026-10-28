#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_shard_runner.py — S3 评测矩阵分片并行驱动器（2026-10-26 S3 续跑单元新增）。

背景：全矩阵 108 行串行 ≈28min，超出单元窗口；实测 GPU 利用率 7%（manual-loop
100 步内核启动 bound），32 核 CPU 有余量 → 按 (seed, arm) 分片多进程并行。

设计约束（诚信优先）：
  - 不改动 pilot_threearm.py 任何数值路径：本驱动器只 import 该模块并调用其
    已验证函数（pilot_splits / load_model / eval_arm_condition / save_progress
    / save_timing），逐行持久化口径与 run_eval_matrix 逐字一致；
  - 每个分片写独立 progress 文件（启动时从主 progress 快照复制，已跑出行跳过），
    与主评测进程零文件竞争；合并由 merge_eval_shards.py 按键去元成；
  - 断点续跑：kill/超时后重跑同一命令即续跑（分片文件内已完成行跳过）。

用法：
  G:/ai/python11/python.exe experiments/eval_shard_runner.py \
      --seed 2 --arms A,B --progress results/pilot_progress.shard_s2ab.json
  G:/ai/python11/python.exe experiments/eval_shard_runner.py \
      --seed 2 --arms C   --progress results/pilot_progress.shard_s2c.json
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
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
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--arms", required=True, help="逗号分隔臂名子集，如 A,B 或 C")
    ap.add_argument("--progress", required=True, help="分片 progress 路径（相对课题目录）")
    ap.add_argument("--dataset", default="quickdraw")
    args = ap.parse_args()

    P = load_module()
    shard_path = os.path.join(PROJECT, args.progress)
    # 启动时从主 progress 快照初始化（不存在则空表）；重跑时保留分片自身进度
    if not os.path.exists(shard_path) and os.path.exists(P.PROGRESS):
        shutil.copyfile(P.PROGRESS, shard_path)
    setattr(P, "PROGRESS", shard_path)             # save/load_progress 走分片文件
    setattr(P, "TIMING", shard_path.replace(".json", ".timing.json"))
    arms = [a.strip().upper() for a in args.arms.split(",") if a.strip()]
    arm_keys = (["ab"] if ({"A", "B"} & set(arms)) else []) + (["c"] if "C" in arms else [])

    t0 = time.time()
    x_tr, y_tr, x_te, y_te = P.pilot_splits(args.dataset)
    progress = P.load_progress()
    rows = list(progress.get("eval_rows", []))
    done = {(r.get("dataset"), r.get("seed"), r.get("arm"), r.get("condition"), r.get("pattern"))
            for r in rows}
    models = {a: P.load_model(args.seed, a, args.dataset)[0] for a in arm_keys}
    t_eval = time.time()
    for arm_name, arm_key in [("A", "ab"), ("B", "ab"), ("C", "c")]:
        if arm_name not in arms:
            continue
        for cond in P.CONDITIONS:
            for pattern in range(P.N_PATTERNS):
                key = (args.dataset, args.seed, arm_name, cond, pattern)
                if key in done:
                    continue
                accs, mf = P.eval_arm_condition(models[arm_key], arm_name,
                                                x_te, y_te, cond, args.seed, pattern)
                rows.append({"dataset": args.dataset, "seed": args.seed, "arm": arm_name,
                             "condition": cond, "pattern": pattern, "n_eval": x_te.shape[0],
                             "masked_fraction_realized": round(mf, 4),
                             "acc_meanpool": round(accs["meanpool"], 4),
                             "acc_final": round(accs["final"], 4),
                             "acc_gapnb": round(accs["gapnb"], 4)})
                progress["eval_rows"] = rows
                P.save_progress(progress)      # 逐行持久化：超时/kill 不丢已出行
        print(f"[shard] seed={args.seed} arm={arm_name} done "
              f"({time.time() - t_eval:.0f}s cum, {len(rows)} rows in shard)", flush=True)
    P.save_timing(progress, {"data_prep_sec": round(t_eval - t0, 1),
                             "shard_seed": args.seed, "shard_arms": arms,
                             "eval_sec": round(time.time() - t_eval, 1),
                             "total_sec": round(time.time() - t0, 1)})
    print(f"[shard] seed={args.seed} arms={arms} COMPLETE ({len(rows)} rows in shard)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
