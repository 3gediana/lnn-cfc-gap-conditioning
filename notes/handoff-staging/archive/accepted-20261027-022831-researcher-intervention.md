---
stage: researcher-intervention
kind: analysis
status: ok
did: S5 第五单元 failed 空壳回执判读：科学交付 PASS（44 项独立复算全过），回执格式失败勘误为 partial；新发现 verify() 两处倒挂残留已补修并证指标不变；fb-ab50d0ec9f 纳入=下一单元算子优化先行（禁批量训练）。
why: 空壳 failed 回执既不能当 stage 故障重跑、也不能采信叙述——须独立复算盘上产物定性，并按用户最新反馈（先优化算子再跑实验）调整下一步派发顺序。
how: driver trajectory 补回+队列 failed_models+用户侧 bridge 三源定位根因；ckpt 直读/log 逐行对账/CSV 结构/代码补丁核验 44 项复算；探针+回归+verify 三重独立重跑对账；workflow actions 更新接管下一单元指令。
result: supported（第五单元科学结论确认：训练 6/6、掩码 Convention 倒挂 bug 六项证据+3 处科学路径修正+回归 PASS、本轮 CSV/MD 作废、C 臂移存、A/B ckpt 有效）；判读全文 notes/researcher-interventions/710a1c50feff4a9ab0943e929ad06ab6.md
next: continue（算子优化单元 ≤90min → C 臂重训 3×30ep≈72min+修正 Convention 重算 108 行≈3min → S5 收口判读）
artifacts: [notes/researcher-interventions/710a1c50feff4a9ab0943e929ad06ab6.md, experiments/s5_judge_710a_recheck.py, experiments/s5_judge_710a_recheck.txt, experiments/s5_judge_710a_ckpt_verify.txt, experiments/s5_judge_710a_regression_rerun.log, experiments/s5_judge_710a_probe_rerun.log, experiments/s5_judge_710a_probe_original.json, experiments/s5_judge_710a_verify_rerun.py, experiments/s5_judge_710a_verify_rerun.log, results/s5_mask_convention_probe_judge_rerun.json, workflow.json, STATUS.md, notes/DECISIONS.md, notes/RETRO.md]
info_need: 无
---
