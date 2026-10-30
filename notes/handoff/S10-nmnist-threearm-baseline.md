---
stage: S10-nmnist-threearm-baseline
kind: experiment
status: ok
did: N-MNIST 三臂结论级基准全量跑完：epoch 矛盾裁决定案（10ep）、6/6 训练收口、108 行评测落表、判据机械输出 H1=falsified。
why: H1 需回论文原文数据集 N-MNIST 复演（QuickDraw 为 F3 降级数据集），S8 loader+S9 放行后本阶段执行结论级基准。
how: import-not-copy 实现 nmnist_threearm.py（掩码 view (B,L,1,1,1) 适配）；selftest 六门+冒烟四门（实测 11.15s/ep）过后跑 all；逐 epoch 原子 ckpt+逐行原子落盘；独立复算 33 项全 PASS 后才报数。
result: meanpool 主口径 3 种子 mean：block5-30 B−A=+0.09pp（逐种子 +0.53/+0.04/−0.29）、clean B−A=+0.00pp→H1=falsified（预注册负结果分支）；clean A≡B=0.000pp、uniform30 z=266.86、三口径分化 45.08pp 全过；D7 A@clean=98.12% vs 论文 Table I 0.9938 缺口 −1.26pp（≤3pp 未触发 caveat）；C 臂 C−A=+9.47pp 但 clean 逐种子 0.95/0.43/0.62 不全≤0.5pp→C_gate_pass=False；H2 Δ=−0.09pp 不 adjudicate。epoch=10ep 定案（run 脚本明文+日志 10 行+Table I 0.9938 三源一致；Table V 30ep 双记 caveat）。
next: researcher 判读（H1 N-MNIST 终判+D7 记账+C 臂保守门+S11 QuickDraw LR decay 归因+S6 打包前评估）；next_action=redesign 为预注册机械输出，最终路线由判读定。
artifacts: [experiments/nmnist_threearm.py, experiments/ckpt/nmnist_seed0_ab.pt, experiments/ckpt/nmnist_seed0_c.pt, experiments/ckpt/nmnist_seed1_ab.pt, experiments/ckpt/nmnist_seed1_c.pt, experiments/ckpt/nmnist_seed2_ab.pt, experiments/ckpt/nmnist_seed2_c.pt, results/nmnist_threearm.csv, results/nmnist_threearm.md, results/nmnist_progress.json, results/nmnist_timing.json, experiments/s10_recheck.py, experiments/s10_recheck.txt, experiments/s10_ckpt_verify.txt, experiments/logs/nm_smoke.log, experiments/logs/nm_all.log, experiments/logs/nm_report.log]
info_need: 无
---
