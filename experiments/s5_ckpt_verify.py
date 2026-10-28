#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_ckpt_verify.py — kill 后校验 full_* checkpoint 完整性（续跑前提）。
用法：G:/ai/python11/python.exe experiments/s5_ckpt_verify.py
"""
import json
import os

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CKPT = os.path.join(HERE, "ckpt")

for f in sorted(os.listdir(CKPT)):
    if not f.startswith("full_"):
        continue
    pth = os.path.join(CKPT, f)
    d = torch.load(pth, map_location="cpu", weights_only=False)
    hist = d.get("history", [])
    print(f"{f}: epochs_done={d.get('epochs_done')} target={d.get('epochs_target')} "
          f"train_n={d.get('train_n')} last_acc={d.get('train_acc'):.4f} "
          f"history_len={len(hist)} sec={d.get('train_sec')} "
          f"has_opt={'opt_state_dict' in d} size={os.path.getsize(pth)}")
    # 历史单调性（防交叉写损坏）
    eps = [h["epoch"] for h in hist]
    assert eps == list(range(1, len(eps) + 1)), f"history not contiguous: {eps}"
print("ckpt integrity OK (history contiguous, opt state present)")

# progress 快照
with open(os.path.join(PROJ, "results", "full_progress.json"), encoding="utf-8") as fh:
    prog = json.load(fh)
print("progress: runs=", list(prog.get("runs", {})), "eval_rows=", len(prog.get("eval_rows", [])),
      "verify_pass=", prog.get("sanity", {}).get("verify_real_size", {}).get("verify_pass"))
