# S5-full-protocol QuickDraw 全量三臂结果（% acc，3 种子 mean±std，逐种子明细见 CSV）

> **作废（superseded，2026-10-27T01:3x 确认、02:1x 判读维持）**：本表全部数值按掩码
> Convention 倒挂实现（`xin=xb*mask` 保留掩码帧）计算，**不得引用为 S5 结论**；作废事实与
> 六项决定性证据见 results/full_threearm_CONVENTION_NOTE.md。正确数值待 C 臂按修正
> Convention 重训+108 格重算后落表（S5 收口判读）。

- 数据集：quickdraw（论文协议全量：首 5000/类×10 类=50k，85/15 seeded split → train 42500 / test 7500；N-MNIST 仍 SSL 墙，结论级基准留后续单元）
- 训练：全量 30 epoch × 6 次（A/B 共享 3 种子 + C-aug 3 种子），逐 epoch checkpoint；臂语义 D1-D3 与 pilot 完全一致（同源代码 import）
- 读表口径：预注册主口径=meanpool（论文口径），三口径 meanpool/gapnb/final 兼报
- 臂：A=库 forward(timespans=None,均匀dt=1)；B=manual-loop+D2 真实 timespans（与 A 共享 checkpoint/掩码）；C=B+gap 指示位+块状增强训练（单独 checkpoint）
- 条件：clean / uniform30(逐时间步 Bernoulli 0.3) / block5-30、block15-30（块长 b 划分、每块 Bernoulli 0.3，期望掩码率 30%；3 固定种子化模式跨臂配对）

| 条件 | A | B | C | B−A(pp) | C−A(pp) |
|---|---|---|---|---|---|
| clean | 9.56±0.00 | 9.56±0.00 | 9.93±0.44 | +0.00 | +0.37 |
| uniform30 | 18.84±2.34 | 17.70±2.31 | 59.36±2.11 | -1.14 | +40.52 |
| block5-30 | 29.74±3.02 | 27.40±3.71 | 68.68±1.49 | -2.34 | +38.93 |
| block15-30 | 36.69±2.81 | 34.34±3.51 | 55.04±1.91 | -2.34 | +18.35 |

## 强制 sanity（S2 入口条件同款）
- clean A≡B：|A−B|=0.000pp → PASS(<0.1pp)
- A@uniform30=18.84% → 方向核对 PASS(z=25.51>2 vs chance)
- A@clean=9.56% → D7 结论级（论文 Table III QuickDraw ≈98.6-98.7%）未达（缺口 -89.04pp）
- 恒定类消失伴生判据：A 臂 clean 三口径={'meanpool': 9.56, 'final': 10.21, 'gapnb': 9.56}，分化=0.65pp → 已分化（非恒定类）
- manual-loop 真实尺寸复验：verify_pass=True，vs 库 B=1 max diff=0.0

## 门线与假设判读（design.md §五；主口径 meanpool）
- H1（block5-30 下 B 或 C ≥+2pp 且该臂 clean 降幅 ≤0.5pp）：B−A=-2.34pp、C−A=+38.93pp；B clean 降幅=+0.00pp、C clean 降幅=+0.37pp → gate_pass_arm=None
- C clean 逐种子降幅（pp）：{'0': 0.77, '1': -0.25, '2': 0.59} → 逐种子门控(全 ≤0.5pp) FAIL
- block5-30 逐种子 C−A（pp）：{'0': 0.42, '1': 0.39, '2': 0.36}
- 三口径兼报（block5-30）：B−A meanpool=-2.34 / gapnb=-0.46 / final=-0.06pp；C−A meanpool=+38.93 / gapnb=+25.80 / final=+0.96pp
- H2（block15 增益 ≥ block5 增益，mean 意义）：Δ=-0.00pp
- 判读：decision=falsified_negative_branch，next_action=redesign

## 限制
- C−A 含增强训练混杂（D3 预注册：门线对 C 为保守存活判据，归因细化=E2 B-train 对照臂，留后续单元）
- QuickDraw L=100（block15 为字面块长）；N-MNIST L=10 场景 block15 退化为整段掩码，结论级须回 N-MNIST 复现
- 计时（U5）：{"data_prep_sec": 1.8, "train_runs": {"seed1_c": 1046.7, "seed2_ab": 1438.7, "seed2_c": 1454.3}, "eval_sec": 167.3, "total_sec": 4111.6}
