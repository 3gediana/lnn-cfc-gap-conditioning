#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_judge_710a_update_workflow.py — 判读单元 710a1c50 更新 workflow.json S5 阶段。

- S5.actions：前置「第六单元起=算子优化先行」指令（fb-ab50d0ec9f），旧文本转历史沿革
- estimate_min：35 → 60（算子 bench+修复+回归）
- 放行依据：追加本判读条目
- lessons：追加 receipt_judged 条目
- updated_at 刷新
"""
import json
import os

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(P, "workflow.json")

with open(WF, encoding="utf-8") as fh:
    w = json.load(fh)

s5 = [s for s in w["stages"] if s.get("id") == "S5-full-protocol"][0]
old_actions = s5["actions"]

new_block = (
    "续跑链（2026-10-27T02:1x 判读 unit.receipt 710a1c50feff4a9ab0943e929ad06ab6 后更新）："
    "**第六单元起=算子优化先行单元（fb-ab50d0ec9f「先优化算子再跑实验」，2026-10-27T01:28 phone/global 生效至 11-03；"
    "本单元禁止任何 30epoch 批量训练）**。"
    "背景：第五单元（unit 6e9acd73c626431abd4f28ac2c49df9a，00:16:37-01:41:09）科学交付已判读 PASS——训练 6/6 收口+108 格落表后"
    "发现掩码 Convention 倒挂 bug（预注册 D2 mask=1=零填充 vs 实现 xb*mask 保留掩码帧，clean 输入全清零→chance），"
    "六项证据（experiments/s5_mask_convention_probe.py T1-T6）+3 处科学路径修正+回归 R1-R3 全 PASS，本轮 CSV/MD 作废"
    "（results/full_threearm_CONVENTION_NOTE.md）、C 臂 3 ckpt 移存 experiments/ckpt/superseded_inverted_mask_20261027/、"
    "progress 自愈化（eval_rows=0/verdict=null，下一单元 all 自动重训 C+重算）；回执 failed+全空系收尾模型调用抽风致 status "
    "非契约枚举（driver 01:52 unit-notes-backfilled 从 trajectory 补回，队列 failed_models+用户侧观察三源互证），勘误为 partial；"
    "判读复算 44 项全 PASS（experiments/s5_judge_710a_recheck.py）+verify() 两处倒挂残留已由判读单元补修并重跑证 identity 指标不变。"
    "第六单元动作：①写并实跑 experiments/operator_bench.py——对 CfC/液态单元实现路径（ncps 0.0.2："
    "G:/ai/python11/Lib/site-packages/ncps/torch 的 ltc_cell.py/cfc_cell.py + 本仓 experiments/pilot_threearm.py、"
    "full_protocol.py 调用路径）做数值稳定性基准（τ-tie 覆写点 ltc_cell.py:223-244、scale-state 爆炸风险（harvest 2610.15139）、"
    "dt=0 零输入收缩性（S0 结论 u2_probe.json 断言②既有）、梯度量级、B>1 timespans RuntimeError 已知边界）与效率基准"
    "（manual-loop 逐样本 vs 库路径代价、d2 向量化后残余瓶颈、108 格评测 167.3s 构成）；②落 results/operator_bench.md"
    "（问题定位+修法+是否数值保真）；③能修的落修复+回归（恒等性/边缘用例，规格同 04:4x selftest 68 项；修复若改变前向数值"
    "必须显式标注并给出 A/B ckpt 是否需重训的判定）；④修不掉早退，把算子墙记入 workflow stop_conditions（F8），不硬撑；"
    "⑤禁批量训练；已跑 ckpt 全部保留、结论一律标注「基于旧算子（ncps 0.0.2；倒挂 Convention 已修正、不影响 A/B 干净训练）」。"
    "排产：算子单元 ≤90min，写断点不硬撑。后续链由后续判读逐段解锁：C 臂重训 3×30ep≈72min（48-52s/ep 实测带，ckpt 已移存从零始）"
    "+修正 Convention 重算 108 行≈3min→落正确 results/full_threearm.csv/md→S5 收口判读（判读须知不变：meanpool 主口径三口径兼报、"
    "C clean 逐种子门控、A/B 恒定类消失伴生判据、D7 结论级=复现论文 Table III QuickDraw≈98.6-98.7% 数量级；QuickDraw 108 格"
    "落表前不宣称 D7）；若算子修复改变前向数值则 A/B 也重训=6×30ep≈4.6h+eval≈3min（由算子单元结论+下一判读定）；"
    "其后=S3/S4 pilot 按修正 Convention 重算（108 行≈38min，ckpt 在盘）交 researcher 复审 S4 判词数值基础；"
    "再其后=N-MNIST 事件 loader 固化+结论级基准（fb-98640319cd）、E2 B-train 对照臂。"
    "派发路由=lab-executor/stepfun/step-5-preview 主+openrouter-rotator 兜底（队列 failed_models 已记 stepfun 一次收尾抽风、"
    "rotator 注册在位）；禁手写并行分片（progress 写竞争+GPU 争抢，S3 有实证）。researcher 唤醒点=算子单元回执"
    "（operator_bench.md+修复是否数值保真+A/B 是否需重训）或算子硬失败（F8 算子墙早退）。"
    "【以下为 2026-10-26 04:4x-07:4x 沿革，历史记录】"
)

s5["actions"] = new_block + old_actions
s5["estimate_min"] = 60
s5["放行依据"] = s5["放行依据"] + (
    "；2026-10-27T02:1x 判读 unit.receipt 710a1c50feff4a9ab0943e929ad06ab6：第五单元 failed 空壳回执=科学交付 PASS"
    "（44 项独立复算全过：6 ckpt 直读+log 逐行对账+CSV 108 格+代码补丁核验，探针/回归/verify 三重独立重跑逐项一致）"
    "+回执格式失败勘误为 partial（收尾模型抽风致 status 非枚举，driver trajectory 补回+队列 failed_models+用户侧观察三源互证）；"
    "掩码 Convention 倒挂 bug 结论确认、本轮 CSV/MD 作废、C 臂移存 superseded、A/B ckpt 有效、S3/S4 pilot 重算移交确认；"
    "fb-ab50d0ec9f 纳入=下一单元算子优化先行（operator_bench+修复+回归、禁批量训练、estimate_min=60），C 臂重训+108 格重算排其后，"
    "已跑 ckpt 保留且结论标注基于旧算子；fb-98640319cd 排序随调（N-MNIST loader 在 S5 QuickDraw 收口后）；"
    "S5 维持 ready（结论级表未出）、next_units=[]（workflow 分支自动派，手写拒收）、唤醒点=算子单元回执"
)

w.setdefault("lessons", []).append({
    "at": "2026-10-27T02:3x+08:00",
    "type": "receipt_judged",
    "note": (
        "S5 第五单元 failed 空壳回执判读 PASS（unit 6e9acd73c626431abd4f28ac2c49df9a，判读全文 "
        "notes/researcher-interventions/710a1c50feff4a9ab0943e929ad06ab6.md）：科学交付 44 项独立复算全 PASS"
        "（s5_judge_710a_recheck.py：6 ckpt 直读+log 逐行对账六臂 30ep 无跳号+CSV 108 格完备+代码补丁核验）+探针/回归/verify "
        "独立重跑逐项一致（T3 补丁后 0.9160=修正生效证据，补丁前 probe JSON 按 9a2bb15 恢复防漂移）；回执 failed+全空=收尾模型"
        "调用抽风致 status 非枚举（driver 01:52 unit-notes-backfilled+队列 failed_models+用户侧 bridge 三源互证），勘误为 partial，"
        "stage 失败计数无风险（workflow 分支 attempts 重置+同 stage 队列项剔除）；新发现=verify() 两处倒挂残留"
        "（xb[..]*mask[..] 索引形式，首轮正则漏检、二轮抓到）已补修并重跑证 identity 指标不变；fb-ab50d0ec9f 纳入=第六单元起"
        "算子优化先行（operator_bench+修复+回归、禁批量训练、estimate_min=60），C 臂重训+108 格重算排其后，已跑 ckpt 保留且"
        "结论标注基于旧算子；fb-98640319cd 排序随调；next_units=[]（手写拒收 :1142）、唤醒点=算子单元回执；"
        "看板 t_f6e7bac5 sqlite 评论同步"
    ),
})
w["updated_at"] = "2026-10-27T02:3x+08:00"

with open(WF, "w", encoding="utf-8") as fh:
    json.dump(w, fh, ensure_ascii=False, indent=1)

# 自校验：重载后关键字段在位
with open(WF, encoding="utf-8") as fh:
    w2 = json.load(fh)
s5b = [s for s in w2["stages"] if s.get("id") == "S5-full-protocol"][0]
assert s5b["actions"].startswith("续跑链（2026-10-27T02:1x"), "actions 前置失败"
assert s5b["estimate_min"] == 60
assert w2["lessons"][-1]["type"] == "receipt_judged"
assert w2["updated_at"] == "2026-10-27T02:3x+08:00"
print("workflow.json updated: actions prepended (operator-first), estimate_min=60, lessons n=", len(w2["lessons"]))
