import sqlite3, time

db = r"D:\hermes-data\kanban\boards\research\kanban.db"
c = sqlite3.connect(db)
row = c.execute("select id,title,status from tasks where id='t_f6e7bac5'").fetchone()
print("card:", row)
assert row and row[0] == "t_f6e7bac5"

body = ("2026-10-27 02:1x 判读（researcher，unit.receipt 710a1c50feff4a9ab0943e929ad06ab6，S5 第五单元 failed 空壳回执，"
        "执行单元 6e9acd73 00:16-01:41）：科学交付 PASS、回执格式失败勘误为 partial——根因=收尾模型调用抽风致 status 非契约枚举"
        "（driver 01:52 unit-notes-backfilled 从 trajectory 补回+队列 failed_models=[stepfun]+用户侧 bridge 观察三源互证，"
        "同 02:4x design 收尾工具墙先例）。本单元独立复算 44 项全 PASS（s5_judge_710a_recheck.py：6 ckpt 直读+full_run.log "
        "逐行对账六臂 30ep 无跳号+CSV 108 格完备+代码补丁核验）+探针/回归/verify 三重独立重跑逐项一致（T3 补丁后 0.9160=修正生效证据）。"
        "新发现=verify() 两处倒挂残留（xb[..]*mask[..] 索引形式）已补修并重跑证 identity 指标不变。"
        "fb-ab50d0ec9f（先优化算子再跑实验，01:28 全局生效至 11-03）纳入：第六单元起=算子优化先行"
        "（experiments/operator_bench.py+修复+回归，禁批量训练，estimate 60min），C 臂重训 3×30ep≈72min+修正 Convention 重算 108 行"
        "排其后；已跑 ckpt 全部保留、结论标注基于旧算子（ncps 0.0.2）。S5 维持 ready（结论级表未出）；next_units=[]"
        "（workflow actions 已更新，03:05 tick 起自动派）；唤醒点=算子单元回执。判读全文 "
        "notes/researcher-interventions/710a1c50feff4a9ab0943e929ad06ab6.md。卡状态维持 ready 记账。")

now = int(time.time())
c.execute("insert into task_comments (task_id, author, body, created_at) values (?,?,?,?)",
          ("t_f6e7bac5", "research", body, now))
c.commit()
chk = c.execute("select id,task_id,created_at,substr(body,1,60) from task_comments where task_id='t_f6e7bac5' order by created_at desc limit 1").fetchall()
for r in chk:
    print("comment:", r)
print("OK comment inserted at", now)
