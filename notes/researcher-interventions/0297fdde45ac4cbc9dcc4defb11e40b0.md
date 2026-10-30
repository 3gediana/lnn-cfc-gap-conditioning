# S7-e2-btrain-arm 收口判读（researcher 单元 0297fdde45ac4cbc9dcc4defb11e40b0，2026-10-31 03:0x）

## 0. 判读对象与回执定性

- 事件：unit.receipt 0dce44084bad43d8b9fc8ef8e478dcee，logical_stage=S7-e2-btrain-arm，status=failed，notes/artifacts/next_action/next_units 全空，finished_at 2026-10-31T02:56:14+08:00。
- 定性：**failed 空壳=科学交付 PASS、收尾格式失败**（回执缺契约必填字段→驱动器记 failed）。盘上科学产物齐全（mtime 02:04-02:54，commit 45d1286 已入库），本单元首轮全量独立复跑 ALL PASS，勘误为 ok。同型先例：710a1c50（S5 第五单元）、design 8086fe74，第三次。

## 1. 独立复算（不采信回执/MD；首轮全量，符合判读速度纪律）

复算入口：`G:/ai/python11/python.exe experiments/s7_judge_0297_recheck.py`，exit=0 ALL PASS，证据 experiments/s7_judge_0297_recheck.txt。逐项：

1. 结构：e2_btrain.csv 144 数据行、键 (seed,arm,condition,pattern) 唯一、n_eval 全 7500、臂 A/B/C/D、条件 clean/uniform30/block5-30/block15-30。
2. 三种子 mean±std（meanpool，%）：clean A=B=92.30±0.86/C=92.89±0.17/D=92.54±1.02；uniform30 A=63.93±2.86/B=64.37±3.76/C=86.10±0.80/D=84.41±1.15；block5-30 A=71.03±4.10/B=69.81±4.69/C=88.52±0.66/D=86.33±2.35；block15-30 A=72.83±2.80/B=72.03±3.22/C=83.55±1.08/D=80.80±3.16。与 MD/回执逐位一致。
3. 配对差（逐种子=同 seed 3 pattern 配对均值，D4 语义）：block5-30 D−A=+15.31pp（逐种子 +21.85/+9.69/+14.38）、D−C=−2.18pp（−0.57/−5.37/−0.61）、C−A=+17.49pp（与 S5 锚点一致）、B−A=−1.22pp（与 S5 一致）；clean D−A mean+0.24pp（+1.94/−1.92/+0.71）；uniform30 D−A=+20.48/D−C=−1.69；block15-30 D−A=+7.96/D−C=−2.75。与 MD 逐位一致。
4. 预注册判据机械输出（跑前写死、禁事后改）：**双侧逐种子 clean 约定（S5 实现口径 |Δ|≤0.5pp）=③部分归因**（seed0 +1.94pp 超门线）；**单侧字面约定（预注册「clean 降幅≤0.5pp」）=①E2 被反驳**（mean+0.24pp 过门）。两种约定共同结论见下。
5. 对账：A/B/C 与 S5 结论级表 results/full_threearm.csv 108 格逐位比较 mismatches=0（确定性+路径无漂移）；D 行掩码率 block5-30 0.3031/uniform30 0.3014/block15-30 0.2991≈名义 0.30。
6. ckpt 直读第二路径（torch.load）：full_quickdraw_seed{0,1,2}_d.pt 均 epochs_done=30、history 30 连续、opt state 在盘。
7. 三口径兼报（block5-30）：meanpool D−A=+15.31/D−C=−2.18；gapnb D−A=+18.41/D−C=−4.08；final D−A=+0.41/D−C=−0.38（final 口径无增益，与 S5 C 臂 final +0.79pp 同型——meanpool 为预注册主口径，兼报已防口径选择性）。

## 2. 科学判词（E2 归因终判）

- **训练期激活的时间通路（forward_ts + D2 真实 timespans）贡献 C−A(+17.49pp) 增益的 87.5%（D−A/(C−A)=0.8752）；gap 指示位（输入端信息）边际贡献仅 −2.18pp（D−C）。**
- E2 字面主张（timespans 通路训练期未激活→推理期喂变 dt 用不上）在强意义被反驳：同增强训练下，训练期激活通路即可拿到绝大部分增益；gap 位非必需。
- 与 H1 终判（falsified）合成完整叙事：B 臂（推理期才条件化）无增益；D 臂（训练期即激活）≈C 臂——差异不在「推理期有没有时间信息」，在「训练期有没有让时间通路参与学习」。
- caveat 必带：QuickDraw 降级数据集 + D7 保真度缺口（A@clean 92.30% vs 论文 98.6-98.7%）；final 口径 D−A 仅 +0.41pp（读表口径敏感性，meanpool 为预注册主口径）。

## 3. 机器态

- 公开仓（fb-4d1c1b82ec 立项即公开）：github.com/3gediana/lnn-cfc-gap-conditioning（gh 已登录 3gediana，本单元创建并随阶段推送；本地 mirror remote 保留 D:/hermes-data/repos/lnn-4a1c4c0a.git）。

- S7-e2-btrain-arm：ready→**done+result**（receipt 契约字段由本判读补全落盘 workflow.json）。
- S8-nmnist-event-loader / S9-fidelity-gap：维持 ready（depends_on=S5-full-protocol 已 done；workflow 分支自动派，next_units=[]，手写入队会被拒）。
- S6-repo-package：维持 gated（科学线未全收口；公开仓按 fb-4d1c1b82ec 随打包单元建）。
- 唤醒点：S8/S9 回执。

## 4. 复盘（成功也要复盘）

1. **可复用路径**：「failed 空壳三分法」（盘上产物核验→独立复算→勘误定性）第三次零成本生效；判读复算脚本模式（期望值从盘上 CSV 重算而非抄回执）再次兑现。
2. **本单元自身 bug 被抓**：复算脚本首版逐种子配对差误取单格（pattern[0]），与被测 MD 的逐种子数不符→第二轮按 (seed,pattern) 跨臂同模式键修正后 ALL PASS。沉淀=**逐种子配对差必须按同 seed 同 pattern 键跨臂配对（D4 语义），不能取代表格**；独立复算不仅核对手方，也抓自身实现错。
3. 下一个最小同类改进：S8 N-MNIST loader 固化后，D 臂结论回 N-MNIST 复演（H1 原文数据集）是同类「隔离变量臂」模式的直接复用。

## 5. 重复投递复核（2026-10-31T03:2x researcher，第二轮差异/抽样复核）

同一 unit.receipt 事件（0dce44084bad43d8b9fc8ef8e478dcee）二次投递至本判读单元（首轮消费后 inbox 已空、再触发）。按判读速度纪律（2026-10-26：首轮全量复跑拿证据，之后同一阶段按差异/抽样复核即可），本单元只做独立抽样复算+机器态终值核验，不重做首轮全量：

1. 独立抽样复算 experiments/s7_judge_0297_redelivery_check.py exit=0 ALL PASS（证据 experiments/s7_judge_0297_redelivery_check.txt）：144 数据行/键唯一；block5-30 D−A=+15.31pp（逐种子 +21.85/+9.69/+14.38）、D−C=−2.18pp、C−A=+17.49pp、clean D−A=+0.24pp（+1.94/−1.92/+0.71）；ratio 0.8752 与判据双约定复现；A/B/C 与 S5 结论级表 108 格逐位对账 mismatches=0；四条件×四臂 mean 全表 16 格与 §1 逐位一致。首版脚本配对方向写反（D−A 算成 A−D，幅值逐位一致当即暴露），第二轮自身抓出修正——§4.2 同型教训第二次实证（独立复算也核自身）。
2. 机器态终值（research-workflow.verify_stage_status，fb-923d6f83b2 字段终值口径，标记块/commit message 不作数）：S7-e2-btrain-arm=done/closed_by=None、S8-nmnist-event-loader=ready、S9-fidelity-gap=ready、S6-repo-package=gated，四项 ok=true。
3. git/origin：本地 master=origin/master=GitHub ls-remote master=8d9d8a6（fb-4d1c1b82ec 公开推送保持同步，github.com/3gediana/lnn-cfc-gap-conditioning）；夜队列仅剩 S7 陈旧条目 1 条（attempts=1、无 partial 指针、S7 已 done，选择器按 workflow ready 渲染不会重派——驱动器内部事务，不干预）。
4. 审计链补齐：DECISIONS.md 补登 S5 收口判读（73fb33f2，首轮遗漏）+ 本 S7 判读两条。
5. 结论不变：E2 归因终判维持 §2；next=S8/S9 由驱动器派单（S8=N-MNIST loader 固化=H1/H2 原文数据集复演数据前置；S9=D7 归因纯分析无 GPU），唤醒点=S8/S9 回执。
