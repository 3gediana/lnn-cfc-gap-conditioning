#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_append_decisions.py — 向 notes/DECISIONS.md 追加 S5 首单元决策条目。"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

ENTRY = (
    "\n- 2026-10-26 05:2x（unit.S5 lab-executor，S5-full-protocol 首单元，status=partial/checkpointed）："
    "**full_protocol.py 落盘（results/full_threearm.csv/md 的生成器）+ QuickDraw 全量训练启动并交断点**。"
    "①协议升级点仅三项且全部预注册内：数据 pilot 子集(10k/3k)→论文协议全量(50k，85/15 seeded split=42500/7500，"
    "同 perm 种子 12345 保证 pilot 子集⊂全量子集可比)、EPOCHS 2→30（design.md §五「全量数据 30 epoch」）、"
    "新增逐 epoch checkpoint+断点续跑（30epoch×6 训练跨窗必需）；训练路径复用 pilot_threearm.py 同源代码"
    "（import 不复制，模型/掩码/timespans/读表/D1-D3 臂语义零漂移），ckpt 命名 full_* 与 pilot_* 分离不覆盖证据。"
    "②**性能补丁决策**：开工探针实测 C 臂训练瓶颈=CPU 双层 Python 循环版 d2_timespans 867ms/batch"
    "（fwd+bwd 仅 188ms），系 pilot 未优化的历史实现；落向量化 d2_timespans_vec（GPU 整数算术）并 monkeypatch "
    "pilot 模块全局（eval_arm_condition 同受益），恒等性经 selftest 68 项 torch.equal（含 all-masked/alternating/"
    "run-at-end 等边缘 mask，CPU+GPU 双设备）+ 1+1 epoch 续跑 vs 2 epoch 一次跑 bitwise 一致（max|Δstate|=0）担保；"
    "C 臂 30epoch×333batch 预估 175.7min→约 32min，6 训练总预估 ~9.5h→~2.7h。"
    "③判读须知落码（S4 §六 复算带出）：summarize_full 预注册主口径=meanpool 论文口径并三口径兼报、"
    "C clean 降幅逐种子门控（全种子 |drop|≤0.5pp 才计 PASS）、A 臂 clean 三口径分化作恒定类消失伴生判据、"
    "D7 结论级判 A@clean≥98.5%（论文 Table III QuickDraw≈98.6-98.7% 数量级）。"
    "④负结果分支预注册不变：结论级 block5-30 C−A(meanpool)<2pp → 收缩声称+负结果落盘不硬撑。"
    "⑤窗口账：单元硬超时 2446s 内跑到 seed0_ab ep4（~45s/epoch，train acc 0.40→0.84 收敛中，pilot 2epoch 仅 0.31），"
    "半程不落表（CSV/MD 须 108 行齐），交断点给下一单元续跑。\n"
)

path = os.path.join(PROJ, "notes", "DECISIONS.md")
with open(path, "a", encoding="utf-8") as fh:
    fh.write(ENTRY)
print("appended", len(ENTRY), "chars to", path)
