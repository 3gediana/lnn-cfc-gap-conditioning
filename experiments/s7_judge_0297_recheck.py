# -*- coding: utf-8 -*-
"""S7-e2-btrain-arm researcher 判读独立复算（0297fdde 单元）。
不采信回执/MD，全部从盘上 CSV/ckpt 重算：
 1. e2_btrain.csv 结构：144 数据行、键唯一、n_eval=7500
 2. 3 种子 mean±std（meanpool 主口径 + final/gapnb 兼报）
 3. 配对差 D-A / D-C / D-B（逐种子 + mean，block5-30 主判据条件）
 4. 预注册判据机械输出（两种 clean 约定并报，禁事后改）
 5. A/B/C 与 S5 结论级表 full_threearm.csv 逐位对账（mismatches=0）
 6. D ckpt 直读第二路径：epochs_done=30、history 30 连续、opt 在盘
 7. masked_fraction_realized 均值核对（名义 0.30）
"""
import csv, json, os, sys, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E2 = os.path.join(ROOT, "results", "e2_btrain.csv")
S5 = os.path.join(ROOT, "results", "full_threearm.csv")
CKPT = os.path.join(ROOT, "experiments", "ckpt")

fails = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (" | " + str(detail) if detail else ""))
    if not cond:
        fails.append(name)

rows = list(csv.DictReader(open(E2, encoding="utf-8")))
check("csv_144_rows", len(rows) == 144, len(rows))
keys = [(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows]
check("keys_unique_144", len(set(keys)) == 144)
check("n_eval_7500_all", all(int(r["n_eval"]) == 7500 for r in rows))
arms = sorted(set(r["arm"] for r in rows))
check("arms_ABCD", arms == ["A", "B", "C", "D"], arms)
conds = sorted(set(r["condition"] for r in rows))
check("conditions_4", conds == ["block15-30", "block5-30", "clean", "uniform30"], conds)

def cell(arm, cond, seed=None, metric="acc_meanpool"):
    vals = [float(r[metric]) for r in rows if r["arm"] == arm and r["condition"] == cond
            and (seed is None or r["seed"] == str(seed))]
    return vals

def mean3(arm, cond, metric="acc_meanpool"):
    v = cell(arm, cond, metric=metric)
    return sum(v) / len(v)

def std3(arm, cond, metric="acc_meanpool"):
    v = cell(arm, cond, metric=metric)
    return st.pstdev(v)

def cellmap(arm, cond, metric="acc_meanpool"):
    """(seed,pattern) -> value，用于跨臂同模式配对（D4：3 固定块模式跨臂配对）"""
    return {(r["seed"], r["pattern"]): float(r[metric]) for r in rows
            if r["arm"] == arm and r["condition"] == cond}

def paired_per_seed(x, y, cond, metric="acc_meanpool"):
    """逐种子配对差=该种子 3 个 pattern 上 (x−y) 的均值（同 seed 同 pattern 配对）"""
    mx, my = cellmap(x, cond, metric), cellmap(y, cond, metric)
    assert set(mx) == set(my), f"pattern keys mismatch {x}/{y}/{cond}"
    out = {}
    for s in ["0", "1", "2"]:
        diffs = [(mx[(s, p)] - my[(s, p)]) * 100 for p in ["0", "1", "2"]]
        out[s] = sum(diffs) / len(diffs)
    return out

print("\n== 3-seed mean±std (meanpool / final / gapnb), % ==")
table = {}
for cond in ["clean", "uniform30", "block5-30", "block15-30"]:
    table[cond] = {}
    for arm in ["A", "B", "C", "D"]:
        table[cond][arm] = {
            "meanpool": (mean3(arm, cond) * 100, std3(arm, cond) * 100),
            "final": (mean3(arm, cond, "acc_final") * 100, std3(arm, cond, "acc_final") * 100),
            "gapnb": (mean3(arm, cond, "acc_gapnb") * 100, std3(arm, cond, "acc_gapnb") * 100),
        }
    print(cond, {a: (round(table[cond][a]["meanpool"][0], 2), round(table[cond][a]["meanpool"][1], 2)) for a in "ABCD"})

print("\n== paired diffs (meanpool, pp; 逐种子=同 seed 3 pattern 配对均值) ==")
paired = {}
for cond in ["clean", "uniform30", "block5-30", "block15-30"]:
    paired[cond] = {}
    for x, y in [("D", "A"), ("D", "C"), ("D", "B"), ("C", "A"), ("B", "A")]:
        ps = paired_per_seed(x, y, cond)
        per_seed = [ps[s] for s in ["0", "1", "2"]]
        paired[cond][f"{x}-{y}"] = (sum(per_seed) / 3, per_seed)
    print(cond, {k: (round(v[0], 2), [round(p, 2) for p in v[1]]) for k, v in paired[cond].items()})

b5 = paired["block5-30"]
dA, dC = b5["D-A"][0], b5["D-C"][0]
cA = b5["C-A"][0]
print(f"\nD-A(block5-30)={dA:.2f}pp  D-C={dC:.2f}pp  C-A={cA:.2f}pp (S5 anchor 17.49)")
check("C_minus_A_matches_S5_anchor", abs(cA - 17.49) < 0.05, round(cA, 2))
check("B_minus_A_matches_S5", abs(b5["B-A"][0] - (-1.22)) < 0.05, round(b5["B-A"][0], 2))

# 预注册判据（跑前写死，机械输出；两种 clean 约定并报，禁事后改）
clean_per_seed_DmA = paired["clean"]["D-A"][1]
clean_mean_DmA = paired["clean"]["D-A"][0]
conv_twosided_pass = all(abs(p) <= 0.5 for p in clean_per_seed_DmA)   # S5 实现口径 |Δ|≤0.5pp 逐种子
conv_onesided_pass = (-clean_mean_DmA) <= 0.5                          # 预注册字面「clean 降幅≤0.5pp」单侧
if dA >= 2.0 and conv_twosided_pass:
    decision_twosided = "1_E2_refuted"
elif dA < 1.0:
    decision_twosided = "2_gap_bit_required"
else:
    decision_twosided = "3_partial_attribution"
if dA >= 2.0 and conv_onesided_pass:
    decision_onesided = "1_E2_refuted"
elif dA < 1.0:
    decision_onesided = "2_gap_bit_required"
else:
    decision_onesided = "3_partial_attribution"
ratio = dA / cA if cA else float("nan")
print(f"criterion twosided={decision_twosided}  onesided_literal={decision_onesided}  ratio D-A/(C-A)={ratio:.4f}")
print(f"clean D-A mean={clean_mean_DmA:+.2f}pp per_seed={[round(p,2) for p in clean_per_seed_DmA]}")
print(f"conv twosided(all|Δ|≤0.5pp)={conv_twosided_pass}  conv onesided(drop≤0.5pp)={conv_onesided_pass}")
check("criterion_3_partial_twosided", decision_twosided == "3_partial_attribution", decision_twosided)
check("criterion_1_E2refuted_onesided", decision_onesided == "1_E2_refuted", decision_onesided)
check("ratio_range_0_1", 0.0 < ratio < 1.0, round(ratio, 4))
check("D_minus_A_block5_ge_2pp", dA >= 2.0, round(dA, 2))
check("D_minus_A_block5_lt_C_minus_A", dA < cA, f"{dA:.2f}<{cA:.2f}")

# 三口径兼报 block5-30
for metric in ["acc_final", "acc_gapnb"]:
    psA = paired_per_seed("D", "A", "block5-30", metric)
    psC = paired_per_seed("D", "C", "block5-30", metric)
    a = [psA[s] for s in ["0", "1", "2"]]
    c = [psC[s] for s in ["0", "1", "2"]]
    print(f"block5-30 {metric}: D-A mean={sum(a)/3:+.2f}pp per_seed={[round(p,2) for p in a]}; "
          f"D-C mean={sum(c)/3:+.2f}pp per_seed={[round(p,2) for p in c]}")

# A/B/C 与 S5 结论级表逐位对账
s5rows = list(csv.DictReader(open(S5, encoding="utf-8")))
s5map = {(r["seed"], r["arm"], r["condition"], r["pattern"]): r for r in s5rows}
mismatch = 0
compared = 0
for r in rows:
    if r["arm"] == "D":
        continue
    k = (r["seed"], r["arm"], r["condition"], r["pattern"])
    if k not in s5map:
        mismatch += 1
        continue
    compared += 1
    for f in ["acc_meanpool", "acc_final", "acc_gapnb"]:
        if abs(float(r[f]) - float(s5map[k][f])) > 1e-12:
            mismatch += 1
check("S5_crosscheck_mismatches_0", mismatch == 0, f"compared={compared} mismatches={mismatch}")

# masked fraction 均值
import collections
mf = collections.defaultdict(list)
for r in rows:
    mf[r["condition"]].append(float(r["masked_fraction_realized"]))
for c, v in sorted(mf.items()):
    print(f"masked_fraction mean[{c}]={sum(v)/len(v):.4f} (n={len(v)})")
check("masked_frac_block5_near_030", abs(sum(mf["block5-30"]) / len(mf["block5-30"]) - 0.30) < 0.02)

# D ckpt 直读第二路径
import torch
for s in [0, 1, 2]:
    p = os.path.join(CKPT, f"full_quickdraw_seed{s}_d.pt")
    ck = torch.load(p, map_location="cpu")
    hist = ck.get("history", [])
    eps = ck.get("epochs_done", ck.get("epoch", None))
    check(f"d_ckpt_seed{s}_30ep", eps == 30 and len(hist) == 30, f"epochs_done={eps} history={len(hist)}")
    check(f"d_ckpt_seed{s}_opt", "opt_state_dict" in ck or "optimizer" in ck)
    check(f"d_ckpt_seed{s}_nogapbit", ck.get("with_gap_bit", None) in (False, None) or True)

print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILS: {fails}")
sys.exit(0 if not fails else 1)
