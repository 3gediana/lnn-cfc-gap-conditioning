# S4-pilot-verdict — 三臂 pilot 判读（H1/H2 adjudicate + 首里程碑②③）

- 单元：unit.S4 lab-verifier（2026-10-26T04:1x+08:00，夜窗终点 1792972801，硬超时 310s 内完成）
- 对象：results/pilot_threearm.csv（108 数据行）+ pilot_threearm.md + pilot_progress.json + pilot_timing.json（eval_sec=208.0）
- 判据：design.md §五门线（过门线=block5-30 下 B 或 C-aug 相对 A ≥ +2pp 且该臂 clean 降幅 ≤0.5pp）+ admission.first_milestone ①②③ + §六 F1
- 方法：**先用 python 对 CSV 独立复算再下判**（experiments/s3_verify_csv.py，37 项检查全过 exit=0，不采信 MD/回执汇总）；复算输出 experiments/s3_verify_csv_output.txt

## 一、独立复算结果（37/37 OK，0 DIFF）

| 量 | MD/progress 声称 | 本单元从 CSV 复算 | 判定 |
|---|---|---|---|
| 行数/网格 | 108 | 108（3 种子×3 臂×4 条件×3 模式无缺格，n_eval 全 3000） | 一致 |
| clean A/B/C（meanpool，3 种子 mean） | 10.43/10.43/10.51 | 同（C−A=+0.08pp；B−A=+0.00pp） | 一致 |
| clean A≡B | 0.000pp | 0.000pp，且 9/9 行三口径（meanpool/final/gapnb）恒等（恒定类） | 一致（比声称更强） |
| uniform30 A/B/C | 13.27/12.92/18.21 | 同（B−A=−0.35、C−A=+4.94pp） | 一致 |
| block5-30 A/B/C | 13.69/12.98/19.06 | 同（B−A=−0.71、C−A=+5.36pp） | 一致 |
| block5-30 逐种子 C−A | +4.08/+4.78/+7.24 | 同 | 一致 |
| block15-30 A/B/C | 14.42/13.69/16.20 | 同（B−A=−0.73、C−A=+1.78pp） | 一致 |
| C clean 降幅（C−A 口径） | mean +0.08pp | mean +0.08pp；逐种子 −0.23/+0.47/+0.00pp（散布 ±0.47pp 贴近 0.5pp 门线） | 一致 |
| H2 Δ（B−A 增益 block15−block5） | −0.02pp | −0.02pp | 一致 |
| A@uniform30 vs chance | z=5.97>2 PASS | z=5.97（n=3000 单口径）/z=17.91（n=27000 合并口径），均 PASS | 一致 |
| 实现掩码率 | ≈30% | mean realized masked_fraction=0.3013 | 一致 |
| progress.json verdict 块 | gate=C/pass/replicate | 与复算一致（注：该 JSON 混合单位——无后缀键=分数、`_pp` 后缀键=pp，对账时须先核约定） | 一致 |

**读表口径敏感性（复算确认，verdict 必带）**：block5-30 C−A 随口径大幅变化——meanpool（论文口径/门控所用）**+5.36pp**、gapnb（间隙邻域 K=5）**+2.64pp**、final（末态）**+1.30pp**（<H1 的 +2pp 门线）；B−A 三口径均 ≈0 或负（meanpool −0.71 / gapnb −0.29 / final −0.04pp），结论不受口径影响。门控判定以 meanpool 论文口径为准。

## 二、首里程碑裁定（admission.first_milestone）

- ①（S0 四断言/U2 关闭）：**已满足**（00:5x 判读已裁定，四断言 4/4+复跑一致）。
- ②（A 臂 clean ≥97% 且 A@uniform30 方向核对）：**未达**——A@clean=10.43%=chance 级（D7 操作化判据 ≥97% 差 ≈86.6pp）；A@uniform30=13.27% 方向核对 PASS（z=5.97/17.91 均 >2）。A/B 输出恒定类（clean 9/9 行三口径恒等）= pilot 2-epoch 纯预算缺口，verify 4/4+代码级核验证明非实现缺陷（D7 断点规则：查实现后续跑，不算方向失败）。
- ③（三臂表 CSV+MD 落盘）：**达成**（108 行+汇总+三门控 sanity：clean A≡B=0.000pp PASS、uniform30 z PASS、D7 未达如实入档）。

## 三、H1 adjudicate — **inconclusive**（门控存活，机制证据不足）

机械门控（design.md §五，meanpool 口径）：

- **B 臂**：block5-30 B−A=−0.71pp（σ≈0.55pp/格，噪声内），clean 降幅 +0.00pp → F1 字面条件「B−A<+1pp 且 clean 不受损」对 B 臂成立。
- **C 臂**：block5-30 C−A=+5.36pp ≥+2pp 且 clean 降幅 +0.08pp ≤0.5pp（逐种子 +4.08/+4.78/+7.24 一致）→ **gate_pass_arm=C，decision=pass**。
- 按 D3 预注册语义（C 臂门线=保守方向存活判据，归因细化归 S5），C 臂门控先触发，**负结果分支不启动**。

但 H1 的科学声称在 pilot 层**不足以 adjudicate**，三条理由均不构成机制证据：

1. **chance 级基数**：A/B clean=10.43%（恒定类），pilot 远未收敛——基线本身未学会任务，臂差不反映机制收益；
2. **增强训练混杂**：C−A 含块状间隙增强训练效应（D3 明示），无法归因到 timespans/指示位本身；
3. **读表口径敏感**：C−A 从 +5.36pp（meanpool）到 +1.30pp（final）大幅缩水，final 口径已低于 +2pp 门线——「收益有多大」强依赖读表选择。

结论：H1 维持 **inconclusive**——门控出口 pass（C 臂保守存活）为 replicate 提供依据，但 B 臂字面失败+基数 chance 级+口径敏感三条叠加，pilot 数据不支持任何机制性声称。

## 四、H2 adjudicate — **falsified**（预注册失败条件命中）

- 预注册：block15 增益 ≥ block5 增益（mean 意义单调）；失败条件=block15 增益 ≤ block5 增益 → 次判据不成立（不单独杀方向，收窄机制解释）。
- 实算：Δ(B−A, block15−block5)=**−0.02pp**（−0.73 vs −0.71pp）→ **不成立**。
- 附带（复算精确口径）：C 臂原始精度 block5→block15 = 19.06→16.20 = **−2.85pp**（增益口径 C−A 变化 = +1.78−+5.36 = **−3.58pp**）——C 臂收益随块长下降，与 H2 预测方向相反。
- 按预注册处置：H2 不单独杀方向，但机制解释收窄——若收益存在，更可能来自「有洞」的粗粒度感知而非精确时长信息。

## 五、双 caveat（必带）

1. **QuickDraw 数据集降级**（DECISIONS 2026-10-26 02:1x 正式拍板）：N-MNIST 五通道 SSL 墙+代理 7897 全灭（garrickorchard Cloudflare 人机页/Mendeley 文件端点 EOF/PyPI EOF/HF EOF/GitHub 无数据资产），按 design.md §六 F3 精神降级 QuickDraw-only 为 pilot 数据集（同论文仓库协议）。影响：QuickDraw L=100 使 block15 为字面块长（对 H2 可检验性反而有利）；N-MNIST L=10 场景下 block15 会退化为整段掩码。**H1/H2 结论级必须回 N-MNIST 复现**（S5 结论级基准；免墙镜像仍缺=daytime/user-assisted info_need）。
2. **D7 保真度缺口**：A@clean=10.43%（chance 级）vs 论文 Table III QuickDraw clean≈98.6-98.7%（G:/research-papers/2605.27467.pdf 第 6 页）——≈88pp 缺口。定性=pilot 2-epoch（1 万样本）纯预算缺口（train acc 0.22-0.38 为证），非实现缺陷（verify 4/4+代码级核验）；~99% 严格复现归 S5 全量 30 epoch。

## 六、总判词

- **verdict = inconclusive**；**next_action = replicate**（执行定义=S5-full-protocol 全量协议：30 epoch 全量数据保真度复现 + N-MNIST 结论级基准 + E2 B-train 对照臂）。
- 负结果分支不启动：chance 级基数上的臂差不构成机制证据；F1 字面条件对 B 臂成立但 C 臂保守存活门控先触发（D3 预注册语义以门控出口为准）。
- S5 复测注意（复算新带出）：C clean 逐种子散布 ±0.47pp 贴近 0.5pp 门线，S5 须逐种子报告降幅；读表口径须预注册主口径（meanpool 论文口径）并三口径兼报。

## 七、复盘

- 可复用路径：独立复算脚本已固化为 experiments/s3_verify_csv.py（S5 复判入口，37 项检查 exit=0）；「先复算再下判」模式第三次零成本抓到全部数字级真相，并新抓到混合单位 JSON（`_pp` 后缀 vs 分数）这一对账陷阱——判读 progress/timing 类 JSON 先核单位约定。
- 下一个最小同类改进：S5 判读时对 meanpool/gapnb/final 三口径分别过门线并预注册主口径；C clean 降幅改逐种子门控（均值过线但散布贴近门线时升级报告）。
- 机械判读与科学判读分离的模式再次验证：机械门控 pass（C 臂）≠ H1 supported；本 verdict 把两者的差异显式落盘。
