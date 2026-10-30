#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s8_nmnist_probe.py — S8-nmnist-event-loader：N-MNIST .bin 事件格式裁决探针。

目的：在固化 loader 前，用真实数据裁决两种字节解读，并与 2026-10-26 wrap 独立
分布复验结论（notes/DECISIONS.md 10-26 07:6x 条）对账：
  - Train/1/17665.bin 652 条事件，p 字节实测 {0..4}∪{128..132}，129-132 合计
    299/652≈46% 带 128 高位；x∈[1,33]、y∈[0,33]；t 全局/像素分块均不单调。

解读 A（40-bit 打包，README 位描述 + 低位小端待裁决）：
    b0=X, b1=Y, b2=(polarity<<7)|(t>>16), t_low16 = b3,b4 的两种字节序
解读 B（朴素 1+1+1+2）：x=b0, y=b1, p=b2, t=u16(b3,b4)

判据（先写后跑）：
  1) X,Y 必须 ∈[0,33]（34x34 传感器）；
  2) README 声明采样步长 100µs → 正确解读下 t 应全部为 100 的倍数；
  3) 正确解读下 t 范围应覆盖样本全程（不出现 u16 回绕伪影）；
  4) b2 直方图必须复现 10-26 实测 {0..4}∪{128..132}（含高位极性）；
  5) 17665.bin 复算必须与 10-26 数字逐项一致（652 条、299/652）。

输出：results/s8_nmnist_probe.json + stdout 摘要。
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

import numpy as np

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_NM = os.path.join(PROJECT, "data", "nmnist", "unpacked")
OUT = os.path.join(PROJECT, "results", "s8_nmnist_probe.json")

# 10-26 wrap 复验锚点（notes/DECISIONS.md 10-26 07:6x 条）
ANCHOR_FILE = os.path.join(DATA_NM, "Train", "1", "17665.bin")
ANCHOR_NEV = 652
ANCHOR_PHI_N = 299          # 129-132 合计
ANCHOR_PHI_FRAC = 299 / 652  # ≈0.4586

PROBE_FILES = [
    ("Train", "0", "00002.bin"),
    ("Train", "1", "17665.bin"),
    ("Train", "5", "00100.bin"),
    ("Test", "3", "00011.bin"),
    ("Test", "9", "00004.bin"),
]


def read_bin(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    if len(raw) % 5 != 0:
        raise ValueError(f"{path}: {len(raw)} bytes not divisible by 5")
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, 5)


def parse(e, t_low_be=True):
    """解读 A：b0=X,b1=Y,b2=(p<<7)|(t>>16),t_low16 字节序由 t_low_be 选。"""
    x = e[:, 0].astype(np.int64)
    y = e[:, 1].astype(np.int64)
    b2 = e[:, 2].astype(np.int64)
    p = (b2 >> 7) & 1
    t_hi = b2 & 0x7F
    if t_low_be:
        t_lo = (e[:, 3].astype(np.int64) << 8) | e[:, 4].astype(np.int64)
    else:
        t_lo = (e[:, 4].astype(np.int64) << 8) | e[:, 3].astype(np.int64)
    t = (t_hi << 16) | t_lo
    return x, y, p, t, b2


def inv_frac(t):
    """相邻逆序比例（t 非假设排序的度量）。"""
    if len(t) < 2:
        return 0.0
    return float((np.diff(t) < 0).mean())


def summarize_file(path, t_low_be):
    e = read_bin(path)
    x, y, p, t, b2 = parse(e, t_low_be=t_low_be)
    u16_le = (e[:, 3].astype(np.int64)) | (e[:, 4].astype(np.int64) << 8)
    return {
        "path": os.path.relpath(path, PROJECT).replace("\\", "/"),
        "n_events": int(len(e)),
        "bytes": int(len(e) * 5),
        "x_range": [int(x.min()), int(x.max())],
        "y_range": [int(y.min()), int(y.max())],
        "p_on_frac": float(p.mean()),
        "b2_hist": {int(k): int(v) for k, v in sorted(Counter(b2).items())},
        "t_min": int(t.min()),
        "t_max": int(t.max()),
        "t_span": int(t.max() - t.min()),
        "t_mult100_frac": float((t % 100 == 0).mean()),
        "t_mono_frac": float((np.diff(t) >= 0).mean()),
        "t_inv_frac": inv_frac(t),
        "t_distinct": int(len(np.unique(t))),
        "u16le_t_min": int(u16_le.min()),
        "u16le_t_max": int(u16_le.max()),
        "u16le_inv_frac": inv_frac(u16_le),
    }


def main():
    rep = {"anchor": {}, "probe": [], "verdict": {}}

    # ---- 1) 锚点文件：复现 10-26 复验 ----
    if not os.path.exists(ANCHOR_FILE):
        rep["anchor"]["error"] = f"missing {ANCHOR_FILE}"
    else:
        e = read_bin(ANCHOR_FILE)
        b2 = e[:, 2].astype(np.int64)
        x, y = e[:, 0].astype(np.int64), e[:, 1].astype(np.int64)
        u16_le = (e[:, 3].astype(np.int64)) | (e[:, 4].astype(np.int64) << 8)
        hi = b2[(b2 >= 128) & (b2 <= 132)]
        rep["anchor"] = {
            "path": os.path.relpath(ANCHOR_FILE, PROJECT).replace("\\", "/"),
            "n_events": int(len(e)),
            "x_range": [int(x.min()), int(x.max())],
            "y_range": [int(y.min()), int(y.max())],
            "b2_hist": {int(k): int(v) for k, v in sorted(Counter(b2).items())},
            "b2_keys_sorted": sorted(int(k) for k in Counter(b2)),
            "n_129_132": int(len(hi)),
            "frac_129_132": float(len(hi) / len(e)),
            "u16le_t_min": int(u16_le.min()),
            "u16le_t_max": int(u16_le.max()),
            "u16le_inv_frac": inv_frac(u16_le),
            "match_1026": {
                "n_events_652": bool(len(e) == ANCHOR_NEV),
                "p_keys_subset_0_4_128_132": bool(
                    set(int(k) for k in Counter(b2)) <= set(range(0, 5)) | set(range(128, 133))),
                "n_129_132_299": bool(len(hi) == ANCHOR_PHI_N),
                "frac_129_132_approx": abs(len(hi) / len(e) - ANCHOR_PHI_FRAC) < 0.01,
                "x_within_1_33": bool(1 <= x.min() and x.max() <= 33),
                "y_within_0_33": bool(0 <= y.min() and y.max() <= 33),
            },
        }

    # ---- 2) 多样本解读裁决 ----
    for split, cls, name in PROBE_FILES:
        path = os.path.join(DATA_NM, split, cls, name)
        if not os.path.exists(path):
            rep["probe"].append({"path": f"{split}/{cls}/{name}", "error": "missing"})
            continue
        rec = {"split": split, "cls": cls, "name": name}
        for be in (True, False):
            s = summarize_file(path, t_low_be=be)
            rec["t_low_be" if be else "t_low_le"] = s
        rep["probe"].append(rec)

    # ---- 3) 裁决 ----
    v = {}
    be_ok = all(
        r.get("t_low_be", {}).get("t_mult100_frac", 0) > 0.999
        for r in rep["probe"] if "t_low_be" in r)
    le_ok = all(
        r.get("t_low_le", {}).get("t_mult100_frac", 0) > 0.999
        for r in rep["probe"] if "t_low_le" in r)
    v["t_low_be_all_mult100"] = bool(be_ok)
    v["t_low_le_all_mult100"] = bool(le_ok)
    v["chosen"] = "A_bigendian_low16" if be_ok and not le_ok else (
        "A_littleendian_low16" if le_ok and not be_ok else "UNDECIDED")
    spans = [r["t_low_be"]["t_span"] for r in rep["probe"] if "t_low_be" in r]
    v["t_span_min_max"] = [int(min(spans)), int(max(spans))] if spans else None
    mono = [r["t_low_be"]["t_mono_frac"] for r in rep["probe"] if "t_low_be" in r]
    v["t_mono_frac_range"] = [float(min(mono)), float(max(mono))] if mono else None
    rep["verdict"] = v

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)

    print(json.dumps(rep, ensure_ascii=False, indent=1))
    print(f"[probe] wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
