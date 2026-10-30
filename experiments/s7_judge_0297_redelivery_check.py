# S7 判读重复投递复核（researcher 单元，2026-10-31T03:2x）
# 事件 unit.receipt 0dce44084bad43d8b9fc8ef8e478dcee（S7-e2-btrain-arm，failed 空壳）
# 已由判读单元 0297fdde45ac4cbc9dcc4defb11e40b0 完成首轮全量复跑（s7_judge_0297_recheck.py ALL PASS）。
# 本脚本=第二轮差异/抽样复核（判读速度纪律）：只独立重算结论级关键数字，
# 期望值取自判读笔记/STATUS 的文字结论（非抄回执），与盘上 CSV 直接对账。
# 入口：G:/ai/python11/python.exe experiments/s7_judge_0297_redelivery_check.py
import csv
import sys
from collections import defaultdict

CSV = "results/e2_btrain.csv"
S5_CSV = "results/full_threearm.csv"

fails = []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"{tag} {name} | {detail}")
    if not cond:
        fails.append(name)


rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
check("csv_rows_144", len(rows) == 144, f"rows={len(rows)}")
keys = [(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows]
check("keys_unique", len(set(keys)) == len(keys), f"unique={len(set(keys))}")

# per (seed, arm, condition): mean over 3 patterns of acc_meanpool
cell = defaultdict(list)
for r in rows:
    cell[(r["seed"], r["arm"], r["condition"])].append(float(r["acc_meanpool"]))
mean = {k: sum(v) / len(v) * 100.0 for k, v in cell.items()}  # -> pp

conds = ["clean", "uniform30", "block5-30", "block15-30"]
seeds = ["0", "1", "2"]

# 期望值（判读笔记 §1/§2 文字结论，单位 pp）
exp = {
    ("block5-30", "D-A"): (15.31, [21.85, 9.69, 14.38]),
    ("block5-30", "D-C"): (-2.18, [-0.57, -5.37, -0.61]),
    ("block5-30", "C-A"): (17.49, [22.41, 15.06, 14.99]),
    ("clean", "D-A"): (0.24, [1.94, -1.92, 0.71]),
}
TOL = 0.02  # CSV 单元格 4 位小数舍入容差

for (cond, pair), (exp_mean, exp_seeds) in exp.items():
    a, b = pair.split("-")  # pair "X-Y" = X 减 Y
    per_seed = [mean[(s, a, cond)] - mean[(s, b, cond)] for s in seeds]
    got_mean = sum(per_seed) / 3.0
    check(f"{cond} {pair} mean", abs(got_mean - exp_mean) <= TOL,
          f"got={got_mean:.2f} exp={exp_mean}")
    for s, g, e in zip(seeds, per_seed, exp_seeds):
        check(f"{cond} {pair} seed{s}", abs(g - e) <= TOL, f"got={g:.2f} exp={e}")

# 判据机械输出复核（跑前写死的三条）
d_a = sum(mean[(s, "D", "block5-30")] - mean[(s, "A", "block5-30")] for s in seeds) / 3.0
c_a = sum(mean[(s, "C", "block5-30")] - mean[(s, "A", "block5-30")] for s in seeds) / 3.0
ratio = d_a / c_a
check("ratio_08752", abs(ratio - 0.8752) <= 0.002, f"ratio={ratio:.4f}")
clean_drops = [mean[(s, "D", "clean")] - mean[(s, "A", "clean")] for s in seeds]
twosided = all(abs(d) <= 0.5 for d in clean_drops)  # S5 实现口径：全部 |Δ|≤0.5pp 才落①
onesided = (sum(clean_drops) / 3.0) <= 0.5          # 预注册字面：clean 降幅≤0.5pp
check("conv_twosided_false", twosided is False, f"per_seed={[round(d,2) for d in clean_drops]}")
check("conv_onesided_true", onesided is True, f"mean={sum(clean_drops)/3.0:.2f}")

# S5 结论级表对账（A/B/C 108 格，防漂移；轻量版=全量比对仍很快）
s5 = {}
for r in csv.DictReader(open(S5_CSV, encoding="utf-8")):
    s5[(r["seed"], r["arm"], r["condition"], r["pattern"])] = r
mism = 0
for r in rows:
    if r["arm"] in ("A", "B", "C"):
        k = (r["seed"], r["arm"], r["condition"], r["pattern"])
        s = s5.get(k)
        if s is None:
            mism += 1
            continue
        for col in ("acc_meanpool", "acc_final", "acc_gapnb", "n_eval"):
            if r[col] != s[col]:
                mism += 1
                break
check("s5_crosscheck_108_mismatches_0", mism == 0, f"mismatches={mism}")

# mean±std 全表（4 条件 × 4 臂，meanpool）与判读笔记 §1 第 2 条对账
exp_tbl = {
    "clean": {"A": 92.30, "B": 92.30, "C": 92.89, "D": 92.54},
    "uniform30": {"A": 63.93, "B": 64.37, "C": 86.10, "D": 84.41},
    "block5-30": {"A": 71.03, "B": 69.81, "C": 88.52, "D": 86.33},
    "block15-30": {"A": 72.83, "B": 72.03, "C": 83.55, "D": 80.80},
}
for cond in conds:
    for arm in ("A", "B", "C", "D"):
        got = sum(mean[(s, arm, cond)] for s in seeds) / 3.0
        check(f"tbl {cond} {arm}", abs(got - exp_tbl[cond][arm]) <= TOL,
              f"got={got:.2f} exp={exp_tbl[cond][arm]}")

print()
print("RESULT:", "ALL PASS" if not fails else f"FAIL {fails}")
sys.exit(0 if not fails else 1)
