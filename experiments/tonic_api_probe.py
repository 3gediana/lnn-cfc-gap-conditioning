#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tonic_api_probe.py — 全走 api.github.com（可用通道）取 tonic 的 NMNIST 数据集源码。"""
import base64
import json
import re
import urllib.request

UA = {"User-Agent": "pilot-probe"}


def get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url: str) -> dict:
    return json.loads(get(url))


# 1) 文件树
tree = None
for branch in ("main", "master"):
    try:
        tree = get_json(f"https://api.github.com/repos/neuromorphs/tonic/git/trees/{branch}?recursive=1")
        print(f"branch={branch} ok")
        break
    except Exception as e:
        print(f"branch={branch}: {type(e).__name__}: {e}")
if tree is None:
    raise SystemExit("no tree")

paths = [t["path"] for t in tree.get("tree", []) if t["path"].endswith(".py") and "mnist" in t["path"].lower()]
print("mnnist-ish files:", paths)

# 2) 取源码（contents API，base64）
for p in paths:
    try:
        c = get_json(f"https://api.github.com/repos/neuromorphs/tonic/contents/{p}")
        src = base64.b64decode(c["content"]).decode("utf-8", "replace")
        urls = sorted(set(re.findall(r'https?://[^\s"\')]+', src)))
        print(f"\n== {p}")
        for u in urls:
            print("   ", u)
    except Exception as e:
        print(f"-- {p}: {type(e).__name__}: {e}")
