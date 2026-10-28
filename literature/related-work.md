# 相关工作筛查｜液态网络抗丢帧没接时间：CfC 基准补真实间隙条件化

- 单元：candidate_screening（screening_attempts=1，本文件与 admission.json 同批产出）
- 执行 profile：research-scout（夜间生产单元，本地落盘）
- 时间：2026-10-25T00:55–01:15+08:00
- 结论速览：主锚 2605.27467 全文+开源 stress_test.py 全文逐行核验，缺口坐实（均匀随机置零丢帧、推理期 only、原生 timespans 未用、单次训练）；6 条不同查询、3 个可用渠道内未发现同型占坑工作；相邻范式（GRU-D/Latent-ODE/mTAND/Neural CDE/NIALIM/Contimask）有近邻但无一在「该部署级基准 × 块状间隙 × CfC 原生时间条件化」交点上。向前引文追踪受通道限制记 unknown。

## 一、search_log（7 条查询，2 个可用渠道 + 2 个受阻通道）

| # | query | channel | checked_at (UTC+8) | 结果摘要 |
|---|---|---|---|---|
| Q1 | closed-form continuous-time neural network CfC timespans irregular sampling missing data | web_search（搜索引擎后端） | 2026-10-25T01:00 | 命中 CfC 原文不规则采样实验（bit-stream XOR/PhysioNet/物理动力学含 missing phases）、Landsat CfC 重建、JeffLabonte/cfc-tsf-sagemaker（要求数据无缺失值）、NIALIM；无同型占坑 |
| Q2 | liquid neural network robustness missing frames block gaps sensor dropout | web_search | 2026-10-25T01:00 | 命中 2605.27467 原文页（压测协议 quote）、2510.07578 综述（missing data 列为 future work）、飞行导航 Science Robotics（扰动=噪声/亮度/对比度，非时间丢帧）；无块状间隙占坑 |
| Q3 | irregularly sampled time series missing values neural ODE GRU-D mTAND liquid network comparison | web_search | 2026-10-25T01:01 | 相邻范式簇确认：GRU-D/Latent-ODE/mTAND/Neural CDE（Kidger 2020 同样丢 30/50/70% 但=均匀随机、不同模型族）、Contimask（NeurIPS 2025，可解释性）；无一做 CfC×块状间隙×timespans |
| Q4 | "2605.27467" OR "Comparative Analysis of Liquid Neural Networks and LSTM" cited by | web_search | 2026-10-25T01:05 | 0 条可核验引用（仅 arXiv catchup 列表页、作者主页 [to appear]）；S2 API 通道 SSL 故障无法交叉验证 → 向前引文记 unknown |
| Q5 | "Accuracy, Memory Efficiency and Generalization" liquid neural networks recurrent 2510.07578 missing data irregular | web_search | 2026-10-25T01:05 | 2510.07578=综述+案例研究（投稿 TNNLS），missing data 明确列为 future work，不占坑 |
| Q6 | NIALIM rederived closed-form continuous-time neural networks irregular missing robustness timespans ablation | web_search | 2026-10-25T01:08 | NIALIM（TNNLS 2026）=近似误差理论+新闭式变体，非丢帧鲁棒性协议，不占坑；CfC 原文不规则实验为训练期设定非推理期压测 |
| Q7 | "ye-kyaw-thu/LNN-vs-LSTM" stress_test.py temporal dropout masked zeros inference | web_search + web_extract(raw.githubusercontent) | 2026-10-25T01:12 | stress_test.py 全文逐行核验（见证据账本 EV-06） |

渠道说明：
- 可用渠道 1＝web_search 搜索引擎后端；可用渠道 2＝本地 PDF 全文抽取（G:/research-papers/2605.27467.pdf、2106.13898.pdf 在盘）；可用渠道 3＝web_extract 对 raw.githubusercontent.com（arxiv.org/semanticscholar.org 域 SSL EOF 全败，raw.githubusercontent 同刻成功＝通道选择性故障，非全线断）。
- 受阻记录：web_extract 对 arxiv.org/html/*、api.semanticscholar.org 均 SSL unexpected eof（Firecrawl/Parallel 两个后端同报）；Semantic Scholar 引文 API 因此未核验。

## 二、evidence_ledger（决定性判断的证据）

- EV-01 | kind=full_text | status=verified | source=arXiv:2605.27467v1（PDF 在盘 G:/research-papers/2605.27467.pdf） | locator=§VI.C Robustness Stress Test | observation=原文 quote：「we performed a stress test by applying temporal [18] dropout during inference. We randomly masked out 0%, 30%, 50%, and 70% of the input frames/points to simulate sensor failure or intermittent signal loss.」＋ Table III（N-MNIST 30%: LSTM 77.48 vs LNN 91.84；QuickDraw 70%: LSTM 18.43 vs LNN 22.48）。
- EV-02 | kind=full_text | status=verified | source=同上 PDF | locator=§III.D 与 §V.D | observation=原文 quote：「The time-delta between consecutive observations is included as an additional input feature to make the model aware of sampling irregularity—a critical design choice that allows continuous-time models to exploit the gap duration directly.」——time-delta 仅在 PhysioNet 作为 40 维输入特征之一拼接，N-MNIST/QuickDraw 不带时间。
- EV-03 | kind=full_text | status=verified | source=同上 PDF | locator=§VI.A + §VIII | observation=原文 quote：「All reported results are obtained from a single training run per configuration.」；结论自认「further validation across more diverse datasets, stronger baselines, and multiple experimental runs is necessary」。
- EV-04 | kind=full_text | status=verified | source=同上 PDF | locator=REFERENCES [1]–[30] | observation=向后引文追踪：30 条参考文献全部读过标题/角色——最近的不规则时序文献仅 [30] Rubanova Latent-ODE（作为 sepsis 语境引用），无任何块状间隙/丢帧条件化/原生时间消融工作被引。
- EV-05 | kind=full_text | status=verified | source=同上 PDF | locator=Appendix Table IV + stress_test.py 段 | observation=ncps 0.0.7、Python 3.10、单张 NVIDIA GPU；「stress_test.py: A unified script for the temporal dropout robustness experiment…The stress test is applied at inference time only」；仓库 github.com/ye-kyaw-thu/LNN-vs-LSTM。
- EV-06 | kind=protocol_source | status=verified | source=github.com/ye-kyaw-thu/LNN-vs-LSTM main/stress_test.py（raw.githubusercontent.com 全文抓取，2026-10-25） | locator=Stress Evaluation 段与 DrawingClassifier.forward | observation=逐行核验：①掩码语义=逐时间步 Bernoulli 均匀随机、整帧/整点置零（`mask = (torch.rand(x.size(0), x.size(1), 1) > dr).float(); x = x * mask`），无块状结构、无重索引删帧；②CfC 调用 `out, _ = self.core(x)` 未传 timespans（原生时间输入全程未用，dossier 猜测坐实）；③N-MNIST 预处理=10 bin、log1p，与论文一致；④QuickDraw=10 类、每类 5000、max_len=100；⑤掩码只在 eval 循环内施加。
- EV-07 | kind=web_page(搜索快照) | status=verified_snippet | source=arxiv.org/html/2510.07578v1（Zong et al. 综述，2025-10-08，投稿 TNNLS） | locator=Future work 段与 §V | observation=该综述把「sensor noise, missing data, or regime changes」下的不变性目标列为 future work；其案例研究只做噪声扰动（σ=0.01–0.02），未做丢帧/块状间隙/时间条件化 → 不占坑，且佐证缺口存在。全文 PDF 未读（full_text_checked=false，仅搜索快照级）。
- EV-08 | kind=full_text | status=verified(前序单元) | source=arXiv:2106.13898（PDF 在盘 G:/research-papers/2106.13898.pdf） | locator=dossier _state/candidate-lnn-gap-cfc-20261025.json evidence_summary | observation=前序单元 2026-10-25 00:2x 全文核验，quote「since time appears explicitly in closed-form…」；本轮 Q1/Q6 搜索快照进一步印证：其不规则采样实验（bit-stream XOR、PhysioNet、含 missing phases 的物理动力学）均为训练期设定，无推理期丢帧压测、无该部署级基准。
- EV-09 | kind=web_page | status=verified_snippet | source=Neural CDE（Kidger et al., NeurIPS 2020） | locator=Experiment 段 | observation=quote：「We run three experiments, in which we drop either 30%, 50% or 70% of the data. The observations to drop are selected uniformly at random」——30/50/70 丢数据协议先例存在但=均匀随机、模型族为 CDE 非 CfC、无块状间隙、无部署级 LNN 基准 → 相邻不占坑。
- EV-10 | kind=web_page | status=verified_snippet | source=PubMed 41790819 / ORCID（NIALIM, IEEE TNNLS 2026, DOI 10.1109/TNNLS.2026.3669345） | locator=Abstract | observation=改进 CfC 零阶近似在高分辨率/不规则数据下的误差（Lagrange 插值近似理论+6 任务 SOTA），属近似精度线，非丢帧鲁棒性协议 → 相邻不占坑，related work 须引。
- EV-11 | kind=api_channel | status=blocked | source=api.semanticscholar.org/graph/v1/paper/arXiv:2605.27467 | locator=web_extract 返回 SSL unexpected eof（Firecrawl/Parallel 双后端） | observation=向前引文核验的 S2/OpenAlex 通道不可用；Q4 搜索引擎通道 0 命中。结论记 unknown，不用「没搜到」证明「没人引」。

## 三、closest_work（进 admission.json 的两条全读）

1. 2605.27467（JCSSE 2026 扩展预印本，2026-05-26 提交）——被改进对象。全文已读（EV-01/02/03/04/05）+ 开源 stress_test.py 逐行核验（EV-06）。它做了什么：四模态基准（N-MNIST/QuickDraw/IAM/PhysioNet Sepsis-3）CfC vs LSTM + 推理期均匀随机置零丢帧压测。与我们的差异：均匀随机→块状变长间隙；time-delta 仅作输入特征且 N-MNIST/QuickDraw 无时间→真实 Δt 喂 CfC 原生 timespans；单次训练→多种子。
2. 2106.13898（CfC 原文，Nature Machine Intelligence 4:992-1003，2021/v2 2022）——方法来源。全文在盘已读（EV-08）。它做了什么：LTC 闭式解，时间显式进入公式，含不规则采样训练实验。与我们的差异：不测「部署基准上推理期块状丢帧下原生时间输入的边际收益」；我们把它当工具在其结构最该兑现的场景量化。

辅助近邻（不进 closest_work 全读门槛）：2510.07578 综述（EV-07，snippet 级）、Neural CDE（EV-09）、NIALIM（EV-10）、GRU-D/mTAND/Latent-ODE 簇（Q3）。

## 四、citation_chasing

- backward：已做——2605.27467 参考文献表 30 条全部读过（EV-04）。无同型工作，最近邻=[30] Latent-ODE（语境引用）、[16] 飞行导航（扰动类型不同）。
- forward：部分受阻——搜索引擎通道（Q4）0 条可核验引用（论文 2026-05 挂出，引用窗口短）；Semantic Scholar API 通道 SSL 故障（EV-11）。状态=unknown，下一步（design 单元或下轮 screening）可重试 S2/OpenAlex；不得以本记录推断「无人跟进」。

## 五、claims

| claim_id | claim | status | evidence_refs |
|---|---|---|---|
| C1 | 2605.27467 的丢帧压测=推理期、均匀随机、置零式掩码，无块状间隙条件 | verified | EV-01, EV-05, EV-06 |
| C2 | 2605.27467 从未把时间喂给 CfC 原生 timespans（time-delta 仅 PhysioNet 输入特征，代码 core(x) 无 timespans） | verified | EV-02, EV-06 |
| C3 | 其全部结果为单次训练、无方差 | verified | EV-03 |
| C4 | 可检索范围内（2 渠道 7 查询）无「该基准×块状间隙×原生时间条件化」同型占坑；S2 向前引文通道受阻记 unknown | verified_with_unknown | Q1–Q7, EV-07, EV-09, EV-10, EV-11 |
| C5 | 三臂消融（A 论文式 / B 零填充+真实 timespans / C +gap 指示位）的判据、失败条件、验证路径可操作化 | verified（协议级，未实跑） | dossier validation_path, EV-06（A 臂语义已锁定） |

## 六、uncertainties / 未知项

- U1（已收敛）：原 dossier 头号不确定「masked 的确切语义」已由 EV-06 逐行核验解决＝置零、逐时间步、均匀随机；A 臂忠实复现语义锁定。
- U2（收窄但未关）：ncps 0.0.7（论文用版）timespans 行为仅以本机 1.0.1 源码核验（前序单元），0.0.7 未实测——pilot 第一步跑通最小 timespans 前向即可关闭。
- U3（记 unknown）：向前引文（S2/OpenAlex）未核验；不据此写「无人跟进」。
- U4：2510.07578 与 NIALIM 仅搜索快照级核验；若 design 阶段发现其正文含同型协议，须重开 screening。
- U5：N-MNIST 全量 30 epoch 单轮耗时未实测（Windows 数据加载可能上浮）——pilot 用子集，过门后再评全量成本。

## 七、品味/口径对照（taste-corpus checklist 映射）

- 清单#2 novelty 定位：两条 closest_work 全文核验+差异段落齐（本文件第三节）。
- 清单#5 消融完整：三臂=每组件「只换它」（A→B 只换时间条件化、B→C 只加 gap 指示位），判据带 ≥2pp 门槛与多种子要求——对齐清单#6 统计兜底（补 2605.27467 单次训练缺口本身即贡献之一）。
- 清单#7 声称收缩：贡献声称限定在「该公开基准的协议修正」，不泛化到「液态网络普遍抗块状丢帧」。
- 玩具红线：真实模型（ncps CfC）+ 真实公开 benchmark（N-MNIST/QuickDraw）+ 论文开源协议，无合成数据/自制小网络（toy_only_risk 见 admission.json）。
