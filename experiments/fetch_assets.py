#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_assets.py — S3 数据/代码资产获取（多通道降级尝试）。

通道顺序：
  1) git clone github.com/ye-kyaw-thu/LNN-vs-LSTM（理想：同时得 stress_test.py + download_nmnist.py）
  2) curl raw.githubusercontent.com 单文件（download_nmnist.py / stress_test.py）
  3) 直连 N-MNIST 官方 zip（garrickorchard.com）

产物：experiments/_repo/（克隆仓库或脚本）、data/nmnist/（数据，.gitignore 排除）
本脚本只做获取与校验，不训练。
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIR = os.path.join(PROJECT, "experiments", "_repo")
DATA_DIR = os.path.join(PROJECT, "data", "nmnist")

REPO_URL = "https://github.com/ye-kyaw-thu/LNN-vs-LSTM.git"
RAW = "https://raw.githubusercontent.com/ye-kyaw-thu/LNN-vs-LSTM/main/"
NMNIST_URLS = [
    "https://www.garrickorchard.com/docs/NMNIST_train.zip",
    "https://www.garrickorchard.com/docs/NMNIST_test.zip",
]


def run(cmd: list[str], timeout: int) -> tuple[int, str]:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT after {timeout}s"
    except Exception as exc:  # noqa: BLE001
        return 125, f"{type(exc).__name__}: {exc}"


def main() -> int:
    os.makedirs(os.path.dirname(REPO_DIR), exist_ok=True)
    report: dict = {"attempts": []}

    # ---- 通道 1：git clone ----
    rc, out = run(["git", "clone", "--depth", "1", REPO_URL, REPO_DIR], 150)
    report["attempts"].append({"channel": "git clone", "rc": rc, "tail": out[-600:]})
    if rc == 0 and os.path.isdir(os.path.join(REPO_DIR, ".git")):
        report["repo_cloned"] = True
    else:
        report["repo_cloned"] = False

    # ---- 通道 2：curl 单文件（无论 clone 成败都补 stress_test.py 缺失检查）----
    os.makedirs(REPO_DIR, exist_ok=True)
    for fname in ["download_nmnist.py", "stress_test.py"]:
        dst = os.path.join(REPO_DIR, fname)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            continue
        rc, out = run(["curl", "-sSL", "--connect-timeout", "20", "--max-time", "60",
                       "-o", dst, RAW + fname], 70)
        report["attempts"].append({"channel": f"curl {fname}", "rc": rc, "tail": out[-300:]})
        if rc != 0 or not os.path.exists(dst) or os.path.getsize(dst) < 100:
            if os.path.exists(dst):
                os.remove(dst)
            report.setdefault("missing_files", []).append(fname)

    # ---- 通道 3：N-MNIST zip ----
    os.makedirs(DATA_DIR, exist_ok=True)
    dl_status = []
    for url in NMNIST_URLS:
        name = url.rsplit("/", 1)[-1]
        dst = os.path.join(DATA_DIR, name)
        if os.path.exists(dst) and os.path.getsize(dst) > 1_000_000:
            dl_status.append({"url": url, "status": "exists", "size": os.path.getsize(dst)})
            continue
        rc, out = run(["curl", "-sSL", "--connect-timeout", "20", "--max-time", "420",
                       "-o", dst, url], 430)
        size = os.path.getsize(dst) if os.path.exists(dst) else 0
        dl_status.append({"url": url, "rc": rc, "size": size, "tail": out[-300:]})
        if rc != 0 or size < 1_000_000:
            if os.path.exists(dst):
                os.remove(dst)
    report["nmnist_downloads"] = dl_status

    # ---- 汇总 ----
    have_repo_files = {f: os.path.exists(os.path.join(REPO_DIR, f))
                       for f in ["download_nmnist.py", "stress_test.py"]}
    zips = [f for f in os.listdir(DATA_DIR) if f.endswith(".zip")] if os.path.isdir(DATA_DIR) else []
    report["repo_files"] = have_repo_files
    report["zips_present"] = zips
    report["ok"] = bool(have_repo_files.get("stress_test.py")) and len(zips) > 0
    import json
    out_path = os.path.join(PROJECT, "results", "fetch_assets_report.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: report[k] for k in ["repo_cloned", "repo_files", "zips_present", "ok"]},
                     ensure_ascii=False))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
