# S5 续跑链第四单元回执独立复算（researcher 判读单元 2026-10-26T07:0x）
# 对账 unit.receipt（unit proc_9862b9502b6f/winpid 1064，finished_at 06:55:53，commit a9955ed）每一项数字与盘上事实。
# 参数化：期望值从回执 metrics JSON（experiments/s5_unit4_metrics.json）自动读取，不硬编码（06:1x 判读教训落地）。
# 入口：G:/ai/python11/python.exe experiments/s5_researcher_unit4_recheck.py
import json, re, subprocess, sys, os, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
fails = []
def check(name, ok, detail):
    print(("PASS" if ok else "FAIL"), name, "|", detail)
    if not ok:
        fails.append(name)

met = json.load(open(os.path.join(PROJ, "experiments", "s5_unit4_metrics.json"), encoding="utf-8"))

# ---- 1. ckpt 直接读盘（独立于 s5_ckpt_verify.py 的第二路径）----
import torch
CK = os.path.join(PROJ, "experiments", "ckpt")
exp_ckpt = {
    ("seed0", "ab"): (met["seed0_ab_epochs_done"], met["seed0_ab_final_train_acc"]),
    ("seed0", "c"):  (met["seed0_c_epochs_done"],  met["seed0_c_final_train_acc"]),
    ("seed1", "ab"): (met["seed1_ab_epochs_done"], met["seed1_ab_final_train_acc"]),
    ("seed1", "c"):  (met["seed1_c_epochs_done"],  met["seed1_c_train_acc"]),
}
for (seed, arm), (exp_ep, exp_acc) in exp_ckpt.items():
    p = os.path.join(CK, f"full_quickdraw_{seed}_{arm}.pt")
    ck = torch.load(p, map_location="cpu", weights_only=False)
    ep = ck.get("epochs_done"); hist = ck.get("history") or []
    acc = ck.get("last_acc") or ck.get("train_acc")
    has_opt = any(("opt" in k.lower()) for k in ck.keys())
    size = os.path.getsize(p)
    check(f"ckpt {seed}_{arm} epochs_done={exp_ep}", ep == exp_ep, f"disk={ep} receipt={exp_ep}")
    check(f"ckpt {seed}_{arm} history 连续(len==ep)", len(hist) == ep, f"history_len={len(hist)} epochs_done={ep}")
    check(f"ckpt {seed}_{arm} last_acc={exp_acc}", abs(float(acc) - exp_acc) < 5e-4, f"disk={acc} receipt={exp_acc}")
    check(f"ckpt {seed}_{arm} opt 在盘", has_opt, f"keys={sorted(ck.keys())[:8]}")
    check(f"ckpt {seed}_{arm} 体积合理(2.9-3.1MB)", 2_900_000 < size < 3_100_000, f"size={size}")

# ---- 2. full_run.log 逐行对账（全量累计，无跳号）----
log = open(os.path.join(PROJ, "experiments", "full_run.log"), encoding="utf-8").read()
eps = {(s, a): [int(m) for m in re.findall(rf"full-train seed={s} arm={a} ep=(\d+)/30", log)]
       for s in (0, 1, 2) for a in ("ab", "c")}
for (seed, arm), (exp_ep, _) in exp_ckpt.items():
    s = int(seed[-1]); seq = eps[(s, arm)]
    check(f"log seed{s}_{arm} ep 连续 1-{exp_ep}", seq == list(range(1, exp_ep + 1)),
          f"n={len(seq)} last={seq[-3:]}")
check("log 无 seed2 行（未启动）", eps[(2, "ab")] == [] and eps[(2, "c")] == [], f"s2ab={len(eps[(2,'ab')])} s2c={len(eps[(2,'c')])}")
check("log resume seed=0 arm=c from epoch 26 实证", "resume seed=0 arm=c from epoch 26" in log, "")
m = re.search(r"seed=1 arm=c ep=10/30\] loss=[\d.]+ acc=([\d.]+) \((\d+)s\)", log)
check("log seed1_c ep10 acc=0.5822@478s", m and abs(float(m.group(1)) - 0.5822) < 5e-4 and int(m.group(2)) == 478,
      m.groups() if m else "missing")
m = re.search(r"seed=1 arm=ab ep=30/30\] loss=[\d.]+ acc=([\d.]+) \((\d+)s\)", log)
check("log seed1_ab ep30 acc=0.9661@1382s", m and abs(float(m.group(1)) - 0.9661) < 5e-4 and int(m.group(2)) == 1382,
      m.groups() if m else "missing")
m = re.search(r"seed=0 arm=c ep=30/30\] loss=[\d.]+ acc=([\d.]+)", log)
check("log seed0_c ep30 acc=0.6885", m and abs(float(m.group(1)) - 0.6885) < 5e-4, m.group(1) if m else "missing")
n_lines = len(re.findall(r"full-train", log))
check("log full-train 总行数=103（30+30+30+10+3 单元残留? 见 detail）", n_lines == 103, f"n={n_lines}")

# ---- 3. progress 对账 ----
prog = json.load(open(os.path.join(PROJ, "results", "full_progress.json"), encoding="utf-8"))
for run in ("seed0_ab", "seed0_c", "seed1_ab"):
    r = prog["runs"].get(run, {})
    exp_ep = exp_ckpt[(run[:5], run[6:])][0]
    exp_acc = exp_ckpt[(run[:5], run[6:])][1]
    check(f"progress {run} {exp_ep}ep acc", r.get("epochs") == exp_ep and abs(r.get("train_acc", 0) - exp_acc) < 5e-4,
          f"epochs={r.get('epochs')} acc={r.get('train_acc')} sec={r.get('sec')}")
check("progress runs 恰 3 个收口", set(prog["runs"].keys()) == {"seed0_ab", "seed0_c", "seed1_ab"}, str(list(prog["runs"].keys())))
check("progress eval_rows=0（半程不落表合规）", prog.get("eval_rows") == [], f"eval_rows={prog.get('eval_rows')}")
check("progress sanity verify_pass", prog["sanity"]["verify_real_size"]["verify_pass"] is True, "")

# ---- 4. 回执指标 vs 盘上（速率/推进量/排产复算）----
c0_rate = met["seed0_c_sec_this_unit"] / met["seed0_c_advanced_this_unit"]
ab1_rate = met["seed1_ab_sec_this_unit"] / met["seed1_ab_advanced_this_unit"]
c1_rate = met["seed1_c_sec_this_unit"] / met["seed1_c_advanced_this_unit"]
check("seed0_c 本单元 4ep 速率 46.7", met["seed0_c_advanced_this_unit"] == 4 and abs(c0_rate - 46.7) < 0.1, f"{c0_rate:.2f}s/ep")
check("seed1_ab 本单元 30ep 速率 46.1", met["seed1_ab_advanced_this_unit"] == 30 and abs(ab1_rate - 46.1) < 0.1, f"{ab1_rate:.2f}s/ep")
check("seed1_c 本单元 10ep 速率 47.8", met["seed1_c_advanced_this_unit"] == 10 and abs(c1_rate - 47.8) < 0.1, f"{c1_rate:.2f}s/ep")
check("本单元推进 44 epoch", met["epochs_advanced_this_unit"] == 44 == 4 + 30 + 10, str(met["epochs_advanced_this_unit"]))
check("双速率复核与 06:1x 校准一致（ab 46-47/c 47-48，64s 出清）",
      46.0 <= ab1_rate <= 47.0 and 46.5 <= c1_rate <= 48.0, f"ab={ab1_rate:.1f} c={c1_rate:.1f}")
# 排产复算：剩余 = seed1_c 20ep + seed2_ab 30ep + seed2_c 30ep，按各臂实测速率
remain = (30 - met["seed1_c_epochs_done"]) * c1_rate + 30 * ab1_rate + 30 * c1_rate
check("剩余训练 80ep 复算≈回执 3773s", met["remaining_train_epochs"] == 80 and abs(remain - met["remaining_train_sec_est"]) < 30,
      f"receipt={met['remaining_train_sec_est']}s recompute={remain:.0f}s")
eval_sec = 3 * (12 * 1.2 + 12 * 52.4 + 12 * 52.7)
check("eval 3827s 复算", abs(eval_sec - met["eval_sec_est"]) < 2, f"{eval_sec:.0f}s")
total_h = (remain + eval_sec) / 3600
check("总剩余≈2.11h", abs(total_h - met["remaining_total_h_est"]) < 0.03, f"{total_h:.2f}h vs receipt {met['remaining_total_h_est']}h")
# 夜窗剩余复核：kill 06:51:05 → 终点 08:00:00
kill = datetime.datetime.fromisoformat(met["killed_at"])
end = datetime.datetime.fromisoformat("2026-10-26T08:00:00+08:00")
remain_min = (end - kill).total_seconds() / 60
check("kill 时点夜窗剩余≈69min", abs(remain_min - met["night_window_remaining_min_at_kill"]) < 1.5,
      f"recompute={remain_min:.1f}min receipt={met['night_window_remaining_min_at_kill']}min")
check("总剩余 2.11h > 夜窗剩余（交下一窗判据成立）", total_h * 60 > remain_min, f"{total_h*60:.0f}min > {remain_min:.0f}min")

# ---- 5. 快照滞后规则（commit 时点 vs 盘上末态）----
head_line = subprocess.run(["git", "-C", PROJ, "log", "--oneline", "-1"], capture_output=True, text=True).stdout.strip()
check("HEAD=a9955ed（回执 commit 实载）", head_line.startswith("a9955ed"), head_line[:80])
ct = subprocess.run(["git", "-C", PROJ, "log", "-1", "--format=%ct"], capture_output=True, text=True).stdout.strip()
commit_ts = datetime.datetime.fromtimestamp(int(ct), datetime.timezone(datetime.timedelta(hours=8)))
lag = []
for f in ("full_quickdraw_seed0_c.pt", "full_quickdraw_seed1_ab.pt", "full_quickdraw_seed1_c.pt"):
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(CK, f)), datetime.timezone(datetime.timedelta(hours=8)))
    if mt > commit_ts:
        lag.append(f"{f} mtime={mt:%H:%M:%S} > commit={commit_ts:%H:%M:%S}")
check("快照滞后规则：无 commit 后在飞原子写（ckpt mtime 均早于 commit）", not lag, "; ".join(lag) or f"commit={commit_ts:%H:%M:%S}, all ckpt mtime earlier")
check("回执 seed1_c ep10 与盘上 ckpt 三方互证（快照滞后无触发）",
      exp_ckpt[("seed1", "c")][0] == 10 and eps[(1, "c")][-1] == 10, f"receipt=10 disk_ckpt={exp_ckpt[('seed1','c')][0]} log_last={eps[(1,'c')][-1]}")
st = subprocess.run(["git", "-C", PROJ, "status", "--short"], capture_output=True, text=True).stdout.strip()
check("git 工作树仅剩判读证据文件（researcher 命名）+PROJECT.md", all(("researcher" in l or "PROJECT.md" in l) for l in st.splitlines()), repr(st[:300]))

# ---- 6. 队列 / driver 对账 ----
q = json.load(open(os.path.join(PROJ, "..", "_state", "night-queue.json"), encoding="utf-8"))
s5u = [u for u in q.get("units", []) if u.get("stage") == "S5-full-protocol"]
check("队列 S5 resume 单元在队 attempts=1", len(s5u) == 1 and s5u[0].get("attempts") == 1,
      f"units={len(q.get('units', []))} attempts={s5u[0].get('attempts') if s5u else None}")
drv = open(os.path.join(PROJ, "..", "_state", "night-production.jsonl"), encoding="utf-8").read().splitlines()
last_done = [json.loads(l) for l in drv if '"unit-done"' in l][-1]
check("driver unit-done partial@06:55:53 duration≈2422s api_calls=43",
      last_done["status"] == "partial" and last_done["ts"].startswith("2026-10-26T06:55:53")
      and abs(last_done["duration_s"] - 2422.1) < 1 and last_done["usage"]["api_calls"] == 43
      and last_done["execution_model"] == "stepfun/step-5-preview",
      f"status={last_done['status']} dur={last_done['duration_s']} calls={last_done['usage']['api_calls']} model={last_done['execution_model']}")
check("driver queue_added=0（回执未手写 next_units）", last_done.get("queue_added") == 0, str(last_done.get("queue_added")))

print()
print("FAILS:", fails if fails else "无 — 回执指标与盘上事实逐项一致")
sys.exit(1 if fails else 0)
