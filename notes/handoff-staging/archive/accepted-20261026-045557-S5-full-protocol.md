---
stage: S5-full-protocol
kind: experiment
status: partial
did: 校验 kill 后 ckpt 完整（seed0_ab ep7/30）后重跑 full_protocol.py all 断点续跑：detach 进程确认从 ep8 无损恢复（model+opt+history 全恢复），单元窗口内继续训练到约 ep13/30 后交断点。
why: S4 verdict=replicate 的续跑链第二单元：pilot A@clean=10.43% chance 级系 2-epoch 预算缺口，须全量 30 epoch 复现论文 Table III QuickDraw≈98.6-98.7% 后再 adjudicate H1/H2，本单元只负责把长跑往前推并保全断点。
how: 每 epoch 原子 ckpt（tmp+os.replace）保 kill 无损；重跑同一命令 all 即自动从最新 ckpt 续跑并跳过已完成训练；判读按 S5 须知（meanpool 主口径三口径兼报、C clean 逐种子门控、恒定类消失伴生判据、D7 结论级≈98.6-98.7%）；排产实测基准 ab≈46s/epoch、c≈64s/epoch、eval 108 格≈64min（A 1.2s/B 52.4s/C 52.7s 每格@7500）。
result: ckpt 完整性复验 exit=0（epochs_done=7/30、history 1-7 连续、opt state 在盘、train acc 0.8993@323.2s）；续跑实证 [full-train] resume seed=0 arm=ab from epoch 7 → ep8 loss=0.5722 acc=0.8802 (45s)，实测 ~46s/epoch 与首单元一致；单元硬超时 421s（04:50:11 起）内推进到约 ep13/30（以 full_run.log 与 ckpt epochs_done 为准），无 108 格评测、无 CSV/MD（预注册半程不落表）。
next: 下一单元重跑同一命令 G:/ai/python11/python.exe experiments/full_protocol.py all 自动续跑（seed0_ab 约 ep14 起，逐 epoch 原子落盘 kill 无损；6 训练跑齐后自动进 108 格评测逐行断点续跑→齐 108 行自动落 results/full_threearm.csv/md 并按 S5 须知判读）；排产剩余≈2.2h 训练+≈64min 评测，预计还需 3-4 个 checkpoint 单元，尾部交下一窗/白天，不硬撑不缩数据；E2 B-train 对照臂与 N-MNIST 结论级基准仍留后续。
artifacts: [experiments/full_protocol.py, experiments/full_run.log, experiments/s5_ckpt_verify.py, results/full_progress.json, experiments/ckpt/full_quickdraw_seed0_ab.pt, STATUS.md, notes/DECISIONS.md]
info_need: N-MNIST 免墙镜像（daytime/user-assisted；experiments/download_nmnist_mendeley.py 等数据脚本在位可重跑，结论级基准必需）；harvest 累计 9 条检索需求已消化 5 条（research/harvest/INDEX.md digested=true 可直接用），余 4 条无阻塞本单元。
---
