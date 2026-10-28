#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_judge_710a_recheck.py — 判读单元 710a1c50 对 S5 第五单元（unit 6e9acd73）的独立复算。

不采信回执/交接单/STATUS 叙述，全部从盘上重新算：
  A. 6 个 full ckpt 直读（torch.load 第二路径）：主目录 3 个 ab 30/30 + superseded 3 个 c 30/30
  B. full_run.log 逐行对账：6 臂各 30 epoch 无跳号、末态 acc 对齐 progress、4 条 resume、评测 108/108
  C. full_threearm.csv 结构：108 行=3 种子×3 臂×4 条件×3 模式；seed0/A/clean=0.0956（倒挂假象复现）
  D. 代码补丁核验：pilot_threearm.py/full_protocol.py 活跃代码中 xb*mask=0 处、xb*(1.0-mask)=3 处
  E. full_progress.json：eval_rows=0、verdict=null、convention_reset 块在盘、c 臂路径指向 superseded
  F. 关键产物文件存在性
"""
import csv
import json
import os
import re
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CK = os.path.join(HERE, "ckpt")
SUP = os.path.join(CK, "superseded_inverted_mask_20261027")

fails = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        fails.append(name)


# ---------- A. ckpt 直读 ----------
prog = json.load(open(os.path.join(PROJ, "results", "full_progress.json"), encoding="utf-8"))
runs = prog["runs"]
check("A0 progress runs=6", len(runs) == 6, str(list(runs.keys())))

main_full = sorted(f for f in os.listdir(CK) if f.startswith("full_") and f.endswith(".pt"))
check("A1 主目录 full ckpt=3 且全是 ab", len(main_full) == 3 and all("_ab.pt" in f for f in main_full), str(main_full))
sup_full = sorted(f for f in os.listdir(SUP) if f.startswith("full_") and f.endswith(".pt"))
check("A2 superseded full ckpt=3 且全是 c", len(sup_full) == 3 and all("_c.pt" in f for f in sup_full), str(sup_full))

exp_acc = {"seed0_ab": 0.9518, "seed1_ab": 0.9661, "seed2_ab": 0.9688,
           "seed0_c": 0.6885, "seed1_c": 0.7144, "seed2_c": 0.6840}
for d, files in ((CK, main_full), (SUP, sup_full)):
    for f in files:
        pth = os.path.join(d, f)
        ck = torch.load(pth, map_location="cpu", weights_only=False)
        key = f[len("full_quickdraw_"):-3]
        hist = ck.get("history", [])
        eps = [h["epoch"] for h in hist]
        ok = (ck.get("epochs_done") == 30 and eps == list(range(1, 31))
              and "opt_state_dict" in ck and abs(ck.get("train_acc", 0) - exp_acc[key]) < 5e-4)
        check(f"A3 {key} ckpt 完整", ok,
              f"epochs_done={ck.get('epochs_done')} hist={len(hist)} acc={ck.get('train_acc'):.4f} "
              f"(progress {runs[key]['train_acc']}) opt={'opt_state_dict' in ck}")

# ---------- B. full_run.log 逐行对账 ----------
log = open(os.path.join(HERE, "full_run.log"), encoding="utf-8").read()
ep_re = re.compile(r"\[full-train seed=(\d+) arm=(\w+) ep=(\d+)/30\] loss=([\d.]+) acc=([\d.]+)")
eps_seen, last_acc = {}, {}
for m in ep_re.finditer(log):
    s, arm, ep, acc = int(m.group(1)), m.group(2), int(m.group(3)), float(m.group(5))
    eps_seen.setdefault((s, arm), set()).add(ep)
    last_acc[(s, arm)] = acc
for key in exp_acc:
    s, arm = int(key[4]), key[6:]
    got = eps_seen.get((s, arm), set())
    check(f"B1 {key} log 30 epoch 无跳号", got == set(range(1, 31)), f"n={len(got)}")
    check(f"B2 {key} log 末态 acc 对齐 progress", abs(last_acc.get((s, arm), -1) - exp_acc[key]) < 5e-4,
          f"log={last_acc.get((s, arm))} progress={exp_acc[key]}")
resumes = re.findall(r"resume seed=(\d+) arm=(\w+) from epoch (\d+)", log)
check("B3 resume 链 4 条（ep7/ep14/ep26/ep10）",
      [r[2] for r in resumes] == ["7", "14", "26", "10"], str(resumes))
ev = re.findall(r"\[full-eval\] seed=(\d+) arm=(\w+) done \(\d+s cum, (\d+)/108 rows\)", log)
check("B4 评测 9 臂落盘且 108/108", len(ev) == 9 and ev[-1][2] == "108", str(ev[-1] if ev else None))

# ---------- C. CSV 结构 ----------
with open(os.path.join(PROJ, "results", "full_threearm.csv"), encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
check("C1 CSV 108 数据行", len(rows) == 108, f"n={len(rows)}")
keys = {(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows}
expect = {(str(s), a, c, str(p)) for s in range(3) for a in "ABC"
          for c in ["clean", "uniform30", "block5-30", "block15-30"] for p in range(3)}
check("C2 CSV 格子完备 3×3×4×3", keys == expect, f"unique={len(keys)}")
r0 = [r for r in rows if r["seed"] == "0" and r["arm"] == "A" and r["condition"] == "clean"][0]
check("C3 seed0/A/clean meanpool=0.0956（倒挂假象与 NOTE 一致）",
      abs(float(r0["acc_meanpool"]) - 0.0956) < 5e-4, r0["acc_meanpool"])

# ---------- D. 代码补丁（含索引形式 xb[..]*mask[..]） ----------
BAD_RE = r"xb(\s*\[[^\]]*\])?\s*\*\s*mask"
FIX_RE = r"xb(\s*\[[^\]]*\])?\s*\*\s*\(1\.0\s*-\s*mask"
for fn in ("pilot_threearm.py", "full_protocol.py"):
    src = open(os.path.join(HERE, fn), encoding="utf-8").read()
    active_bad = active_fix = 0
    for line in src.splitlines():
        code = line.split("#")[0]
        if re.search(BAD_RE, code):
            active_bad += 1
        if re.search(FIX_RE, code):
            active_fix += 1
    check(f"D {fn} 活跃代码 xb*mask=0", active_bad == 0, f"bad={active_bad}")
    if fn == "full_protocol.py":
        check("D full_protocol.py 活跃代码 xb*(1.0-mask)=1（C 训练路径）", active_fix == 1, f"fix={active_fix}")
    else:
        check("D pilot_threearm.py 活跃代码 xb*(1.0-mask)=4（eval+C训练+verify×2）", active_fix == 4, f"fix={active_fix}")

# ---------- E. progress 状态 ----------
check("E1 eval_rows=0（stale 108 行已清）", len(prog.get("eval_rows", [])) == 0)
check("E2 verdict=null", prog.get("verdict") is None)
cr = prog.get("convention_reset", {})
check("E3 convention_reset 块在盘且 cleared=108", cr.get("cleared_eval_rows") == 108 and bool(cr.get("reason")))
check("E4 c 臂 progress 路径指向 superseded",
      all("superseded" in runs[k]["ckpt"] for k in runs if k.endswith("_c")))
check("E5 ab 臂 progress 路径在主目录",
      all("superseded" not in runs[k]["ckpt"] for k in runs if k.endswith("_ab")))

# ---------- F. 产物存在性 ----------
for rel in ("results/full_threearm.csv", "results/full_threearm.md",
            "results/full_threearm_CONVENTION_NOTE.md", "results/s5_mask_convention_probe.json",
            "experiments/s5_mask_convention_probe.py", "experiments/s5_mask_fix_regression.py",
            "experiments/s5_mask_fix_regression.log", "experiments/s5_reset_stale_eval.py",
            "notes/handoff/S5-full-protocol.md"):
    check(f"F {rel} 在盘", os.path.exists(os.path.join(PROJ, rel)))

print("=" * 60)
print(f"RECHECK: {len(fails)} FAIL" if fails else "RECHECK: ALL PASS (0 fail)")
sys.exit(1 if fails else 0)
