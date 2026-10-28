#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s3_probe.py — 列 tonic-datasets S3 桶找 N-MNIST 真实 key。"""
import json
import urllib.request

UA = {"User-Agent": "pilot-probe"}


def get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


out = {}
for prefix in ["NMNIST", "nmnist", "N-MNIST", "n_mnist", "datasets/NMNIST"]:
    url = f"https://tonic-datasets.s3.amazonaws.com/?list-type=2&max-keys=30&prefix={prefix}"
    try:
        body = get(url).decode("utf-8", "replace")
        keys = []
        for part in body.split("<Key>")[1:]:
            keys.append(part.split("</Key>")[0])
        if keys:
            out[prefix] = keys
    except Exception as e:
        out[prefix] = f"{type(e).__name__}: {e}"
print(json.dumps(out, ensure_ascii=False, indent=1)[:3000])
