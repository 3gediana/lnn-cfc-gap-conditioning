#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nm_probes_recheck.py — nm_negative_probes 独立复算（不 import 被测代码，读盘上行重算）。

复算项（全部从 results/nm_negative_probes.csv + nm_dt_response_spectrum.json +
nm_negative_probes_progress.json + S10 的 results/nmnist_threearm.csv 独立重算）：
  1. CSV 结构：108 行、键唯一、(probe,seed,cond,pattern) 网格完备、n_eval=10000、
     masked_fraction≈0.30（clean=0）。
  2. 判据①：C_no_dt−A（block5-30，3 种子 mean）=+9.58pp、逐种子 16.49/6.85/5.41、
     verdict=training_dominant_supported；C−A=+9.47pp 与 S10 锚点对账；
     推理期 dt 净效应 C−C_no_dt≈−0.11pp。
  3. 判据②：dt*=20（独立实现饱和点定义）、R_max=0.199260、flat=False、
     verdict=supported；finite_all=True。
  4. 判据③：clean 口径切换差=0.0pp<0.3pp PASS。
  5. 恒等自检：A_ref/C_dt 与 S10 CSV 同 (seed,cond,pattern) 行 max|diff|<5e-4。
  6. progress↔CSV↔spectrum 一致性；MD 关键数字在场。
exit=0 全 PASS；证据落 experiments/nm_probes_recheck.txt。
"""
import json
import os
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(PROJECT, "results")
ok = True
lines = []


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    msg = f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}"
    print(msg)
    lines.append(msg)


def read_csv(path):
    with open(path, encoding="utf-8") as fh:
        rows = [ln.rstrip("\n").split(",") for ln in fh if ln.strip()]
    return rows[0], rows[1:]


print("[recheck] 1. CSV 结构 ...")
hdr, data = read_csv(os.path.join(R, "nm_negative_probes.csv"))
check("108 data rows", len(data) == 108, f"n={len(data)}")
keys = [(r[0], int(r[2]), r[3], int(r[4])) for r in data]
check("keys unique", len(set(keys)) == 108, f"unique={len(set(keys))}")
probes = {"C_dt", "C_no_dt", "A_ref", "C_no_dt_nogap"}
conds = {"clean", "uniform30", "block5-30"}
seeds = {0, 1, 2}
pats = {0, 1, 2}
want = {(p, s, c, q) for p in probes for s in seeds for c in conds for q in pats}
check("grid complete (4 probes x 3 seeds x 3 conds x 3 patterns)",
      set(keys) == want, f"missing={len(want - set(keys))} extra={len(set(keys) - want)}")
check("n_eval all 10000", all(int(r[5]) == 10000 for r in data))
mf_ok = all((float(r[6]) == 0.0) if r[3] == "clean" else abs(float(r[6]) - 0.30) < 0.06
            for r in data)
check("masked_fraction: clean=0 / 其余 ≈0.30", mf_ok)

print("[recheck] 2. 判据①主探针（独立聚合）...")


def agg(probe, cond, col=7):
    """每种子对 3 模式取均值（round 4 位，与判据同路径），再 3 种子 mean；返回 (mean3, per_seed)。"""
    per = {}
    for s in sorted(seeds):
        vals = [round(float(r[col]), 4) for r in data
                if r[0] == probe and r[3] == cond and int(r[2]) == s]
        per[s] = sum(vals) / len(vals)
    return sum(per.values()) / len(per), per


cnd_b5, cnd_ps = agg("C_no_dt", "block5-30")
a_b5, a_ps = agg("A_ref", "block5-30")
cdt_b5, _ = agg("C_dt", "block5-30")
diff_pp = (cnd_b5 - a_b5) * 100
check("C_no_dt(block5-30)=90.57%", abs(cnd_b5 * 100 - 90.57) < 0.02, f"got={cnd_b5 * 100:.2f}")
check("A_ref(block5-30)=80.99%", abs(a_b5 * 100 - 80.99) < 0.02, f"got={a_b5 * 100:.2f}")
check("C_dt(block5-30)=90.45%", abs(cdt_b5 * 100 - 90.45) < 0.02, f"got={cdt_b5 * 100:.2f}")
check("C_no_dt-A=+9.58pp", abs(diff_pp - 9.58) < 0.02, f"got={diff_pp:+.2f}")
ps = {s: round((cnd_ps[s] - a_ps[s]) * 100, 2) for s in sorted(seeds)}
exp_ps = {0: 16.49, 1: 6.85, 2: 5.41}   # 判据路径值（先 round 4 位再差）
check("per-seed ≈ 16.49/6.85/5.41（±0.02pp rounding 容差）",
      set(ps) == set(exp_ps) and all(abs(ps[s] - exp_ps[s]) <= 0.02 for s in exp_ps),
      f"got={ps}（独立路径；seed2 真值≈5.405 跨 rounding 边界，与判据路径差 0.01pp，"
      f"不影响冻结判据——判据看 3 种子 mean）")
v1 = ("training_dominant_supported" if diff_pp >= 5.0
      else "inference_dt_dominant_contradiction" if diff_pp < 2.0 else "inconclusive")
check("criterion1 verdict=training_dominant_supported", v1 == "training_dominant_supported",
      f"got={v1}")
check("C-A=+9.47pp", abs((cdt_b5 - a_b5) * 100 - 9.47) < 0.02,
      f"got={(cdt_b5 - a_b5) * 100:+.2f}")
infer_dt = (cdt_b5 - cnd_b5) * 100
check("推理期 dt 净效应 ≈ -0.11pp（|·|<0.5pp=推理期无增益）",
      abs(infer_dt + 0.11) < 0.02, f"got={infer_dt:+.2f}")

print("[recheck] 3. 判据②dt 响应谱（独立复算 dt*）...")
with open(os.path.join(R, "nm_dt_response_spectrum.json"), encoding="utf-8") as fh:
    spec = json.load(fh)
b5 = spec["conditions"]["block5-30"]
rvals = {int(k): v["rel_L2_response_vs_dt1"] for k, v in b5["per_dt"].items()}
r_max = max(rvals.values())
dt_star = None
for dt in [2, 5, 10, 20]:
    if rvals[dt] >= 0.95 * r_max:
        dt_star = dt
        break
if dt_star is None:
    dt_star = ">20"
check("R 谱与盘上一致（0/0.073098/0.148303/0.181729/0.19926）",
      rvals == {1: 0.0, 2: 0.073098, 5: 0.148303, 10: 0.181729, 20: 0.19926},
      f"got={rvals}")
check("dt*=20（独立复算）", dt_star == 20, f"got={dt_star}")
check("R_max=0.199260", abs(r_max - 0.19926) < 1e-6, f"got={r_max}")
check("flat=False", not b5["flat"])
check("finite_all=True", b5["finite_all"] is True)
v2 = ("inconclusive_flat" if b5["flat"] else "falsified" if dt_star == 2 else "supported")
check("criterion2 verdict=supported", v2 == "supported", f"got={v2}")
check("dt_scan 点集={1,2,5,10,20}", spec["dt_scan"] == [1, 2, 5, 10, 20])
check("稳健性：uniform30/clean 均 dt*=20",
      spec["conditions"]["uniform30"]["dt_star"] == 20
      and spec["conditions"]["clean"]["dt_star"] == 20)

print("[recheck] 4. 判据③clean 口径切换 ...")
cnd_c, _ = agg("C_no_dt", "clean")
cdt_c, _ = agg("C_dt", "clean")
switch_pp = abs(cnd_c - cdt_c) * 100
check("clean 切换差=0.0pp<0.3pp PASS", switch_pp < 0.3, f"got={switch_pp:.4f}pp")

print("[recheck] 5. 恒等自检（vs S10 同行）...")
_, s10 = read_csv(os.path.join(R, "nmnist_threearm.csv"))
s10_map = {(r[2], int(r[1]), r[3], int(r[4])): float(r[7]) for r in s10}
worst = 0.0
for r in data:
    if r[0] == "A_ref":
        ref = s10_map[("A", int(r[2]), r[3], int(r[4]))]
        worst = max(worst, abs(float(r[7]) - ref))
    elif r[0] == "C_dt":
        ref = s10_map[("C", int(r[2]), r[3], int(r[4]))]
        worst = max(worst, abs(float(r[7]) - ref))
check("A_ref/C_dt vs S10 同行 max|diff|<5e-4", worst < 5e-4, f"got={worst:.6f}")

print("[recheck] 6. progress 一致性 + MD 关键数字 ...")
with open(os.path.join(R, "nm_negative_probes_progress.json"), encoding="utf-8") as fh:
    prog = json.load(fh)
check("progress rows=108", len(prog["rows"]) == 108)
check("progress status=done", prog["status"] == "done")
check("progress smoke gates_all_pass", prog["smoke"]["gates_all_pass"] is True)
pc = prog["criteria"]["criterion1_main_probe"]
check("progress 判据①与复算一致",
      abs(pc["C_no_dt_minus_A_pp"] - 9.58) < 0.02
      and pc["verdict"] == "training_dominant_supported")
check("progress 判据②与复算一致",
      prog["criteria"]["criterion2_dt_spectrum"]["dt_star"] == 20
      and prog["criteria"]["criterion2_dt_spectrum"]["verdict"] == "supported")
check("progress 判据③ pass",
      prog["criteria"]["criterion3_clean_switch_sanity"]["pass"] is True)
check("progress identity_pass", prog["criteria"]["crosschecks"]["identity_pass"] is True)
csv_keys = {(r[0], int(r[2]), r[3], int(r[4])) for r in data}
prog_keys = {(r["probe"], r["seed"], r["condition"], r["pattern"]) for r in prog["rows"]}
check("progress rows 键集 == CSV 键集", csv_keys == prog_keys)
with open(os.path.join(R, "nm_negative_probes.md"), encoding="utf-8") as fh:
    md = fh.read()
for token in ["+9.58pp", "training_dominant_supported", "dt*=20", "0.0000pp",
              "identity_pass=True", "nm_negative_probes.py all", "C_no_dt"]:
    check(f"MD 含关键内容 [{token}]", token in md)

print(f"[recheck] OVERALL: {'PASS' if ok else 'FAIL'}")
with open(os.path.join(PROJECT, "experiments", "nm_probes_recheck.txt"), "w",
          encoding="utf-8") as fh:
    fh.write("\n".join(lines) + f"\n[recheck] OVERALL: {'PASS' if ok else 'FAIL'}\n")
sys.exit(0 if ok else 1)
