#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""operator_bench.py — S5-full-protocol 第六单元：CfC/液态单元算子基准（fb-ab50d0ec9f）。

动机（用户反馈「先优化算子再跑实验」，2026-10-27T01:28 生效至 11-03）：
  在继续任何批量训练前，先对本课题科学路径上的算子（ncps 0.0.2 的 CfC/液态单元
  实现 + 本仓 pilot_threearm.py / full_protocol.py 调用路径）做数值稳定性与
  效率基准，定位问题、能修的修（数值恒等优先）、修不掉的记算子墙（F8）。

本脚本纪律：
  - 禁止 30epoch 批量训练；E6 训练步构成只跑个位数 step 做计时，不落任何 ckpt、
    不写 progress、不动 experiments/ckpt/ 与 results/full_* 既有产物；
  - 已跑 ckpt 全部保留；一切结论标注「基于旧算子（ncps 0.0.2；倒挂 Convention
    已修正、不影响 A/B 干净训练）」；
  - 所有数字实测落盘 results/operator_bench.json，MD 由本单元据 JSON 撰写。

覆盖（单元指令①）：
  N0 Convention 现状锚定（修正后 clean A≡B + 名义/实际掩码率）
  N1 τ-tie 覆写点 ltc_cell.py:223-244（LTC 路径 elapsed_time=0 → cm/0）
  N2 scale-state 爆炸风险（harvest 2610.15139：数值爆炸 17→3.9e3）实测
  N3 dt=0 零输入收缩性（S0 u2_probe.json 断言②的真实尺寸扩展：128→256+训练后权重）
  N4 梯度量级（‖∇_ts L‖ vs dt、时间门饱和、参数组梯度、掩码帧输入梯度）
  N5 B>1 timespans RuntimeError 边界（cfc.py:166 squeeze）+ manual-loop 恒等复验
  E1 d2 向量化前后代价（B=128/256，GPU）
  E2 108 格评测 167.3s 构成（A/B/C 单格成本 + 分段计时 profile mirror）
  E3 逐 batch .item() 同步开销（候选修复 FIX-1 的量化依据）
  E4 manual-loop 逐样本 vs 批式/库路径代价
  E5 108 格构成模型 vs 盘上实测 167.3s + 6 格真实样本验证
  E6 训练步构成（benchmark only）

用法：G:/ai/python11/python.exe experiments/operator_bench.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import torch
import torch.nn as nn

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PROJECT = os.path.dirname(HERE)

import pilot_threearm as P          # noqa: E402  协议同源代码

_ORIG_D2 = P.d2_timespans           # patch 前快照的循环版（E1 计时/恒等基准）
import full_protocol as F           # noqa: E402  full_splits / d2_timespans_vec

# 与生产路径一致：full_protocol.main() 会把 pilot 的 d2_timespans patch 成向量化版，
# 本基准复现该 patch（否则 P.eval_arm_condition 走补丁前 CPU 循环版，计时无意义）。
F._patch_pilot_d2()

DEV = P.DEVICE
RESULTS = os.path.join(PROJECT, "results")
OUT_JSON = os.path.join(RESULTS, "operator_bench.json")
CKPT_AB = os.path.join(P.CKPT_DIR, "full_quickdraw_seed0_ab.pt")

R = {"schema": "operator-bench/v1", "stage": "S5-full-protocol",
     "purpose": "CfC/液态单元算子基准（fb-ab50d0ec9f 先优化算子再跑实验）",
     "sections": {}}


def _rec(name, payload, t0):
    R["sections"][name] = payload
    R["sections"][name]["sec"] = round(time.time() - t0, 2)
    print(f"[bench] {name}: done ({R['sections'][name]['sec']}s)", flush=True)


def _finite(t: torch.Tensor):
    return bool(torch.isfinite(t).all().item())


def _load_trained_ab():
    payload = torch.load(CKPT_AB, map_location=DEV, weights_only=False)
    model = P.DrawingClassifier("quickdraw", with_gap_bit=False)
    model.load_state_dict(payload["state_dict"])
    return model.to(DEV).eval(), payload


# ==================== N0：Convention 现状锚定 ====================

def sec_n0(x_te, y_te):
    t0 = time.time()
    model, payload = _load_trained_ab()
    n = 512
    xb, yb = x_te[:n].to(DEV), y_te[:n].to(DEV)
    with torch.no_grad():
        accA, _ = P.eval_arm_condition(model, "A", xb, yb, "clean", 0, 0)
        accB, _ = P.eval_arm_condition(model, "B", xb, yb, "clean", 0, 0)
        # 模型级 A≡B 数值差（clean，ts=1 vs 库 None）
        mask_clean = P.make_mask("clean", n, xb.shape[1], 0, 0).to(DEV)
        xin = xb * (1.0 - mask_clean)
        _, out_a = model.forward_lib(xin)
        ts1 = torch.ones(n, xb.shape[1], device=DEV)
        _, out_b = model.forward_ts(xin, ts1)
        max_d = (out_a.double() - out_b.double()).abs().max().item()
        # 名义 vs 实际掩码率（Convention 修正后）
        mf5 = P.eval_arm_condition(model, "B", xb, yb, "block5-30", 0, 0)[1]
        mfu = P.eval_arm_condition(model, "B", xb, yb, "uniform30", 0, 0)[1]
        # 倒挂 bug 探针量：clean 条件下输入被修改的帧比例（修正后应=0；倒挂态下≈1）
        modified = (xin != xb).any(dim=2).float().mean().item()
        # 原始数据结构性零帧（短序列 zero-padding，与 Convention 无关的背景量）
        raw_zero = (xb == 0).all(dim=2).float().mean().item()
    _rec("N0_convention_anchor", {
        "trained_ckpt": os.path.relpath(CKPT_AB, PROJECT),
        "ckpt_train_acc": payload.get("train_acc"),
        "n": n,
        "A_clean_acc": accA["meanpool"], "B_clean_acc": accB["meanpool"],
        "A_equals_B": accA["meanpool"] == accB["meanpool"],
        "clean_armB_vs_armA_max_abs_diff": max_d,
        "clean_input_modified_frame_fraction": modified,
        "raw_data_structurally_zero_frame_fraction": raw_zero,
        "block5-30_realized_masked_fraction": round(mf5, 4),
        "uniform30_realized_masked_fraction": round(mfu, 4),
        "note": "修正后 Convention：mask=1=掩码(清零)，clean 下输入修改帧=0（倒挂态下≈1，"
                "即第五单元 T4 探测量）；A@clean≈0.91 与 T1（ckpt 直推 0.9160）互证；"
                "原始数据 ~54% 结构零帧=短序列 padding，与 Convention 无关",
    }, t0)


# ==================== N1：τ-tie 覆写点（LTC 路径） ====================

def sec_n1():
    t0 = time.time()
    from ncps.torch import LTC
    torch.manual_seed(0)
    rnn = LTC(16, 32).to("cpu").eval()          # 与 CfC 无关的 LTC 路径（本协议未使用）
    x = torch.randn(1, 5, 16)                   # B=1：B>1 时 cfc/ltc.py 同款 squeeze 边界（见 N5）
    out = {}
    for dt in [0.0, 1e-8, 1e-4, 1.0]:
        ts = torch.full((1, 5), float(dt))
        with torch.no_grad():
            o, h = rnn(x, timespans=ts)
        out[f"dt_{dt:g}"] = {"finite": _finite(o) and _finite(h),
                             "max_abs_out": float(o.abs().max()),
                             "max_abs_hidden": float(h.abs().max())}
    # 本协议实际路径（CfC default 模式）ts=0 是否受影响：ltc_cell.py:223-244 的
    # cm_t = cm/(elapsed_time/ode_unfolds) 只存在于 LTC；CfC 无除零（N3 实测）。
    from ncps.torch import CfC
    torch.manual_seed(0)
    cfc = CfC(16, 32).to("cpu").eval()
    xc = torch.randn(1, 5, 16)                  # B=1（B>1 崩溃见 N5，非同因）
    with torch.no_grad():
        oc, hc = cfc(xc, timespans=torch.zeros(1, 5))
    _rec("N1_tau_tie_ltc", {
        "ltc_path": out,
        "cfc_default_ts0_finite": _finite(oc) and _finite(hc),
        "cfc_default_ts0_max_abs_out": float(oc.abs().max()),
        "wall": "ltc_cell.py:223-244 cm_t=softplus(cm)/(elapsed_time/ode_unfolds)："
                "elapsed_time=0 → 除零 → inf/inf=NaN（LTC 路径硬墙）",
        "on_scientific_path": False,
        "path_note": "本协议用非 wiring CfC（CfCCell default 模式，cfc_cell.py:136-166，"
                     "无 cm_t 除法），LTC 不在科学路径上；墙为潜在（wired/LTC 用法才会踩）",
        "guard_recipe": "若未来用 LTC+dt=0：wrapper 内 clamp elapsed_time>=1e-6 "
                        "（实测 dt=1e-4 有限；代价=语义近似，需显式标注）",
    }, t0)


# ==================== N2：scale-state 爆炸风险 ====================

def sec_n2(model):
    t0 = time.time()
    cell = model.core.rnn_cell                      # 真实尺寸 CfCCell(128→256, default)
    from ncps.torch.cfc_cell import CfCCell
    torch.manual_seed(0)
    pure = CfCCell(128, 256, mode="pure", backbone_units=128,
                   backbone_layers=1).to(DEV).eval()

    def scaled_feedback(c, scales, steps=100):
        """scale-state 反馈（harvest 2610.15139 失效模式）：状态按 s 放大后回馈为 hx。"""
        res = {}
        zero_in = torch.zeros(64, 128, device=DEV)
        ts1 = torch.tensor(1.0, device=DEV)
        for s in scales:
            h = torch.zeros(64, 256, device=DEV)
            mx = 0.0
            with torch.no_grad():
                for _ in range(steps):
                    _, h = c(zero_in, s * h, ts1)
                    mx = max(mx, float(h.abs().max()))
            res[f"scale_{s:g}"] = {"max_abs_hidden_over_steps": mx,
                                   "finite": bool(torch.isfinite(h).all().item())}
        return res

    default_res = scaled_feedback(cell, [1.0, 10.0, 100.0, 1e4])
    pure_res = scaled_feedback(pure, [1.0, 10.0, 100.0, 1e4])

    # 全模型输入尺度（LN backbone 兜底）
    xb = torch.randn(256, 100, 5, device=DEV) * 3.0
    scale_res = {}
    with torch.no_grad():
        for s in [1.0, 10.0, 100.0]:
            logits, out = model.forward_lib(xb * s)
            scale_res[f"input_x_{s:g}"] = {"max_abs_out": float(out.abs().max()),
                                           "finite": _finite(out)}
    _rec("N2_scale_state", {
        "cfc_default_scaled_state_feedback": default_res,
        "cfc_pure_scaled_state_feedback": pure_res,
        "full_model_input_scale": scale_res,
        "harvest_ref": "2610.15139（scale-state 反馈数值爆炸 17→3.9e3、yoke 仅挽回 "
                       "1.82/5.39 nats，harvest INDEX 20261026-074512 已消化）",
        "verdict": "本协议路径（CfC default 模式 + LN backbone）状态结构性有界："
                   "default 模式 new_hidden=ff1*(1-t_interp)+t_interp*ff2 且 ff1/ff2=tanh "
                   "⇒ |h|≤1；pure 模式 -A*exp(-ts*(|w_tau|+|ff1|))*ff1+A 对大 |ff1| 指数"
                   "衰减回 A ⇒ 亦有界。scale-state 爆炸模式在本机 ncps 0.0.2 CfC 上不复现",
        "on_scientific_path_risk": False,
    }, t0)


# ==================== N3：dt=0 零输入收缩性（真实尺寸） ====================

def sec_n3(model, x_te):
    t0 = time.time()
    B = 128
    xb = x_te[:B].to(DEV)
    with torch.no_grad():
        # (i) cell 级零输入 dt=0（h0=0 与随机初态）。收缩判据用逐样本相对变化
        #（u2 a2 同口径：mean_i ||Δh_i||/||h_i||；batch 总 Frobenius 会被不同样本的
        #  不同不动点主导，不是收缩性的正确度量——首版踩过此坑，勿回退）
        cell = model.core.rnn_cell
        zero_in = torch.zeros(B, 128, device=DEV)
        for tag, h0 in [("h0_zero", torch.zeros(B, 256, device=DEV)),
                        ("h0_randn", torch.randn(B, 256, device=DEV))]:
            h = h0.clone()
            rels, dabs, mx = [], [], 0.0
            for step in range(100):
                _, h_new = cell(zero_in, h, torch.tensor(0.0, device=DEV))
                dabs.append(float((h_new - h).norm(dim=1).mean()))
                if step > 0 or tag == "h0_randn":      # h0=0 首步分母为 0，跳过
                    rels.append(float(((h_new - h).norm(dim=1)
                                       / (h.norm(dim=1) + 1e-6)).mean()))
                h = h_new
                mx = max(mx, float(h.abs().max()))
            R["sections"].setdefault("N3_dt0_contraction", {})[f"cell_zeroinput_{tag}"] = {
                "per_sample_abs_change_first10": sum(dabs[:10]) / 10,
                "per_sample_abs_change_last10": sum(dabs[-10:]) / 10,
                "per_sample_rel_change_first10": sum(rels[:10]) / 10,
                "per_sample_rel_change_last10": sum(rels[-10:]) / 10,
                "contracting": (sum(rels[-10:]) / 10) < (sum(rels[:10]) / 10),
                "max_abs_hidden": mx, "finite": bool(torch.isfinite(h).all().item())}
        # (ii) 模型级全掩码（xin=0 → backbone(0) 常数特征）dt=0 100 步
        mask_all = torch.ones(B, xb.shape[1], 1, device=DEV)
        xin = xb * (1.0 - mask_all)
        feats = model.features(xin)
        ts0 = torch.zeros(B, xb.shape[1], device=DEV)
        h_prev = torch.zeros(B, model.core.state_size, device=DEV)
        h = h_prev.clone()
        rels, dabs, mx = [], [], 0.0
        for t in range(xb.shape[1]):
            _, h = model.core.rnn_cell.forward(feats[:, t], h_prev, ts0[:, t].unsqueeze(1))
            dabs.append(float((h - h_prev).norm(dim=1).mean()))
            if t > 0:
                rels.append(float(((h - h_prev).norm(dim=1)
                                   / (h_prev.norm(dim=1) + 1e-6)).mean()))
            h_prev = h
            mx = max(mx, float(h.abs().max()))
        # (iii) 间隙恢复：50 步 dt=0（零输入）后 1 真实帧 dt=51
        h = torch.zeros(B, model.core.state_size, device=DEV)
        with torch.no_grad():
            for _ in range(50):
                _, h = cell(zero_in, h, torch.tensor(0.0, device=DEV))
            feats_real = model.features(xb)
            _, h_gap = cell(feats_real[:, 0], h, torch.tensor(51.0, device=DEV))
        res = R["sections"]["N3_dt0_contraction"]
        res["model_all_masked_dt0_100steps"] = {
            "max_abs_hidden": mx, "finite": bool(torch.isfinite(h).all().item()),
            "per_sample_abs_change_first10": sum(dabs[:10]) / 10,
            "per_sample_abs_change_last10": sum(dabs[-10:]) / 10,
            "per_sample_rel_change_first10": sum(rels[:10]) / 10,
            "per_sample_rel_change_last10": sum(rels[-10:]) / 10,
            "contracting": (sum(rels[-10:]) / 10) < (sum(rels[:10]) / 10)}
        res["gap_recovery_dt51_after_50_dt0"] = {
            "max_abs_hidden_after": float(h_gap.abs().max()),
            "finite": _finite(h_gap)}
        res["pass_criteria"] = ("finite + max|h|≤2 + 逐样本收缩（后10步 mean rel change "
                                "< 前10步）；u2_probe a2 迷你尺寸 16→32 随机权重的真实尺寸扩展")
        res["u2_probe_ref"] = ("S0 断言②（results/u2_probe.json a2）为迷你尺寸 16→32 随机权重；"
                               "本单元扩展至真实尺寸 128→256 + 训练后权重")
        res["overall_pass"] = all([
            res["cell_zeroinput_h0_zero"]["finite"], res["cell_zeroinput_h0_randn"]["finite"],
            res["cell_zeroinput_h0_zero"]["contracting"], res["cell_zeroinput_h0_randn"]["contracting"],
            res["model_all_masked_dt0_100steps"]["finite"],
            res["model_all_masked_dt0_100steps"]["contracting"],
            res["gap_recovery_dt51_after_50_dt0"]["finite"],
            max(res["cell_zeroinput_h0_zero"]["max_abs_hidden"],
                res["cell_zeroinput_h0_randn"]["max_abs_hidden"],
                res["model_all_masked_dt0_100steps"]["max_abs_hidden"]) <= 2.0])
    _rec("N3_dt0_contraction", R["sections"]["N3_dt0_contraction"], t0)


# ==================== N4：梯度量级 ====================

def sec_n4(model, x_te, y_te):
    t0 = time.time()
    B = 128
    xb, yb = x_te[:B].to(DEV), y_te[:B].to(DEV)
    L = xb.shape[1]
    cell = model.core.rnn_cell
    sweep = {}
    for dt in [0.0, 1.0, 2.0, 5.0, 15.0, 30.0, 101.0]:
        ts = torch.full((B, L), float(dt), device=DEV, requires_grad=True)
        logits, _ = model.forward_ts(xb, ts)
        loss = nn.CrossEntropyLoss()(logits, yb)
        loss.backward()
        g = ts.grad
        # 时间门饱和诊断（用 cell 自身参数复算首步门控 pre-activation）
        with torch.no_grad():
            feats0 = model.features(xb)[:, 0]
            x = torch.cat([feats0, torch.zeros(B, cell.hidden_size, device=DEV)], dim=1)
            x = cell.backbone(x)
            z = cell.time_a(x) * dt + cell.time_b(x)
            sat = float((z.abs() > 4).float().mean())
        pn = {}
        pfin = True
        for n_, p in model.named_parameters():
            if p.grad is not None:
                pn[n_] = round(float(p.grad.norm()), 6)
                pfin = pfin and bool(torch.isfinite(p.grad).all())
        sweep[f"dt_{dt:g}"] = {
            "loss": round(float(loss.detach()), 6),
            "grad_ts_norm": round(float(g.norm()), 8),
            "grad_ts_max_abs": round(float(g.abs().max()), 8),
            "grad_ts_frac_gt_1e-4": round(float((g.abs() > 1e-4).float().mean()), 6),
            "time_gate_saturation_frac_absz_gt_4": round(sat, 6),
            "param_grads_all_finite": pfin,
            "param_grad_norms": pn,
        }
        model.zero_grad()
    # 真实 D2 模式（block5-30：dt 多为 1、掩码 run 内 0、run 末 gap_len+1≤6）
    mask = P.make_mask("block5-30", B, L, 0, 0).to(DEV)
    ts_real = P.d2_timespans(mask).to(DEV).requires_grad_(True)
    logits, _ = model.forward_ts(xb, ts_real)
    nn.CrossEntropyLoss()(logits, yb).backward()
    pfin = all(bool(torch.isfinite(p.grad).all()) for p in model.parameters() if p.grad is not None)
    assert ts_real.grad is not None
    with torch.no_grad():
        vals, cnts = torch.unique(ts_real.detach(), return_counts=True)
        real_dt_hist = {str(float(v)): int(c) for v, c in zip(vals, cnts)}
    realistic = {
        "dt_value_histogram": real_dt_hist,
        "grad_ts_norm": round(float(ts_real.grad.norm()), 8),
        "grad_ts_max_abs": round(float(ts_real.grad.abs().max()), 8),
        "param_grads_all_finite": pfin,
    }
    model.zero_grad()
    # 掩码帧输入梯度（结构性零）
    xin = xb.clone().requires_grad_(True)
    ts = P.d2_timespans(mask).to(DEV)
    logits, _ = model.forward_ts(xin * (1.0 - mask), ts)
    nn.CrossEntropyLoss()(logits, yb).backward()
    gx = xin.grad
    masked_grad = float(gx[mask[:, :, 0] > 0.5].abs().mean()) if (mask > 0.5).any() else None
    unmasked_grad = float(gx[mask[:, :, 0] <= 0.5].abs().mean())
    _rec("N4_gradients", {
        "constant_dt_sweep": sweep,
        "realistic_d2_pattern_block5-30": realistic,
        "masked_frame_input_grad_mean_abs": masked_grad,
        "unmasked_frame_input_grad_mean_abs": unmasked_grad,
        "note": "harvest 20261025-153306-5e00647e 的 ‖∇_τL‖>1e-4 等数字为云端估计，"
                "本表为本地实测（S5 判据只认实测）。恒定 dt 压力测试：dt≥15 起 ∇_ts 爆炸"
                "（dt=101 时参数梯度全 Inf）——门控饱和移除收缩混合后循环雅可比放大；"
                "真实 D2 模式 dt≤6 且非常量，梯度有限（见 realistic 块）",
    }, t0)


# ==================== N5：B>1 timespans 边界 ====================

def sec_n5(model, x_te):
    t0 = time.time()
    xb = x_te[:4].to(DEV)
    mask = P.make_mask("block5-30", 4, xb.shape[1], 0, 0).to(DEV)
    xin = xb * (1.0 - mask)
    ts = P.d2_timespans(mask).to(DEV)
    feats = model.features(xin)
    shapes = {}
    with torch.no_grad():
        try:
            model.core(feats, timespans=ts)
            shapes["batched_(4,L)"] = {"ok": True}
        except RuntimeError as exc:
            shapes["batched_(4,L)"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        for tag, ff, tt in [
            ("library_(1,L)", feats[:1], ts[:1]),
            ("library_(1,L,1)", feats[:1], ts[:1].unsqueeze(-1)),
            ("batchless_(L,C)+(L,)", feats[0], ts[0]),
            ("batchless_(L,C)+(L,1)", feats[0], ts[0].unsqueeze(-1)),
        ]:
            try:
                o, h = model.core(ff, timespans=tt)
                shapes[tag] = {"ok": True, "finite": _finite(o)}
            except RuntimeError as exc:
                shapes[tag] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        # manual-loop vs 库 B=1 逐样本恒等（真实尺寸+训练后权重）
        max_d = 0.0
        for r in range(4):
            out_lib, _ = model.core(feats[r:r + 1], timespans=ts[r:r + 1])
            _, out_man = model.forward_ts(xin[r:r + 1], ts[r:r + 1])
            max_d = max(max_d, (out_lib.double() - out_man.double()).abs().max().item())
    _rec("N5_batched_timespans_boundary", {
        "shape_matrix": shapes,
        "manual_loop_vs_library_B1_max_abs_diff": max_d,
        "root_cause": "cfc.py:166 ts=timespans[:, t].squeeze()：B>1 时得 (B,)，"
                      "与 cell 内 (B,H) 广播失败；B=1 squeeze 成标量故可用",
        "mitigation": "协议 B/C 臂走 manual-loop（u2_probe 实测与库 B=1 差 3.28e-07；"
                      "本单元真实尺寸复验如上）——不改 site-packages 共享库",
    }, t0)


# ==================== E1：d2 向量化前后代价 ====================

def sec_e1():
    t0 = time.time()
    res = {}
    for B in [128, 256]:
        torch.manual_seed(0)
        m = (torch.rand(B, 100, 1, device=DEV) < 0.3).float()
        ref = _ORIG_D2(m).cpu()                  # patch 前快照的循环版（恒等基准）
        # 循环版（GPU 上逐元素索引同步，代价即补丁前形态）
        torch.cuda.synchronize()
        t1 = time.time()
        for _ in range(5):
            _ = _ORIG_D2(m)
        torch.cuda.synchronize()
        loop_ms = (time.time() - t1) / 5 * 1000
        torch.cuda.synchronize()
        t2 = time.time()
        for _ in range(20):
            got = F.d2_timespans_vec(m)
        torch.cuda.synchronize()
        vec_ms = (time.time() - t2) / 20 * 1000
        res[f"B={B}"] = {"loop_ms_per_call": round(loop_ms, 3),
                         "vec_ms_per_call": round(vec_ms, 3),
                         "speedup": round(loop_ms / max(vec_ms, 1e-6), 1),
                         "identity_torch_equal": bool(torch.equal(got.cpu(), ref))}
    _rec("E1_d2_cost", {
        "per_call": res,
        "note": "循环版在 GPU 上逐元素标量索引触发逐次同步（补丁前 C 臂训练主瓶颈）；"
                "向量化版恒等（torch.equal）已由 full_protocol selftest 68 项担保",
    }, t0)


# ==================== E2/E3：评测单格成本 + 同步开销（profile mirror） ====================

def _eval_cell_profile(model, arm, x, y, cond, seed, pattern,
                       defer_sync=False, sync_sections=False, bs=256):
    """eval_arm_condition 的计时镜像（数学逐字一致；identity 由本脚本断言）。
    defer_sync=True：逐 batch 的 4 次 .item() 改为 cell 末一次同步（候选修复 FIX-1）。"""
    model.eval()
    n = x.shape[0]
    c = {"meanpool": 0, "final": 0, "gapnb": 0}
    if defer_sync:
        c = {k: torch.zeros((), dtype=torch.int64, device=DEV) for k in c}
    mf = torch.zeros((), dtype=torch.float32, device=DEV) if defer_sync else 0.0
    tot = 0
    br = {"mask_d2": 0.0, "feats": 0.0, "cell_loop": 0.0, "readout": 0.0}

    def _sync():
        if sync_sections:
            torch.cuda.synchronize()

    with torch.no_grad():
        for i in range(0, n, bs):
            xb = x[i:i + bs].to(DEV)
            yb = y[i:i + bs].to(DEV)
            t0 = time.time()
            mask = P.make_mask(cond, xb.shape[0], xb.shape[1], seed, pattern).to(DEV)
            xin = xb * (1.0 - mask)
            ts = P.d2_timespans(mask).to(DEV)
            _sync(); br["mask_d2"] += time.time() - t0
            t1 = time.time()
            feats = model.features(xin)
            _sync(); br["feats"] += time.time() - t1
            t2 = time.time()
            if arm == "A":
                out, _ = model.core(feats)
            else:
                if arm == "C":
                    feats = torch.cat([feats, mask], dim=2)
                b, l = feats.shape[0], feats.shape[1]
                h = torch.zeros((b, model.core.state_size), device=DEV)
                outs = []
                for t in range(l):
                    h_out, h = model.core.rnn_cell.forward(feats[:, t], h,
                                                           ts[:, t].unsqueeze(1))
                    outs.append(model.core.fc(h_out))
                out = torch.stack(outs, dim=1)
            _sync(); br["cell_loop"] += time.time() - t2
            t3 = time.time()
            logits = model.classifier(torch.mean(out, dim=1))
            w = P.gap_neighborhood_weights(mask)
            pooled = (out * w.unsqueeze(-1)).sum(dim=1) / w.sum(dim=1, keepdim=True)
            if defer_sync:
                c["meanpool"] += (logits.argmax(1) == yb).sum()
                c["final"] += (model.classifier(out[:, -1]).argmax(1) == yb).sum()
                c["gapnb"] += (model.classifier(pooled).argmax(1) == yb).sum()
                mf += mask.sum()
            else:
                c["meanpool"] += (logits.argmax(1) == yb).sum().item()
                c["final"] += (model.classifier(out[:, -1]).argmax(1) == yb).sum().item()
                c["gapnb"] += (model.classifier(pooled).argmax(1) == yb).sum().item()
                mf += mask.sum().item()
            tot += mask.numel()
            _sync(); br["readout"] += time.time() - t3
    if defer_sync:
        accs = {k: c[k].item() / n for k in c}
        mfv = mf.item() / max(tot, 1)
    else:
        accs = {k: v / n for k, v in c.items()}
        mfv = mf / max(tot, 1)
    return accs, mfv, br


def sec_e2e3(model_ab, x_te, y_te):
    t0 = time.time()
    torch.manual_seed(0)
    model_c = P.DrawingClassifier("quickdraw", with_gap_bit=True).to(DEV).eval()
    n = x_te.shape[0]
    # --- identity：mirror(defer=False) vs 生产 P.eval_arm_condition（n=512）---
    ident = {}
    xs, ys = x_te[:512], y_te[:512]
    for arm, mdl in [("A", model_ab), ("B", model_ab)]:
        for cond in ["clean", "block5-30"]:
            a_ref, mf_ref = P.eval_arm_condition(mdl, arm, xs, ys, cond, 0, 0)
            a_m, mf_m, _ = _eval_cell_profile(mdl, arm, xs, ys, cond, 0, 0)
            a_d, mf_d, _ = _eval_cell_profile(mdl, arm, xs, ys, cond, 0, 0, defer_sync=True)
            ident[f"{arm}/{cond}"] = {
                "accs_equal_production": a_ref == a_m, "mf_equal": mf_ref == mf_m,
                "accs_equal_defer": a_m == a_d, "mf_equal_defer": mf_m == mf_d}
    # --- 生产计时（cell 末同步；defer=False 复现现行行为）---
    prod = {}
    for arm, mdl in [("A", model_ab), ("B", model_ab), ("C", model_c)]:
        cond = "block5-30"
        _eval_cell_profile(mdl, arm, x_te[:256], y_te[:256], cond, 0, 0)   # 预热
        torch.cuda.synchronize(); t1 = time.time()
        accs, mf, _ = _eval_cell_profile(mdl, arm, x_te, y_te, cond, 0, 0)
        torch.cuda.synchronize()
        prod[arm] = {"sec_per_cell_n7500": round(time.time() - t1, 2), "accs": accs}
    # --- FIX-1 候选：defer_sync 的生产计时（B 臂 block5-30）---
    t1 = time.time()
    _eval_cell_profile(model_ab, "B", x_te, y_te, "block5-30", 0, 0, defer_sync=True)
    torch.cuda.synchronize()
    defer_sec = time.time() - t1
    # --- 分段归因（含逐段同步，总和可能大于生产计时=异步重叠被同步点破坏的证据）---
    _, _, br = _eval_cell_profile(model_ab, "B", x_te, y_te, "block5-30", 0, 0,
                                  sync_sections=True)
    _rec("E2_eval_cost_composition", {
        "identity_mirror_vs_production": ident,
        "production_sec_per_cell": {k: v["sec_per_cell_n7500"] for k, v in prod.items()},
        "production_accs_block5-30": {k: v["accs"] for k, v in prod.items()},
        "composition_108_cells_estimate_sec": round(
            36 * prod["A"]["sec_per_cell_n7500"] + 36 * prod["B"]["sec_per_cell_n7500"]
            + 36 * prod["C"]["sec_per_cell_n7500"], 1),
        "B_cell_section_breakdown_sec": {k: round(v, 2) for k, v in br.items()},
        "B_cell_defer_sync_sec": round(defer_sec, 2),
        "sync_overhead_sec": round(prod["B"]["sec_per_cell_n7500"] - defer_sec, 2),
        "sync_overhead_pct": round(100 * (prod["B"]["sec_per_cell_n7500"] - defer_sec)
                                   / max(prod["B"]["sec_per_cell_n7500"], 1e-9), 1),
        "note": "C 臂用同架构随机初始化模型（成本由结构决定，与科学结论无关）；"
                "A/B 用训练后 ckpt full_quickdraw_seed0_ab.pt",
    }, t0)


# ==================== E4：逐样本 vs 批式路径代价 ====================

def sec_e4(model_ab, x_te):
    t0 = time.time()
    n = 64
    xb = x_te[:n].to(DEV)
    mask = P.make_mask("block5-30", n, xb.shape[1], 0, 0).to(DEV)
    xin = xb * (1.0 - mask)
    ts = P.d2_timespans(mask).to(DEV)
    feats = model_ab.features(xin)
    # 库路径逐样本 B=1
    with torch.no_grad():
        for r in range(4):
            model_ab.core(feats[r:r + 1], timespans=ts[r:r + 1])
        torch.cuda.synchronize(); t1 = time.time()
        for r in range(n):
            model_ab.core(feats[r:r + 1], timespans=ts[r:r + 1])
        torch.cuda.synchronize()
        lib_ps = (time.time() - t1) / n
        # manual-loop 逐样本 B=1
        for r in range(4):
            model_ab.forward_ts(xin[r:r + 1], ts[r:r + 1])
        torch.cuda.synchronize(); t2 = time.time()
        for r in range(n):
            model_ab.forward_ts(xin[r:r + 1], ts[r:r + 1])
        torch.cuda.synchronize()
        man_ps = (time.time() - t2) / n
        # 批式 manual-loop（同 64 样本一次）
        model_ab.forward_ts(xin, ts)
        torch.cuda.synchronize(); t3 = time.time()
        model_ab.forward_ts(xin, ts)
        torch.cuda.synchronize()
        batched = time.time() - t3
    _rec("E4_per_sample_vs_batched", {
        "library_B1_per_sample_ms": round(lib_ps * 1000, 3),
        "manual_loop_B1_per_sample_ms": round(man_ps * 1000, 3),
        "batched_manual_loop_64_samples_ms": round(batched * 1000, 2),
        "extrapolated_per_sample_path_7500_sec": round(lib_ps * 7500, 1),
        "batched_speedup_vs_per_sample": round(lib_ps * n / max(batched, 1e-9), 1),
        "verdict": "逐样本路径（库 B=1 或 manual-loop B=1）单样本固定 ~ms 级 launch 开销，"
                   "7500 样本外推 ~10s 级/格且无法摊薄——协议采用批式 manual-loop 是唯一可行路径",
    }, t0)


# ==================== E5：108 格构成模型验证 ====================

def sec_e5(model_ab, x_te, y_te, comp):
    t0 = time.time()
    # 6 格真实样本（seed0，A/B × clean/block5-30 × pattern0，n=7500）
    sample = {}
    torch.cuda.synchronize(); t_start = time.time()
    for arm in ["A", "B"]:
        for cond in ["clean", "block5-30"]:
            P.eval_arm_condition(model_ab, arm, x_te, y_te, cond, 0, 0)   # 预热
            torch.cuda.synchronize(); t1 = time.time()
            P.eval_arm_condition(model_ab, arm, x_te, y_te, cond, 0, 0)
            torch.cuda.synchronize()
            sample[f"{arm}/{cond}"] = round(time.time() - t1, 2)
    torch.cuda.synchronize()
    total6 = time.time() - t_start
    actual_ref = None
    tp = os.path.join(RESULTS, "full_timing.json")
    if os.path.exists(tp):
        with open(tp, encoding="utf-8") as fh:
            actual_ref = json.load(fh).get("u5_runtime", {}).get("eval_sec")
    est6 = None
    pc = comp.get("production_sec_per_cell", {})
    if "A" in pc and "B" in pc:
        est6 = round(2 * pc["A"] + 2 * pc["B"], 1)   # A/B × clean/block5-30 各 1 格
    _rec("E5_composition_validation", {
        "six_cell_sample_sec": sample,
        "six_cell_total_sec": round(total6, 2),
        "six_cell_model_prediction_sec": est6,
        "model_estimate_108_sec": comp.get("composition_108_cells_estimate_sec"),
        "on_disk_actual_eval_sec_5th_unit": actual_ref,
        "on_disk_actual_ref": "results/full_timing.json（第五单元 108 格实测，本轮 Convention "
                              "倒挂数值作废但计时构成有效）",
        "validation": "6 格实测总和 vs 构成模型对应 6 格预测（36 格模型按 1/6 折算）",
    }, t0)


# ==================== E6：训练步构成（benchmark only，不落 ckpt） ====================

def sec_e6(x_tr, y_tr):
    t0 = time.time()
    B = P.BATCH
    xb, yb = x_tr[:B].to(DEV), y_tr[:B].to(DEV)
    out = {}
    for arm in ["ab", "c"]:
        torch.manual_seed(0)
        model = P.DrawingClassifier("quickdraw", with_gap_bit=(arm == "c")).to(DEV)
        opt = torch.optim.AdamW(model.parameters(), lr=P.LR, weight_decay=P.WD)
        crit = nn.CrossEntropyLoss()

        def fwd():
            if arm == "ab":
                logits, _ = model.forward_lib(xb)
            else:
                mask = P.make_mask("block5-30", xb.shape[0], xb.shape[1], 0, 0).to(DEV)
                xin = xb * (1.0 - mask)
                ts = P.d2_timespans(mask).to(DEV)
                logits, _ = model.forward_ts_gap(xin, ts, mask)
            return crit(logits, yb)

        def one_step():
            loss = fwd()
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), P.CLIP)
            opt.step()

        for _ in range(3):
            one_step()                                   # 预热（含 autotune）
        torch.cuda.synchronize(); t1 = time.time()
        for _ in range(8):
            one_step()
        torch.cuda.synchronize()
        step_ms = (time.time() - t1) / 8 * 1000
        # fwd/bwd 拆分（3 步，逐相同步=归因上界）
        fwd_s, bwd_s = [], []
        for _ in range(3):
            torch.cuda.synchronize(); a = time.time()
            loss = fwd()
            torch.cuda.synchronize(); b = time.time()
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), P.CLIP); opt.step()
            torch.cuda.synchronize(); cc = time.time()
            fwd_s.append(b - a); bwd_s.append(cc - b)
        out[arm] = {
            "step_ms_8steps_single_sync": round(step_ms, 2),
            "epoch_estimate_sec_333batches": round(step_ms * 333 / 1000, 1),
            "fwd_ms_with_section_sync": round(sum(fwd_s) / 3 * 1000, 2),
            "bwd_ms_with_section_sync": round(sum(bwd_s) / 3 * 1000, 2),
            "measured_epoch_sec_ref": "ab≈46-48s/ep、c≈47-53s/ep（full_run.log 实测带）",
            "note": "benchmark only：计时后即丢弃，不落 ckpt、不写 progress；"
                    "step_ms 为单次同步对的最小偏估计（预热后 8 步）",
        }
    _rec("E6_train_step_composition", out, t0)


# ==================== main ====================

def main():
    t_start = time.time()
    R["env"] = {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device": str(DEV),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "ncps": "0.0.2",
        "operator_basis": "旧算子（ncps 0.0.2；倒挂 Convention 已修正、不影响 A/B 干净训练）",
        "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    print("[bench] loading data ...", flush=True)
    x_tr, y_tr, x_te, y_te = F.full_splits("quickdraw")
    print(f"[bench] data: train={x_tr.shape[0]} test={x_te.shape[0]}", flush=True)
    model_ab, _ = _load_trained_ab()

    for name, fn in [
        ("N0", lambda: sec_n0(x_te, y_te)),
        ("N1", sec_n1),
        ("N2", lambda: sec_n2(model_ab)),
        ("N3", lambda: sec_n3(model_ab, x_te)),
        ("N4", lambda: sec_n4(model_ab, x_te, y_te)),
        ("N5", lambda: sec_n5(model_ab, x_te)),
        ("E1", sec_e1),
        ("E2E3", lambda: sec_e2e3(model_ab, x_te, y_te)),
        ("E4", lambda: sec_e4(model_ab, x_te)),
        ("E5", lambda: sec_e5(model_ab, x_te, y_te,
                              R["sections"]["E2_eval_cost_composition"])),
        ("E6", lambda: sec_e6(x_tr, y_tr)),
    ]:
        try:
            fn()
        except Exception as exc:                      # 单节失败不杀全基准（落盘部分结果）
            import traceback
            R["sections"][name] = {"error": f"{type(exc).__name__}: {exc}",
                                   "traceback": traceback.format_exc()[-1500:]}
            print(f"[bench] {name}: ERROR {type(exc).__name__}: {exc}", flush=True)

    R["total_sec"] = round(time.time() - t_start, 1)
    os.makedirs(RESULTS, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1)
    print(f"[bench] wrote {os.path.relpath(OUT_JSON, PROJECT)} "
          f"({R['total_sec']}s total)", flush=True)

    # 摘要（回执指标来源）
    n1 = R["sections"].get("N1_tau_tie_ltc", {})
    n3 = R["sections"].get("N3_dt0_contraction", {})
    n4 = R["sections"].get("N4_gradients", {})
    e2 = R["sections"].get("E2_eval_cost_composition", {})
    print("[bench] SUMMARY " + json.dumps({
        "N0_A_clean_acc": R["sections"].get("N0_convention_anchor", {}).get("A_clean_acc"),
        "N0_A_equals_B": R["sections"].get("N0_convention_anchor", {}).get("A_equals_B"),
        "N0_clean_modified_frac": R["sections"].get("N0_convention_anchor", {}).get(
            "clean_input_modified_frame_fraction"),
        "N1_ltc_dt0_finite": n1.get("ltc_path", {}).get("dt_0", {}).get("finite"),
        "N1_cfc_ts0_finite": n1.get("cfc_default_ts0_finite"),
        "N3_overall_pass": n3.get("overall_pass"),
        "N4_realistic_grad_ts_norm": n4.get("realistic_d2_pattern_block5-30", {}).get("grad_ts_norm"),
        "N4_realistic_param_finite": n4.get("realistic_d2_pattern_block5-30", {}).get(
            "param_grads_all_finite"),
        "N4_dt101_param_finite": n4.get("constant_dt_sweep", {}).get("dt_101", {}).get(
            "param_grads_all_finite"),
        "N5_manual_vs_lib_B1_max_diff": R["sections"].get(
            "N5_batched_timespans_boundary", {}).get("manual_loop_vs_library_B1_max_abs_diff"),
        "E1_speedup_B128": R["sections"].get("E1_d2_cost", {}).get(
            "per_call", {}).get("B=128", {}).get("speedup"),
        "E2_per_cell_sec": e2.get("production_sec_per_cell"),
        "E2_108_estimate_sec": e2.get("composition_108_cells_estimate_sec"),
        "E2_identity_all_equal": all(
            v["accs_equal_production"] and v["accs_equal_defer"]
            for v in e2.get("identity_mirror_vs_production", {}).values()),
        "E3_sync_overhead_pct": e2.get("sync_overhead_pct"),
        "E5_6cell_total_vs_model": [R["sections"].get("E5_composition_validation", {}).get(
            "six_cell_total_sec"), R["sections"].get("E5_composition_validation", {}).get(
                "six_cell_model_prediction_sec")],
        "E5_on_disk_actual_sec": R["sections"].get("E5_composition_validation", {}).get(
            "on_disk_actual_eval_sec_5th_unit"),
        "E6_epoch_estimate_sec": {k: v.get("epoch_estimate_sec_333batches")
                                  for k, v in R["sections"].get(
                                      "E6_train_step_composition", {}).items()
                                  if isinstance(v, dict)},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
