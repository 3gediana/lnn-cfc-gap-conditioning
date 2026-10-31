# 复盘台账 — 液态网络抗丢帧没接时间（CfC 基准补真实间隙条件化）

## 2026-10-26 07:3x wrap 收尾复盘（成功项：S5 续跑链跨夜窗 5 单元零损耗）

- 做对了什么（可复用路径）：「detach 长跑 + 每 epoch 原子 checkpoint + 窗口尽头发 kill 交断点 + 下一单元同命令自动 resume」链条今夜第 5 次零损耗生效（seed0_ab ep7→ep13→ep30、seed0_c ep26→ep30、seed1_ab ep1→ep30、seed1_c ep1→ep10），证据=resume 日志 + history 连续性 + kill 后 verify exit=0 三互证；「partial 判读三件套」（独立复跑脚本+ckpt 完整性+续跑路径行号级核验）8 个判读单元全部抓到真问题或证实无失实（ep13/ep14 快照滞后勘误、S2.result 丢字段回归、两处门控 bug）。
- 证据在哪：experiments/s5_ckpt_verify.py（复跑 exit=0）、experiments/full_run.log、experiments/ckpt/full_quickdraw_seed{0,1}_{ab,c}.pt、results/pilot_threearm.csv（108 行）、results/pilot_verdict.md/json、git log 3e93907 等今夜 commits、课题 STATUS/DECISIONS 全链。
- 下一个最小同类改进：「收尾三查」（ps + ckpt 完整性复验 + log 对账，≈2min）固化为 wrap 单元标准动作——本单元已实操一遍可行；下一夜窗 S5 尾部（seed1_c 收口+seed2 臂）与两候选 design 后的训练阶段直接复用同链条。
- 失败/不足项复盘（不等同方向死亡）：①N-MNIST 数据五通道全挡→F3 降级 QuickDraw（已按预注册执行、限制如实入档），结论级回 N-MNIST 的 info_need=daytime/user-assisted 不变；②排产估计带病两轮（C 臂 64s 未经实测）→ 已校准为 ab≈46-47/c≈47-48s/ep，教训=未经实测的单项估计不得进排产公式；③证书门控/快权重 10-25 用户撤回改动滞留 ≈19h 未提交→wrap 单元已补提交（证书门控含 push），教训=terminal/撤回类改动当天入库，不等「顺便」。
- 是否回写模板/技能：wrap 收尾三查 + partial 判读三件套已在课题 DECISIONS 落账；跨课题可复用部分（夜班长任务跨窗口接续模式）随 PORTFOLIO 今夜摘要留给下一班统筹。

## 2026-10-26 07:5x wrap 收尾单元#2 复盘（成功项：N-MNIST 数据墙松动、原子步骤真实收完）

- 做对了什么（可复用路径）：①「收尾三查」（ps+ckpt 完整性复验+log/进程链对账）第二次标准动作生效——本单元靠它抓到下载循环仍在飞，并一路追到 Train.zip 07:43:50 落盘，把 07:4x 判读留的「归属待核」闭环为「进程链实证+数据到手」；②新沉淀「数据三重验收法」（清单大小对账+zipfile CRC+结构解析，≈1min/包），可复用于今后任何下载型数据落地；③对外部重试循环不擅杀、只核实与记录——边界内动作，等它自然 break，避免误杀非本单元的原子步骤。
- 证据在哪：data/nmnist/{Test,Train}.zip（testzip 均 None、条目 10010/60010、60000 个 .bin 全按 5 字节整除、抽样事件解析合规）、experiments/download_nmnist_requests_20261026.log、Get-CimInstance 进程链快照（124136→42808，已退出）、s5_ckpt_verify.py 复跑 exit=0、课题 STATUS/DECISIONS 本条、PORTFOLIO 今夜摘要 07:5x 段。
- 下一个最小同类改进：N-MNIST 事件 loader 固化（5 字节记录 [x,y,p,t_lo,t_hi]、t=u16LE μs）并抽样对账（30min 验法=写 loader+读 100 个 bin 与官方 Read_Ndataset.m 口径核对；失败条件=坐标/极性/时间戳任一字段口径不符则回退人工核 Read_Ndataset.m）；info_need 正式更新交判读单元。
- 失败/不足项复盘：无新失败；遗留=时间戳 u16LE 上限（抽样文件 t 上限 65447）与 N-MNIST 标称 300ms 样本时长的关系待 loader 固化时核（若不符则疑样本截断或单位非 μs——不猜，落 loader 验法）；curl/urllib TLS 墙对该域仍存在，不得宣称墙已解。
- 是否回写模板/技能：数据三重验收法+N-MNIST 5 字节事件记录口径随本条留库；跨课题可复用部分（外部重试循环核实规程）随 PORTFOLIO 今夜摘要留给下一班统筹。

## 2026-10-27 02:1x 判读复盘（成功项：空壳 failed 回执的科学工作零损失确认 + 倒挂残留修类 + 算子优先排序）

- 做对了什么（可复用路径）：①「failed 先分类再处理」第三次生效——driver unit-notes-backfilled（trajectory 补回）+队列 failed_models+用户侧 bridge 观察三源互证，≈10 分钟定位为收尾模型抽风而非科学失败，没有把空壳回执当 stage 故障重跑；②「首轮全量复跑」纪律抓到一个真问题（verify() 两处倒挂残留）——若按差异/抽样跳过代码核验就会漏；复算脚本固化 experiments/s5_judge_710a_recheck.py（44 项，可作 S5 收口判读的复判入口，与 s3_verify_csv.py/s5_researcher_receipt_recheck.py 并列）。
- 证据在哪：experiments/s5_judge_710a_recheck.py+.txt、s5_judge_710a_ckpt_verify.txt、s5_judge_710a_regression_rerun.log、s5_judge_710a_probe_rerun.log、s5_judge_710a_probe_original.json、s5_judge_710a_verify_rerun.py+.log、results/s5_mask_convention_probe_judge_rerun.json、notes/researcher-interventions/710a1c50feff4a9ab0943e929ad06ab6.md、workflow.json S5.actions。
- 下一个最小同类改进：算子优化单元（fb-ab50d0ec9f）落 operator_bench 时，把本轮「名义 vs 实际」断言教训推广到算子级——τ 值域/梯度量级/scale-state 量级的 nominal-vs-realized 断言进 bench（30min 验法=bench 跑通+三项断言各至少一个反例 Red；失败条件=断言无法区分修前修后则验法无效、重设计断言）。
- 失败/不足项复盘：①第五单元收尾回执格式失败（status 非枚举→空壳 failed）——执行单元收尾时回执 JSON 应先自校验枚举值再输出（沉淀为执行单元标准动作建议，交模板层）；②判读单元首轮正则漏索引形式——补丁核验正则必须含 xb[..]*mask[..] 形态（已落脚本）。
- 是否回写模板/技能：空壳 failed 三源定位法+补丁核验索引正则随本条留库；跨课题可复用部分（收尾回执枚举自校验建议）随 PORTFOLIO 留给下一班统筹。

## 2026-10-31 05:2x S10 执行复盘（阶段科学交付成立：负结果按预注册落盘，非单元失败）

- 做对了什么（可复用路径）：①「先冒烟实测 s/ep 再排产」第三次兑现——11.15s/ep 实测（QuickDraw 46-58s 参考带未进公式），总投影 669s≪2700s 硬顶，一个单元跑完 smoke→6 训练→108 行评测→落表全链；②「import-not-copy+selftest 先行」——N-MNIST 适配只新增掩码 view (B,L,1,1,1) 一处，selftest 六门在训练前抓出全部机制问题（含 B=8 小样本掩码率方差误报的容差标定修正：block 条件须 B≥256 或用预注册 20% 容差）；③「逐 epoch 原子 ckpt+逐行原子落盘」第 8 次跨命令零损耗（smoke 3ep→all 同 ckpt 续跑至 10ep、verify exit=0）；④独立复算 33 项全 PASS 后才报数（s10_recheck.py），抓到自身两处问题（timing 键名误标、复算容差方差模型错）都当场修复/修正。
- 证据在哪：experiments/nmnist_threearm.py、experiments/ckpt/nmnist_seed{0,1,2}_{ab,c}.pt（verify：experiments/s10_ckpt_verify.txt）、results/nmnist_threearm.csv（108 行）/md、results/nmnist_progress.json、results/nmnist_timing.json、experiments/s10_recheck.py+.txt、experiments/logs/nm_{smoke,all,report}.log。
- 科学结论（负结果）：H1 在原文数据集 N-MNIST 复现负值——推理期真实 timespans 条件化在块状间隙下无增益（block5-30 B−A=+0.09pp，三口径 +0.09/+0.10/−0.05pp，逐种子 +0.53/+0.04/−0.29），clean 完全无损（A≡B=0.000pp，D1 同输入结构性保证）；结合 QuickDraw S5（−1.22pp）与 S7 E2（训练期激活时间通路贡献 C−A 增益 87.5%），叙事收敛为「差异不在推理期有无时间信息，在训练期有无让时间通路参与学习」；C 臂 +9.47pp 增益但 clean 逐种子门控 FAIL（0.95/0.43/0.62pp）与 S5 同型；D7 保真度好于预期（A@clean 98.12% vs 论文 99.38%，缺口 −1.26pp≤3pp 未触发 caveat）→协议差未构成保真度威胁。
- ≥3 条替代方向（各带 30min 验法与失败条件）：①输入端 gap-embedding 隔离（F2 回退路径）：C−A 含增强混杂，30min 验法=用 seed0_ab ckpt 推理期给 B 臂输入拼接恒 0 gap 位对照（结构上应≈B），失败条件=与 B 差 <0.5pp 则输入端 gap 信息无边际；②论文协议精确复刻（D7 归因第一嫌疑=协议差 units128/双CNN+BN/batch64/Cosine）：30min 验法=按 lln_nmnist.py 复刻训练 1 种子 10ep，对比 A@clean 98.12% vs 论文 99.38%，失败条件=复刻版 ≤98.12% 则协议差非缺口主因（转向数据量子集/评估口径）；③S11 QuickDraw LR step decay 已在队（跨数据集归因，~570s）：失败条件=A@clean 提升 <+0.5pp→LR 调度非 QuickDraw 保真度缺口主因，剩余嫌疑=分类头 dropout/85-15 子集；④条件触发项=B-train 臂回 N-MNIST 复演 E2（仅当 B−A 转正，本轮 +0.09pp 不触发）。
- 是否回写模板/技能：git blob 绕行中文深层路径墙（第 4 条路）+make_mask 同种子重建的协议特性（单行有效样本≈256、掩码率方差模型）+「实测 s/ep 再排产」已随 DECISIONS 05:2x 条落账；make_mask 协议特性建议回写 EV-06 协议说明交判读单元；N-MNIST L=10 训练速率（11s/ep@60000）可入跨课题排产参考。
## 2026-10-31 05:5x 判读复盘（成功项：H1 结论级证伪按预注册机械执行+归因链三解释闭合；路线 redesign 已重定义）

- 做对了什么（可复用路径）：①「判据先冻结、终判后置」链条第 4 次零争议执行——执行单元不代判 H1（交 researcher），预注册三档（≥+2pp/<+1pp/其间）跑前冻结、跑完机械输出、判读单元只核验+归因+定路线；②双数据集证伪归因链模板成型：证伪「接口有效」类假设必须依次排除复现保真度（D7 缺口 vs 论文锚点）、实现缺陷（sanity 六门）、机制归属（E2 类分离臂）三个竞争解释才可下结论级判断——本阶段三链全闭合，负结果达到可写进论文的归因完整度；③「redesign 阶段内容过期检查」新标准动作——驱动器自动生成的 redesign 阶段是上一阶段复本（prediction 照抄），本轮实测抓到（原 prediction 仍写「H1 复演两种走向」而 H1 已终判），已重定义为负结果归因探针，避免空转重跑已证伪实验。
- 证据在哪：notes/researcher-interventions/eaea7487ddfc479c83fe016c90d89c8f.md（判读全文）、experiments/s10_judge_recheck.py（独立复算）、results/nmnist_threearm.csv/md、experiments/s10_recheck.py+.txt、workflow.json（redesign/S6/H1 三处变更，deep-check 除本判读修改外与 HEAD 语义一致）。
- 科学结论（终判）：H1「推理期真实 timespans 条件化提升块状丢帧精度」双数据集结论级证伪（QuickDraw −1.22pp / N-MNIST +0.09pp，clean 均零损）；机制叙事收敛为「差异在训练期有无让时间通路参与学习，不在推理期有无时间信息」；新增可证伪候选解释=帧化 dt 量化（L=10 bin≈30ms vs 事件 µs 分辨率，约 4 个数量级损失），不由判读采信，交 redesign 次探针判决。
- 下一个最小同类改进：redesign 单元（nmnist-negative-result-probes，纯推理 ~45min）：主探针 C 臂推理期 dt 分离（判据 C_no_dt−A(block5-30)≥+5pp→训练期主导/<+2pp→查实现/其间→inconclusive）；次探针 dt 粒度响应谱（判据 dt*≥5→量化假设存活/dt*<5→证伪）；两探针共同回答「C 臂 +9.47pp 从哪来」与「H1 失败是否协议侧量化所致」，是负结果仓库打包（S6）前最后两块归因。30min 验法=seed0_c 单 ckpt 两口径 clean 冒烟（差<0.3pp）+dt 扫描 hidden 有限；失败条件=冒烟不过落 partial+断点、不硬撑。
- 失败/不足项复盘：①C 臂 clean 门控 FAIL（0.95/0.43/0.62 不全≤0.5pp）使 +9.47pp 暂不能作为有效证据——非方向死亡，转 redesign 主探针做两因素分离；②QuickDraw D7 缺口 −3.47pp 仍未归因（S11 在队）——N-MNIST 侧 −1.26pp 已排除保真度威胁，QuickDraw 侧不阻塞 H1 结论（臂间配对比较与绝对水位无关，S9 已判）；③未选方向留档（非否决）：论文协议精确复刻（units128/双CNN+BN 复刻 1 种子，边际信息量低于探针，留待 S6 前若需加强 D7 再启）、L=34 重分箱（等 dt 响应谱结果，避免盲重建 6.5GB 张量）。
- 是否回写模板/技能：双数据集证伪归因链模板+redesign 过期检查标准动作随本条留库；「先冒烟实测 s/ep 再排产」第 4 次兑现（11.15s/ep@N-MNIST L=10）入跨课题排产参考；夜班派单面=ready 阶段维持 2 个（S11+redesign），符合 fb-5103987612 验收口径（starved_ready_stages=0）。

## 2026-11-01 00:5x 课题收官复盘（S6 判读+公开推送+收线 terminal；成功收官也要复盘）

- 做对了什么（可复用路径）：①「首轮全量复跑拿证据」在收官单元兑现——判读者亲自跑 stress_gap_test.py（147/147 exit=0 + --identity 148/148 exit=0）而非只读回执/日志，打包类回执的「机械组装零新造」声称由此变成可核验事实；建议固化为 packaging 类阶段判读标准动作。②负结果仓库形态标准化=一条命令秒级复现（纯标准库零依赖）+冻结锚点 expected_verdicts.json（逐项带 provenance）+预注册门线机械输出+大白话结论+What was ruled out 5 条+诚实限制清单 8 条，达到「外人可独立复现、可引用」的交付度；九节结构可作 S6 packaging 模板参考。③公开策略执行口径=fb-4d1c1b82ec（全部公开、立项即公开、不开卡）：本课题两个公开仓落成（主课题仓=完整研究过程全记录；lnn-cfc-gap-conditioning-negative-result=负结果交付物），README 交叉链接；公开仓名冲突时「另建交付仓+记录理由」成新处置先例。
- 完结四指标：跳过率=0（S1-S11+S10-redesign 全阶段有执行+判读双记录，无跳过阶段）；重跑密度=1 次真返工（掩码 Convention 倒挂致 C 臂重训，判读 710a1c50 坐实）+2 处判读补丁（MD 逐种子报告 bug、D7 参照系引错 −2.83pp 虚增）——均为抓到的真问题，无空转重跑；卡滞天数≈3 晚全外部因素（N-MNIST SSL 数据墙→F3 降级、用户 10-29 停机一夜、P6 误闭合饿死一夜，后两项已代码级修复留账）；产物引用=公开双仓+expected_verdicts.json 冻结锚点+判读复算脚本 35+ 项（s3_verify/s5_judge/s7_judge/s10_recheck/s11_recheck/nm_probes_recheck 等）。
- 科学终局（一句话）：H1「推理期真实 timespans 条件化提升块状丢帧精度」双数据集结论级证伪；C 臂增益 87.5% 来自训练期；帧化量化（dt*=20）为协议侧候选解释带 caveat 存活；D7 两数据集缺口≤3pp 排除保真度解释。
- 下一个最小同类改进：L=34 重分箱（≈10ms/bin）加强验帧化量化假设——seed0_ab ckpt 纯推理复测 dt 响应谱饱和点是否随 bin 变细右移；30min 验法=重建 6.5GB 张量（repo/REPRODUCE.md 协议已复刻）+单 ckpt 扫 dt∈{1,2,5,10,20,34}；失败条件=dt* 不随 L 变化→量化假设证伪、机制 caveat 关闭。由后世按需立项，不占本课题路径。
- 是否回写模板/技能：收官单元「亲自跑复现入口而非只读回执」+「公开仓名冲突时另建交付仓并记录理由」+负结果仓库九节结构随本条留库；L=34 重分箱入口（协议+验法+失败条件）留给后世同型课题直接取用。

