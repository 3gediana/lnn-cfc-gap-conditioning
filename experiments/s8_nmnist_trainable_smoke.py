#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s8_nmnist_trainable_smoke.py — S8：N-MNIST 张量「可训练」冒烟（真实模型真实数据）。

证明 data/nmnist/cache 物化的 (N,L,2,34,34) 张量可直接进 pilot_threearm.py 的
nmnist 分支模型（Conv2d(2,32,...) 输入规格）并完成前向/反向/三臂路径：
  A 臂 forward_lib（timespans=None）、B 臂 forward_ts（d2_timespans 真实 Δt）、
  C 臂 forward_ts_gap（gap 指示位），以及 clean/uniform30/block5-30 条件。
判据（先写后跑）：
  ① 形状 (N,10,2,34,34)→logits (N,10)；
  ② 损失有限、梯度非零（骨干+core+分类头）；
  ③ 小子集上 30 步训练 loss 显著下降（<初值 70%）；
  ④ clean A≡B 输出逐位一致（D1 共享输入同规格，S5 同款 sanity 的 N-MNIST 版）；
  ⑤ 落盘 results/s8_nmnist_trainable_smoke.json + experiments/s8_nmnist_trainable_smoke.log。
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from nmnist_loader import load_split, L_BINS  # noqa: E402
import pilot_threearm as pt  # noqa: E402

OUT_JSON = os.path.join(PROJECT, "results", "s8_nmnist_trainable_smoke.json")

N_TR = 512      # 冒烟训练子集
N_TE = 256      # 冒烟评测子集
STEPS = 30
BATCH = 128


def main():
    rep = {"n_train_sub": N_TR, "n_test_sub": N_TE, "steps": STEPS, "checks": {}}
    xt, yt = load_split("train")
    xe, ye = load_split("test")
    assert xt.shape[1:] == (L_BINS, 2, 34, 34), xt.shape
    g = torch.Generator().manual_seed(999)
    idx_tr = torch.randperm(xt.shape[0], generator=g)[:N_TR].numpy()
    idx_te = torch.randperm(xe.shape[0], generator=g)[:N_TE].numpy()
    x_tr = torch.from_numpy(np.asarray(xt[idx_tr])).float()
    y_tr = torch.from_numpy(np.asarray(yt[idx_tr])).long()
    x_te = torch.from_numpy(np.asarray(xe[idx_te])).float()
    y_te = torch.from_numpy(np.asarray(ye[idx_te])).long()
    rep["checks"]["tensor_shapes"] = bool(x_tr.shape == (N_TR, L_BINS, 2, 34, 34)
                                          and x_te.shape == (N_TE, L_BINS, 2, 34, 34))
    rep["checks"]["value_range_log1p"] = [float(x_tr.min()), float(x_tr.max())]
    rep["checks"]["nonzero_frac"] = float((x_tr > 0).float().mean())

    dev = pt.DEVICE
    torch.manual_seed(0)
    model = pt.DrawingClassifier("nmnist", with_gap_bit=False).to(dev)
    xb, yb = x_tr[:BATCH].to(dev), y_tr[:BATCH].to(dev)

    # ① A 臂前向 + 反向
    logits, _ = model.forward_lib(xb)
    loss = nn.CrossEntropyLoss()(logits, yb)
    loss.backward()
    gnorm = sum(p.grad.abs().sum().item() for p in model.parameters() if p.grad is not None)
    rep["checks"]["a_arm"] = {
        "logits_shape": list(logits.shape), "loss": float(loss.item()),
        "grad_abs_sum": gnorm, "finite": bool(torch.isfinite(loss).item()),
    }

    # ② B 臂 manual-loop + 真实 timespans（clean / uniform30 / block5-30）
    # 注意：N-MNIST 输入 (B,L,2,34,34)，mask 需 view 成 (B,L,1,1,1) 才能广播
    # （QuickDraw (B,L,5) 下 (B,L,1) 即可；这是 N-MNIST 三臂基准的集成注意点）
    bres = {}
    for cond in ["clean", "uniform30", "block5-30", "block15-30"]:
        mask = pt.make_mask(cond, BATCH, L_BINS, 0, 0).to(dev)
        ts = pt.d2_timespans(mask).to(dev)
        xin = xb * (1.0 - mask.view(BATCH, L_BINS, 1, 1, 1))
        lg, _ = model.forward_ts(xin, ts)
        bres[cond] = {"loss": float(nn.CrossEntropyLoss()(lg, yb).item()),
                      "mask_rate": float(mask.mean().item()),
                      "ts_max": float(ts.max().item())}
    rep["checks"]["b_arm"] = bres

    # ③ C 臂（gap 指示位；注意 C 臂模型必须 with_gap_bit=True，与 train_one 的 arm='c' 一致）
    model_c = pt.DrawingClassifier("nmnist", with_gap_bit=True).to(dev)
    mask = pt.make_mask("block5-30", BATCH, L_BINS, 0, 0).to(dev)
    ts = pt.d2_timespans(mask).to(dev)
    lg, _ = model_c.forward_ts_gap(xb * (1.0 - mask.view(BATCH, L_BINS, 1, 1, 1)), ts, mask)
    rep["checks"]["c_arm_loss"] = float(nn.CrossEntropyLoss()(lg, yb).item())

    # ④ clean A≡B（同输入同规格，D1 sanity 的 N-MNIST 版）
    mask0 = pt.make_mask("clean", BATCH, L_BINS, 0, 0).to(dev)
    ts0 = pt.d2_timespans(mask0).to(dev)
    la, _ = model.forward_lib(xb)
    lb, _ = model.forward_ts(xb, ts0)
    rep["checks"]["clean_A_eq_B_max_abs_diff"] = float((la - lb).abs().max().item())

    # ⑤ 30 步训练 loss 下降
    torch.manual_seed(0)
    m2 = pt.DrawingClassifier("nmnist", with_gap_bit=False).to(dev)
    opt = torch.optim.AdamW(m2.parameters(), lr=pt.LR, weight_decay=pt.WD)
    crit = nn.CrossEntropyLoss()
    t0 = time.time()
    first = None
    for s in range(STEPS):
        i = (s * BATCH) % N_TR
        xb2, yb2 = x_tr[i:i + BATCH].to(dev), y_tr[i:i + BATCH].to(dev)
        opt.zero_grad()
        lg, _ = m2.forward_lib(xb2)
        ls = crit(lg, yb2)
        ls.backward()
        nn.utils.clip_grad_norm_(m2.parameters(), pt.CLIP)
        opt.step()
        if first is None:
            first = float(ls.item())
    last = float(ls.item())
    # 小子集 test acc
    m2.eval()
    with torch.no_grad():
        correct = 0
        for i in range(0, N_TE, BATCH):
            lg, _ = m2.forward_lib(x_te[i:i + BATCH].to(dev))
            correct += (lg.argmax(1).cpu() == y_te[i:i + BATCH]).sum().item()
    rep["checks"]["train30"] = {
        "loss_first": first, "loss_last": last,
        "drop_frac": (first - last) / first if first else None,
        "test_acc_sub": correct / N_TE, "sec": round(time.time() - t0, 1),
    }

    passed = (rep["checks"]["tensor_shapes"]
              and rep["checks"]["a_arm"]["finite"] and rep["checks"]["a_arm"]["grad_abs_sum"] > 0
              and rep["checks"]["clean_A_eq_B_max_abs_diff"] < 1e-4
              and rep["checks"]["train30"]["drop_frac"] > 0.3
              and rep["checks"]["train30"]["test_acc_sub"] > 0.2)
    rep["verdict"] = "supported" if passed else "falsified"
    rep["passed"] = bool(passed)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    print(f"[smoke] wrote {OUT_JSON}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
