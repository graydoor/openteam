import re

from agents.base import SpecialistAgent
from core.models import AgentOutput


class PlannerAgent(SpecialistAgent):
    name = "planner"

    def run(self, task: str, context: dict) -> AgentOutput:
        raw_points = re.split(r"[。.!?\n;；]+", task)
        points = [point.strip() for point in raw_points if point.strip()]
        primary_goal = points[0] if points else task.strip()

        actions = [
            f"澄清目标边界：{primary_goal}",
            "拆分任务为可并行的实现子项，并定义输入输出。",
            "给每个子项补充验收标准（功能、质量、风险）。",
        ]
        if context:
            actions.append("结合上下文约束校正优先级和技术方案。")

        output = AgentOutput(
            summary=f"已完成需求拆解草案，核心目标是：{primary_goal}",
            actions=actions,
            risks=[
                "需求边界不清可能导致返工。",
                "缺少可量化验收标准会影响里程碑判定。",
            ],
            next_steps=[
                "确认拆解结果并锁定第一批可交付任务。",
                "进入实现阶段并设置每日进度检查点。",
            ],
        )
        return self._finalize(output)
