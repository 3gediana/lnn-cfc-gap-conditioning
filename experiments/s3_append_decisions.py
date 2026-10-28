#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s3_append_decisions.py — DECISIONS.md 追加 S3 三补单元条目。"""
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(PROJECT, "notes", "DECISIONS.md")
with open(PATH, encoding="utf-8") as fh:
    s = fh.read()

ENTRY = (
    "\n- 2026-10-26 03:3x（unit.S3 lab-executor，S3-pilot-threearm 三补单元，status=ok）："
    "**eval 矩阵 108/108 行齐，四份契约产物落盘，S3 机器态 done**。①执行链（先合并后续跑，避免重算）："
    "ps 实证无残留进程→experiments/consolidate_progress.py 把分片 14 行 union 写回规范 progress"
    "（主 84+分片 14=98，76 个重叠键数值零冲突）→G:/ai/python11/python.exe experiments/pilot_threearm.py eval "
    "跳过 98 行、只算缺的 10 格（seed2 B/C × block5-30 模式1,2 + block15-30 模式0,1,2）实测 208s"
    "（≈21s/行，与 03:1x 判读 4-6min 预估一致）→experiments/merge_eval_shards.py --canonical 交叉校验"
    "（union=108、CSV 逐字节一致、verdict 一致，双代码路径互证确定性）→experiments/eval_patch_selftest.py "
    "exit=0（48 用例 hit 恒等+门控回归 3/3）。若跳过合并直接 eval 会重算 seed2 B/C 全 24 格（≈7.6min），"
    "「先合并后续跑」是关键路径优化，重叠键冲突检测是合并安全前提。②最终数（CSV 实算，3 种子 mean）："
    "clean A=B=10.43%（B−A 逐种子恒 +0.00pp）、C=10.51%；block5-30 B−A=−0.71pp、C−A=+5.36pp"
    "（逐种子 +4.08/+4.78/+7.24 一致）；block15-30 B−A=−0.73pp、C−A=+1.78pp；uniform30 B−A=−0.35pp、"
    "C−A=+4.94pp；H2 block15−block5 Δ=−0.02pp。③门控三门：clean A≡B=0.000pp PASS、A@uniform30 z=5.97>2 "
    "PASS、A@clean=10.43% D7≥97% 未达（pilot 2-epoch 纯预算缺口，verify 4/4+代码级核验为证）；机械门控 "
    "gate_pass_arm=C、decision=pass、next_action=replicate。④**本单元 verdict=inconclusive**：H1/H2 因保真度"
    "缺口 pilot 不足以 adjudicate（A/B 输出恒定类表明 pilot 远未收敛，chance 级基数上的臂差不构成机制证据），"
    "next_action=replicate 交 S4 出最终判读；F1 字面条件对 B 臂成立（B−A=−0.71pp<+1pp 且 clean 不受损）但 C 臂"
    "保守存活门控先触发，按 D3 预注册语义以门控出口为准，负结果分支不启动。⑤小补丁：merge_eval_shards.py "
    "合并计时携带 pilot_timing.json 真实计时快照（resume_eval_run eval_sec=208.0），防空壳计时覆盖真实数字；"
    "shard_timing 为空为已知不阻塞项（分片进程被硬超时终止未及写 timing）。⑥机器态：workflow.json "
    "S3-pilot-threearm→done+result+dispatch_log 第四条、u_status U5→closed（真实计时入 results/pilot_timing.json）。"
    "⑦经验沉淀：「断点续跑+先合并后续跑」对分片并行遗产的收敛成本低（10 格 208s vs 重算 24 格 7.6min）；"
    "用第二代码路径（merge）对同一 union 重新出表可互证确定性（本次 CSV 逐字节一致）；partial 遗产合并前必须"
    "复算重叠键数值一致性（本次 76 键零冲突）。\n"
)

if not s.endswith("\n"):
    s += "\n"
s += ENTRY
with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(s)
print("DECISIONS.md appended:", len(s), "chars")
