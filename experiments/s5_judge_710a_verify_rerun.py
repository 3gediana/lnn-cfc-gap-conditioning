#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_judge_710a_verify_rerun.py — 判读单元补修 verify() 两处倒挂遗留后重跑 sanity。

verify() 的三项指标均为 convention 无关对比（manual-loop vs 库 B=1 同输入 identity、
B>1 崩溃为形状广播、clean A≡B 用原始未掩码 xb）→ 补修前后指标应逐项相同。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PROJ = os.path.dirname(HERE)

import pilot_threearm as P  # noqa: E402
import full_protocol as F  # noqa: E402

F._patch_pilot_d2()

x_tr, y_tr, x_te, y_te = F.full_splits("quickdraw")
rep = P.verify("quickdraw", x_te)
prog = json.load(open(os.path.join(PROJ, "results", "full_progress.json"), encoding="utf-8"))
old = prog["sanity"]["verify_real_size"]

print("rerun:", json.dumps(rep, ensure_ascii=False))
print("old  :", json.dumps(old, ensure_ascii=False))
same = all(str(rep.get(k)) == str(old.get(k)) for k in old) and rep.get("verify_pass") == old.get("verify_pass")
print("METRICS-IDENTICAL:", same)
print("VERIFY-RERUN:", "PASS" if (same and rep.get("verify_pass")) else "FAIL")
sys.exit(0 if (same and rep.get("verify_pass")) else 1)
