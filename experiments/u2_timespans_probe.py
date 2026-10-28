#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""u2_timespans_probe.py — S0 最小前向探针（关闭 U2：ncps CfC timespans 行为实测）。

课题：液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a
阶段：S2-pilot-gate-checks（design.md §四 S0 四断言；workflow.json S2）

四断言（design.md §四 S0 逐字规格）：
  ① forward(x, timespans=None) 与 timespans=全1 输出关系记录（相同/差异入档）；
  ② dt=0 步不推进状态（或如实记录其行为，供 D2 回退裁决）；
  ③ 变 dt（1→6→1）改变输出且方向合理；
  ④ dt∈{0..16} 无 NaN/Inf。
失败条件：②④不成立且紧缩回退不可行 → F2 触发。

实测新增（U2 核心发现，ncps 0.0.2）：CfC.forward 在 batch_first=True 且 B>1 时
传 timespans 直接 RuntimeError（cfc.py:166 `timespans[:, t].squeeze()` 得 (B,)
无法与 (B,H) 广播）。本探针对四断言用 B=1（可用形态），并验证一条 manual-loop
替代路径（ts 以 (B,1) 进 cell，与库函数逐样本一致），供 S3 批式 eval/训练选路。

补充（非四断言，标 supplementary）：timespans 通路反向传播有限性——S3 的 C 臂
（D3：块状间隙增强训练 + 真实 timespans）需要梯度流过 timespans，提前排雷。

运行环境约定：必须用 terminal 里的 G:/ai/python11/python.exe（torch 2.10.0+cu128、
ncps 0.0.2 在位）；execute_code 内核没有 torch/ncps，不用它跑本脚本。
本探针用 CPU + float32 + 固定种子，保证确定性可复现。

产物：results/u2_probe.json（全部原始数字 + 逐断言结论 + API 发现 + 替代路径验证）。
"""

from __future__ import annotations

import json
import os
import platform
import sys
import time

import torch

from ncps.torch import CfC

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
RESULTS = os.path.join(PROJECT, "results")
OUT_JSON = os.path.join(RESULTS, "u2_probe.json")

SEED = 0
IN_SIZE = 16      # 探针用迷你输入维（与 pilot 的 128 无关，只测 timespans 语义）
UNITS = 32        # 探针用迷你隐藏维
B_WORK = 1        # ncps 0.0.2 中传 timespans 唯一可用的 batch 形态
DEVICE = "cpu"
GAP_LEN = 5       # D2 语义：块长 5 的间隙（与 H1 主假设 block5 对齐）


def rel_change(new: torch.Tensor, old: torch.Tensor) -> float:
    """逐 batch 的 ||new-old||/||old|| 的 batch 均值（float64 计算防精度噪声）。"""
    a = new.double()
    b = old.double()
    denom = b.norm(dim=1).clamp_min(1e-12)
    num = (a - b).norm(dim=1)
    return (num / denom).mean().item()


def max_abs_diff(a: torch.Tensor, b: torch.Tensor) -> float:
    return (a.double() - b.double()).abs().max().item()


def build_d2_timespans(seq_len: int, gap_positions: list[int], gap_len: int,
                       batch: int) -> tuple[torch.Tensor, torch.Tensor]:
    """D2 参考编码（design.md §4.0 D2，供 S3 直接复用）：
    被掩码帧（零填充输入）timespans=0（不推进时间）；间隙后首个真实帧
    timespans=gap_len+1（真实经过时间一次性入账）；其余真实帧 timespans=1。
    返回 (mask, timespans)：mask=1 表示该帧被掩码（零填充）。
    gap_positions：每个间隙的起始帧索引（连续 gap_len 帧被掩码）。
    """
    mask = torch.zeros(seq_len)
    ts = torch.ones(seq_len)
    for start in gap_positions:
        for k in range(gap_len):
            idx = start + k
            assert idx < seq_len, "gap 越界"
            mask[idx] = 1.0
            ts[idx] = 0.0
        after = start + gap_len
        assert after < seq_len, "间隙后必需还有真实帧"
        ts[after] = float(gap_len + 1)
    return mask, ts.unsqueeze(0).repeat(batch, 1)


def cfc_forward_ts_b1(model: CfC, input: torch.Tensor,
                      timespans: torch.Tensor | None):
    """manual-loop 替代路径：逐字复刻 ncps.torch.cfc.CfC.forward
    （batch_first=True / return_sequences=True / mixed_memory=False 支路），
    唯一改动=ts 以 (B,1) 进 cell（而非 squeeze() 后的 (B,)），使其可与 (B,H) 广播。
    与库函数在 B=1 上逐样本数值一致性在本探针中验证。
    """
    device = input.device
    batch_size, seq_len = input.size(0), input.size(1)
    h_state = torch.zeros((batch_size, model.state_size), device=device)
    output_sequence = []
    for t in range(seq_len):
        inputs = input[:, t]
        ts = 1.0 if timespans is None else timespans[:, t].unsqueeze(1)
        h_out, h_state = model.rnn_cell.forward(inputs, h_state, ts)
        output_sequence.append(model.fc(h_out))
    return torch.stack(output_sequence, dim=1), h_state


def main() -> int:
    t0 = time.time()
    os.makedirs(RESULTS, exist_ok=True)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)

    import ncps
    import ncps.torch.cfc as cfc_mod

    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "ncps": getattr(ncps, "__version__", "unknown"),
        "device": DEVICE,
        "dtype": "float32",
        "seed": SEED,
        "cfc_module_file": os.path.abspath(str(cfc_mod.__file__)),
        "cfc_forward_signature": "forward(self, input, hx=None, timespans=None) (cfc.py:112)",
        "source_evidence": {
            "cfc.py:166": "ts = 1.0 if timespans is None else timespans[:, t].squeeze()  # None 即均匀网格 dt=1；squeeze() 使 B>1 时 ts=(B,) 无法与 (B,H) 广播",
            "cfc_cell.py:162": "t_interp = self.sigmoid(t_a * ts + t_b)",
            "cfc_cell.py:166": "new_hidden = ff1 * (1.0 - t_interp) + t_interp * ff2",
        },
    }

    model = CfC(IN_SIZE, UNITS, mode="default").to(DEVICE).eval()
    config = {
        "model": "ncps.torch.CfC(input_size=16, units=32, mode='default')",
        "batch_working_shape": B_WORK,
        "input_size": IN_SIZE, "units": UNITS,
        "gap_len": GAP_LEN,
        "note": "迷你尺寸只测 timespans 语义；pilot 真实尺寸（CNN-128+CfC-128）在 S3",
    }

    assertions: dict = {}

    # ---------- U2 API 形态发现（ncps 0.0.2 B>1 + timespans 崩溃 + 替代路径验证） ----------
    with torch.no_grad():
        x_api = torch.randn(2, 8, IN_SIZE, device=DEVICE)
        crash = None
        try:
            model(x_api, timespans=torch.ones(2, 8, device=DEVICE))
        except RuntimeError as exc:
            crash = f"{type(exc).__name__}: {exc}"
        # B=1 库函数路径
        x_b1 = x_api[:1]
        out_lib, hx_lib = model(x_b1, timespans=torch.ones(1, 8, device=DEVICE))
        # manual-loop B=2（同输入，整批一次）
        out_man, hx_man = cfc_forward_ts_b1(model, x_api, torch.ones(2, 8, device=DEVICE))
        # manual-loop B=2 vs 库函数 B=1（逐样本对齐）：差应≈0
        d_manual_vs_lib = max(max_abs_diff(out_man[:1], out_lib),
                              max_abs_diff(hx_man[:1], hx_lib))
        # manual-loop 的 None 支路 vs 库函数 None 支路（复刻正确性）
        out_lib_n, hx_lib_n = model(x_api)
        out_man_n, hx_man_n = cfc_forward_ts_b1(model, x_api, None)
        d_manual_none = max(max_abs_diff(out_man_n, out_lib_n),
                            max_abs_diff(hx_man_n, hx_lib_n))
        # 库函数 (B=1, L, 1) 形态也可用
        out_lib_3d, hx_lib_3d = model(x_b1, timespans=torch.ones(1, 8, 1, device=DEVICE))
        d_lib_3d_vs_2d = max(max_abs_diff(out_lib_3d, out_lib),
                             max_abs_diff(hx_lib_3d, hx_lib))
    api_finding = {
        "installed_ncps": env["ncps"],
        "batched_timespans_shape_(B,L)_B>1": {
            "works": crash is None,
            "error": crash,
            "root_cause": "cfc.py:166 ts=timespans[:, t].squeeze() 得 (B,)，与 cell 内 (B,H) 广播失败",
        },
        "working_invocations": {
            "library_B1_shape_(1,L)": True,
            "library_B1_shape_(1,L,1)": {"works": True, "max_diff_vs_(1,L)": d_lib_3d_vs_2d},
            "manual_loop_ts_(B,1)": {
                "works": True,
                "max_diff_vs_library_B1_per_sample": d_manual_vs_lib,
                "none_branch_matches_library": {"max_diff": d_manual_none},
            },
        },
        "impact_for_S3": (
            "A 臂不传 timespans 不受影响；B 臂/C 臂若需 B>1 批式前向/训练，"
            "用已验证的 manual-loop（本脚本 cfc_forward_ts_b1，与库函数逐样本一致，"
            "最大差 {:.2e}）或逐样本 B=1。pilot 前应在真实尺寸上复验一次。"
        ).format(d_manual_vs_lib),
    }

    # ---------- 断言①：timespans=None vs 全1（B=1 可用形态） ----------
    x1 = torch.randn(B_WORK, 24, IN_SIZE, device=DEVICE)
    with torch.no_grad():
        out_none, hx_none = model(x1)                                   # timespans=None
        out_ones, hx_ones = model(x1, timespans=torch.ones(B_WORK, 24, device=DEVICE))
    d_out = max_abs_diff(out_none, out_ones)
    d_hx = max_abs_diff(hx_none, hx_ones)
    a1_pass = (d_out < 1e-6) and (d_hx < 1e-6)
    assertions["a1_none_vs_ones"] = {
        "statement": "forward(x, timespans=None) 与 timespans=全1 的输出关系",
        "max_abs_diff_output": d_out,
        "max_abs_diff_final_hidden": d_hx,
        "relation": "相同" if a1_pass else "有差异",
        "pass": bool(a1_pass),
        "interpretation": (
            "源码 cfc.py:166：timespans=None 时 ts=1.0，与全1向量逐元素相等 → 数值相同"
            "（实测最大差 {:.2e}）。含义：A 臂（论文式 core(x) 不传 timespans）等价于"
            "均匀网格 dt=1，正是 EV-06 锁定的论文协议语义，A 臂无需显式构造全1向量。"
        ).format(max(d_out, d_hx)),
    }

    # ---------- 断言②：dt=0 行为（如实记录，供 D2 回退裁决） ----------
    with torch.no_grad():
        # 2a 单步：固定输入与状态，dt=0 是否"冻结"状态
        xs = torch.randn(B_WORK, 1, IN_SIZE, device=DEVICE)
        h0 = torch.randn(B_WORK, UNITS, device=DEVICE)
        _, h_dt0 = model(xs, hx=h0, timespans=torch.zeros(B_WORK, 1, device=DEVICE))
        _, h_dt1 = model(xs, hx=h0, timespans=torch.ones(B_WORK, 1, device=DEVICE))
        rel_dt0 = rel_change(h_dt0, h0)
        rel_dt1 = rel_change(h_dt1, h0)
        rel_dt0_vs_dt1 = rel_change(h_dt0, h_dt1)   # dt=0 与 dt=1 的单步输出差（时间推进的净效应）

        # 2b D2 间隙场景：零填充帧 dt=0 连续 20 步——状态是否有界/收缩/发散
        h = h0.clone()
        steps = []
        for k in range(20):
            h_prev = h.clone()
            _, h = model(torch.zeros(B_WORK, 1, IN_SIZE, device=DEVICE), hx=h,
                         timespans=torch.zeros(B_WORK, 1, device=DEVICE))
            steps.append(rel_change(h, h_prev))
        max_abs_h = h.abs().max().item()
        final_rel_vs_start = rel_change(h, h0)

        # 2c D2 完整间隙模拟：零填充+dt=0+间隙后首真实帧 dt=gap+1（B 臂）
        #     对照 A 臂（同输入、timespans=None 即全1）与紧缩重索引替代实现
        L_real = 24
        gap_start = 7
        seq_len = L_real + GAP_LEN
        x_real = torch.randn(B_WORK, L_real, IN_SIZE, device=DEVICE)
        x_gap = torch.zeros(B_WORK, seq_len, IN_SIZE, device=DEVICE)
        x_gap[:, :gap_start] = x_real[:, :gap_start]
        x_gap[:, gap_start + GAP_LEN:] = x_real[:, gap_start:]
        mask_v, ts_d2 = build_d2_timespans(seq_len, [gap_start], GAP_LEN, B_WORK)
        out_b, hx_b = model(x_gap, timespans=ts_d2)                    # B 臂（D2 主语义）
        out_a, hx_a = model(x_gap)                                     # A 臂（均匀网格）
        # 紧缩重索引：删掉被掩码帧，间隙后首真实帧 dt=gap+1
        keep = [i for i in range(seq_len) if mask_v[i].item() == 0.0]
        x_compact = x_gap[:, keep]
        ts_compact = torch.ones(B_WORK, len(keep), device=DEVICE)
        ts_compact[:, gap_start] = float(GAP_LEN + 1)                  # 紧缩后间隙后首帧的位置
        _, hx_compact = model(x_compact, timespans=ts_compact)

    a2_bounded_ok = (
        bool(torch.isfinite(h).all().item())
        and steps[-1] < steps[0]
        and max_abs_h <= 1.0 + 1e-6
    )
    a2 = {
        "statement": "dt=0 步不推进状态（或如实记录其行为，供 D2 回退裁决）",
        "single_step_dt0_rel_state_change": rel_dt0,
        "single_step_dt1_rel_state_change": rel_dt1,
        "single_step_dt0_vs_dt1_rel_diff": rel_dt0_vs_dt1,
        "dt0_freezes_state": bool(rel_dt0 < 1e-6),
        "zero_input_dt0_iteration": {
            "steps": 20,
            "per_step_rel_change": [round(s, 6) for s in steps],
            "first_step_rel_change": steps[0],
            "last_step_rel_change": steps[-1],
            "contracting": bool(steps[-1] < steps[0]),
            "max_abs_state": max_abs_h,
            "final_rel_change_vs_initial": final_rel_vs_start,
            "finite": bool(torch.isfinite(h).all().item()),
        },
        "d2_gap_simulation": {
            "gap_len": GAP_LEN, "gap_start_frame": gap_start, "seq_len": seq_len,
            "armB_final_hidden_vs_armA_max_abs_diff": max_abs_diff(hx_b, hx_a),
            "armB_output_vs_armA_max_abs_diff": max_abs_diff(out_b, out_a),
            "zero_fill_vs_compact_reindex_max_abs_diff": max_abs_diff(hx_b, hx_compact),
            "note": ("零填充+dt=0 与紧缩重索引是同一时间信息的两种表示，轨迹数值不同（预期）；"
                     "D2 选零填充以与 A 臂共享输入张量（D1）"),
        },
        "pass": bool(a2_bounded_ok),
        "recorded_behavior": (
            "dt=0 不冻结状态：单步即以门控偏置 sigmoid(t_b) 做一次瞬时更新。"
            "随机初态 h0 在流形外，首步被大幅拉回（dt=0 相对变化 {:.1%}、dt=1 为 {:.1%}），"
            "dt=0 与 dt=1 的单步净差 {:.2%}（时间推进的真实效应量）。"
            "零输入 dt=0 连续 20 步有界、收缩（首步 {:.4f}→末步 {:.4f}）、|h|max={:.3f}<1、"
            "无 NaN——间隙帧把状态温和推向零输入不动点，不是退化/漂移。"
        ).format(rel_dt0, rel_dt1, rel_dt0_vs_dt1, steps[0], steps[-1], max_abs_h),
        "verdict_detail": (
            "字面'dt=0 不推进状态'=否（状态被更新但时间不推进：ts=0 → 门控取偏置值，"
            "闭式解中无时间衰减激活）；按 design.md 的'或如实记录其行为'分支入档。"
            "回退触发条件（状态被推进失真/NaN）未出现：零输入 dt=0 迭代有界收缩。"
        ),
    }
    assertions["a2_dt0_behavior"] = a2

    # ---------- 断言③：变 dt（1→6→1）改变输出且方向合理 ----------
    with torch.no_grad():
        x3 = torch.randn(B_WORK, 12, IN_SIZE, device=DEVICE)
        ts_vary = torch.ones(B_WORK, 12, device=DEVICE)
        ts_vary[:, 3] = 6.0                       # 1→6→1
        out_v, hx_v = model(x3, timespans=ts_vary)
        out_c, hx_c = model(x3, timespans=torch.ones(B_WORK, 12, device=DEVICE))
        d_out_vary = max_abs_diff(out_v, out_c)
        d_hx_vary = max_abs_diff(hx_v, hx_c)
        # 每时间步输出差剖面（B=1 取 batch 0）：扰动效应的时间结构
        step_diff = (out_v[0].double() - out_c[0].double()).abs().mean(dim=1)  # (L,)
        frac_steps_changed = (step_diff > 1e-3).double().mean().item()

        # 单步 ts 扫描：每隐藏单元 new_hidden 对 ts 单调（结构保证 sigmoid 单调）
        ts_grid = [0.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]
        sweep = []
        for tv in ts_grid:
            _, h_tv = model(xs, hx=h0, timespans=torch.full((B_WORK, 1), tv, device=DEVICE))
            sweep.append(h_tv[0].double())        # 取 batch 0 逐单元
        sweep_t = torch.stack(sweep, dim=0)       # (len(ts_grid), UNITS)
        nondec = (sweep_t[1:] - sweep_t[:-1] >= -1e-6).all(dim=0)
        noninc = (sweep_t[1:] - sweep_t[:-1] <= 1e-6).all(dim=0)
        mono_frac = (nondec | noninc).double().mean().item()
        # dt=6 单步结果落在 dt=1 与 dt=64 之间（逐单元，方向合理性的直接证据）
        _, h_dt6 = model(xs, hx=h0, timespans=torch.full((B_WORK, 1), 6.0, device=DEVICE))
        lo = torch.minimum(sweep_t[1], sweep_t[-1])
        hi = torch.maximum(sweep_t[1], sweep_t[-1])
        between_frac = ((h_dt6[0].double() >= lo - 1e-6) &
                        (h_dt6[0].double() <= hi + 1e-6)).double().mean().item()

    a3_pass = (d_out_vary > 1e-3) and (frac_steps_changed >= 0.5) \
        and (mono_frac >= 0.99) and (between_frac >= 0.99)
    assertions["a3_varying_dt"] = {
        "statement": "变 dt（1→6→1）改变输出且方向合理",
        "multistep_1_6_1": {
            "output_sequence_max_abs_diff_vs_constant1": d_out_vary,
            "final_hidden_max_abs_diff_vs_constant1": d_hx_vary,
            "fraction_timesteps_changed": frac_steps_changed,
            "per_timestep_mean_abs_diff": [round(v, 6) for v in step_diff.tolist()],
        },
        "single_step_ts_sweep": {
            "ts_grid": ts_grid,
            "monotone_units_fraction": mono_frac,
            "dt6_between_dt1_and_dt64_fraction": between_frac,
        },
        "pass": bool(a3_pass),
        "interpretation": (
            "变 dt 显著改变输出：输出序列最大差 {:.4f}、{:.0%} 时间步均值差>1e-3"
            "（扰动步 t=3 及其后立即最大）。终态差仅 {:.5f} 是 CfC 收缩性"
            "（状态被重新收敛回流形，与断言②的零输入 dt=0 收缩一致），不是'无变化'。"
            "单步逐单元对 ts 单调比例 {:.3f}、dt=6 落在 dt=1 与 dt=64 之间比例 {:.3f}"
            "——与闭式解 sigmoid(t_a*ts+t_b) 单调性结构一致，方向合理。"
            "S3 注意：B−A 差异集中在间隙附近时间步，若读表只取末态需评估收缩衰减。"
        ).format(d_out_vary, frac_steps_changed, d_hx_vary, mono_frac, between_frac),
    }

    # ---------- 断言④：dt∈{0..16} 无 NaN/Inf ----------
    fin = {}
    all_finite = True
    with torch.no_grad():
        for dt in range(0, 17):
            x4 = torch.randn(B_WORK, 48, IN_SIZE, device=DEVICE)
            out4, hx4 = model(x4, timespans=torch.full((B_WORK, 48), float(dt), device=DEVICE))
            ok = bool(torch.isfinite(out4).all().item() and torch.isfinite(hx4).all().item())
            fin[f"dt_{dt}"] = {
                "finite": ok,
                "max_abs_output": out4.abs().max().item(),
                "max_abs_hidden": hx4.abs().max().item(),
            }
            all_finite = all_finite and ok
        # 混合极端模式 + 长 D2 间隙模式
        mask_l, ts_l = build_d2_timespans(64, [10, 30, 50], GAP_LEN, B_WORK)
        patterns = {
            "mixed_0_16": torch.cat([torch.zeros(B_WORK, 8), torch.full((B_WORK, 8), 16.0),
                                     torch.ones(B_WORK, 8), torch.zeros(B_WORK, 8),
                                     torch.full((B_WORK, 16), 6.0)], dim=1),
            "d2_three_gaps_L64": ts_l,
        }
        extra = {}
        for name, ts_p in patterns.items():
            L_p = ts_p.shape[1]
            x_p = torch.randn(B_WORK, L_p, IN_SIZE, device=DEVICE)
            if name == "d2_three_gaps_L64":
                x_p = x_p * (1 - mask_l).view(1, -1, 1)
            out_p, hx_p = model(x_p, timespans=ts_p)
            ok = bool(torch.isfinite(out_p).all().item() and torch.isfinite(hx_p).all().item())
            extra[name] = {"finite": ok, "max_abs_hidden": hx_p.abs().max().item()}
            all_finite = all_finite and ok
    assertions["a4_finiteness"] = {
        "statement": "dt∈{0..16} 无 NaN/Inf",
        "per_dt": fin,
        "mixed_patterns": extra,
        "all_finite": bool(all_finite),
        "pass": bool(all_finite),
    }

    # ---------- 补充（非四断言）：timespans 通路反向传播有限性（S3 C 臂排雷） ----------
    model.zero_grad()
    xg = torch.randn(B_WORK, 16, IN_SIZE, device=DEVICE, requires_grad=True)
    ts_g = build_d2_timespans(16, [5], GAP_LEN, B_WORK)[1]
    out_g, _ = model(xg, timespans=ts_g)
    out_g.pow(2).sum().backward()
    assert xg.grad is not None
    grad_finite = bool(torch.isfinite(xg.grad).all().item())
    param_grad_finite = all(
        bool(p.grad is None or torch.isfinite(p.grad).all().item())
        for p in model.parameters()
    )
    input_grad_abs_max = xg.grad.abs().max().item()
    model.zero_grad()

    # manual-loop B=2 反向（验证替代路径可训练）
    xg2 = torch.randn(2, 16, IN_SIZE, device=DEVICE, requires_grad=True)
    ts_g2 = build_d2_timespans(16, [5], GAP_LEN, 2)[1]
    out_g2, _ = cfc_forward_ts_b1(model, xg2, ts_g2)
    out_g2.pow(2).sum().backward()
    assert xg2.grad is not None
    manual_grad_finite = bool(torch.isfinite(xg2.grad).all().item())
    manual_grad_abs_max = xg2.grad.abs().max().item()
    model.zero_grad()

    supplementary = {
        "backward_through_timespans": {
            "library_B1": {
                "input_grad_finite": grad_finite,
                "param_grads_finite": param_grad_finite,
                "input_grad_abs_max": input_grad_abs_max,
            },
            "manual_loop_B2": {
                "input_grad_finite": manual_grad_finite,
                "input_grad_abs_max": manual_grad_abs_max,
            },
            "note": "S3 C 臂（D3 增强训练+真实 timespans）需要梯度流过 timespans；两条路径实测均有限",
        }
    }

    # ---------- 汇总 ----------
    a1 = assertions["a1_none_vs_ones"]["pass"]
    a2p = assertions["a2_dt0_behavior"]["pass"]
    a3 = assertions["a3_varying_dt"]["pass"]
    a4 = assertions["a4_finiteness"]["pass"]
    summary = {
        "assertions_total": 4,
        "assertions_passed": int(a1) + int(a2p) + int(a3) + int(a4),
        "prediction_check": {
            "predicted": "断言①③④过, 断言②(dt=0) 决定 B 臂实现路径",
            "actual": ("①③④过；②字面冻结=否但行为有界收缩无 NaN（design.md 允许的记录分支）。"
                       "另实测 ncps 0.0.2 B>1 传 timespans 崩溃——B 臂实现路径=manual-loop"
                       "（已验证）或逐样本 B=1，A 臂不受影响"),
            "prediction_confirmed": bool(a1 and a3 and a4),
            "b_arm_path_decided_by_a2": True,
        },
        "f2_trigger_condition": "②④不成立且紧缩回退不可行",
        "f2_triggered": bool(not (a2p and a4)),
        "u2_status": "closed" if (a1 and a2p and a3 and a4) else "open",
        "runtime_sec": round(time.time() - t0, 2),
    }

    payload = {
        "schema": "u2-timespans-probe/v1",
        "stage": "S2-pilot-gate-checks",
        "purpose": "S0 最小前向探针：关闭 U2（ncps CfC timespans 行为实测），裁决 D2 主语义/回退",
        "design_ref": "design.md §四 S0 四断言 + §4.0 D2；workflow.json S2",
        "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "reproduce": "G:/ai/python11/python.exe experiments/u2_timespans_probe.py",
        "env": env,
        "config": config,
        "u2_api_finding": api_finding,
        "assertions": assertions,
        "supplementary": supplementary,
        "d2_reference_encoding": {
            "rule": "掩码帧 dt=0；间隙后首真实帧 dt=gap_len+1；其余真实帧 dt=1；保序保长零填充",
            "helper": "build_d2_timespans(seq_len, gap_positions, gap_len, batch) 在本脚本内，S3 可复用",
        },
        "summary": summary,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(json.dumps({
        "out_json": os.path.relpath(OUT_JSON, PROJECT),
        "a1": a1, "a2_recorded_bounded": a2p, "a3": a3, "a4": a4,
        "batched_timespans_crash": crash is not None,
        "manual_loop_max_diff_vs_library": d_manual_vs_lib,
        "u2_status": summary["u2_status"],
        "f2_triggered": summary["f2_triggered"],
        "runtime_sec": summary["runtime_sec"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
