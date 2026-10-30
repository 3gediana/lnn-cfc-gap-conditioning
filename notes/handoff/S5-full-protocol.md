---
stage: S5-full-protocol
kind: experiment
status: ok
did: detach 重跑 full_protocol.py all：自动跳过 5 个 30/30、seed2_c 从 ep10 无损续跑 21ep 收口，6/6 齐自动进 108 格评测并落 results/full_threearm.csv/md 结论级表。
why: S5 唯一剩余断点=seed2_c 21ep+评测+落表；本单元完成 S5 完成判据（结论级表 108 行 CSV/MD+s5_ckpt_verify rc=0）。
how: 开工三查（ps 无 G:/ai 残留+ckpt verify exit=0+续跑路径代码级核验）后 detach 续跑、每 epoch 原子 ckpt；收工复跑 s5_ckpt_verify.py exit=0+s5_unit8_csv_recheck.py 8 项全 PASS（108 行/唯一键/MD 表由 CSV 复算逐格一致）。
result: seed2_c 30/30（acc 0.9047@1007.0s≈47.95s/ep 历史带内）；eval 108/108@128.9s。meanpool：clean A=B=92.30/C=92.89；uniform30 C−A=+22.17pp；block5-30 B−A=−1.22/C−A=+17.49pp；block15-30 C−A=+10.72pp。sanity：A≡B=0.000pp、z=155.68、恒定类消失（分化 82.57pp）。门线 gate=None（B 幅值不过；C 幅值过但 clean 降幅 +0.59pp 且逐种子 0.61/0.37/0.78 不全≤0.5）→falsified_negative_branch/redesign；H2 Δ=+0.42pp；D7 未达（92.30% vs 论文 98.6-98.7%，缺口 −6.30pp）。终判交收口判读。
next: S5 收口判读（researcher analysis：H1/H2 终判+C 逐种子门控+D7 结论级）；其后=S3/S4 pilot 按修正 Convention 重算交复审、N-MNIST loader、E2 B-train。
artifacts: [results/full_threearm.csv, results/full_threearm.md, results/full_progress.json, experiments/full_run.log, experiments/s5_unit8_csv_recheck.py, experiments/s5_unit8_csv_recheck.txt, experiments/s5_unit8_window_probe.py, results/full_threearm_CONVENTION_NOTE.md]
info_need: 无
---
