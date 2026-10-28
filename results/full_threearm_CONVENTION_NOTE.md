# full_threearm.csv/md Convention 倒挂作废说明（2026-10-27T01:3x）

**状态：results/full_threearm.csv 与 results/full_threearm.md（2026-10-27T01:2x 落表）
全部数值作废（superseded），保留作历史证据，不得引用为 S5 结论。**

## Bug 事实

预注册语义（design.md §4.0 D2/D4、EV-06）：`mask=1` = 该帧被掩码（零填充），
掩码帧 dt=0、间隙后首真实帧 dt=gap+1，条件名 block5-30/uniform30 期望掩码率 30%。

实现（experiments/pilot_threearm.py `eval_arm_condition` 与 C 臂训练、
experiments/full_protocol.py `train_one_full` C 臂）用了 `xin = xb * mask`
——mask=1 的帧被**保留**、mask=0 的帧被**清零**，与预注册完全倒挂：

- clean（mask=0）→ 输入 100% 帧被清零 → 任何模型都是 chance；
- uniform30/block*-30 → 实际清零 ~86%（名义掩码 30% 的倒挂钩：实际零填充 ≈70%）；
- d2_timespans 的 ts=0 落在被保留帧而非被清零帧，违反 D2「掩码帧 dt=0」。

## 决定性证据（experiments/s5_mask_convention_probe.py，exit=0）

| 项 | 结果 |
|---|---|
| T1 ckpt 直推 clean test（不经掩码管线） | acc=0.9160（模型完好） |
| T2 ckpt 直推 train 子集 | acc=0.9468（对齐训练日志 0.9518） |
| T3 现管线 eval_arm_condition A@clean | meanpool=0.0962（chance，复现落表值） |
| T4 clean 条件下 xb*mask 后被清零帧占比 | 1.0000（uniform30 0.8631/block5 0.8579/block15 0.8673） |
| T5 d2_timespans(mask=1@t=3) | ts=[1,1,1,0,2,1,1,1] → ts=0 落在 mask=1（被保留）帧 |
| T6 修正 Convention 后 A 臂（n=2048, seed0） | clean 0.9160 / uniform30 0.6138 / block5-30 0.6431 / block15-30 0.6978 |

落表 CSV/MD 中的 A@clean=9.56%、「掩码越重 meanpool 精度越高」
（9.6%→15.6%→25.8%→30.9%，实为保留帧连续块越长信号越完整）、C@uniform30=60.6%
均为该 bug 假象；verdict 块（decision=falsified_negative_branch）作废。

## 影响面

1. **本单元 full_threearm.csv/md**：作废（本文件即为标注）。
2. **S3/S4 pilot 产物**（results/pilot_threearm.csv/md、pilot_verdict.md/json）：
   同一函数同法计算，**同为倒挂 Convention**——pilot「A/B 恒定类」部分为 clean
   全零输入假象（非纯粹训练不足）、C 臂实际零填充 ~70% 而非 30%。
   S4 verdict=inconclusive/replicate 的数值基础需按修正 Convention 重算后交
   researcher 复审；本执行单元不代改 S4 判词。
3. **A/B 臂 full ckpt 不受影响**：干净训练不经掩码管线（T1 0.9160 为证），
   full_quickdraw_seed{0,1,2}_ab.pt 继续有效。
4. **C 臂 full ckpt 作废**：倒挂 Convention 下训练（输入/gapbit/ts 与预注册反向），
   已移至 experiments/ckpt/superseded_inverted_mask_20261027/ 保留证据，
   progress full_progress.json 的 eval_rows/verdict 已清空（stale 数据），
   下一单元重跑 `full_protocol.py all` 将自动重训 C 臂 3×30ep 并按修正
   Convention 重算 108 行落表。

## 修正（experiments/s5_mask_fix_regression.py R1-R3 全 PASS，exit=0）

3 处 `xb * mask` → `xb * (1.0 - mask)`：pilot_threearm.py
`eval_arm_condition`（eval 侧）、pilot_threearm.py `train_one`（C 臂）、
full_protocol.py `train_one_full`（C 臂）。回归：R1 修正后 A@clean=0.9160
（原 0.096）；R2 A@block5-30=0.6431 且 masked_fraction=0.3059；
R3 C 臂训练清零率（原始非零帧中）=0.2962/0.2911≈0.30、gapbit=0.2984、loss 有限。

## 排产修正（实测）

本单元 eval 108 行 167.3s（s5_eval_cost_probe 的 3827s 估计测的是补丁前
d2_timespans CPU 循环路径 867ms/batch；full_protocol 向量化补丁使评测加速 ~23×，
该估计项出清）。训练速率实测：seed2_ab 48.0s/ep、seed2_c 48.5s/ep、seed1_c
52.3s/ep（本单元 20ep 1046.7s）——均在 46-53s/ep 带内，无新 >20% 偏差，
维持既有排产校准。C 臂重训 3×30ep≈72min+eval≈3min≈75min < 单元硬超时 90min，
一个 checkpoint 单元可完成 S5 收口。
