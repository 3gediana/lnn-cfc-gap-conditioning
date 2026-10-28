# -*- coding: utf-8 -*-
"""2026-10-29 夜班开班统筹（unit b15f43d3971059238e7c4205d96c6390）机器态修复：

病灶=P6 兜底 reconcile_parent_stages 误闭合。2026-10-28T23:06:15 驱动器
workflow 分支把「子阶段 done ⇒ 父阶段 done」规则套在 S5-full-protocol-continue
上——但该子阶段是 apply_result 按 next_action=continue 自动追加、由 researcher
判读单元 c74da1aa 显式关闭的 superseded 占位空壳（无 actions/inputs/outputs，
其 result.notes 自述「本条目 superseded 不再单独派发」），不是「判读段已完成」
的证据。父阶段 S5-full-protocol 科学上并未收口：

  - results/full_progress.json：eval_rows=[]、verdict=null；
  - results/full_threearm.csv/md：mtime 2026-10-27，为掩码 Convention 倒挂
    作废值（CONVENTION_NOTE 在盘标注）；
  - experiments/ckpt/full_quickdraw_seed2_c.pt：epochs_done=9/30（本单元
    torch.load 直读复核），修正 Convention 的 seed2_c 重训未完成；
  - night-production.jsonl 自 2026-10-28T07:51:58 后无本课题 unit-done。

修复=数据层+代码层两手：
  1) 本脚本（数据层，幂等可重跑）：S5-full-protocol done→ready（删除
     closed_by/closed_at，落 state_repair 留痕，actions 第八单元语义不变）；
     S5-full-protocol-continue 的 result 补结构化 superseded=true 标记。
  2) research-workflow.py reconcile_parent_stages 已加占位跳过（代码层，
     2026-10-29 同单元）：result.superseded 为真的 done 子阶段不闭合父阶段；
     合成回归 4 例 + selftest 13 项全绿（见回执）。
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOPIC = HERE.parent
SCRIPTS = Path("D:/hermes-data/scripts")

spec = importlib.util.spec_from_file_location("research_workflow", SCRIPTS / "research-workflow.py")
rw = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(rw)

STAGE = "S5-full-protocol"
CHILD = "S5-full-protocol-continue"


def main() -> int:
    workflow = rw.load_workflow(TOPIC)
    stages = rw._stage_map(workflow)
    parent = stages.get(STAGE)
    child = stages.get(CHILD)
    if not isinstance(parent, dict) or not isinstance(child, dict):
        print(json.dumps({"ok": False, "error": "stage missing",
                          "has_parent": isinstance(parent, dict),
                          "has_child": isinstance(child, dict)}, ensure_ascii=False))
        return 1

    before = {
        "parent_status": parent.get("status"),
        "parent_closed_by": parent.get("closed_by"),
        "child_status": child.get("status"),
        "child_result_superseded": (child.get("result") or {}).get("superseded")
        if isinstance(child.get("result"), dict) else None,
    }

    # --- 数据层修复 ---
    child_result = child.get("result")
    if not isinstance(child_result, dict):
        child_result = {}
        child["result"] = child_result
    child_result["superseded"] = True
    note = str(child_result.get("notes") or "")
    add = ("；2026-10-29T00:2x 开班统筹 b15f43d3：补结构化 superseded=true 标记——"
           "本阶段为 apply_result 自动追加的占位空壳，其 done 不是父阶段科学收口证据；"
           "research-workflow.reconcile_parent_stages P6 修正（同单元）后占位阶段不再触发父闭合")
    if "b15f43d3" not in note:
        child_result["notes"] = (note + add)[:2000]

    parent["status"] = "ready"
    parent.pop("closed_by", None)
    parent.pop("closed_at", None)
    parent["state_repair"] = {
        "at": "2026-10-29T00:2x+08:00",
        "by": "researcher 夜班开班统筹 unit b15f43d3971059238e7c4205d96c6390",
        "event": "P6 reconcile_parent_stages 误闭合回滚",
        "false_closure_at": "2026-10-28T23:06:15+08:00（父阶段被 S5-full-protocol-continue 的 done 误闭合）",
        "evidence_science_incomplete": [
            "results/full_progress.json eval_rows=[] verdict=null",
            "results/full_threearm.csv/md mtime 2026-10-27（Convention 倒挂作废值）",
            "experiments/ckpt/full_quickdraw_seed2_c.pt epochs_done=9/30（torch.load 直读）",
            "night-production.jsonl 07:51:58 后无本课题 unit-done",
        ],
        "action": "done→ready 恢复第八单元派发资格（actions 语义不变：seed2_c ep10 续跑 21ep+108 格评测+结论级表落盘≈23-25min）",
        "code_fix": "research-workflow.py reconcile_parent_stages 跳过 result.superseded=true 的占位子阶段（合成回归 4 例+selftest 13 项）",
    }
    parent["status_reason"] = ("2026-10-29T00:2x 开班统筹修复：P6 误闭合回滚（closed_by=S5-full-protocol-continue 系 superseded 占位空壳，"
                               "非判读完成证据；科学未收口证据见 state_repair）→恢复 ready，第八单元由驱动器 workflow 分支自动派")
    rw.save_workflow(TOPIC, workflow)

    # --- 自校验 ---
    reloaded = rw.load_workflow(TOPIC)
    rmap = rw._stage_map(reloaded)
    ready = [s.get("id") for s in rw.ready_stages(reloaded)]
    closed_again = rw.reconcile_parent_stages(json.loads(json.dumps(reloaded)))
    checks = {
        "parent_status": rmap[STAGE].get("status"),
        "parent_closed_by": rmap[STAGE].get("closed_by"),
        "child_status": rmap[CHILD].get("status"),
        "child_result_superseded": (rmap[CHILD].get("result") or {}).get("superseded"),
        "ready_stages": ready,
        "reconcile_would_close": closed_again,
        "stage_has_content": rw._stage_has_content(rmap[STAGE]) if hasattr(rw, "_stage_has_content") else "n/a",
    }
    ok = (checks["parent_status"] == "ready"
          and checks["parent_closed_by"] is None
          and checks["child_result_superseded"] is True
          and checks["ready_stages"] == [STAGE]
          and checks["reconcile_would_close"] == [])
    print(json.dumps({"ok": ok, "before": before, "after": checks}, ensure_ascii=False))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
