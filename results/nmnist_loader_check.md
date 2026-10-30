# N-MNIST 事件 loader 分布核验报告（S8-nmnist-event-loader）

- 课题：液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a
- 阶段：S8-nmnist-event-loader（2026-10-31 03:1x-03:4x lab-executor 单元）
- 判据来源：data/nmnist/README.md（位描述+文件清单）、notes/DECISIONS.md 2026-10-26 07:6x 条
  （wrap 独立分布复验：Train/1/17665.bin 652 条、p 字节 {0..4}∪{128..132}、129-132 合计
  299/652≈46%、x∈[1,33]、y∈[0,33]、t 非单调表述）、experiments/_repo/lln_nmnist.py
  （论文仓库自带 N-MNIST loader）、experiments/pilot_threearm.py nmnist 分支输入规格。
- **结论：分布与 10-26 独立复验逐项相符（锚点 6/6 项精确一致），预注册失败条件未触发；
  loader 固化完成，可训练张量已物化。** 原始数字：results/s8_nmnist_dist.json、
  results/s8_nmnist_probe.json、results/s8_nmnist_trainable_smoke.json。

---

## 1. 字节格式裁决（两种解读，先写判据后跑）

每个 `.bin` = 事件序列，每事件 5 字节。候选解读：

| 解读 | x | y | 极性 | t |
|---|---|---|---|---|
| A（40-bit 位域，README 位描述） | b0 | b1 | (b2>>7)&1 | ((b2&0x7f)<<16)\|(b3<<8)\|b4（23-bit，µs） |
| B（朴素 1+1+1+2，10-26 wrap 字面） | b0 | b1 | b2 原值 | u16LE(b3,b4) |

判据（跑前写死）：①X/Y∈[0,33]；②正确解读下 t 应为连续全程（无 u16 回绕伪影）；
③b2 直方图必须复现 10-26 实测 {0..4}∪{128..132}；④锚点文件数字与 10-26 逐项一致。

裁决证据（experiments/s8_nmnist_probe.py + experiments/s8_nmnist_check.py）：

1. **两种解读下 b2 完全相同**（字段切分不依赖字节序选择），实测直方图恰为
   {0..4}∪{128..132}（见 §4）——即 **b2 = polarity<<7 | (t>>16)**：高位是极性，
   低 7 位是 23-bit 时间戳的高 7 位（t>>16∈{0..4}，因 t<327680µs≈328ms）。
   10-26 复验看到的「p 分布 {0..4}∪{128..132}、129-132 占 46%」正是这个联合分布，
   **不是极性取值**——把 b2 当极性做布尔化「合规」判定会吞掉这一口径分歧，故本 loader
   显式拆分（极性 = b2>>7；时间戳高 7 位 = b2&0x7f）。
2. 时间戳低 16 位字节序：**b3 为高字节（大端）**。实测 anchor 文件 Train/1/17665.bin：
   大端读 t∈[768, 303173] 且 652/652 事件严格单调；小端读 t∈[3, 327466]、单调率仅
   55.6%；10-26 的 u16LE 读法（字节交换）逆序率 44.5%、t∈[3, 65447] 出现 5 次回绕——
   **10-26「t 非单调」是低位双字节字节序伪影，不是数据性质**。
3. 解读 A 与论文仓库 `experiments/_repo/lln_nmnist.py:37-40` 逐字一致
   （x=raw[0::5]、y=raw[1::5]、p=(raw[2::5]&128)>>7、
   t=((raw[2::5]&127)<<16)|(raw[3::5]<<8)|raw[4::5]）——实测与论文档位双向坐实。

**采纳：解读 A（大端低位）。** loader 实现 = experiments/nmnist_loader.py::parse_bin。

## 2. 帧堆积规则（显式定义；L 与时 Bin 无先验，以论文仓库口径为准并鲁棒化）

- **L=10**（EV-06/design.md 协议锁定；pilot_threearm.py 文档串「N-MNIST=10 bin log1p」；
  论文仓库 `NMNISTDataset(time_bins=10)`）。
- **时 Bin**：每样本按自身时间跨度等分——`t_bin=(t_max−t_min)/L`，
  `bin=min(L−1, floor((t−t_min)/t_bin))`；跨度=0 时全部落 bin 0。
  与论文 `_to_frames`（lln_nmnist.py:43-56）同规则；唯一差异：论文用 `t[0],t[-1]` 作端点
  （假设时序存储），本 loader 用 `min/max`（**不假设排序**）。全量实测
  `endpoints_eq_minmax = 70000/70000`（§4），二者在本数据集上恒等；若遇非单调文件，
  论文版会产生负 bin_idx 的 Python 负索引 silent bug，本版不受影响。
- **空间与通道**：`frames[bin, p, y, x]`（行=y、列=x，与论文一致），x/y≥34 的事件按论文
  口径丢弃（全量实测 0 条被丢弃，§4）；通道 0=OFF(p=0)、1=ON(p=1)。
- **取值**：`log1p(counts)`，float32；输出 **(N, 10, 2, 34, 34)**，与
  pilot_threearm.py nmnist 分支 `Conv2d(2,32,3,padding=1)` 输入规格一致
  （MaxPool2d(2)→17×17→Linear(32·17·17,128)）。
- **样本枚举**：按 (label, 文件名) 排序（论文用 glob 无序；排序保证种子化子集可复现）。

与 README 的两处口径分歧（如实记录、不吞）：
1. README「采样步长 100µs」**不成立**：t%100 在 0..99 上均匀分布（train 各残差计数
   2.50M±0.2%），时间戳为 1µs 分辨率；实测每样本跨度 290.9-315.3ms（均值 306.5ms）。
2. README「L=10（10 帧×100µs）/L=100（10 帧×1ms）」的定宽读法**不可复现**：样本跨度
   ~306ms，10×100µs=1ms 仅覆盖 0.3%；论文仓库实现即「每样本跨度等分 L 份」，本报告
   按此固化。不影响结论级资格（时 Bin 规则已显式定义且与论文一致）。

## 3. 样本聚合（全量 find + 逐类计数）

| split | 样本数 | 每类计数（0..9） | 事件总数 | 事件/样本 |
|---|---|---|---|---|
| Train | **60000** | 5923, 6742, 5958, 6131, 5842, 5421, 5918, 6265, 5851, 5949 | 250,316,228 | 4171.9（min 652 / max 8183） |
| Test | **10000** | 980, 1135, 1032, 1010, 982, 892, 958, 1028, 974, 1009 | 42,036,067 | 4203.6（min 742 / max 7869） |

- 与 README 清单（Train 60000 + Test 10000 个 .bin）一致；**每类不均衡**
  （Train 5421-6742，Test 892-1135）——N-MNIST 转换的固有分布，后续基准不得假设均衡类。
- 空文件 0；span=0 样本 0；x/y 越界（≥34）事件 0（无事件被丢弃）。

## 4. 每事件字段分布（全量 292,352,295 事件）

**极性（b2 高位）**：Train ON 125,019,145 / OFF 125,297,083（ON 占 0.49940）；
Test ON 20,873,622 / OFF 21,162,445（ON 占 0.49661）——ON/OFF 均衡，符合 N-MNIST 预期。

**b2 直方图（polarity<<7 | t>>16，全量；仅列非零桶）**：

| b2 | 0 | 1 | 2 | 3 | 4 | 128 | 129 | 130 | 131 | 132 |
|---|---|---|---|---|---|---|---|---|---|---|
| Train | 37,318,848 | 12,807,705 | 35,617,767 | 24,239,786 | 15,312,977 | 36,434,473 | 14,026,066 | 34,727,639 | 24,016,011 | 15,814,956 |
| Test | 6,170,970 | 2,394,938 | 5,913,403 | 3,973,867 | 2,709,259 | 5,957,176 | 2,514,017 | 5,717,841 | 3,904,202 | 2,780,372 |

Test 另有 b2=5（8 条）与 b2=133（14 条）：t≥327680µs 的极少数事件（Test t_max=336040），
Train 无（t_max=315474）。其余桶（5-127、134-255）全为 0。

**时间戳**：全局 t∈[0, 336040] µs；每样本跨度 Train 290,901-315,348µs（均值 306,500µs）、
Test 292,339-314,890µs（均值 306,197µs）；t%100 均匀（1µs 分辨率，见 §2 分歧 1）。

**单调性（「t 非单调不得假设排序」的实测核验）**：正确解读下
**70000/70000 文件严格单调、全部 2.92 亿事件 0 逆序**；`(t[0],t[-1])==(min,max)` 率
100%。10-26 的「非单调」为 u16LE 字节交换伪影（anchor 文件逆序率 44.5% vs 正确解读 0%）。
loader 仍不依赖排序（min/max 端点 + 分箱与输入序无关），鲁棒性不受结论影响。

**锚点对账（Train/1/17665.bin vs 10-26 独立复验，6/6 精确一致）**：

| 10-26 复验项 | 10-26 值 | 本单元复算 | 相符 |
|---|---|---|---|
| 事件数 | 652 | 652 | ✓ |
| p 字节取值集合 | {0..4}∪{128..132} | {0..4}∪{128..132}（直方图见上） | ✓ |
| 129-132 合计 | 299 | 299 | ✓ |
| 129-132 占比 | 299/652≈46% | 0.45859 | ✓ |
| x 范围 | [1,33] | [1,33] | ✓ |
| y 范围 | [0,33] | [0,33] | ✓ |

10-26 wrap 回执字面「p∈{0-4,128}」漏报 129-132、「t=u16LE µs 单调」两处不精确，
判读当时已勘误；本单元全量分布坐实判读勘误正确（布尔化合规判定会吞口径分歧，
抽样落分布后无可调和分歧）。

## 5. 与论文 loader 的逐位一致性

`experiments/nmnist_loader.py` 的向量化 `events_to_frames` 与论文
`_repo/lln_nmnist.py::_to_frames` 逐事件循环在 **200 个确定性抽样文件上逐位相等**
（np.array_equal，含 anchor；入口 `python experiments/nmnist_loader.py verify`，
证据 experiments/s8_nmnist_loader_verify.log）。即：预处理数值路径与论文零漂移。

## 6. 可训练张量物化 + 冒烟（输入规格坐实）

- 物化：`python experiments/nmnist_loader.py build --split all` →
  data/nmnist/cache/{train,test}_x.f32.npy（(60000/10000, 10, 2, 34, 34) float32，
  5.55GB+0.92GB，G: 盘 data/nmnist junction 下）+ {train,test}_y.i64.npy + manifest.json
  （重建命令入 manifest；data/ 不入 git）。
- 冒烟（experiments/s8_nmnist_trainable_smoke.py，真实张量+真实模型，证据
  results/s8_nmnist_trainable_smoke.json）：
  - A 臂 forward_lib：logits (128,10)、loss 2.2959 有限、梯度 abs_sum 493.2 非零；
  - B 臂 forward_ts（d2_timespans 真实 Δt）：clean/uniform30/block5-30/block15-30
    四条件全通（掩码率 0/0.294/0.297/0.25）；
  - C 臂 forward_ts_gap（with_gap_bit=True）：loss 2.2948；
  - clean A≡B 最大差 **0.0**（D1 同输入 sanity 的 N-MNIST 版成立）；
  - 30 步训练 loss 2.2959→0.9716（降 57.7%），256 样本 test 子集 acc 59.4%（chance=10%）。
- **集成注意点（留给后续 N-MNIST 三臂基准单元）**：N-MNIST 输入 (B,L,2,34,34) 下掩码
  须 view 成 (B,L,1,1,1) 才能广播（QuickDraw (B,L,5) 下 (B,L,1) 即可）；C 臂模型必须
  with_gap_bit=True；L=10 时 block15-30 退化为整段掩码（pilot_threearm.py:596 已记载的
  口径特性，非 loader 问题）。

## 7. 复现入口

```
python experiments/nmnist_loader.py verify                        # 格式/锚点/论文一致/缓存一致（exit=0）
python experiments/nmnist_loader.py build --split all             # 重建张量缓存（约 4min）
python experiments/s8_nmnist_check.py                             # 全量分布核验 → results/s8_nmnist_dist.json
python experiments/s8_nmnist_trainable_smoke.py                   # 可训练冒烟 → results/s8_nmnist_trainable_smoke.json
python experiments/s8_nmnist_probe.py                             # 字节解读裁决探针 → results/s8_nmnist_probe.json
```
（解释器 G:/ai/python11/python.exe；数据只读，未改任何 .bin/zip；缓存为派生文件可随时重建。）

## 8. 限制与下一步

- 时 Bin 采用论文口径（每样本跨度等分 L=10）；若后续要换定宽/等事件数分箱，需重跑 build
  并在基准报告显式标注（本报告已把规则钉死，防跨单元口径漂移）。
- 每类不均衡 + Test 仅 10000 样本：结论级基准的评测子集抽样须带种子并报告逐类计数。
- 下一步（交下一单元）：N-MNIST 三臂结论级基准（A/B/C × clean/uniform30/block5-30/
  block15-30 × 3 种子），复用本 loader 的 load_split + pilot_threearm 模型/掩码/timespans
  路径，门线与 S5/S7 同款预注册冻结。
