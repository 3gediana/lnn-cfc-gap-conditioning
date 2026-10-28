#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s3_update_status.py — S3 收口：更新 STATUS.md（阶段行/最近更新/最近产物/下一步）。
禁词纪律：写完由调用方 grep 禁词清单 + 复跑 research-project-state.py 双验证。"""
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(PROJECT, "STATUS.md")
with open(PATH, encoding="utf-8") as fh:
    s = fh.read()

NEW_STAGE = (
    "active / S3-pilot-threearm 收口（2026-10-26T03:3x lab-executor 三补单元实跑：eval 矩阵 "
    "108/108 行齐，四份契约产物落盘）。执行链：ps 实证无残留进程→experiments/consolidate_progress.py "
    "把分片 14 行 union 写回规范 progress（主 84+分片 14=98 行，76 个重叠键数值零冲突，避免重算 "
    "seed2 B/C 全 24 格）→G:/ai/python11/python.exe experiments/pilot_threearm.py eval 跳过 98 行、"
    "只算缺的 10 格（seed2 B/C × block5-30 模式1,2 + block15-30 模式0,1,2）实测 208s（≈21s/行，"
    "与 4-6min 预估一致）→experiments/merge_eval_shards.py --canonical 交叉校验 union=108、CSV 逐字节"
    "一致、verdict 一致（双代码路径互证；小补丁=合并计时携带 eval 真实计时快照，防空壳计时覆盖真实数字）"
    "→experiments/eval_patch_selftest.py exit=0（48 用例 hit 恒等+门控回归 3/3）。最终数（3 种子 mean，"
    "CSV 实算）：clean A=B=10.43%（逐种子 B−A 恒 +0.00pp）、C=10.51%；uniform30 A=13.27/B=12.92/C=18.21"
    "（B−A=−0.35pp、C−A=+4.94pp）；block5-30 A=13.69/B=12.98/C=19.06（B−A=−0.71pp、C−A=+5.36pp，"
    "逐种子 +4.08/+4.78/+7.24 一致）；block15-30 A=14.42/B=13.69/C=16.20（B−A=−0.73pp、C−A=+1.78pp）；"
    "H2 block15−block5 Δ=−0.02pp；sanity 三门控：clean A≡B=0.000pp PASS、A@uniform30 z=5.97>2 PASS、"
    "A@clean=10.43% D7≥97% 未达（pilot 2-epoch 纯预算缺口，verify 4/4+代码级核验为证）；机械门控 "
    "gate_pass_arm=C、decision=pass、next_action=replicate；H1/H2 因保真度缺口 pilot 不足以 adjudicate，"
    "本单元 verdict=inconclusive，最终判读交 S4"
)

anchor = "- 阶段：**"
i = s.index(anchor) + len(anchor)
j = s.index("**", i)
s = s[:i] + NEW_STAGE + s[j:]

NEW_UPDATE = (
    "2026-10-26T03:3x+08:00（unit.S3 lab-executor 三补单元，status=ok）：eval 矩阵 108/108 行齐并落四份"
    "契约产物（results/pilot_threearm.csv 108 数据行、pilot_threearm.md、pilot_progress.json 带 verdict、"
    "pilot_timing.json eval_sec=208.0）。先合并后续跑（consolidate 98 行→eval 只算缺的 10 格 208s）避免"
    "重算 24 格；merge --canonical 双路径互证（CSV 逐字节一致）；selftest exit=0。机器态：workflow.json "
    "S3→done+result+dispatch_log 第四条、u_status U5→closed（真实计时在盘）。判读要点交 S4：C 臂 block5 "
    "C−A=+5.36pp 过线（03:1x 预览 +4.90pp/+7.06 为不完整数据快照，完整数据 seed2=+7.24）、C clean 降幅 "
    "+0.08pp ≤0.5pp；B−A=−0.71pp 噪声内（F1 字面条件对 B 臂成立但 C 臂保守存活门控先触发）；H2 Δ=−0.02pp "
    "不成立；A/B 输出恒定类（clean 三模式恒等）表明 pilot 远未收敛，chance 级基数上的臂差不构成机制证据→"
    "verdict=inconclusive、next_action=replicate。上次更新："
)
k = s.index("- 最近更新：") + len("- 最近更新：")
s = s[:k] + NEW_UPDATE + s[k:]

NEW_ART = (
    "- 最近产物：results/pilot_threearm.csv（108 数据行：3 种子×3 臂×4 条件×3 模式，三读口径 "
    "meanpool/final/gapnb）+ results/pilot_threearm.md（汇总表+三门控 sanity+门线判读+限制）+ "
    "results/pilot_progress.json（108 行+verdict+sanity.verify_real_size）+ results/pilot_timing.json"
    "（u5_runtime：merged_at+resume_eval_run eval_sec=208.0+shard_timing 空已知不阻塞）+ "
    "experiments/pilot_threearm.py（S1/S2 主脚本：断点续跑+门控修复版）+ experiments/ckpt/（6 个训练 "
    "checkpoint 在盘）+ experiments/consolidate_progress.py（分片→规范位合并，重叠键冲突检测）+ "
    "experiments/s3_inspect_progress.py（缺口盘点）+ experiments/s3_per_seed_numbers.py（逐种子实算）+ "
    "experiments/s3_final_check.py（终态校验）+ experiments/eval_resume.log（续跑日志）。"
    "历史产物链（design.md H1/H2+E1-E4+D1-D7+S0-S2+门线+F1-F4、workflow.json S1-S6、screening/判读文档）见下文各节。"
)
a = s.index("- 最近产物：")
b = s.index("\n", a)
s = s[:a] + NEW_ART + s[b:]

NEW_NEXT = (
    "- 下一步：S4-pilot-verdict 判读（researcher；S3 机器态已 done、S4 depends_on 满足可派）：首里程碑②③"
    "验收+H1/H2 adjudicate。必带双 caveat：QuickDraw 数据集降级（N-MNIST 五通道 SSL 墙+代理 7897 全灭，"
    "DECISIONS 2026-10-26 02:1x 正式拍板）+D7 保真度缺口（A@clean=10.43% chance 级 vs 论文 Table III "
    "QuickDraw clean≈98.6-98.7%）。判读要点（完整数据 CSV 实算）：机械门控 C 臂 block5 C−A=+5.36pp 过线且 "
    "C clean 降幅 +0.08pp ≤0.5pp、逐种子 +4.08/+4.78/+7.24 一致；B−A=−0.71pp 在噪声内（σ≈0.55pp/格，"
    "F1 字面条件对 B 臂成立但 C 臂保守存活门控先触发、D3 预注册语义）；H2 Δ=−0.02pp 不成立；uniform30 "
    "C−A=+4.94pp 但 block15 C−A 降至 +1.78pp；A/B 输出恒定类（clean 三模式逐种子恒等）表明 pilot 训练远未"
    "收敛，chance 级基数上的臂间差不构成机制证据→建议默认 replicate→S5 全量协议（30 epoch 全量数据保真度"
    "复现+N-MNIST 结论级基准+E2 B-train 对照臂），负结果分支不启动；最终 verdict 由 S4 出。派发要素："
    "researcher profile + openrouter-rotator 路由。N-MNIST 数据通道移出今夜队列（daytime/user-assisted "
    "info_need：用户可提供免墙镜像，experiments/ 脚本可直接重跑）；harvest 两条检索（2501.15330）移交 S4 "
    "参考。三臂判据与失败条件按 dossier _state/candidate-lnn-gap-cfc-20261025.json + design.md。"
)
c = s.index("- 下一步：")
d = s.index("\n", c)
s = s[:c] + NEW_NEXT + s[d:]

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(s)
print("STATUS.md updated:", len(s), "chars")
