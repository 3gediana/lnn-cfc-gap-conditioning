# 待判读卡：S5-full-protocol 空回执对账（receipt-reconcile a4983054）

- 性质：待判读卡。按修理任务口径"只从盘上事实重建待判读卡，禁止把空回执自动判科学成功"——本卡只陈列盘上事实与判读要点，科学结论以既有 ok 回执与 workflow.json 为准，本卡不重新判决、不追认任何成功。
- 生成：2026-11-01 00:2x build agent 自修补轮 r18。空回执来源：night-production.jsonl unit-done。

## 一、空回执事实（ledger 原样）

- ts=2026-10-27T01:41:09+08:00，event=unit-done，project=液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a，stage=S5-full-protocol，status=**failed**，artifacts=[]、commits=[]、notes=""（空）。
- session 20261027_001642_30bbe2，duration=5071.5s（≈84.6min，超 tick 预算的典型时长），model=stepfun/step-5-preview，52 次 api 调用，total_tokens≈5.10M。

## 二、盘上事实（2026-11-01 00:2x 实测）

- workflow.json：S5-full-protocol status=**done**，result.status=ok，result_kind=scientific_result，verdict=**falsified**，next_action=redesign，result_files 10 个（results/full_threearm.csv/md、full_progress.json、experiments/full_protocol.py 等）全部在盘。
- notes/handoff/S5-full-protocol.md 在盘（mtime 10-31 00:37）。
- 同一 stage 后续有三次带产物的 ok 回执：10-27T03:00:00（artifacts 8 项+commit ca44643）、10-28T03:21:40（intervention 1f338cdb+commit 7d997c2）、10-31T00:42:14（results 全套+2 commits，仪表盘 scientific_results 中 S5-full-protocol verdict=falsified 即来自此条）。
- 判定：01:41 的 failed 空回执是被后续成功执行取代的超时型失败（5071s），科学结论（falsified→redesign）由 ok 回执链承载，不依赖本空回执。

## 三、待判读要点（交 researcher，本卡不代判）

1. 账簿口径：该 failed 空回执是否标注"superseded by 10-27T03:00 ok"（纯记账勘误，不动科学结论）。
2. 5071s 超时是否需要在 PLAYBOOK 粒度上记一次（实验单元时长预算 vs 实际 full-protocol 运行时长）。
3. 无需重跑、无需复算——verdict 已有三次 ok 回执与 results/ 全套文件支撑。
