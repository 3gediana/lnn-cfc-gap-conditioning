---
stage: S5-full-protocol
kind: experiment
status: partial
did: detach 重跑 full_protocol.py all：ab 臂 3 ckpt 在盘自动跳过，C 臂按修正 Convention 从零重训——seed0_c/seed1_c 30/30 收口（train acc 0.8907/0.8898），seed2_c 到 ep9/30 时 02:54:51 主动 kill 交断点（硬顶 03:02:09 前留门控窗口），kill 后 ckpt 校验 exit=0。
why: 第七单元=C 臂重训+修正 Convention 重算单元（第六单元算子先行已收口、禁批量训练解除）：旧 C ckpt 为掩码 Convention 倒挂训练已移存 superseded，须按修正 Convention 重训 3×30ep 后再重算 108 格落结论级表。
how: 每 epoch 原子 ckpt（kill 无损）；开工三查（ps 无本课题训练残留+progress/ckpt 状态在盘+修正代码 full_protocol.py:180 在位）；收工三查（taskkill+会话 kill 后 ps 实证无残留、s5_ckpt_verify.py 复跑 exit=0 六 ckpt history 连续+opt 在盘、log 末行与 ckpt epochs_done 三方互证）；速率只认实测（56-58s/ep）。
result: C 臂重训 2/3 收口：seed0_c 30/30 acc 0.8907（1737.9s≈57.9s/ep）、seed1_c 30/30 acc 0.8898（1735.1s≈57.8s/ep）——均显著高于旧倒挂 Convention 的 0.6885/0.7144（训练/评测分布对齐的预期效应，D7 相关但未落表不宣称）；seed2_c 9/30 acc 0.8497@507.5s（56.4s/ep，resume from ep10）；ab 臂 3×30/30 未动（0.9518/0.9661/0.9688）；eval_rows=0（半程不落表，预注册合规）；速率 56-58s/ep vs 历史 46-53s/ep 带 +9~26%，归因=sibling 课题 58b37930 physionet 下载（--workers 32，pid 478，01:37:57 起在飞）CPU 争抢，GPU 单租户非争抢；剩余=seed2_c 21ep≈20min+评测 108 行≈3min≈23min。
next: 下一单元重跑同一命令 G:/ai/python11/python.exe experiments/full_protocol.py all：自动跳过 5 个 30/30、从 seed2_c ep10 无损续跑（~21ep）→6/6 齐自动进 108 格评测（≈167s）→齐 108 行自动落 results/full_threearm.csv/md→S5 收口判读（meanpool 主口径三口径兼报、C clean 逐种子门控、A/B 恒定类消失伴生判据、D7 结论级≈98.6-98.7% 数量级；落表前不宣称 D7）。开工仍先 ps 防双开（注意 sibling 下载进程属别的课题、不碰）。
artifacts: [experiments/full_run.log, experiments/s5_unit7_metrics.json, experiments/s5_unit7_ckpt_rerun.txt, experiments/ckpt/full_quickdraw_seed0_c.pt, experiments/ckpt/full_quickdraw_seed1_c.pt, experiments/ckpt/full_quickdraw_seed2_c.pt, results/full_progress.json, STATUS.md, notes/DECISIONS.md]
info_need: 无（排产已用实测项：C 臂 56-58s/ep 下界；sibling 下载进程可能仍在飞，下一单元实测复核速率即可，无需外部信息）
---
