#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_eval_cost_probe.py — researcher 判读探针：全量规模（n=7500/格）单格评测真实耗时。

动机：S5 首单元交接单称 full eval 108 格「向量化后预计约 8-10min」，但该数字
无实测支撑；pilot 实测 B/C 臂 ≈21s/格 @n=3000（DECISIONS 03:3x），按 n 线性
外推 7500 应为 ≈52s/格 → 108 格 ≈60-95min，与 8-10min 差 6-10 倍。
本探针用随机权重模型（计算量与训练后模型相同）实测三臂单格耗时，给下一单元
排产提供证据级估计。用法：G:/ai/python11/python.exe experiments/s5_eval_cost_probe.py
"""
import os
import sys
import time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pilot_threearm import DrawingClassifier, eval_arm_condition, make_mask  # noqa: E402

DEVICE = torch.device("cuda")
N = 7500  # full 协议每格评测样本数（与 run_eval_matrix_full 的 x_te 一致）
torch.manual_seed(0)
# 与 run_eval_matrix_full 一致：A/B 臂用 ab 模型（with_gap_bit=False），C 臂用 c 模型
m_ab = DrawingClassifier("quickdraw", with_gap_bit=False).to(DEVICE).eval()
m_c = DrawingClassifier("quickdraw", with_gap_bit=True).to(DEVICE).eval()
x = torch.randn(N, 100, 5, device=DEVICE)
y = torch.randint(0, 10, (N,), device=DEVICE)

res = {}
for arm, model in [("A", m_ab), ("B", m_ab), ("C", m_c)]:
    cond = "block5-30"
    eval_arm_condition(model, arm, x[:256], y[:256], cond, 0, 0)  # 预热不计时
    t0 = time.time()
    accs, mf = eval_arm_condition(model, arm, x, y, cond, 0, 0)
    dt = time.time() - t0
    res[arm] = {"sec_per_cell": round(dt, 1), "masked_fraction": round(mf, 4)}
    print(f"[eval-cost] arm={arm} cond={cond} n={N}: {dt:.1f}s/cell masked={mf:.4f}",
          flush=True)

# 108 格 = 3 臂 × 4 条件 × 3 模式 × 3 种子；A 臂 36 格、B/C 各 36 格
per_seed = 12 * res["A"]["sec_per_cell"] + 12 * res["B"]["sec_per_cell"] + 12 * res["C"]["sec_per_cell"]
total = 3 * per_seed
print(f"[eval-cost] extrapolation: per_seed={per_seed:.0f}s total_108_cells={total:.0f}s "
      f"({total / 60:.1f}min)", flush=True)
print("[eval-cost] note: 随机权重模型，计算量与真实 ckpt 相同（同 L/同 manual-loop 路径）",
      flush=True)
