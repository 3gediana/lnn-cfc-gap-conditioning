#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pypi_probe.py — 经 PyPI JSON API 找 tonic 的仓库地址（绕开 pip SSL 墙）。"""
import json
import urllib.request

UA = {"User-Agent": "pilot-probe"}


def get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


try:
    d = json.loads(get("https://pypi.org/pypi/tonic/json"))
    info = d["info"]
    print(json.dumps({
        "version": info.get("version"),
        "home_page": info.get("home_page"),
        "project_urls": info.get("project_urls"),
        "summary": info.get("summary"),
    }, ensure_ascii=False, indent=1))
except Exception as e:
    print(f"pypi_err: {type(e).__name__}: {e}")
