---
stage: S5-full-protocol
kind: experiment
status: ok
did: 写并实跑 experiments/operator_bench.py（CfC/液态单元 16 项算子基准：τ-tie/scale-state/dt=0 收缩/梯度/B>1 边界+d2 向量化收益/108 格构成/同步开销/逐样本/训练步），落 results/operator_bench.md，F8 算子墙写入 workflow.json，零修复落地（FIX-1 被 E3 数据否决），回归 68+48 项全 PASS。
why: fb-ab50d0ec9f「先优化算子再跑实验」：C 臂重训与 108 格重算等批量训练前，先定位算子数值稳定性与效率问题并给出 A/B 是否重训判定。
how: 全部数字实测落 results/operator_bench.json；修复门槛=数值恒等且收益显著（E3 实测延迟同步仅 +0.2% 噪声→否决）；不改 site-packages 共享库；禁 30epoch 训练（E6 仅个位数 step 计时即丢弃）；回归=full_protocol selftest 68 项 case-device 恒等+eval_patch_selftest 48 用例 hit 恒等+门控 3/3。
result: N0 Convention 锚定 PASS（clean A≡B=0.9121、输入修改帧=0.0、block5-30 实际掩码率 0.3059）；N1 LTC dt=0 NaN 硬墙（不在科学路径，CfC ts=0 有限）；N2 scale-state 爆炸不复现（s≤1e4 全有限有界）；N3 dt=0 有界+有限 PASS 但强收缩不成立（真实尺寸 1.24→0.96，修正 u2 迷你结论）；N4 真实 D2 模式 ‖∇_ts‖=0.0307 参数梯度全有限，恒定 dt≥15 压力测试 ∇_ts 爆炸至 1.7e18（协议 dt≤6 不触发）；N5 B>1 崩溃边界+manual-loop 恒等 4.05e-06；E1 d2 向量化 3103× 恒等；E2 108 格构成 165.6s vs 实测 167.3s（偏差 1.0%）；E3 同步开销 +0.2%→FIX-1 否决；E4 逐样本 46ms/样本（批式 56×）；E6 训练 ~50s/ep 落在实测带。零修复→前向数值逐位不变→A/B ckpt 不需重训。
next: C 臂重训 3×30ep≈72min（Convention 修正原因，与算子无关）+修正 Convention 重算 108 行≈3min→落 results/full_threearm.csv/md→S5 收口判读（meanpool 主口径三口径兼报、C clean 逐种子门控、D7≈98.6-98.7% 数量级；QuickDraw 108 格落表前不宣称 D7）。
artifacts: [experiments/operator_bench.py, results/operator_bench.json, results/operator_bench.md, experiments/operator_regression_selftest.log, experiments/operator_regression_evalpatch.log, experiments/s5_operator_unit_update_workflow.py, workflow.json]
info_need: 无（决策点留给 researcher：是否击穿 W-LAUNCH——torch.compile/融合 cell 改变前向数值→需 A/B 也重训 6×30ep≈4.6h，operator_bench.md §4/§5 已量化收益代价）
---
