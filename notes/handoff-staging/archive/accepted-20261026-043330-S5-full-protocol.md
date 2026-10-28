---
stage: S5-full-protocol
kind: experiment
status: partial
did: 写好 experiments/full_protocol.py（QuickDraw 全量 50k×30epoch×6 训练+108 格评测，全程断点续跑）并 selftest 四项全过，启动 6 次训练长跑（detach），单元窗口内实测跑到 seed0_ab 第 5/30 epoch 的逐 epoch checkpoint 后交断点。
why: S4 verdict=replicate 要求结论级保真度复现：pilot A@clean=10.43% chance 级系 2-epoch/10k 预算缺口，须全量 30 epoch 复现论文 Table III QuickDraw≈98.6-98.7% 后再 adjudicate H1/H2。
how: 训练路径复用 pilot_threearm.py 同源代码（import 不复制不改写），升级点仅全量数据(42500/7500)/30epoch/逐 epoch checkpoint；d2_timespans 向量化补丁经 68 项 torch.equal 恒等自验+1+1 续跑 bitwise 一致；判读按 S5 须知（meanpool 主口径三口径兼报、C clean 逐种子门控、恒定类消失伴生判据、D7 结论级≈98.6-98.7%）。
result: selftest OVERALL PASS（d2 恒等 68 项、full_splits 42500/7500 确定性与 pilot 子集关系、续跑 max|Δstate|=0、eval 机制 A≡B+掩码率 0.305）；verify_real_size PASS（manual-loop vs 库 B=1 diff=0.0、B>1 崩现场录存）；seed0_ab 训练实测 ~45s/epoch、train acc 0.40→0.84(ep5) 收敛中（pilot 2epoch 仅 0.31）；C 臂瓶颈定位=CPU 循环版 d2_timespans 867ms/batch，向量化后 fwd+bwd 仅 ~190ms/batch，6 训练总预估 ~2.7h。单元窗口内未跑完 6 训练，无 108 格评测、无 CSV/MD（预注册：半程不落表）。
next: 下一单元重跑同一命令 G:/ai/python11/python.exe experiments/full_protocol.py all（逐 epoch checkpoint 无损续跑，已跑行/epoch 自动跳过）：先续跑完 6 训练（ab≈22min/次、c≈32min/次），再自动进入 108 格评测（全量 7500/格，向量化后预计约 8-10min）→ 齐 108 行自动落 results/full_threearm.csv/md 并按 S5 须知出判读；E2 B-train 对照臂与 N-MNIST 结论级基准仍留后续单元。
artifacts: [experiments/full_protocol.py, experiments/full_run.log, experiments/s5_probe.py, experiments/s5_probe2.py, experiments/s5_probe3.py, results/full_progress.json, experiments/ckpt/full_quickdraw_seed0_ab.pt, STATUS.md, notes/DECISIONS.md]
info_need: N-MNIST 免墙镜像（daytime/user-assisted；experiments/download_nmnist_mendeley.py 等数据脚本在位可重跑，结论级基准必需）；harvest 累计 9 条检索需求已消化 5 条（research/harvest/INDEX.md digested=true 可直接用），余 4 条无阻塞本单元。
---
