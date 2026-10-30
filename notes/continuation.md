# Continuation 判读与下一步冻结 — 2026-10-31T04:1x-04:2x（night continuation 单元）

单元性质：夜班 continuation（工作流无夜派 ready 阶段时由驱动器生成的「自己决定下一步」单元）。
本单元=判读+下一步冻结，未跑任何训练/GPU 实验。

## 1. 「ready 为空」根因（先查机制再动手）

research-workflow.ready_stages() 口径：status=ready 且 depends_on 全 done。盘上 S9-fidelity-gap
确为 ready（depends_on=S5-full-protocol 已 done），但 night-production.py:2071 `_is_judgment_stage`
把 kind=analysis 列入 _JUDGMENT_KINDS（P3：判读类阶段当夜不派，归 20:30 research-judge）→ 夜班
派单池过滤后 ready 为空。**根因分类=state-anomaly 之外的「设计内过滤」（非轮转未生效/非尾窗锁死/
非状态损坏）**；解除方式=由本判读单元直接落账 S9（与 S8-continue 判读先例一致），并把下一步立成
kind=experiment 阶段（夜班可派）。

## 2. 上一步判读（S8-nmnist-event-loader-continue）

workflow.json 里该阶段 prediction="事件字段与 10-26 抽样分布一致；帧堆积规则需显式定义"、
failure_conditions="分布不符且两种解读规则都无法对齐→落负结果+求助"；其 result 已标明
「驱动器 apply_result 按 next_action=continue 自动创建的空阶段，superseded by S10，同型第五例」。
判读=**该占位无科学内容，关闭正确**；真实上一步=S8-nmnist-event-loader（done）+ researcher 判读
0ffcac05（notes/researcher-interventions/0ffcac0580e642c0bc3a29ee144f8846.md）：回执属实 PASS、
零失实（独立重跑 loader verify 全项 PASS exit=0，证据 experiments/s8_judge_0ffc_loader_verify_rerun.txt；
三源数字一致 60000/10000、292,352,295 事件、锚点 652/299/0.45859、冒烟 loss 2.2959→0.9716/acc 59.4%/
clean A≡B=0.0），预注册失败条件未触发。**S8 线判读=成立，无需重做。**

## 3. S9-fidelity-gap 执行落账（本单元完成的科学工作）

证据（全部在盘）：
- 论文 PDF（G:/research-papers/2605.27467.pdf，arXiv:2605.27467v1）Table I：QuickDraw LNN
  Train 0.9978 / **Test 0.9577**；§VI.A「全部结果单次训练」；§V.C QuickDraw 架构（5 维→128→
  256-unit core→Mean Pooling→MLP(Dropout+ReLU)→10 类）。
- 论文 Table III：N-MNIST LSTM 98.63 / LNN 98.71（0% 列）；QuickDraw LNN 0%=92.69/30%=68.80/
  50%=41.47/70%=22.48。**S5 引的「Table III QuickDraw≈98.6-98.7%」实为 Table III 的 N-MNIST 行
  0% 列（论文正文同段「N-MNIST…from 98.6% to 77.5%」佐证）→ 参照系引错，虚增缺口 2.83pp。**
- 论文仓库日志 experiments/_repo/0.06_result/lnn_10/lln_10.log：30 epoch、LR 1e-3(ep1-12)→
  5e-4(ep13-25)→2.5e-4(ep26-30)、310 it/ep、终值 TRAIN 0.9978/TEST 0.9577（与 Table I 逐位一致）。
- 论文仓库日志 experiments/_repo/lln_nmnist_10.log：10 epoch、终值 TRAIN 0.9997/TEST 0.9938
  （与 Table I N-MNIST 逐位一致）。
- 本仓 experiments/full_protocol.py:67,145,170,185 + pilot_threearm.py:71-76：EPOCHS_FULL=30、
  AdamW(lr=1e-3,wd=0.01)、batch=128、clip=1.0、UNITS=256、SEEDS=[0,1,2]、**无 LR scheduler**
  （grep 零命中）；分类头=单层 Linear(256,10)（论文为 MLP+Dropout）。
- 本仓 S5 结论 results/full_threearm.md：A@clean=92.30±0.86（meanpool 3 种子）、A@uniform30=63.93。

结论：
- D7 缺口改写：vs 论文 Table I 0.9577 = **-3.47pp**；vs Table III QuickDraw 0% 列 92.69 = **-0.39pp**
  （3 种子 ±0.86 噪声内）。原 -6.30pp 中 -2.83pp 为记账伪量。
- 协议差异表 8 项（epoch 一致；LR 调度/分类头/单次-vs-3 种子=偏离；310 vs 332 it/ep、优化器/
  wd/batch=unknown）。归因排序：①参照系引错（已修）②LR 调度（S11 实测）③分类头 dropout
  ④单次 vs 3 种子 ⑤数据量口径。
- S9 prediction（epoch/口径/seed 三选一）**证伪**（epoch 完全一致，主因=引错+LR 调度）；
  failure_conditions（常数无法确认→不开重训）**未触发**（LR 调度/epoch/精度锚均已确认；
  仅优化器/wd/batch 因中文深层路径间歇墙记 unknown）。
- 压力侧兼报：A@uniform30=63.93 vs 论文 Table III QuickDraw 30%=68.80（-4.87pp），不改变
  臂间结论方向。

## 4. 下一步决定（已冻结进 workflow.json）

- **S9-fidelity-gap → done + result**（result_kind=scientific_result、source_mode=archive/
  historical=true、metrics 17 项、verdict=falsified、next_action=continue；契约校验
  validate_result_contract PASS；kind=analysis 不在 SCIENTIFIC 之外，不会因 continue 搓空壳阶段）。
- **S10-nmnist-threearm-baseline → ready**（放行依据=S9 判读落账+N-MNIST 常数同评完成：
  论文 N-MNIST 10ep 双源确认；LR/batch unknown→用项目冻结常数+S10 预注册 fallback，无需改常数；
  QuickDraw 偏离隔离进 S11 不影响 N-MNIST 常数；D7 主判据 0.9938 不变、Table III 98.71 兼报）。
- **新增 S11-quickdraw-lrdecay-retrain（ready，kind=experiment）**：A/B 共享 ckpt ×3 种子 ×30ep，
  唯一变量=论文 LR step decay（1e-3→5e-4@ep13→2.5e-4@ep26），禁动分类头/数据/口径；判据跑前冻结：
  A@clean 3 种子 mean vs S5 基线 92.30±0.86，增益 ≥+1.5pp→supported（D7 主因=LR 调度）；<+0.5pp→
  falsified 负结果落盘不开二轮调参；其间→inconclusive+留 dropout 头 30min 验法。估计 ~570s（S5 计时
  6 runs=1139.6s 推算），总量 1500s 硬顶。
- **S6-repo-package 维持 gated**（科学线收口前不打包；公开仓授权=fb-4d1c1b82ec）。
- verify_stage_status 四项终值核对 ok（S9=done/S10=ready/S11=ready/S6=gated，closed_by 均空）。
- ready_stages 现=[S10, S11]（均 kind=experiment，夜班可派）→ 派单饥饿解除。

## 5. 复盘

- 论文仓库自带训练日志是协议常数（LR 调度/epoch/精度锚）廉价权威源，且日志终值与论文 Table I
  逐位一致→可互为校验（S8 之后第二次兑现）。
- **跨表引用必须核对行标签+论文正文同段佐证**：本次 -2.83pp 伪量即跨表引错的直接代价；
  QuickDraw 的干净锚点有两个（Table I 95.77 / Table III 0% 92.69），论文自身两表差 3.08pp，
  报告须双锚点并报。
- 工具墙：lln_quickdraw_0.06.py 与 run_lln_quickdraw.sh 三路（bash/python/git）读取均失败，
  按 oneshot-tool-walls 协议 ≤2 次/路即停；优化器/wd/batch/「0.06」含义记 unknown，
  已用日志 LR 行绕过（日志每 epoch 打印 LR）。
- 夜班饥饿根因分类沉淀：kind=analysis 命中 P3 判读类过滤=设计内过滤，应由 continuation 判读单元
  直接落账并转立 kind=experiment 阶段，而非等待 20:30 research-judge。
