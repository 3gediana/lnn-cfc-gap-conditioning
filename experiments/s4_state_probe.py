# -*- coding: utf-8 -*-
"""读 research-project-state.py 输出，打印 4a1c4c0a 课题的判定字段。"""
import json
import re
import subprocess
import sys

out = subprocess.run(
    [sys.executable, "scripts/research-project-state.py"],
    cwd="D:/hermes-data", capture_output=True, text=True,
)
txt = out.stdout + out.stderr
m = re.search(r"\{.*\}", txt, re.S)
if not m:
    print("NO_JSON_FOUND"); sys.exit(1)
d = json.loads(m.group(0))
items = d if isinstance(d, list) else d.get("projects", d.get("items", [d]))
if not isinstance(items, list):
    items = [items]
hits = 0
for p in items:
    s = json.dumps(p, ensure_ascii=False)
    if "4a1c4c0a" in s or "液态" in s:
        hits += 1
        print(json.dumps({k: p.get(k) for k in (
            "project_id", "name", "classification", "terminal_action",
            "ready_stage_ids", "admission_eligible")}, ensure_ascii=False))
if not hits:
    print("PROJECT_NOT_FOUND; top-level keys:", list(d.keys())[:10])
