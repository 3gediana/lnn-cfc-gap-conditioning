import sqlite3, time

db = r"D:\hermes-data\kanban\boards\research\kanban.db"
c = sqlite3.connect(db)
row = c.execute("select id,title,status from tasks where id='t_f6e7bac5'").fetchone()
print("card:", row)
assert row and row[0] == "t_f6e7bac5"

body = ("2026-10-27 03:2x 判读（researcher，unit.receipt c74da1aa7b4347f9b1c270f191d3b9a8，"
        "S5-full-protocol 第六单元算子优化先行 ok 回执，执行单元 716807f799aa，02:30-03:00，commit ca44643）："
        "回执属实 PASS——首轮全量独立复跑（operator_bench.py 复跑 exit=0：identity 类逐位一致 N0 A≡B=0.912109375 exact、"
        "N5 manual-loop 恒等 4.05e-06 exact、E2 mirror 全 equal，计时类 ±3-9% 波动不改变结论；"
        "selftest 68 项+eval_patch 48 用例+ckpt 3×30-30 三重复跑 exit=0）+禁批量训练纪律硬证据"
        "（progress/full_*/ckpt 零改动）。结论确认=零修复（E3 双跑 +0.2%/+0.7% 否决 FIX-1）"
        "+F8 算子墙四台账无阻塞+数值保真→A/B ckpt 不需重训+C 臂重训排产不变。"
        "机器态修正=驱动器 apply_result 按 ok 回执误置 S5 done（完成判据结论级表未出、算子单元是 checkpoint 非收口）"
        "已改回 ready，S5-full-protocol-continue 空阶段按先例关闭（同型第四例），ready_stages 唯一。"
        "拍板=W-LAUNCH 不击穿（A/B 重训 4.6h 收益/代价不成比例；新臂训练启动前可重评）。"
        "排产不变=C 臂重训 3×30ep≈72min+修正 Convention 重算 108 行≈3min→results/full_threearm.csv/md→S5 收口判读。"
        "next_units=[]（workflow 分支自动派、手写拒收）；唤醒点=下一回执或 108 行 CSV/MD 落盘或硬失败。"
        "判读全文 notes/researcher-interventions/c74da1aa7b4347f9b1c270f191d3b9a8.md。卡状态维持 ready 记账。")

now = int(time.time())
c.execute("insert into task_comments (task_id, author, body, created_at) values (?,?,?,?)",
          ("t_f6e7bac5", "research", body, now))
c.commit()
chk = c.execute("select id,task_id,created_at,substr(body,1,60) from task_comments where task_id='t_f6e7bac5' order by created_at desc limit 1").fetchall()
for r in chk:
    print("comment:", r)
print("OK comment inserted at", now)
