#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""consolidate_progress.py — 把主 progress + 分片 progress 的 eval_rows 合并写回规范位
results/pilot_progress.json（S3 三补单元前置）。

动机：分片并行时代 seed2 B/C 的 14 行落在 shard 文件里，主 progress 只有 84 行；
直接跑 eval 会把 seed2 B/C 全部 24 格重算（≈7.6min）。先把 98 行 union 写回规范位，
eval 断点跳过即只算缺的 10 格（≈3-5min）。
竞争前提：已 ps 实证无残留评测进程（2026-10-26T03:3x 本单元复核）。
幂等：可重跑，union 键 (dataset,seed,arm,condition,pattern)，主文件行优先。
"""
import glob
import json
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, "results")

main_path = os.path.join(RESULTS, "pilot_progress.json")
with open(main_path, encoding="utf-8") as fh:
    main = json.load(fh)

rows_by_key = {}
for r in main.get("eval_rows", []):
    key = (r.get("dataset"), r.get("seed"), r.get("arm"), r.get("condition"), r.get("pattern"))
    rows_by_key[key] = r
n_main = len(rows_by_key)

shard_files = sorted(glob.glob(os.path.join(RESULTS, "pilot_progress.shard*.json")))
for f in shard_files:
    with open(f, encoding="utf-8") as fh:
        p = json.load(fh)
    n_new = 0
    for r in p.get("eval_rows", []):
        key = (r.get("dataset"), r.get("seed"), r.get("arm"), r.get("condition"), r.get("pattern"))
        if key not in rows_by_key:
            rows_by_key[key] = r
            n_new += 1
    print(f"[consolidate] {os.path.basename(f)}: +{n_new} rows")

print(f"[consolidate] main={n_main} -> union={len(rows_by_key)}")

# 一致性检查：主/分片对同一键的数值必须一致（ researcher 03:1x 判读已验证 seed2A 双份零差异，
# 这里对全部重叠键再复核一次，防静默数据分歧）
conflicts = []
by_key_all = {}
for f in [main_path] + shard_files:
    with open(f, encoding="utf-8") as fh:
        p = json.load(fh)
    for r in p.get("eval_rows", []):
        key = (r.get("dataset"), r.get("seed"), r.get("arm"), r.get("condition"), r.get("pattern"))
        by_key_all.setdefault(key, []).append(r)
for key, rs in by_key_all.items():
    if len(rs) > 1:
        vals = {(r.get("acc_meanpool"), r.get("acc_final"), r.get("acc_gapnb")) for r in rs}
        if len(vals) > 1:
            conflicts.append((key, vals))
if conflicts:
    print(f"[consolidate] CONFLICT {len(conflicts)} keys, e.g. {conflicts[:3]}")
    raise SystemExit(3)
print(f"[consolidate] overlap keys checked: {sum(1 for v in by_key_all.values() if len(v) > 1)}, conflicts=0")

main["eval_rows"] = sorted(rows_by_key.values(),
                           key=lambda r: (r["seed"], r["arm"], r["condition"], r["pattern"]))
tmp = main_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(main, fh, ensure_ascii=False, indent=2)
os.replace(tmp, main_path)
print(f"[consolidate] canonical progress written: {len(main['eval_rows'])} rows; "
      f"sanity keys={sorted(main.get('sanity', {}).keys())}")
