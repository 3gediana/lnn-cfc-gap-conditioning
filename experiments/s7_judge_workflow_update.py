# -*- coding: utf-8 -*-
"""S7 判读落机器态：workflow.json S7-e2-btrain-arm ready→done+result（receipt 契约字段补全），
刷新 updated_at，追加 lesson。用 json load/dump 保证语法合法。"""
import json, os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(ROOT, "workflow.json")

with io.open(WF, encoding="utf-8") as f:
    wf = json.load(f)

stage = None
for s in wf["stages"]:
    if s["id"] == "S7-e2-btrain-arm":
        stage = s
        break
assert stage is not None, "S7 stage not found"
assert stage["status"] == "ready", f"unexpected status {stage['status']}"

stage["status"] = "done"
stage["result"] = {
    "status": "ok",
    "project": wf["project"],
    "stage": "S7-e2-btrain-arm",
    "stage_id": "S7-e2-btrain-arm",
    "result_kind": "scientific_result",
    "source_mode": "live",
    "historical": False,
    "source": "",
    "result_files": [
        "results/e2_btrain.csv",
        "results/e2_btrain.md",
        "results/e2_btrain_progress.json",
        "results/e2_btrain_timing.json",
        "experiments/e2_btrain.py",
        "experiments/ckpt/full_quickdraw_seed0_d.pt",
        "experiments/ckpt/full_quickdraw_seed1_d.pt",
        "experiments/ckpt/full_quickdraw_seed2_d.pt",
        "experiments/s7_judge_0297_recheck.py",
        "experiments/s7_judge_0297_recheck.txt",
        "notes/handoff/S7-e2-btrain-arm.md",
        "notes/researcher-interventions/0297fdde45ac4cbc9dcc4defb11e40b0.md",
    ],
    "artifacts": [
        "results/e2_btrain.csv",
        "results/e2_btrain.md",
        "results/e2_btrain_progress.json",
        "experiments/e2_btrain.py",
        "experiments/ckpt/full_quickdraw_seed0_d.pt",
        "experiments/ckpt/full_quickdraw_seed1_d.pt",
        "experiments/ckpt/full_quickdraw_seed2_d.pt",
    ],
    "metrics": {
        "executor_unit": "0dce44084bad43d8b9fc8ef8e478dcee",
        "executor_receipt_status": "failed_empty_shell_judged_ok",
        "judge_recheck_exit": 0,
        "csv_rows": 144,
        "s5_crosscheck_mismatches": 0,
        "d_ckpts_30ep": 3,
        "block5_D_minus_A_pp": 15.31,
        "block5_D_minus_A_per_seed_pp": [21.85, 9.69, 14.38],
        "block5_D_minus_C_pp": -2.18,
        "block5_C_minus_A_pp": 17.49,
        "clean_D_minus_A_pp": 0.24,
        "clean_D_minus_A_per_seed_pp": [1.94, -1.92, 0.71],
        "uniform30_D_minus_A_pp": 20.48,
        "uniform30_D_minus_C_pp": -1.69,
        "block15_D_minus_A_pp": 7.96,
        "block15_D_minus_C_pp": -2.75,
        "attribution_ratio_D_minus_A_over_C_minus_A": 0.8752,
        "criterion_decision_twosided": "3_partial_attribution",
        "criterion_decision_onesided_literal": "1_E2_refuted",
        "meanpool_pct": {
            "clean_A": 92.3, "clean_B": 92.3, "clean_C": 92.89, "clean_D": 92.54,
            "uniform30_A": 63.93, "uniform30_B": 64.37, "uniform30_C": 86.1, "uniform30_D": 84.41,
            "block5_A": 71.03, "block5_B": 69.81, "block5_C": 88.52, "block5_D": 86.33,
            "block15_A": 72.83, "block15_B": 72.03, "block15_C": 83.55, "block15_D": 80.8,
        },
    },
    "verdict": "supported",
    "E2_verdict": "refuted_in_strong_sense: training-period-activated timespans pathway carries 87.5% of C-A gain; gap indicator bit marginal -2.18pp",
    "reproduction": "cd 课题目录 && G:/ai/python11/python.exe experiments/s7_judge_0297_recheck.py（独立复算：CSV 结构+配对差+判据机械输出+S5 对账+ckpt 直读，exit=0=ALL PASS）；原实验入口=G:/ai/python11/python.exe experiments/e2_btrain.py",
    "next_action": "continue",
    "commits": ["45d1286"],
    "next_units": [],
    "judged_by": "researcher 夜间判读单元 2026-10-31T03:0x（unit 0dce44084bad43d8b9fc8ef8e478dcee failed 空壳回执；判读全文 notes/researcher-interventions/0297fdde45ac4cbc9dcc4defb11e40b0.md；首轮全量独立复跑 exit=0 ALL PASS）",
    "notes": "failed 空壳=科学交付 PASS、收尾格式失败（第三次同型先例）；E2 归因终判：训练期激活时间通路贡献 C-A(+17.49pp) 的 87.5%（D-A=+15.31pp），gap 指示位边际 -2.18pp；预注册判据双约定并报（双侧=③部分归因/单侧字面=①E2 被反驳），结论对约定选择稳健；caveat=QuickDraw 降级+D7 缺口+final 口径 D-A 仅 +0.41pp（meanpool 为预注册主口径）。",
}

wf["updated_at"] = "2026-10-31T03:0x+08:00"
wf.setdefault("lessons", []).append({
    "at": "2026-10-31T03:0x+08:00",
    "type": "receipt_judged",
    "note": "S7-e2-btrain-arm 收口判读（unit 0dce44084bad43d8b9fc8ef8e478dcee failed 空壳回执，判读全文 notes/researcher-interventions/0297fdde45ac4cbc9dcc4defb11e40b0.md）：failed 空壳=科学交付 PASS、收尾格式失败（第三次同型先例，勘误为 ok）；首轮全量独立复跑 experiments/s7_judge_0297_recheck.py exit=0 ALL PASS（CSV 144 行/键唯一、A/B/C 与 S5 表 108 格 mismatches=0、3 D ckpt 30/30、掩码率≈0.30）。E2 终判=训练期激活的时间通路贡献 C-A(+17.49pp) 增益 87.5%（D-A=+15.31pp 逐种子 +21.85/+9.69/+14.38）、gap 指示位边际 -2.18pp；预注册判据双约定并报（双侧=③部分归因 ratio 0.8752/单侧字面=①E2 被反驳），冻结纪律不改判。机器态=S7 done+result（receipt 契约字段由本判读补全）；S8/S9 维持 ready 由 workflow 分支自动派（next_units=[]）；S6 维持 gated。复盘=复算脚本首版逐种子配对误取单格 pattern[0] 被自身第二轮抓出修正——逐种子配对必须按 (seed,pattern) 跨臂同模式键（D4 语义）。",
})

with io.open(WF, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

# 自校验
with io.open(WF, encoding="utf-8") as f:
    wf2 = json.load(f)
st = [s for s in wf2["stages"] if s["id"] == "S7-e2-btrain-arm"][0]
ready = [s["id"] for s in wf2["stages"] if s.get("status") == "ready"]
print("OK S7 status =", st["status"], "| result keys =", sorted(st["result"].keys())[:5], "...")
print("ready stages =", ready)
print("lessons tail at =", wf2["lessons"][-1]["at"])
print("updated_at =", wf2["updated_at"])
