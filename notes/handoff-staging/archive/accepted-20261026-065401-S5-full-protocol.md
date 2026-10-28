---
stage: S5-full-protocol
kind: experiment
status: partial
did: detach 重跑 full_protocol.py all，从 seed0_c ep27 无损续跑：seed0_c 30/30 收口、seed1_ab 新启 30/30 收口、seed1_c 跑到 ep10/30 主动 kill 交断点，本单元共推进 44 个 epoch，零协议变更。
why: S5 续跑链第四单元：30 epoch×6 训练跨夜窗，按 D6 逐 epoch 原子 checkpoint 分单元推进，跑不完写断点不硬撑、不缩数据。
how: 开工三查（ps 无残留+ckpt 复验 exit=0+续跑路径代码核验）→06:16:40 detach 重跑 all→日志实证 resume seed=0 arm=c from epoch 26→每 epoch 原子落盘→06:51:05 主动 kill→kill 后 s5_ckpt_verify.py 复验 exit=0（history 连续+opt 在盘+无半截文件）→排产按双实测速率重算。
result: seed0_c 30/30（acc 0.6679→0.6885，4ep 186.8s≈46.7s/ep）；seed1_ab 30/30（acc 0.9661，30ep 1381.8s≈46.1s/ep）；seed1_c ep10/30（acc 0.5822）。双速率实测 ab≈46.1-47.0、c≈46.7-47.8s/ep，与 06:1x 校准后排产一致（64s 估计项出清）；剩余训练 80ep≈63min+eval≈64min≈2.11h>夜窗剩余 69min→预计夜窗内 1 个 checkpoint 单元，seed2_c+108 格评测交下一窗/白天。窗口内无评测无 CSV/MD（半程不落表）；D7 不提前声称（train acc≠test acc）。
next: 下一单元重跑同一命令自动从 seed1_c ep11 续跑（预计完成 seed1_c 收口+seed2_ab 30/30）；seed2_c 收口+108 格评测+CSV/MD 落表交后续单元；E2 B-train 对照臂与 N-MNIST 结论级基准仍留后续。
artifacts: [experiments/full_protocol.py, experiments/full_run.log, experiments/s5_unit4_metrics.json, experiments/s5_unit4_ckpt_rerun.txt, results/full_progress.json, experiments/ckpt/full_quickdraw_seed0_c.pt, experiments/ckpt/full_quickdraw_seed1_ab.pt, experiments/ckpt/full_quickdraw_seed1_c.pt, STATUS.md, notes/DECISIONS.md]
info_need: 无
---
