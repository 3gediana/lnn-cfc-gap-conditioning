---
stage: S8-nmnist-event-loader
kind: experiment
status: ok
did: 固化 N-MNIST 事件 loader（experiments/nmnist_loader.py）：5 字节 40-bit 位域解析+每样本跨度等分 L=10 时 Bin+log1p 帧堆积，物化 (60000/10000,10,2,34,34) 张量到 data/nmnist/cache/，全量分布核验与 10-26 复验对账。
why: S5/S7 结论均在 QuickDraw 降级数据集上取得（N-MNIST SSL 墙已于 10-26 解除、数据全量在盘）；H1/H2/E2 回原文数据集的结论级复演需要可复现、口径钉死的事件 loader 作数据前置。
how: 两种字节解读先写判据后跑（X/Y∈0-33、t 全程无回绕、b2 直方图复现 10-26、锚点 6 项逐位对账）；与论文仓库 experiments/_repo/lln_nmnist.py:37-40/43-56 双向坐实，向量化 vs 论文逐事件循环 200 文件 np.array_equal 逐位一致；t 不假设排序（min/max 端点+分箱与输入序无关，实测全量 70000/70000 文件单调 0 逆序）；冒烟=真实张量进 pilot_threearm nmnist 分支模型 A/B/C 三臂+30 步训练。
result: 格式=x=b0/y=b1/p=(b2>>7)&1/t=((b2&0x7f)<<16)|(b3<<8)|b4（µs 低位大端）；10-26「p 字节 {0..4}∪{128..132}」=b2=polarity<<7|(t>>16) 联合分布、「t 非单调」=u16LE 字节交换伪影。全量：Train 60000（每类 5421-6742 非均衡）/Test 10000、292,352,295 事件、ON 占比 0.4994/0.4966、t∈[0,336040]µs、样本跨度 290.9-315.3ms、空文件 0、x/y≥34 事件 0；锚点对账 6/6 精确一致（652 事件/299=45.86%/x[1,33]/y[0,33]），预注册失败条件未触发。loader verify exit=0 ALL PASS；张量 5.55GB+0.92GB 一条命令可重建；冒烟 clean A≡B=0.0、30 步 loss 2.2959→0.9716（降 57.7%）、子集 acc 59.4%。README 两处口径分歧记录不吞（100µs 步长不成立、定宽 L 不可复现）。
next: 交 researcher 按 stage next_condition 立 N-MNIST 三臂结论级基准阶段（H1 原文数据集复演）：复用 load_split+pilot_threearm 模型/掩码/timespans 路径，门线与 S5/S7 同款跑前冻结；集成注意点=掩码 view (B,L,1,1,1)、C 臂 with_gap_bit=True、L=10 下 block15-30 退化整段掩码（已知口径特性）。S9-fidelity-gap 维持 ready 由驱动器派。
artifacts: [experiments/nmnist_loader.py, results/nmnist_loader_check.md, experiments/s8_nmnist_probe.py, experiments/s8_nmnist_check.py, experiments/s8_nmnist_trainable_smoke.py, results/s8_nmnist_dist.json, results/s8_nmnist_probe.json, results/s8_nmnist_trainable_smoke.json, experiments/s8_nmnist_build.log, experiments/s8_nmnist_check.log, experiments/s8_nmnist_trainable_smoke.log, experiments/s8_nmnist_loader_verify.log, data/nmnist/cache/manifest.json]
info_need: 无
