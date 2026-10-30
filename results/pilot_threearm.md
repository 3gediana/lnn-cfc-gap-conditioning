> **superseded（2026-10-31 判读补注）**：本表数值系 2026-10-26 在**倒挂掩码 Convention** 下评测得出（clean 输入被 100% 清零→chance 级 10.43%，证据 results/s5_mask_convention_probe.json、results/full_threearm_CONVENTION_NOTE.md），**不得引用为科学结论**；S4 的 verdict=inconclusive/replicate 即基于该作废读数。pilot 的科学职能（go/no-go 门）已由 S5-full-protocol 结论级表（results/full_threearm.csv/md，修正 Convention）履行，本表仅存历史证据。原文「N-MNIST SSL 墙」表述已过时：N-MNIST 数据 2026-10-26 已全量落盘（data/nmnist，Train 60000+Test 10000 个 .bin，SHA-256 在 README）。

# S3-pilot-threearm 三臂 pilot 结果（% acc，3 种子 mean±std，逐种子明细见 CSV）

- 数据集：quickdraw（F3 式降级：N-MNIST 数据通道被 SSL 墙挡，证据见 results/fetch_assets_report.json、data/nmnist/download_report.json；N-MNIST 移交下一单元）
- 协议：stress_test.py 逐字同款（EV-06）；pilot 子集 train 10k×2 epoch、eval 3000；读表三口径=meanpool(论文)/final/gapnb(间隙邻域K=5)
- 臂：A=库 forward(timespans=None,均匀dt=1)；B=manual-loop+D2 真实 timespans（与 A 共享 checkpoint/掩码）；C=B+gap 指示位+块状增强训练（单独 checkpoint）
- 条件：clean / uniform30(逐时间步 Bernoulli 0.3) / block5-30、block15-30（块长 b 划分、每块 Bernoulli 0.3，期望掩码率 30%；3 固定种子化模式跨臂配对）

| 条件 | A | B | C | B−A(pp) | C−A(pp) |
|---|---|---|---|---|---|
| clean | 10.43±0.00 | 10.43±0.00 | 10.51±0.29 | +0.00 | +0.08 |
| uniform30 | 13.27±0.54 | 12.92±0.54 | 18.21±1.33 | -0.35 | +4.94 |
| block5-30 | 13.69±0.50 | 12.98±0.45 | 19.06±1.27 | -0.71 | +5.36 |
| block15-30 | 14.42±0.60 | 13.69±0.67 | 16.20±0.74 | -0.73 | +1.78 |

## 强制 sanity（S2 入口条件）
- clean A≡B：|A−B|=0.000pp → PASS(<0.1pp)
- A@uniform30=13.27% → 方向核对 PASS(z=5.97>2 vs chance)
- A@clean=10.43% → D7 pilot 忠实性(≥97%) 未达（按 D7 查实现，不算方向失败）
- manual-loop 真实尺寸复验：verify_pass=True，vs 库 B=1 max diff=0.0

## 门线与假设判读（design.md §五）
- H1（block5-30 下 B 或 C ≥+2pp 且该臂 clean 降幅 ≤0.5pp）：B−A=-0.71pp、C−A=+5.36pp；B clean 降幅=+0.00pp、C clean 降幅=+0.08pp → gate_pass_arm=C
- H2（block15 增益 ≥ block5 增益，mean 意义）：Δ=-0.02pp
- 判读：decision=pass，next_action=replicate

## 限制
- pilot 为内部方向性结果（1 万样本 1-2 epoch、3 种子、评测子集 3000）；结论级归 S5 全量协议
- C−A 含增强训练混杂（D3 预注册：门线对 C 为保守存活判据，归因细化归 S5）
- QuickDraw L=100（block15 为字面块长）；N-MNIST L=10 时 block15 将退化为整段掩码，故 pilot 数据集选择本身影响 H2 可检验性
- 计时（U5）：{"merged_at": "2026-10-26T03:33:12+0800", "shard_timing": {}, "note": "S3 分片并行（eval_shard_runner）+ 主进程 seed1 段合并", "resume_eval_run": {"data_prep_sec": 0.0, "train_runs": {}, "eval_sec": 208.0, "total_sec": 208.1}}
