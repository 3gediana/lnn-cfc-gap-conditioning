# -*- coding: utf-8 -*-
"""73fb33f2 判读补刀：修复 summarize 逐种子 bug 后，用盘上 progress eval_rows 重生成
results/full_threearm.csv/md（不重跑训练/评测），并更新 progress["verdict"]。
diff 证明：CSV 应逐字节一致；MD 仅两行逐种子数字变化。"""
import json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
os.chdir(ROOT)

import full_protocol as F  # noqa: E402

prog = F.load_progress()
rows = prog["eval_rows"]
assert len(rows) == 108, f"eval_rows={len(rows)}"
rows = sorted(rows, key=lambda r: (r["seed"], r["arm"],
                                   F.CONDITIONS.index(r["condition"]), r["pattern"]))
timing = json.load(open(os.path.join(F.RESULTS, "full_timing.json"), encoding="utf-8"))
verify_rep = prog["sanity"].get("verify_real_size", {})

# 备份
for f in ["full_threearm.csv", "full_threearm.md"]:
    shutil.copy2(os.path.join(F.RESULTS, f), os.path.join(F.RESULTS, f + ".bak-73fb33f2"))

summary = F.summarize_full(rows)
prog["verdict"] = summary["verdict"]
F.save_progress(prog)
F.write_csv_md_full(rows, summary, "quickdraw", verify_rep, timing)
print("[regen] done; verdict keys:", sorted(summary["verdict"].keys()))

# diff 核验
for f in ["full_threearm.csv", "full_threearm.md"]:
    r = subprocess.run(["git", "diff", "--no-color", "--", f"results/{f}"],
                       capture_output=True, text=True)
    print(f"\n===== git diff results/{f} =====")
    print(r.stdout[:4000] if r.stdout else "(无差异)")

# 机械断言：CSV 与备份逐字节一致
same = open(os.path.join(F.RESULTS, "full_threearm.csv"), "rb").read() == \
    open(os.path.join(F.RESULTS, "full_threearm.csv.bak-73fb33f2"), "rb").read()
print("\ncsv_byte_identical_vs_backup:", same)
assert same, "CSV 与备份不一致——检查 row 排序/列"
print("OK")
