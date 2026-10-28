---
stage: S3-pilot-threearm
kind: experiment
status: ok
did: 合并分片 98 行后 canonical eval 续跑补齐缺的 10 格（208s），评测矩阵 108/108 行齐，四份契约产物（CSV/MD/progress/timing）落盘，merge 双路径交叉校验+selftest 回归全过。
why: 收口 design.md §四 S2 预注册评测矩阵（三臂×4 条件×3 模式×3 种子=108 行），产出三臂 pilot 表供 S4 判 H1/H2 门线与首里程碑②③。
how: consolidate_progress.py 把分片 14 行 union 写回规范 progress（主 84+分片 14=98，76 个重叠键数值零冲突，避免重算 seed2 B/C 全 24 格）→pilot_threearm.py eval 断点跳过 98 行只算缺的 10 格（≈21s/行）→merge_eval_shards.py --canonical 交叉校验（union=108、CSV 逐字节一致、verdict 一致）→eval_patch_selftest.py exit=0。
result: 108/108 行齐（CSV 108 数据行实核）。clean A=B=10.43%（B−A 逐种子恒 +0.00pp）、C=10.51%；block5-30 B−A=−0.71pp、C−A=+5.36pp（逐种子 +4.08/+4.78/+7.24 一致，C clean 降幅 +0.08pp ≤0.5pp）；block15-30 B−A=−0.73pp、C−A=+1.78pp；uniform30 C−A=+4.94pp；H2 block15−block5 Δ=−0.02pp。门控三门：clean A≡B=0.000pp PASS、A@uniform30 z=5.97>2 PASS、A@clean=10.43% D7≥97% 未达（pilot 2-epoch 纯预算缺口）。机械门控 gate_pass_arm=C、decision=pass、next_action=replicate。本单元 verdict=inconclusive（A/B 输出恒定类表明 pilot 远未收敛，chance 级基数臂差不构成机制证据，H1/H2 不足以 adjudicate），最终判读交 S4。
next: S4-pilot-verdict 判读（researcher；S3 机器态已 done、S4 depends_on 满足）：首里程碑②③验收+H1/H2 adjudicate，必带双 caveat（QuickDraw 数据集降级+D7 保真度缺口）；建议默认 replicate→S5 全量协议（30 epoch 全量保真度复现+N-MNIST 结论级+E2 B-train 对照臂），负结果分支不启动。
artifacts: [results/pilot_threearm.csv, results/pilot_threearm.md, results/pilot_progress.json, results/pilot_timing.json, experiments/pilot_threearm.py, experiments/consolidate_progress.py, experiments/merge_eval_shards.py, experiments/eval_patch_selftest.py, experiments/s3_inspect_progress.py, experiments/s3_per_seed_numbers.py, experiments/s3_final_check.py, experiments/eval_resume.log, experiments/ckpt/, STATUS.md, notes/DECISIONS.md, workflow.json]
info_need: 无（S4 判读依赖全在盘；verdict 出后由 S4 唤醒 researcher 放行 gated→ready）。N-MNIST 免墙镜像仍缺（daytime/user-assisted info_need，S5 结论级基准用；experiments/ 数据脚本在位可直接重跑）。
---

## 上轮遗留勘误保留（2026-10-26T03:1x researcher，unit.receipt 4e46cdbd）

- union 实为 98/108（02:55 快照 92 之后单元结束前又落 6 行）：seed0/seed1 各全 36、seed2 A 12/B 7/C 7；真实缺口=10 格（seed2 B/C × block5-30 模式1,2 + block15-30 模式0,1,2），「缺 seed1C×3」为陈旧快照幻影。
- 「A≡B=0.1043」系准确率值误标：臂间差 A−B=+0.000pp（三种子逐模式恒等，比声称更强）。
- 本单元实跑确认以上勘误并闭环：consolidate 后 inspect 复算 union=98/108、缺 10 格与清单逐格一致；eval 后 CSV 108 行、per-seed 实算 B−A 逐种子恒 0.00pp。
- 03:1x 预览数字与完整数据差异（供 S4 对账）：C 臂 block5 均值 +4.90pp→+5.36pp、seed2 逐种子 +7.06→+7.24（补齐 2 格所致）；B−A −0.67pp→−0.71pp。以 CSV 为准。

## 本单元执行细节（2026-10-26T03:3x lab-executor）

- 环境：terminal python=G:/ai/python11/python.exe（torch 2.10.0+cu128、ncps 0.0.2，RTX 5060 8G，跑前 GPU 0% 空闲）；execute_code 内核无 torch 未用；无残留进程（ps 实证）。
- 时序：unit 起 1792956282 → eval 起 1792956427 → 108 行齐 1792956637（eval 段 208s，其中 98 行跳过 ≈0s、10 行 ≈21s/行）；硬超时 1964s 内余量充足。
- 交叉校验：merge_eval_shards.py --canonical 从主+分片三源重新 union=108，重出 CSV 与 eval 路径逐字节一致（MD 仅计时行差异=合并计时携带 resume_eval_run 真实快照）；selftest 48 用例 hit 恒等 + summarize 门控回归 3/3，exit=0。
- 小补丁（merge_eval_shards.py）：合并计时携带 pilot_timing.json 的 u5_runtime 快照（resume_eval_run eval_sec=208.0），防空壳计时覆盖真实数字；shard_timing 为空=已知不阻塞项（分片进程被硬超时终止未及写 timing）。
- 提交：4ad33cd（产物+STATUS/DECISIONS）、e18c75c（workflow.json 机器态 S3→done+result+dispatch_log+U5 closed）。
