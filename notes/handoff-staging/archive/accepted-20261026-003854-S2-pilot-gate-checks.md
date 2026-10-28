---
stage: S2-pilot-gate-checks
kind: experiment
status: ok
did: 落盘并实跑 ncps 最小前向四断言探针（terminal G:/ai/python11/python.exe，torch2.10+cu128/ncps0.0.2，CPU/float32/seed0，1.71s）：四断言 4/4 过，U2 关闭，D2 主语义保留、F2 未触发；三产物与 workflow/STATUS/DECISIONS 机器态同步落盘。
why: S0 是首里程碑①与 S3 放行前置：U2（ncps timespans 行为未实测）不关，S3 的 B 臂实现路径与 clean A≡B sanity 都缺依据，pilot 有实现伪影风险（E4）。
how: 按 design.md §四 S0 逐字规格写探针、判定式先写后跑：①None vs 全1；②dt=0 单步+零输入 20 步迭代+间隙模拟（有界/收缩/有限=记录通过）；③1→6→1 多步+单步 ts 扫描单调性；④dt 0..16+混合+三间隙全有限；附加实测库 API 边界并验证 manual-loop 与库逐样本一致。
result: 四断言 4/4：①None≡全1 恒同（max diff 0.0）；②dt=0 不冻结但有界收缩（1.0931→0.0006，|h|max=0.266）无 NaN，回退未触发；③输出序列 max diff 0.4155、58% 步改变、单调比例 1.0；④全有限。D2 保留，零填充 vs 紧缩终态差 1.02e-05。新实测：ncps 0.0.2 B>1 传 timespans 崩溃→manual-loop 验证（差 3.28e-07，反向有限）。U4：元数据通道占坑 0 命中、引文双通道复确 0，全文通道 SSL 受阻维持 narrowed_open。
next: researcher 判读 S2 回执，按 admission.first_milestone ①②③+design.md §五门线裁定 S3 放行（①已满足）；S3 按 entry_conditions 执行：B/C 臂 manual-loop 或 B=1、保留 clean A≡B<0.1pp sanity、读表兼记末态与间隙邻域均值、真实尺寸复验 manual-loop。
artifacts: [experiments/u2_timespans_probe.py, results/u2_probe.json, results/gate_checks.json, workflow.json, STATUS.md, notes/DECISIONS.md]
info_need: ①2510.07578/NIALIM 全文（全文通道恢复后定向扫关 U4，F4 触发器保留）；②ncps 0.0.7 源码（比对论文版 timespans 行为，PyPI/GitHub raw 通道 SSL 受阻未做成）；③harvest 待消化条目中如有「LNN×块状间隙×timespans」同型工作请判读（INDEX digested=true 直接用）。
---
