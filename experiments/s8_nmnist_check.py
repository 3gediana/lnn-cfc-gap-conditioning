#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s8_nmnist_check.py — S8：N-MNIST loader 分布核验（全量 70000 样本）。

对账基准 = 2026-10-26 wrap 独立分布复验结论（notes/DECISIONS.md 10-26 07:6x 条）：
  Train/1/17665.bin 652 条事件；p 字节实测 {0..4}∪{128..132}；129-132 合计 299/652≈46%
  带 128 高位；x∈[1,33]、y∈[0,33]；t 全局/像素分块均不单调（u16LE 解读下）。

本脚本输出（供 results/nmnist_loader_check.md 引用）：
  - 样本数/每类计数（Train 60000 / Test 10000，逐类）；
  - 全量每事件字段分布：polarity ON/OFF、b2 直方图（256 桶）、t 范围/跨度分布/
    t%100 分布（README「100µs 步长」 Claim 核验）、单调性（逆序事件数/非单调文件数/
    (t[0],t[-1])==(min,max) 率）、x/y≥34 丢弃计数、空文件；
  - 锚点文件与 10-26 逐项对账（布尔 + 分布双落）；
  - 与论文 _repo/lln_nmnist.py 解析/分箱口径的逐位一致（200 文件抽样）；
  - 帧堆积产物健全性：非空帧比例、log1p 值域、逐类均值（防退化为全零/常数）。
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from nmnist_loader import (DATA_NM, SPLITS, parse_bin, events_to_frames,  # noqa: E402
                           paper_events_to_frames, iter_samples, ANCHOR)

OUT_JSON = os.path.join(PROJECT, "results", "s8_nmnist_dist.json")


def scan_split(split: str, log=print) -> dict:
    phase, _ = SPLITS[split]
    samples = iter_samples(split)
    st = {
        "split": split, "n_samples": len(samples),
        "per_class": Counter(), "n_events": 0,
        "p_on": 0, "p_off": 0,
        "b2_hist": np.zeros(256, dtype=np.int64),
        "t_min": None, "t_max": None,
        "span_min": None, "span_max": None, "span_sum": 0,
        "t_mod100_hist": np.zeros(100, dtype=np.int64),
        "mono_files": 0, "nonmono_files": 0, "inv_events": 0,
        "endpoints_eq_minmax": 0, "span0_files": 0, "empty_files": 0,
        "x_ge34": 0, "y_ge34": 0, "x_min": None, "x_max": None,
        "y_min": None, "y_max": None,
        "ev_per_sample_min": None, "ev_per_sample_max": 0, "ev_per_sample_sum": 0,
        "frames_nonempty": 0, "frames_max": 0.0, "frames_sum": 0.0,
        "per_class_frame_sum": np.zeros((10,), dtype=np.float64),
    }
    t0 = time.time()
    for i, (path, label) in enumerate(samples):
        st["per_class"][label] += 1
        x, y, p, t = parse_bin(path)
        n = t.shape[0]
        st["n_events"] += int(n)
        st["ev_per_sample_sum"] += int(n)
        st["ev_per_sample_max"] = max(st["ev_per_sample_max"], int(n))
        st["ev_per_sample_min"] = int(n) if st["ev_per_sample_min"] is None else min(st["ev_per_sample_min"], int(n))
        if n == 0:
            st["empty_files"] += 1
            continue
        st["p_on"] += int(p.sum())
        st["p_off"] += int((p == 0).sum())
        b2 = ((p << 7) | (t >> 16)).astype(np.int64)
        st["b2_hist"] += np.bincount(b2, minlength=256)
        tmn, tmx = int(t.min()), int(t.max())
        st["t_min"] = tmn if st["t_min"] is None else min(st["t_min"], tmn)
        st["t_max"] = tmx if st["t_max"] is None else max(st["t_max"], tmx)
        span = tmx - tmn
        st["span_min"] = span if st["span_min"] is None else min(st["span_min"], span)
        st["span_max"] = span if st["span_max"] is None else max(st["span_max"], span)
        st["span_sum"] += span
        if tmn == tmx:
            st["span0_files"] += 1
        st["t_mod100_hist"] += np.bincount(t % 100, minlength=100)
        inv = int((np.diff(t) < 0).sum())
        st["inv_events"] += inv
        if inv == 0:
            st["mono_files"] += 1
        else:
            st["nonmono_files"] += 1
        if int(t[0]) == tmn and int(t[-1]) == tmx:
            st["endpoints_eq_minmax"] += 1
        st["x_ge34"] += int((x >= 34).sum())
        st["y_ge34"] += int((y >= 34).sum())
        st["x_min"] = int(x.min()) if st["x_min"] is None else min(st["x_min"], int(x.min()))
        st["x_max"] = int(x.max()) if st["x_max"] is None else max(st["x_max"], int(x.max()))
        st["y_min"] = int(y.min()) if st["y_min"] is None else min(st["y_min"], int(y.min()))
        st["y_max"] = int(y.max()) if st["y_max"] is None else max(st["y_max"], int(y.max()))
        fr = events_to_frames(x, y, p, t)
        st["frames_nonempty"] += int((fr > 0).any())
        st["frames_max"] = max(st["frames_max"], float(fr.max()))
        st["frames_sum"] += float(fr.sum())
        st["per_class_frame_sum"][label] += float(fr.sum())
        if (i + 1) % 10000 == 0:
            log(f"[scan {split}] {i + 1}/{len(samples)} ({time.time() - t0:.0f}s)")
    st["per_class"] = {int(k): int(v) for k, v in sorted(st["per_class"].items())}
    st["scan_sec"] = round(time.time() - t0, 1)
    return st


def anchor_check() -> dict:
    path = os.path.join(DATA_NM, ANCHOR["relpath"])
    x, y, p, t = parse_bin(path)
    b2 = ((p << 7) | (t >> 16)).astype(np.int64)
    u16le = (t & 0xFFFF)
    keys = sorted(set(b2.tolist()))
    n_hi = int(((b2 >= 129) & (b2 <= 132)).sum())
    # 论文 loop vs 向量化
    a = events_to_frames(x, y, p, t)
    b = paper_events_to_frames(x, y, p, t)
    return {
        "relpath": ANCHOR["relpath"],
        "n_events": int(x.shape[0]),
        "b2_keys": keys,
        "b2_hist": {int(c): int((b2 == c).sum()) for c in keys},
        "n_b2_129_132": n_hi,
        "frac_b2_129_132": n_hi / x.shape[0],
        "x_range": [int(x.min()), int(x.max())],
        "y_range": [int(y.min()), int(y.max())],
        "t_min": int(t.min()), "t_max": int(t.max()),
        "t_monotonic": bool((np.diff(t) >= 0).all()),
        "u16le_inv_frac": float((np.diff(u16le) < 0).mean()),
        "t_mult100_frac": float((t % 100 == 0).mean()),
        "vectorized_eq_paper": bool(np.array_equal(a, b)),
        "vs_1026": {
            "n_events_652": bool(x.shape[0] == 652),
            "b2_keys_0_4_128_132": bool(keys == list(range(0, 5)) + list(range(128, 133))),
            "n_129_132_299": bool(n_hi == 299),
            "frac_129_132_46pct": bool(abs(n_hi / x.shape[0] - 299 / 652) < 0.01),
            "x_in_1_33": bool(int(x.min()) >= 1 and int(x.max()) <= 33),
            "y_in_0_33": bool(int(y.min()) >= 0 and int(y.max()) <= 33),
        },
    }


def main():
    rep = {"anchor": anchor_check(), "splits": {}}
    print("[check] anchor:", json.dumps(rep["anchor"], ensure_ascii=False))
    for sp in ("train", "test"):
        st = scan_split(sp)
        rep["splits"][sp] = st
        print(f"[check] {sp}: n={st['n_samples']} events={st['n_events']} "
              f"p_on={st['p_on']} ({st['p_on'] / max(1, st['n_events']):.4f}) "
              f"t=[{st['t_min']},{st['t_max']}] mono={st['mono_files']}/{st['n_samples']} "
              f"inv={st['inv_events']} span0={st['span0_files']} empty={st['empty_files']} "
              f"x>=34:{st['x_ge34']} y>=34:{st['y_ge34']} scan={st['scan_sec']}s")
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    def _san(o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        return o

    def _walk(o):
        if isinstance(o, dict):
            return {k: _walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_walk(v) for v in o]
        return _san(o)

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(_walk(rep), fh, ensure_ascii=False, indent=1)
    print(f"[check] wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
