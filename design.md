# 设计冻结 — 液态网络抗丢帧没接时间：CfC基准补真实间隙条件化

- 单元：unit.design（research-planner profile，夜间生产监督试点，仅本地落盘）
- 时间：2026-10-25T02:3x+08:00
- 状态：novelty/fit gate 已过（admission.json decision=admitted）；本文件冻结可证伪假设、竞争解释、判决性实验与停止条件。机器可读版见 workflow.json。
- 输入基线：admission.json（schema research-topic-admission/v1）、literature/related-work.md（EV-01..EV-12、Q1..Q7）、dossier `research/_state/candidate-lnn-gap-cfc-20261025.json`、research/taste.md、research-approval.json（auto:cand-4a1c4c0adbd71b47）。
- 本单元边界：不训练、不跑 benchmark、不建仓、不公开推送。

## 一、开工复核结论（四项输入逐项过）

### 1.1 admission.json — 复核通过
- 结构：schema=v1，decision=admitted、screening_attempts=1、passed；claims C1–C5 每条可解析到 EV 引用；novelty_checks 六键全真；user_fit_evidence 三条（direct_user_preference / taste_document / active_project）。
- 遗留不确定项与交接一致：U2（ncps 0.0.7/1.0.1 timespans 行为未实测）、U3（向前引文）、U4（2510.07578/NIALIM 仅快照级）、U5（全量耗时）。
- first_milestone（status=accepted）三条件 ①②③ 与过门线可直接操作化（见 §四/§五）。

### 1.2 related-work 矩阵 — 复核通过
- 两条 closest_work 全文级（2605.27467 五条全文证据 EV-01/02/03/04/05 + 代码逐行 EV-06；2106.13898 全文 EV-08）；相邻范式（Neural CDE EV-09、NIALIM EV-10、综述 2510.07578 EV-07、GRU-D/mTAND/Latent-ODE 簇 Q3）均有定位与不占坑理由。
- 关键锁定（A 臂忠实性依据）：EV-06——`mask = (torch.rand(x.size(0), x.size(1), 1) > dr).float(); x = x * mask`（逐时间步 Bernoulli 均匀随机、整帧置零、无块状、无重索引）；`out, _ = self.core(x)` 未传 timespans；掩码只在 eval 循环内施加；N-MNIST=10 bin log1p；QuickDraw=10 类、每类 5000、max_len=100。

### 1.3 用户品味依据 — 复核通过
- taste.md [correction] 2026-10-24 选题口径（22:09/22:16 原话）：候选=别人论文里一个具体缺口上的小改进、产物=能放 GitHub 的独立小仓库、单卡 8G、1-2 周、pilot 30 分钟见数、禁大主题拼接——本课题逐项命中（单缺口、单改动、单判据、模块级）。
- 拒稿死法对照：清单#2（novelty 定位：两条 closest_work 全文+差异段）；#5（消融每臂只换一组件，见 §四臂设计）；#6（统计兜底：3 种子 ±std 预注册，直补被改进对象单次训练缺口 EV-03）；E9z9jhSjB5 死法②（相邻范式已查：不规则时序主线+近似精度线+2026 新邻 MR-MoE，见 §1.5）；声称收缩（贡献限定「该公开基准的协议修正+机制归因」，不泛化「液态网络普遍抗块状丢帧」）。
- 玩具红线：真实模型（ncps CfC）+真实公开 benchmark（N-MNIST/QuickDraw）+论文开源协议；pilot 数据只作内部看方向、结论级必须全量+多种子+±std（admission toy_only_risk 缓解条款原样继承）。

### 1.4 真 benchmark 入口 — 复核通过（含通道注记）
- 代码入口：github.com/ye-kyaw-thu/LNN-vs-LSTM `stress_test.py`（EV-06 逐行核验，2026-10-25 screening 期经 raw.githubusercontent 全文抓取）。
- 数据入口：仓库自带 download_nmnist.py / quickdraw ndjson；协议常数已从源码锁定（§1.2）。
- 模型栈：ncps（论文 0.0.7；本机 G:/ai/python11 为 1.0.1，`ncps/torch/cfc.py` L112 `forward(input, hx=None, timespans=None)` 源码核验，dossier 记录）。
- 通道注记：本单元尝试重抓 stress_test.py 复验，web_extract 后端 SSL EOF（与 EV-11 同一堵墙，oneshot-tool-walls.md 协议不再重试）；EV-06 的逐行核验记录仍为权威依据。arxiv.org 域同样受阻。

### 1.5 本单元新增核验（U3 升级、U4 收窄）
- U3（向前引文）——由 unknown 升级为「三通道实查 0 条」：①screening 期搜索引擎 Q4（0 条可核验引用）；②本单元 S2 API `citations(ARXIV:2605.27467, dir=in)` ok=true count=0（02:22:44）；③本单元 OpenAlex API `citations(DOI:10.48550/arXiv.2605.27467, dir=in)` ok=true count=0（02:26:22）。保留 caveat：论文 2026-05 挂出、引用窗口短，「0 条」不得写成「无人跟进」（EV-11 原则）；S2 paper 详情查询被共享池限流（429），S2 收录状态未单独确认——已如实记录。
- U4（两近邻全文扫）——收窄未关闭：arxiv HTML 2510.07578 §V-B 原文段落经搜索通道直接引得：「invariance-inducing objectives that maintain performance under sensor noise, missing data, or regime changes」——missing data 明确在 future work 段，比 screening 期的快照级证据强一档；另捞到 2026 相邻工作 MR-MoE（arXiv:2606.12240）对缺失值用 forward filling——旁证「LNN 线至今没人接原生时间条件化」。NIALIM 仍为摘要级（TNNLS 付费墙）。残余风险与触发器保留（§六 F4）。

## 二、可证伪假设（冻结）

### H1 主假设
- 陈述：在 2605.27467 协议的 N-MNIST（10 bin log1p、CNN-128+CfC-128、ncps）上，推理期 30% 块状间隙（块长 5 帧）条件下，把真实经过时间喂给 CfC 原生 timespans 接口（B 臂），相对论文式处理（A 臂：同掩码置零、时间按均匀网格）能提升 test 准确率 ≥2pp，且干净数据上几乎无代价。
- 立论依据：CfC 闭式解时间显式进入动力学（EV-08）；被改进对象的压测恰好从不把时间告诉模型（C2：EV-02+EV-06 双重核验）；块状间隙下「间隙宽度」是均匀随机丢帧里不存在的真实信息量；该信息只能经 timespans 进入（其代码从未传，EV-06）。
- 可测量预测：B−A（test acc，block5-30）≥ +2pp（3 训练种子 mean，报 ±std）；B 在 clean 上与 A 差 ≤0.5pp。
- 失败条件（预注册，命中即按 §六 转向，不硬撑）：B−A < +1pp 且 clean 不受损 → H1 在 pilot 层面证伪（负结果落盘，转多种子复现文档单元，dossier 转向路径①）。

### H2 次假设（机制梯度）
- 陈述：真实时间条件化的收益随块长增大而增大（block15 > block5 的 B−A 增益，mean 意义单调）。
- 立论依据：间隙越长，均匀网格假设失真越大，真实 Δt 携带的信息增量越大。
- 失败条件：block15 增益 ≤ block5 增益 → 次判据不成立（不单独杀方向，但收窄机制解释：收益若存在，更可能来自「有洞」的粗粒度感知而非精确时长）。

## 三、竞争解释与区分实验（每条预注册区分法）

| # | 竞争解释 | 若真则看到 | 区分实验 |
|---|---|---|---|
| E1 | 零填充隐式插值解释：LNN 抗性主要来自零帧的隐式平滑，与时间通路无关 | B≈A（<1pp） | 即 H1 主对照本身；若 E1 真则负结果修正社区叙事（预注册价值成立） |
| E2 | 训练-推理失配解释：timespans 通路训练期从未被激活（干净数据 dt 恒定），推理期喂变 dt 用不上 | B 不稳定或小幅为负；B-train 变体（训练期也过 timespans 路径/训练期注入合成间隙）显著更好 | S5 阶段加 B-train 对照臂（每种子+1 次训练）；pilot 不做，失败归因时再做 |
| E3 | 结构效应解释：收益（若有）来自块状比均匀更易/更难，而非时间信息 | A 在 block 条件与 uniform30 条件差异巨大，且 B−A 的增量与之相关 | 评测矩阵含 A@uniform30（论文原语义 anchor）与 A@block 的同臂对照（推理期免费） |
| E4 | 实现伪影解释：timespans 语义/尺度/版本行为与预期不符（U2） | clean 下 A 与 B 出现非零差异；或 dt=0/大 dt 出现 NaN、状态漂移 | S0 最小前向探针四断言（§四 S0）；clean 下 A≡B 数值一致性是 S2 评测的强制 sanity 项 |

## 四、判决性实验（pilot，首里程碑）— 三步 S0/S1/S2

### 4.0 对预注册臂语义的可操作化修正（需首里程碑判读时 researcher 过目）
- D1（A/B 共享训练产物）：每种子只训练一次（论文协议：干净数据训练、压测仅推理期，EV-06 ⑤）。A 与 B 用同一 checkpoint、同一掩码后的输入张量，唯一差异=timespans 向量（A=None/全 1，B=真实）。这是「每臂只换一组件」的最强形式：两臂输入逐元素相同。省一半算力，纯化机制归因。
- D2（B 臂「真实 timespans」语义）：保持零填充表示（与预注册字面一致）：被掩码帧的 timespans=0（不推进时间），间隙后首个真实帧的 timespans=间隙帧数+1（真实经过时间一次性入账）。信息上等价于「紧缩重索引+真实 Δt」（dossier A 臂描述里已出现的合法表示），但保序保长、与 A 共享输入张量。回退：若 S0 探针发现 ncps 对 dt=0 行为退化（状态被推进/NaN），改用紧缩重索引实现（数学等价，S0 断言裁决）。
- D3（C 臂训练协议显式化）：C=B+可学习 gap 指示位（每步标量 1[帧被掩码]，拼接进 CfC 输入特征，输入维 +1）。指示位在纯干净数据上无梯度（恒 0），结构上不可学习——故 C 采用块状间隙增强训练（训练序列注入合成块状间隙、指示位=1、真实 timespans）。此选择使 C−A 含「增强训练」混杂；预注册门线「B 或 C ≥2pp」对 C 而言是保守的方向存活判据（连增强都救不回则方向死），归因细化（指示位 vs 增强本身）延后到 S5 加 B-aug 对照。C 单独训练（每种子 1 次）。
- D4（评测矩阵，推理期施加、训练后全部免费）：gaps={clean, uniform30（论文原语义，anchor）, block5-30, block15-30}；臂={A, B} 共享 3 种子 checkpoint + C-aug 3 种子。块模式=固定 3 种块位置模式（种子化），跨臂复用同一掩码（配对比较）；uniform30 逐时间步 Bernoulli 0.3 与 EV-06 逐字一致。
- D5（统计）：种子={0,1,2} 固定表；报告 mean±std；所有差值报逐种子配对明细。过门线按 mean 判，std 报告不省略（拒稿清单#6）。
- D6（预算/断点）：S0≈5 分钟；S1=6 次训练（1 万样本子集、1-2 epoch、8G 单卡）预计 20–25 分钟——按 ≤35 分钟粒度切单元：S0+S1(种子0) 一个单元打通全链，S1 余下种子+S2 下一单元；每次训练完成即写 checkpoint（experiments/ckpt/ + results/pilot_progress.json）。
- D7（A 臂忠实性判据的预算内操作化）：预注册要求干净基线达 Table I 数量级（N-MNIST ~99%），与「1 万样本 1-2 epoch」预算存在张力。操作化：pilot 层面 A 臂 clean test acc ≥97%（Table I −2pp）即视为忠实性初步成立；~99% 严格复现归 S5 结论级强制。pilot 达不到 ≥97% 时先查实现（epoch/数据量/预处理），按断点规则续跑，不算方向失败。

### S0 — U2 关闭（ncps timespans 行为探针）
- 产物：experiments/u2_timespans_probe.py + results/u2_probe.json。
- 四断言：①`forward(x, timespans=None)` 与 `timespans=全1` 输出关系记录（相同/差异入档）；②dt=0 步不推进状态（或如实记录其行为，供 D2 回退裁决）；③变 dt（1→6→1）改变输出且方向合理；④dt∈{0..16} 无 NaN/Inf。
- 失败条件：断言②④不成立且紧缩回退也不可行 → F2 触发（转输入端 gap-embedding 路径，不硬撑）。

### S1 — 训练（A/B 共享 + C-aug）
- 每种子：A/B 一次（论文协议干净训练）+ C-aug 一次（间隙增强）。共 6 次。超参与预处理逐字对齐 stress_test.py（EV-06：10 bin log1p、hidden 128、CNN-128 backbone）。

### S2 — 评测矩阵出表
- 产物：results/pilot_threearm.csv（逐种子×臂×间隙条件）+ results/pilot_threearm.md（mean±std 表+B/C 相对 A 差值+干净降幅）+ results/pilot_timing.json（U5 计时）。
- 强制 sanity：clean 下 A≡B（数值差 <0.1pp，D2 语义自检）；A@uniform30 与论文 Table III 方向一致（LNN@30% 应显著高于随机水平，pilot 预算内只做方向性核对，数量级核对归 S5）。

## 五、门线与结果映射（首里程碑验收=admission.first_milestone ①②③ + 本节）

- ①S0 四断言通过（U2 关闭）；②A 臂 clean ≥97%（D7 操作化）且 A@uniform30 方向核对通过；③三臂表落盘（CSV+MD）。
- 过门线：block5-30 下 B 或 C-aug 相对 A ≥ +2pp，且该臂 clean 降幅 ≤0.5pp。
- 结果映射：
  - pass → next_action=replicate：S5 全量协议（全量数据 30 epoch、≥3 种子、±std、N-MNIST+QuickDraw、clean 复现 Table I 数量级），S5 内做 E2/E3 归因细化。
  - B−A < +1pp 且 clean 不受损 → next_action=redesign（预注册负结果分支）：负结果落盘（FAILURE-PATTERNS 语义：时间条件化在该基准无边际收益，E1 成立），转「多种子复现+显著性」文档单元兜底其单次训练缺口。
  - +1pp ≤ B−A < +2pp 或 std 盖过效应 → next_action=continue（inconclusive）：加种子/加 epoch 放大后再判，不轻弃（2026-10-24 用户拍板「不要太轻易放弃」）。
  - S0 断言不可满足 → F2 转向路径（输入端修正项）。
  - 两轮跑不出第一组数 → F3 降级（QuickDraw 子集或 hidden 减半）。

## 六、停止条件（冻结）

- F1（负结果）：pilot 过门线未达且 B−A<+1pp、clean 不受损——按 §五 负结果分支处理，方向不再投算力。
- F2（实现边界）：ncps timespans 行为不兼容且紧缩回退/输入端修正项成本超出「小改进」边界 → 按预注册转向，不硬撑。
- F3（跑不出数）：pilot 两轮无第一组数 → 降级配置再试一轮，仍无则断点移交并求助 researcher。
- F4（占坑命中）：U4 残余触发器——pilot 开工前若通道恢复，定向全文扫 2510.07578 与 NIALIM；或 S2/OpenAlex 日后出现「该基准×块状间隙×原生时间条件化」同型工作 → stop → 转 screening-negative 并记录占坑来源。
- 单元级：硬超时 2560s；任何长步骤先 checkpoint 再继续；拿到改变决策的关键发现即早退。

## 七、复现入口

- 准入与证据链：admission.json（C1–C5→EV 引用可解析）；literature/related-work.md（EV-01..12、Q1..Q7）。
- U3 复现：lit_query citations（S2: ARXIV:2605.27467；OpenAlex: DOI:10.48550/arXiv.2605.27467）——两通道 count=0（2026-10-25 02:22/02:26 实查）。
- U4 复现：arxiv HTML 2510.07578 §V-B future work 段（§1.5 引文）；MR-MoE 2606.12240 forward filling 旁证（搜索快照级）。
- benchmark 入口：github.com/ye-kyaw-thu/LNN-vs-LSTM stress_test.py（EV-06）+ 本机 ncps 1.0.1（G:/ai/python11，cfc.py L112）。
- eligible/状态复验：`python scripts/research-topic-admission.py`、`python scripts/research-project-state.py`。
- 实验复现：S0–S2 脚本规格见 §四；产物落 results/（workflow.json 每阶段列明）。

## 八、遗留（本单元工具墙如实记录）

- 本 profile（research-planner）无 terminal、无 kanban 工具（tool_search 全库核实，仅 12 个 research 工具+文件/网络工具）→ git commit（research/ 根仓库，main）与看板卡更新留下一单元执行单元顺手完成，提交范围=design.md、workflow.json、STATUS.md、notes/DECISIONS.md（同 scout 先例，DECISIONS 01:1x 条）。
- 求助事件脚本（researcher-request.py）同样需 terminal，本单元无求助需求，未使用。
