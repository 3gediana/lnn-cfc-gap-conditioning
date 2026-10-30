# S7-e2-btrain-arm：E2 归因臂 = D 臂（B-train）结果（% acc，3 种子 mean±std）

- 数据集：quickdraw（论文协议全量：train 42500 / test 7500，与 S5 同 split 种子 12345）
- 训练：D 臂 3 种子×30 epoch，与 C 臂完全同训练（同 block5-30 增强调度 P.make_mask("block5-30",B,L,seed*77+ep,0)、同优化器/批量/CLIP、逐 epoch 原子 ckpt），唯一差异=DrawingClassifier(with_gap_bit=False)+forward_ts（timespans 通路训练期激活）
- 评测：D=36 格（3 种子×4 条件×3 模式，B 式 manual-loop+真实 timespans、无 gap 位）；A/B/C 同跑入表仅用于 D−A/D−C 配对与 S5 对账（非本阶段新增）
- 读表口径：预注册主口径=meanpool（论文口径），三口径 meanpool/gapnb/final 兼报
- 臂：A=库 forward(timespans=None,均匀dt=1)；B=A 共享 ckpt+manual-loop D2 timespans；C=B+gap 指示位+增强训练；D=C 同训练但不带 gap 指示位（timespans 训练期激活）
- 条件：clean / uniform30(逐时间步 Bernoulli 0.3) / block5-30、block15-30（块长 b 划分、每块 Bernoulli 0.3，期望掩码率 30%；3 固定种子化模式跨臂配对）

| 条件 | A | B | C | D | D−A(pp) | D−C(pp) |
|---|---|---|---|---|---|---|
| clean | 92.30±0.86 | 92.30±0.86 | 92.89±0.17 | 92.54±1.02 | +0.24 | -0.34 |
| uniform30 | 63.93±2.86 | 64.37±3.76 | 86.10±0.80 | 84.41±1.15 | +20.48 | -1.69 |
| block5-30 | 71.03±4.10 | 69.81±4.69 | 88.52±0.66 | 86.33±2.35 | +15.31 | -2.18 |
| block15-30 | 72.83±2.80 | 72.03±3.22 | 83.55±1.08 | 80.80±3.16 | +7.96 | -2.75 |

## Sanity
- A/B/C 与 S5 结论级表（results/full_threearm.csv）同跑逐位对账：identical=True，mismatches=0（0=确定性+路径无漂移）
- D 与 B 同 eval 路径：P.eval_arm_condition(model_D, 'B', ...) = forward_ts manual-loop（与 B 臂逐行同分支）；clean 下 D−B=0.24333333333332874pp（不同 ckpt 属预期；路径同一由 B 行对 S5 逐位一致证明）
- D 行实现掩码率 mean=0.2259（名义 0.30）
- 收敛伴生判据（D train acc vs C 臂同种子 80% 门）：{"0": {"D_train_acc": 0.8972, "C_train_acc_ref": 0.8907, "ratio_vs_C": 1.0073, "converged_ge_80pct_C": true}, "1": {"D_train_acc": 0.8628, "C_train_acc_ref": 0.8898, "ratio_vs_C": 0.9697, "converged_ge_80pct_C": true}, "2": {"D_train_acc": 0.8977, "C_train_acc_ref": 0.9047, "ratio_vs_C": 0.9923, "converged_ge_80pct_C": true}}

## 预注册判据机械输出（跑前写死；主口径 meanpool）
- D−A(block5-30) = +15.31pp（逐种子 pp：{'0': 21.85, '1': 9.69, '2': 14.38}）
- C−A(block5-30) = S5 结论级锚点 +17.49pp
- D−C(block5-30) = -2.18pp（=gap 指示位贡献的配对估计）
- D clean 降幅 mean=+0.24pp、逐种子={'0': 1.94, '1': -1.92, '2': 0.71}；双侧约定(实现口径)PASS=False、单侧字面(预注册)PASS=True
- 三口径兼报（block5-30）：{"meanpool": {"D_minus_A": 15.31, "D_minus_C": -2.18}, "final": {"D_minus_A": 0.41, "D_minus_C": -0.38}, "gapnb": {"D_minus_A": 18.41, "D_minus_C": -4.08}}
- **判据=③：decision=partial_attribution，next_action=continue**（幅值比例 D−A/(C−A)=0.8752）
- 判据字面：①D−A≥+2pp 且 clean 降幅≤0.5pp→E2 被反驳（训练期激活即可用）；②D−A<+1pp 且 C−A=+17.49pp→必需 gap 指示位，强化 H1 负结果；③居中→按 D−A/(C−A) 幅值比例部分归因。主口径 meanpool。

## 限制
- QuickDraw 降级数据集（N-MNIST 结论级基准=S8 后续）；L=100 使 block15 为字面块长
- D7 保真度缺口（S5：A@clean 92.30% vs 论文 98.6-98.7%）未在本阶段处理（S9 归因）
- 计时（U5）：{"data_prep_sec": 0.0, "train_runs": {}, "eval_sec": 151.2, "total_sec": 151.3}
