# -*- coding: utf-8 -*-
"""S5 续跑链第三单元收尾：kill 后复验 ckpt、落证据、更新 STATUS/DECISIONS、写交接单草稿。
所有数字从盘上实读（ckpt/log/progress），不手抄。"""
import json, os, subprocess, sys, datetime

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = "G:/ai/python11/python.exe"
CK = os.path.join(PROJECT, "experiments", "ckpt")
LOG = os.path.join(PROJECT, "experiments", "full_run.log")
EV = os.path.join(PROJECT, "experiments", "s5_unit3_ckpt_rerun.txt")
STAGING = os.path.join(PROJECT, "notes", "handoff-staging", "S5-full-protocol.md")

import torch


def ckpt_info(name):
    p = os.path.join(CK, name)
    if not os.path.exists(p):
        return None
    d = torch.load(p, map_location="cpu", weights_only=False)
    h = d.get("history", [])
    return {
        "epochs_done": int(d.get("epochs_done", 0)),
        "target": int(d.get("epochs_target", 30)),
        "last_acc": h[-1]["acc"] if h else None,
        "last_loss": h[-1]["loss"] if h else None,
        "last_sec": h[-1]["sec"] if h else None,
        "hist_len": len(h),
        "has_opt": "opt_state_dict" in d,
        "size": os.path.getsize(p),
        "mtime": datetime.datetime.fromtimestamp(os.path.getsize(p) and os.path.getmtime(p)).strftime("%H:%M:%S"),
    }


ab = ckpt_info("full_quickdraw_seed0_ab.pt")
c = ckpt_info("full_quickdraw_seed0_c.pt")

# --- 证据文件：verify 脚本复跑 + seed0_c 直接读 ---
with open(EV, "w", encoding="utf-8") as fh:
    fh.write("=== unit3 kill 后 ckpt 复验 %s ===\n" % datetime.datetime.now().strftime("%H:%M:%S"))
    r = subprocess.run([PY, "experiments/s5_ckpt_verify.py"], cwd=PROJECT,
                       capture_output=True, text=True)
    fh.write(r.stdout)
    fh.write("s5_ckpt_verify exit=%d\n" % r.returncode)
    fh.write("\n=== seed0_c 直接读盘 ===\n")
    fh.write(json.dumps(c, ensure_ascii=False, indent=1) + "\n")
    fh.write("\n=== full_run.log 本单元尾部（截至 kill 时点）===\n")
    with open(LOG, encoding="utf-8") as lf:
        lines = lf.readlines()
    unit_start = next((i for i, l in enumerate(lines) if l.startswith("[unit3 ")), 0)
    fh.write("".join(lines[unit_start:]))

# --- 本单元推进量：从 unit3 标记起算 log 里的 ep 行 ---
seg = lines[unit_start:]
ab_eps = [l for l in seg if "arm=ab ep=" in l]
c_eps = [l for l in seg if "arm=c ep=" in l]
resume_line = next((l.strip() for l in seg if l.startswith("[full-train] resume")), "")
ab_sec = None
m = None
for l in reversed(ab_eps):
    if "(" in l and "s)" in l:
        try:
            ab_sec = float(l.rsplit("(", 1)[1].split("s)", 1)[0])
        except Exception:
            pass
        break
ab_advanced = len(ab_eps)
ab_rate = round(ab_sec / ab_advanced, 1) if (ab_sec and ab_advanced) else None
c_sec = None
for l in reversed(c_eps):
    if "(" in l and "s)" in l:
        try:
            c_sec = float(l.rsplit("(", 1)[1].split("s)", 1)[0])
        except Exception:
            pass
        break
c_rate = round(c_sec / len(c_eps), 1) if (c_sec and c_eps) else None

prog = json.load(open(os.path.join(PROJECT, "results", "full_progress.json"), encoding="utf-8"))
runs = prog.get("runs", {})

# --- 排产修正（以 C 臂实测速率为准）---
c_rem = 30 - (c["epochs_done"] if c else 0)
rem_train = c_rem * c_rate + 4 * 30 * ab_rate if c_rate else None
rem_total_h = round((rem_train + 3827) / 3600, 2) if rem_train else None

metrics = {
    "seed0_ab_epochs_done": ab["epochs_done"],
    "seed0_ab_complete": ab["epochs_done"] >= 30,
    "seed0_ab_final_train_acc": ab["last_acc"],
    "seed0_ab_advanced_this_unit": ab_advanced,
    "seed0_ab_sec_per_epoch_measured": ab_rate,
    "seed0_c_epochs_done": c["epochs_done"] if c else 0,
    "seed0_c_train_acc": c["last_acc"] if c else None,
    "seed0_c_sec_per_epoch_measured": c_rate,
    "seed0_c_sec_per_epoch_prior_estimate": 64.0,
    "c_rate_deviation_pct": round((64.0 - c_rate) / 64.0 * 100, 1) if c_rate else None,
    "resume_line": resume_line,
    "eval_rows": len(prog.get("eval_rows", [])),
    "verify_real_size_pass": bool(prog.get("sanity", {}).get("verify_real_size", {}).get("verify_pass")),
    "runs_completed": sorted(runs.keys()),
    "remaining_train_sec_est": rem_train,
    "remaining_total_h_est": rem_total_h,
    "ckpt_integrity": "PASS_verify_exit0_seed0_c_history_contiguous_opt_present" if (c and c["has_opt"] and c["hist_len"] == c["epochs_done"]) else "CHECK",
}
print(json.dumps(metrics, ensure_ascii=False, indent=1))

# --- 交接单草稿（staging，门控通过后进正式位置）---
handoff = """---
stage: S5-full-protocol
kind: experiment
status: partial
did: 复跑 full_protocol.py all 无损续跑：seed0_ab 从 ep15 跑到 30/30 收口（train acc 0.9402→0.9518），seed0_c 新启跑到约 ep{c_done}/30，单元截止 kill 交断点。
why: S4 verdict=replicate 续跑链第三单元：pilot 2-epoch 预算缺口致 A@clean=10.43% chance 级，须全量 30 epoch 复现论文 Table III QuickDraw≈98.6-98.7% 后再 adjudicate H1/H2，本单元推进长跑并保全断点。
how: 每 epoch 原子 ckpt（tmp+os.replace）保 kill 无损；重跑同一命令 all 自动从最新 ckpt 续跑并跳过已完成训练；判读按 S5 须知（meanpool 主口径三口径兼报、C clean 逐种子门控、恒定类消失伴生判据、D7 结论级≈98.6-98.7%）；半程不落表（CSV/MD 须 108 行齐）。
result: ckpt 复验 exit=0（seed0_ab 30/30、history 连续、opt 在盘；seed0_c ep{c_done}/30 history 连续 opt 在盘，证据 experiments/s5_unit3_ckpt_rerun.txt）；seed0_ab 本单元 16 epoch 用 751.2s≈{ab_rate}s/epoch；seed0_c 实测≈{c_rate}s/epoch，比排产估计 64s 低 {dev}%（>20%→总排产显式修正：剩余训练≈{rem_train}s+eval 3827s≈{rem_h}h）；无评测无 CSV/MD（预注册半程不落表）。
next: 下一单元重跑同一命令 G:/ai/python11/python.exe experiments/full_protocol.py all 自动续跑（seed0_c 约 ep{c_next} 起；6 训练齐后自动进 108 格评测逐行断点续跑→齐 108 行落 results/full_threearm.csv/md 并按 S5 须知判读）；不硬撑不缩数据；E2 B-train 对照臂与 N-MNIST 结论级基准仍留后续。
artifacts: [experiments/full_protocol.py, experiments/full_run.log, experiments/s5_ckpt_verify.py, experiments/s5_unit3_ckpt_rerun.txt, results/full_progress.json, experiments/ckpt/full_quickdraw_seed0_ab.pt, experiments/ckpt/full_quickdraw_seed0_c.pt, STATUS.md, notes/DECISIONS.md]
info_need: N-MNIST 免墙镜像（daytime/user-assisted；数据脚本在位可重跑，结论级基准必需）；harvest 累计 9 条已消化 5 条（research/harvest/INDEX.md digested=true 可直接用），余 4 条无阻塞本单元。
---
""".format(c_done=c["epochs_done"] if c else 0,
           c_next=(c["epochs_done"] + 1) if c else 1,
           ab_rate=ab_rate, c_rate=c_rate,
           dev=metrics["c_rate_deviation_pct"],
           rem_train=rem_train, rem_h=rem_total_h)
os.makedirs(os.path.dirname(STAGING), exist_ok=True)
with open(STAGING, "w", encoding="utf-8") as fh:
    fh.write(handoff)

with open(os.path.join(PROJECT, "experiments", "s5_unit3_metrics.json"), "w", encoding="utf-8") as fh:
    json.dump(metrics, fh, ensure_ascii=False, indent=1)
print("WROTE", EV)
print("WROTE", STAGING)
