# S5 续跑链第三单元回执独立复算（researcher 判读单元 2026-10-26T06:0x）
# 对账 unit.receipt 0145909001de4f48a3eff7ddaec8c035（unit c7d8d768）的每一项数字与盘上事实。
# 入口：G:/ai/python11/python.exe experiments/s5_researcher_receipt_recheck.py
import json, re, subprocess, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
fails = []
def check(name, ok, detail):
    print(("PASS" if ok else "FAIL"), name, "|", detail)
    if not ok:
        fails.append(name)

# ---- 1. ckpt 直接读盘（独立于 s5_ckpt_verify.py 的第二路径）----
import torch
for arm, exp_ep, exp_acc in (("ab", 30, 0.9518), ("c", 26, 0.6679)):
    p = os.path.join(PROJ, "experiments", "ckpt", f"full_quickdraw_seed0_{arm}.pt")
    ck = torch.load(p, map_location="cpu", weights_only=False)
    ep = ck.get("epochs_done"); hist = ck.get("history") or []
    acc = ck.get("last_acc") or ck.get("train_acc")
    has_opt = any(("opt" in k.lower()) for k in ck.keys())
    check(f"ckpt seed0_{arm} epochs_done", ep == exp_ep, f"disk={ep} receipt={exp_ep}")
    check(f"ckpt seed0_{arm} history 连续", len(hist) == ep, f"history_len={len(hist)} epochs_done={ep}")
    check(f"ckpt seed0_{arm} last_acc", abs(float(acc) - exp_acc) < 5e-4, f"disk={acc} receipt={exp_acc}")
    check(f"ckpt seed0_{arm} opt 在盘", has_opt, f"keys={sorted(ck.keys())[:8]}")

# ---- 2. full_run.log 逐行对账 ----
log = open(os.path.join(PROJ, "experiments", "full_run.log"), encoding="utf-8").read()
ab_eps = [int(m) for m in re.findall(r"arm=ab ep=(\d+)/30", log)]
c_eps = [int(m) for m in re.findall(r"arm=c ep=(\d+)/30", log)]
check("log ab epoch 连续 1-30", ab_eps == list(range(1, 31)), f"n={len(ab_eps)} first={ab_eps[:3]} last={ab_eps[-3:]}")
check("log c epoch 连续 1-26", c_eps == list(range(1, 27)), f"n={len(c_eps)} last={c_eps[-3:]}")
m15 = re.search(r"arm=ab ep=15/30\] loss=[\d.]+ acc=([\d.]+)", log)
m30 = re.search(r"arm=ab ep=30/30\] loss=[\d.]+ acc=([\d.]+)", log)
check("log ab ep15 acc=0.9402", m15 and abs(float(m15.group(1)) - 0.9402) < 5e-4, m15.group(1) if m15 else "missing")
check("log ab ep30 acc=0.9518", m30 and abs(float(m30.group(1)) - 0.9518) < 5e-4, m30.group(1) if m30 else "missing")

# ---- 3. progress / metrics 对账 ----
prog = json.load(open(os.path.join(PROJ, "results", "full_progress.json"), encoding="utf-8"))
r = prog["runs"].get("seed0_ab", {})
check("progress seed0_ab 30ep acc", r.get("epochs") == 30 and abs(r.get("train_acc", 0) - 0.9518) < 5e-4,
      f"epochs={r.get('epochs')} acc={r.get('train_acc')} sec={r.get('sec')}")
check("progress eval_rows=0（半程不落表）", prog.get("eval_rows") == [], f"eval_rows={prog.get('eval_rows')}")
check("progress sanity verify_pass", prog["sanity"]["verify_real_size"]["verify_pass"] is True, "")
met = json.load(open(os.path.join(PROJ, "experiments", "s5_unit3_metrics.json"), encoding="utf-8"))

# ---- 4. 速率与排产复算 ----
ab_rate = 751.2 / 16           # 本单元 16 epoch
c_rate = 1243.0 / 26           # seed0_c 26 epoch
dev = (64.0 - c_rate) / 64.0 * 100
check("ab 速率 46.9s/ep", abs(ab_rate - 46.9) < 0.1, f"{ab_rate:.2f}")
check("c 速率 47.8s/ep", abs(c_rate - 47.8) < 0.1, f"{c_rate:.2f}")
check("C 偏差 25.3%>20%", abs(dev - 25.3) < 0.15 and dev > 20, f"{dev:.1f}%")
# 剩余训练精化：seed0_c 余 4ep + seed1/seed2 各 ab+c 共 4 个全量
remain_train = 4 * c_rate + 2 * 30 * ab_rate + 2 * 30 * c_rate
remain_train_receipt = met["remaining_train_sec_est"]
check("剩余训练复算≈回执（回执按全 ab 速率，精化按实测 C 速率）",
      abs(remain_train - remain_train_receipt) / remain_train_receipt < 0.02,
      f"receipt={remain_train_receipt:.0f}s refined={remain_train:.0f}s diff={100*(remain_train-remain_train_receipt)/remain_train_receipt:.1f}%")
eval_sec = 3 * (12 * 1.2 + 12 * 52.4 + 12 * 52.7)   # 108 格：3 种子 ×(A/B/C 各 12 格)
check("eval 3827s 复算", abs(eval_sec - 3827) < 2, f"{eval_sec:.0f}s")
total_h = (remain_train + eval_sec) / 3600
check("总剩余≈2.68h", abs(total_h - 2.68) < 0.05, f"{total_h:.2f}h")

# ---- 5. git / 队列 / 机器态 ----
head = subprocess.run(["git", "-C", PROJ, "log", "--oneline", "-1"], capture_output=True, text=True).stdout.strip()
check("HEAD=d6b71bb（回执 commit 实载）", head.startswith("d6b71bb"), head[:80])
st = subprocess.run(["git", "-C", PROJ, "status", "--short"], capture_output=True, text=True).stdout.strip()
check("git 工作树干净（除本单元证据文件）", st == "" or all("researcher" in l for l in st.splitlines()), repr(st[:200]))
q = json.load(open(os.path.join(PROJ, "..", "_state", "night-queue.json"), encoding="utf-8"))
s5u = [u for u in q.get("units", []) if u.get("stage") == "S5-full-protocol"]
check("队列 S5 resume 单元在队", len(s5u) == 1, f"units={len(q.get('units', []))} attempts={s5u[0].get('attempts') if s5u else None}")

print()
print("FAILS:", fails if fails else "无 — 回执指标与盘上事实逐项一致")
sys.exit(1 if fails else 0)
