---
stage: S3-pilot-threearm
kind: experiment
status: partial
did: 复验补丁（selftest exit=0）后跑评测矩阵；串行 22.5s/行超窗，改为 (seed,arm) 三路分片并行，GPU 争抢劣化至 60s/行，硬超时前逐行落盘 92+/108 行，无丢失，CSV/MD 未出（契约=108 行齐）。
why: 执行 design.md §四 S2 预注册评测矩阵（三臂×4 条件×3 模式×3 种子=108 行），供 S4 判 H1/H2 门线与首里程碑②③。
how: eval_shard_runner.py 只复用 pilot_threearm.py 已验证函数、独立 progress 文件零竞争；merge_eval_shards.py 按键去重、108 行齐才写 CSV/MD；续跑=重跑同命令跳过已跑出行。
result: 02:54:59 快照 union 92/108：seed0 全 36 行、seed1 全 36 行、seed2 A 12+B 4+C 4；缺 seed1C×3+seed2B×8+seed2C×8（单元结束前还会增）。sanity：seed0 clean A≡B=0.1043（A−B=0.0）；三读口径非退化（final/gapnb 与 meanpool 同量级）。分片并行被证伪：3 路并发 GPU 86%、单路 22.5→60s/行。
next: 下一单元先 ps 查主评测进程（本单 02:34 起的 canonical eval）是否存活→跑 merge_eval_shards.py 看 union→缺行用两条 shard 命令补（seed2 B/C 各剩 6-8 行，2 路 ≈30-40s/行）或 canonical eval 单跑→108 齐后 merge 出 CSV/MD/timing→交接→S4。
artifacts: [experiments/pilot_threearm.py, experiments/eval_patch_selftest.py, experiments/eval_shard_runner.py, experiments/merge_eval_shards.py, experiments/eval_run.log, experiments/shard_s2ab.log, experiments/shard_s2c.log, results/pilot_progress.json, results/pilot_progress.shard_s2ab.json, results/pilot_progress.shard_s2c.json, experiments/ckpt/]
info_need: 无（窗口内可补齐；若驱动器不再派 S3 需人工重排队）。N-MNIST 免墙镜像仍缺（daytime/user-assisted，S5 结论级用）。
---
