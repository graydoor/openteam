# M0 验收文档（最小可运行框架）

## 目标
- 交付可运行的 `Orchestrator + Router + 2 Specialists + Trace`。
- 支持端到端“需求 -> 代码建议”演示。

## 已交付能力
- API：`GET /healthz`、`POST /runs`、`GET /runs/{run_id}`、`GET /traces/{trace_id}`
- Orchestrator：run 状态机（`queued -> routing -> running -> succeeded/failed`）
- Router：3 类任务意图识别（planning/coding/review），review 暂回退到 planner
- Specialists：`PlannerAgent`、`CoderAgent`
- Trace：全链路 `trace_id` 透传与事件记录
- 错误处理：统一错误码 + 结构化错误响应
- Guardrail（占位）：输出长度限制 + 敏感信息脱敏

## 运行步骤
1. `python3 -m pip install -e ".[dev]"`
2. `uvicorn agent_api.main:app --reload`
3. `./scripts/demo_run.sh`
4. `pytest`

## 验收结果（本次基线）
- 功能：M0 最小链路可运行
- Trace：每次 run 返回 `trace_id`，可追溯事件链
- 测试：覆盖 Router、状态机、API 基础行为
- 本地执行说明：当前环境缺少可用 `python>=3.11` 与 `pytest` 运行时，测试已编写但未在此环境完成执行

## 已知限制
- Session 持久化与上下文裁剪未实现（M2）
- 审批流、权限分级未实现（M3）
- 观测看板、告警体系未实现（M4）
- 当前 Router 以规则为主，准确率需通过样本集持续校准

## 下一步（面向 M1）
- 引入 `handoff + as_tool` 混合编排
- 增加 `ReviewerAgent` 并减少 review 回退路径
- 补充路由评测集，拉升多类任务路由准确率
