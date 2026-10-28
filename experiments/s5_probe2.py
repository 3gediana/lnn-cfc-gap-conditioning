#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_probe2.py — ncps 版本 + B>1 timespans 库路径可用性 + C 臂单 batch 计时拆解。
用法：G:/ai/python11/python.exe experiments/s5_probe2.py
"""
import os
import time

import torch
import ncps
import ncps.torch
from ncps.torch import CfC

print("ncps", getattr(ncps, "__version__", "?"))

DEVICE = torch.device("cuda")
UNITS = 256
torch.manual_seed(0)
core = CfC(129, UNITS, proj_size=UNITS, batch_first=True,
           backbone_layers=1, backbone_units=128).to(DEVICE)
B, L = 128, 100
feats = torch.randn(B, L, 129, device=DEVICE)
ts = torch.ones(B, L, device=DEVICE)

# 1) 库 forward with timespans B>1
try:
    out, _ = core(feats, timespans=ts)
    torch.cuda.synchronize()
    print("lib_timespans_B>1: OK", tuple(out.shape))
except Exception as exc:  # noqa: BLE001
    print("lib_timespans_B>1: CRASH", type(exc).__name__, str(exc)[:200])

# 2) manual-loop 单 batch 前向计时（fwd only）
h = torch.zeros((B, core.state_size), device=DEVICE)
t0 = time.time()
outs = []
with torch.no_grad():
    for t in range(L):
        h_out, h = core.rnn_cell.forward(feats[:, t], h, ts[:, t].unsqueeze(1))
        outs.append(core.fc(h_out))
torch.cuda.synchronize()
print(f"manual_loop fwd-only 1 batch: {time.time() - t0:.3f}s")

# 3) d2_timespans python 循环计时（CPU）
from experiments.pilot_threearm import d2_timespans  # noqa: E402

mask = (torch.rand(B, L, 1) < 0.3).float()
t0 = time.time()
tsd = d2_timespans(mask)
print(f"d2_timespans loop 1 batch (cpu): {time.time() - t0:.3f}s")
