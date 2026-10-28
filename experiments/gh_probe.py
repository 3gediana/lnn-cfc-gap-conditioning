#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gh_probe.py — GitHub API 探测（找 N-MNIST 数据镜像）。只读。"""
import json
import urllib.request

def get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "pilot-probe", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

out = {}
try:
    d = get("https://api.github.com/search/repositories?q=nmnist&per_page=15")
    out["repo_total"] = d.get("total_count")
    out["repos"] = [r["full_name"] for r in d.get("items", [])]
except Exception as e:
    out["repo_err"] = f"{type(e).__name__}: {e}"

# 对候选 repo 查 releases（release assets 是 GitHub 托管可下载）
for repo in out.get("repos", [])[:15]:
    try:
        rel = get(f"https://api.github.com/repos/{repo}/releases?per_page=5")
        assets = []
        for r in rel:
            for a in r.get("assets", []):
                assets.append({"tag": r.get("tag_name"), "name": a["name"], "size": a["size"],
                               "url": a["browser_download_url"]})
        if assets:
            out.setdefault("release_assets", {})[repo] = assets
    except Exception as e:
        out.setdefault("rel_err", {})[repo] = f"{type(e).__name__}"

print(json.dumps(out, ensure_ascii=False, indent=1)[:4000])
