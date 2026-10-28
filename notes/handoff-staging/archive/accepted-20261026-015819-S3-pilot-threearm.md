---
stage: S3-pilot-threearm
kind: experiment
status: partial
did: S1 六次训练全部 checkpoint 完成（A/B 共享 3 种子 + C-aug 3 种子，QuickDraw 1 万样本 2 epoch），S2 评测矩阵进行中；真实尺寸 verify 全过（manual-loop 与库 B=1 差 0.0、B>1 崩溃记录、clean A≡B=0.0）。
why: 执行 design.md §四 S1/S2 预注册三臂 pilot：块状间隙下真实 timespans（B/C）相对论文式均匀时间（A）的边际收益首测。
how: 协议逐字对齐 stress_test.py（EV-06）；A/B 共享 checkpoint 同掩码输入唯一差异 timespans；B=manual-loop+D2 编码；C=+gap 指示位+块状增强；条件×3 种子化模式跨臂配对；读表 meanpool/final/gapnb 三口径；每次训练即写 ckpt+progress（可断点续跑）。
result: N-MNIST 数据 5 通道全被 SSL 墙挡（garrickorchard Cloudflare/Mendeley EOF/PyPI EOF/HF EOF/GitHub 无资产，证据 results/fetch_assets_report.json+data/nmnist/download_report.json），按 F3 式降级用 QuickDraw（同论文协议、storage.googleapis.com 可达）。verify 4/4 过。训练 acc：A/B 臂 0.22-0.38（2 epoch 预算内）、C 臂 0.12-0.17（增强+小预算）。D7 忠实性（clean≥97%）未达——纯预算差距非实现缺陷（代码级核验+verify 为证），按 D7 断点规则续跑。评测矩阵出表后交 S4 判读。
next: 下一单元跑 `python experiments/pilot_threearm.py eval`（ckpt 已在盘，约 3 分钟）出 CSV/MD/timing，或按 D7 提高 epoch 重训（删 ckpt+progress runs 条目后 all）；N-MNIST 数据通道恢复后按原协议补测。
artifacts: [experiments/pilot_threearm.py, experiments/pilot_run.log, results/pilot_progress.json, results/fetch_assets_report.json, data/nmnist/download_report.json, experiments/ckpt/]
info_need: N-MNIST 可达镜像（garrickorchard/Mendeley/PyPI/HF 均 SSL 墙；GitHub api 可达但无 N-MNIST 资产）——需 researcher 提供免 SSL 墙的数据通道或授权改用 PhysioNet/UCI-HAR 等价协议；另 harvest 两条本课题检索（2501.15330 负结果旁证）未消化，供 S4 判读参考。
---
