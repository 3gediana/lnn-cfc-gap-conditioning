#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_operator_unit_update_workflow.py — 第六单元（算子优化先行）落账：
- stop_conditions 增 F8 算子墙（W-LTC-τ / W-BATCH-TS / W-BIGDT-GRAD / W-LAUNCH 台账，
  结论=当前无一堵墙阻塞科学路径，不触发早退）
- S5.actions 追记算子单元结论（零修复落地、A/B 不需重训、C 臂重训排产不变）
- updated_at 刷新
"""
import json
import os

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(P, "workflow.json")

with open(WF, encoding="utf-8") as fh:
    w = json.load(fh)

F8 = ("F8 算子墙: CfC/液态单元算子边界（experiments/operator_bench.py 实测台账）——"
      "W-LTC-τ ltc_cell.py:223-244 LTC+elapsed_time=0 除零 NaN（不在科学路径，缓解=wrapper clamp>=1e-4）；"
      "W-BATCH-TS cfc.py:166 库 forward B>1+timespans 广播崩溃（已缓解=manual-loop 恒等 4.05e-06）；"
      "W-BIGDT-GRAD 恒定 dt>=15 的 100 步反传 ∇_ts 爆炸至 1e18 量级（协议 D2 dt<=6 不触发，兜底=grad clip 1.0）；"
      "W-LAUNCH 100 步 Python 循环 launch-bound ~1.5s/格（恒等修复空间已穷尽，非恒等修复需 A/B 重训判定）。"
      "触发条件=后续单元需要 wired/LTC+dt=0、库批式 timespans 或恒定大 dt 训练 → 早退并回退设计；"
      "当前无一堵墙阻塞科学路径（2026-10-27 算子单元判定）")

if not any(str(x).startswith("F8 ") for x in w.get("stop_conditions", [])):
    w.setdefault("stop_conditions", []).append(F8)

s5 = [s for s in w["stages"] if s.get("id") == "S5-full-protocol"][0]
s5["actions"] = s5["actions"] + (
    " ‖ 第六单元（算子优化先行，2026-10-27T03:2x lab-executor）回执判据："
    "experiments/operator_bench.py 实跑落 results/operator_bench.json+operator_bench.md——"
    "N0 Convention 锚定 PASS（clean A≡B=0.9121、修改帧=0）；N1 LTC τ-tie dt=0 NaN 硬墙（不在科学路径）；"
    "N2 scale-state 爆炸不复现（结构性有界）；N3 dt=0 有界+有限 PASS 但强收缩不成立（真实尺寸如实修正 u2 迷你结论）；"
    "N4 真实 D2 模式梯度有限（‖∇_ts‖=0.0307），恒定 dt>=15 压力测试 ∇_ts 爆炸至 1e18（协议不触发）；"
    "N5 B>1 timespans 崩溃边界+manual-loop 恒等 4.05e-06；E1 d2 向量化 3103× 恒等；"
    "E2 108 格构成模型 165.6s vs 实测 167.3s（偏差 1.0%）；E3 延迟同步收益 +0.2%（噪声）→ FIX-1 否决；"
    "零修复落地→科学路径前向数值逐位不变→A/B ckpt 不需重训；C 臂重训 3×30ep≈72min（Convention 修正原因，"
    "与算子单元无关）+修正 Convention 重算 108 行≈3min 排产不变；回归 full_protocol selftest 68 项+eval_patch_selftest "
    "48 用例全 PASS（experiments/operator_regression_*.log）；F8 算子墙已入 stop_conditions（无阻塞）"
)
w["updated_at"] = "2026-10-27T03:2x+08:00"

with open(WF, "w", encoding="utf-8") as fh:
    json.dump(w, fh, ensure_ascii=False, indent=1)

with open(WF, encoding="utf-8") as fh:
    w2 = json.load(fh)
s5b = [s for s in w2["stages"] if s.get("id") == "S5-full-protocol"][0]
assert any(str(x).startswith("F8 ") for x in w2["stop_conditions"]), "F8 落盘失败"
assert "第六单元（算子优化先行" in s5b["actions"], "actions 追记失败"
assert s5b["estimate_min"] == 60
assert w2["updated_at"] == "2026-10-27T03:2x+08:00"
print("workflow.json updated: F8 appended (n_stop=", len(w2["stop_conditions"]),
      "), S5.actions appended, updated_at refreshed")
