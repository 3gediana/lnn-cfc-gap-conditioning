---
stage: S4-pilot-verdict
kind: analysis
status: ok
did: 先用 python 对 pilot_threearm.csv 独立复算（37 项全过 exit=0）再下判，pilot verdict 落 results/pilot_verdict.md/json，STATUS/DECISIONS 同步更新并提交 65f1992。
why: 按 design.md §五门线+admission.first_milestone ②③ 对三臂 pilot 做终判：H1/H2 adjudicate、首里程碑验收、定 next_action，负结果分支是否启动以此为准。
how: experiments/s3_verify_csv.py 只读 CSV 重算全部数字（不采信 MD/回执），与门线逐条对账；H1 看机械门控（meanpool 口径 C−A≥+2pp 且 clean 降幅≤0.5pp）+D3 保守存活语义；H2 看 block15−block5 增益；首里程碑②③按 admission 条文判。
result: 复算 37/37 与 CSV 自洽。首里程碑②未达（A@clean=10.43% chance 级 vs D7≥97%，论文 QuickDraw clean≈98.6-98.7%）③达成、①已满足。H1=inconclusive：机械门控 gate_pass_arm=C/decision=pass（block5-30 C−A=+5.36pp 逐种子 +4.08/+4.78/+7.24、C clean +0.08pp）但 B−A=−0.71pp 噪声内、chance 级基数+增强混杂+读表口径敏感（C−A meanpool +5.36/gapnb +2.64/final +1.30pp，final<+2pp 门）三条均不构成机制证据。H2=falsified（Δ=−0.02pp；C 臂 block15−block5 raw −2.85pp/增益 −3.58pp 反向）。总 verdict=inconclusive、next_action=replicate（=S5-full-protocol），负结果分支不启动。
next: researcher 判读单元按 verdict 放行 S5-full-protocol（gated→ready，无 depends_on 不自动放行）+同型关闭将自动生成的 S4-pilot-verdict-replicate 空阶段；S5=30 epoch 全量保真度复现+N-MNIST 结论级基准+E2 B-train 对照臂，判读须知已写入 STATUS。
artifacts: [results/pilot_verdict.md, results/pilot_verdict.json, experiments/s3_verify_csv.py, experiments/s3_verify_csv_output.txt, experiments/s4_state_probe.py, STATUS.md, notes/DECISIONS.md]
info_need: N-MNIST 免墙镜像（daytime/user-assisted，S5 结论级基准必需；experiments/ 数据脚本在位可重跑）；看板卡 t_f6e7bac5 同步留给带 kanban 工具的统筹/执行单元（本 profile 无 kanban 工具）。
---
