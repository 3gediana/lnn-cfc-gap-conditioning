#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""np_env_check.py — nm_negative_probes 单元开工环境自检（只读，零副作用）。

检查项：python/torch/cuda、GPU 现存进程归属（防与 S11 争 GPU）、
6 个 nmnist ckpt 可加载性与 epochs_done、S10 结果 CSV 关键锚点数字、
data/nmnist 缓存存在性。exit=0 全过。
"""
import json
import os
import subprocess
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT, "experiments"))

ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")


print("[env] torch/cuda ...")
import torch  # noqa: E402

print(f"  torch={torch.__version__} cuda_available={torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  device={torch.cuda.get_device_name(0)} "
          f"mem={torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f}GiB")
check("cuda_available", torch.cuda.is_available())

print("[env] GPU processes (tasklist wide, G:/ai python = 训练残留嫌疑) ...")
try:
    out = subprocess.run(["tasklist", "/V", "/FO", "CSV"], capture_output=True,
                         text=True, timeout=60).stdout
    hits = [ln for ln in out.splitlines()
            if ("python" in ln.lower() or "G:\\ai" in ln or "G:/ai" in ln)]
    for ln in hits[:10]:
        print("   ", ln[:160])
    n_gai = sum(1 for ln in out.splitlines() if "G:\\ai" in ln or "G:/ai" in ln)
    print(f"  G:/ai 相关进程行数={n_gai}")
except Exception as exc:  # noqa: BLE001
    print(f"  tasklist 失败: {exc}")

print("[env] nmnist ckpt ...")
CKPT = os.path.join(PROJECT, "experiments", "ckpt")
for seed in [0, 1, 2]:
    for arm in ["ab", "c"]:
        p = os.path.join(CKPT, f"nmnist_seed{seed}_{arm}.pt")
        if not os.path.exists(p):
            check(f"nmnist_seed{seed}_{arm}.pt", False, "missing")
            continue
        payload = torch.load(p, map_location="cpu", weights_only=False)
        ep = int(payload.get("epochs_done", -1))
        gap = payload.get("with_gap_bit", None)
        hist = payload.get("history", [])
        check(f"nmnist_seed{seed}_{arm}.pt", ep == 10 and len(hist) == 10,
              f"epochs_done={ep} history={len(hist)} with_gap_bit={gap} "
              f"train_acc={payload.get('train_acc')}")

print("[env] S10 CSV anchors ...")
csvp = os.path.join(PROJECT, "results", "nmnist_threearm.csv")
with open(csvp, encoding="utf-8") as fh:
    rows = [ln.strip().split(",") for ln in fh if ln.strip()]
hdr, data = rows[0], rows[1:]
check("S10 CSV 108 data rows", len(data) == 108, f"n={len(data)}")


def mean_acc(arm, cond, col=6):
    vals = [float(r[col]) for r in data if r[2] == arm and r[3] == cond]
    return sum(vals) / len(vals) if vals else float("nan")


for cond in ["clean", "uniform30", "block5-30"]:
    a = mean_acc("A", cond)
    c = mean_acc("C", cond)
    print(f"  S10 {cond}: A={a * 100:.2f}% C={c * 100:.2f}% C-A={(c - a) * 100:+.2f}pp")

print("[env] data cache ...")
for rel in [os.path.join("data", "nmnist", "cache")]:
    p = os.path.join(PROJECT, rel)
    check(f"{rel} exists", os.path.isdir(p))
    if os.path.isdir(p):
        for f in sorted(os.listdir(p))[:8]:
            sz = os.path.getsize(os.path.join(p, f))
            print(f"    {f} {sz / 1024 ** 3:.2f}GiB" if sz > 1024 ** 3 else f"    {f} {sz}B")

print(f"[env] OVERALL: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
