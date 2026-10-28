---
stage: S3-pilot-threearm
kind: experiment
status: partial
did: S1 六次训练全部 checkpoint 完成（A/B 共享 3 种子 + C-aug 3 种子，QuickDraw 1 万样本 2 epoch），S2 评测矩阵单臂 265s 后遇硬超时，0/108 行落盘；真实尺寸 verify 全过（manual-loop 与库 B=1 差 0.0、B>1 崩溃记录、clean A≡B=0.0）。
why: 执行 design.md §四 S1/S2 预注册三臂 pilot：块状间隙下真实 timespans（B/C）相对论文式均匀时间（A）的边际收益首测。
how: 协议逐字对齐 stress_test.py（EV-06）；A/B 共享 checkpoint 同掩码输入唯一差异 timespans；B=manual-loop+D2 编码；C=+gap 指示位+块状增强；条件×3 种子化模式跨臂配对；读表 meanpool/final/gapnb 三口径；每次训练即写 ckpt+progress。
result: N-MNIST 数据 5 通道全被 SSL 墙挡（garrickorchard Cloudflare/Mendeley EOF/PyPI EOF/HF EOF/GitHub 无资产，代理 7897 亦不救），按 F3 正式降级用 QuickDraw。verify 4/4 过。训练 acc：A/B 臂 0.22-0.38、C 臂 0.12-0.17（2 epoch 预算内）。D7 忠实性（QuickDraw 等价判据≈98.6%）未达——纯预算差距非实现缺陷。评测矩阵因原实现无断点持久化+gapnb 逐样本循环（GPU 利用率 6% 主因）未在窗口内完成。researcher 02:1x 判读已落补丁（逐行落盘+断点跳过+gapnb 向量化 5021×+读表口径修复+原子写）并自验 PASS，冒烟 3 行非退化、progress 恢复原状（0/108 行）。
next: 下一单元先读 STATUS 下一步节+判读文档 179711d008e94d12ae7638998ff6da31.md，跑 G:/ai/python11/python.exe experiments/eval_patch_selftest.py 复验补丁（exit=0），再跑 python experiments/pilot_threearm.py eval 全矩阵（补丁后实测预估≈23-26 分钟；超时不丢已出行，重跑同命令续跑；CSV/MD 仅 108 行齐全后落盘）→ 收工前缩小矩阵冒烟自检（1 种子×clean×1 模式，三读口径非退化）→ 交接单过 research-handoff-gate.py 门控 → 回执交 S4-pilot-verdict 判读（带数据集降级 caveat）。
artifacts: [experiments/pilot_threearm.py, experiments/eval_patch_selftest.py, experiments/pilot_run.log, results/pilot_progress.json, results/fetch_assets_report.json, data/nmnist/download_report.json, experiments/ckpt/, notes/researcher-interventions/179711d008e94d12ae7638998ff6da31.md]
info_need: N-MNIST 免墙镜像（用户可提供；五通道+代理今夜全灭）——daytime 重试，脚本 experiments/ 可直接重跑；另 harvest 两条本课题检索（2501.15330 负结果旁证）未消化，供 S4 判读参考。
---
