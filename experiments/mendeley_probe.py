#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mendeley_probe.py — Mendeley Data 公共 API 找 N-MNIST zip 直链。"""
import json
import urllib.request

UA = {"User-Agent": "pilot-probe", "Accept": "application/json"}


def get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def show(url: str) -> None:
    try:
        body = get(url)
        print(f"== {url}  ({len(body)} bytes)")
        try:
            d = json.loads(body)
            print(json.dumps(d, ensure_ascii=False, indent=1)[:3000])
        except Exception:
            print(body[:500])
    except Exception as e:
        print(f"-- {url}: {type(e).__name__}: {e}")


show("https://data.mendeley.com/public-api/datasets/468j46mzdv")
show("https://data.mendeley.com/public-api/datasets/468j46mzdv/files")
