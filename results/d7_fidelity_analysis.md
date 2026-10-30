# S9-fidelity-gap：QuickDraw D7 保真度缺口归因（2026-10-31 判读单元，纯分析无 GPU）

阶段：S9-fidelity-gap（kind=analysis，depends_on=S5-full-protocol）｜执行=本 continuation 判读单元
（夜班 P3 规则 kind=analysis 不派单，故由 researcher 判读单元直接落账；与 S8-continue 判读先例一致）

## 0. 结论一句话

S5 的「D7 缺口 -6.30pp」中 **-2.83pp 是参照系引错**（把论文 Table III 里 **N-MNIST** 的 0% 列
98.63/98.71 误当作 QuickDraw 数字）；按论文正确口径重算，真实缺口 =
**vs 论文 Table I QuickDraw LNN Test 0.9577 → -3.47pp**；**vs 论文 Table III QuickDraw LNN 0% 列 92.69 → -0.39pp**
（3 种子 ±0.86 噪声内）。剩余缺口有明确协议偏离候选（LR 调度/分类头/单次训练），
按阶段预注册决策规则立 S11-quickdraw-lrdecay-retrain（复现成本 ~10min GPU <2h）。

## 1. 证据源（全部在盘，可复现）

| 证据 | 路径 | 关键内容 |
|---|---|---|
| 论文 PDF 全文 | G:/research-papers/2605.27467.pdf（arXiv:2605.27467v1） | Table I：QuickDraw LNN Train 0.9978 / **Test 0.9577**；§V.C QuickDraw 架构；§VI.A「全部结果单次训练」 |
| 论文 Table III | 同上（§VI.C） | N-MNIST LSTM 98.63 / LNN 98.71（0% 列）；QuickDraw LNN 0%=92.69 / 30%=68.80 / 50%=41.47 / 70%=22.48 |
| 论文自带 QuickDraw 训练日志 | experiments/_repo/0.06_result/lnn_10/lnn_10.log（+_full.log） | **30 epoch**；LR 打印：1e-3(ep1-12)→5e-4(ep13-25)→2.5e-4(ep26-30)；310 it/ep；终值 TRAIN 0.9978 / TEST 0.9577（与 Table I 逐位一致） |
| 论文自带 N-MNIST 训练日志 | experiments/_repo/lln_nmnist_10.log | 10 epoch；终值 TRAIN 0.9997 / TEST 0.9938（与 Table I N-MNIST 逐位一致） |
| 本仓 S5 结论 | results/full_threearm.md（+full_threearm.csv） | A@clean=92.30±0.86（meanpool 主口径，3 种子）；A@uniform30=63.93±2.86 |
| 本仓训练配置 | experiments/full_protocol.py:67,145,170,185 + experiments/pilot_threearm.py:71-76 | EPOCHS_FULL=30；AdamW(lr=P.LR=1e-3, wd=0.01)；batch=128；clip=1.0；UNITS=256；SEEDS=[0,1,2]；**无任何 LR scheduler**（grep scheduler=0 命中） |

取证路径注记：experiments/_repo/lln_quickdraw_0.06.py 与 run_lln_quickdraw.sh 遇中文深层路径
间歇墙（bash/python/git 三路均失败，按 oneshot-tool-walls 协议未反复重试）→ 论文 QuickDraw 的
优化器/weight_decay/batch/「0.06」含义记 **unknown**；但 LR 调度与 epoch 数已由日志直接坐实
（日志每 epoch 打印 LR），不影响本条归因主结论。

## 2. 协议差异表（本仓 vs 论文，逐项带证据）

| # | 项 | 论文 | 本仓 | 判定 |
|---|---|---|---|---|
| 1 | epoch 数 | 30（lln_10.log 逐 epoch 至 30） | 30（full_protocol.py:67 EPOCHS_FULL=30） | **一致**（S9 预测候选之一被排除） |
| 2 | LR 调度 | **step decay：1e-3→5e-4@ep13→2.5e-4@ep26**（lln_10.log 每 epoch LR 行） | **恒定 1e-3，无 scheduler**（full_protocol.py:145 单 AdamW；grep 无 scheduler/lr step） | **明确偏离 #1** |
| 3 | 分类头 | Mean Pooling 后 MLP（Dropout+ReLU）→10 类（论文 §V.C） | 单层 Linear(256,10)（pilot_threearm.py DrawingClassifier.classifier） | **明确偏离 #2**（正则差） |
| 4 | 训练次数 | 单次训练/配置（论文 §VI.A 原文） | 3 种子 mean±std（pilot_threearm.py:71） | 偏离 #3（对 mean 比较影响 ~±1pp 量级） |
| 5 | 每 epoch 步数 | 310 it/ep（lln_10_full.log tqdm 行） | 42500/128≈332 it/ep | **待核**（若 batch 相同则论文每 epoch 少 ~6.6% 数据；脚本墙未确认） |
| 6 | 数据切分/特征 | 10 类子集；stroke x,y+pen state 共 5 维（§II.G/§V.C） | 首 5000/类×10 类，5 特征(nx,ny,ndx,ndy,p)，max_len=100，85/15 seeded split（pilot_threearm.py:9,94-97） | 一致（EV 既有核验） |
| 7 | core/读表 | 5→Linear+LN+ReLU→128；256-unit core；Mean Pooling（§V.C） | Linear(5,128)+LN+ReLU；CfC(128,256,proj256)；meanpool 主口径 | 一致 |
| 8 | 优化器/wd/batch | unknown（脚本墙；日志不打印） | AdamW/wd0.01/batch128 | unknown（论文侧） |

## 3. 缺口归因排序（每条带证据与可证伪下一步）

1. **参照系引错（-2.83pp，纯记账修复，无需实验）**：S5 引的「Table III QuickDraw≈98.6-98.7%」
   实为 Table III **N-MNIST** 行 0% 列（LSTM 98.63 / LNN 98.71；论文正文同段「N-MNIST…drops
   sharply from 98.6% to 77.5%」佐证）。QuickDraw 正确锚点：Table I LNN Test **0.9577**（=仓库日志
   ep30 TEST 0.9577，双源一致）；论文 Table III QuickDraw 0% 列 92.69 亦在盘。
   验法=已验（PDF+日志双源）。→ D7 缺口改写为 -3.47pp（vs Table I）/ -0.39pp（vs Table III 0%）。
2. **LR 调度偏离（估计 -1～-3pp，S11 实验判定）**：论文 30ep 内两次 LR 减半，日志显示 5e-4/2.5e-4
   段 TEST 在 0.948-0.959 区间震荡后收敛到 0.9577；本仓恒定 1e-3 收尾。可证伪下一步=S11 同代码
   仅加调度重跑 A/B 3 种子：若 A@clean 向 95.77 回归 ≥1.5pp → 缺口主因=LR 调度，QuickDraw 结论级
   基准按新协议更新；否则记 caveat。
3. **分类头 Dropout 缺失（幅值 unknown，与 #2 同实验附带观测）**：论文 MLP+Dropout vs 本仓单 Linear；
   论文 dropout 率 unknown。S11 不改架构（隔离变量），仅在报告记 unknown；如 S11 后缺口仍 >2pp 且
   分类头差异可疑→另立 30min 验法（读论文脚本/试 0.1-0.5 dropout 单种子）。
4. **单次训练 vs 3 种子 mean（±0.86pp 量级，非系统性）**：论文单次（§VI.A），本仓 3 种子
   mean±std=92.30±0.86；论文单跑本身可能偏高 1-2pp。不可复现（论文未给 seed），记 caveat。
5. **每 epoch 步数 310 vs ~332（≤6.6% 数据量口径，unknown）**：脚本墙未确认论文 batch；
   若 batch=128 则论文每 epoch 少 2176 样本。记 unknown，不单独开实验。

## 4. 对既有结论的影响（不重做，只改参照系）

- **H1 门线结论不动**：B−A/C−A 均为臂间配对比较（同协议同 ckpt），clean 绝对水位不影响
  falsified_negative_branch 判定（S5 verdict）。
- **压力下保真度新数据点**：A@uniform30=63.93 vs 论文 Table III QuickDraw LNN 30%=68.80（-4.87pp），
  与 clean 侧 -0.39pp（vs 同表 0% 列）方向一致→缺口在掩码下略放大，量级仍在 seed 噪声+协议差内，
  不改变「C 臂抗丢帧、B 臂无增益」的结论方向。
- **N-MNIST（S10）参照系复核**：论文 Table I N-MNIST LNN Test 0.9938 = 仓库 lln_nmnist_10.log
  终值 0.9938（双源一致）→ S10 的 D7 目标 0.9938 不变；论文 Table III N-MNIST 0% 列 98.71 与
  Table I 不一致（论文内部口径差），S10 以 0.9938 为主并兼报 98.71 口径。
- S9 prediction（「缺口最可能来自 epoch 数/读表口径/seed 平均方式之一」）**被证伪**：
  epoch 完全一致；主因是参照系引错+LR 调度，不是原三项。
  failure_conditions（协议常数无法确认→记 unknown 不开重训）**未触发**：LR 调度/epoch/精度锚
  均已从论文仓库日志+PDF 确认；仅优化器/wd/batch 记 unknown。

## 5. 决策（按 S9 预注册规则）

发现明确协议偏离（LR 调度，#2 表）且复现成本 <2h（S5 计时：6 runs=1139.6s，A/B 3 runs≈570s）
→ **立 S11-quickdraw-lrdecay-retrain（ready，kind=experiment 夜班可派）**；A−B 臂间对比内部
有效性已成立，QuickDraw 重训只更新 D7 保真度记账，不改 H1 结论。
S10-nmnist-threearm-baseline 的 N-MNIST 常数同评结果：论文 N-MNIST=10ep（日志+Table I 双源）、
LR/batch unknown（脚本墙）→ 用项目冻结常数（AdamW 1e-3/wd0.01/clip1.0/batch128）+记 unknown，
与 S10 预注册 fallback 一致，**无需改常数**；按放行条件 S10 → ready。

## 6. 复现入口

- 论文 PDF 表格：G:/research-papers/2605.27467.pdf §VI Table I/III（fitz 提取全文见下）
- 论文日志：experiments/_repo/0.06_result/lnn_10/lln_10.log、experiments/_repo/lln_nmnist_10.log
- 本仓配置：experiments/full_protocol.py:67,145,170,185、experiments/pilot_threearm.py:71-76
- 结构化指标：results/d7_fidelity_analysis.json
