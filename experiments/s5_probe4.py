#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_probe4.py — 读 workflow.json 的 S5 阶段定义（actions/inputs/estimate）。"""
import json
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(PROJ, "workflow.json"), encoding="utf-8") as fh:
    d = json.load(fh)
print("top keys:", list(d.keys()))
stages = d.get("stages", [])
print("n_stages:", len(stages))
for s in stages:
    if isinstance(s, dict) and "S5" in str(s.get("id", "")):
        print(json.dumps(s, ensure_ascii=False, indent=1))
