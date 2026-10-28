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
