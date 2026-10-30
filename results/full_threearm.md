# S5-full-protocol QuickDraw 全量三臂结果（% acc，3 种子 mean±std，逐种子明细见 CSV）

- 数据集：quickdraw（论文协议全量：首 5000/类×10 类=50k，85/15 seeded split → train 42500 / test 7500；N-MNIST 仍 SSL 墙，结论级基准留后续单元）
- 训练：全量 30 epoch × 6 次（A/B 共享 3 种子 + C-aug 3 种子），逐 epoch checkpoint；臂语义 D1-D3 与 pilot 完全一致（同源代码 import）
- 读表口径：预注册主口径=meanpool（论文口径），三口径 meanpool/gapnb/final 兼报
- 臂：A=库 forward(timespans=None,均匀dt=1)；B=manual-loop+D2 真实 timespans（与 A 共享 checkpoint/掩码）；C=B+gap 指示位+块状增强训练（单独 checkpoint）
- 条件：clean / uniform30(逐时间步 Bernoulli 0.3) / block5-30、block15-30（块长 b 划分、每块 Bernoulli 0.3，期望掩码率 30%；3 固定种子化模式跨臂配对）

| 条件 | A | B | C | B−A(pp) | C−A(pp) |
|---|---|---|---|---|---|
| clean | 92.30±0.86 | 92.30±0.86 | 92.89±0.17 | +0.00 | +0.59 |
| uniform30 | 63.93±2.86 | 64.37±3.76 | 86.10±0.80 | +0.44 | +22.17 |
| block5-30 | 71.03±4.10 | 69.81±4.69 | 88.52±0.66 | -1.22 | +17.49 |
| block15-30 | 72.83±2.80 | 72.03±3.22 | 83.55±1.08 | -0.80 | +10.72 |

## 强制 sanity（S2 入口条件同款）
- clean A≡B：|A−B|=0.000pp → PASS(<0.1pp)
- A@uniform30=63.93% → 方向核对 PASS(z=155.68>2 vs chance)
- A@clean=92.30% → D7 结论级（论文 Table III QuickDraw ≈98.6-98.7%）未达（缺口 -6.30pp）
- 恒定类消失伴生判据：A 臂 clean 三口径={'meanpool': 92.3, 'final': 9.73, 'gapnb': 92.3}，分化=82.57pp → 已分化（非恒定类）
- manual-loop 真实尺寸复验：verify_pass=True，vs 库 B=1 max diff=0.0

## 门线与假设判读（design.md §五；主口径 meanpool）
- H1（block5-30 下 B 或 C ≥+2pp 且该臂 clean 降幅 ≤0.5pp）：B−A=-1.22pp、C−A=+17.49pp；B clean 降幅=+0.00pp、C clean 降幅=+0.59pp → gate_pass_arm=None
- C clean 逐种子降幅（pp）：{'0': 1.82, '1': -0.37, '2': 0.31} → 逐种子门控(全 ≤0.5pp) FAIL
- block5-30 逐种子 C−A（pp）：{'0': 22.41, '1': 15.06, '2': 14.99}
- 三口径兼报（block5-30）：B−A meanpool=-1.22 / gapnb=+0.13 / final=+0.05pp；C−A meanpool=+17.49 / gapnb=+22.50 / final=+0.79pp
- H2（block15 增益 ≥ block5 增益，mean 意义）：Δ=+0.42pp
- 判读：decision=falsified_negative_branch，next_action=redesign

## 限制
- C−A 含增强训练混杂（D3 预注册：门线对 C 为保守存活判据，归因细化=E2 B-train 对照臂，留后续单元）
- QuickDraw L=100（block15 为字面块长）；N-MNIST L=10 场景 block15 退化为整段掩码，结论级须回 N-MNIST 复现
- 计时（U5）：{"data_prep_sec": 1.8, "train_runs": {"seed2_c": 1007.0}, "eval_sec": 128.9, "total_sec": 1139.6}
