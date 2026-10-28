#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""download_nmnist_mendeley.py — 从 Mendeley Data（N-MNIST 官方托管，tonic 同源）下载并解压。"""
import json
import os
import urllib.request

UA = {"User-Agent": "pilot-probe"}
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT, "data", "nmnist")


def get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main() -> int:
    os.makedirs(DATA_DIR, exist_ok=True)
    d = json.loads(get("https://data.mendeley.com/public-api/datasets/468j46mzdv"))
    files = d.get("files", [])
    listing = [{"filename": f["filename"], "size": f["size"],
                "url": f["content_details"]["download_url"]} for f in files]
    print(json.dumps(listing, ensure_ascii=False, indent=1))

    # 选大文件（zip）
    targets = [f for f in files if f["filename"].lower().endswith(".zip")]
    report = {"listing": listing, "downloads": []}
    for f in targets:
        dst = os.path.join(DATA_DIR, f["filename"])
        url = f["content_details"]["download_url"]
        if os.path.exists(dst) and os.path.getsize(dst) == f["size"]:
            report["downloads"].append({"filename": f["filename"], "status": "exists"})
            continue
        print(f"downloading {f['filename']} ({f['size']} bytes) ...", flush=True)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, \
                 open(dst, "wb") as fh:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    fh.write(chunk)
            ok = os.path.getsize(dst) == f["size"]
            report["downloads"].append({"filename": f["filename"], "status": "ok" if ok else "size_mismatch",
                                        "got": os.path.getsize(dst), "want": f["size"]})
        except Exception as e:
            report["downloads"].append({"filename": f["filename"], "error": f"{type(e).__name__}: {e}"})

    with open(os.path.join(DATA_DIR, "download_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report["downloads"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
