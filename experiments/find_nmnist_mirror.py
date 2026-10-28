#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""find_nmnist_mirror.py — 定位可用的 N-MNIST 下载源（Python urllib，绕开 curl schannel 墙）。"""
import json
import re
import urllib.request

UA = {"User-Agent": "pilot-probe"}


def get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url: str) -> dict:
    return json.loads(get(url))


out: dict = {}

# 1) 找 tonic 仓库
try:
    d = get_json("https://api.github.com/search/repositories?q=tonic+event-based+data&per_page=5")
    repos = [r["full_name"] for r in d.get("items", [])]
    out["tonic_repo_candidates"] = repos
except Exception as e:
    out["search_err"] = f"{type(e).__name__}: {e}"
    repos = []

# 2) 对每个候选 repo 取文件树，找 n_mnist 相关源码
for repo in repos[:3]:
    try:
        tree = get_json(f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1")
        files = [t["path"] for t in tree.get("tree", []) if "nmnist" in t["path"].lower() and t["path"].endswith(".py")]
        if not files:
            # 试 master 分支
            tree = get_json(f"https://api.github.com/repos/{repo}/git/trees/master?recursive=1")
            files = [t["path"] for t in tree.get("tree", []) if "nmnist" in t["path"].lower() and t["path"].endswith(".py")]
        out.setdefault("nmnist_src_files", {})[repo] = files[:5]
        for f in files[:2]:
            for branch in ("main", "master"):
                try:
                    src = get(f"https://raw.githubusercontent.com/{repo}/{branch}/{f}").decode("utf-8", "replace")
                    urls = re.findall(r'https?://[^\s"\')]+', src)
                    out.setdefault("nmnist_src_urls", {})[f"{repo}/{f}"] = sorted(set(u for u in urls if "zip" in u.lower() or "nmnist" in u.lower() or "s3" in u.lower() or "drive" in u.lower()))
                    break
                except Exception:
                    continue
    except Exception as e:
        out.setdefault("repo_err", {})[repo] = f"{type(e).__name__}: {e}"

# 3) 直接探测几个已知托管点
candidates = [
    "https://tonic-datasets.s3.amazonaws.com/NMNIST/NMNIST_train.zip",
    "https://tonic-datasets.s3.amazonaws.com/nmnist/NMNIST_train.zip",
    "https://n-mnist.s3.amazonaws.com/NMNIST_train.zip",
]
probe = {}
for u in candidates:
    try:
        req = urllib.request.Request(u, method="HEAD", headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            probe[u] = {"status": r.status, "len": r.headers.get("Content-Length")}
    except Exception as e:
        probe[u] = f"{type(e).__name__}: {e}"
out["head_probes"] = probe

print(json.dumps(out, ensure_ascii=False, indent=1)[:5000])
