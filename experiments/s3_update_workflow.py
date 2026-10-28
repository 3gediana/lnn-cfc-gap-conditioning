#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s3_update_workflow.py — workflow.json 机器态：S3-pilot-threearm → done + result + dispatch_log；
u_status U5_runtime → closed。commits 由命令行参数传入（第一次提交 sha）。"""
import json
import os
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(PROJECT, "workflow.json")
SHA = sys.argv[1] if len(sys.argv) > 1 else ""

with open(PATH, encoding="utf-8") as fh:
    wf = json.load(fh)

stage = next(s for s in wf["stages"] if s.get("id") == "S3-pilot-threearm")
stage["status"] = "done"
stage["result"] = {
    "status": "ok",
    "project": wf["project"],
    "stage": "pilot",
    "stage_id": "S3-pilot-threearm",
    "result_kind": "scientific_result",
    "source_mode": "live",
    "historical": False,
    "source": None,
    "result_files": [
        "results/pilot_threearm.csv",
        "results/pilot_threearm.md",
        "results/pilot_progress.json",
        "results/pilot_timing.json",
        "experiments/pilot_threearm.py",
        "experiments/ckpt/"
    ],
    "artifacts": [
        "results/pilot_threearm.csv",
        "results/pilot_threearm.md",
        "results/pilot_progress.json",
        "results/pilot_timing.json",
        "experiments/pilot_threearm.py",
        "experiments/ckpt/"
    ],
    "metrics": {
        "eval_rows_total": 108,
        "eval_rows_prev_units": 98,
        "eval_rows_this_unit": 10,
        "eval_sec_this_unit": 208.0,
        "acc_clean_A": 0.1043,
        "acc_clean_B": 0.1043,
        "acc_clean_C": 0.1051,
        "acc_uniform30_A": 0.1327,
        "acc_uniform30_B": 0.1292,
        "acc_uniform30_C": 0.1821,
        "acc_block5_A": 0.1369,
        "acc_block5_B": 0.1298,
        "acc_block5_C": 0.1906,
        "acc_block15_A": 0.1442,
        "acc_block15_B": 0.1369,
        "acc_block15_C": 0.162,
        "B_minus_A_clean_pp": 0.0,
        "C_minus_A_clean_pp": 0.08,
        "B_minus_A_uniform30_pp": -0.35,
        "C_minus_A_uniform30_pp": 4.94,
        "B_minus_A_block5_pp": -0.71,
        "C_minus_A_block5_pp": 5.36,
        "C_minus_A_block5_per_seed_pp": [4.08, 4.78, 7.24],
        "B_minus_A_block15_pp": -0.73,
        "C_minus_A_block15_pp": 1.78,
        "H2_block15_minus_block5_pp": -0.02,
        "sanity_clean_A_equals_B_pp": 0.0,
        "sanity_clean_A_equals_B_pass": True,
        "sanity_A_uniform30_z_vs_chance": 5.97,
        "sanity_A_uniform30_direction_pass": True,
        "D7_A_clean_fidelity_97_pass": False,
        "gate_pass_arm": "C",
        "gate_decision": "pass",
        "merge_crosscheck_csv_byte_identical": True,
        "selftest_exit_code": 0
    },
    "verdict": "inconclusive",
    "reproduction": (
        "cd 课题目录 && G:/ai/python11/python.exe experiments/consolidate_progress.py（分片 98 行 union 写回规范位）"
        " && G:/ai/python11/python.exe experiments/pilot_threearm.py eval（断点续跑：跳过 98 行只算缺的 10 格，"
        "108 行齐后自动落 CSV/MD/timing/verdict） && G:/ai/python11/python.exe experiments/merge_eval_shards.py "
        "--canonical（union 交叉校验+规范位 consolidated） && G:/ai/python11/python.exe "
        "experiments/eval_patch_selftest.py（回归 exit=0；terminal python，execute_code 内核无 torch 禁用）"
    ),
    "next_action": "replicate",
    "commits": [SHA],
    "next_units": [
        {
            "project": wf["project"],
            "instruction": (
                "S4-pilot-verdict 判读（researcher）：S3 已收口，108/108 行+四份契约产物在盘。首里程碑②③验收"
                "（A@clean≥97% 未达=10.43% chance 级、clean A≡B=0.000pp 过）+H1/H2 adjudicate。必带双 caveat："
                "QuickDraw 数据集降级（N-MNIST SSL 墙）+D7 保真度缺口。判读要点：机械门控 C 臂 block5 C−A=+5.36pp "
                "过线（逐种子 +4.08/+4.78/+7.24）、C clean 降幅 +0.08pp；B−A=−0.71pp 噪声内（F1 字面条件对 B 臂"
                "成立但 C 臂保守存活门控先触发）；H2 Δ=−0.02pp 不成立；A/B 输出恒定类表明 pilot 远未收敛→建议默认 "
                "replicate→S5 全量协议（30 epoch 全量保真度复现+N-MNIST 结论级+E2 B-train 对照），负结果分支不启动。"
            ),
            "estimate_min": 30,
            "stage": "S4-pilot-verdict"
        }
    ],
    "notes": (
        "S3 三补单元收口：先合并后续跑（consolidate 98 行→eval 只算缺的 10 格 208s≈21s/行，避免重算 24 格）；"
        "merge --canonical 双路径互证 CSV 逐字节一致；selftest exit=0。verdict=inconclusive：H1/H2 因 D7 保真度"
        "缺口（A@clean=10.43% chance 级、A/B 输出恒定类）pilot 不足以 adjudicate，机械门控 decision=pass/"
        "gate_pass_arm=C 如实记录，最终 verdict 由 S4 出。已知不阻塞项：shard_timing 为空（分片进程硬超时未及"
        "写 timing），真实计时以 resume_eval_run eval_sec=208.0 为准。"
    )
}
stage.setdefault("dispatch_log", []).append({
    "at": "2026-10-26T03:3x+08:00",
    "unit_id": "lab-executor night unit (S3-pilot-threearm 三补)",
    "outcome": "ok",
    "kind": "三补实跑（union 98→108 行齐）：consolidate 分片 14 行写回规范位（76 重叠键零冲突）→canonical eval 跳过 98 行只算缺的 10 格（seed2 B/C × block5-30 模式1,2+block15-30 模式0,1,2）实测 208s→merge --canonical 交叉校验（union=108、CSV 逐字节一致）→selftest exit=0",
    "scientific_work": "四份契约产物落盘（pilot_threearm.csv 108 数据行/MD/progress 带 verdict/timing eval_sec=208.0）；最终数：clean A=B=10.43%（B−A 逐种子恒 0.00pp）、block5-30 B−A=−0.71pp/C−A=+5.36pp（逐种子 +4.08/+4.78/+7.24）、block15-30 C−A=+1.78pp、H2 Δ=−0.02pp；门控三门（A≡B 0.000pp PASS、z=5.97 PASS、D7 10.43% 未达）；机械门控 gate_pass_arm=C/decision=pass；verdict=inconclusive（保真度缺口不足以 adjudicate H1/H2）",
    "judged_by": "待 S4-pilot-verdict researcher 判读（首里程碑②③+H1/H2）",
    "stage_status_after_judgment": "done（本单元置；S4 depends_on 满足可派）"
})

if "u_status" in wf:
    wf["u_status"]["U5_runtime"] = (
        "closed (S3 收口：results/pilot_timing.json 真实计时在盘——三补单元 canonical eval 续跑 208s/10 格≈21s/行；"
        "全矩阵历史墙钟：串行 22.5s/行、三路分片争抢劣化 60s/行（02:5x 实证）；shard_timing 空为已知不阻塞项)"
    )

with open(PATH, "w", encoding="utf-8") as fh:
    json.dump(wf, fh, ensure_ascii=True, indent=2)
    fh.write("\n")
print("workflow.json updated: S3 status =", stage["status"],
      "| dispatch_log entries =", len(stage["dispatch_log"]),
      "| U5 =", wf.get("u_status", {}).get("U5_runtime", "")[:40])
