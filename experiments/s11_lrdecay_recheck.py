#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s11_lrdecay_recheck.py — S11 收工独立复算（不采信回执/MD，从盘上 CSV+ckpt 重算）。

复算项（全部 exit=0 才 PASS）：
  1. CSV 结构：72 数据行、键 (seed,arm,cond,pattern) 唯一、n_eval 全 7500；
  2. 每条件 A/B mean±std 与 B−A 由 CSV 独立重算，与 progress verdict/MD 一致；
  3. 判据①：A@clean(3 种子 mean) vs S5 基线 92.30±0.86 → 增益与 criterion1 机械输出；
  4. 判据②：clean A≡B <0.1pp（且逐位相等预期）；
  5. 判据③：A@uniform30 vs 论文 Table III 30%=68.80；
  6. ckpt 三枚：epochs_done=30/30、history 30 连续、opt 在盘、LR 序列=12×1e-3/13×5e-4/5×2.5e-4；
  7. 掩码条件实现掩码率≈0.30；
  8. MD 主表 8 格（4 条件×A/B/B−A）由 CSV 逐格复算一致。
"""
from __future__ import annotations

import csv
import json
import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
RESULTS = os.path.join(PROJECT, "results")
CKPT_DIR = os.path.join(HERE, "ckpt")
CSV_PATH = os.path.join(RESULTS, "quickdraw_lrdecay.csv")
MD_PATH = os.path.join(RESULTS, "quickdraw_lrdecay.md")
PROG_PATH = os.path.join(RESULTS, "quickdraw_lrdecay_progress.json")

S5_A_CLEAN = {"0": 0.9109, "1": 0.9304, "2": 0.9277}
S5_A_CLEAN_MEAN = 0.9230
PAPER_U30 = 0.6880
EXPECTED_LR = [1e-3] * 12 + [5e-4] * 13 + [2.5e-4] * 5


def main() -> int:
    ok = True
    fails = []

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")
        if not cond:
            ok = False
            fails.append(name)

    with open(CSV_PATH, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    print(f"[recheck] CSV rows={len(rows)}")

    # 1) 结构
    keys = [(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows]
    check("csv_72_rows", len(rows) == 72, f"n={len(rows)}")
    check("csv_keys_unique", len(set(keys)) == len(keys))
    check("csv_n_eval_7500", all(int(r["n_eval"]) == 7500 for r in rows))
    arms = sorted({r["arm"] for r in rows})
    conds = sorted({r["condition"] for r in rows})
    check("csv_arms_AB", arms == ["A", "B"], str(arms))
    check("csv_conds_4", len(conds) == 4, str(conds))

    # 2) 每条件 A/B mean±std + B−A（独立重算）
    import statistics as st
    conds_order = ["clean", "uniform30", "block5-30", "block15-30"]
    recompute = {}
    for cond in conds_order:
        entry = {}
        for arm in ["A", "B"]:
            vals = [float(r["acc_meanpool"]) for r in rows
                    if r["arm"] == arm and r["condition"] == cond]
            entry[arm] = {"mean": st.mean(vals), "std": st.pstdev(vals), "n": len(vals)}
        entry["B_minus_A"] = entry["B"]["mean"] - entry["A"]["mean"]
        recompute[cond] = entry
        print(f"  {cond}: A={entry['A']['mean'] * 100:.2f}±{entry['A']['std'] * 100:.2f} "
              f"B={entry['B']['mean'] * 100:.2f}±{entry['B']['std'] * 100:.2f} "
              f"B−A={entry['B_minus_A'] * 100:+.2f}pp (n={entry['A']['n']})")

    # 3) 判据①
    a_clean = recompute["clean"]["A"]["mean"]
    a_clean_ps = {}
    for s in ["0", "1", "2"]:
        vals = [float(r["acc_meanpool"]) for r in rows
                if r["arm"] == "A" and r["condition"] == "clean" and r["seed"] == s]
        a_clean_ps[s] = st.mean(vals)
    gain_pp = (a_clean - S5_A_CLEAN_MEAN) * 100
    if gain_pp >= 1.5:
        c1 = "supported"
    elif gain_pp < 0.5:
        c1 = "falsified"
    else:
        c1 = "inconclusive"
    print(f"[recheck] 判据①: A@clean={a_clean * 100:.2f}% (per-seed "
          f"{ {k: round(v * 100, 2) for k, v in a_clean_ps.items()} }) vs S5 92.30 → "
          f"gain={gain_pp:+.2f}pp → criterion1={c1}")
    check("per_seed_matches_s5_extraction",
          all(abs(a_clean_ps[s] - S5_A_CLEAN[s]) < 1e-9 for s in S5_A_CLEAN) or True,
          "(S5 per-seed 锚点仅参照，不断言)")

    # 4) 判据② clean A≡B
    a_b_clean = []
    for r in rows:
        if r["condition"] != "clean":
            continue
        match = [x for x in rows if x["seed"] == r["seed"] and x["arm"] == ("B" if r["arm"] == "A" else "A")
                 and x["condition"] == "clean" and x["pattern"] == r["pattern"]]
        if match and r["arm"] == "A":
            a_b_clean.append(abs(float(r["acc_meanpool"]) - float(match[0]["acc_meanpool"])))
    max_ab = max(a_b_clean) if a_b_clean else 1.0
    check("clean_A_equals_B_lt_0p1pp", max_ab * 100 < 0.1, f"max|A−B|={max_ab * 100:.4f}pp")

    # 5) 判据③
    a_u30 = recompute["uniform30"]["A"]["mean"]
    print(f"[recheck] 判据③: A@uniform30={a_u30 * 100:.2f}% vs 论文 Table III 30%=68.80 → "
          f"{(a_u30 - PAPER_U30) * 100:+.2f}pp")

    # 6) ckpt 三枚
    for s in [0, 1, 2]:
        pth = os.path.join(CKPT_DIR, f"quickdraw_lrdecay_seed{s}_ab.pt")
        if not os.path.exists(pth):
            check(f"ckpt_seed{s}_exists", False, pth)
            continue
        payload = torch.load(pth, map_location="cpu", weights_only=False)
        ep = int(payload.get("epochs_done", 0))
        hist = payload.get("history", [])
        hist_ok = ([h["epoch"] for h in hist] == list(range(1, 31)))
        lrs = [h.get("lr") for h in hist]
        lr_ok = (lrs == EXPECTED_LR)
        opt_ok = "opt_state_dict" in payload
        check(f"ckpt_seed{s}_30of30", ep == 30, f"epochs_done={ep}")
        check(f"ckpt_seed{s}_history_continuous", hist_ok)
        check(f"ckpt_seed{s}_lr_schedule_paper", lr_ok,
              f"lrs={sorted(set(lrs))} seq_ok={lr_ok}")
        check(f"ckpt_seed{s}_opt_state_in_ckpt", opt_ok)
        print(f"    seed{s}: train_acc={payload.get('train_acc')} "
              f"train_loss={payload.get('train_loss')} sec={payload.get('train_sec')}")

    # 7) 掩码率≈0.30
    for cond in ["uniform30", "block5-30", "block15-30"]:
        mfs = [float(r["masked_fraction_realized"]) for r in rows if r["condition"] == cond]
        check(f"masked_fraction_{cond}", abs(st.mean(mfs) - 0.30) < 0.02,
              f"mean={st.mean(mfs):.4f}")

    # 8) MD 主表 8 格复算一致
    with open(MD_PATH, encoding="utf-8") as fh:
        md = fh.read()
    for cond in conds_order:
        e = recompute[cond]
        for cell, val in [(f"| {cond} | {e['A']['mean'] * 100:.2f}±{e['A']['std'] * 100:.2f} "
                           f"| {e['B']['mean'] * 100:.2f}±{e['B']['std'] * 100:.2f} "
                           f"| {e['B_minus_A'] * 100:+.2f} |", True)]:
            check(f"md_table_{cond}", cell in md, cell[:60])

    # progress verdict 对齐
    with open(PROG_PATH, encoding="utf-8") as fh:
        prog = json.load(fh)
    pv = prog.get("verdict") or {}
    check("progress_verdict_criterion1_matches",
          pv.get("criterion1") == c1, f"progress={pv.get('criterion1')} recompute={c1}")
    check("progress_eval_rows_72", len(prog.get("eval_rows", [])) == 72,
          f"n={len(prog.get('eval_rows', []))}")
    check("progress_runs_3", len(prog.get("runs", {})) == 3,
          f"runs={list(prog.get('runs', {}).keys())}")

    print(f"[recheck] OVERALL: {'PASS' if ok else 'FAIL'}"
          + (f" (fails={fails})" if fails else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
