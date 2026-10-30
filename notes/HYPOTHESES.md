
## [验证中] H1: N-MNIST 协议下, 推理期 30% 块状间隙(块长5)时, 真实经过时间经 CfC 原生 timespans(B臂) 相对论文式均匀时间(A臂) 提升 test acc >=2pp(3种子mean), 且 clean 降幅 <=0.5pp
- 立论依据：CfC 闭式解时间显式(EV-08); 被改进对象从未传 timespans(EV-02+EV-06); 块状间隙使『间隙宽度』成为均匀丢帧中没有的真实信息量
- 可测量预测：B-A(block5-30) >= +2pp mean±std; B@clean 与 A@clean 差 <=0.5pp; clean 下 A≡B 数值一致(<0.1pp) 作为语义自检
- 失败条件：B-A < +1pp 且 clean 不受损 → pilot 层面证伪, 走负结果分支(转向路径①)

## [驳倒] H2: 真实时间条件化收益随块长增大而单调增大
- 立论依据：间隙越长, 均匀网格假设失真越大, 真实 Δt 信息增量越大
- 可测量预测：block15 的 B-A 增益 >= block5 的 B-A 增益 (mean 意义)
- 失败条件：block15 增益 <= block5 增益 → 次判据不成立, 收窄机制解释但不单独杀方向

- 状态变更→验证中：QuickDraw 结论级证伪（S5 判读 73fb33f2 2026-10-31：block5-30 B-A=-1.22pp 逐种子 -1.73/-2.42/+0.50、clean B≡A=0.00pp，预注册证伪条件成立）——但 QuickDraw 为 F3 降级数据集，预注册计划要求结论级回 N-MNIST 原文数据集复演；S10-nmnist-threearm-baseline 已立项（gated 待 S9 判读后放行），H1 在 N-MNIST 上重新进入验证

- 状态变更→驳倒：QuickDraw 结论级（S5 判读 73fb33f2）：Δ=+0.417pp 字面证伪条件不触发但两档增益均负（科学空洞）；且 N-MNIST L=10 下 block15-30 退化为整段掩码（pilot_threearm.py:596 已知口径特性），H2 在原文数据集上不可检验 → 维持驳倒不再复验
