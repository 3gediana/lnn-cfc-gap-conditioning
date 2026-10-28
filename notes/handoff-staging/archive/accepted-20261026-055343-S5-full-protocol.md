---
stage: S5-full-protocol
kind: experiment
status: partial
did: 复跑 full_protocol.py all 无损续跑：seed0_ab 从 ep15 跑到 30/30 收口（train acc 0.9402→0.9518），seed0_c 新启跑到约 ep26/30，单元截止 kill 交断点。
why: S4 verdict=replicate 续跑链第三单元：pilot 2-epoch 预算缺口致 A@clean=10.43% chance 级，须全量 30 epoch 复现论文 Table III QuickDraw≈98.6-98.7% 后再 adjudicate H1/H2，本单元推进长跑并保全断点。
how: 每 epoch 原子 ckpt（tmp+os.replace）保 kill 无损；重跑同一命令 all 自动从最新 ckpt 续跑并跳过已完成训练；判读按 S5 须知（meanpool 主口径三口径兼报、C clean 逐种子门控、恒定类消失伴生判据、D7 结论级≈98.6-98.7%）；半程不落表（CSV/MD 须 108 行齐）。
result: ckpt 复验 exit=0（seed0_ab 30/30、history 连续、opt 在盘；seed0_c ep26/30 history 连续 opt 在盘，证据 experiments/s5_unit3_ckpt_rerun.txt）；seed0_ab 本单元 16 epoch 用 751.2s≈46.9s/epoch；seed0_c 实测≈47.8s/epoch，比排产估计 64s 低 25.3%（>20%→总排产显式修正：剩余训练≈5819.2s+eval 3827s≈2.68h）；无评测无 CSV/MD（预注册半程不落表）。
next: 下一单元重跑同一命令 G:/ai/python11/python.exe experiments/full_protocol.py all 自动续跑（seed0_c 约 ep27 起；6 训练齐后自动进 108 格评测逐行断点续跑→齐 108 行落 results/full_threearm.csv/md 并按 S5 须知判读）；不硬撑不缩数据；E2 B-train 对照臂与 N-MNIST 结论级基准仍留后续。
artifacts: [experiments/full_protocol.py, experiments/full_run.log, experiments/s5_ckpt_verify.py, experiments/s5_unit3_ckpt_rerun.txt, results/full_progress.json, experiments/ckpt/full_quickdraw_seed0_ab.pt, experiments/ckpt/full_quickdraw_seed0_c.pt, STATUS.md, notes/DECISIONS.md]
info_need: N-MNIST 免墙镜像（daytime/user-assisted；数据脚本在位可重跑，结论级基准必需）；harvest 累计 9 条已消化 5 条（research/harvest/INDEX.md digested=true 可直接用），余 4 条无阻塞本单元。
---
