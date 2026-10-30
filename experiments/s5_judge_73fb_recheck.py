# -*- coding: utf-8 -*-
"""S5 收口判读独立复算（researcher 判读单元 73fb33f2，2026-10-31T01:0x）。
只读 results/full_threearm.csv + results/full_progress.json，不 import 课题任何模块——
与执行单元 s5_unit8_csv_recheck.py 互为独立第二路径。逐项输出 PASS/FAIL，exit=0=全过。
"""
import csv, json, os, sys, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "results", "full_threearm.csv")
PROG = os.path.join(ROOT, "results", "full_progress.json")
MD = os.path.join(ROOT, "results", "full_threearm.md")

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
prog = json.load(open(PROG, encoding="utf-8"))
md = open(MD, encoding="utf-8").read()

CONDS = ["clean", "uniform30", "block5-30", "block15-30"]
ARMS = ["A", "B", "C"]
SEEDS = [0, 1, 2]
PATS = [0, 1, 2]
fails = []


def chk(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (" | " + detail if detail else ""))
    if not cond:
        fails.append(name)


# ---------- 1. 结构 ----------
chk("rows_108", len(rows) == 108, f"rows={len(rows)}")
keys = [(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows]
chk("keys_unique_108", len(set(keys)) == 108, f"unique={len(set(keys))}")
chk("dims_3x3x4x3",
    sorted({r["seed"] for r in rows}) == ["0", "1", "2"]
    and sorted({r["arm"] for r in rows}) == ["A", "B", "C"]
    and sorted({r["condition"] for r in rows}) == sorted(CONDS)
    and sorted({r["pattern"] for r in rows}) == ["0", "1", "2"])
bad_val = [k for k, r in zip(keys, rows) if not (0.0 <= float(r["acc_meanpool"]) <= 1.0)]
chk("values_in_01", not bad_val, f"bad={bad_val[:3]}")
chk("n_eval_7500", all(int(r["n_eval"]) == 7500 for r in rows))
# 掩码率：clean=0；其余 ≈0.30（预注册期望 30%）
mf = {}
for c in CONDS:
    vals = [float(r["masked_fraction_realized"]) for r in rows if r["condition"] == c]
    mf[c] = st.mean(vals)
chk("maskfrac_clean_zero", abs(mf["clean"]) < 1e-12, f"clean={mf['clean']}")
chk("maskfrac_masked_≈0.30", all(abs(mf[c] - 0.30) < 0.01 for c in CONDS[1:]),
    str({k: round(v, 4) for k, v in mf.items()}))

# ---------- 2. mean 表（与 MD 对账）----------
def pick(arm, cond, key="acc_meanpool"):
    return [float(r[key]) for r in rows if r["arm"] == arm and r["condition"] == cond]


mean_tbl = {}
for c in CONDS:
    for a in ARMS:
        v = pick(a, c)
        mean_tbl[(a, c)] = (st.mean(v), st.pstdev(v) * 100)

md_expect = {  # MD 表内 mean±std（pp），逐字抄自 full_threearm.md
    ("A", "clean"): (92.30, 0.86), ("B", "clean"): (92.30, 0.86), ("C", "clean"): (92.89, 0.17),
    ("A", "uniform30"): (63.93, 2.86), ("B", "uniform30"): (64.37, 3.76), ("C", "uniform30"): (86.10, 0.80),
    ("A", "block5-30"): (71.03, 4.10), ("B", "block5-30"): (69.81, 4.69), ("C", "block5-30"): (88.52, 0.66),
    ("A", "block15-30"): (72.83, 2.80), ("B", "block15-30"): (72.03, 3.22), ("C", "block15-30"): (83.55, 1.08),
}
diffs = []
for k, (em, es) in md_expect.items():
    m, s = mean_tbl[k]
    diffs.append((k, round(m * 100 - em, 3), round(s - es, 3)))
chk("md_table_recomputed", all(abs(d[1]) <= 0.005 and abs(d[2]) <= 0.005 for d in diffs),
    str([(d[0], d[1], d[2]) for d in diffs if abs(d[1]) > 0.005 or abs(d[2]) > 0.005]))

# ---------- 3. B−A / C−A（mean，pooled 口径） ----------
bma = {c: (mean_tbl[("B", c)][0] - mean_tbl[("A", c)][0]) * 100 for c in CONDS}
cma = {c: (mean_tbl[("C", c)][0] - mean_tbl[("A", c)][0]) * 100 for c in CONDS}
chk("B_minus_A_block5=-1.22", abs(bma["block5-30"] + 1.22) < 0.005, f"{bma['block5-30']:+.3f}")
chk("C_minus_A_block5=+17.49", abs(cma["block5-30"] - 17.49) < 0.005, f"{cma['block5-30']:+.3f}")
chk("C_minus_A_uniform30=+22.17", abs(cma["uniform30"] - 22.17) < 0.005, f"{cma['uniform30']:+.3f}")
chk("C_minus_A_block15=+10.72", abs(cma["block15-30"] - 10.72) < 0.005, f"{cma['block15-30']:+.3f}")
chk("B_minus_A_clean=0.00", abs(bma["clean"]) < 1e-9, f"{bma['clean']:+.4f}")
chk("C_minus_A_clean=+0.59", abs(cma["clean"] - 0.59) < 0.005, f"{cma['clean']:+.3f}")

# ---------- 4. 逐种子配对差（修正 MD 两处 bug 后的正确值） ----------
def per_seed(arm, cond, key="acc_meanpool"):
    out = {}
    for s in SEEDS:
        vals = [float(r[key]) for r in rows
                if r["arm"] == arm and r["condition"] == cond and int(r["seed"]) == s]
        out[s] = st.mean(vals)
    return out


ps = {}
for c in CONDS:
    ps[("B-A", c)] = {s: (per_seed("B", c)[s] - per_seed("A", c)[s]) * 100 for s in SEEDS}
    ps[("C-A", c)] = {s: (per_seed("C", c)[s] - per_seed("A", c)[s]) * 100 for s in SEEDS}
    ps[("C-A-clean-drop", c)] = {s: (per_seed("A", c)[s] - per_seed("C", c)[s]) * 100 for s in SEEDS}

print("\n-- 逐种子配对差（pp，正确值；MD 逐种子行应为这些）--")
for c in CONDS:
    print(f"  {c}: B−A={ {k: round(v,2) for k,v in ps[('B-A',c)].items()} } "
          f"C−A={ {k: round(v,2) for k,v in ps[('C-A',c)].items()} }")

b5_ps = ps[("B-A", "block5-30")]
chk("B_block5_perseed_all_<+2pp", all(v < 2.0 for v in b5_ps.values()),
    str({k: round(v, 2) for k, v in b5_ps.items()}))
chk("B_block5_perseed_mean=-1.22", abs(st.mean(b5_ps.values()) + 1.22) < 0.005)
c5_ps = ps[("C-A", "block5-30")]
chk("C_block5_perseed_all_≥+2pp", all(v >= 2.0 for v in c5_ps.values()),
    str({k: round(v, 2) for k, v in c5_ps.items()}))
# MD 错误逐种子行对照（bug 证据）
md_has_bad_clean = "'0': 0.61, '1': 0.37, '2': 0.78" in md
md_has_bad_block5 = "'0': 0.22, '1': 0.15, '2': 0.15" in md
correct_clean_drop = {k: round(v, 2) for k, v in ps[("C-A-clean-drop", "clean")].items()}
print(f"\n-- MD 逐种子行 bug 证据：clean 行含错误dict={md_has_bad_clean}，"
      f"block5 行含错误dict={md_has_bad_block5}；正确 C−A clean 逐种子="
      f"{ {k: round(v,2) for k,v in ps[('C-A','clean')].items()} }（C−A，正=C 更好）；"
      f"正确 A−C（降幅）={correct_clean_drop}")

# ---------- 5. 门线双约定重算 ----------
b_amp = bma["block5-30"] >= 2.0
c_amp = cma["block5-30"] >= 2.0
b_clean_drop = -bma["clean"]          # 降幅 = A−B（正=劣化）
c_clean_drop = -cma["clean"]          # 降幅 = A−C
b_clean_ok_1s = b_clean_drop <= 0.5
c_clean_ok_1s = c_clean_drop <= 0.5
b_clean_ok_2s = abs(bma["clean"]) <= 0.5
c_clean_ok_2s = abs(cma["clean"]) <= 0.5 and all(
    abs(v) <= 0.5 for v in ps[("C-A", "clean")].values())
print(f"\n-- 门线：B 幅值 {b_amp}（{bma['block5-30']:+.2f}pp）/ C 幅值 {c_amp}（{cma['block5-30']:+.2f}pp）")
print(f"   实现约定(对称|Δ|≤0.5pp)：B clean ok={b_clean_ok_2s}，C clean ok={c_clean_ok_2s}"
      f"（mean|Δ|={abs(cma['clean']):.2f}pp，逐种子|C−A|="
      f"{ {k: round(abs(v),2) for k,v in ps[('C-A','clean')].items()} }）")
print(f"   预注册字面(降幅 A−C≤0.5pp 单侧)：B clean ok={b_clean_ok_1s}（降幅 {b_clean_drop:+.2f}pp），"
      f"C clean ok={c_clean_ok_1s}（降幅 {c_clean_drop:+.2f}pp）")
gate_impl = ("B" if (b_amp and b_clean_ok_2s) else "") + ("C" if (c_amp and c_clean_ok_2s) else "")
gate_literal = ("B" if (b_amp and b_clean_ok_1s) else "") + ("C" if (c_amp and c_clean_ok_1s) else "")
chk("gate_impl=None（复现机械输出）", gate_impl == "", f"gate_impl='{gate_impl}'")
chk("gate_literal=C（预注册字面约定）", gate_literal == "C", f"gate_literal='{gate_literal}'")
chk("falsify_branch_condition（B<+1pp 且 clean 不受损）",
    bma["block5-30"] < 1.0 and b_clean_ok_2s, f"B−A={bma['block5-30']:+.2f}pp")

# ---------- 6. sanity / D7 / H2 ----------
a_clean_rows = pick("A", "clean")
b_clean_rows = pick("B", "clean")
chk("clean_A≡B_rowwise_exact", a_clean_rows == b_clean_rows,
    f"maxdiff={max(abs(x-y) for x,y in zip(a_clean_rows,b_clean_rows)):.2e}")
a_u30 = mean_tbl[("A", "uniform30")][0]
z = (a_u30 - 0.10) / (0.10 * 0.90 / 7500) ** 0.5
chk("A_uniform30_z=155.68", abs(z - 155.68) < 0.5, f"z={z:.2f}")
a_clean = mean_tbl[("A", "clean")][0]
chk("D7_gap=-6.30pp", abs((a_clean - 0.986) * 100 + 6.30) < 0.01,
    f"A@clean={a_clean*100:.2f}% gap={(a_clean-0.986)*100:+.2f}pp")
cal = {k: st.mean(pick("A", "clean", f"acc_{k}")) * 100 for k in ["meanpool", "final", "gapnb"]}
chk("constant_class_gone_spread=82.57pp", abs((max(cal.values()) - min(cal.values())) - 82.57) < 0.02,
    str({k: round(v, 2) for k, v in cal.items()}))
h2 = ps[("B-A", "block15-30")]
h2_delta = st.mean(h2.values()) - st.mean(b5_ps.values())
chk("H2_delta=+0.42pp", abs(h2_delta - 0.42) < 0.005, f"Δ={h2_delta:+.3f}pp")
tc = {k: (st.mean(pick("B", "block5-30", f"acc_{k}")) - st.mean(pick("A", "block5-30", f"acc_{k}"))) * 100
      for k in ["meanpool", "final", "gapnb"]}
chk("three_calibers_B_block5", abs(tc["meanpool"] + 1.22) < 0.005 and abs(tc["gapnb"] - 0.13) < 0.005
    and abs(tc["final"] - 0.05) < 0.005, str({k: round(v, 2) for k, v in tc.items()}))
tcC = {k: (st.mean(pick("C", "block5-30", f"acc_{k}")) - st.mean(pick("A", "block5-30", f"acc_{k}"))) * 100
       for k in ["meanpool", "final", "gapnb"]}
chk("three_calibers_C_block5", abs(tcC["meanpool"] - 17.49) < 0.005 and abs(tcC["gapnb"] - 22.50) < 0.005
    and abs(tcC["final"] - 0.79) < 0.005, str({k: round(v, 2) for k, v in tcC.items()}))

# ---------- 7. CSV ↔ progress eval_rows 交叉 ----------
pe = prog.get("eval_rows", [])
chk("progress_eval_rows_108", len(pe) == 108, f"n={len(pe)}")
d2 = []
for r in rows:
    m = [p for p in pe if str(p.get("seed")) == r["seed"] and p.get("arm") == r["arm"]
         and p.get("condition") == r["condition"] and str(p.get("pattern")) == r["pattern"]]
    if len(m) != 1:
        d2.append((r["seed"], r["arm"], r["condition"], r["pattern"], len(m)))
    elif abs(float(m[0].get("acc_meanpool", -9)) - float(r["acc_meanpool"])) > 1e-9:
        d2.append((r["seed"], r["arm"], r["condition"], r["pattern"], "val"))
chk("csv_matches_progress", not d2, str(d2[:3]))

# ---------- 8. 执行回执/文档数字对账 ----------
chk("receipt_metrics_consistent",
    abs(mean_tbl[("A", "clean")][0] * 100 - 92.30) < 0.005
    and abs(mean_tbl[("C", "clean")][0] * 100 - 92.89) < 0.005
    and abs(bma["block5-30"] + 1.22) < 0.005 and abs(cma["block5-30"] - 17.49) < 0.005)

print("\nOVERALL:", "PASS" if not fails else f"FAIL ({fails})")
sys.exit(0 if not fails else 1)
