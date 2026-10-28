---
stage: S5-full-protocol
kind: experiment
status: partial
did: 续跑 full_protocol.py all 从 seed1_c ep11 无损续跑，本单元推进 80 epoch 使训练 6/6 全量收口（seed1_c/seed2_ab/seed2_c 各 30/30），108 格评测 167.3s 落表；落表后发现掩码 Convention 倒挂 bug，六项证据坐实后作废本轮数值、应用 3 处修正并回归全 PASS。
why: S5=QuickDraw 全量保真度复现主线（S4 verdict=replicate），训练跨夜窗需逐 epoch checkpoint 续跑；落表数值与训练精度矛盾（A@clean=chance 而 train acc 0.95+）必须查根因，不能把 bug 假象当科学结论。
how: 开工三查（ckpt verify exit=0+进程/GPU 无残留）后 detach 重跑 all；6 训练逐个查 ckpt 跳过已跑齐；写 s5_mask_convention_probe.py 六项决定性证据（T1 直推 vs T3 管线、T4 实际清零率、T5 d2 语义、T6 修正后复算）+s5_mask_fix_regression.py R1-R3 回归；C ckpt 移存 superseded、progress stale 行清空使下一单元 all 自愈。
result: 训练 6/6：seed0_ab 0.9518/seed0_c 0.6885/seed1_ab 0.9661/seed1_c 收口/seed2_ab 0.9688/seed2_c 0.6840（本单元 20+30+30ep，1046.7/1438.7/1454.3s）。评测 108/108 落表但 Convention 倒挂全部作废：T1 ckpt 直推 clean=0.9160、T3 现管线=0.0962、T4 clean 输入 100% 帧被清零（uniform30 实际清零 86.3%）、T6 修正后 clean 0.9160/uniform30 0.6138/block5-30 0.6431/block15-30 0.6978（n=2048 seed0）。修正 3 处 xb*mask→xb*(1-mask)，回归 R1-R3 全 PASS。排产修正：评测 3827s→167.3s（补丁前 CPU 循环路径估计出清）。D7 预览 91.6% vs 论文 98.6-98.7% 差 ~7pp，不作结论。
next: 下一单元重跑 G:/ai/python11/python.exe experiments/full_protocol.py all：自动重训 C 臂 3×30ep（≈72min，ckpt 已移存故从零始）→按修正 Convention 重算 108 行（≈3min）→落 results/full_threearm.csv/md→S5 收口判读；跑不完写断点不硬撑；S3/S4 pilot 重算交 researcher 复审。
artifacts: [results/full_threearm.csv, results/full_threearm.md, results/full_threearm_CONVENTION_NOTE.md, results/full_progress.json, results/full_timing.json, experiments/full_protocol.py, experiments/pilot_threearm.py, experiments/s5_mask_convention_probe.py, results/s5_mask_convention_probe.json, experiments/s5_mask_fix_regression.py, experiments/s5_mask_fix_regression.log, experiments/s5_reset_stale_eval.py, experiments/full_run.log, STATUS.md, notes/DECISIONS.md]
info_need: 无
