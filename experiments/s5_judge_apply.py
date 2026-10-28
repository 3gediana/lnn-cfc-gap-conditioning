#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_judge_apply.py — researcher 判读单元 0a3623a4 落账：workflow.json + STATUS.md + DECISIONS.md。"""
import io
import json
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUDGE_MD = "notes/researcher-interventions/0a3623a4cc614ab4bb7d8938cd659eeb.md"

# ---------------- workflow.json ----------------
wf_path = os.path.join(PROJ, "workflow.json")
with io.open(wf_path, encoding="utf-8") as fh:
    wf = json.load(fh)

NEW_ACTIONS = (
    "续跑链（2026-10-26T04:4x 判读 unit.receipt 0a3623a4cc614ab4bb7d8938cd659eeb 后更新）："
    "首单元已落 experiments/full_protocol.py 并跑到 seed0_ab ep7/30（train acc 0.40→0.8993 收敛中，"
    "逐 epoch 原子 ckpt 完好、selftest 独立复跑 exit=0）。第二单元起=重跑 "
    "G:/ai/python11/python.exe experiments/full_protocol.py all：自动从 seed0_ab ep8 无损续跑"
    "（model+opt+epoch+history 全恢复，train_one_full:151-160），6 训练逐个查 ckpt、已跑齐的跳过；"
    "跑不完写断点不硬撑（每 epoch 原子落盘 kill 无损）；训练齐后自动进 108 格评测（逐行落盘断点续跑）"
    "→齐 108 行自动落 results/full_threearm.csv/md 并按 S5 判读须知出总结。"
    "排产实测基准：ab≈46s/epoch、c≈64s/epoch、eval A 1.2s/B 52.4s/C 52.7s 每格@n=7500"
    "（探针 experiments/s5_eval_cost_probe.py）→剩余≈2.7h 训练+≈64min 评测，多单元 checkpoint 链，"
    "尾部可能超夜窗交下一窗/白天。禁手写并行分片（progress 写竞争+GPU 争抢双风险，S3 有实证）。"
    "S5 判读须知不变：meanpool 主口径三口径兼报、C clean 逐种子门控、A/B 恒定类消失伴生判据、"
    "D7 结论级=复现论文 Table III QuickDraw ≈98.6-98.7% 数量级。"
    "E2 B-train 对照臂与 N-MNIST 结论级基准留后续 checkpoint 单元（N-MNIST=daytime/user-assisted info_need）。"
)

RELEASE_APPEND = (
    "；2026-10-26T04:4x 判读 unit.receipt 0a3623a4cc614ab4bb7d8938cd659eeb：首单元 partial 属实 PASS"
    "（本单元独立复跑 selftest exit=0+kill 后 ckpt 完整性校验+续跑路径代码级核验，回执零失实），"
    "维持 ready，actions 更新为续跑语义（第二单元起重跑 all 从 seed0_ab ep8 续；剩余训练≈2.7h+eval 实测≈64min；"
    "禁手写并行分片）"
)

n_stage = 0
for s in wf.get("stages", []):
    if s.get("id") == "S5-full-protocol":
        s["actions"] = NEW_ACTIONS
        s["放行依据"] = s.get("放行依据", "") + RELEASE_APPEND
        n_stage += 1
assert n_stage == 1, f"S5 stage patch count={n_stage}"

wf.setdefault("lessons", []).append({
    "at": "2026-10-26T04:4x+08:00",
    "type": "receipt_judged",
    "note": ("S5 首单元 partial 回执 0a3623a4 判读属实 PASS（独立复跑 selftest exit=0+kill 后 ckpt 完整性"
             "+续跑路径代码级核验，零失实）；新发现=eval 108 格耗时实测 63.8min（A 1.2s/B 52.4s/C 52.7s 每格@7500，"
             "原 8-10min 估计作废，探针 experiments/s5_eval_cost_probe.py 固化）；S5 维持 ready 续跑链、"
             "驱动器已重排 resume 单元（not_before 04:36:52）故 next_units=[]；排产=剩余≈2.7h 训练+≈64min 评测"
             ">夜窗剩余≈3.2h，预计 4-5 个 checkpoint 单元尾部交下一窗；下一唤醒点=下一回执或训练齐+108 行表落盘"),
})
wf["updated_at"] = "2026-10-26T04:4x+08:00"

with io.open(wf_path, "w", encoding="utf-8") as fh:
    json.dump(wf, fh, ensure_ascii=False, indent=1)
print("workflow.json updated: S5 actions+放行依据+lessons+updated_at")

# ---------------- STATUS.md ----------------
st_path = os.path.join(PROJ, "STATUS.md")
with io.open(st_path, encoding="utf-8") as fh:
    st = fh.read()

NEW_BULLET = (
    "- 阶段：**active / S5-full-protocol 续跑链（2026-10-26T04:4x researcher 判读 unit.receipt "
    "0a3623a4cc614ab4bb7d8938cd659eeb：首单元 partial/checkpointed 属实 PASS——本单元独立复跑 "
    "full_protocol.py selftest exit=0 四项全过（d2 恒等 68 项、full_splits 42500/7500、1+1 续跑 "
    "max|Δstate|=0、eval 冒烟 A≡B+掩码率 0.305）；full_quickdraw_seed0_ab.pt ep7/30 kill 后校验完整"
    "（history 1-7 连续+opt 在盘+train acc 0.8993@323s）；续跑路径代码级核验（train_one_full:151-160 "
    "从 ep8 无损续跑+eval 逐行断点+双原子写）。下一步=下一单元重跑 G:/ai/python11/python.exe "
    "experiments/full_protocol.py all 自动续跑（seed0_ab ep8 起；剩余 6 训练≈2.7h+108 格评测实测≈64min"
    "→齐 108 行自动落 results/full_threearm.csv/md 并按 S5 须知判读）。**新发现=eval 耗时实测纠正**："
    "A 1.2s/B 52.4s/C 52.7s 每格@n=7500→108 格 3827s≈63.8min（探针 experiments/s5_eval_cost_probe.py，"
    "随机权重同计算路径），交接单 8-10min 估计无依据作废；禁手写并行分片（progress 写竞争+GPU 争抢）。"
    "排产≈3.7h>夜窗剩余≈3.2h→预计 4-5 个 checkpoint 单元、尾部交下一窗/白天，不硬撑不缩数据。"
    "时间戳勘误：首单元节 05:2x 应为 04:2x-04:3x（driver log+mtime 实证）。E2 B-train 与 N-MNIST 结论级仍留后续"
    "（N-MNIST=daytime/user-assisted info_need）。判读全文 " + JUDGE_MD + "）**——\r\n"
)

ANCHOR = "# 状态\r\n\r\n"
if ANCHOR not in st:
    ANCHOR = "# 状态\n\n"
assert ANCHOR in st, "STATUS.md anchor not found"
st = st.replace(ANCHOR, ANCHOR + NEW_BULLET, 1)

OLD_HEAD = "- 最近更新：2026-10-26T04:1x+08:00（researcher 判读 unit.receipt 874c5f01，S4 收口 ok）："
NEW_HEAD = (
    "- 最近更新：2026-10-26T04:4x+08:00（researcher 判读 unit.receipt "
    "0a3623a4cc614ab4bb7d8938cd659eeb，S5 首单元 partial）：partial 属实 PASS（独立复跑 selftest exit=0"
    "+kill 后 ckpt 完整性+续跑路径代码级核验，回执零失实）；S5 维持 ready 续跑链，驱动器 04:35:52 已重排 "
    "S5 resume 单元（not_before=04:36:52、attempts=1）故本判读 next_units=[]；新发现=eval 108 格耗时实测 "
    "63.8min（A 1.2s/B 52.4s/C 52.7s 每格@7500），8-10min 估计作废；排产=剩余训练≈2.7h+eval≈64min≈3.7h"
    ">夜窗剩余≈3.2h，预计 4-5 个 checkpoint 单元尾部交下一窗；唤醒点=下一回执或训练齐+108 行表落盘。"
    "上次更新：2026-10-26T04:1x+08:00（researcher 判读 unit.receipt 874c5f01，S4 收口 ok）："
)
assert OLD_HEAD in st, "STATUS.md 最近更新 head not found"
st = st.replace(OLD_HEAD, NEW_HEAD, 1)

with io.open(st_path, "w", encoding="utf-8") as fh:
    fh.write(st)
print("STATUS.md updated: 判读节置顶+最近更新刷新")

# ---------------- DECISIONS.md ----------------
dec_path = os.path.join(PROJ, "notes", "DECISIONS.md")
with io.open(dec_path, encoding="utf-8") as fh:
    dec = fh.read()

ENTRY = (
    "\r\n- 2026-10-26 04:4x 判读（unit.receipt 0a3623a4cc614ab4bb7d8938cd659eeb，S5-full-protocol 首单元 "
    "partial/checkpointed，执行单元 7580eceaa3c24251a6be27c48661b2bd，duration 1166.2s；判读全文 "
    + JUDGE_MD + "）：**partial 属实 PASS，S5 维持 ready 走续跑链**。①三重独立核验（本单元自己跑）："
    "复跑 full_protocol.py selftest → exit=0 OVERALL PASS（d2 向量化 vs 循环版 68 项 case-device 恒等 CPU+GPU、"
    "full_splits 42500/7500 确定性+pilot 子集⊂全量 sampled200、1+1 epoch 续跑 vs 2 epoch 一次跑 max|Δstate|=0.00e+00 "
    "两臂、eval 冒烟 A≡B+block5-30 掩码率 0.305）；复跑 s5_ckpt_verify.py 实证 kill 后 ckpt 完整"
    "（full_quickdraw_seed0_ab.pt epochs_done=7/30、history 1-7 连续、opt state 在盘、3031243B、"
    "train acc 0.3979→0.8993 七点、323.2s）；续跑路径代码级核验（train_one_full:151-160 断点全恢复从 ep8 续、"
    "all 分支:617-636 六训练逐个查 ckpt、eval 分支:658-674 未齐拒绝评测、run_eval_matrix_full:242-263 逐行原子落盘+跳过、"
    "_atomic_torch_save:131-134/save_progress:223-228 双原子写）。②回执零失实（metrics 12 项与盘上逐项一致，"
    "对比 S3 链三处失实先例）。③**新发现=eval 耗时估计失据+实测拍板**：交接单/STATUS 称 108 格「向量化后预计约 8-10min」"
    "无实测依据（pilot B/C ≈21s/格@n=3000 线性外推即 ≈52s/格@7500）；本单元写探针实测（随机权重模型、同 L=100/同 manual-loop "
    "路径、n=7500/格）：A 1.2s、B 52.4s、C 52.7s 每格→108 格外推 3827s≈63.8min——**拍板：后续排产以 64min 为基准，"
    "8-10min 说法作废**；探针固化 experiments/s5_eval_cost_probe.py（可复用于任何同架构评测耗时声称）。"
    "④时间戳勘误：STATUS/DECISIONS 的 S5 首单元节写 05:2x，实际 04:16:26 启动、04:35:52 收尾（driver 日志+mtime 实证），"
    "应为 04:2x-04:3x；不影响决策，记录备查。⑤机器态：S5-full-protocol 维持 **ready**（不写 done/result——结论级表未出，"
    "partial 不当科学完成；无新增空阶段因 next_action=continue）；actions 更新为续跑语义（第二单元起重跑 all 从 seed0_ab ep8 续、"
    "排产实测基准入 actions、禁手写并行分片）；lessons 追加 receipt_judged、updated_at 刷新。⑥派发要素：kind=experiment→"
    "role=executor→profile=**lab-executor**、路由=profile 默认 **openrouter-rotator**（S5 首单元同路由 1166s 实跑无 prior "
    "failure）、reasoning=high、依赖全在盘（full_protocol.py+selftest 复跑 PASS+seed0_ab ep7 ckpt+data/quickdraw 全量+门控 accepted "
    "交接单+S5 须知已入 summarize_full）；排产实测=剩余训练≈160min（23×46.2s+3×30×64s+2×30×46.2s）+eval≈64min≈3.7h>夜窗剩余≈3.2h"
    "（终点 07:59:58）→预计 4-5 个 checkpoint 单元、尾部（很可能 eval 后段）交下一窗/白天，不硬撑不缩数据（缩数据=毁结论级资格）；"
    "**next_units=[]**（驱动器 04:35:52 已把 S5 resume 单元重排入队 not_before=04:36:52 attempts=1，手写入队会被 "
    "_reconcile_queue 以 workflow-ready-stage-preferred 拒收，02:46/03:4x 两起实证）；researcher 唤醒点=下一回执到达"
    "（核对 sec/epoch 滚动实测 vs 估计、eval 首 3 行实测速率）或训练 6/6 齐+108 行 CSV/MD 落盘（S5 收口判读：首里程碑②③结论级"
    "+H1/H2 复验+双 caveat）；E2 B-train 对照臂与 N-MNIST 结论级基准仍留后续单元（N-MNIST=daytime/user-assisted info_need 不变）。"
    "⑦经验沉淀：「预计 X 分钟」类估计必须附实测或外推依据，否则判读单元用随机权重探针实测纠正（本次 7 倍差，模式固化）；"
    "「partial 判读三件套」（独立复跑入口脚本+kill 后 ckpt 完整性校验+续跑路径行号级核验）第五次零成本验证全链；"
    "下一执行单元收工自查加一项=每 (seed,arm) 训练跑完即把 sec/epoch 滚动实测写进 progress/STATUS、eval 首 3 行出来后立即重估全量并落 STATUS。"
)
dec = dec.rstrip("\r\n") + ENTRY
with io.open(dec_path, "w", encoding="utf-8") as fh:
    fh.write(dec)
print("DECISIONS.md updated: 判读条目追加")
