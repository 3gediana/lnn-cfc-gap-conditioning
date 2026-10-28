#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_probe.py — S5 首单元开工探针：GPU/计时/ckpt 元数据/数据规模。
用法：G:/ai/python11/python.exe experiments/s5_probe.py
"""
import json
import os
import time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
CKPT = os.path.join(HERE, "ckpt")

print("torch", torch.__version__, "cuda_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu", torch.cuda.get_device_name(0),
          "mem_GB", round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1))

for f in sorted(os.listdir(CKPT)):
    if f.endswith(".pt"):
        d = torch.load(os.path.join(CKPT, f), map_location="cpu", weights_only=False)
        print("ckpt", f, json.dumps({k: v for k, v in d.items() if k != "state_dict"},
                                    ensure_ascii=False))

with open(os.path.join(PROJECT, "results", "pilot_timing.json"), encoding="utf-8") as fh:
    print("pilot_timing:", fh.read())

with open(os.path.join(PROJECT, "results", "pilot_threearm.csv"), encoding="utf-8") as fh:
    lines = fh.read().splitlines()
print("pilot_csv_rows", len(lines) - 1, "header", lines[0])
