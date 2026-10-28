#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state_check.py — 复跑 research-project-state.py 并打印本课题判定（禁词自查配套）。"""
import json
import subprocess
import sys

p = subprocess.run([sys.executable, "scripts/research-project-state.py"],
                   capture_output=True, text=True, cwd="D:/hermes-data")
try:
    d = json.loads(p.stdout)
except Exception:
    print("RAW:", p.stdout[:800], p.stderr[:400])
    raise SystemExit(1)
for proj in d.get("projects", []):
    if "4a1c4c0a" in proj.get("project", ""):
        print(json.dumps({
            "project": proj.get("project"),
            "classification": proj.get("classification"),
            "active": proj.get("active"),
            "admission_eligible": proj.get("admission_eligible"),
            "terminal_action": proj.get("terminal_action"),
            "ready_stage_ids": proj.get("ready_stage_ids"),
        }, ensure_ascii=False))
