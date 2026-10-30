---
stage: S7-e2-btrain-arm
kind: experiment
status: ok
did: 实现并全量运行 D 臂（B-train，E2 归因臂）：与 C 臂完全同训练但不带 gap 指示位，3 种子×30ep 收口+144 格同跑评测（D 新增 36 格），落 results/e2_btrain.csv/md+progress。
why: S5 结论级 C−A(block5-30)=+17.49pp 含增强混杂（D3 预注册归因交 E2）；D 臂隔离「训练期激活的 timespans 通路+增强」与「gap 指示位」的贡献，判决 E2 字面主张。
how: e2_btrain.py import full_protocol/pilot helpers（禁改 A/B/C 路径）；train_one_d 与 C 臂逐行同源仅差 with_gap_bit=False+forward_ts；冒烟=tsprobe（ts 梯度非零 0.0217）+seed0 前 5ep loss 1.89→0.85；评测走 B 式 manual-loop+真实 timespans；A/B/C 同跑与 S5 表逐位对账。
result: D−A(block5-30)=+15.31pp（逐种子+21.85/+9.69/+14.38，meanpool 主口径）、D−C=−2.18pp、D clean 降幅 mean+0.24pp（逐种子+1.94/−1.92/+0.71）。预注册判据机械输出=③部分归因（D−A/(C−A)=0.8752；双侧逐种子 clean 约定下 seed0 +1.94pp 超 0.5pp 门线故不落①；单侧字面约定下为①=E2 被反驳——两种约定均支持「训练期激活的时间通路贡献 +17.49pp 增益的 87.5%」）。A/B/C 同跑与 S5 表逐位一致（mismatches=0）；3 训练收敛 PASS（train acc 0.8972/0.8628/0.8977 vs C 臂 0.8907/0.8898/0.9047，ratio 1.007/0.970/0.992）；144 格评测 151.2s。排产实测 41s/ep（低于 C 臂 48s 带，无 gap 位拼接+无争抢）。
next: 交 researcher 判读（归因结论+是否 N-MNIST 前移）；若 partial 则下一单元重跑 all 自动续跑（逐 epoch 原子 ckpt+逐行 eval 落盘，幂等）。
artifacts: [experiments/e2_btrain.py, experiments/ckpt/full_quickdraw_seed0_d.pt, experiments/ckpt/full_quickdraw_seed1_d.pt, experiments/ckpt/full_quickdraw_seed2_d.pt, results/e2_btrain.csv, results/e2_btrain.md, results/e2_btrain_progress.json, results/e2_btrain_timing.json, experiments/logs/e2_btrain_run.log]
info_need: 无
---
