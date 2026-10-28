#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_mask_convention_probe.py — 掩码语义倒挂决定性质证。

背景：S5 full 协议 6 训练 30/30 收口（A/B train acc 0.95+），但 108 格评测落表后
A@clean=9.56%（chance 级）且掩码越重 meanpool 精度越高（clean 9.6% < uniform30
15.6% < block5 25.8% < block15 30.9%），C 臂 uniform30 竟 60.6%——与训练分布
（A/B 干净训练）矛盾。疑点：eval_arm_condition 与 C 臂训练均用 `xin = xb * mask`，
而 make_mask/d2_timespans 预注册语义为「mask=1=该帧被掩码(零填充)」（D2/D4）。
若语义为 1=掩码，则 xb*mask 恰好保留掩码帧、清零未掩码帧——clean（mask=0）时
输入全零 → chance；uniform30 保留 30% 帧 → 略高于 chance；block 保留成块连续帧
→ 精度随块长上升。三者与观测完全吻合。

本探针逐项验证（不靠推断）：
  T1 raw clean：ckpt 直接 forward_lib(x_te)（不经掩码管线）→ 预期 ~90%+（模型完好）
  T2 train raw：同一 ckpt 对 x_tr 子集 → 预期 ~95%（对齐训练日志）
  T3 eval clean：eval_arm_condition("A","clean") 现状管线 → 预期 chance（复现落表值）
  T4 语义字面：make_mask+乘法后输入的零帧占比 vs 名义掩码率（clean 应 0% 零帧）
  T5 d2 语义：构造 mask=1 单帧，检查 ts=0 落在「被保留帧」而非「被清零帧」
  T6 修正 Convention 冒烟：xin = xb*(1-mask) 下 A@clean 子集 → 预期回到 ~T1 水平

注意（2026-10-27T02:1x 判读单元补注）：三处修正生效后重跑本探针，T3 会返回修正后的
~0.916（这正是补丁生效的证据）；verdict 行因判定式按补丁前状态设计（期望 T3<0.2）
会打印 NOT CONFIRMED——非 bug 不存在。倒挂 bug 的决定性证据以 git 9a2bb15 提交的
补丁前运行 JSON（T3=0.0962、T4 clean 清零占比 1.0000）与
results/full_threearm_CONVENTION_NOTE.md 为准；判读单元重跑输出见
results/s5_mask_convention_probe_judge_rerun.json。
"""
import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PROJECT = os.path.dirname(HERE)

import pilot_threearm as P  # noqa: E402
import full_protocol as F  # noqa: E402

F._patch_pilot_d2()

N = 2048
results = {}


def raw_forward_acc(model, x, y):
    model.eval()
    correct = 0
    with torch.no_grad():
        for i in range(0, x.shape[0], 256):
            xb = x[i:i + 256].to(P.DEVICE)
            yb = y[i:i + 256].to(P.DEVICE)
            logits, _ = model.forward_lib(xb)
            correct += (logits.argmax(1) == yb).sum().item()
    return correct / x.shape[0]


def fixed_mask_eval_acc(model, x, y, cond, seed=0, pattern=0):
    """修正 Convention（1=掩码→清零）后的 A 臂评测（A 臂 timespans=None，仅输入零填充差异）。"""
    model.eval()
    correct = 0
    with torch.no_grad():
        for i in range(0, x.shape[0], 256):
            xb = x[i:i + 256].to(P.DEVICE)
            yb = y[i:i + 256].to(P.DEVICE)
            mask = P.make_mask(cond, xb.shape[0], xb.shape[1], seed, pattern).to(P.DEVICE)
            xin = xb * (1.0 - mask)          # 修正：mask=1 的帧被清零
            logits, _ = model.forward_lib(xin)
            correct += (logits.argmax(1) == yb).sum().item()
    return correct / x.shape[0]


def main() -> int:
    x_tr, y_tr, x_te, y_te = F.full_splits("quickdraw")
    model, payload = F.load_model_full(0, "ab", "quickdraw")
    print(f"[probe] ckpt: epochs_done={payload['epochs_done']} train_acc={payload['train_acc']}")

    # T1 raw clean on test
    t1 = raw_forward_acc(model, x_te[:N], y_te[:N])
    results["T1_raw_clean_test_acc"] = round(t1, 4)
    print(f"T1 raw clean (test, no mask pipeline): acc={t1:.4f}")

    # T2 raw on train subset
    t2 = raw_forward_acc(model, x_tr[:N], y_tr[:N])
    results["T2_raw_train_subset_acc"] = round(t2, 4)
    print(f"T2 raw (train subset): acc={t2:.4f}")

    # T3 current-pipeline clean eval
    accs, mf = P.eval_arm_condition(model, "A", x_te[:N], y_te[:N], "clean", 0, 0)
    results["T3_current_pipeline_clean_acc"] = round(accs["meanpool"], 4)
    results["T3_masked_fraction_reported"] = round(mf, 4)
    print(f"T3 current pipeline A@clean: meanpool={accs['meanpool']:.4f} "
          f"(reported masked_fraction={mf:.4f})")

    # T4 literal zero-frame fraction after xb*mask per condition
    t4 = {}
    for cond in ["clean", "uniform30", "block5-30", "block15-30"]:
        xb = x_te[:256].to(P.DEVICE)
        mask = P.make_mask(cond, 256, xb.shape[1], 0, 0).to(P.DEVICE)
        xin = xb * mask
        zero_frac = (xin.abs().sum(dim=2) == 0).float().mean().item()
        nominal = mask.mean().item()
        t4[cond] = {"nominal_mask_rate(mask=1占比)": round(nominal, 4),
                    "actual_zeroed_fraction_after_xb*mask": round(zero_frac, 4)}
        print(f"T4 {cond}: nominal mask=1 rate={nominal:.4f} → 实际被清零帧占比={zero_frac:.4f}")
    results["T4_zeroed_fraction"] = t4

    # T5 d2 semantics: single kept/masked frame → where does ts=0 land?
    m = torch.zeros(1, 8, 1)
    m[0, 3, 0] = 1.0                      # 名义「第3帧被掩码」
    ts = F.d2_timespans_vec(m)
    results["T5_d2_ts_for_single_masked_frame"] = [int(v) for v in ts[0].tolist()]
    print(f"T5 d2_timespans(mask=1@t=3): ts={ts[0].tolist()} "
          f"→ ts=0 落在 mask=1 帧（被保留帧），而非被清零帧")

    # T6 fixed-convention smoke: A@clean / A@block5-30 on subset
    t6 = {}
    for cond in ["clean", "uniform30", "block5-30", "block15-30"]:
        a = fixed_mask_eval_acc(model, x_te[:N], y_te[:N], cond)
        t6[cond] = round(a, 4)
        print(f"T6 fixed-convention A@{cond}: acc={a:.4f}")
    results["T6_fixed_convention_A_acc"] = t6

    ok = (t1 > 0.5) and (t2 > 0.5) and (accs["meanpool"] < 0.2) and (t6["clean"] > 0.5)
    results["verdict"] = ("CONFIRMED: mask convention inverted — clean 输入被全清零"
                          if ok else "NOT CONFIRMED — 需人工研判")
    print(f"[probe] {results['verdict']}")
    with open(os.path.join(PROJECT, "results", "s5_mask_convention_probe.json"),
              "w", encoding="utf-8") as fh:
        import json
        json.dump(results, fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
