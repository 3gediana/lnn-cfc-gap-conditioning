# operator_bench.md — CfC/液态单元算子基准与优化结论（S5-full-protocol 第六单元）

- 课题：液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a
- 阶段：S5-full-protocol 第六单元（fb-ab50d0ec9f「先优化算子再跑实验」：本单元禁止任何 30epoch 批量训练）
- 复现入口：`G:/ai/python11/python.exe experiments/operator_bench.py`（原始数字全量落盘 `results/operator_bench.json`，本 MD 所有数字引自该 JSON）
- 运行环境：torch 2.10.0+cu128 / CUDA 可用 / ncps **0.0.2**（安装版，`G:/ai/python11/Lib/site-packages/ncps/torch`）
- **算子基座声明：一切结论基于旧算子（ncps 0.0.2；掩码 Convention 倒挂已修正、不影响 A/B 干净训练）**；已跑 ckpt 全部保留、本单元零修改（无修复落盘，见 §4）

---

## 1. 结论速览（TL;DR）

| 编号 | 算子项 | 实测结果 | 判定 |
|---|---|---|---|
| N0 | Convention 现状锚定 | clean A≡B（acc 逐位相等 0.9121）、clean 输入修改帧=0.0、block5-30 实际掩码率 0.3059/uniform30 0.2975（名义 0.30） | **PASS**（修正生效，与第五单元 T1/T4 互证） |
| N1 | τ-tie 覆写点（ltc_cell.py:223-244） | LTC elapsed_time=0 → **NaN**（cm_t=softplus(cm)/(0/6) 除零）；dt=1e-8/1e-4/1 有限；本协议 CfC default 路径 ts=0 有限（max&#124;out&#124;=0.866） | LTC 路径**硬墙**；**不在本协议科学路径上**（非 wiring CfC），潜在风险+缓解配方已记录 |
| N2 | scale-state 爆炸风险（harvest 2610.15139） | 状态按 s∈{1,10,100,1e4} 放大回馈 100 步：CfC default 模式 max&#124;h&#124;≤1.0 全有限；pure 模式 ≤0.205 全有限；全模型输入 ×100 输出有限（max&#124;out&#124;≈15.3） | **不复现**（结构性有界：default 的 ff1/ff2=tanh、pure 的指数衰减回 A、backbone LayerNorm） |
| N3 | dt=0 零输入行为（u2 断言②真实尺寸扩展） | 100 连续 dt=0 步：**全部有限、max&#124;h&#124;≤1.0（结构性 tanh 界）**；逐样本收缩仅弱成立（cell 级 rel change 1.24→0.96 / 0.94→0.84，模型级全掩码 0.85→1.03 **不收缩**）；50 步 dt=0 后 dt=51 真实帧恢复有限 | **有界+有限 PASS；强收缩不成立（与 u2 迷你尺寸 1.09→0.0006 的差异如实记录）** |
| N4 | 梯度量级 | 真实 D2 模式（block5-30，dt∈{0,1,..,6}）：‖∇_ts‖=0.0307、参数梯度全有限、掩码帧输入梯度=0.0（结构性）；**恒定 dt 压力测试：dt≥15 起 ∇_ts 爆炸（dt=101 时 ‖∇_ts‖≈1.7e18、参数梯度触及 Inf 边界，两次运行一次全 Inf 一次有限=浮点累积顺序敏感的临界溢出）** | 协议路径**安全**（dt≤6 且非常量）；大 dt 恒定循环为算子边界，grad clip 1.0 为既有兜底 |
| N5 | B>1 timespans 边界（cfc.py:166） | (4,L) 批式 RuntimeError（squeeze 得 (B,) 与 (B,H) 广播失败）复现；(1,L)/(1,L,1)/batchless (L,)/(L,1) 均可用；manual-loop vs 库 B=1 真实尺寸 max diff=**4.05e-06**（<1e-4 门） | 边界已定格；**manual-loop 缓解在位且恒等**（协议 B/C 臂路径） |
| E1 | d2 向量化收益 | 循环版 vs 向量化版（GPU，torch.equal 恒等）：B=128 **1.32s→0.43ms（3103×）**、B=256 同量级 | 补丁收益坐实（补丁前 C 臂训练主瓶颈） |
| E2 | 108 格评测构成 | 单格@n=7500：A=1.50s / B=1.54s / C=1.56s（分段：cell 循环占 ~85%，feats/mask+d2/readout 各 ~5%）；构成模型 36A+36B+36C=**165.6s vs 盘上实测 167.3s（偏差 1.0%）**；profile mirror 与生产 `eval_arm_condition` 输出**逐位相等** | 167.3s 构成已解释；估计模型可复用 |
| E3 | 逐 batch `.item()` 同步开销（候选修复 FIX-1） | defer 同步（4 次/batch → 1 次/cell）对 B 臂单格耗时**无显著影响（+0.2%，噪声内）** | **FIX-1 不采纳**（数据驱动否决，见 §4） |
| E4 | 逐样本 vs 批式路径 | 库 B=1 逐样本 46.4ms/样本、manual-loop B=1 逐样本 45.7ms/样本；批式 64 样本 53ms（**56×** 摊薄）；逐样本路径外推 7500 样本 ≈348s/格 | 协议采用批式 manual-loop 是唯一可行路径（既有决策获量化支持） |
| E5 | 构成模型验证 | 6 格真实样本（A/B×clean/block5-30）计时 12.22s（含 6 格预热，模型预测计时格 6.1s）；108 格模型 165.6s vs 盘上 167.3s | 模型偏差 ~1%，排产可复用 |
| E6 | 训练步构成（benchmark only） | 单步（B=128，预热后 8 步单同步对）：ab 49.6s/epoch 估计、c 50.9s/epoch 估计，落在 full_run.log 实测带 46-53s/ep 内；fwd/bwd（逐相同步归因上界）ab 60/95ms、c 60/72ms | 训练耗时=manual-loop 前向+反传图，无异常成分 |

回归（规格同 04:4x selftest 68 项，全部本单元实跑）：
- `experiments/full_protocol.py selftest` → **OVERALL PASS, exit=0**（d2 向量化 vs 循环版 68 项 case-device torch.equal 恒等 + full_splits 确定性/子集性 + 1+1 epoch 续跑等价 max&#124;Δstate&#124;=0 + eval 冒烟 A≡B/掩码率 0.305）；证据 `experiments/operator_regression_selftest.log`
- `experiments/eval_patch_selftest.py` → **SELFTEST PASS, exit=0**（48 用例 hit 计数恒等 + summarize 门控回归 3/3）；证据 `experiments/operator_regression_evalpatch.log`

---

## 2. 问题定位（按严重度）

### P1（真实 D2 路径外的梯度爆炸边界，非阻塞）
恒定 dt 序列下，CfC default 模式的时间门 `sigmoid(t_a·ts+t_b)` 随 dt 增大饱和（dt=101 时 99.0% 单元 &#124;z&#124;>4），收缩性混合被移除，循环雅可比在 100 步链式反传中放大：‖∇_ts‖ 从 dt≤5 的 0.02-0.18 升至 dt=15 的 4.7e7、dt=30 的 2.8e12、dt=101 的 1.7e18（参数梯度触及 Inf 边界，且该处溢出对浮点累积顺序敏感=临界溢出）。**协议不受影响**：D2 真实模式 dt∈{0,1,…,6}（block5-30 最大 gap_len+1=6；block15-30 最大 16，实测真实模式 ‖∇_ts‖=0.0307 全有限），且 uniform30/block 条件无恒定 dt。训练侧 grad clip 1.0 为既有兜底。**给 S5 判读的输入**：B−A 差异集中在间隙邻域（S2 caveat）在真实尺寸依然成立，且收缩衰减比 u2 迷你探针暗示的更弱（见 P2），gapnb 读表保留更多信号——三口径兼报的预注册要求因此更重要。

### P2（u2 断言②「有界收缩」的真实尺寸修正，非阻塞）
S0 探针（迷你 16→32、随机权重、20 步）记录「零输入 dt=0 迭代有界收缩（1.09→0.0006）」。本单元真实尺寸（128→256、训练后权重、100 步）实测：**有界成立（max&#124;h&#124;≤1.0，全部有限）但强收缩不成立**——cell 级逐样本 rel change 仅 1.24→0.96（100 步衰减 ~23%），模型级全掩码（backbone(0) 常数特征驱动）rel change 0.85→1.03 不降。解释：训练后权的零输入 dt=0 映射存在远离零的不动点、谱半径接近 1；状态在有界流形内保持流动而非塌缩。**影响**：不破坏 D2 语义（无爆炸、无 NaN；间隙恢复 dt=51 有限），但「收缩性使末态差异衰减」的定量幅度不能引用迷你探针数字；读表兼记末态与间隙邻域的 S2 caveat 继续有效。**预注册判据不改写，如实记录为 partial  leg**。

### P3（库 API 硬边界，已缓解）
`cfc.py:166 ts=timespans[:, t].squeeze()`：B>1 时 (B,) 与 cell 内 (B,H) 广播失败 → RuntimeError。B=1/batchless 形态可用。协议 B/C 臂自 S2 起走 manual-loop，本单元真实尺寸复验与库 B=1 max diff=4.05e-06（u2 迷你尺寸 3.28e-07 的同源确认）。不改 site-packages 共享库（环境共享+影响面不可控）。

### P4（LTC τ-tie 除零墙，不在科学路径）
`ltc_cell.py:223-244 cm_t=softplus(cm)/(elapsed_time/ode_unfolds)`：elapsed_time=0 → 除零 → NaN（dt=1e-8 亦仅梯度有界：输出 ~2.5e-7）。本协议用非 wiring CfC（CfCCell default，cfc_cell.py:136-166 无 cm_t 除法），LTC 不在科学路径。若未来 wired/LTC 用法需要 dt=0：wrapper 内 clamp elapsed_time≥1e-4（实测有限，语义近似需显式标注）。

### P5（效率残余瓶颈=launch-bound 循环，无恒等修复空间）
108 格 167.3s 中 ~85% 是 B/C 臂 100 步 Python 循环（每步 ~10 个小 kernel，launch-bound；分段计时总和 > 生产计时即异步重叠被同步点破坏的证据）。逐样本化不可行（46ms/样本）。可击穿此瓶颈的候选（torch.compile/CUDA graph/4×Linear 融合 cell）**均改变前向数值**（融合 GEMM 换 kernel → 舍入不同）→ 按预注册规则会触发 A/B ckpt 重训（6×30ep≈4.6h）判定；收益（评测 167s→~60s、训练每 epoch ~49s→~25s）与代价（4.6h 重训+数值漂移风险）不成比例，**本单元不采纳**，留待 researcher 决策（见 §5 next_units 建议）。

---

## 3. 效率基准明细（排产可复用）

- 单格评测成本@n=7500（训练后 ckpt，block5-30）：A=1.50s、B=1.54s、C=1.56s；clean 条件同量级（E5 样本格）
- 108 格 = 36A+36B+36C ≈ 165.6s（实测 167.3s，偏差 1.0%）——**该模型替代已作废的 3827s 旧估计（那测的是补丁前 d2 CPU 循环路径）**
- C 臂训练 ~50.9s/epoch、ab ~49.6s/epoch（benchmark 估计，落在 full_run.log 实测 46-53s/ep 带）；6 训练 ≈2.5h + 评测 ≈2.8min 的排产分量不变
- d2_timespans_vec 对循环版：B=128 3103×（1.32s→0.43ms）、torch.equal 恒等（68 项 selftest 担保）

---

## 4. 修复决策与数值保真判定（单元指令③）

**本单元落地修复：无。** 决策链（全部数据驱动）：
1. 唯一候选效率修复 FIX-1（eval 逐 batch 4 次 `.item()` 延迟到 cell 末一次同步）：E3 实测收益 **+0.2%（噪声内）** → 不采纳。GPU 队列深度足够吞掉 4 次/batch 的同步，不是瓶颈。
2. 库内修复（LTC clamp、cfc.py squeeze）：均需改 site-packages 共享库，影响面超出本课题且 B>1 已有 manual-loop 恒等缓解 → 不改，只记录边界与配方。
3. 击穿 launch-bound 瓶颈的融合/编译路线：改变前向数值 → 触发 A/B 重训判定 → 收益/代价不成比例（P5）→ 不采纳，交 researcher。

**数值保真判定**：因零修复，本仓科学路径（`pilot_threearm.py` / `full_protocol.py`）前向数值与本单元开工前**逐位一致**（N0 A≡B 输出 max diff=0.0；profile mirror 与生产 eval 输出逐位相等；d2 selftest 68 项 torch.equal）。
**A/B ckpt 是否需重训：不需要（算子侧）。** A/B 臂 3 ckpt（30/30，train acc 0.9518/0.9661/0.9688）继续有效；唯一待重训仍是 C 臂 3 ckpt——原因是 Convention 倒挂修正（第五单元已定），与本算子单元无关。S3/S4 pilot 产物按第五单元判读仍须按修正 Convention 重算（ckpt 在盘）。

---

## 5. 算子墙台账（供 workflow stop_conditions F8 引用）

| 墙 | 位置 | 触发条件 | 状态 |
|---|---|---|---|
| W-LTC-τ | ltc_cell.py:223-244 | LTC + elapsed_time=0 | 硬墙（NaN）；不在科学路径；缓解=wrapper clamp≥1e-4 |
| W-BATCH-TS | cfc.py:166 | 库 forward + B>1 + timespans | 崩溃；已缓解（manual-loop，恒等 4.05e-06） |
| W-BIGDT-GRAD | cfc_cell.py:162 + 循环反传 | 恒定 dt≥15 的 100 步序列反传 | ∇_ts 爆炸至 1e18 量级；协议 dt≤6 不触发；兜底=grad clip 1.0 |
| W-LAUNCH | 100 步 Python 循环 | 任何 B/C 臂批量计算 | launch-bound ~1.5s/格；恒等修复空间已穷尽（E3 证伪），非恒等修复需重训判定 |

**当前无一堵墙阻塞科学路径**（均有缓解或不在路径上）→ 本单元不触发 F8 早退，继续排产；若后续单元需要 wired/LTC+dt=0、库批式 timespans、或恒定大 dt 训练，则 F8 触发并回退设计。

---

## 6. 限制与诚信声明

- 本单元全部数字来自 `results/operator_bench.json`（ran_at 见 JSON env 块）；E6 训练步为 benchmark（个位数 step 后丢弃，未落任何 ckpt、未写 progress、未动 experiments/ckpt/ 与 results/full_* 既有产物）。
- C 臂单格成本用同架构随机初始化模型测得（成本由结构决定；superseded C ckpt 为倒挂 Convention 训练，仅作证据保留，不用于任何计时外的用途）。
- N3「收缩」判据在 mini→real 尺寸间的迁移失败已如实记录（P2），未修改预注册判据、未挑选有利口径。
- 恒定 dt 压力测试的 Inf 溢出对浮点累积顺序敏感（两次运行一次全 Inf 一次有限），报告中以「触及 Inf 边界」表述，不外推为确定性崩溃。
