from agents.base import SpecialistAgent
from core.models import AgentOutput


class CoderAgent(SpecialistAgent):
    name = "coder"

    def run(self, task: str, context: dict) -> AgentOutput:
        task_lower = task.lower()
        candidate_files: list[str] = []
        if "api" in task_lower or "接口" in task_lower:
            candidate_files.append("agent_api/main.py")
        if "router" in task_lower or "路由" in task_lower:
            candidate_files.append("router/service.py")
        if "test" in task_lower or "测试" in task_lower:
            candidate_files.append("tests/")
        if not candidate_files:
            candidate_files = ["core/", "orchestrator/", "tests/"]

        output = AgentOutput(
            summary="已生成代码实现建议，按模块增量修改并先补充可回归测试。",
            actions=[
                "明确受影响模块并定义最小改动面。",
                f"建议优先修改：{', '.join(candidate_files)}",
                "实现后执行单元测试和集成测试，确认无回归。",
            ],
            risks=[
                "未覆盖异常路径会导致线上不可预期错误。",
                "跨模块改动缺少契约测试可能引入集成问题。",
            ],
            next_steps=[
                "根据建议提交首个最小可运行 patch。",
                "补齐测试后再进行下一轮重构。",
            ],
        )
        return self._finalize(output)
