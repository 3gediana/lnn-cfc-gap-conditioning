#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s6_judge_c74da_update_workflow.py — 判读单元 c74da1aa（算子优化先行单元回执）机器态修正：
- S5-full-protocol: done → ready（科学完成判据=结论级表 108 行 CSV/MD 未出；
  算子单元是续跑链 checkpoint 单元非阶段收口；result 保留为 checkpoint 回执并加判读标注）
- S5-full-protocol-continue 空阶段（驱动器 apply_result 按 next_action=continue 自动创建、
  无任何动作字段）→ done+result 关闭（superseded by S5 续跑链后续单元；先例=00:5x/03:4x/04:1x 同型三例）
- lessons 追加 receipt_judged、updated_at 刷新
"""
import json
import os

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(P, "workflow.json")

with open(WF, encoding="utf-8") as fh:
    w = json.load(fh)

s5 = [s for s in w["stages"] if s.get("id") == "S5-full-protocol"][0]
assert s5["status"] == "done", f"预期 S5=done（驱动器 03:00 apply_result 写入），实际 {s5['status']}"

s5["status"] = "ready"
r = s5.get("result") or {}
r["judged_by"] = ("researcher 判读单元 2026-10-27T03:2x（unit.receipt c74da1aa7b4347f9b1c270f191d3b9a8；"
                  "判读全文 notes/researcher-interventions/c74da1aa7b4347f9b1c270f191d3b9a8.md）："
                  "本 result 为第六单元（算子优化先行 checkpoint 单元）回执，非 S5 阶段收口——"
                  "S5 科学完成判据（results/full_threearm.csv/md 结论级表=全量+≥3 种子+±std）未达成，"
                  "算子单元科学交付 PASS（首轮全量独立复跑：operator_bench identity 项逐位一致、"
                  "selftest 68 项/evalpatch 48 用例/ckpt 3×30-30 全 PASS、禁批量训练纪律遵守），"
                  "stage 状态由驱动器 apply_result 误置 done 改回 ready，C 臂重训+108 格重算由续跑链续派")
r["checkpoint_unit"] = "S5 第六单元（算子优化先行，fb-ab50d0ec9f），commit ca44643"
s5["result"] = r

cont = [s for s in w["stages"] if s.get("id") == "S5-full-protocol-continue"][0]
assert cont["status"] == "ready", f"预期 continue=ready，实际 {cont['status']}"
cont["status"] = "done"
cont["result"] = {
    "status": "ok",
    "project": "液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a",
    "stage": "S5-full-protocol-continue",
    "stage_id": "S5-full-protocol-continue",
    "result_kind": "document",
    "source_mode": "manual",
    "historical": False,
    "source": None,
    "result_files": ["notes/researcher-interventions/c74da1aa7b4347f9b1c270f191d3b9a8.md"],
    "artifacts": ["notes/researcher-interventions/c74da1aa7b4347f9b1c270f191d3b9a8.md"],
    "metrics": {},
    "verdict": "inconclusive",
    "reproduction": "判读依据 notes/researcher-interventions/c74da1aa7b4347f9b1c270f191d3b9a8.md 机器态节",
    "next_action": "continue",
    "commits": [],
    "next_units": [],
    "notes": ("驱动器 apply_result 按第六单元回执 next_action=continue 自动创建的空阶段（无 actions/inputs/outputs，"
              "派发=无动作 vague 单元）；S5-full-protocol 本身未收口（结论级表未出）已由判读单元改回 ready，"
              "C 臂重训+108 格重算由 S5 ready 状态续跑链自动派发，本条目 superseded 不再单独派发；"
              "处置先例=00:5x 关闭 S2-pilot-gate-checks-continue、03:4x 关闭 S3-pilot-threearm-replicate、"
              "04:1x 关闭 S4-pilot-verdict-replicate，同型第四例；由 researcher 判读单元 c74da1aa 落账")
}

w["lessons"].append({
    "at": "2026-10-27T03:2x+08:00",
    "type": "receipt_judged",
    "note": ("S5 第六单元（算子优化先行，unit 716807f799aa433683a28163397d3c90，commit ca44643）ok 回执判读属实 PASS"
             "（首轮全量独立复跑：operator_bench.py 复跑 exit=0 identity 项逐位一致——N0 A≡B=0.912109375 exact、"
             "N5 manual-loop 恒等 4.05e-06 exact、E2 identity mirror 全 equal，计时项 ±3-9% 波动不改变结论；"
             "full_protocol selftest 68 项 exit=0+eval_patch_selftest 48 用例 exit=0+s5_ckpt_verify.py exit=0"
             "（3 ab ckpt 30/30 acc 0.9518/0.9661/0.9688 size 逐一未变）三重复跑；禁 30epoch 批量训练纪律遵守"
             "（progress/full_*/ckpt 零改动，find 实证 ckpt/ 无 02:29 后新文件））。结论确认=零修复落地"
             "（E3 数据否决唯一候选 FIX-1：复跑 +0.7% 仍噪声内）+F8 算子墙入 stop_conditions（四墙台账+无阻塞判定）"
             "+科学路径前向数值逐位不变→A/B ckpt 不需重训+C 臂重训排产不变。"
             "机器态修正=驱动器 apply_result 按 ok 回执把 S5 误置 done（S5 科学完成判据结论级表未出、"
             "算子单元是 checkpoint 单元非收口）→改回 ready；S5-full-protocol-continue 空阶段按先例关闭" +
             "（同型第四例）。新拍板=W-LAUNCH 不击穿（compile/融合改变前向数值→A/B 重训 4.6h 收益/代价不成比例，"
             "未来新臂训练启动前可重评）。两处小不精确勘误（MD/回执 E4 逐样本 ms 数互换、speedup 56.0 vs 57.8，"
             "不影响结论）。next_units=[]（S5 续跑链由 workflow 分支自动派、手写拒收）；"
             "唤醒点=下一回执（C 臂重训进度 ckpt epochs_done vs 回执 ep 计数、seed 新启速率 ~50s/ep）"
             "或训练 6/6 齐+108 行 CSV/MD 落盘（S5 收口判读）或硬失败；看板 t_f6e7bac5 sqlite 评论同步")
})
w["updated_at"] = "2026-10-27T03:2x+08:00"

with open(WF, "w", encoding="utf-8") as fh:
    json.dump(w, fh, ensure_ascii=False, indent=2)

with open(WF, encoding="utf-8") as fh:
    w2 = json.load(fh)
s5b = [s for s in w2["stages"] if s.get("id") == "S5-full-protocol"][0]
contb = [s for s in w2["stages"] if s.get("id") == "S5-full-protocol-continue"][0]
assert s5b["status"] == "ready", "S5 改回 ready 失败"
assert "checkpoint_unit" in s5b.get("result", {}), "S5.result 判读标注失败"
assert contb["status"] == "done" and contb["result"]["notes"].startswith("驱动器 apply_result"), "continue 关闭失败"
assert w2["lessons"][-1]["type"] == "receipt_judged", "lessons 追加失败"
ready = [s["id"] for s in w2["stages"] if s.get("status") == "ready"]
assert ready == ["S5-full-protocol"], f"ready 阶段应唯一=S5-full-protocol，实际 {ready}"
print("workflow.json updated: S5 done->ready, continue closed, lessons appended")
print("ready_stages:", ready)
