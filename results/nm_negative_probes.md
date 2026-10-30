# nmnist-negative-result-probes — S10-redesign 负结果归因探针（纯推理，禁训练）

- 课题：液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a
- 阶段：S10-nmnist-threearm-baseline-redesign（researcher 判读 eaea7487 重定义；H1 已双数据集结论级证伪，本阶段回答负结果仓库必答题「C 臂 +9.47pp 从哪来」）
- 输入：experiments/ckpt/nmnist_seed{0,1,2}_{ab,c}.pt（S10 收口 ckpt，10/10 epochs，verify exit=0；本阶段只读不写）+ results/nmnist_threearm.csv（S10 结论级表锚点）
- 口径：A 臂=forward(timespans=None)（无 dt）；C 臂=manual-loop+D2 真实 timespans+gap 指示位；C_no_dt=A 臂口径作用于 C ckpt（gap-bit 通道保留真实掩码，唯一改动=去 dt）
- 判据：跑前冻结（源自 notes/researcher-interventions/eaea7487ddfc479c83fe016c90d89c8f.md 第五节），禁事后改

## 表1 主探针（% acc，meanpool 主口径；逐 seed×条件，每格=3 模式 mean±pstdev）
| seed | 条件 | C_dt（带 dt） | C_no_dt（无 dt） | C_no_dt−C_dt(pp) | A_ref（S10 A 臂重算） | C_no_dt−A(pp) |
|---|---|---|---|---|---|---|
| 0 | clean | 98.82±0.00 | 98.82±0.00 | +0.00 | 97.87±0.00 | +0.95 |
| 0 | uniform30 | 97.84±0.24 | 97.87±0.18 | +0.03 | 84.09±0.70 | +13.78 |
| 0 | block5-30 | 90.74±1.31 | 90.85±1.30 | +0.11 | 74.36±1.06 | +16.49 |
| 1 | clean | 98.80±0.00 | 98.80±0.00 | +0.00 | 98.37±0.00 | +0.43 |
| 1 | uniform30 | 98.09±0.23 | 97.98±0.30 | -0.11 | 93.26±0.49 | +4.72 |
| 1 | block5-30 | 91.29±0.42 | 91.35±0.43 | +0.06 | 84.50±0.87 | +6.85 |
| 2 | clean | 98.73±0.00 | 98.73±0.00 | +0.00 | 98.11±0.00 | +0.62 |
| 2 | uniform30 | 97.62±0.07 | 97.65±0.05 | +0.02 | 92.82±0.25 | +4.83 |
| 2 | block5-30 | 89.33±1.30 | 89.50±1.27 | +0.17 | 84.09±0.50 | +5.41 |

三口径汇总（3 种子 mean±pstdev，跨 9 行）
| 口径 | clean | uniform30 | block5-30 |
|---|---|---|---|
| C_dt（冻结） | 98.78±0.04 | 97.85±0.27 | 90.45±1.37 |
| C_no_dt（冻结） | 98.78±0.04 | 97.83±0.25 | 90.57±1.33 |
| A_ref（恒等自检） | 98.12±0.20 | 90.06±4.26 | 80.99±4.76 |
| C_no_dt_nogap（诊断） | 98.78±0.04 | 97.79±0.26 | 90.56±1.32 |

## 判据①（跑前冻结）：C_no_dt−A（block5-30，meanpool，3 种子 mean）
- C_no_dt=90.57%  A_ref=80.99%  C_dt=90.45%
- **C_no_dt−A=+9.58pp**（逐种子 {'0': 16.49, '1': 6.85, '2': 5.41}）；C−A=+9.47pp（S10 锚点 +9.46pp，对账）；推理期 dt 净效应 C−C_no_dt=-0.11pp
- 冻结阈值：≥+5pp→训练期主导；<+2pp→推理 dt 主导（矛盾→查实现）；其间→inconclusive
- **verdict=training_dominant_supported**：C 臂增益几乎全部来自训练期（块增强+gap-bit）——E2 的 N-MNIST 确认，叙事闭合

## 判据③（sanity）：clean 口径切换差
- C_no_dt@clean=98.78%  C_dt@clean=98.78%  |差|=0.0000pp（容忍 <0.3pp）→ **PASS**：clean 无间隙 dt≡1，两口径应≈同值；差<0.3pp=PASS（口径切换生效）

## 判据②（跑前冻结）：dt 粒度响应谱（seed0_ab，B 臂口径，固定 batch=test 前 256，mask=block5-30(seed0,pattern0)，扫常数 timespans dt）
| dt | mean hidden L2 | 相对 L2 响应 R(dt) vs dt=1 | batch meanpool acc | logits max|Δ| vs dt=1 |
|---|---|---|---|---|
| 1 | 27.8314 | 0.000000 | 85.16% | 0.0000 |
| 2 | 28.1718 | 0.073098 | 84.38% | 1.3523 |
| 5 | 28.4048 | 0.148303 | 82.81% | 2.2595 |
| 10 | 28.4937 | 0.181729 | 83.20% | 2.3474 |
| 20 | 28.5276 | 0.199260 | 83.20% | 2.3112 |
- R_max=0.199260（平坦阈值 0.001），hidden 全有限=True
- **饱和点 dt*=20**（预注册定义：min dt∈[2, 5, 10, 20] 使 R(dt)≥0.95·R_max）
- 冻结阈值：dt*≥5→量化假设存活；dt*<5→证伪；平坦→inconclusive
- **verdict=supported**：dt*>=5——模型对 bin 级 dt 粒度仍敏感，帧化量化是 H1 失败的协议侧候选解释（入机制讨论）
- 稳健性（诊断，非判据输入）：{"uniform30": {"dt_star": 20, "R_max": 0.198682, "flat": false}, "clean": {"dt_star": 20, "R_max": 0.185449, "flat": false}}

## 恒等自检（失败条件项，防口径漂移）
- A_ref vs S10 A 行 max|diff|=0.000044；C_dt vs S10 C 行 max|diff|=0.000033（容差 5e-4）→ identity_pass=True
- 注：A_ref/C_dt 为本进程重算，应与 S10 结论级 CSV 对应臂逐位一致（容差 5e-4=舍入级）；不一致=口径漂移，按失败条件处理

## 冒烟（子步1）
- gates={"ckpt_load": true, "clean_switch_lt_0p3pp": true, "probe_matches_S10_same_seed": true, "dt_scan_hidden_finite": true, "dt_scan_response_nonzero": true}，gates_all_pass=True，smoke_sec=5.3
- seed0 clean 两口径：C_dt=0.9882 / C_no_dt=0.9882 → 切换差 0.0pp

## 计时与复现
- {"schema": "nm-negative-probes-timing/v1", "data_prep_sec": 0.5, "smoke_sec": 5.3, "main_eval_sec": 65.0, "total_sec": 70.4, "hard_cap_sec": 600.0, "note": "纯推理探针；数据只载 test；无训练无 ckpt 写入；data_prep_sec 单独计量（勿与总耗时混记，S10 同款键名 bug 不复犯；本块由执行单元按运行日志校正：data_prep 0.5s=load_test 实测、main 65.0s=108 行累计、smoke 5.3s、总 70.4s）"}
- 复现：G:/ai/python11/python.exe experiments/nm_negative_probes.py all（smoke→main→spectrum→判据→CSV/MD/progress；main 逐行原子落盘可断点续跑；report 子命令从 progress 确定性重建 CSV/MD 不重算）

## 限制
- C_no_dt 的 gap-bit 通道必须填值（C 模型 core_in=129）：冻结口径填真实掩码（只去 dt，隔离推理期因素）；诊断口径 C_no_dt_nogap 填 0（再去 gap 信息，OOD 于 C 训练分布，仅拆解用）
- 次探针为常数 dt 扫描（统一 elapsed time），非 D2 变 dt 序列；测的是 cell 对 dt 量级的敏感性，用于检验帧化量化候选机制，不直接复现 B 臂推理分布
- 本阶段纯推理：未动任何 ckpt、未训练；GPU 与 S11（已收口）无并行争抢
