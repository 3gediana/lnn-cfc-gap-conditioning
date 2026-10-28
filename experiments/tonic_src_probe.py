#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tonic_src_probe.py — 取 tonic 的 n_mnist.py 源码，提取下载 URL。"""
import re
import urllib.request

UA = {"User-Agent": "pilot-probe"}


def get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


for path in ["tonic/datasets/n_mnist.py", "tonic/datasets/NMNIST.py"]:
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/neuromorphs/tonic/{branch}/{path}"
        try:
            src = get(url).decode("utf-8", "replace")
            urls = sorted(set(re.findall(r'https?://[^\s"\')]+', src)))
            print(f"== {url}")
            for u in urls:
                print("   ", u)
            break
        except Exception as e:
            print(f"-- {url}: {type(e).__name__}: {e}")
