---
stage: S10-nmnist-threearm-baseline-redesign
kind: experiment
status: ok
did: 跑完负结果归因两探针（纯推理 70.4s）：C 臂 ckpt 以 A 臂口径（无 dt）重评 108 行+seed0_ab 扫常数 dt 响应谱，判据机械输出+35 项独立复算全 PASS。
why: H1 已双数据集证伪，负结果仓库必须回答「C 臂 +9.47pp 从哪来」：分离训练期（块增强+gap-bit）与推理期 dt 两因素，并检验帧化量化候选机制。
how: 判据跑前冻结（eaea7487 第五节）：①C_no_dt−A(block5-30,3 种子 mean)≥+5pp→训练期主导/<+2pp→查实现落 partial/其间→inconclusive；②dt 响应谱饱和点 dt*≥5→量化假设存活/<5→证伪/平坦→inconclusive；③clean 口径切换差<0.3pp。冒烟五门不过即落 partial 不硬撑；A_ref/C_dt 与 S10 CSV 恒等自检+独立复算脚本盘上重算防口径漂移。
result: 判据①C_no_dt−A=+9.58pp（逐种子 +16.49/+6.85/+5.41）≥+5pp→training_dominant_supported：C 臂增益几乎全部来自训练期，推理期 dt 净效应 C−C_no_dt=−0.11pp≈0（E2 的 N-MNIST 确认，叙事闭合）。判据②R(2/5/10/20)=0.073/0.148/0.182/0.199 单调升不饱和，dt*=20≥5→supported：帧化量化（L=10≈30ms/bin）是 H1 失败协议侧候选解释。判据③clean 切换差 0.0000pp PASS；恒等自检 max|diff|=0.000000。冒烟五门 PASS；首跑门控 bug（锚点 apples-to-oranges）5.3s 自抓已修；108 行逐行原子落盘 65s/总 70.4s<600s 硬顶；timing 键名误标按日志校正。
next: researcher 判读本回执（两探针终判+S6-repo-package 解锁放行：解锁条件 S11 D7 归因+redesign 两探针已全部满足）；后续可选=L=34 重分箱验量化假设（30min 级，重建 6.5GB 张量）或论文协议精确复刻（备选留档）。
artifacts: [experiments/nm_negative_probes.py, experiments/nm_probes_recheck.py, experiments/nm_probes_recheck.txt, results/nm_negative_probes.csv, results/nm_negative_probes.md, results/nm_dt_response_spectrum.json, results/nm_negative_probes_progress.json]
info_need: 无
---
