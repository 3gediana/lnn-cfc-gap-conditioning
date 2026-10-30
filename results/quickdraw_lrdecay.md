# S11-quickdraw-lrdecay-retrain：QuickDraw LR step decay 重训结果（% acc，3 种子 mean±std，逐种子明细见 CSV）

- 阶段动机（S9 归因）：D7 缺口真实锚点=论文 Table I QuickDraw LNN 0.9577（-3.47pp）/Table III 0% 列 92.69（-0.39pp）；候选主因=LR 调度偏离（论文 step decay vs 本仓恒定 1e-3，估计 -1~-3pp）。本阶段唯一变量=LR 调度，其余协议与 S5 逐项一致（import-not-copy）。
- LR 调度：paper step decay: 1e-3(ep1-12) -> 5e-4(ep13-25) -> 2.5e-4(ep26-30) (lln_10.log; S9 judge re-extract 12x1e-3/13x5e-4/5x2.5e-4=30ep)
- 数据/模型/优化器：全量 50k（85/15 seeded split→train 42500/test 7500，SPLIT_SEED=12345）、DrawingClassifier(quickdraw)、AdamW lr_base=1e-3/wd0.01/batch128/clip1.0、30ep、meanpool 主口径三口径兼报；A/B 共享 ckpt（D1），B=manual-loop+D2 真实 timespans
- 条件：clean / uniform30(逐时间步 Bernoulli 0.3) / block5-30、block15-30（块长 b 划分、每块 Bernoulli 0.3；3 固定种子化模式跨臂同掩码配对）；评测全量 test 7500

| 条件 | A | B | B−A(pp) |
|---|---|---|---|
| clean | 93.20±0.09 | 93.20±0.09 | +0.00 |
| uniform30 | 64.81±2.48 | 65.09±3.39 | +0.28 |
| block5-30 | 73.36±2.20 | 71.87±3.00 | -1.49 |
| block15-30 | 75.47±2.15 | 73.93±2.28 | -1.55 |

## 强制 sanity
- clean A≡B：|A−B|=0.000pp → PASS(<0.1pp)
- A@uniform30=64.81% → 方向核对 PASS(z=158.23>2 vs chance)
- 恒定类消失伴生判据：A 臂 clean 三口径={'meanpool': 93.2, 'final': 10.22, 'gapnb': 93.2}，分化=82.99pp

## 判据机械输出（跑前冻结；主口径 meanpool）
- 判据① A@clean(3 种子 mean)=93.20±0.09% vs S5 恒定 LR 基线 92.30±0.86 → 增益 +0.90pp → **criterion1=inconclusive**（+0.5~+1.5pp：inconclusive，留 dropout 头/数据量 30min 验法选项）
- 逐种子 A@clean vs S5 基线配对（pp）：{'0': 1.99, '1': 0.2, '2': 0.52}（S5 逐种子 {'0': 0.9109, '1': 0.9304, '2': 0.9277}）
- 判据② clean A≡B<0.1pp：PASS
- 判据③ A@uniform30=64.81% 兼报 vs 论文 Table III QuickDraw 30%=68.80 → 缺口 -3.99pp
- D7 缺口（本阶段后）：vs Table I 0.9577 = -2.57pp；vs Table III 0% 列 92.69 = +0.51pp
- block5-30 B−A=-1.49pp（兼报；本阶段不做臂间新判据（F1 同款不适用）；B−A 为 LR 变更后复演值兼报，H1 结论级判定以 S5/S10 为准不变）

## 限制
- 论文单次训练/配置 vs 本仓 3 种子 mean（±0.86pp 量级，非系统性）；论文每 epoch 步数310 vs 本仓 ~332（it-ep 口径 unknown，脚本墙未确认）
- 分类头差异仍在（论文 MLP+Dropout vs 本仓单 Linear；本阶段禁改分类头，Dropout 留待判据①后由 researcher 定 30min 验法）
- 计时（U5）：{"data_prep_sec": 0.0, "train_runs": {"seed0_ab": 1225.4, "seed1_ab": 1165.9, "seed2_ab": 1175.0}, "eval_sec": 76.4, "total_sec": 3644.9}
