<!-- dossier:seed:start -->
# 项目档案｜液态网络抗丢帧没接时间：CfC基准补真实间隙条件化

- 立项日期：2026-10-25
- 立项理由：用户 2026-10-24 点名「液态网络落地应用：只做别人论文里一个具体缺口的小改进，产出能放 GitHub 的小仓库」。2605.27467（JCSSE 2026，代码/日志全开源）刚给出「LNN 比 LSTM 抗丢帧」的部署级证据，正是落地选型会引用的那种结论；但全文核验发现它的压测是均匀随机丢帧（0/30/50/70% 推理期掩码），时间信息从未进 CfC 的原生时间输入——宣称的连续时间优势，恰好在最能兑现它的场景（成段丢失、不规则采样）没被接上。这是一个可指认的已发表缺口：补上它，正结果＝给「液态网络在真实传感器失效下更稳」补齐缺失证据，直接改进边缘/临床选型依据；负结果＝其优势主要来自零填充的隐式插值而非时间机制，同样修正社区叙事。改进动作是纯模块级（换时间条件化方式），无新数据集、无新架构。
- 目的：回答「在 JCSSE 2026 公开的 CfC-vs-LSTM 鲁棒性基准（arXiv:2605.27467，代码开源）上，把推理期丢帧从「均匀随机丢帧＋时间信息不进模型」升级为「变长块状间隙＋真实经过时间」，并把每步真实 Δt 喂给 CfC 原生 timespans 接口（论文原设定把 time-delta 仅当普通输入特征、丢帧后时间仍按均匀网格处理）：原生时间条件化在块状间隙下比论文原设定多救回几个点的测试准确率，干净数据上付出多少代价？」；得到答案后，要能说清这个方法或机制在什么条件下可信、代价是多少。
- 研究问题：在 JCSSE 2026 公开的 CfC-vs-LSTM 鲁棒性基准（arXiv:2605.27467，代码开源）上，把推理期丢帧从「均匀随机丢帧＋时间信息不进模型」升级为「变长块状间隙＋真实经过时间」，并把每步真实 Δt 喂给 CfC 原生 timespans 接口（论文原设定把 time-delta 仅当普通输入特征、丢帧后时间仍按均匀网格处理）：原生时间条件化在块状间隙下比论文原设定多救回几个点的测试准确率，干净数据上付出多少代价？
- 可证伪预测：待补充（进入设计阶段时写清楚）。
- 失败条件：未知/待定
- 最小可判别实验：pilot（30 分钟见第一组数）：N-MNIST 沿用论文预处理（10 个时间 bin、log(1+count)），hidden=128 CfC（ncps），1 万样本子集训练 1-2 epoch，然后推理期 30% 块状丢帧（块长 5 帧、3 种块模式）跑三臂对照：A＝论文式（丢帧置零/紧缩重索引、时间按均匀网格）、B＝零填充＋真实 timespans（原生时间条件化）、C＝真实 timespans＋可学习 gap 指示位（输入端修正项）。第一组数＝三臂 test acc 一张表。判据（3 种子、30 epoch 全量，过门线）：30% 块状间隙下 B 或 C 相对 A 的 test acc 提升 ≥2pp，且干净数据降幅 ≤0.5pp；次判据＝块长 5→15 收益单调增。失败条件（命中任一即按指明路径转向，不硬撑）：①B/C 相对 A 提升 <1pp 且干净精度不降——时间条件化无边际收益，负结果落盘，转「多种子复现＋显著性」文档单元兜底该论文 G3 缺口（单次训练无方差）；②ncps 0.0.7 与 1.0.1 timespans 行为不兼容、cell 内改造成本超出小改进边界——改走输入端 gap-embedding 修正项路径；③pilot 两轮跑不出第一组数——降级 QuickDraw 子集或 hidden 减半。产物＝独立小仓库：fork 论文协议说明 + stress_gap_test.py + README（中文大白话）+ 结果表 CSV/MD，可复现入口一条命令。
<!-- dossier:seed:end -->

## 当前快照（系统按项目事实维护）
- 当前阶段：active / S5-full-protocol 第七单元回执判读（2026-10-28T03:1x researcher，unit.receipt 5c20248f062940c08df8dc0fefa7b729，执行单元 commit 311896b；判读全文 notes/researcher-interventions/1f338cdbe2fb4625a65c8285b8c6179f.md）：partial/checkpointed 属实 PASS、零失实（首轮全量独立复跑）→ S5 维持 ready，第八单元（seed2_c ep10 续跑+108 格评测+结论级表落盘）由驱动器自动派。①独立复跑（本单元实跑，证据 experiments/s5_unit7_judge_ckpt_rerun.txt）：s5_ckpt_verify.py exit=0 六 ckpt 与回执逐位一致（seed0_c/seed1_c 30/30 acc 0.8907/0.8898 size 3034059、seed2_c 9/30 acc 0.8497 size 3032907 history 连续+opt 在盘、ab 三臂 0.9518/0.9661/0.9688 size 逐一未动、progress runs=6/eval_rows=0/verify_pass=True）；full_run.log 逐行对账（seed1_c ep30 acc 0.8898@1735s、seed2_c 末行 ep9 acc 0.8497@508s）与 ckpt epochs_done=9 三方互证、快照滞后规则无触发；代码级核验=Convention 修正在位（full_protocol.py:180 xb*(1.0-mask)）+skip/resume 逻辑（:617-636）确认下一单元自动跳过 5 个 30/30、从 seed2_c ep10 无损续+eval 门（:658-674）未齐拒评；git HEAD=311896b 工作树干净；ps 无本课题训练残留（sibling 58b37930 physionet 下载 pid 478 03:06 仍在飞=速率归因佐证）；CSV/MD 仍为 10-27 作废值未提前落表；workflow S5=ready 且无新增空 continue 阶段。②科学意义：C 臂修正 Convention 训练精度阶跃 0.6885/0.7144→0.8907/0.8898（+20pp 级）=倒挂 bug 修复有效性的训练侧直接证据（与第五单元 T1/T6 评测侧证据互证）；D7 仍不宣称（108 格落表前）。③排产修正（第三速率带）：C 臂本轮 56.4-57.9s/ep vs 历史 46-53s/ep 带 +9~26%（均值约 +18%），归因=sibling 下载 --workers 32 CPU 争抢（GPU 单租户非争抢）；下一单元 21ep≈20min+评测≈167s+落表≈23-25min（下载若结束回带则更短，开工实测复核）。④机器态：S5-full-protocol 维持 ready（partial 执行态不改阶段状态）；S5.result=第七单元 partial 回执+judged_by/checkpoint_unit 标注；S5.actions 刷成第八单元语义、estimate_min 75→30（剩余量远低于 92min 硬顶、无需拆 continuation，fb-f591a1594c 核对通过）；lessons/updated_at 落账；next_units=[]（第八单元已由驱动器武装=night-queue resume attempts=1+partial_receipt 指针，workflow ready 每 tick 现渲染指令、手写拒收）；路由偏差显式记录（fb-baf547df25：kind=experiment 不在 GPT 路由集合 {proof,design,analysis}，按 stepfun 主+rotator 兜底）；唤醒点=第八单元回执（第 2/3 次 partial 机械确认不派判读）或训练齐+108 行 CSV/MD 落盘（S5 收口判读）或硬失败。⑤复盘：detach+原子 ckpt 跨单元无损接续第八次生效；主动 kill 交断点模式第五次；新教训=开工三查扩展为「ps 全核 G:/ai 进程归属」防速率归因延迟一个单元——
- 下一步：S5-full-protocol 已放行 ready（04:1x 判读）——首单元=QuickDraw 全量 30 epoch × 6 训练保真度复现主线（A/B 共享 3 种子+C-aug 3 种子，D1-D3 臂语义与 pilot 一致；训练路径复用 experiments/pilot_threearm.py train 改 full 数据+epoch=30，逐次 checkpoint 落 experiments/ckpt/，跑不完写断点；训练齐后按既有 eval 断点续跑补 108 格同协议评测矩阵）。N-MNIST 仍墙（免墙镜像 daytime/user-assisted info_
- 阻塞：无/未记录
- 最近结果：判定 inconclusive；发现 先独立复算（37 项 exit=0）再下判：首里程碑②未达③达成，H1=inconclusive（C 臂机械门控 pass 但 chance 级基数+增强混杂+读表口径敏感不构成机制证据），H2=falsified，verdict=inconclusive、replicate=S5-full-protocol，负结果分支不启动；S5 放行与 S4-pilot-verdict-replicate 空阶段关闭留给 researcher 判读单元（已写入 STATUS/DECISIONS/交接单）。
- 关键指标：尚无

## 决策要点（最近记录）
- 2026-10-26 05:1x 判读（unit.receipt d800137bd92245b298617229d4fff67f，S5-full-protocol 续跑链第二单元 partial/checkpointed，执行单元 6080015e，driver 实测 duration 444.7s；判读全文 not
- 2026-10-26 06:1x 判读（unit.receipt 0145909001de4f48a3eff7ddaec8c035，S5-full-protocol 续跑链第三单元 partial/checkpointed，执行单元 c7d8d768，driver 实测 duration 2272.5s；判读全文 no
- 2026-10-26 06:5x（unit.S5 lab-executor，S5-full-protocol 续跑链第四单元，status=partial/checkpointed，unit proc_9862b9502b6f/winpid 1064，06:15:44 起）：续跑链再推进一个 checkpoint 单元
- 2026-10-26 07:0x 判读（unit.receipt，S5-full-protocol 续跑链第四单元 partial/checkpointed，执行单元 proc_9862b9502b6f/winpid 1064，driver 实测 duration 2422.1s、api_calls=43，commit
- 2026-10-26 07:3x（wrap 收尾单元，stage=wrap；窗口剩余≈41min<NIGHT_UNIT_TIMEOUT 2297s）：拍板=不启动 S5 第五执行单元，断点交下一夜窗/白天。依据：①wrap 指令明文「不开新实验、不启动长任务」；②driver 07:18:40 实测已改派 wrap 单
- 2026-10-26 07:4x 判读（unit.receipt 901f94afb0814c7895078b2715c9dcf7，_portfolio wrap 收尾单元，unit 11646bc337674b3496a37160af54310d，finished_at 07:30:04；判读全文 _state/re
- 2026-10-26 07:5x（wrap 收尾单元#2，stage=wrap，unit 5b97ab0a216d471691b237b806333629/run e836872f78b444ceb6932acc58eafaf1；窗口剩余≈15min，按指令不开新实验不启动长任务）：N-MNIST 数据全量落盘+三重校
- 2026-10-26 11:0x 白天推进会·上午场（researcher，收夜班产出；本场零实验零重跑，只判读+确认派发路径）：夜窗 00:05-08:01 全链 20 个 unit-done 回执判读确认——夜班 9 个判读单元已逐条独立判读（selftest 复跑/s5_ckpt_verify.py 复跑/s3_
- 2026-10-27 01:3x（S5-full-protocol 第五单元，lab-executor，run 6e9acd73c626431abd4f28ac2c49df9a）：拍板=掩码 Convention 倒挂 bug 确认+修正+S5 本轮评测数值作废（partial，不硬撑不缩数据）。事实链：本单元训练 6
- 2026-10-27 03:2x 判读（unit.receipt c74da1aa7b4347f9b1c270f191d3b9a8，S5-full-protocol 第六单元算子优化先行 ok 回执，执行单元 716807f799aa433683a28163397d3c90，02:30:14-03:00:00，comm
- 2026-10-28 02:5x（S5-full-protocol 第七单元，lab-executor，run 5c20248f062940c08df8dc0fefa7b729，status=partial/checkpointed）：C 臂按修正 Convention 从零重训 2/3 收口+seed2_c ep9 
- 2026-1
