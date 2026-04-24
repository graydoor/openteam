# OpenTeam Agent (M0)

M0 目标：交付最小可运行框架，支持 `Orchestrator + Router + 2 Specialists + Trace` 的端到端链路。

## 快速开始

1. 安装依赖

```bash
python3 -m pip install -e ".[dev]"
```

2. 启动服务

```bash
uvicorn agent_api.main:app --reload
```

3. 运行 demo

```bash
./scripts/demo_run.sh
```

4. 运行测试

```bash
pytest
```

## 当前实现范围（M0）

- API：`/healthz`、`/runs`、`/runs/{run_id}`、`/traces/{trace_id}`
- 编排：run 状态机、路由分派、重试与超时、失败归因
- 专家：`PlannerAgent`、`CoderAgent`
- Trace：`run_started`、`routed`、`agent_invoked`、`agent_retry`、`run_finished`、`run_failed`
- 最小 Guardrail：输出长度限制、敏感信息脱敏

## 目录结构

```text
agent_api/       # FastAPI 入口
orchestrator/    # run 生命周期与执行编排
router/          # 任务意图路由
agents/          # 专家 Agent
tracing/         # trace 事件记录
core/            # 配置、模型、错误定义
tests/           # 单元 + 集成测试
scripts/         # demo 脚本
```
