# 待判读卡：S7-e2-btrain-arm 空回执对账（receipt-reconcile a4983054）

- 性质：待判读卡。只陈列盘上事实与判读要点，不自动判科学成功；科学结论以既有 ok 回执与 workflow.json 为准。
- 生成：2026-11-01 00:2x build agent 自修补轮 r18。

## 一、空回执事实（ledger 原样）

- ts=2026-10-31T02:56:14+08:00，event=unit-done，project=液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a，stage=S7-e2-btrain-arm，status=**failed**，artifacts=[]、commits=[]、notes=""（空）。
- session 20261031_013539_99927a，duration=4838.3s（≈80.6min），model=stepfun/step-5-preview，54 次 api 调用，total_tokens≈9.30M。

## 二、盘上事实（2026-11-01 00:2x 实测）

- workflow.json：S7-e2-btrain-arm status=**done**，result.status=ok，result_kind=scientific_result，verdict=**falsified**，next_action=continue，result_files 12 个（results/e2_btrain.csv/md/progress/timing、experiments/e2_btrain.py、3 个 ckpt、s7_judge_0297_recheck、notes/handoff/S7-e2-btrain-arm.md 等）在盘。
- 同一 stage 16 分钟后有带产物 ok 回执：10-31T03:12:50（intervention 0297fdde45ac4cbc9dcc4defb11e40b0.md + s7_judge_0297_redelivery_check + STATUS/DECISIONS，commit 82f5894）。
- 判定：02:56 的 failed 空回执是被 03:12 ok 回执取代的超时型失败；verdict=falsified 由 ok 回执链承载。

## 三、待判读要点（交 researcher，本卡不代判）

1. 账簿口径：该 failed 空回执是否标注"superseded by 10-31T03:12 ok"（纯记账勘误）。
2. 与 wrap 空回执（同日 07:42，已由判读卡 e938d438 勘误为"回执写入环节断裂"）是否同因——若同因，属夜间回执写入通道的夜间窗问题，留生产车道，本卡不扩判。
3. 无需重跑。
