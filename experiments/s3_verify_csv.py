# -*- coding: utf-8 -*-
"""S4-pilot-verdict 独立复算入口（S5 复判可复用）。

对 results/pilot_threearm.csv 重新分组聚合，逐项重算：
  1. 行数/结构完整性（3 种子 x 3 臂 x 4 条件 x 3 模式 = 108）
  2. 各条件 A/B/C meanpool 三种子均值与 B-A / C-A
  3. block5-30 逐种子 C-A（配对明细）
  4. C clean 降幅（mean + 逐种子）
  5. H2: B-A 增益 block15-30 - block5-30
  6. 读表口径敏感性: block5-30 下 C-A 与 B-A 的 meanpool/gapnb/final 三口径
  7. clean A==B 恒等性（9 行 x 3 口径）
  8. A@uniform30 vs chance 二项 z 检验（n=3000 单口径 + n=27000 合并口径）
  9. 实现掩码率均值
 10. pilot_progress.json verdict 块与 CSV 复算对账

退出码 0 = 全部关键项与 CSV 自洽（打印 DIFF 行为差异，需人工裁定）。
"""
import csv
import json
import math
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJ, "results", "pilot_threearm.csv")
PROG_PATH = os.path.join(PROJ, "results", "pilot_progress.json")

CONDITIONS = ["clean", "uniform30", "block5-30", "block15-30"]
ARMS = ["A", "B", "C"]
SEEDS = [0, 1, 2]
METRICS = ["acc_meanpool", "acc_final", "acc_gapnb"]


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["seed"] = int(r["seed"])
        r["pattern"] = int(r["pattern"])
        for m in METRICS:
            r[m] = float(r[m])
        r["masked_fraction_realized"] = float(r["masked_fraction_realized"])
    return rows


def cell(rows, seed, arm, cond, metric):
    vals = [r[metric] for r in rows if r["seed"] == seed and r["arm"] == arm and r["condition"] == cond]
    return sum(vals) / len(vals)


def mean3(rows, arm, cond, metric):
    return sum(cell(rows, s, arm, cond, metric) for s in SEEDS) / 3.0


def pp(x):
    return round(x * 100, 2)


def main():
    rows = load_rows(CSV_PATH)
    out = {}
    diffs = []

    def check(name, got, exp, tol):
        ok = abs(got - exp) <= tol
        if not ok:
            diffs.append((name, got, exp))
        print("%-46s got=%-10s exp=%-10s %s" % (name, got, exp, "OK" if ok else "DIFF"))

    # 1. 结构
    n = len(rows)
    check("row_count", n, 108, 0)
    expected_keys = {(s, a, c, p) for s in SEEDS for a in ARMS for c in CONDITIONS for p in (0, 1, 2)}
    actual_keys = {(r["seed"], r["arm"], r["condition"], r["pattern"]) for r in rows}
    check("key_grid_complete", len(actual_keys), 108, 0)
    check("n_eval_all_3000", len([r for r in rows if r["n_eval"] == "3000"]), n, 0)

    # 2. 各条件 meanpool 三种子均值与臂差
    for cond in CONDITIONS:
        a, b, c = (mean3(rows, arm, cond, "acc_meanpool") for arm in ARMS)
        out[cond] = dict(A=pp(a), B=pp(b), C=pp(c), B_minus_A=pp(b - a), C_minus_A=pp(c - a))
        print("cond=%-11s A=%.2f B=%.2f C=%.2f  B-A=%+.2fpp C-A=%+.2fpp" % (cond, pp(a), pp(b), pp(c), pp(b - a), pp(c - a)))
    check("clean_A", out["clean"]["A"], 10.43, 0.005)
    check("clean_B", out["clean"]["B"], 10.43, 0.005)
    check("clean_C", out["clean"]["C"], 10.51, 0.005)
    check("clean_B_minus_A", out["clean"]["B_minus_A"], 0.00, 0.005)
    check("clean_C_minus_A", out["clean"]["C_minus_A"], 0.08, 0.005)
    check("uniform30_A", out["uniform30"]["A"], 13.27, 0.005)
    check("uniform30_B", out["uniform30"]["B"], 12.92, 0.005)
    check("uniform30_C", out["uniform30"]["C"], 18.21, 0.005)
    check("uniform30_B_minus_A", out["uniform30"]["B_minus_A"], -0.35, 0.005)
    check("uniform30_C_minus_A", out["uniform30"]["C_minus_A"], 4.94, 0.005)
    check("block5_A", out["block5-30"]["A"], 13.69, 0.005)
    check("block5_B", out["block5-30"]["B"], 12.98, 0.005)
    check("block5_C", out["block5-30"]["C"], 19.06, 0.005)
    check("block5_B_minus_A", out["block5-30"]["B_minus_A"], -0.71, 0.005)
    check("block5_C_minus_A", out["block5-30"]["C_minus_A"], 5.36, 0.005)
    check("block15_A", out["block15-30"]["A"], 14.42, 0.005)
    check("block15_B", out["block15-30"]["B"], 13.69, 0.005)
    check("block15_C", out["block15-30"]["C"], 16.20, 0.005)
    check("block15_B_minus_A", out["block15-30"]["B_minus_A"], -0.73, 0.005)
    check("block15_C_minus_A", out["block15-30"]["C_minus_A"], 1.78, 0.005)

    # 3. block5-30 逐种子 C-A
    per_seed_ca = [pp(cell(rows, s, "C", "block5-30", "acc_meanpool") - cell(rows, s, "A", "block5-30", "acc_meanpool")) for s in SEEDS]
    out["block5_per_seed_C_minus_A"] = per_seed_ca
    print("block5-30 per-seed C-A (pp):", per_seed_ca)
    for i, exp in enumerate([4.08, 4.78, 7.24]):
        check("block5_per_seed_C_minus_A[%d]" % i, per_seed_ca[i], exp, 0.005)

    # 4. C clean 降幅（mean + 逐种子；降幅 = C - A，正=C 更差，与 MD/progress 口径一致）
    c_clean_drops = [pp(cell(rows, s, "C", "clean", "acc_meanpool") - cell(rows, s, "A", "clean", "acc_meanpool")) for s in SEEDS]
    out["C_clean_drop_per_seed_pp"] = c_clean_drops
    out["C_clean_drop_mean_pp"] = round(sum(c_clean_drops) / 3.0, 2)
    print("C clean drop (C-A, pp):", c_clean_drops, "mean:", out["C_clean_drop_mean_pp"])
    check("C_clean_drop_mean", out["C_clean_drop_mean_pp"], 0.08, 0.005)
    # C 臂原始精度 block5->block15 变化（ researcher 文档 -2.85pp 口径）与增益口径变化
    c_raw_delta = round(out["block15-30"]["C"] - out["block5-30"]["C"], 2)
    out["C_arm_raw_block15_minus_block5_pp"] = c_raw_delta
    print("C arm raw acc block15-block5 (pp):", c_raw_delta)

    # 5. H2: B-A 增益 block15 - block5
    h2 = round(out["block15-30"]["B_minus_A"] - out["block5-30"]["B_minus_A"], 2)
    out["H2_block15_vs_block5_pp"] = h2
    check("H2_delta", h2, -0.02, 0.005)
    c_h2 = round(out["block15-30"]["C_minus_A"] - out["block5-30"]["C_minus_A"], 2)
    out["H2_C_arm_delta_pp"] = c_h2
    print("C arm block15-block5 gain (pp):", c_h2)

    # 6. 读表口径敏感性（block5-30 与 uniform30 全口径）
    for cond in ["block5-30", "uniform30", "block15-30"]:
        for metric in METRICS:
            a, b, c = (mean3(rows, arm, cond, metric) for arm in ARMS)
            out.setdefault("metric_sensitivity", {})["%s|%s" % (cond, metric)] = dict(B_minus_A=pp(b - a), C_minus_A=pp(c - a))
            print("sens %-11s %-12s B-A=%+.2fpp C-A=%+.2fpp" % (cond, metric, pp(b - a), pp(c - a)))
    check("block5_C_minus_A_meanpool", out["metric_sensitivity"]["block5-30|acc_meanpool"]["C_minus_A"], 5.36, 0.005)
    check("block5_C_minus_A_gapnb", out["metric_sensitivity"]["block5-30|acc_gapnb"]["C_minus_A"], 2.64, 0.005)
    check("block5_C_minus_A_final", out["metric_sensitivity"]["block5-30|acc_final"]["C_minus_A"], 1.30, 0.005)

    # 7. clean A==B 恒等（9 行 x 3 口径）
    clean_rows = [r for r in rows if r["condition"] == "clean"]
    max_ab = max(max(abs(r[m] - s[m]) for m in METRICS) for r in clean_rows if r["arm"] == "A" for s in clean_rows if s["arm"] == "B" and s["seed"] == r["seed"] and s["pattern"] == r["pattern"])
    out["clean_A_minus_B_max_abs_pp"] = pp(max_ab)
    check("clean_A_minus_B_max_abs", pp(max_ab), 0.00, 0.005)
    const_class = all(r["acc_meanpool"] == r["acc_final"] == r["acc_gapnb"] for r in clean_rows if r["arm"] in ("A", "B"))
    out["clean_AB_three_metrics_identical"] = const_class
    print("clean A/B three-metric identical (constant class):", const_class)

    # 8. A@uniform30 二项 z vs chance=0.10
    a_uni = mean3(rows, "A", "uniform30", "acc_meanpool")
    for n_eval in (3000, 27000):
        z = (a_uni - 0.10) / math.sqrt(0.10 * 0.90 / n_eval)
        out["A_uniform30_z_n%d" % n_eval] = round(z, 2)
        print("A@uniform30=%.2f%% vs chance z(n=%d)=%.2f" % (pp(a_uni), n_eval, z))
    check("A_uniform30_z_n3000", out["A_uniform30_z_n3000"], 5.97, 0.005)

    # 9. 掩码率
    mf = [r["masked_fraction_realized"] for r in rows if r["condition"] != "clean"]
    out["mean_masked_fraction"] = round(sum(mf) / len(mf), 4)
    print("mean realized masked fraction:", out["mean_masked_fraction"])

    # 10. progress.json verdict 对账
    with open(PROG_PATH, encoding="utf-8") as f:
        prog = json.load(f)
    v = prog["verdict"]
    check("progress_B_minus_A_block5", round(v["B_minus_A_block5"] * 100, 2), out["block5-30"]["B_minus_A"], 0.005)
    check("progress_C_minus_A_block5", round(v["C_minus_A_block5"] * 100, 2), out["block5-30"]["C_minus_A"], 0.005)
    check("progress_H2", round(v["H2_block15_vs_block5"] * 100, 2), out["H2_block15_vs_block5_pp"], 0.005)
    check("progress_C_clean_drop", v["C_clean_drop_pp"], out["C_clean_drop_mean_pp"], 0.005)  # 该键带 _pp 后缀=pp 单位
    print("progress verdict gate_pass_arm=%s decision=%s next_action=%s" % (v["gate_pass_arm"], v["decision"], v["next_action"]))
    out["progress_verdict"] = {k: v[k] for k in ("gate_pass_arm", "decision", "next_action")}

    # 11. 首里程碑 ② D7 判据
    out["first_milestone_2_A_clean_pct"] = out["clean"]["A"]
    out["D7_threshold_pct"] = 97.0
    out["paper_quickdraw_clean_pct"] = "98.6-98.7"

    print("\n==== SUMMARY ====")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if diffs:
        print("\nDIFFS (need adjudication):")
        for d in diffs:
            print(" ", d)
        return 2
    print("\nALL CHECKS OK (0 diffs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
