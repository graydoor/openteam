from core.models import RouteDecision, TaskIntent

INTENT_KEYWORDS = {
    TaskIntent.PLANNING: [
        "plan",
        "规划",
        "拆解",
        "roadmap",
        "方案",
        "milestone",
        "需求",
    ],
    TaskIntent.CODING: [
        "code",
        "编码",
        "实现",
        "refactor",
        "fix",
        "bug",
        "接口",
        "api",
    ],
    TaskIntent.REVIEW: [
        "review",
        "评审",
        "pr",
        "diff",
        "风险",
        "检查",
        "静态",
    ],
}

SPECIALIST_BY_INTENT = {
    TaskIntent.PLANNING: "planner",
    TaskIntent.CODING: "coder",
    TaskIntent.REVIEW: "planner",
}


class Router:
    def route(self, task: str) -> RouteDecision:
        task_lower = task.lower()
        scores = {
            intent: sum(1 for keyword in keywords if keyword in task_lower)
            for intent, keywords in INTENT_KEYWORDS.items()
        }
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        if best_score == 0:
            return RouteDecision(
                intent=TaskIntent.PLANNING,
                specialist="planner",
                confidence=0.40,
                reason="no_rule_match_fallback_to_planner",
                fallback=True,
            )

        confidence = min(0.95, 0.50 + best_score * 0.12)
        specialist = SPECIALIST_BY_INTENT[best_intent]
        fallback = best_intent == TaskIntent.REVIEW
        reason = "keyword_rule_match"
        if fallback:
            reason = "review_agent_unavailable_fallback_to_planner"

        return RouteDecision(
            intent=best_intent,
            specialist=specialist,
            confidence=confidence,
            reason=reason,
            fallback=fallback,
        )
