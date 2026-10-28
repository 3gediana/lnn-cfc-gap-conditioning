#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""size_probe.py — GitHub nmnist 仓库体积 + QuickDraw 文件体积（60 秒决策用）。"""
import json
import urllib.request

UA = {"User-Agent": "pilot-probe", "Accept": "application/json"}


def get(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


try:
    st, body = get("https://api.github.com/search/repositories?q=nmnist&per_page=19")
    d = json.loads(body)
    print("== github nmnist repos (size KB)")
    for r in d.get("items", []):
        print(f"  {r['size']:>9} KB  {r['full_name']}")
except Exception as e:
    print("gh err:", e)

print("== quickdraw ndjson HEAD")
for cat in ["airplane", "apple"]:
    u = f"https://storage.googleapis.com/quickdraw_dataset/full/simplified/{cat}.ndjson"
    try:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "pilot-probe"})
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"  {cat}: {r.status} len={r.headers.get('Content-Length')}")
    except Exception as e:
        print(f"  {cat}: {type(e).__name__}: {e}")
