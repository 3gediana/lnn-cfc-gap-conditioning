#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""final_mirror_probe.py — 最后一轮 N-MNIST 镜像探测（HF / GitHub code search / 候选主机）。"""
import json
import urllib.request

UA = {"User-Agent": "pilot-probe", "Accept": "application/json"}
out = {}


def get(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


# 1) HuggingFace datasets 搜索
try:
    st, body = get("https://huggingface.co/api/datasets?search=nmnist&limit=20")
    out["hf_nmnist"] = [d["id"] for d in json.loads(body)]
except Exception as e:
    out["hf_nmnist_err"] = f"{type(e).__name__}: {e}"
try:
    st, body = get("https://huggingface.co/api/datasets?search=n-mnist&limit=20")
    out["hf_n_mnist"] = [d["id"] for d in json.loads(body)]
except Exception as e:
    out["hf_n_mnist_err"] = f"{type(e).__name__}: {e}"

# 2) GitHub code search（未认证，试）
try:
    st, body = get("https://api.github.com/search/code?q=NMNIST_train.zip&per_page=5")
    d = json.loads(body)
    out["gh_code_total"] = d.get("total_count")
    out["gh_code_items"] = [i.get("html_url") for i in d.get("items", [])]
except Exception as e:
    out["gh_code_err"] = f"{type(e).__name__}: {e}"

# 3) 候选主机可达性
probe = {}
for u in [
    "https://huggingface.co/api/datasets/EventBench/n-mnist",
    "https://huggingface.co/datasets/EventBench/n-mnist/resolve/main/README.md",
]:
    try:
        st, body = get(u, 15)
        probe[u] = {"status": st, "len": len(body)}
    except Exception as e:
        probe[u] = f"{type(e).__name__}: {e}"
out["host_probes"] = probe

print(json.dumps(out, ensure_ascii=False, indent=1)[:3000])
