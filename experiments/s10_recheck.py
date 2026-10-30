#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s10_recheck.py — S10 独立复算：从 results/nmnist_threearm.csv 重算全部判据数字，
与 results/nmnist_progress.json verdict 块 + results/nmnist_threearm.md 对账（不采信汇总）。
判据跑前冻结、机械输出；本脚本只验算不改判据。
"""
import csv
import json
import math
import statistics as st
import sys

PROJ = "D:/hermes-data/research/液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a"
CSV_PATH = f"{PROJ}/results/nmnist_threearm.csv"
PROG_PATH = f"{PROJ}/results/nmnist_progress.json"
MD_PATH = f"{PROJ}/results/nmnist_threearm.md"

CONDITIONS = ["clean", "uniform30", "block5-30", "block15-30"]
SEEDS = [0, 1, 2]
PAPER_T1 = 0.9938
PAPER_T3 = 0.9871
ok = True


def chk(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
print(f"rows={len(rows)}")
chk("row_count_108", len(rows) == 108, f"({len(rows)})")
keys = [(r["dataset"], int(r["seed"]), r["arm"], r["condition"], int(r["pattern"])) for r in rows]
chk("unique_keys", len(set(keys)) == len(keys))
chk("n_eval_all_10000", all(int(r["n_eval"]) == 10000 for r in rows))
chk("arms_ABC", {r["arm"] for r in rows} == {"A", "B", "C"})
chk("seeds_012", {int(r["seed"]) for r in rows} == {0, 1, 2})
chk("conditions_4", {r["condition"] for r in rows} == set(CONDITIONS))
chk("patterns_012", {int(r["pattern"]) for r in rows} == {0, 1, 2})

# 掩码率口径（预注册容差=偏离名义 0.30 的 20% 内，同冒烟门；
# 注意 make_mask 每 batch 以同种子重建 generator→满 batch 复用同一 256 样本投放模式
# （与 QuickDraw S5/S7 协议逐字同款），单行有效样本≈256，block 条件行间 std≈0.02-0.03，
# 故不得按 i.i.d.-10000 方差设窄容差；科学相关性质=跨臂同掩码配对，下方单独断言）
for cond in ["uniform30", "block5-30", "block15-30"]:
    rates = [float(r["masked_fraction_realized"]) for r in rows if r["condition"] == cond]
    chk(f"mask_rate_{cond}_within_20pct", all(abs(v - 0.30) <= 0.20 * 0.30 for v in rates),
        f"min={min(rates):.4f} max={max(rates):.4f} mean={sum(rates)/len(rates):.4f}")
clean_rates = [float(r["masked_fraction_realized"]) for r in rows if r["condition"] == "clean"]
chk("mask_rate_clean_zero", all(v == 0.0 for v in clean_rates))
# D4 跨臂同掩码配对：同 (seed,cond,pattern) 三臂实现掩码率逐位相等
pair = {}
for r in rows:
    pair.setdefault((int(r["seed"]), r["condition"], int(r["pattern"])), set()).add(
        r["masked_fraction_realized"])
chk("D4_cross_arm_mask_pairing", all(len(v) == 1 for v in pair.values()),
    f"({len(pair)} (seed,cond,pattern) groups)")


def pick(arm, cond, key="acc_meanpool"):
    return [float(r[key]) for r in rows if r["arm"] == arm and r["condition"] == cond]


def per_seed(arm, cond, key="acc_meanpool"):
    out = {}
    for s in SEEDS:
        v = [float(r[key]) for r in rows if r["arm"] == arm and r["condition"] == cond
             and int(r["seed"]) == s]
        if v:
            out[s] = st.mean(v)
    return out


means = {}
for cond in CONDITIONS:
    for arm in ["A", "B", "C"]:
        v = pick(arm, cond)
        means[(arm, cond)] = (st.mean(v), st.pstdev(v) if len(v) > 1 else 0.0)

print("\n== 主口径 meanpool（3 种子 mean±std, %） ==")
for cond in CONDITIONS:
    a, b, c = means[("A", cond)], means[("B", cond)], means[("C", cond)]
    bma = (b[0] - a[0]) * 100
    cma = (c[0] - a[0]) * 100
    print(f"  {cond:12s} A={a[0]*100:6.2f}±{a[1]*100:.2f}  B={b[0]*100:6.2f}±{b[1]*100:.2f}  "
          f"C={c[0]*100:6.2f}±{c[1]*100:.2f}  B-A={bma:+.2f}pp  C-A={cma:+.2f}pp")

# 逐种子配对（D4：(seed,pattern) 跨臂同模式键）
b5_ps = {s: (per_seed("B", "block5-30")[s] - per_seed("A", "block5-30")[s]) * 100 for s in SEEDS}
c5_ps = {s: (per_seed("C", "block5-30")[s] - per_seed("A", "block5-30")[s]) * 100 for s in SEEDS}
cl_ps = {s: (per_seed("B", "clean")[s] - per_seed("A", "clean")[s]) * 100 for s in SEEDS}
ccl_ps = {s: (per_seed("C", "clean")[s] - per_seed("A", "clean")[s]) * 100 for s in SEEDS}
print(f"\n逐种子 B-A(block5-30) pp: { {k: round(v, 2) for k, v in b5_ps.items()} }")
print(f"逐种子 C-A(block5-30) pp: { {k: round(v, 2) for k, v in c5_ps.items()} }")
print(f"逐种子 B-A(clean) pp:     { {k: round(v, 2) for k, v in cl_ps.items()} }")
print(f"逐种子 C-A(clean) pp:     { {k: round(v, 2) for k, v in ccl_ps.items()} }")

# ---- 判据机械输出（跑前冻结） ----
b5 = (means[("B", "block5-30")][0] - means[("A", "block5-30")][0]) * 100
c5 = (means[("C", "block5-30")][0] - means[("A", "block5-30")][0]) * 100
b_clean_drop = (means[("B", "clean")][0] - means[("A", "clean")][0]) * 100
c_clean_drop = (means[("C", "clean")][0] - means[("A", "clean")][0]) * 100
print(f"\n== 判据机械输出 ==")
print(f"  ① H1: B-A(block5-30)={b5:+.2f}pp, clean B-A={b_clean_drop:+.2f}pp")
if b5 >= 2.0 and abs(b_clean_drop) <= 0.5:
    h1 = "supported"
elif b5 < 1.0 and b_clean_drop >= -0.5:
    h1 = "falsified"
else:
    h1 = "inconclusive"
print(f"     -> H1_verdict={h1}")
chk("H1_verdict_falsified", h1 == "falsified")
chk("H1_negative_branch_conditions", b5 < 1.0 and b_clean_drop >= -0.5,
    f"(B-A={b5:+.2f}<1.0, clean_drop={b_clean_drop:+.2f}>=-0.5)")

ab = abs(means[("A", "clean")][0] - means[("B", "clean")][0])
chk("sanity_clean_A_equals_B_lt_0p1pp", ab < 0.001, f"|A-B|={ab*100:.3f}pp")

a_u30 = means[("A", "uniform30")][0]
z = (a_u30 - 0.10) / math.sqrt(0.10 * 0.90 / 10000)
chk("sanity_uniform30_z_gt_2", z > 2.0, f"A@uniform30={a_u30*100:.2f}% z={z:.2f}")

d7 = (means[("A", "clean")][0] - PAPER_T1) * 100
d7_3 = (means[("A", "clean")][0] - PAPER_T3) * 100
chk("D7_gap_within_3pp", d7 >= -3.0, f"A@clean={means[('A','clean')][0]*100:.2f}% "
    f"vs Table I {PAPER_T1*100:.2f}% gap={d7:+.2f}pp (vs Table III {PAPER_T3*100:.2f}%: {d7_3:+.2f}pp)")

cal = {k: st.mean(pick("A", "clean", f"acc_{k}")) for k in ["meanpool", "final", "gapnb"]}
spread = (max(cal.values()) - min(cal.values())) * 100
chk("convergence_three_caliber_spread", spread > 0.1,
    f"calibers={ {k: round(v*100, 2) for k, v in cal.items()} } spread={spread:.2f}pp")

c_gate = (c5 >= 2.0 and abs(c_clean_drop) <= 0.5
          and all(abs(x) <= 0.5 for x in ccl_ps.values()))
chk("C_gate_per_seed_fail_as_reported", (not c_gate),
    f"C-A={c5:+.2f}pp C_clean_drop={c_clean_drop:+.2f}pp per_seed={ {k: round(v,2) for k,v in ccl_ps.items()} }")

# 三口径兼报（block5-30）
tc = {}
for k in ["meanpool", "final", "gapnb"]:
    tc[f"B-A_{k}"] = (st.mean(pick("B", "block5-30", f"acc_{k}"))
                      - st.mean(pick("A", "block5-30", f"acc_{k}"))) * 100
    tc[f"C-A_{k}"] = (st.mean(pick("C", "block5-30", f"acc_{k}"))
                      - st.mean(pick("A", "block5-30", f"acc_{k}"))) * 100
print(f"  三口径 block5-30: B-A meanpool={tc['B-A_meanpool']:+.2f}/gapnb={tc['B-A_gapnb']:+.2f}/"
      f"final={tc['B-A_final']:+.2f}pp; C-A meanpool={tc['C-A_meanpool']:+.2f}/"
      f"gapnb={tc['C-A_gapnb']:+.2f}/final={tc['C-A_final']:+.2f}pp")
chk("three_calibers_B_all_near_zero", all(abs(tc[f"B-A_{k}"]) < 1.0 for k in
                                          ["meanpool", "gapnb", "final"]))

# ---- 与 progress verdict 块对账 ----
prog = json.load(open(PROG_PATH, encoding="utf-8"))
v = prog.get("verdict") or {}
pairs = [
    ("B_minus_A_block5", v.get("B_minus_A_block5"), b5 / 100, 1e-3),
    ("C_minus_A_block5", v.get("C_minus_A_block5"), c5 / 100, 1e-3),
    ("B_clean_drop_pp", v.get("B_clean_drop_pp"), b_clean_drop, 1e-2),
    ("C_clean_drop_pp", v.get("C_clean_drop_pp"), c_clean_drop, 1e-2),
    ("H1_verdict", v.get("H1_verdict"), h1, None),
    ("decision", v.get("decision"), "falsified_negative_branch", None),
    ("next_action", v.get("next_action"), "redesign", None),
    ("C_gate_pass", v.get("C_gate_pass"), c_gate, None),
    ("C_clean_drop_all_seeds_le_0p5pp", v.get("C_clean_drop_all_seeds_le_0p5pp"),
     all(abs(x) <= 0.5 for x in ccl_ps.values()), None),
]
print("\n== progress verdict 对账 ==")
for name, got, exp, tol in pairs:
    if tol is None:
        good = got == exp
    else:
        good = got is not None and abs(float(got) - exp) <= tol
    chk(f"verdict_{name}", good, f"(progress={got} recomputed={exp})")

# MD 关键数字在场
md = open(MD_PATH, encoding="utf-8").read()
for token in ["H1_verdict=falsified", "+0.09pp", "98.12", "-1.26pp", "C_gate_pass=False",
              "falsified_negative_branch", "10ep", "0.9938"]:
    chk(f"md_contains[{token}]", token in md)

print(f"\nRECHECK OVERALL: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
