#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_judge_apply_unit4.py — researcher 判读单元 07:0x 落账：workflow.json + STATUS.md + DECISIONS.md。
判读对象：unit.receipt（S5 续跑链第四单元 partial，unit proc_9862b9502b6f，commit a9955ed）。
判读全文 notes/researcher-interventions/44656e219aff404b92fbc650babaeeba.md"""
import io
import json
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUDGE_MD = "notes/researcher-interventions/44656e219aff404b92fbc650babaeeba.md"

# ---------------- workflow.json ----------------
wf_path = os.path.join(PROJ, "workflow.json")
with io.open(wf_path, encoding="utf-8") as fh:
    wf = json.load(fh)

NEW_LEAD = (
    "续跑链（2026-10-26T07:0x 判读 unit.receipt（S5 续跑链第四单元 partial，unit proc_9862b9502b6f，"
    "commit a9955ed）后更新）：第五单元起=重跑 G:/ai/python11/python.exe experiments/full_protocol.py all，"
    "自动从 seed1_c ep11 无损续跑（盘上 ckpt epochs_done=10/30、last_acc=0.5822@478.3s，本判读单元 53 项独立复算 "
    "exit=0+s5_ckpt_verify.py 复跑 exit=0、回执零失实、快照滞后规则无触发；seed0_ab/seed0_c/seed1_ab 已 30/30 收口、"
    "progress runs 在盘；6 训练逐个查 ckpt、已跑齐的跳过；跑不完写断点不硬撑，每 epoch 原子落盘 kill 无损；"
    "规则：commit 后仍有原子写在飞时，交接单数字须标注「截至 commit 时点」）；排产双实测速率复核确认"
    "（ab≈46.1-47.0s/ep、c≈46.7-47.8s/ep，与 06:1x 校准一致、64s 估计项彻底出清、无新 >20% 偏差→维持排产修正不二次修正）"
    "→剩余训练=seed1_c 20ep+seed2_ab 30ep+seed2_c 30ep=80ep≈3773s≈63min+eval 3827s≈64min≈2.11h>夜窗剩余"
    "（kill 时点≈69min、07:05 tick remaining_min=54.8）→预计夜窗内 1 个 checkpoint 单元（07:05 tick 先派本判读单元、"
    "执行单元在判读收工后同 tick 派发，窗口约 30-35min：确定项=seed1_c 收口≈16min、seed2_ab 预计推进 14-22ep），"
    "seed2 臂尾部+108 格评测交下一夜窗/白天，不硬撑不缩数据；未经实测的估计项不得进排产公式；"
    "D7 不提前声称（双 ab 臂 train acc 0.9518/0.9661 收敛正常、pilot 恒定类问题消失，但 train acc≠test acc，"
    "A 臂 clean 结论级判据须 108 格评测落表后判）；researcher 唤醒点=下一回执（核对 ckpt epochs_done vs 回执 ep 计数、"
    "seed2 新启速率、训练是否 6/6 齐自动进评测）或训练齐+108 行 CSV/MD 落盘（S5 收口判读）。"
    "【以下为 04:4x-06:5x 沿革，历史记录】"
)

RELEASE_APPEND = (
    "；2026-10-26T07:0x 判读 unit.receipt（S5 续跑链第四单元 partial，unit proc_9862b9502b6f）："
    "第四单元 partial 属实 PASS（53 项独立复算 exit=0+4 ckpt 直读第二路径+log 逐行对账+排产复算+git/队列/driver 对账"
    "+ps 无残留；回执零失实、快照滞后规则无触发），维持 ready，actions 更新为第五单元起 seed1_c ep11 续跑"
    "+双速率排产复核（ab 46.1-47.0/c 46.7-47.8/eval 64min，64s 估计项出清、无新偏差）"
)

n_stage = 0
for s in wf.get("stages", []):
    if s.get("id") == "S5-full-protocol":
        old_actions = s.get("actions", "")
        assert "【以下为 04:4x-05:5x 沿革，历史记录】" in old_actions, "历史沿革标记未找到"
        s["actions"] = NEW_LEAD + old_actions.replace(
            "【以下为 04:4x-05:5x 沿革，历史记录】", "", 1)
        s["放行依据"] = s.get("放行依据", "") + RELEASE_APPEND
        n_stage += 1
assert n_stage == 1, f"S5 stage patch count={n_stage}"

wf.setdefault("lessons", []).append({
    "at": "2026-10-26T07:2x+08:00",
    "type": "receipt_judged",
    "note": ("S5 续跑链第四单元 partial 回执（unit proc_9862b9502b6f，commit a9955ed）判读属实 PASS"
             "（53 项独立复算 exit=0：4 ckpt 直读第二路径 seed0_ab/seed0_c/seed1_ab 30/30 acc 0.9518/0.6885/0.9661、"
             "seed1_c 10/30 acc 0.5822，history 全连续+opt 在盘；full_run.log 逐行对账四臂 ep 连续无跳号+resume seed0_c ep26 实证；"
             "progress 3 runs/eval_rows=0；速率与排产复算 3773s+3827s=2.11h；git HEAD 实载+4 ckpt mtime 均早于 commit 06:54:16 无在飞写；"
             "队列 resume attempts=1；driver partial@06:55:53 duration 2422.1s api_calls=43；ps 无残留；回执零失实、快照滞后规则无触发）；"
             "新发现=双速率实测复核确认 06:1x 校准（ab 46.06-46.70/c 47.83s/ep 落 46-48 带、64s 估计项彻底出清、无新 >20% 偏差）"
             "→维持排产修正不二次修正；剩余 2.11h>夜窗剩余→预计夜窗内 1 个 checkpoint 单元（07:05 tick 先派判读单元、执行单元同 tick 后续派、"
             "窗口约 30-35min：seed1_c 收口+seed2_ab 14-22ep），seed2 臂尾部+108 格评测交下一窗/白天；D7 不提前声称；"
             "机器态：S5 维持 ready，actions 更新为第五单元起 seed1_c ep11 续跑语义+双速率排产复核；next_units=[]"
             "（night-production.py:2384-2407 选择器以 fresh workflow 单元吸收队列 partial 指针派发，手写入队会被拒，本单元代码级复核确认）；"
             "看板卡 t_f6e7bac5 sqlite 评论同步；路由确认=lab-executor 默认 stepfun/step-5-preview+openrouter-rotator（/v1/status 200）；"
             "唤醒点=第五单元回执（核对 ckpt epochs_done vs 回执 ep 计数、seed2 新启速率、6/6 齐自动进评测）或训练齐+108 行 CSV/MD 落盘（S5 收口判读）"),
})
wf["updated_at"] = "2026-10-26T07:2x+08:00"

with io.open(wf_path, "w", encoding="utf-8") as fh:
    json.dump(wf, fh, ensure_ascii=False, indent=1)
print("workflow.json updated: S5 actions+放行依据+lessons+updated_at")

# ---------------- STATUS.md ----------------
st_path = os.path.join(PROJ, "STATUS.md")
with io.open(st_path, encoding="utf-8") as fh:
    st = fh.read()

NEW_BULLET = (
    "- 阶段：**active / S5-full-protocol 续跑链第四单元判读（2026-10-26T07:0x researcher 判读 unit.receipt，"
    "unit proc_9862b9502b6f，commit a9955ed）：第四单元 partial/checkpointed 属实 PASS——本单元 53 项独立复算 exit=0"
    "（experiments/s5_researcher_unit4_recheck.py+.txt，期望值参数化自回执 metrics JSON：4 ckpt 直读第二路径 "
    "seed0_ab 30/30 acc 0.9518、seed0_c 30/30 acc 0.6885、seed1_ab 30/30 acc 0.9661、seed1_c 10/30 acc 0.5822，"
    "history 全连续+opt 在盘；full_run.log 逐行对账四臂 ep 连续无跳号+resume seed0_c ep26 实证；progress 3 runs/"
    "eval_rows=0 半程不落表合规；速率复算 seed0_c 46.70/s、seed1_ab 46.06/s、seed1_c 47.83s per ep；排产复算 "
    "3773s+3827s≈2.11h；git HEAD 实载+4 ckpt mtime 均早于 commit 06:54:16 无在飞原子写、回执 ep10 与盘上 ckpt/log "
    "三方互证、快照滞后规则无触发、回执零失实）+s5_ckpt_verify.py 复跑 exit=0（experiments/s5_researcher_ckpt_rerun_unit4.txt）"
    "+ps 无 G:/ai 残留+队列 resume 单元 attempts=1+driver 对账（06:55:53 partial duration 2422.1s api_calls=43）。"
    "**新发现=双速率实测复核确认 06:1x 校准**：ab 46.06-46.70s/ep、c 47.83s/ep 均落 46-48s/ep 带、无新 >20% 偏差，"
    "64s 估计项彻底出清→维持排产修正不二次修正；剩余 80ep≈63min+eval≈64min≈2.11h>夜窗剩余（kill 时点 68.9min、"
    "07:05 tick remaining_min=54.8）→预计夜窗内 1 个 checkpoint 单元（07:05 tick 先派本判读单元、执行单元在判读收工后"
    "同 tick 派发、窗口约 30-35min：确定项=seed1_c 收口≈16min、seed2_ab 预计推进 14-22ep——06:5x 交接单「42min 窗口"
    "可完成 seed2_ab 30/30」预期据此修正），seed2 臂尾部+108 格评测交下一夜窗/白天，不硬撑不缩数据。"
    "收敛伴生判据正面：seed1_ab train acc 0.9661+seed0_ab 0.9518 双 ab 臂全量 30 epoch 收敛正常、pilot 恒定类问题"
    "在 full 协议下消失，但 D7 不提前声称（train acc≠test acc，A 臂 clean 结论级须 108 格落表后判）；C 臂 train acc "
    "0.6885/0.5822 与 pilot 模式一致无异常。S5 维持 ready；next_units=[]（night-production.py:2384-2407 选择器以 fresh "
    "workflow 单元吸收队列 partial 指针派发、手写入队会被拒，本单元代码级复核确认）；看板卡 t_f6e7bac5 sqlite 评论同步；"
    "路由确认 stepfun/step-5-preview+openrouter-rotator（/v1/status 200 实探）。判读全文 " + JUDGE_MD + "）**——\r\n"
)

ANCHOR = "# 状态\r\n\r\n"
if ANCHOR not in st:
    ANCHOR = "# 状态\n\n"
assert ANCHOR in st, "STATUS.md anchor not found"
st = st.replace(ANCHOR, ANCHOR + NEW_BULLET, 1)

OLD_HEAD_PREFIX = "- 最近更新：2026-10-26T06:5x+08:00"
NEW_HEAD = (
    "- 最近更新：2026-10-26T07:2x+08:00（researcher 判读 unit.receipt，S5 续跑链第四单元 partial）："
    "partial 属实 PASS（53 项独立复算 exit=0，回执零失实、快照滞后规则无触发）；新发现=双速率实测复核确认 06:1x 校准"
    "（ab 46.1-47.0/c 46.7-47.8s/ep、64s 估计项出清、无新 >20% 偏差）→维持排产修正不二次修正；剩余≈2.11h>夜窗剩余"
    "→预计夜窗内 1 个 checkpoint 单元（本 tick 判读后同 tick 派发、约 30-35min 窗口：seed1_c 收口+seed2_ab 14-22ep），"
    "seed2 臂尾部+108 格评测交下一窗/白天；D7 不提前声称；S5 维持 ready，workflow actions 更新为第五单元起 seed1_c ep11 "
    "续跑语义+双速率排产复核、放行依据/lessons 追加，next_units=[]（fresh workflow 单元吸收队列 partial 指针派发），"
    "看板卡 t_f6e7bac5 sqlite 评论同步；唤醒点=第五单元回执（核对 ckpt epochs_done vs 回执 ep 计数、seed2 新启速率、"
    "训练 6/6 齐自动进评测）或训练齐+108 行 CSV/MD 落盘（S5 收口判读）。上次更新：2026-10-26T06:5x+08:00"
)
assert OLD_HEAD_PREFIX in st, "STATUS.md 最近更新 head not found"
st = st.replace(OLD_HEAD_PREFIX, NEW_HEAD, 1)

with io.open(st_path, "w", encoding="utf-8") as fh:
    fh.write(st)
print("STATUS.md updated: 判读节置顶+最近更新刷新")

# ---------------- DECISIONS.md ----------------
dec_path = os.path.join(PROJ, "notes", "DECISIONS.md")
with io.open(dec_path, encoding="utf-8") as fh:
    dec = fh.read()

ENTRY = (
    "\r\n- 2026-10-26 07:0x 判读（unit.receipt，S5-full-protocol 续跑链第四单元 partial/checkpointed，执行单元 "
    "proc_9862b9502b6f/winpid 1064，driver 实测 duration 2422.1s、api_calls=43，commit a9955ed；判读全文 " + JUDGE_MD + "）："
    "**partial 属实 PASS（53 项独立复算 exit=0，回执零失实）→ S5 维持 ready 续跑链**。①核验（本单元自己跑，复算脚本参数化落地"
    "=期望值从回执 metrics JSON 自动读取，06:1x 教训转化）：4 ckpt 直读第二路径（seed0_ab/seed0_c/seed1_ab 均 30/30、"
    "acc 0.9518/0.6885/0.9661，seed1_c 10/30 acc 0.5822，history 全连续+opt 在盘）；s5_ckpt_verify.py 复跑 exit=0；"
    "full_run.log 逐行对账四臂 ep 连续无跳号+resume seed0_c ep26 实证；progress 3 runs/eval_rows=0 半程不落表合规；"
    "速率复算（seed0_c 46.70、seed1_ab 46.06、seed1_c 47.83s per ep）；排产复算 3773s+3827s≈2.11h；git HEAD=a9955ed 实载、"
    "4 ckpt mtime 均早于 commit 06:54:16 无在飞原子写、回执 ep10 与盘上 ckpt/log 三方互证——**快照滞后规则无触发**"
    "（对比 05:1x ep13/ep14 先例）；队列 resume 单元 attempts=1；driver 对账 partial@06:55:53；ps 无残留。"
    "②**新发现=双速率实测复核确认 06:1x 校准**：本单元 seed1_ab 30ep 实测 46.06s/ep、seed1_c 10ep 47.83s/ep、"
    "seed0_c 4ep 46.70s/ep，双臂落 46-48s/ep 带、与校准值（ab≈46.9/c≈47.8）一致，历史 64s 估计项彻底出清、无新 >20% 偏差"
    "→**拍板维持 06:1x 排产修正、不二次修正**（预注册 >20% 偏差显式修正规则本单元无触发）。③**排产与窗口（修正 06:5x 交接单预期）**："
    "剩余=seed1_c 20ep+seed2_ab 30ep+seed2_c 30ep=80ep≈3773s≈63min+eval 3827s≈64min≈2.11h>夜窗剩余（kill 时点 68.9min、"
    "07:05 tick remaining_min=54.8）→预计夜窗内 1 个 checkpoint 单元；06:5x 交接单称「07:05 tick 派执行单元、约 42min 窗口"
    "可完成 seed1_c 收口+seed2_ab 30/30」与 driver 日志不符——07:05:12 tick 实际先派本 researcher-event 判读单元"
    "（selection=researcher-event 实证），执行单元在本判读收工后同 tick 派发（预算守卫 min(window_left,tick_left)>480s 可过）、"
    "窗口约 30-35min：确定项=seed1_c 20ep 收口≈16min，seed2_ab 预计推进 14-22ep、30/30 完不成；seed2 臂尾部+108 格评测"
    "交下一夜窗/白天，不硬撑不缩数据。④**收敛伴生判据（D7 仍不提前声称）**：seed0_ab 0.9518+seed1_ab 0.9661 双 ab 臂"
    "全量 30 epoch 收敛正常、pilot 2-epoch 的 A/B 恒定类问题在 full 协议下消失（S5 判读须知伴生判据趋势成立）；"
    "C 臂 train acc 偏低（0.6885/0.5822）与 pilot 模式一致（块状间隙增强训练更难）无异常；train acc≠test acc，"
    "D7 结论级（A 臂 clean≥98.5%、复现论文 Table III QuickDraw≈98.6-98.7% 数量级）须 108 格评测落表后判。"
    "⑤机器态：S5-full-protocol 维持 **ready**（不写 done/result——结论级表未出，partial 不当科学完成；"
    "next_action=continue 无新空阶段）；workflow.json S5 actions 更新为第五单元起语义（seed1_c ep11 续跑+双速率排产复核+"
    "唤醒点，历史沿革保留【】内）、放行依据追加本判读条、lessons+updated_at 刷新；**next_units=[]**（resume 单元在队 "
    "attempts=1，且 night-production.py:2384-2407 选择器每 tick 从 workflow.json 现渲染 ready 阶段单元并吸收队列 partial "
    "指针、剔除旧副本——手写入队会被 _reconcile_queue 拒收，本单元代码级复核确认该机制，判读单元只更新 workflow.json 即刷新"
    "下一单元指令）；看板卡 t_f6e7bac5 sqlite 追加评论同步（维持 ready 记账；置 done 判据=结论级表验收通过，尚未到）。"
    "⑥派发要素确认：kind=experiment→role=executor→profile=**lab-executor**（13:41 命名新规生效名）、路由=profile 默认 "
    "**stepfun/step-5-preview**+**openrouter-rotator** 本地代理（127.0.0.1:15730，本单元 /v1/status 200 实探；第四单元同路由 "
    "api_calls=43 正常收口实证）、estimate_min=35（D6 粒度）、依赖全在盘（full_protocol.py 04:28 后零变动 selftest 不重跑+"
    "4 full ckpt+data/quickdraw 全量+交接单过门控+S5 须知已入 summarize_full）；执行口径=重跑 "
    "G:/ai/python11/python.exe experiments/full_protocol.py all 自动从 seed1_c ep11 无损续跑、6 训练逐个查 ckpt 跳过已跑齐、"
    "跑不完写断点不硬撑、禁手写并行分片；**researcher 唤醒点=第五单元回执**（重点核对 ckpt epochs_done vs 回执 ep 计数防 "
    "commit 时点快照滞后、seed2 新启速率是否维持 ~47s、训练是否 6/6 齐自动进 108 格评测）**或训练齐+108 行 CSV/MD 落盘"
    "（S5 收口判读=结论级 adjudicate H1/H2）或硬失败**；E2 B-train 对照臂与 N-MNIST 结论级基准仍留后续"
    "（N-MNIST=daytime/user-assisted info_need 不变）。⑦经验沉淀：「partial 判读三件套」（独立复跑入口脚本+kill 后 ckpt "
    "完整性校验+续跑路径行号级核验）第八次零成本生效；06:1x 提出的「recheck 脚本参数化（期望值从回执 metrics 自动读取）」"
    "改进本单元落地、后续判读单元换 metrics 文件名即可复用；选择器「fresh workflow 单元吸收队列 partial 指针」机制经 "
    "night-production.py:2384-2407 代码级复核确认——判读单元只须更新 workflow.json、不必不手改队列；复算脚本自身一处切片笔误"
    "（seed/arm 切分 KeyError）自查抓到即修，再次验证「FAIL 先分清盘上事实不符 vs 校验代码笔误」教训（课题事实零失实）。"
)
dec = dec.rstrip("\r\n") + ENTRY
with io.open(dec_path, "w", encoding="utf-8") as fh:
    fh.write(dec)
print("DECISIONS.md updated: 判读条目追加")
