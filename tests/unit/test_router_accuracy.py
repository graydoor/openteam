from core.models import TaskIntent
from router.service import Router

CASES = [
    ("请拆解这个需求并给出实施步骤", TaskIntent.PLANNING),
    ("帮我规划M0和M1的交付节奏", TaskIntent.PLANNING),
    ("请输出这个项目的技术方案", TaskIntent.PLANNING),
    ("给我一个roadmap，分两周推进", TaskIntent.PLANNING),
    ("需求不清晰，请先梳理边界", TaskIntent.PLANNING),
    ("请实现这个API并补充测试", TaskIntent.CODING),
    ("修复这个bug并提交代码建议", TaskIntent.CODING),
    ("把现有模块重构一下，降低耦合", TaskIntent.CODING),
    ("需要编码实现router和orchestrator", TaskIntent.CODING),
    ("请写代码完成接口逻辑", TaskIntent.CODING),
    ("请review这个PR，指出风险点", TaskIntent.REVIEW),
    ("帮我做代码评审并给出注释", TaskIntent.REVIEW),
    ("看一下diff有没有明显问题", TaskIntent.REVIEW),
    ("对这个PR做静态检查建议", TaskIntent.REVIEW),
    ("请检查变更风险和回归影响", TaskIntent.REVIEW),
    ("先做需求拆解，再评估实现复杂度", TaskIntent.PLANNING),
    ("实现接口后请补测试", TaskIntent.CODING),
    ("请给这个发布计划做review", TaskIntent.REVIEW),
    ("帮我规划里程碑并定义验收", TaskIntent.PLANNING),
    ("修复线上bug并优化代码结构", TaskIntent.CODING),
]


def test_router_offline_accuracy_baseline() -> None:
    router = Router()
    hit = 0
    for task, expected_intent in CASES:
        decision = router.route(task)
        if decision.intent == expected_intent:
            hit += 1
    accuracy = hit / len(CASES)
    assert accuracy >= 0.80
