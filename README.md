# 液态网络抗丢帧没接时间-cfc基准补真实间隙条件化-4a1c4c0a

> 每晚自动快照仓库（`ship-snapshot.py`）。人写内容随便改，脚本只在文件不存在时生成这个骨架。

## 结论

- 当前结论：**待定（本项目尚未收口）**
- 依据：results/s5_mask_convention_probe.json, results/s5_mask_convention_probe_judge_rerun.json, results/u2_probe.json

## What was ruled out

- 见 `notes/JUDGMENT.md` 与 `snapshots/`；证伪/停止时须在此写清排除了什么

## 怎么复现

```
python experiments/<entry>.py   # 见 experiments/ 下的入口
```

## 结构与产物

- `results/` 实验/分析结果（json / md）
- `snapshots/` 每夜快照说明（`night-YYYYMMDD.md`）
- `notes/` 判读、决策、交接单（内部用）

## 已知限制

- 自动快照只记录「做了什么、产出了什么」，不判断价值；判断见 notes/JUDGMENT.md
