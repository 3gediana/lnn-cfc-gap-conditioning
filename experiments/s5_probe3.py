#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_probe3.py — C 臂单训练 step 全链路计时拆解（找真瓶颈）。
用法：cd 课题根 && G:/ai/python11/python.exe experiments/s5_probe3.py
"""
import os
import sys
import time

import torch
import torch.nn as nn
import torch.optim as optim

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pilot_threearm import (DrawingClassifier, d2_timespans, make_mask,  # noqa: E402
                            EPOCHS, BATCH)

DEVICE = torch.device("cuda")
torch.manual_seed(0)
model = DrawingClassifier("quickdraw", with_gap_bit=True).to(DEVICE)
opt = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
crit = nn.CrossEntropyLoss()

B, L = BATCH, 100
xb = torch.randn(B, L, 5, device=DEVICE)
yb = torch.randint(0, 10, (B,), device=DEVICE)

# 预热
for _ in range(2):
    mask = make_mask("block5-30", B, L, 0, 0).to(DEVICE)
    xin = xb * mask
    ts = d2_timespans(mask).to(DEVICE)
    logits, _ = model.forward_ts_gap(xin, ts, mask)
    loss = crit(logits, yb)
    loss.backward()
    opt.step()
    opt.zero_grad()
torch.cuda.synchronize()

# 分段计时（5 次平均）
segs = {"make_mask_cpu": 0.0, "to_device": 0.0, "d2_ts_cpu": 0.0,
        "fwd_bwd": 0.0, "total": 0.0}
N = 5
t_total = time.time()
for it in range(N):
    t0 = time.time()
    mask = make_mask("block5-30", B, L, 77 + it, 0)
    t1 = time.time()
    mask = mask.to(DEVICE)
    xin = xb * mask
    t2 = time.time()
    ts = d2_timespans(mask)
    t3 = time.time()
    ts = ts.to(DEVICE)
    t4 = time.time()
    opt.zero_grad()
    logits, _ = model.forward_ts_gap(xin, ts, mask)
    loss = crit(logits, yb)
    loss.backward()
    nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    torch.cuda.synchronize()
    t5 = time.time()
    segs["make_mask_cpu"] += t1 - t0
    segs["to_device"] += t2 - t1
    segs["d2_ts_cpu"] += t3 - t2
    segs["fwd_bwd"] += t5 - t4
torch.cuda.synchronize()
segs["total"] = time.time() - t_total
print("C-arm per-batch breakdown (avg over %d):" % N)
for k, v in segs.items():
    print(f"  {k}: {v / N * 1000:.1f} ms")
print(f"=> projected 30 epochs x 333 batches: {segs['total'] / N * 9990 / 60:.1f} min")

# 对照：A/B 臂 step 计时
t0 = time.time()
for it in range(N):
    opt.zero_grad()
    logits, _ = model.forward_lib(xb)
    loss = crit(logits, yb)
    loss.backward()
    opt.step()
torch.cuda.synchronize()
print(f"AB-arm per-batch: {(time.time() - t0) / N * 1000:.1f} ms "
      f"=> 30 epochs x 333 batches: {(time.time() - t0) / N * 9990 / 60:.1f} min")
