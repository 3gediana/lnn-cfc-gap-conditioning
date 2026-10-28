# 判读：S3-pilot-threearm 收口回执（unit.receipt f70d880509ed4f6fab4dd8ebfffbbbe4）

- 时间：2026-10-26T03:4x+08:00（researcher 判读单元，profile=research，夜窗终点 1792972797，本单元硬超时 1077s 内完成）
- 对象：unit.S3 lab-executor 三补单元回执（finished_at 2026-10-26T03:39:15+08:00，status=ok，verdict=inconclusive，next_action=replicate）
- 结论一句话：**回执属实 PASS（本单元对 CSV 独立复算，全部数字逐项一致）；S3 阶段收口确认；首里程碑②未达/③达成；H1/H2 因双 caveat 不足以 adjudicate → 维持 verdict=inconclusive、next_action=replicate；S4-pilot-verdict 派发要素确认并就位；不重做已收口阶段。**

## 一、回执核验（产物在盘 + 独立复算，非采信回执文字）

产物逐项实证（mtime 均为 2026-10-26 03:33，与回执一致）：

- results/pilot_threearm.csv：108 数据行+1 表头（本单元 wc/复算实证；3 种子×3 臂×4 条件×3 模式=108，无缺行）
- results/pilot_threearm.md（汇总表+三门控 sanity+门线判读+限制）、results/pilot_progress.json（verdict 块+sanity.verify_real_size verify_pass=true）、results/pilot_timing.json（resume_eval_run eval_sec=208.0）
- experiments/：pilot_threearm.py、consolidate_progress.py、merge_eval_shards.py、s3_final_check.py、s3_per_seed_numbers.py、eval_patch_selftest.py、ckpt/（6 个训练 checkpoint）
- notes/handoff/S3-pilot-threearm.md（含 03:1x 勘误保留节+本单元执行细节）；workflow.json S3→done+result（机器态，executor 提交 e18c75c/60ca6eb 后驱动器又落 S4 自动放行等改动，见第四节）

**独立复算**（本单元实跑：对 CSV 用 python 重新分组聚合，不依赖任何既有汇总）：

| 量 | 回执/MD 声称 | 本单元复算 | 判定 |
|---|---|---|---|
| 数据行数 | 108 | 108 | 一致 |
| clean A / B / C | 10.43 / 10.43 / 10.51 | 10.43 / 10.43 / 10.51（std 0.00/0.00/0.29） | 一致 |
| clean B−A / C−A | +0.00 / +0.08pp | +0.00 / +0.08pp | 一致 |
| clean A≡B 逐行恒等 | 是 | 是（9/9 行 acc 三口径全等） | 一致（比声称更强） |
| uniform30 A/B/C | 13.27/12.92/18.21 | 同（B−A=−0.35、C−A=+4.94pp） | 一致 |
| block5-30 A/B/C | 13.69/12.98/19.06 | 同（B−A=−0.71、C−A=+5.36pp） | 一致 |
| block5-30 逐种子 C−A | +4.08/+4.78/+7.24 | +4.08/+4.78/+7.24 | 一致 |
| block15-30 A/B/C | 14.42/13.69/16.20 | 同（B−A=−0.73、C−A=+1.78pp） | 一致 |
| H2 Δ（B−A 增益 block15−block5） | −0.02pp | −0.02pp | 一致 |
| A@uniform30 vs chance | z=5.97>2 PASS | PASS（口径注记见下） | 一致 |
| 实现掩码率 | ≈30% | mean realized masked_fraction=0.3013 | 一致 |
| pilot_progress.json verdict 块 | B−A=−0.0071/C−A=+0.0536/H2=−0.0002/gate=C/pass/replicate | 与复算一致 | 一致 |

口径注记（非失实，S4 判读须知）：MD 的 z=5.97 按 n=3000（单评测子集）计；本单元把 9 行×3000 合并为 n=27000 得 z=17.91——两种口径均远 >2，方向判据 PASS 不受口径影响。

## 二、本单元新发现（回执未覆盖，需带入 S4）

1. **读表口径敏感性（新）**：block5-30 的 C−A 随读表口径大幅变化——meanpool（论文口径，门控所用）=+5.36pp、gapnb（间隙邻域 K=5）=+2.64pp、final（末态）=+1.30pp。即 C 臂收益的幅度强烈依赖读表口径；meanpool 口径过线但 final 口径仅 +1.30pp（<H1 的 +2pp）。这不是实现问题（三口径都已修并经 selftest 回归），但 S4 落 verdict 时必须显式声明口径，且「收益有多大」的结论应带口径敏感性 caveat。B−A 在三口径下均为 ≈0 或负（−0.71/−0.29/−0.04pp），结论不受口径影响。
2. **C clean 逐种子**（新）：seed0 −0.23pp / seed1 +0.47pp / seed2 +0.00pp——C clean 降幅 mean +0.08pp ≤0.5pp 过线，但逐种子散布 ±0.47pp 已贴近 0.5pp 门线；seed1 实为升幅。S5 全量复测时此项需重新核。
3. **机器态链**（新，代码级定位）：workflow.json 工作区里 S3→done 之后的两处改动非 executor 手写——驱动器 research-workflow.py `apply_result`（:481-500）按回执 next_action=replicate **自动创建**了 "S3-pilot-threearm-replicate" 空阶段（kind=experiment、role=executor、无 actions/inputs/outputs、status=ready），`promote_unblocked_stages`（:277-298）把 S4 gated→ready（S4 显式 depends_on=[S3] 且 S3 done）并记 lessons[stage_released]。这两处改动在 executor 最后两个 commit（e18c75c/60ca6eb）之后落盘，目前未提交。
4. **重复/空跑派发风险（新，已处置）**：`ready_stages` 按 stages 列表序取 ready[0]。当前 ready=[S4-pilot-verdict(idx3), S3-pilot-threearm-replicate(idx7)] → 下一 tick 派 S4，正确。但 S4 完成后：S4 回执 next_action 若为 replicate，`apply_result` 会再自动建 "S4-pilot-verdict-replicate"（同类空阶段）且 S5 无 depends_on 不会被自动放行（保持 gated 等 researcher 放行）→ ready[0] 将落到空复跑阶段，派发出无动作指令的实验单元（ vague 单元风险）。处置：本单元按 00:5x 先例（S2-pilot-gate-checks-continue 同型关闭）把 S3-pilot-threearm-replicate 置 done+result（superseded：replicate 执行路径=S5-full-protocol）；S4 回执判读单元须同型关闭 S4-pilot-verdict-replicate（已写入 STATUS 备忘）。

## 三、判读与拍板（S4 判读预览的完整数据确认，不代判最终 verdict）

- **S3 回执属实 PASS**：108/108 行+四契约产物+双路径互证+selftest exit=0 均有盘上证据；03:1x 预览与完整数据差异（C−A +4.90→+5.36pp、seed2 +7.06→+7.24、B−A −0.67→−0.71pp）已按完整数据勘误，回执本身用的就是完整数据，无失实。
- **首里程碑**（admission.first_milestone）：①（ncps 最小前向/U2）此前已满足；**② A 臂 clean≥97% 未达**（10.43%=chance 级，A/B 输出恒定类=pilot 2-epoch 纯预算缺口，verify 4/4+代码级核验证明非实现缺陷）；**③ 三臂表 CSV+MD 达成**（108 行+汇总+三门控 sanity）。
- **H1**：B−A=−0.71pp 在噪声内（σ≈0.55pp/格；F1 字面条件「B−A<+1pp 且 clean 不受损」对 B 臂成立），但 C 臂保守存活门控先触发（block5-30 C−A=+5.36pp、逐种子 +4.08/+4.78/+7.24 一致、C clean 降幅 +0.08pp≤0.5pp，gate_pass_arm=C）——按 D3 预注册语义以门控出口为准，**H1 在 pilot 层不足以 adjudicate**（C−A 含增强训练混杂+chance 级基数+读表口径敏感，三条都不构成机制证据）。
- **H2**：Δ=−0.02pp 不成立（B−A 增益 block15 −0.73pp ≤ block5 −0.71pp）；附带：C 臂 block15−block5=−2.85pp，收益随块长下降，与 H2 预测方向相反（C 臂归因细化归 S5）。
- **verdict=inconclusive、next_action=replicate 维持**：负结果分支不启动（chance 级基数上的臂差不构成机制证据，F1 字面触发被 C 臂门控先覆盖 per D3 预注册语义）；replicate 的执行定义=S5 全量协议（30 epoch 全量数据保真度复现+N-MNIST 结论级基准+E2 B-train 对照臂）。
- **双 caveat 必带**：①QuickDraw 数据集降级（N-MNIST 五通道 SSL 墙+代理 7897 全灭，DECISIONS 2026-10-26 02:1x 正式拍板；QuickDraw L=100 使 block15 字面化）；②D7 保真度缺口（A@clean=10.43% vs 论文 Table III QuickDraw clean≈98.6-98.7%）。

## 四、机器态落账（本单元实做）

- workflow.json：S4-pilot-verdict 充实派发字段（role=verifier 显式化、estimate_min=30、inputs 增补 progress/timing/handoff/判读文档、actions 写入判读要点+双 caveat+建议默认 replicate→S5、note 更新为完整数据口径）；S3-pilot-threearm-replicate 置 done+result（superseded 说明+指向本判读文档）；lessons 追加本条判读记录；updated_at 更新。executor 未提交的两处驱动器自动改动（S3.result 回执同构化+S4 放行+S3-replicate 创建+feedback jsonl S3 行）随本单元一并提交（git diff 语义级对账：除上述外无其他内容差异，Unicode 转义形态差异无害）。
- STATUS.md：阶段/最近更新/下一步三行更新+新增本节判读确认。
- notes/DECISIONS.md：追加 2026-10-26 03:4x 判读条。
- 看板卡 t_f6e7bac5：本 profile 无 kanban 工具（research/_state 无 kanban 状态文件、scripts 全库无入口，与历次判读一致），按先例记账留给带 kanban 工具的统筹/执行单元。

## 五、下一步派发要素与 researcher 唤醒点（已确认可执行）

- **S4-pilot-verdict**：workflow.json 中 status=ready、depends_on=[S3-pilot-threearm]（done）满足 → 由驱动器 workflow 分支自动派发（`_select_next_unit`：workflow_units 优先于任何队列项，且会把该项目全部手写队列单元剔除——**故本判读 next_units=[]，不手写 S4 队列单元**，00:5x/01:0x 同型先例）。派发参数：kind=analysis → role_for_stage 回落 ROLE_BY_KIND[analysis]=verifier → profile=**lab-verifier**（registry 已注册，openrouter-rotator 路由在位，reasoning=xhigh）；estimate_min=30；依赖全在盘（CSV/MD/progress/timing/handoff/design.md §五/本判读文档/DECISIONS 双 caveat 条）。
- **S4 完成后**：S4 回执（verdict 落 results/pilot_verdict.md/json）到达 → researcher-event 判读单元唤醒；该单元须：①按 S4 verdict 放行 S5-full-protocol（gated→ready，S5 无 depends_on 不会被自动放行，必须人工/判读落账）；②关闭驱动器自动创建的 S4-pilot-verdict-replicate 空阶段（同 00:5x/本单元先例）；③若 verdict 转向 redesign/负结果分支，按预注册走文档单元。
- **S5 前置提示**（给 S5 派发单元）：N-MNIST 免墙镜像仍缺（daytime/user-assisted info_need），S5 结论级基准需要；experiments/ 数据获取脚本在位可直接重跑；QuickDraw 全量数据已在盘（data/quickdraw/）。
- researcher 唤醒点汇总：S4 回执到达（pilot_verdict.md/json→放行 S5+关闭自动空阶段）或 S4 硬失败。

## 六、复盘（成功也要复盘）

- 可复用路径：「独立复算对账」模式再次零成本抓到全部数字级真相（本次 12 项全对，且新抓到读表口径敏感性——只看 MD 汇总表发现不了，因为 MD 只列 meanpool 口径）；「apply_result/promote 机械放行会造空阶段」的模式本次完整走通（S3-replicate），处置先例（00:5x S2-continue）直接套用，判读成本 <3 分钟。
- 下一个最小同类改进：S4 verdict 落盘时若 next_action=replicate，其回执会被 apply_result 自动建 S4-pilot-verdict-replicate 空阶段——S4 阶段 actions 里已无法阻止（驱动器行为），但 S4 判读单元的检查清单可固化为「回执 apply 后必查 stages 尾段有无新空阶段+ready[0] 是否指向有动作的阶段」；另：判读文档的复算脚本可沉淀为 experiments/s3_verify_csv.py（本次是内联 python，30 秒成本，值得固化为 S5 复判入口）。
