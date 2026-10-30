"""S5 第八单元收工复算：full_threearm.csv 结构+数字独立校验（不采信 MD/回执）。"""
import csv
import json
import os
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(PROJECT, "results", "full_threearm.csv")
PROG = os.path.join(PROJECT, "results", "full_progress.json")

fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" | " + detail) if detail else ""))
    if not cond:
        fails.append(name)


with open(CSV, encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))

check("csv_data_rows_108", len(rows) == 108, f"rows={len(rows)}")
keys = [(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows]
check("csv_keys_unique_108", len(set(keys)) == 108, f"unique={len(set(keys))}")

seeds = sorted({r["seed"] for r in rows})
arms = sorted({r["arm"] for r in rows})
conds = sorted({r["condition"] for r in rows})
pats = sorted({r["pattern"] for r in rows})
check("csv_dims_3x3x4x3", (len(seeds), len(arms), len(conds), len(pats)) == (3, 3, 4, 3),
      f"seeds={seeds} arms={arms} conds={conds} pats={pats}")

# 三口径数值合法且在 [0,1]（列名 acc_meanpool/acc_gapnb/acc_final）
bad = [k for r in rows for k in ("acc_meanpool", "acc_gapnb", "acc_final")
       if not (0.0 <= float(r[k]) <= 1.0)]
check("csv_values_in_01", not bad, f"bad={bad[:5]}")

# 与 progress eval_rows 逐行一致
with open(PROG, encoding="utf-8") as fh:
    prog = json.load(fh)
prow = {(r["seed"], r["arm"], r["condition"], r["pattern"]): r for r in prog["eval_rows"]}


def csv_val(k, col="acc_meanpool"):
    return float([r for r in rows
                  if (r["seed"], r["arm"], r["condition"], r["pattern"]) == k][0][col])


diffs = [k for k in keys if k in prow and
         abs(float(prow[k]["meanpool"]) - csv_val(k)) > 1e-9]
check("csv_matches_progress_eval_rows", len(prow) == 108 and not diffs,
      f"prog_rows={len(prow)} diffs={diffs[:3]}")

# 复算 mean（3 种子×3 模式）与 MD 表对账（MD 是 00:33 新表）


def mean_of(arm, cond, col="acc_meanpool"):
    vals = [float(r[col]) for r in rows if r["arm"] == arm and r["condition"] == cond]
    return sum(vals) / len(vals)


md_expect = {  # (arm, cond): MD 表中 meanpool 数值（%）
    ("A", "clean"): 92.30, ("B", "clean"): 92.30, ("C", "clean"): 92.89,
    ("A", "uniform30"): 63.93, ("B", "uniform30"): 64.37, ("C", "uniform30"): 86.10,
    ("A", "block5-30"): 71.03, ("B", "block5-30"): 69.81, ("C", "block5-30"): 88.52,
    ("A", "block15-30"): 72.83, ("B", "block15-30"): 72.03, ("C", "block15-30"): 83.55,
}
mism = []
for (arm, cond), exp in md_expect.items():
    got = mean_of(arm, cond) * 100
    if abs(got - exp) > 0.01:
        mism.append((arm, cond, round(got, 2), exp))
check("md_table_recomputed_from_csv", not mism, f"mismatch={mism}")

# clean A≡B（sanity）
check("sanity_clean_A_equiv_B", abs(mean_of("A", "clean") - mean_of("B", "clean")) < 1e-9,
      f"|A-B|={abs(mean_of('A','clean')-mean_of('B','clean'))*100:.4f}pp")

# verdict 块一致性
v = prog["verdict"]
check("verdict_block_present", v is not None and v.get("decision") == "falsified_negative_branch",
      f"decision={v.get('decision')} next_action={v.get('next_action')} gate={v.get('gate_pass_arm')}")

print()
print("OVERALL:", "PASS" if not fails else f"FAIL ({fails})")
sys.exit(0 if not fails else 1)
