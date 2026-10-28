#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_mask_fix_regression.py — 掩码 Convention 修正后快速回归（~30s）。

验证 2026-10-27T01:3x 三处修正（eval/C 训练 xb*mask → xb*(1-mask)）后：
  R1 修正后 eval_arm_condition A@clean ≈ 0.916（探针 T1/T6 基准，原 0.096）
  R2 修正后 A@block5-30 meanpool 合理且 masked_fraction≈0.30
  R3 C 臂修正后训练路径可跑（loss 有限、清零率≈0.30、gapbit≈0.30）
"""
import os
import sys

import torch
import torch.nn as nn
import torch.optim as optim

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pilot_threearm as P  # noqa: E402
import full_protocol as F  # noqa: E402

F._patch_pilot_d2()

x_tr, y_tr, x_te, y_te = F.full_splits("quickdraw")
model, _ = F.load_model_full(0, "ab", "quickdraw")

accs, mf = P.eval_arm_condition(model, "A", x_te[:2048], y_te[:2048], "clean", 0, 0)
print(f"R1 patched eval A@clean meanpool={accs['meanpool']:.4f} (expect ~0.916, was 0.096)")
r1 = accs["meanpool"] > 0.85

accs2, mf2 = P.eval_arm_condition(model, "A", x_te[:2048], y_te[:2048], "block5-30", 0, 0)
print(f"R2 patched eval A@block5-30 meanpool={accs2['meanpool']:.4f} masked_fraction={mf2:.4f}")
r2 = (0.3 < accs2["meanpool"] < 0.95) and abs(mf2 - 0.30) < 0.05

mc = P.DrawingClassifier("quickdraw", with_gap_bit=True).to(P.DEVICE)
opt = optim.AdamW(mc.parameters(), lr=P.LR)
crit = nn.CrossEntropyLoss()
r3 = True
for i in range(2):
    xb = x_tr[i * 128:(i + 1) * 128].to(P.DEVICE)
    yb = y_tr[i * 128:(i + 1) * 128].to(P.DEVICE)
    mask = P.make_mask("block5-30", xb.shape[0], xb.shape[1], 77, 0).to(P.DEVICE)
    xin = xb * (1.0 - mask)
    ts = F.d2_timespans_vec(mask).to(P.DEVICE)
    logits, _ = mc.forward_ts_gap(xin, ts, mask)
    loss = crit(logits, yb)
    loss.backward()
    opt.step()
    opt.zero_grad()
    raw_nonzero = (xb.abs().sum(dim=2) > 0)          # 原始非 padding 帧
    zf = ((xin.abs().sum(dim=2) == 0) & raw_nonzero).float().sum().item() / raw_nonzero.float().sum().item()
    print(f"R3 C-train smoke batch{i} loss={loss.item():.4f} zeroed_among_raw_nonzero={zf:.4f} gapbit={mask.mean().item():.4f}")
    r3 = r3 and (loss.item() < 10.0) and abs(zf - 0.30) < 0.05

print(f"REGRESSION: R1={'PASS' if r1 else 'FAIL'} R2={'PASS' if r2 else 'FAIL'} R3={'PASS' if r3 else 'FAIL'}")
sys.exit(0 if (r1 and r2 and r3) else 1)
