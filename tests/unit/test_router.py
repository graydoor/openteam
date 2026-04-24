from core.models import TaskIntent
from router.service import Router


def test_route_planning_intent() -> None:
    router = Router()
    decision = router.route("请帮我拆解需求并规划迭代里程碑")
    assert decision.intent == TaskIntent.PLANNING
    assert decision.specialist == "planner"
    assert decision.fallback is False


def test_route_coding_intent() -> None:
    router = Router()
    decision = router.route("请实现这个 API 并修复 bug")
    assert decision.intent == TaskIntent.CODING
    assert decision.specialist == "coder"
    assert decision.fallback is False


def test_route_review_fallback() -> None:
    router = Router()
    decision = router.route("请 review 这次 PR 并指出风险")
    assert decision.intent == TaskIntent.REVIEW
    assert decision.specialist == "planner"
    assert decision.fallback is True


def test_route_no_match_fallback_to_planner() -> None:
    router = Router()
    decision = router.route("hello world task")
    assert decision.intent == TaskIntent.PLANNING
    assert decision.specialist == "planner"
    assert decision.fallback is True
