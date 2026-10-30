# S10-nmnist-threearm-baseline N-MNIST 三臂结论级基准（% acc，3 种子 mean±std，逐种子明细见 CSV）

- 数据集：N-MNIST（论文原文数据集；S8 loader 口径：L=10 每样本跨度等分+log1p，Train 60000 / Test 10000；评测用全量 test n_eval=10000）
- 训练：全量 60000 × 10 epoch × 6 次（A/B 共享 3 种子 + C-aug 3 种子），逐 epoch 原子 ckpt
- 臂：A=库 forward(timespans=None,均匀dt=1)；B=manual-loop+D2 真实 timespans（与 A 共享 checkpoint/掩码）；C=B+gap 指示位+块状增强训练（单独 checkpoint）
- 条件：clean / uniform30(逐时间步 Bernoulli 0.3,EV-06 逐字一致) / block5-30、block15-30（块长 b 划分、每块 Bernoulli 0.3，期望掩码率 30%；3 固定种子化模式跨臂配对）
- 读表口径：预注册主口径=meanpool（论文口径），三口径 meanpool/gapnb/final 兼报

| 条件 | A | B | C | B−A(pp) | C−A(pp) |
|---|---|---|---|---|---|
| clean | 98.12±0.20 | 98.12±0.20 | 98.78±0.04 | +0.00 | +0.67 |
| uniform30 | 90.06±4.26 | 90.13±3.71 | 97.85±0.27 | +0.07 | +7.79 |
| block5-30 | 80.99±4.76 | 81.08±4.47 | 90.45±1.37 | +0.09 | +9.47 |
| block15-30（L=10 退化为整段掩码=已知口径特性，行保留作协议可比） | 71.34±1.83 | 71.34±1.83 | 71.44±1.94 | +0.00 | +0.10 |

## 强制 sanity
- ②clean A≡B：|A−B|=0.000pp → PASS(<0.1pp)
- ⑤A@uniform30=90.06% → 方向核对 PASS(z=266.86>2 vs chance)
- ④D7：A@clean=98.12% vs 论文 Table I N-MNIST LNN 99.38% → 缺口 -1.26pp（兼报 vs Table III 0% 列 98.71%：-0.59pp（缺口≤3pp，未触发 caveat 条款））
- ⑥收敛伴生：A 臂 clean 三口径={'meanpool': 98.12, 'final': 53.04, 'gapnb': 98.12}，分化=45.08pp → 已分化（非恒定类）
- manual-loop 真实尺寸复验：verify_pass=True，vs 库 B=1 max diff=0.0，B>1 崩溃记录=有

## 判据机械输出（跑前冻结；H1 终判交 researcher）
- ①H1 主判据（block5-30，meanpool，3 种子 mean）：B−A=+0.09pp（逐种子 {'0': 0.53, '1': 0.04, '2': -0.29}）、clean B−A=+0.00pp（逐种子 {'0': 0.0, '1': 0.0, '2': 0.0}）→ **H1_verdict=falsified**
- ③C 臂保守门（D3）：C−A=+9.47pp（逐种子 {'0': 16.38, '1': 6.79, '2': 5.23}）、C clean 降幅=+0.67pp（逐种子 {'0': 0.95, '1': 0.43, '2': 0.62}）→ C_gate_pass=False
- 三口径兼报（block5-30）：B−A meanpool=+0.09 / gapnb=+0.10 / final=-0.05pp；C−A meanpool=+9.47 / gapnb=+6.05 / final=+24.96pp
- H2（block15 增益 ≥ block5 增益）：Δ=-0.09pp（H2 已由 S5 在 QuickDraw 结论级驳倒且 L=10 下 block15 退化不可检验，本阶段不 adjudicate，仅协议可比记录）
- decision=falsified_negative_branch，next_action=redesign

## 协议常数与 caveat（子步1 取证，双记）
- epoch：10ep（论文 run_lln_nmnist.sh --epochs 10 + lln_nmnist_10.log 10 行 + Table I 0.9938 三源一致；Table V 记 30ep=论文内部矛盾，双记）
- 论文架构：units128/CfC(4096,128,proj128)/双CNN+BN/batch64/no-wd/no-clip/Cosine
- 本仓冻结规格：units256/CfC(128,256,proj256,backbone_layers=1,backbone_units=128)/单CNN+LN+ReLU/batch128/wd0.01/clip1.0/AdamW lr0.001 恒定
- 协议差 caveat：batch/wd/clip/units/架构/lr-schedule 与论文 Table V/代码默认值的差异全部记入；不改冻结规格与判据（H1 主判据 B−A 为同 ckpt 推理期配对不受影响）；D7 缺口>3pp 归因第一嫌疑=协议差，禁实现缺陷归因
- 评测集：全量 test 10000（QuickDraw S5 为 7500 子集，差异入报告）

## 限制
- C−A 含增强训练混杂（D3 预注册：门线对 C 为保守存活判据；E2 已由 S7 在 QuickDraw 结论级解答：训练期激活时间通路贡献 C−A 增益 87.5%，N-MNIST 不重开 D 臂除非 B−A 转正）
- block15-30 在 L=10 退化为整段掩码（每样本 30% 概率全掩码），为已知口径特性非 bug，行保留作协议可比
- 计时（U5）：{"data_prep_sec": null, "data_prep_note": "report 模式未重载数据；原始 all-run 的 data_prep 曾误标为总耗时（键名 bug，本轮修正），此处诚实留空", "train_runs": {"seed0_ab": 79.0, "seed0_c": 108.7, "seed1_ab": 105.2, "seed1_c": 107.9, "seed2_ab": 104.8, "seed2_c": 108.8}, "eval_sec": 64.3, "total_sec": 686.1, "regenerated_from": "results/nmnist_progress.json"}
