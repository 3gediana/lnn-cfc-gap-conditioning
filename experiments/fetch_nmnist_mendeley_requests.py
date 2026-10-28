# -*- coding: utf-8 -*-
"""Download N-MNIST Train/Test zips from Mendeley Data (works where urllib/curl TLS fails).

2026-10-26: curl(schannel) and urllib both failed TLS handshake to data.mendeley.com,
but python-requests (OpenSSL) gets HTTP 200. Use resumable Range downloads.
"""
from __future__ import annotations

import os
import sys
import time

import requests

BASE = r"D:\hermes-data\research\液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a\data\nmnist"
FILES = [
    ("Test.zip", "https://data.mendeley.com/public-files/datasets/468j46mzdv/files/05a4d654-7e03-4c15-bdfa-9bb2bcbea494/file_downloaded", 169674850),
    ("Train.zip", "https://data.mendeley.com/public-files/datasets/468j46mzdv/files/39c25547-014b-4137-a934-9d29fa53c7a0/file_downloaded", 1011893601),
]
LOG = os.path.join(BASE, "download_requests.log")
CHUNK = 1024 * 1024


def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def download(name: str, url: str, expected: int) -> bool:
    final = os.path.join(BASE, name)
    part = final + ".part"
    if os.path.isfile(final) and os.path.getsize(final) == expected:
        log(f"{name}: already complete ({expected} bytes)")
        return True
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    for attempt in range(1, 8):
        existing = os.path.getsize(part) if os.path.isfile(part) else 0
        if existing > expected:
            os.remove(part)
            existing = 0
        headers = {"Range": f"bytes={existing}-"} if existing else {}
        try:
            with session.get(url, headers=headers, stream=True, timeout=60, verify=True) as r:
                if r.status_code == 416:
                    log(f"{name}: range not satisfiable, restarting")
                    os.remove(part)
                    continue
                if r.status_code not in (200, 206):
                    log(f"{name}: HTTP {r.status_code} attempt {attempt}")
                    time.sleep(5)
                    continue
                mode = "ab" if r.status_code == 206 and existing else "wb"
                if mode == "wb":
                    existing = 0
                log(f"{name}: {r.status_code} start existing={existing} ctype={r.headers.get('content-type')}")
                done = existing
                last_report = done
                with open(part, mode) as fh:
                    for chunk in r.iter_content(CHUNK):
                        if not chunk:
                            continue
                        fh.write(chunk)
                        done += len(chunk)
                        if done - last_report >= 40 * 1024 * 1024:
                            log(f"{name}: {done}/{expected} ({done * 100.0 / expected:.1f}%)")
                            last_report = done
                size = os.path.getsize(part)
                if size == expected:
                    os.replace(part, final)
                    log(f"{name}: DONE {size} bytes")
                    return True
                log(f"{name}: incomplete {size}/{expected}, retry")
        except Exception as exc:  # noqa: BLE001
            log(f"{name}: attempt {attempt} error {type(exc).__name__}: {str(exc)[:200]}")
            time.sleep(5)
    return False


def main() -> int:
    os.makedirs(BASE, exist_ok=True)
    ok = True
    for name, url, expected in FILES:
        ok = download(name, url, expected) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
