---
stage: S11-quickdraw-lrdecay-retrain
kind: experiment
status: ok
did: QuickDraw 加论文 LR step decay（1e-3→5e-4@ep13→2.5e-4@ep26）重训 A/B 共享臂 3 种子×30ep，72 行评测落表，判据①机械输出=inconclusive。
why: S9 归因疑 D7 缺口（vs 论文 Table I -3.47pp）主因是 LR 调度偏离（本仓恒定 1e-3），需隔离变量复测：只加 LR 调度，其余协议不动。
how: import-not-copy 复用 S5 同代码路径（quickdraw_lrdecay.py）；selftest+冒烟双门（loss 降/A≡B 逐位相等/LR 序列）；逐 epoch 原子 ckpt 断点续跑；收工独立复算 s11_lrdecay_recheck.py 30+ 项全 PASS。
result: A@clean=93.20±0.09%（逐种子 93.08/93.24/93.29）vs S5 基线 92.30±0.86 → 增益 +0.90pp（+1.99/+0.20/+0.52）→ criterion1=inconclusive（冻结带 +0.5~+1.5pp）；clean A≡B=0.000pp PASS；A@uniform30=64.81±2.48 vs 论文 68.80 缺口 -3.99pp；D7 vs Table I 缺口 -3.47pp→-2.57pp、vs Table III 0% 列转 +0.51pp；block5-30 B−A=-1.49pp（S5 -1.22pp 同向）；train acc 0.9923/0.9964/0.9969（S5 0.9518/0.9661/0.9688）；实测 3644.9s（训练 3566.3+eval 76.4）。
next: researcher 判读：D7 归因终判（LR 至多次要因子）+inconclusive 带内预注册选项裁定（dropout 头 30min 验法或 it-ep 310 对齐）+S6 打包前保真度记账。
artifacts: [results/quickdraw_lrdecay.csv, results/quickdraw_lrdecay.md, results/quickdraw_lrdecay_progress.json, results/quickdraw_lrdecay_timing.json, experiments/quickdraw_lrdecay.py, experiments/s11_lrdecay_recheck.py, experiments/s11_lrdecay_recheck.txt, experiments/ckpt/quickdraw_lrdecay_seed0_ab.pt, experiments/ckpt/quickdraw_lrdecay_seed1_ab.pt, experiments/ckpt/quickdraw_lrdecay_seed2_ab.pt, experiments/logs/s11_lrdecay_selftest.log, experiments/logs/s11_lrdecay_smoke.log, experiments/logs/s11_lrdecay_all.log]
info_need: 论文 QuickDraw 分类头 dropout 率与每 epoch 步数 310 的 batch 口径（_repo 脚本中文深层路径间歇墙未读取，lln_10.log LR/epoch/精度已双源取证）；如开 dropout 头 30min 验法需先取该率。
---
